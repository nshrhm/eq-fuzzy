from __future__ import annotations

"""Inspect SCIS main-run score and entropy decomposition artifacts."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

from analyze_factorial_scores import decompose_two_way, write_csv


DEFAULT_ANALYSIS_DIR = "artifacts/scis2026/main_analysis_v1"
DEFAULT_OUTPUT_DIR = "artifacts/scis2026/main_inspection_v1"
DEFAULT_DOC = "docs/scis2026/phase6_main_result_inspection.md"
DEFAULT_PRIMARY_FAMILY = "sigmoid_s_v1"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    return float(value)


def build_metric_decomposition(
    cell_summary: list[dict[str, str]],
    *,
    metric: str,
    value_column: str,
    membership_family: str = "",
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[tuple[str, float], float]] = defaultdict(dict)
    for row in cell_summary:
        if membership_family and row.get("membership_family") != membership_family:
            continue
        value = as_float(row.get(value_column))
        if value is None:
            continue
        key = (row["model_id"], row["story_id"], row["emotion"])
        grouped[key][(row["persona_id"], float(row["temperature"]))] = value

    out: list[dict[str, Any]] = []
    for (model_id, story_id, emotion), values in sorted(grouped.items()):
        decomposition = decompose_two_way(values)
        if decomposition["is_estimable"] is True:
            total_ss = (
                float(decomposition["SS_persona"])
                + float(decomposition["SS_temperature"])
                + float(decomposition["SS_persona_x_temperature"])
            )
        else:
            total_ss = ""
        out.append(
            {
                "metric": metric,
                "model_id": model_id,
                "story_id": story_id,
                "emotion": emotion,
                **decomposition,
                "total_SS": round(total_ss, 9) if total_ss != "" else "",
            }
        )
    return out


def summarize_decomposition(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["is_estimable"] is True:
            grouped[(str(row["metric"]), str(row["emotion"]))].append(row)

    out: list[dict[str, Any]] = []
    for (metric, emotion), metric_rows in sorted(grouped.items()):
        persona = [float(row["SS_persona"]) for row in metric_rows]
        temperature = [float(row["SS_temperature"]) for row in metric_rows]
        interaction = [float(row["SS_persona_x_temperature"]) for row in metric_rows]
        total = [float(row["total_SS"]) for row in metric_rows]
        burden = [float(row["interaction_burden"]) for row in metric_rows]
        separability = [float(row["separability_share"]) for row in metric_rows]
        out.append(
            {
                "metric": metric,
                "emotion": emotion,
                "n_units": len(metric_rows),
                "mean_SS_persona": round(mean(persona), 9),
                "mean_SS_temperature": round(mean(temperature), 9),
                "mean_SS_persona_x_temperature": round(mean(interaction), 9),
                "mean_total_SS": round(mean(total), 9),
                "mean_interaction_burden": round(mean(burden), 9),
                "median_interaction_burden": round(median(burden), 9),
                "mean_separability_share": round(mean(separability), 9),
                "median_separability_share": round(median(separability), 9),
            }
        )
    return out


def top_interactions(rows: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    estimable = [row for row in rows if row["is_estimable"] is True]
    return sorted(estimable, key=lambda row: float(row["interaction_burden"]), reverse=True)[:limit]


def top_absolute_interactions(rows: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    estimable = [row for row in rows if row["is_estimable"] is True]
    return sorted(estimable, key=lambda row: float(row["SS_persona_x_temperature"]), reverse=True)[:limit]


def valid_output_summary(analysis_summary: dict[str, Any]) -> dict[str, Any]:
    responses = int(analysis_summary["n_response_rows"])
    ok = int(analysis_summary["n_response_ok"])
    return {
        "n_response_rows": responses,
        "n_response_ok": ok,
        "valid_output_rate": round(ok / responses, 9) if responses else "",
        "n_emotion_rows": analysis_summary["n_emotion_rows"],
        "n_missing_score_rows": analysis_summary["n_missing_score_rows"],
        "n_missing_structural_cells": analysis_summary["n_missing_structural_cells"],
        "n_non_estimable_decomposition_units": analysis_summary["n_non_estimable_decomposition_units"],
        "readiness_passed": analysis_summary["readiness_passed"],
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
    analysis_summary: dict[str, Any],
    inspection_summary: dict[str, Any],
    decomposition_summary: list[dict[str, Any]],
    top_rows: list[dict[str, Any]],
    top_absolute_rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected_summary = [
        row
        for row in decomposition_summary
        if row["metric"] in ("score", "H_norm_sigmoid_s_v1")
    ]
    body = f"""# SCIS Phase 6.5 Main Result Inspection

This document records the first descriptive inspection of the SCIS 2026 main
run. It is an analysis-readiness and result-shaping note, not the final paper
interpretation.

## Input

- Analysis directory: `artifacts/scis2026/main_analysis_v1/`
- Inspection directory: `artifacts/scis2026/main_inspection_v1/`
- Run id: `{analysis_summary["run_id"]}`
- Primary membership family: `{analysis_summary["primary_membership_family"]}`

## Readiness Facts

- Responses: `{analysis_summary["n_response_ok"]} / {analysis_summary["n_response_rows"]}`
- Emotion rows: `{analysis_summary["n_emotion_rows"]}`
- Missing score rows: `{analysis_summary["n_missing_score_rows"]}`
- Missing structural cells: `{analysis_summary["n_missing_structural_cells"]}`
- Non-estimable decomposition units: `{analysis_summary["n_non_estimable_decomposition_units"]}`
- Readiness passed: `{analysis_summary["readiness_passed"]}`

