from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


REQUIRED_HUMAN_COLUMNS = {"story_id", "emotion", "mean"}
REQUIRED_MODEL_COLUMNS = {"model_id", "provider", "language", "story_id", "emotion", "score"}


def _validate_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{name} is missing required columns: {sorted(missing)}")


def _safe_corr(x: pd.Series, y: pd.Series, method: str = "pearson") -> float:
    if len(x) < 2 or len(y) < 2:
        return np.nan
    if x.nunique(dropna=True) < 2 or y.nunique(dropna=True) < 2:
        return np.nan
    return float(x.corr(y, method=method))


def prepare_human_reference(human_summary: pd.DataFrame) -> pd.DataFrame:
    human_summary = human_summary.copy()
    if {"story_id", "emotion", "mean"}.issubset(human_summary.columns):
        out = human_summary[["story_id", "emotion", "mean"]].rename(columns={"mean": "human_mean"})
    elif {"story_id", "emotion", "human_mean"}.issubset(human_summary.columns):
        out = human_summary[["story_id", "emotion", "human_mean"]]
    else:
        raise ValueError("Human summary must contain either mean or human_mean column.")
    return out.sort_values(["story_id", "emotion"]).reset_index(drop=True)


def aggregate_model_scores(model_scores: pd.DataFrame) -> pd.DataFrame:
    model_scores = model_scores.copy()
    model_scores["score"] = pd.to_numeric(model_scores["score"], errors="coerce")
    model_scores = model_scores.dropna(subset=["score"])
    aggregated = (
        model_scores.groupby(["model_id", "provider", "language", "story_id", "emotion"], as_index=False)
        .agg(model_mean=("score", "mean"), n_raw=("score", "size"))
    )
    return aggregated


def score_alignment_bundle(
    human_summary_path: str | Path,
    model_scores_path: str | Path,
    output_dir: str | Path,
    primary_language: str = "ja",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    human_summary_path = Path(human_summary_path)
    model_scores_path = Path(model_scores_path)
    if not human_summary_path.exists():
        raise FileNotFoundError(f"Human summary not found: {human_summary_path}")
    if not model_scores_path.exists():
        raise FileNotFoundError(
            "Model scores file not found: "
            f"{model_scores_path}. Generate it first with `python main.py normalize-model-scores ...` "
            "or place a long-format CSV at this path. See data/templates/model_scores_template.csv."
        )

    human = pd.read_csv(human_summary_path)
    model_scores = pd.read_csv(model_scores_path)

    human_ref = prepare_human_reference(human)
    _validate_columns(model_scores, REQUIRED_MODEL_COLUMNS, "Model scores")

    cell = aggregate_model_scores(model_scores).merge(
        human_ref, on=["story_id", "emotion"], how="left", validate="many_to_one"
    )
    cell["abs_error_vs_human"] = (cell["model_mean"] - cell["human_mean"]).abs()

    profile_rows = []
    for (model_id, provider, language), sub in cell.groupby(["model_id", "provider", "language"]):
        sub = sub.sort_values(["story_id", "emotion"]).reset_index(drop=True)
        pearson = _safe_corr(sub["model_mean"], sub["human_mean"], method="pearson")
        spearman = _safe_corr(sub["model_mean"], sub["human_mean"], method="spearman")
        profile_rows.append(
            {
                "model_id": model_id,
                "provider": provider,
                "language": language,
                "n_cells": int(sub.shape[0]),
                "mae_to_human": round(float(sub["abs_error_vs_human"].mean()), 6),
                "pearson_to_human": round(pearson, 6) if pd.notna(pearson) else np.nan,
                "spearman_to_human": round(spearman, 6) if pd.notna(spearman) else np.nan,
            }
        )
    profile = pd.DataFrame(profile_rows)

    # Japanese baseline drift
    ja_profiles = (
        cell[cell["language"] == primary_language][["model_id", "story_id", "emotion", "model_mean"]]
        .rename(columns={"model_mean": "ja_model_mean"})
    )
    drift = cell.merge(ja_profiles, on=["model_id", "story_id", "emotion"], how="left")
    drift["drift_vs_japanese"] = (drift["model_mean"] - drift["ja_model_mean"]).abs()

    drift_summary = (
        drift.groupby(["model_id", "provider", "language"], as_index=False)
        .agg(mean_drift_vs_japanese=("drift_vs_japanese", "mean"))
    )
    profile = profile.merge(drift_summary, on=["model_id", "provider", "language"], how="left")
    profile["mean_drift_vs_japanese"] = profile["mean_drift_vs_japanese"].round(6)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cell_path = output_dir / "model_language_cell_level.csv"
    profile_path = output_dir / "model_language_alignment.csv"
    cell.to_csv(cell_path, index=False)
    profile.to_csv(profile_path, index=False)

    return profile, cell
