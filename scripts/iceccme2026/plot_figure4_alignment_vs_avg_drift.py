from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("MPLCONFIGDIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "iceccme2026-matplotlib"))

import matplotlib.pyplot as plt
import pandas as pd

from src.iceccme2026.paper_exports import (
    PAPER_FIG_DIR,
    RESULTS_CSV_DIR,
    display_model_name,
    ensure_dir,
    numeric_series,
    require_columns,
)

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

RANKING_INPUT_PATH = RESULTS_CSV_DIR / "ja_primary_ranking.csv"
DRIFT_INPUT_PATH = RESULTS_CSV_DIR / "model_language_drift_vs_ja.csv"
OUTPUT_STEM = PAPER_FIG_DIR / "figure4_alignment_vs_avg_drift"
FIGURE_DATA_PATH = PAPER_FIG_DIR / "figure_data.csv"
X_LABEL = "JA human-alignment MAE (lower is better)"
Y_LABEL = "Average EN/ZH drift vs JA (lower is better)"
LABEL_OFFSETS = {
    "Qwen3.6 Plus": (8, -16),
    "GPT-5.4": (8, 11),
    "Gemini 2.5 Pro": (-76, 3),
}


def load_tradeoff(
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
            "model_id": ranking[ranking_columns["model"]].astype(str),
            "ja_mae": numeric_series(ranking, ranking_columns["mae"], str(ranking_path)),
            "ja_pearson": numeric_series(ranking, ranking_columns["pearson"], str(ranking_path)),
            "ja_spearman": numeric_series(ranking, ranking_columns["spearman"], str(ranking_path)),
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
            "model_id": drift[drift_columns["model"]].astype(str),
            "language": drift[drift_columns["language"]].astype(str).str.lower(),
            "drift": numeric_series(drift, drift_columns["drift"], str(drift_path)),
        }
    )
    drift_values = drift_values[drift_values["language"].isin(["en", "zh"])].copy()
    drift_wide = drift_values.pivot(index="model_id", columns="language", values="drift").reset_index()
    drift_wide = drift_wide.rename(columns={"en": "en_drift", "zh": "zh_drift"})
    drift_wide["avg_drift"] = drift_wide[["en_drift", "zh_drift"]].mean(axis=1)

    tradeoff = primary.merge(drift_wide, on="model_id", how="inner")
    tradeoff["model"] = tradeoff["model_id"].map(display_model_name)
    return tradeoff.sort_values("ja_mae", ascending=True).reset_index(drop=True)


def save_figure_data(tradeoff: pd.DataFrame, path: Path = FIGURE_DATA_PATH) -> Path:
    ensure_dir(path.parent)
    columns = ["model", "ja_mae", "ja_pearson", "ja_spearman", "en_drift", "zh_drift", "avg_drift"]
    tradeoff.loc[:, columns].to_csv(path, index=False, float_format="%.3f")
    return path


def save_figure(tradeoff: pd.DataFrame, output_stem: Path = OUTPUT_STEM) -> list[Path]:
    ensure_dir(output_stem.parent)

    fig, ax = plt.subplots(figsize=(4.9, 3.35))
    ax.scatter(tradeoff["ja_mae"], tradeoff["avg_drift"], s=52)
    for row in tradeoff.itertuples(index=False):
        label_offset = LABEL_OFFSETS.get(row.model, (5, 3))
        ax.annotate(
            row.model,
            (row.ja_mae, row.avg_drift),
            xytext=label_offset,
            textcoords="offset points",
            fontsize=8,
            arrowprops=(
                {
                    "arrowstyle": "-",
                    "color": "0.45",
                    "linewidth": 0.5,
                    "shrinkA": 0,
                    "shrinkB": 3,
                }
                if row.model in LABEL_OFFSETS
                else None
            ),
        )
    ax.set_xlabel(X_LABEL)
    ax.set_ylabel(Y_LABEL)
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.set_axisbelow(True)

    x_margin = 0.7
    y_margin = 0.4
    ax.set_xlim(tradeoff["ja_mae"].min() - x_margin, tradeoff["ja_mae"].max() + x_margin)
    ax.set_ylim(2.5, tradeoff["avg_drift"].max() + y_margin)
    fig.tight_layout()

    output_paths = [output_stem.with_suffix(".png"), output_stem.with_suffix(".pdf")]
    for output_path in output_paths:
        fig.savefig(output_path, bbox_inches="tight", pad_inches=0.02, dpi=300)
    plt.close(fig)
    return output_paths


def main() -> None:
    tradeoff = load_tradeoff()
    output_paths = [save_figure_data(tradeoff), *save_figure(tradeoff)]
    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
