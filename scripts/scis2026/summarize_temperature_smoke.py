from __future__ import annotations

"""Summarize SCIS 2026 Phase 1 temperature smoke-test raw JSONL output."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_INPUT = "runs/scis2026/phase1_temperature_smoke_v1/raw.jsonl"
DEFAULT_SUMMARY_JSON = "runs/scis2026/phase1_temperature_smoke_v1/summary.json"
DEFAULT_SUMMARY_CSV = "runs/scis2026/phase1_temperature_smoke_v1/summary.csv"
DEFAULT_TEMPERATURES = (0.1, 0.4, 0.7, 0.9)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def summarize(records: list[dict[str, Any]], required_temperatures: tuple[float, ...]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["model_id"]].append(record)

    rows: list[dict[str, Any]] = []
    for model_id, model_records in sorted(grouped.items()):
        ok_records = [r for r in model_records if r.get("ok") is True]
        accepted = sorted({float(r["temperature"]) for r in ok_records})
        attempted = sorted({float(r["temperature"]) for r in model_records})
        failed_records = [r for r in model_records if r.get("ok") is not True]
        elapsed = [float(r["elapsed_sec"]) for r in model_records if isinstance(r.get("elapsed_sec"), (int, float))]
        status_codes = sorted(
            {
                str(r.get("error_status_code"))
                for r in failed_records
                if r.get("error_status_code") is not None
            }
        )
        validation_errors = sorted(
            {
                err
                for r in failed_records
                for err in (r.get("validation_errors") or [])
            }
        )
        rows.append(
            {
                "model_id": model_id,
                "provider": model_records[0].get("provider", ""),
                "route": model_records[0].get("route", ""),
                "model_group": model_records[0].get("model_group", ""),
                "candidate_role": model_records[0].get("candidate_role", ""),
                "attempted_temperatures": attempted,
                "accepted_temperatures": accepted,
                "required_temperatures": list(required_temperatures),
                "n_attempts": len(model_records),
                "n_ok": len(ok_records),
                "n_failed": len(failed_records),
                "malformed_or_error_rate": round(len(failed_records) / len(model_records), 6),
                "mean_elapsed_sec": round(mean(elapsed), 3) if elapsed else None,
                "error_status_codes": status_codes,
                "validation_errors": validation_errors,
                "passes_phase1_gate": all(t in accepted for t in required_temperatures),
            }
        )
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            encoded = {
                key: json.dumps(value, ensure_ascii=False) if isinstance(value, list) else value
                for key, value in row.items()
            }
            writer.writerow(encoded)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--input-jsonl", default=DEFAULT_INPUT)
    parser.add_argument("--summary-json", default=DEFAULT_SUMMARY_JSON)
    parser.add_argument("--summary-csv", default=DEFAULT_SUMMARY_CSV)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    records = load_jsonl(repo_root / args.input_jsonl)
    rows = summarize(records, DEFAULT_TEMPERATURES)

    summary_json = repo_root / args.summary_json
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps({"models": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(rows, repo_root / args.summary_csv)
    print(f"Wrote {len(rows)} model summaries to {summary_json}")


if __name__ == "__main__":
    main()
