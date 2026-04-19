from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
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

INPUT_PATH = RESULTS_CSV_DIR / "ja_primary_ranking.csv"
OUTPUT_STEM = PAPER_FIG_DIR / "figure2_ja_ranking"
X_LABEL = "Mean absolute error to Japanese human reference (lower is better)"


def load_ranking(path: Path = INPUT_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    columns = require_columns(
        df,
        {
            "model": ["model_id", "model"],
            "mae": ["mae_to_human", "mae"],
        },
        str(path),
    )

    out = pd.DataFrame(
        {
            "Model": df[columns["model"]].map(display_model_name),
            "MAE": numeric_series(df, columns["mae"], str(path)),
        }
    )
    return out.sort_values("MAE", ascending=True).reset_index(drop=True)


def save_figure(ranking: pd.DataFrame, output_stem: Path = OUTPUT_STEM) -> list[Path]:
    ensure_dir(output_stem.parent)

    fig_height = max(3.2, 0.45 * len(ranking) + 1.4)
    fig, ax = plt.subplots(figsize=(7.0, fig_height))
    ax.barh(ranking["Model"], ranking["MAE"])
    ax.invert_yaxis()
    ax.set_xlabel(X_LABEL)
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle=":", linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()

    output_paths = [output_stem.with_suffix(".png"), output_stem.with_suffix(".pdf")]
    for output_path in output_paths:
        fig.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return output_paths


def main() -> None:
    ranking = load_ranking()
    output_paths = save_figure(ranking)
    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