## Inspection Scope

The inspection computes the same balanced persona x temperature decomposition
for:

- `score`, using cell-level mean scores.
- `H_norm_sigmoid_s_v1`, using normalized fuzzy entropy under the primary
  `sigmoid_s_v1` membership family.

The quantities are descriptive effect components, not confirmatory inference:

- `SS_persona`
- `SS_temperature`
- `SS_persona_x_temperature`
- `interaction_burden`
- `separability_share`

## Metric-Level Summary

{markdown_table(selected_summary, [
        "metric",
        "emotion",
        "n_units",
        "mean_SS_persona",
        "mean_SS_temperature",
        "mean_SS_persona_x_temperature",
        "mean_total_SS",
        "mean_interaction_burden",
        "mean_separability_share",
    ])}

## Largest Relative Interaction Burdens

These rows are useful for selecting representative figures and for checking
where persona and temperature are least separable.

{markdown_table(top_rows, [
        "metric",
        "model_id",
        "story_id",
        "emotion",
        "SS_persona",
        "SS_temperature",
        "SS_persona_x_temperature",
        "total_SS",
        "interaction_burden",
        "separability_share",
    ], limit=12)}

Because `interaction_burden` is a ratio, rows with small absolute variation can
rank highly. The following table ranks by absolute interaction sum of squares.

## Largest Absolute Interaction Components

{markdown_table(top_absolute_rows, [
        "metric",
        "model_id",
        "story_id",
        "emotion",
        "SS_persona",
        "SS_temperature",
        "SS_persona_x_temperature",
        "total_SS",
        "interaction_burden",
        "separability_share",
    ], limit=12)}

## Next Use

Use this inspection to choose Phase 7 tables and Phase 8 figures. The current
results support moving from run validation to descriptive result construction,
while bootstrap confidence intervals remain a separate Phase 9 task.

## Machine-Readable Summary

```json
{json.dumps(inspection_summary, ensure_ascii=False, indent=2)}
```
"""
    path.write_text(body, encoding="utf-8")


def run_inspection(
    *,
    analysis_dir: Path,
    output_dir: Path,
    doc_path: Path,
    primary_family: str,
    top_n: int,
) -> dict[str, Any]:
    analysis_summary = load_json(analysis_dir / "analysis_summary.json")
    score_cells = load_csv(analysis_dir / "cell_score_summary.csv")
    entropy_cells = load_csv(analysis_dir / "entropy_cell_summary.csv")

    score_decomposition = build_metric_decomposition(
        score_cells,
        metric="score",
        value_column="mean_score",
    )
    entropy_decomposition = build_metric_decomposition(
        entropy_cells,
        metric=f"H_norm_{primary_family}",
        value_column="mean_H_norm",
        membership_family=primary_family,
    )
    metric_decomposition = score_decomposition + entropy_decomposition
    decomposition_summary = summarize_decomposition(metric_decomposition)
    top_rows = top_interactions(metric_decomposition, limit=top_n)
    top_absolute_rows = top_absolute_interactions(metric_decomposition, limit=top_n)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(metric_decomposition, output_dir / "metric_decomposition.csv")
    write_csv(decomposition_summary, output_dir / "decomposition_summary_by_metric_emotion.csv")
    write_csv(top_rows, output_dir / "top_interaction_burdens.csv")
    write_csv(top_absolute_rows, output_dir / "top_absolute_interactions.csv")

    inspection_summary = {
        "analysis_dir": str(analysis_dir),
        "output_dir": str(output_dir),
        "primary_membership_family": primary_family,
        "valid_output": valid_output_summary(analysis_summary),
        "n_score_decomposition_units": len(score_decomposition),
        "n_entropy_decomposition_units": len(entropy_decomposition),
        "n_metric_decomposition_units": len(metric_decomposition),
        "n_decomposition_summary_rows": len(decomposition_summary),
        "top_n": top_n,
        "max_interaction_burden": round(float(top_rows[0]["interaction_burden"]), 9) if top_rows else "",
        "max_interaction_metric": top_rows[0]["metric"] if top_rows else "",
        "max_absolute_interaction": (
            round(float(top_absolute_rows[0]["SS_persona_x_temperature"]), 9) if top_absolute_rows else ""
        ),
        "max_absolute_interaction_metric": top_absolute_rows[0]["metric"] if top_absolute_rows else "",
    }
    (output_dir / "inspection_summary.json").write_text(
        json.dumps(inspection_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_report(
        path=doc_path,
        analysis_summary=analysis_summary,
        inspection_summary=inspection_summary,
        decomposition_summary=decomposition_summary,
        top_rows=top_rows,
        top_absolute_rows=top_absolute_rows,
    )
    return inspection_summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--doc", default=DEFAULT_DOC)
    parser.add_argument("--primary-family", default=DEFAULT_PRIMARY_FAMILY)
    parser.add_argument("--top-n", type=int, default=20)
    args = parser.parse_args()

    summary = run_inspection(
        analysis_dir=Path(args.analysis_dir),
        output_dir=Path(args.output_dir),
        doc_path=Path(args.doc),
        primary_family=args.primary_family,
        top_n=args.top_n,
    )
    print(f"Wrote inspection artifacts to {Path(args.output_dir).resolve()}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
