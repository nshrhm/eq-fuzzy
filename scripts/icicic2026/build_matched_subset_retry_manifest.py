from __future__ import annotations

"""Build an ICICIC matched-subset retry manifest for failed raw rows only."""

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_MANIFEST = "runs/icicic2026/icicic2026_benchmark_positioning_v1_sanity/manifest.csv"
DEFAULT_RAW_JSONL = "runs/icicic2026/icicic2026_benchmark_positioning_v1_sanity/raw.jsonl"
DEFAULT_OUTPUT = "runs/icicic2026/icicic2026_benchmark_positioning_v1_sanity/retry_failed_manifest.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def failed_manifest_rows(records: list[dict[str, Any]]) -> set[int]:
    return {
        int(record["manifest_row"])
        for record in records
        if record.get("ok") is not True
    }


def build_retry_manifest(*, source_manifest: Path, raw_jsonl: Path, output_path: Path) -> list[dict[str, str]]:
    manifest_rows = load_csv(source_manifest)
    raw_records = load_jsonl(raw_jsonl)
    failed_rows = failed_manifest_rows(raw_records)
    retry_rows = [row for row in manifest_rows if int(row["manifest_row"]) in failed_rows]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not retry_rows:
        output_path.write_text("", encoding="utf-8")
        return []
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(retry_rows[0].keys()))
        writer.writeheader()
        writer.writerows(retry_rows)
    return retry_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--source-manifest", default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--raw-jsonl", default=DEFAULT_RAW_JSONL)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    retry_rows = build_retry_manifest(
        source_manifest=repo_root / args.source_manifest,
        raw_jsonl=repo_root / args.raw_jsonl,
        output_path=repo_root / args.output,
    )
    print(f"Wrote {len(retry_rows)} retry rows.")


if __name__ == "__main__":
    main()
