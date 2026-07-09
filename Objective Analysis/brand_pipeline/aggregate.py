import argparse
import json
import os
import re
from urllib.parse import urlparse

import pandas as pd


def normalize_descriptor_key(phrase):
    key = re.sub(r"\s+", " ", phrase.strip().lower())
    if len(key) > 1 and key.endswith("s") and not key.endswith("ss"):
        key = key[:-1]
    return key


def normalize_figure_key(value):
    key = value.strip().lower()
    key = key.replace(",", "")
    key = re.sub(r"\+\s*$", "", key)
    key = re.sub(r"\s+", " ", key).strip()
    return key


def extract_domain(source):
    s = source.strip()
    if not s:
        return None
    candidate = s if "://" in s else "https://" + s
    try:
        parsed = urlparse(candidate)
    except ValueError:
        return None
    netloc = parsed.netloc.lower()
    if not netloc:
        return None
    netloc = netloc.split(":")[0]
    labels = netloc.split(".")
    if len(labels) > 2:
        netloc = ".".join(labels[-2:])
    return netloc or None


def load_records(cache_path, limit=None):
    records = []
    with open(cache_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    records.sort(key=lambda r: r["row_index"])
    if limit is not None:
        records = [r for r in records if r["row_index"] < limit]
    return records


def _mode(series):
    counts = series.value_counts()
    return counts.idxmax() if not counts.empty else None


def aggregate_descriptors(records, total_rows):
    entries = []
    for rec in records:
        for phrase in rec.get("descriptors", []):
            phrase = phrase.strip()
            if not phrase:
                continue
            entries.append({"phrase": phrase, "key": normalize_descriptor_key(phrase)})

    if not entries:
        return pd.DataFrame(columns=["phrase", "frequency", "pct_of_responses"])

    df = pd.DataFrame(entries)
    freq = df.groupby("key").size().rename("frequency")
    canonical = df.groupby("key")["phrase"].agg(_mode).rename("phrase")
    result = pd.concat([canonical, freq], axis=1).reset_index(drop=True)
    result["pct_of_responses"] = result["frequency"] / total_rows * 100
    result = result.sort_values("frequency", ascending=False).head(20).reset_index(drop=True)
    return result[["phrase", "frequency", "pct_of_responses"]]


def aggregate_figures(records, total_rows):
    entries = []
    for rec in records:
        seen_in_row = {}
        for fig in rec.get("figures", []):
            value = (fig.get("value") or "").strip()
            context = (fig.get("context") or "").strip()
            if not value:
                continue
            key = normalize_figure_key(value)
            if key not in seen_in_row:
                seen_in_row[key] = (value, context)
        for key, (value, context) in seen_in_row.items():
            entries.append({"row_index": rec["row_index"], "key": key, "value": value, "context": context})

    zero_figure_pct = 100.0
    if not entries:
        empty = pd.DataFrame(columns=["figure", "context", "raw_frequency", "dominance_pct"])
        return empty, zero_figure_pct

    df = pd.DataFrame(entries)
    rows_with_any_figure = df["row_index"].nunique()
    zero_figure_pct = (total_rows - rows_with_any_figure) / total_rows * 100

    raw_freq = df.groupby("key")["row_index"].nunique().rename("raw_frequency")
    canonical_value = df.groupby("key")["value"].agg(_mode).rename("figure")
    canonical_context = df.groupby("key")["context"].agg(_mode).rename("context")

    result = pd.concat([canonical_value, canonical_context, raw_freq], axis=1).reset_index(drop=True)
    result["dominance_pct"] = result["raw_frequency"] / rows_with_any_figure * 100
    result = result.sort_values("raw_frequency", ascending=False).head(10).reset_index(drop=True)
    return result[["figure", "context", "raw_frequency", "dominance_pct"]], zero_figure_pct


def aggregate_sources(records, total_rows):
    entries = []
    for rec in records:
        domains_in_row = set()
        for src in rec.get("sources", []):
            domain = extract_domain(src)
            if domain:
                domains_in_row.add(domain)
        for domain in domains_in_row:
            entries.append({"row_index": rec["row_index"], "domain": domain})

    zero_source_pct = 100.0
    if not entries:
        empty = pd.DataFrame(columns=["domain", "frequency"])
        return empty, zero_source_pct

    df = pd.DataFrame(entries)
    rows_with_any_source = df["row_index"].nunique()
    zero_source_pct = (total_rows - rows_with_any_source) / total_rows * 100

    freq = df.groupby("domain")["row_index"].nunique().rename("frequency").reset_index()
    freq = freq.sort_values("frequency", ascending=False).head(20).reset_index(drop=True)
    return freq[["domain", "frequency"]], zero_source_pct


def _write_section(f, title, df):
    f.write(f"=== {title} ===\n")
    df.to_csv(f, index=False)
    f.write("\n")


def run_aggregation(cache_path, output_dir, limit=None):
    records = load_records(cache_path, limit=limit)
    total_rows = len(records)
    if total_rows == 0:
        raise ValueError(f"No cached extraction records found in {cache_path}")

    os.makedirs(output_dir, exist_ok=True)

    descriptors_df = aggregate_descriptors(records, total_rows)
    figures_df, zero_figure_pct = aggregate_figures(records, total_rows)
    sources_df, zero_source_pct = aggregate_sources(records, total_rows)

    figures_summary_df = pd.DataFrame(
        [{"metric": "pct_responses_with_zero_qualifying_figures", "value": zero_figure_pct}]
    )
    sources_summary_df = pd.DataFrame(
        [{"metric": "pct_responses_with_zero_identifiable_sources", "value": zero_source_pct}]
    )

    output_path = os.path.join(output_dir, "brand_analysis.csv")
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        _write_section(f, "DESCRIPTORS", descriptors_df)
        _write_section(f, "FIGURES", figures_df)
        _write_section(f, "FIGURES SUMMARY", figures_summary_df)
        _write_section(f, "SOURCES", sources_df)
        _write_section(f, "SOURCES SUMMARY", sources_summary_df)

    return total_rows


def main():
    parser = argparse.ArgumentParser(description="Aggregate cached brand extractions into output CSVs")
    parser.add_argument("--cache", required=True, help="Path to jsonl cache file")
    parser.add_argument("--output-dir", required=True, help="Directory to write output CSVs to")
    parser.add_argument("--limit", type=int, default=None, help="Only aggregate rows with row_index < N")
    args = parser.parse_args()

    n = run_aggregation(args.cache, args.output_dir, limit=args.limit)
    print(f"Aggregation complete for {n} row(s). Output: {args.output_dir}")


if __name__ == "__main__":
    main()
