from __future__ import annotations

"""Build SCIS main-run primary paper tables from inspection artifacts."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

from analyze_factorial_scores import write_csv
from inspect_main_results import load_csv, load_json, run_inspection


DEFAULT_ANALYSIS_DIR = "artifacts/scis2026/main_analysis_v1"
DEFAULT_INSPECTION_DIR = "artifacts/scis2026/main_inspection_v1"
DEFAULT_OUTPUT_DIR = "artifacts/scis2026/main_tables_v1"
DEFAULT_DOC = "docs/scis2026/phase7_primary_tables.md"
DEFAULT_PRIMARY_FAMILY = "sigmoid_s_v1"


def num(value: Any) -> float:
    return float(value)


def fmt(value: Any, digits: int = 3) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.{digits}f}"


def pct(value: Any, digits: int = 1) -> str:
    if value in ("", None):
        return ""
    return f"{float(value) * 100:.{digits}f}\\%"


def latex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def metric_label(metric: str) -> str:
    if metric == "score":
        return "Score"
    if metric.startswith("H_norm_"):
        return r"Entropy $H^*$"
    return latex_escape(metric)


def emotion_label(emotion: str) -> str:
    return {
        "interest": "Interest",
        "surprise": "Surprise",
        "sadness": "Sadness",
        "anger": "Anger",
    }.get(emotion, emotion.title())


def compact_model_label(model_id: str) -> str:
    labels = {
        "openai/gpt-5.4": "GPT-5.4",
        "anthropic/claude-sonnet-4.5": "Claude Sonnet 4.5",
        "google/gemini-2.5-pro": "Gemini 2.5 Pro",
        "x-ai/grok-4.20": "Grok 4.20",
        "deepseek/deepseek-v3.2": "DeepSeek V3.2",
        "meta-llama/llama-4-maverick": "Llama 4 Maverick",
    }
    return labels.get(model_id, model_id)


def write_latex_table(
    *,
    path: Path,
    caption: str,
    label: str,
    headers: list[str],
    rows: list[list[str]],
    alignment: str | None = None,
    table_star: bool = False,
) -> None:
    env = "table*" if table_star else "table"
    align = alignment or ("l" * len(headers))
    lines = [
        rf"\begin{{{env}}}[t]",
        r"\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        rf"\begin{{tabular}}{{{align}}}",
        r"\hline",
        " & ".join(headers) + r" \\",
        r"\hline",
    ]
    for row in rows:
        lines.append(" & ".join(row) + r" \\")
    lines.extend(
        [
            r"\hline",
            r"\end{tabular}",
            rf"\end{{{env}}}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_run_validity_table(analysis_summary: dict[str, Any]) -> list[dict[str, Any]]:
    response_rows = int(analysis_summary["n_response_rows"])
    response_ok = int(analysis_summary["n_response_ok"])
    emotion_rows = int(analysis_summary["n_emotion_rows"])
    missing_scores = int(analysis_summary["n_missing_score_rows"])
    return [
        {
            "run_id": analysis_summary["run_id"],
            "stage": analysis_summary["stage"],
            "response_rows": response_rows,
            "response_ok": response_ok,
            "valid_output_rate": round(response_ok / response_rows, 9),
            "emotion_rows": emotion_rows,
            "missing_score_rows": missing_scores,
            "missing_structural_cells": analysis_summary["n_missing_structural_cells"],
            "non_estimable_decomposition_units": analysis_summary["n_non_estimable_decomposition_units"],
        }
    ]


def shares(row: dict[str, Any]) -> tuple[float, float, float]:
    total = num(row["total_SS"])
    if total == 0.0:
        return 0.0, 0.0, 0.0
    return (
        num(row["SS_persona"]) / total,
        num(row["SS_temperature"]) / total,
        num(row["SS_persona_x_temperature"]) / total,
    )


def build_effect_summary_table(metric_decomposition: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in metric_decomposition:
        if row["is_estimable"] == "True":
            grouped[(row["metric"], row["emotion"])].append(row)

    out: list[dict[str, Any]] = []
    for (metric, emotion), rows in sorted(grouped.items()):
        persona_shares: list[float] = []
        temperature_shares: list[float] = []
        interaction_shares: list[float] = []
        total_ss = []
        for row in rows:
            p_share, t_share, i_share = shares(row)
            persona_shares.append(p_share)
            temperature_shares.append(t_share)
            interaction_shares.append(i_share)
            total_ss.append(num(row["total_SS"]))
        out.append(
            {
                "metric": metric,
                "emotion": emotion,
                "n_units": len(rows),
                "mean_persona_share": round(mean(persona_shares), 9),
                "mean_temperature_share": round(mean(temperature_shares), 9),
                "mean_interaction_burden": round(mean(interaction_shares), 9),
                "median_interaction_burden": round(median(interaction_shares), 9),
                "mean_separability_share": round(1.0 - mean(interaction_shares), 9),
                "median_total_SS": round(median(total_ss), 9),
            }
        )
    return out


def build_model_metric_table(metric_decomposition: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in metric_decomposition:
        if row["is_estimable"] == "True":
            grouped[(row["model_id"], row["metric"])].append(row)

    out: list[dict[str, Any]] = []
    for (model_id, metric), rows in sorted(grouped.items()):
        persona_shares: list[float] = []
        temperature_shares: list[float] = []
        interaction_shares: list[float] = []
        absolute_interactions = []
        for row in rows:
            p_share, t_share, i_share = shares(row)
            persona_shares.append(p_share)
            temperature_shares.append(t_share)
            interaction_shares.append(i_share)
            absolute_interactions.append(num(row["SS_persona_x_temperature"]))
        out.append(
            {
                "model_id": model_id,
                "model_label": compact_model_label(model_id),
                "metric": metric,
                "n_units": len(rows),
                "mean_persona_share": round(mean(persona_shares), 9),
                "mean_temperature_share": round(mean(temperature_shares), 9),
                "mean_interaction_burden": round(mean(interaction_shares), 9),
                "median_interaction_burden": round(median(interaction_shares), 9),
                "max_interaction_burden": round(max(interaction_shares), 9),
                "max_absolute_interaction": round(max(absolute_interactions), 9),
            }
        )
    return out


def build_top_case_table(
    top_relative: list[dict[str, str]],
    top_absolute: list[dict[str, str]],
    *,
    limit_each: int,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str, str, str]] = set()
    for rank_type, rows in (("relative", top_relative[:limit_each]), ("absolute", top_absolute[:limit_each])):
        for rank, row in enumerate(rows, start=1):
            key = (
                rank_type,
                row["metric"],
                row["model_id"],
                row["story_id"],
                row["emotion"],
                str(rank),
            )
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "rank_type": rank_type,
                    "rank": rank,
                    "metric": row["metric"],
                    "model_id": row["model_id"],
                    "model_label": compact_model_label(row["model_id"]),
                    "story_id": row["story_id"],
                    "emotion": row["emotion"],
                    "SS_persona": row["SS_persona"],
                    "SS_temperature": row["SS_temperature"],
                    "SS_persona_x_temperature": row["SS_persona_x_temperature"],
                    "total_SS": row["total_SS"],
                    "interaction_burden": row["interaction_burden"],
                    "separability_share": row["separability_share"],
                }
            )
    return out


def build_entropy_sensitivity_table(
    entropy_family_comparison: list[dict[str, str]],
    analysis_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    hmax = analysis_summary["membership_hmax"]
    for row in entropy_family_comparison:
        primary = row["primary_family"]
        baseline = row["baseline_family"]
        out.append(
            {
                "primary_family": primary,
                "baseline_family": baseline,
                "primary_Hmax": hmax[primary],
                "baseline_Hmax": hmax[baseline],
                "n_cell_pairs": row["n_cell_pairs"],
                "pearson_H_norm_cell_mean": row["pearson_H_norm_cell_mean"],
                "mean_abs_H_norm_diff": row["mean_abs_H_norm_diff"],
                "max_abs_H_norm_diff": row["max_abs_H_norm_diff"],
            }
        )
    return out


def write_latex_outputs(
    *,
    output_dir: Path,
    run_validity: list[dict[str, Any]],
    effect_summary: list[dict[str, Any]],
    model_metric: list[dict[str, Any]],
    entropy_sensitivity: list[dict[str, Any]],
    top_cases: list[dict[str, Any]],
) -> None:
    validity = run_validity[0]
    write_latex_table(
        path=output_dir / "table1_run_validity.tex",
        caption="SCIS main-run validity and completeness.",
        label="tab:scis-validity",
        headers=["Resp.", "Valid", "Rate", "Emo. rows", "Miss. scores", "Miss. cells"],
        rows=[
            [
                str(validity["response_rows"]),
                str(validity["response_ok"]),
                pct(validity["valid_output_rate"]),
                str(validity["emotion_rows"]),
                str(validity["missing_score_rows"]),
                str(validity["missing_structural_cells"]),
            ]
        ],
        alignment="rrrrrr",
    )

    effect_rows = [
        [
            metric_label(row["metric"]),
            emotion_label(row["emotion"]),
            str(row["n_units"]),
            pct(row["mean_persona_share"]),
            pct(row["mean_temperature_share"]),
            pct(row["mean_interaction_burden"]),
            pct(row["mean_separability_share"]),
        ]
        for row in effect_summary
    ]
    write_latex_table(
        path=output_dir / "table2_effect_summary.tex",
        caption=(
            "Balanced persona-temperature effect decomposition by metric and emotion. "
            "Entropy rows use the primary sigmoid-S membership family."
        ),
        label="tab:scis-effect-summary",
        headers=["Metric", "Emotion", "$n$", "Persona", "Temp.", "Interaction", "Separability"],
        rows=effect_rows,
        alignment="llrrrrr",
        table_star=True,
    )

    model_rows = [
        [
            latex_escape(row["model_label"]),
            metric_label(row["metric"]),
            str(row["n_units"]),
            pct(row["mean_persona_share"]),
            pct(row["mean_temperature_share"]),
            pct(row["mean_interaction_burden"]),
            pct(row["max_interaction_burden"]),
        ]
        for row in model_metric
    ]
    write_latex_table(
        path=output_dir / "table3_model_metric_summary.tex",
        caption="Model-level mean decomposition shares by metric.",
        label="tab:scis-model-summary",
        headers=["Model", "Metric", "$n$", "Persona", "Temp.", "Mean int.", "Max int."],
        rows=model_rows,
        alignment="llrrrrr",
        table_star=True,
    )

    sensitivity_rows = [
        [
            latex_escape(row["primary_family"]),
            latex_escape(row["baseline_family"]),
            str(row["n_cell_pairs"]),
            fmt(row["primary_Hmax"]),
            fmt(row["baseline_Hmax"]),
            fmt(row["pearson_H_norm_cell_mean"]),
            fmt(row["mean_abs_H_norm_diff"]),
            fmt(row["max_abs_H_norm_diff"]),
        ]
        for row in entropy_sensitivity
    ]
    write_latex_table(
        path=output_dir / "table4_entropy_sensitivity.tex",
        caption=(
            "Normalized fuzzy entropy sensitivity to membership-family choice. "
            "$n=1152$ denotes model-text-persona-temperature-emotion cell means; "
            "$H_{\\max,P}$ and $H_{\\max,B}$ are the family-specific normalization "
            "constants for the primary and baseline families, respectively; "
            "$r$ is the cell-mean correlation."
        ),
        label="tab:scis-entropy-sensitivity",
        headers=["Primary", "Baseline", "$n$", "$H_{\\max,P}$", "$H_{\\max,B}$", "$r$", "Mean $|\\Delta|$", "Max $|\\Delta|$"],
        rows=sensitivity_rows,
        alignment="llrrrrrr",
        table_star=True,
    )

    top_rows = [
        [
            latex_escape(row["rank_type"]),
            str(row["rank"]),
            metric_label(row["metric"]),
            latex_escape(row["model_label"]),
            latex_escape(row["story_id"]),
            emotion_label(row["emotion"]),
            fmt(row["SS_persona_x_temperature"]),
            pct(row["interaction_burden"]),
        ]
        for row in top_cases[:12]
    ]
    write_latex_table(
        path=output_dir / "table5_top_interaction_cases.tex",
        caption="Largest relative and absolute persona-temperature interaction cases.",
        label="tab:scis-top-interactions",
        headers=["Type", "Rank", "Metric", "Model", "Text", "Emotion", "SS int.", "Burden"],
        rows=top_rows,
        alignment="rrlllrrr",
        table_star=True,
    )


def markdown_table(rows: list[dict[str, Any]], columns: list[str], *, limit: int | None = None) -> str:
    shown = rows[:limit] if limit is not None else rows
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in shown:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def write_phase_doc(
    *,
    path: Path,
    summary: dict[str, Any],
    run_validity: list[dict[str, Any]],
    effect_summary: list[dict[str, Any]],
    entropy_sensitivity: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# SCIS Phase 7 Primary Tables

This document records the construction of primary paper-table candidates from
the SCIS 2026 main-run inspection artifacts. These tables are descriptive and
are intended to guide manuscript drafting before bootstrap confidence intervals
are added.

## Inputs

- Main analysis: `artifacts/scis2026/main_analysis_v1/`
- Main inspection: `artifacts/scis2026/main_inspection_v1/`
- Primary tables: `artifacts/scis2026/main_tables_v1/`

## Generated Tables

- `table1_run_validity`: run completeness and valid-output rate.
- `table2_effect_summary`: metric x emotion persona-temperature decomposition
  shares.
- `table3_model_metric_summary`: model x metric decomposition shares.
- `table4_entropy_sensitivity`: `sigmoid_s_v1` versus `legacy_linear_v1`
  normalized entropy comparison.
- `table5_top_interaction_cases`: largest relative and absolute interaction
  cases for figure and appendix selection.

Each table is written as both CSV and LaTeX (`.tex`) output.

## Run Validity

{markdown_table(run_validity, [
        "response_rows",
        "response_ok",
        "valid_output_rate",
        "emotion_rows",
        "missing_score_rows",
        "missing_structural_cells",
    ])}

## Effect Summary

{markdown_table(effect_summary, [
        "metric",
        "emotion",
        "n_units",
        "mean_persona_share",
        "mean_temperature_share",
        "mean_interaction_burden",
        "mean_separability_share",
    ])}

## Entropy Sensitivity

{markdown_table(entropy_sensitivity, [
        "primary_family",
        "baseline_family",
        "n_cell_pairs",
        "pearson_H_norm_cell_mean",
        "mean_abs_H_norm_diff",
        "max_abs_H_norm_diff",
    ])}

## Construction Summary

```json
{json.dumps(summary, ensure_ascii=False, indent=2)}
```
"""
    path.write_text(body, encoding="utf-8")


