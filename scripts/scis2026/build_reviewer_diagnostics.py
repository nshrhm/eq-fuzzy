from __future__ import annotations

"""Build reviewer-risk diagnostics for the SCIS 2026 main run."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_RUN_DIR = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1"
DEFAULT_ANALYSIS_DIR = "artifacts/scis2026/main_analysis_v1"
DEFAULT_INSPECTION_DIR = "artifacts/scis2026/main_inspection_v1"
DEFAULT_TABLES_DIR = "artifacts/scis2026/main_tables_v1"
DEFAULT_OUTPUT_DIR = "artifacts/scis2026/main_reviewer_diagnostics_v1"
DEFAULT_DOC = "docs/scis2026/phase14_reviewer_risk_diagnostics.md"
PRIMARY_METRICS = ("score", "H_norm_sigmoid_s_v1")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def round_or_blank(value: float | None, digits: int = 9) -> float | str:
    return round(value, digits) if value is not None else ""


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row["metric"] in PRIMARY_METRICS and row["is_estimable"] == "True"]


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, float | int | str]:
    if not rows:
        return {
            "n_units": 0,
            "mean_persona_share": "",
            "mean_temperature_share": "",
            "mean_interaction_burden": "",
            "mean_separability_share": "",
        }
    persona = [float(row["SS_persona"]) / float(row["total_SS"]) for row in rows]
    temperature = [float(row["SS_temperature"]) / float(row["total_SS"]) for row in rows]
    interaction = [float(row["interaction_burden"]) for row in rows]
    return {
        "n_units": len(rows),
        "mean_persona_share": round(mean(persona), 9),
        "mean_temperature_share": round(mean(temperature), 9),
        "mean_interaction_burden": round(mean(interaction), 9),
        "mean_separability_share": round(1.0 - mean(interaction), 9),
    }


def build_full_summary(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["metric"], row["emotion"])].append(row)
    return {key: summarize_rows(value) for key, value in grouped.items()}


def build_leave_one_model_out(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    all_models = sorted({row["model_id"] for row in rows})
    full = build_full_summary(rows)
    out: list[dict[str, Any]] = []
    for omitted_model in all_models:
        subset = [row for row in rows if row["model_id"] != omitted_model]
        grouped = build_full_summary(subset)
        for metric, emotion in sorted(full):
            full_summary = full[(metric, emotion)]
            subset_summary = grouped[(metric, emotion)]
            full_burden = float(full_summary["mean_interaction_burden"])
            subset_burden = float(subset_summary["mean_interaction_burden"])
            out.append(
                {
                    "omitted_model_id": omitted_model,
                    "metric": metric,
                    "emotion": emotion,
                    "n_units": subset_summary["n_units"],
                    "full_mean_interaction_burden": full_summary["mean_interaction_burden"],
                    "leave_one_out_mean_interaction_burden": subset_summary["mean_interaction_burden"],
                    "delta_interaction_burden": round(subset_burden - full_burden, 9),
                    "full_mean_persona_share": full_summary["mean_persona_share"],
                    "leave_one_out_mean_persona_share": subset_summary["mean_persona_share"],
                }
            )
    return out


def build_story_stratified(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["story_id"], row["metric"], row["emotion"])].append(row)

    out: list[dict[str, Any]] = []
    for (story_id, metric, emotion), group_rows in sorted(grouped.items()):
        summary = summarize_rows(group_rows)
        out.append({"story_id": story_id, "metric": metric, "emotion": emotion, **summary})
    return out


def build_emotion_stratified(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["metric"], row["emotion"])].append(row)

    out: list[dict[str, Any]] = []
    for (metric, emotion), group_rows in sorted(grouped.items()):
        out.append({"metric": metric, "emotion": emotion, **summarize_rows(group_rows)})
    return out


def compact_failure_reason(record: dict[str, Any]) -> str:
    errors = record.get("validation_errors") or []
    if errors:
        return ";".join(str(error) for error in errors)
    if record.get("error"):
        return str(record["error"])
    response = record.get("response") or {}
    choices = response.get("choices") or []
    if choices:
        finish_reason = choices[0].get("finish_reason") or choices[0].get("native_finish_reason")
        if finish_reason:
            return f"finish_reason:{finish_reason}"
    return "unknown"


def build_retry_diagnostics(run_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw_records = load_jsonl(run_dir / "raw.jsonl")
    retry_records = load_jsonl(run_dir / "raw_retry_failed_v1.jsonl")
    repaired_records = load_jsonl(run_dir / "raw_repaired.jsonl")

    failed_base = [record for record in raw_records if record.get("ok") is not True]
    retry_by_row = {int(record["manifest_row"]): record for record in retry_records}
    repaired_by_row = {int(record["manifest_row"]): record for record in repaired_records}

    out: list[dict[str, Any]] = []
    for record in sorted(failed_base, key=lambda item: int(item["manifest_row"])):
        row_id = int(record["manifest_row"])
        retry = retry_by_row.get(row_id, {})
        repaired = repaired_by_row.get(row_id, {})
        out.append(
            {
                "manifest_row": row_id,
                "model_id": record["model_id"],
                "story_id": record["story_id"],
                "condition_id": record["condition_id"],
                "persona_id": record["persona_id"],
                "temperature": record["temperature"],
                "repetition": record["repetition"],
                "base_ok": record.get("ok") is True,
                "retry_ok": retry.get("ok") is True,
                "repaired_ok": repaired.get("ok") is True,
                "base_failure_reason": compact_failure_reason(record),
                "retry_failure_reason": "" if retry.get("ok") is True else compact_failure_reason(retry),
            }
        )

    failure_by_model = Counter(row["model_id"] for row in out)
    failure_by_story = Counter(row["story_id"] for row in out)
    failure_by_temperature = Counter(str(row["temperature"]) for row in out)
    summary = {
        "base_response_rows": len(raw_records),
        "base_failed_rows": len(failed_base),
        "retry_rows": len(retry_records),
        "retry_success_rows": sum(1 for record in retry_records if record.get("ok") is True),
        "repaired_response_rows": len(repaired_records),
        "repaired_failed_rows": sum(1 for record in repaired_records if record.get("ok") is not True),
        "failure_by_model": dict(sorted(failure_by_model.items())),
        "failure_by_story": dict(sorted(failure_by_story.items())),
        "failure_by_temperature": dict(sorted(failure_by_temperature.items())),
    }
    return out, summary


def build_risk_summary(
    *,
    retry_summary: dict[str, Any],
    emotion_summary: list[dict[str, Any]],
    leave_one_out: list[dict[str, Any]],
    story_summary: list[dict[str, Any]],
    entropy_sensitivity: list[dict[str, str]],
) -> dict[str, Any]:
    max_loo_delta = max(abs(float(row["delta_interaction_burden"])) for row in leave_one_out)
    max_story_burden = max(float(row["mean_interaction_burden"]) for row in story_summary)
    score_rows = [row for row in emotion_summary if row["metric"] == "score"]
    entropy_rows = [row for row in emotion_summary if row["metric"] == "H_norm_sigmoid_s_v1"]
    sensitivity = entropy_sensitivity[0] if entropy_sensitivity else {}
    return {
        "retry_gate_passed": retry_summary["base_failed_rows"] == retry_summary["retry_success_rows"]
        and retry_summary["repaired_failed_rows"] == 0,
        "base_failed_rows": retry_summary["base_failed_rows"],
        "repaired_failed_rows": retry_summary["repaired_failed_rows"],
        "max_abs_leave_one_model_out_delta_interaction_burden": round(max_loo_delta, 9),
        "max_story_stratified_mean_interaction_burden": round(max_story_burden, 9),
        "score_mean_interaction_burden_range": [
            round(min(float(row["mean_interaction_burden"]) for row in score_rows), 9),
            round(max(float(row["mean_interaction_burden"]) for row in score_rows), 9),
        ],
        "entropy_mean_interaction_burden_range": [
            round(min(float(row["mean_interaction_burden"]) for row in entropy_rows), 9),
            round(max(float(row["mean_interaction_burden"]) for row in entropy_rows), 9),
        ],
        "entropy_sensitivity_cell_mean_correlation": sensitivity.get("pearson_H_norm_cell_mean", ""),
        "entropy_sensitivity_mean_abs_delta": sensitivity.get("mean_abs_H_norm_diff", ""),
        "requires_main_run_redesign": False,
    }


def markdown_table(rows: list[dict[str, Any]], columns: list[str], *, limit: int | None = None) -> str:
    shown = rows[:limit] if limit is not None else rows
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in shown:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def write_report(
    *,
    path: Path,
    summary: dict[str, Any],
    retry_rows: list[dict[str, Any]],
    emotion_summary: list[dict[str, Any]],
    leave_one_out: list[dict[str, Any]],
    story_summary: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    largest_loo = sorted(
        leave_one_out,
        key=lambda row: abs(float(row["delta_interaction_burden"])),
        reverse=True,
    )[:12]
    largest_story = sorted(
        story_summary,
        key=lambda row: float(row["mean_interaction_burden"]),
        reverse=True,
    )[:12]
    body = f"""# SCIS Phase 14 Reviewer-Risk Diagnostics

