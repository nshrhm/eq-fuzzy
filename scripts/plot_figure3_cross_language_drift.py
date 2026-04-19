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

DRIFT_INPUT_PATH = RESULTS_CSV_DIR / "model_language_drift_vs_ja.csv"
RANKING_INPUT_PATH = RESULTS_CSV_DIR / "ja_primary_ranking.csv"
OUTPUT_STEM = PAPER_FIG_DIR / "figure3_cross_language_drift"
Y_LABEL = "Profile drift vs Japanese"


def load_model_order(path: Path = RANKING_INPUT_PATH) -> list[str] | None:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    columns = require_columns(
        df,
        {
            "model": ["model_id", "model"],
            "mae": ["mae_to_human", "mae"],
        },
        str(path),
    )
    ranking = pd.DataFrame(
        {
            "model": df[columns["model"]],
            "mae": numeric_series(df, columns["mae"], str(path)),
        }
    )
    return ranking.sort_values("mae", ascending=True)["model"].astype(str).tolist()


def load_drift(path: Path = DRIFT_INPUT_PATH, ranking_path: Path = RANKING_INPUT_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    columns = require_columns(
        df,
        {
            "model": ["model_id", "model"],
            "language": ["lang", "language"],
            "drift": ["drift_vs_ja", "mean_drift_vs_japanese", "mean_drift_vs_ja"],
        },
        str(path),
    )

    out = pd.DataFrame(
        {
            "model": df[columns["model"]].astype(str),
            "language": df[columns["language"]].astype(str).str.lower(),
            "drift": numeric_series(df, columns["drift"], str(path)),
        }
    )
    out = out[out["language"] != "ja"].copy()
    out = out[out["language"].isin(["en", "zh"])].copy()

    model_order = load_model_order(ranking_path)
    if model_order is None:
        model_order = sorted(out["model"].unique())
    else:
        remaining = sorted(set(out["model"]) - set(model_order))
        model_order = [model for model in model_order if model in set(out["model"])] + remaining

    out["Model"] = out["model"].map(display_model_name)
    out["Model"] = pd.Categorical(out["Model"], [display_model_name(model) for model in model_order], ordered=True)
    out["Language"] = out["language"].map({"en": "EN", "zh": "ZH"})
    return out.sort_values(["Model", "Language"]).reset_index(drop=True)


def save_figure(drift: pd.DataFrame, output_stem: Path = OUTPUT_STEM) -> list[Path]:
    ensure_dir(output_stem.parent)

    pivot = drift.pivot(index="Model", columns="Language", values="drift")
    pivot = pivot.reindex(columns=["EN", "ZH"])

    x_positions = list(range(len(pivot.index)))
    width = 0.36

    fig_width = max(7.0, 0.8 * len(pivot.index) + 2.5)
    fig, ax = plt.subplots(figsize=(fig_width, 4.2))
    ax.bar([x - width / 2 for x in x_positions], pivot["EN"], width=width, label="EN")
    ax.bar([x + width / 2 for x in x_positions], pivot["ZH"], width=width, label="ZH")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(pivot.index, rotation=30, ha="right")
    ax.set_ylabel(Y_LABEL)
    ax.set_xlabel("")
    ax.grid(axis="y", linestyle=":", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    fig.tight_layout()

    output_paths = [output_stem.with_suffix(".png"), output_stem.with_suffix(".pdf")]
    for output_path in output_paths:
        fig.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return output_paths


def main() -> None:
    drift = load_drift()
    output_paths = save_figure(drift)
    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
