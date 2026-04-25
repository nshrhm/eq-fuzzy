from __future__ import annotations

"""Bootstrap confidence intervals for SCIS main-run primary effect summaries."""

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from analyze_factorial_scores import (
    add_primary_entropy_columns,
    build_cell_summary,
    build_entropy_cell_summary,
    build_entropy_rows,
    expand_emotion_rows,
    hmax_by_family,
    load_jsonl,
    load_membership_config,
    write_csv,
)
from build_primary_tables import build_effect_summary_table, pct, write_latex_table
from inspect_main_results import build_metric_decomposition, load_csv


DEFAULT_INPUT = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw_repaired.jsonl"
DEFAULT_MEMBERSHIP_CONFIG = "configs/scis/fuzzy_membership_v1.yaml"
DEFAULT_PRIMARY_TABLE = "artifacts/scis2026/main_tables_v1/table2_effect_summary.csv"
DEFAULT_OUTPUT_DIR = "artifacts/scis2026/main_bootstrap_v1"
DEFAULT_DOC = "docs/scis2026/phase9_bootstrap_ci.md"
DEFAULT_PRIMARY_FAMILY = "sigmoid_s_v1"
DEFAULT_N_BOOTSTRAP = 500
DEFAULT_SEED = 20260425
CI_LEVEL = 0.95
NORMAL_Z_95 = 1.959963984540054


def response_cell_key(record: dict[str, Any]) -> tuple[str, str, str, float]:
    return (
        str(record["model_id"]),
        str(record["story_id"]),
        str(record["persona_id"]),
        float(record["temperature"]),
    )


def group_records_by_cell(records: list[dict[str, Any]]) -> dict[tuple[str, str, str, float], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, str, float], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[response_cell_key(record)].append(record)
    return dict(sorted(grouped.items()))


def resample_records(
    grouped: dict[tuple[str, str, str, float], list[dict[str, Any]]],
    *,
    rng: random.Random,
) -> list[dict[str, Any]]:
    sampled: list[dict[str, Any]] = []
    for records in grouped.values():
        sampled.extend(rng.choice(records) for _ in records)
    return sampled


def metric_decomposition_for_records(
    records: list[dict[str, Any]],
    *,
    primary_family: str,
    hmax: float,
) -> list[dict[str, Any]]:
    emotion_rows = expand_emotion_rows(records)
    add_primary_entropy_columns(emotion_rows, primary_family=primary_family, hmax=hmax)
    score_cells = build_cell_summary(emotion_rows)
    entropy_rows = build_entropy_rows(
        emotion_rows,
        families=[primary_family],
        hmaxes={primary_family: hmax},
    )
    entropy_cells = build_entropy_cell_summary(entropy_rows)
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
    return score_decomposition + entropy_decomposition


