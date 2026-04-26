from __future__ import annotations

"""Analyze ICICIC external mini-comparison raw JSONL output."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_INPUT = "runs/icicic2026/icicic2026_external_mini_comparison_v1/raw.jsonl"
DEFAULT_OUTPUT_DIR = "artifacts/icicic2026/external_mini_analysis_v1"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def normalize_answer(value: Any) -> str:
    return str(value or "").strip().casefold()


def expand_item_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
        answer = parsed.get("answer", "")
        answer_key = record.get("answer_key", "")
        is_exact_match = normalize_answer(answer) == normalize_answer(answer_key)
        rows.append(
            {
                "run_id": record.get("run_id", ""),
                "design_id": record.get("design_id", ""),
                "manifest_row": record.get("manifest_row", ""),
                "model_id": record.get("model_id", ""),
                "provider": record.get("provider", ""),
                "benchmark_id": record.get("benchmark_id", ""),
                "item_id": record.get("item_id", ""),
                "native_metric": record.get("native_metric", ""),
                "ok": bool(record.get("ok") is True),
                "answer": answer,
                "answer_key": answer_key,
                "exact_match": bool(record.get("ok") is True and is_exact_match),
                "confidence": parsed.get("confidence", "") if record.get("ok") is True else "",
                "validation_errors": ";".join(str(err) for err in (record.get("validation_errors") or [])),
            }
        )
    return rows


def build_summary_rows(item_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in item_rows:
        grouped[(row["model_id"], row["provider"], row["benchmark_id"])].append(row)

    out: list[dict[str, Any]] = []
    for (model_id, provider, benchmark_id), rows in sorted(grouped.items()):
        ok_rows = [row for row in rows if row["ok"] is True]
        exact_rows = [row for row in rows if row["exact_match"] is True]
        confidence = [float(row["confidence"]) for row in ok_rows if row["confidence"] != ""]
        out.append(
            {
                "model_id": model_id,
                "provider": provider,
                "benchmark_id": benchmark_id,
                "n_items": len(rows),
                "n_ok": len(ok_rows),
                "valid_output_rate": round(len(ok_rows) / len(rows), 6) if rows else "",
                "native_exact_match_rate": round(len(exact_rows) / len(rows), 6) if rows else "",
                "mean_confidence": round(mean(confidence), 6) if confidence else "",
            }
        )
    return out


def run_analysis(*, input_jsonl: Path, output_dir: Path) -> dict[str, Any]:
    records = load_jsonl(input_jsonl)
    item_rows = expand_item_rows(records)
    summary_rows = build_summary_rows(item_rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(item_rows, output_dir / "item_results.csv")
    write_csv(summary_rows, output_dir / "benchmark_model_summary.csv")
    summary = {
        "analysis_id": "icicic2026_external_mini_analysis_v1",
        "input_jsonl": str(input_jsonl),
        "n_response_rows": len(records),
        "n_item_rows": len(item_rows),
        "n_summary_rows": len(summary_rows),
        "claim_discipline": "descriptive external benchmark mini-comparison only",
    }
    (output_dir / "analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--input-jsonl", default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    summary = run_analysis(
        input_jsonl=repo_root / args.input_jsonl,
        output_dir=repo_root / args.output_dir,
    )
    print(f"Wrote external mini analysis with {summary['n_response_rows']} response rows.")


if __name__ == "__main__":
    main()