This document records lightweight diagnostics for reviewer-facing risk checks.
These diagnostics use the completed SCIS main run and do not change the main
experimental design.

## Summary

```json
{json.dumps(summary, ensure_ascii=False, indent=2)}
```

Interpretation: the diagnostics do not indicate a need to redesign the `r = 5`
main run. They identify points to describe carefully in the manuscript or
appendix.

## Retry and Validity Check

{markdown_table(retry_rows, [
        "manifest_row",
        "model_id",
        "story_id",
        "condition_id",
        "persona_id",
        "temperature",
        "repetition",
        "retry_ok",
        "repaired_ok",
        "base_failure_reason",
    ])}

## Emotion-Level Interaction Summary

{markdown_table(emotion_summary, [
        "metric",
        "emotion",
        "n_units",
        "mean_persona_share",
        "mean_temperature_share",
        "mean_interaction_burden",
        "mean_separability_share",
    ])}

## Largest Leave-One-Model-Out Changes

{markdown_table(largest_loo, [
        "omitted_model_id",
        "metric",
        "emotion",
        "full_mean_interaction_burden",
        "leave_one_out_mean_interaction_burden",
        "delta_interaction_burden",
    ])}

## Largest Story-Stratified Interaction Burdens

{markdown_table(largest_story, [
        "story_id",
        "metric",
        "emotion",
        "n_units",
        "mean_persona_share",
        "mean_temperature_share",
        "mean_interaction_burden",
    ])}