def normalize_estimable_flags(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        out = dict(row)
        out["is_estimable"] = "True" if row["is_estimable"] is True else str(row["is_estimable"])
        normalized.append(out)
    return normalized


def effect_summary_for_records(
    records: list[dict[str, Any]],
    *,
    primary_family: str,
    hmax: float,
) -> list[dict[str, Any]]:
    decomposition = metric_decomposition_for_records(
        records,
        primary_family=primary_family,
        hmax=hmax,
    )
    return build_effect_summary_table(normalize_estimable_flags(decomposition))


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row["metric"]), str(row["emotion"])


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("Cannot compute percentile of an empty list")
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = q * (len(sorted_values) - 1)
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def format_ci_rows(
    *,
    point_rows: list[dict[str, Any]],
    bootstrap_rows: list[list[dict[str, Any]]],
    columns: list[str],
) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str], dict[str, Any]] = {row_key(row): row for row in point_rows}
    samples: dict[tuple[str, str], dict[str, list[float]]] = {
        key: {column: [] for column in columns}
        for key in by_key
    }
    for replicate in bootstrap_rows:
        replicate_by_key = {row_key(row): row for row in replicate}
        for key in by_key:
            row = replicate_by_key[key]
            for column in columns:
                samples[key][column].append(float(row[column]))

    out: list[dict[str, Any]] = []
    alpha = (1.0 - CI_LEVEL) / 2.0
    for key, point_row in sorted(by_key.items()):
        row: dict[str, Any] = {
            "metric": point_row["metric"],
            "emotion": point_row["emotion"],
            "n_units": point_row["n_units"],
        }
        for column in columns:
            values = samples[key][column]
            point = float(point_row[column])
            pct_low = percentile(values, alpha)
            pct_high = percentile(values, 1.0 - alpha)
            basic_low = 2.0 * point - pct_high
            basic_high = 2.0 * point - pct_low
            sd = pstdev(values)
            normal_low = point - NORMAL_Z_95 * sd
            normal_high = point + NORMAL_Z_95 * sd
            row[f"{column}_point"] = round(point, 9)
            row[f"{column}_boot_mean"] = round(mean(values), 9)
            row[f"{column}_boot_sd"] = round(sd, 9)
            row[f"{column}_percentile_ci_low"] = round(pct_low, 9)
            row[f"{column}_percentile_ci_high"] = round(pct_high, 9)
            row[f"{column}_basic_ci_low"] = round(basic_low, 9)
            row[f"{column}_basic_ci_high"] = round(basic_high, 9)
            row[f"{column}_normal_ci_low"] = round(normal_low, 9)
            row[f"{column}_normal_ci_high"] = round(normal_high, 9)
        out.append(row)
    return out


