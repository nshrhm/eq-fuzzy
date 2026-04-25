from __future__ import annotations

"""Build a SCIS factorial retry manifest from failed raw JSONL records."""

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_MANIFEST = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/manifest.csv"
DEFAULT_RAW_JSONL = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw.jsonl"
DEFAULT_OUTPUT = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/retry_failed_v1_manifest.csv"


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def failed_manifest_rows(records: list[dict[str, Any]]) -> list[int]:
    return sorted(int(record["manifest_row"]) for record in records if record.get("ok") is not True)


def write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--source-manifest", default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--raw-jsonl", default=DEFAULT_RAW_JSONL)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    manifest = load_manifest(repo_root / args.source_manifest)
    records = load_jsonl(repo_root / args.raw_jsonl)
    failed_rows = failed_manifest_rows(records)
    by_row = {int(row["manifest_row"]): row for row in manifest}

    missing = [row_id for row_id in failed_rows if row_id not in by_row]
    if missing:
        raise SystemExit(f"Failed rows not found in source manifest: {missing}")

    retry_rows = [by_row[row_id] for row_id in failed_rows]
    output = repo_root / args.output
    write_manifest(retry_rows, output)
    print(f"Wrote {len(retry_rows)} retry rows to {output}")
    if failed_rows:
        print("Retry manifest rows:", ", ".join(str(row_id) for row_id in failed_rows))


if __name__ == "__main__":
    main()
