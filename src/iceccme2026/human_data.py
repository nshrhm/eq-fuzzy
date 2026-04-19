from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Iterable, Sequence

import pandas as pd
import numpy as np


EMOTIONS = ["interest", "surprise", "sadness", "anger"]
EMOTION_JA = {
    "interest": "面白さ",
    "surprise": "驚き",
    "sadness": "悲しみ",
    "anger": "怒り",
}


@dataclass(frozen=True)
class HumanPreparationOutputs:
    long_path: Path
    summary_path: Path
    reference_path: Path
    respondent_summary_path: Path
    summary_json_path: Path


def _default_story_ids() -> list[str]:
    return ["T1", "T2", "T3"]


def load_surveymonkey_export(path: str | Path, story_ids: Sequence[str] | None = None) -> pd.DataFrame:
    """Load the SurveyMonkey workbook and return a sanitized long-form dataframe.

    Assumptions:
    - first row is the export header
    - second row contains the literal text "Open-Ended Response"
    - columns 9 onward are 3 repeated blocks of 4 emotion columns
    """
    story_ids = list(story_ids or _default_story_ids())
    if len(story_ids) != 3:
        raise ValueError("Expected exactly three story identifiers.")

    df_raw = pd.read_excel(path)
    if df_raw.shape[1] < 21:
        raise ValueError("Unexpected workbook shape. The expected export has at least 21 columns.")

    df = df_raw.iloc[1:].copy().reset_index(drop=True)
    blocks = [
        (story_ids[0], df.columns[9:13]),
        (story_ids[1], df.columns[13:17]),
        (story_ids[2], df.columns[17:21]),
    ]

    records: list[dict] = []
    for idx, row in df.iterrows():
        submitted = pd.to_datetime(row["date_created"]) if pd.notna(row["date_created"]) else pd.NaT
        modified = pd.to_datetime(row["date_modified"]) if pd.notna(row["date_modified"]) else pd.NaT
        duration_sec = (
            (modified - submitted).total_seconds()
            if pd.notna(submitted) and pd.notna(modified)
            else np.nan
        )

        for story_id, cols in blocks:
            for emotion, col in zip(EMOTIONS, cols):
                val = pd.to_numeric(row[col], errors="coerce")
                records.append(
                    {
                        "respondent_uid": f"R{idx + 1:03d}",
                        "submitted_at": submitted.isoformat() if pd.notna(submitted) else "",
                        "duration_sec": round(float(duration_sec), 1) if pd.notna(duration_sec) else "",
                        "story_id": story_id,
                        "emotion": emotion,
                        "emotion_ja": EMOTION_JA[emotion],
                        "score": int(val) if pd.notna(val) else "",
                    }
                )

    long_df = pd.DataFrame(records)
    score_num = pd.to_numeric(long_df["score"], errors="coerce")
    complete_case = (
        long_df.assign(score_num=score_num)
        .groupby("respondent_uid")["score_num"]
        .apply(lambda s: s.notna().all())
    )
    long_df = long_df.merge(complete_case.rename("is_complete_case"), on="respondent_uid")
    return long_df


def summarize_human_reference(long_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict, pd.DataFrame]:
    numeric = long_df.copy()
    numeric["score"] = pd.to_numeric(numeric["score"], errors="coerce")

    summary = (
        numeric.dropna(subset=["score"])
        .groupby(["story_id", "emotion", "emotion_ja"], as_index=False)
        .agg(
            n=("score", "size"),
            mean=("score", "mean"),
            sd=("score", "std"),
            median=("score", "median"),
            p25=("score", lambda s: s.quantile(0.25)),
            p75=("score", lambda s: s.quantile(0.75)),
            min=("score", "min"),
            max=("score", "max"),
        )
    )
    for col in ["mean", "sd", "median", "p25", "p75", "min", "max"]:
        summary[col] = summary[col].round(4)

    reference = summary[["story_id", "emotion", "mean"]].rename(columns={"mean": "human_mean"})

    respondent_summary = (
        numeric.groupby("respondent_uid")
        .agg(
            n_nonmissing=("score", lambda s: int(s.notna().sum())),
            is_complete_case=("is_complete_case", "first"),
            duration_sec=("duration_sec", lambda s: pd.to_numeric(s, errors="coerce").dropna().mean()),
        )
        .reset_index()
    )

    summary_json = {
        "n_respondents_total": int(numeric["respondent_uid"].nunique()),
        "n_complete_case": int(
            respondent_summary["is_complete_case"].fillna(False).astype(bool).sum()
        ),
        "n_nonmissing_scores": int(numeric["score"].notna().sum()),
        "n_total_possible_scores": int(numeric.shape[0]),
        "nonmissing_rate": round(float(numeric["score"].notna().mean()), 6),
        "story_level_nonmissing_counts": {
            key: int(val)
            for key, val in (
                numeric.groupby("story_id")["score"].apply(lambda s: int(s.notna().sum())).to_dict().items()
            )
        },
    }
    return summary, reference, summary_json, respondent_summary


def prepare_human_outputs(
    input_path: str | Path,
    output_dir: str | Path,
    summary_json_path: str | Path | None = None,
    story_ids: Sequence[str] | None = None,
) -> HumanPreparationOutputs:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    long_df = load_surveymonkey_export(input_path, story_ids=story_ids)
    summary, reference, summary_json, respondent_summary = summarize_human_reference(long_df)

    long_path = output_dir / "human_vas_long.csv"
    summary_path = output_dir / "human_vas_summary.csv"
    reference_path = output_dir / "human_reference_12cell.csv"
    respondent_summary_path = output_dir / "human_respondent_summary.csv"

    long_df.to_csv(long_path, index=False)
    summary.to_csv(summary_path, index=False)
    reference.to_csv(reference_path, index=False)
    respondent_summary.to_csv(respondent_summary_path, index=False)

    summary_json_path = Path(summary_json_path) if summary_json_path else output_dir.parent.parent / "results" / "json" / "human_reference_summary.json"
    summary_json_path.parent.mkdir(parents=True, exist_ok=True)
    summary_json_path.write_text(json.dumps(summary_json, ensure_ascii=False, indent=2), encoding="utf-8")

    return HumanPreparationOutputs(
        long_path=long_path,
        summary_path=summary_path,
        reference_path=reference_path,
        respondent_summary_path=respondent_summary_path,
        summary_json_path=summary_json_path,
    )