def ensure_inspection(
    *,
    analysis_dir: Path,
    inspection_dir: Path,
    primary_family: str,
) -> None:
    required = [
        inspection_dir / "metric_decomposition.csv",
        inspection_dir / "top_interaction_burdens.csv",
        inspection_dir / "top_absolute_interactions.csv",
        inspection_dir / "inspection_summary.json",
    ]
    if all(path.exists() for path in required):
        return
    run_inspection(
        analysis_dir=analysis_dir,
        output_dir=inspection_dir,
        doc_path=Path("docs/scis2026/phase6_main_result_inspection.md"),
        primary_family=primary_family,
        top_n=20,
    )


def build_primary_tables(
    *,
    analysis_dir: Path,
    inspection_dir: Path,
    output_dir: Path,
    doc_path: Path,
    primary_family: str,
    top_case_limit_each: int,
) -> dict[str, Any]:
    ensure_inspection(
        analysis_dir=analysis_dir,
        inspection_dir=inspection_dir,
        primary_family=primary_family,
    )
    analysis_summary = load_json(analysis_dir / "analysis_summary.json")
    metric_decomposition = load_csv(inspection_dir / "metric_decomposition.csv")
    top_relative = load_csv(inspection_dir / "top_interaction_burdens.csv")
    top_absolute = load_csv(inspection_dir / "top_absolute_interactions.csv")
    entropy_family_comparison = load_csv(analysis_dir / "entropy_family_comparison.csv")

    run_validity = build_run_validity_table(analysis_summary)
    effect_summary = build_effect_summary_table(metric_decomposition)
    model_metric = build_model_metric_table(metric_decomposition)
    top_cases = build_top_case_table(top_relative, top_absolute, limit_each=top_case_limit_each)
    entropy_sensitivity = build_entropy_sensitivity_table(entropy_family_comparison, analysis_summary)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(run_validity, output_dir / "table1_run_validity.csv")
    write_csv(effect_summary, output_dir / "table2_effect_summary.csv")
    write_csv(model_metric, output_dir / "table3_model_metric_summary.csv")
    write_csv(entropy_sensitivity, output_dir / "table4_entropy_sensitivity.csv")
    write_csv(top_cases, output_dir / "table5_top_interaction_cases.csv")

    write_latex_outputs(
        output_dir=output_dir,
        run_validity=run_validity,
        effect_summary=effect_summary,
        model_metric=model_metric,
        entropy_sensitivity=entropy_sensitivity,
        top_cases=top_cases,
    )

    summary = {
        "analysis_dir": str(analysis_dir),
        "inspection_dir": str(inspection_dir),
        "output_dir": str(output_dir),
        "primary_family": primary_family,
        "n_run_validity_rows": len(run_validity),
        "n_effect_summary_rows": len(effect_summary),
        "n_model_metric_rows": len(model_metric),
        "n_entropy_sensitivity_rows": len(entropy_sensitivity),
        "n_top_case_rows": len(top_cases),
        "latex_tables": [
            "table1_run_validity.tex",
            "table2_effect_summary.tex",
            "table3_model_metric_summary.tex",
            "table4_entropy_sensitivity.tex",
            "table5_top_interaction_cases.tex",
        ],
    }
    (output_dir / "primary_table_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_phase_doc(
        path=doc_path,
        summary=summary,
        run_validity=run_validity,
        effect_summary=effect_summary,
        entropy_sensitivity=entropy_sensitivity,
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--inspection-dir", default=DEFAULT_INSPECTION_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--doc", default=DEFAULT_DOC)
    parser.add_argument("--primary-family", default=DEFAULT_PRIMARY_FAMILY)
    parser.add_argument("--top-case-limit-each", type=int, default=8)
    args = parser.parse_args()

    summary = build_primary_tables(
        analysis_dir=Path(args.analysis_dir),
        inspection_dir=Path(args.inspection_dir),
        output_dir=Path(args.output_dir),
        doc_path=Path(args.doc),
        primary_family=args.primary_family,
        top_case_limit_each=args.top_case_limit_each,
    )
    print(f"Wrote primary tables to {Path(args.output_dir).resolve()}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
