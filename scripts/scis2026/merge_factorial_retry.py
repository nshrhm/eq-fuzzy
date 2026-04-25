from __future__ import annotations

"""Merge successful SCIS factorial retry records into a repaired raw JSONL."""

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_BASE_JSONL = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw.jsonl"
DEFAULT_RETRY_JSONL = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw_retry_failed_v1.jsonl"
DEFAULT_OUTPUT_JSONL = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw_repaired.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--base-jsonl", default=DEFAULT_BASE_JSONL)
    parser.add_argument("--retry-jsonl", default=DEFAULT_RETRY_JSONL)
    parser.add_argument("--output-jsonl", default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--allow-failed-retry", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    base_records = load_jsonl(repo_root / args.base_jsonl)
    retry_records = load_jsonl(repo_root / args.retry_jsonl)

    retry_by_row: dict[int, dict[str, Any]] = {}
    duplicate_retry_rows: list[int] = []
    failed_retry_rows: list[int] = []
    for record in retry_records:
        row_id = int(record["manifest_row"])
        if row_id in retry_by_row:
            duplicate_retry_rows.append(row_id)
        retry_by_row[row_id] = record
        if record.get("ok") is not True:
            failed_retry_rows.append(row_id)

    if duplicate_retry_rows:
        raise SystemExit(f"Duplicate retry manifest rows: {sorted(duplicate_retry_rows)}")
    if failed_retry_rows and not args.allow_failed_retry:
        raise SystemExit(f"Retry records still failed: {sorted(failed_retry_rows)}")

    base_by_row = {int(record["manifest_row"]): record for record in base_records}
    missing_retry_rows = [row_id for row_id in retry_by_row if row_id not in base_by_row]
    if missing_retry_rows:
        raise SystemExit(f"Retry rows not found in base raw JSONL: {sorted(missing_retry_rows)}")

    repaired: list[dict[str, Any]] = []
    replaced_rows: list[int] = []
    for record in base_records:
        row_id = int(record["manifest_row"])
        if row_id in retry_by_row:
            repaired.append(retry_by_row[row_id])
            replaced_rows.append(row_id)
        else:
            repaired.append(record)

    write_jsonl(repaired, repo_root / args.output_jsonl)
    print(f"Wrote {len(repaired)} repaired records to {repo_root / args.output_jsonl}")
    print("Replaced manifest rows:", ", ".join(str(row_id) for row_id in replaced_rows))


if __name__ == "__main__":
    main()