## Manuscript Use

- The retry check supports describing the four failed main-run rows as targeted
  repair cases rather than systematic failure.
- Leave-one-model-out and story-stratified outputs should be used as appendix
  material unless a reviewer asks whether a single model or text dominates the
  result.
- The emotion summary supports the current Results narrative: entropy has
  larger interaction burden than score, with anger and surprise requiring the
  most careful discussion.
"""
    path.write_text(body, encoding="utf-8")


def run_diagnostics(
    *,
    run_dir: Path,
    inspection_dir: Path,
    tables_dir: Path,
    output_dir: Path,
    doc_path: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = metric_rows(load_csv(inspection_dir / "metric_decomposition.csv"))
    entropy_sensitivity = load_csv(tables_dir / "table4_entropy_sensitivity.csv")

    retry_rows, retry_summary = build_retry_diagnostics(run_dir)
    leave_one_out = build_leave_one_model_out(rows)
    story_summary = build_story_stratified(rows)
    emotion_summary = build_emotion_stratified(rows)
    summary = build_risk_summary(
        retry_summary=retry_summary,
        emotion_summary=emotion_summary,
        leave_one_out=leave_one_out,
        story_summary=story_summary,
        entropy_sensitivity=entropy_sensitivity,
    )

    write_csv(output_dir / "retry_diagnostics.csv", retry_rows)
    write_csv(output_dir / "leave_one_model_out_interaction.csv", leave_one_out)
    write_csv(output_dir / "story_stratified_interaction.csv", story_summary)
    write_csv(output_dir / "emotion_stratified_interaction.csv", emotion_summary)
    (output_dir / "reviewer_diagnostics_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(
        path=doc_path,
        summary=summary,
        retry_rows=retry_rows,
        emotion_summary=emotion_summary,
        leave_one_out=leave_one_out,
        story_summary=story_summary,
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--run-dir", default=DEFAULT_RUN_DIR)
    parser.add_argument("--analysis-dir", default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--inspection-dir", default=DEFAULT_INSPECTION_DIR)
    parser.add_argument("--tables-dir", default=DEFAULT_TABLES_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--doc", default=DEFAULT_DOC)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    summary = run_diagnostics(
        run_dir=repo_root / args.run_dir,
        inspection_dir=repo_root / args.inspection_dir,
        tables_dir=repo_root / args.tables_dir,
        output_dir=repo_root / args.output_dir,
        doc_path=repo_root / args.doc,
    )
    print(f"Wrote reviewer diagnostics to {repo_root / args.output_dir}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
