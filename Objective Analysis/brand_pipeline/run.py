import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brand_pipeline.aggregate import run_aggregation

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "Brand", "Output")
DEFAULT_CACHE = os.path.join(DEFAULT_OUTPUT_DIR, "extractions_cache.jsonl")


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate cached brand extractions (descriptors/figures/sources) into output CSVs"
    )
    parser.add_argument("--cache", default=DEFAULT_CACHE, help="Path to jsonl extraction cache")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory to write output CSVs to")
    parser.add_argument("--limit", type=int, default=None, help="Only aggregate rows with row_index < N")
    args = parser.parse_args()

    run_aggregation(args.cache, args.output_dir, limit=args.limit)


if __name__ == "__main__":
    main()
