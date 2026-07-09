import csv


def detect_columns(header):
    lower = [h.strip().lower() for h in header]
    query_idx = None
    response_idx = None
    for i, h in enumerate(lower):
        if h in ("query", "queries"):
            query_idx = i
        if h == "response":
            response_idx = i
    if query_idx is None:
        query_idx = 0
    if response_idx is None:
        response_idx = len(header) - 1
    return query_idx, response_idx


def load_rows(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        query_idx, response_idx = detect_columns(header)
        rows = []
        for row in reader:
            if not row or all(not c.strip() for c in row):
                continue
            query = row[query_idx].strip() if query_idx < len(row) else ""
            response = row[response_idx].strip() if response_idx < len(row) else ""
            if query.lower() == "total run time":
                # trailing run-summary row appended by querycapture.py, not a real query/response
                continue
            rows.append({"query": query, "response": response})
    return rows