def write_effect_ci_latex(rows: list[dict[str, Any]], path: Path) -> None:
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                str(row["metric"]).replace("_", r"\_"),
                str(row["emotion"]).title(),
                str(row["n_units"]),
                (
                    f"{pct(row['mean_persona_share_point'])} "
                    f"[{pct(row['mean_persona_share_normal_ci_low'])}, "
                    f"{pct(row['mean_persona_share_normal_ci_high'])}]"
                ),
                (
                    f"{pct(row['mean_temperature_share_point'])} "
                    f"[{pct(row['mean_temperature_share_normal_ci_low'])}, "
                    f"{pct(row['mean_temperature_share_normal_ci_high'])}]"
                ),
                (
                    f"{pct(row['mean_interaction_burden_point'])} "
                    f"[{pct(row['mean_interaction_burden_normal_ci_low'])}, "
                    f"{pct(row['mean_interaction_burden_normal_ci_high'])}]"
                ),
                (
                    f"{pct(row['mean_separability_share_point'])} "
                    f"[{pct(row['mean_separability_share_normal_ci_low'])}, "
                    f"{pct(row['mean_separability_share_normal_ci_high'])}]"
                ),
            ]
        )
    write_latex_table(
        path=path,
        caption="Bootstrap confidence intervals for primary persona-temperature decomposition shares.",
        label="tab:scis-bootstrap-ci",
        headers=["Metric", "Emotion", "$n$", "Persona", "Temp.", "Interaction", "Separability"],
        rows=table_rows,
        alignment="llrllll",
        table_star=True,
    )


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def write_doc(
    *,
    path: Path,
    summary: dict[str, Any],
    ci_rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# SCIS Phase 9 Bootstrap Confidence Intervals

This phase adds uncertainty estimates to the primary descriptive effect
summaries. The bootstrap keeps model, text, persona, and temperature cells
fixed, resamples repeats within each cell, and preserves the four emotion
scores from the same response as a block. Machine-readable outputs include
percentile, basic, and point-centered normal bootstrap intervals; the
manuscript-facing LaTeX table uses the point-centered normal intervals for
readability.

## Outputs

- `artifacts/scis2026/main_bootstrap_v1/effect_summary_bootstrap_ci.csv`
- `artifacts/scis2026/main_bootstrap_v1/effect_summary_bootstrap_ci.tex`
- `artifacts/scis2026/main_bootstrap_v1/bootstrap_summary.json`

## Primary CI Summary

{markdown_table(ci_rows, [
        "metric",
        "emotion",
        "mean_persona_share_point",
        "mean_persona_share_normal_ci_low",
        "mean_persona_share_normal_ci_high",
        "mean_temperature_share_point",
        "mean_temperature_share_normal_ci_low",
        "mean_temperature_share_normal_ci_high",
        "mean_interaction_burden_point",
        "mean_interaction_burden_normal_ci_low",
        "mean_interaction_burden_normal_ci_high",
    ])}

## Construction Summary

```json
{json.dumps(summary, ensure_ascii=False, indent=2)}
```
"""
    path.write_text(body, encoding="utf-8")


def run_bootstrap(
    *,
    input_jsonl: Path,
    membership_config: Path,
    primary_table: Path,
    output_dir: Path,
    doc_path: Path,
    primary_family: str,
    n_bootstrap: int,
    seed: int,
) -> dict[str, Any]:
    records = load_jsonl(input_jsonl)
    grouped = group_records_by_cell(records)
    config = load_membership_config(membership_config)
    hmaxes = hmax_by_family(config)
    hmax = hmaxes[primary_family]
    rng = random.Random(seed)
    point_rows = [
        {
            "metric": row["metric"],
            "emotion": row["emotion"],
            "n_units": int(row["n_units"]),
            "mean_persona_share": float(row["mean_persona_share"]),
            "mean_temperature_share": float(row["mean_temperature_share"]),
            "mean_interaction_burden": float(row["mean_interaction_burden"]),
            "mean_separability_share": float(row["mean_separability_share"]),
        }
        for row in load_csv(primary_table)
    ]
    bootstrap_rows: list[list[dict[str, Any]]] = []
    for _ in range(n_bootstrap):
        sampled_records = resample_records(grouped, rng=rng)
        bootstrap_rows.append(
            effect_summary_for_records(
                sampled_records,
                primary_family=primary_family,
                hmax=hmax,
            )
        )

    columns = [
        "mean_persona_share",
        "mean_temperature_share",
        "mean_interaction_burden",
        "mean_separability_share",
    ]
    ci_rows = format_ci_rows(
        point_rows=point_rows,
        bootstrap_rows=bootstrap_rows,
        columns=columns,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(ci_rows, output_dir / "effect_summary_bootstrap_ci.csv")
    write_effect_ci_latex(ci_rows, output_dir / "effect_summary_bootstrap_ci.tex")
    summary = {
        "input_jsonl": str(input_jsonl),
        "membership_config": str(membership_config),
        "primary_table": str(primary_table),
        "output_dir": str(output_dir),
        "primary_family": primary_family,
        "n_records": len(records),
        "n_cells": len(grouped),
        "cell_sizes": sorted({len(cell_records) for cell_records in grouped.values()}),
        "n_bootstrap": n_bootstrap,
        "seed": seed,
        "ci_level": CI_LEVEL,
        "latex_ci_method": "point_centered_normal_bootstrap",
        "n_ci_rows": len(ci_rows),
    }
    (output_dir / "bootstrap_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_doc(path=doc_path, summary=summary, ci_rows=ci_rows)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", default=DEFAULT_INPUT)
    parser.add_argument("--membership-config", default=DEFAULT_MEMBERSHIP_CONFIG)
    parser.add_argument("--primary-table", default=DEFAULT_PRIMARY_TABLE)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--doc", default=DEFAULT_DOC)
    parser.add_argument("--primary-family", default=DEFAULT_PRIMARY_FAMILY)
    parser.add_argument("--n-bootstrap", type=int, default=DEFAULT_N_BOOTSTRAP)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    summary = run_bootstrap(
        input_jsonl=Path(args.input_jsonl),
        membership_config=Path(args.membership_config),
        primary_table=Path(args.primary_table),
        output_dir=Path(args.output_dir),
        doc_path=Path(args.doc),
        primary_family=args.primary_family,
        n_bootstrap=args.n_bootstrap,
        seed=args.seed,
    )
    print(f"Wrote bootstrap artifacts to {Path(args.output_dir).resolve()}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
