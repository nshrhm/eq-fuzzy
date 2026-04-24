from __future__ import annotations

"""Summarize SCIS 2026 factorial raw JSONL output."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_INPUT = "runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw.jsonl"
DEFAULT_SUMMARY_JSON = "runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/summary.json"
DEFAULT_CELL_CSV = "runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/cell_summary.csv"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def cell_key(record: dict[str, Any]) -> tuple[str, str, str, str, float]:
    return (
        str(record.get("model_id", "")),
        str(record.get("story_id", "")),
        str(record.get("condition_id", "")),
        str(record.get("persona_id", "")),
        float(record.get("temperature", 0.0)),
    )


def summarize(records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ok_records = [r for r in records if r.get("ok") is True]
    failed_records = [r for r in records if r.get("ok") is not True]
    elapsed = [float(r["elapsed_sec"]) for r in records if isinstance(r.get("elapsed_sec"), (int, float))]

    by_model = Counter(r.get("model_id", "") for r in records)
    ok_by_model = Counter(r.get("model_id", "") for r in ok_records)
    validation_errors = sorted({err for r in failed_records for err in (r.get("validation_errors") or [])})
    status_codes = sorted({str(r.get("error_status_code")) for r in failed_records if r.get("error_status_code") is not None})

    grouped: dict[tuple[str, str, str, str, float], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[cell_key(record)].append(record)

    cells: list[dict[str, Any]] = []
    for key, cell_records in sorted(grouped.items()):
        model_id, story_id, condition_id, persona_id, temperature = key
        cell_ok = [r for r in cell_records if r.get("ok") is True]
        cells.append(
            {
                "model_id": model_id,
                "story_id": story_id,
                "condition_id": condition_id,
                "persona_id": persona_id,
                "temperature": temperature,
                "n_attempts": len(cell_records),
                "n_ok": len(cell_ok),
                "n_failed": len(cell_records) - len(cell_ok),
                "valid_rate": round(len(cell_ok) / len(cell_records), 6),
            }
        )

    summary = {
        "run_id": records[0].get("run_id") if records else "",
        "stage": records[0].get("stage") if records else "",
        "design_id": records[0].get("design_id") if records else "",
        "n_records": len(records),
        "n_ok": len(ok_records),
        "n_failed": len(failed_records),
        "valid_rate": round(len(ok_records) / len(records), 6) if records else None,
        "mean_elapsed_sec": round(mean(elapsed), 3) if elapsed else None,
        "models": sorted(by_model),
        "n_models": len(by_model),
        "n_cells": len(cells),
        "model_valid_rates": {
            model_id: round(ok_by_model[model_id] / count, 6)
            for model_id, count in sorted(by_model.items())
        },
        "error_status_codes": status_codes,
        "validation_errors": validation_errors,
    }
    return summary, cells


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
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
    parser.add_argument("--input-jsonl", default=DEFAULT_INPUT)
    parser.add_argument("--summary-json", default=DEFAULT_SUMMARY_JSON)
    parser.add_argument("--cell-csv", default=DEFAULT_CELL_CSV)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    records = load_jsonl(repo_root / args.input_jsonl)
    summary, cells = summarize(records)

    summary_path = repo_root / args.summary_json
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(cells, repo_root / args.cell_csv)
    print(f"Wrote summary to {summary_path}")
    print(f"Wrote {len(cells)} cell rows.")


if __name__ == "__main__":
    main()
