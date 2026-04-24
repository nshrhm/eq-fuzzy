from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.iceccme2026.paper_exports import (
    PAPER_TABLES_DIR,
    RESULTS_CSV_DIR,
    RESULTS_TABLES_DIR,
    display_model_name,
    ensure_dir,
    latex_escape,
    numeric_series,
    require_columns,
)

RANKING_INPUT_PATH = RESULTS_CSV_DIR / "ja_primary_ranking.csv"
DRIFT_INPUT_PATH = RESULTS_CSV_DIR / "model_language_drift_vs_ja.csv"
CSV_OUTPUT_PATH = RESULTS_TABLES_DIR / "table2_primary_summary.csv"
TEX_OUTPUT_PATH = PAPER_TABLES_DIR / "table2_primary_summary.tex"

OUTPUT_COLUMNS = ["Model", "JA MAE", "JA Pearson r", "JA Spearman ρ", "EN drift", "ZH drift"]


def load_table2(
    ranking_path: Path = RANKING_INPUT_PATH,
    drift_path: Path = DRIFT_INPUT_PATH,
) -> pd.DataFrame:
    ranking = pd.read_csv(ranking_path)
    ranking_columns = require_columns(
        ranking,
        {
            "model": ["model_id", "model"],
            "mae": ["mae_to_human", "mae"],
            "pearson": ["pearson_to_human", "pearson_r", "pearson"],
            "spearman": ["spearman_to_human", "spearman_r", "spearman"],
        },
        str(ranking_path),
    )

    primary = pd.DataFrame(
        {
            "model": ranking[ranking_columns["model"]].astype(str),
            "JA MAE": numeric_series(ranking, ranking_columns["mae"], str(ranking_path)),
            "JA Pearson r": numeric_series(ranking, ranking_columns["pearson"], str(ranking_path)),
            "JA Spearman ρ": numeric_series(ranking, ranking_columns["spearman"], str(ranking_path)),
        }
    )

    drift = pd.read_csv(drift_path)
    drift_columns = require_columns(
        drift,
        {
            "model": ["model_id", "model"],
            "language": ["lang", "language"],
            "drift": ["drift_vs_ja", "mean_drift_vs_japanese", "mean_drift_vs_ja"],
        },
        str(drift_path),
    )
    drift_values = pd.DataFrame(
        {
            "model": drift[drift_columns["model"]].astype(str),
            "language": drift[drift_columns["language"]].astype(str).str.lower(),
            "drift": numeric_series(drift, drift_columns["drift"], str(drift_path)),
        }
    )
    drift_values = drift_values[drift_values["language"].isin(["en", "zh"])].copy()
    drift_wide = drift_values.pivot(index="model", columns="language", values="drift").reset_index()
    drift_wide = drift_wide.rename(columns={"en": "EN drift", "zh": "ZH drift"})

    table = primary.merge(drift_wide, on="model", how="left")
    table = table.sort_values("JA MAE", ascending=True)
    table.insert(0, "Model", table["model"].map(display_model_name))
    table = table[OUTPUT_COLUMNS].copy()

    numeric_columns = [column for column in OUTPUT_COLUMNS if column != "Model"]
    table[numeric_columns] = table[numeric_columns].round(3)
    return table.reset_index(drop=True)


def format_number(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.3f}"


def write_latex_tabular(table: pd.DataFrame, output_path: Path = TEX_OUTPUT_PATH) -> None:
    ensure_dir(output_path.parent)
    header = ["Model", "JA MAE", "JA Pearson r", r"JA Spearman $\rho$", "EN drift", "ZH drift"]
    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        " & ".join(header) + r" \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        cells = [latex_escape(row["Model"])]
        cells.extend(format_number(row[column]) for column in OUTPUT_COLUMNS[1:])
        lines.append(" & ".join(cells) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def export_table2(table: pd.DataFrame) -> list[Path]:
    ensure_dir(CSV_OUTPUT_PATH.parent)
    ensure_dir(TEX_OUTPUT_PATH.parent)
    table.to_csv(CSV_OUTPUT_PATH, index=False, float_format="%.3f")
    write_latex_tabular(table, TEX_OUTPUT_PATH)
    return [CSV_OUTPUT_PATH, TEX_OUTPUT_PATH]


def main() -> None:
    table = load_table2()
    output_paths = export_table2(table)
    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
