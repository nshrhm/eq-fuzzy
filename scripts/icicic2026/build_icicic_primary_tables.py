from __future__ import annotations

"""Build ICICIC manuscript-facing primary tables from matched-subset analysis outputs."""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_ANALYSIS_DIR = "artifacts/icicic2026/matched_subset_stable6_analysis_v1"
DEFAULT_OUTPUT_DIR = "artifacts/icicic2026/main_tables_v1"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def tex_escape(value: Any) -> str:
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


def write_tex_table(
    rows: list[dict[str, Any]],
    columns: list[str],
    path: Path,
    *,
    column_labels: dict[str, str] | None = None,
) -> None:
    if not rows:
        path.write_text("% No rows available.\n", encoding="utf-8")
        return
    labels = column_labels or {}
    lines = [
        r"\begin{tabular}{" + "l" * len(columns) + "}",
        r"\hline",
        " & ".join(tex_escape(labels.get(col, col.replace("_", " "))) for col in columns) + r" \\",
        r"\hline",
    ]
    for row in rows:
        lines.append(" & ".join(tex_escape(row.get(col, "")) for col in columns) + r" \\")
    lines.extend([r"\hline", r"\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def round_or_blank(value: str, digits: int = 6) -> str:
    if value in ("", None):
        return ""
    return str(round(float(value), digits))


def build_model_table(model_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in model_rows:
        out.append(
            {
                "model_id": row["model_id"],
                "valid_output_rate": round_or_blank(row["valid_output_rate"]),
                "mean_within_cell_sd_score": round_or_blank(row["mean_within_cell_sd_score"]),
                "mean_cell_H_norm": round_or_blank(row["mean_cell_H_norm"]),
                "mean_profile_entropy": round_or_blank(row["mean_profile_entropy"]),
                "mean_target_shift_abs": round_or_blank(row["mean_target_shift_abs"]),
            }
        )
    return out


def build_target_shift_summary(target_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in target_rows:
        grouped[(row["model_id"], row["emotion"])].append(float(row["target_shift_abs"]))
    out: list[dict[str, Any]] = []
    for (model_id, emotion), values in sorted(grouped.items()):
        out.append(
            {
                "model_id": model_id,
                "emotion": emotion,
                "n_cells": len(values),
                "mean_target_shift_abs": round(mean(values), 6),
                "max_target_shift_abs": round(max(values), 6),
            }
        )
    return out


def build_valid_output_table(cell_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in cell_rows:
        grouped[(row["model_id"], row["target_mode"])].append(float(row["valid_output_rate"]))
    out: list[dict[str, Any]] = []
    for (model_id, target_mode), values in sorted(grouped.items()):
        out.append(
            {
                "model_id": model_id,
                "target_mode": target_mode,
                "n_cells": len(values),
                "mean_valid_output_rate": round(mean(values), 6),
                "min_valid_output_rate": round(min(values), 6),
            }
        )
    return out


def build_primary_tables(*, analysis_dir: Path, output_dir: Path) -> dict[str, Any]:
    model_rows = load_csv(analysis_dir / "model_summary.csv")
    target_rows = load_csv(analysis_dir / "target_shift.csv")
    cell_rows = load_csv(analysis_dir / "cell_summary.csv")

    output_dir.mkdir(parents=True, exist_ok=True)
    model_table = build_model_table(model_rows)
    target_table = build_target_shift_summary(target_rows)
    valid_table = build_valid_output_table(cell_rows)

    write_csv(model_table, output_dir / "table2_model_added_descriptors.csv")
    write_csv(target_table, output_dir / "table3_target_shift_by_model_emotion.csv")
    write_csv(valid_table, output_dir / "table4_valid_output_by_target_mode.csv")

    write_tex_table(
        model_table,
        [
            "model_id",
            "valid_output_rate",
            "mean_within_cell_sd_score",
            "mean_cell_H_norm",
            "mean_profile_entropy",
            "mean_target_shift_abs",
        ],
        output_dir / "table2_model_added_descriptors.tex",
        column_labels={
            "model_id": "Model",
            "valid_output_rate": "Valid",
            "mean_within_cell_sd_score": "Mean SD",
            "mean_cell_H_norm": "Cell H",
            "mean_profile_entropy": "Profile H",
            "mean_target_shift_abs": "Shift",
        },
    )
    write_tex_table(
        target_table,
        ["model_id", "emotion", "n_cells", "mean_target_shift_abs", "max_target_shift_abs"],
        output_dir / "table3_target_shift_by_model_emotion.tex",
        column_labels={
            "model_id": "Model",
            "emotion": "Emotion",
            "n_cells": "n",
            "mean_target_shift_abs": "Mean shift",
            "max_target_shift_abs": "Max shift",
        },
    )
    write_tex_table(
        valid_table,
        ["model_id", "target_mode", "n_cells", "mean_valid_output_rate", "min_valid_output_rate"],
        output_dir / "table4_valid_output_by_target_mode.tex",
        column_labels={
            "model_id": "Model",
            "target_mode": "Target",
            "n_cells": "n",
            "mean_valid_output_rate": "Mean valid",
            "min_valid_output_rate": "Min valid",
        },
    )

    summary = {
        "table_set": "icicic2026_main_tables_v1",
        "analysis_dir": str(analysis_dir),
        "output_dir": str(output_dir),
        "n_model_rows": len(model_table),
        "n_target_shift_rows": len(target_table),
        "n_valid_output_rows": len(valid_table),
        "claim_discipline": "descriptive added descriptors only",
    }
    (output_dir / "primary_table_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--analysis-dir", default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    summary = build_primary_tables(
        analysis_dir=repo_root / args.analysis_dir,
        output_dir=repo_root / args.output_dir,
    )
    print(f"Wrote ICICIC primary tables to {summary['output_dir']}")


if __name__ == "__main__":
    main()
