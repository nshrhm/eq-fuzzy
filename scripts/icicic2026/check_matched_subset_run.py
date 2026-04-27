from __future__ import annotations

"""Gate-check ICICIC matched-subset analysis outputs."""

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_ANALYSIS_DIR = "artifacts/icicic2026/matched_subset_stable6_analysis_v1"
EXPECTED_RESPONSES = {"sanity": 4, "main": 360}
EXPECTED_TARGET_SHIFT_ROWS = {"sanity": 4, "main": 72}
EMOTIONS = {"interest", "surprise", "sadness", "anger"}
TARGET_MODES = {"reader_side", "character_side"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_outputs(*, analysis_dir: Path, stage: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    summary_path = analysis_dir / "analysis_summary.json"
    emotion_path = analysis_dir / "emotion_long.csv"
    cell_path = analysis_dir / "cell_summary.csv"
    target_shift_path = analysis_dir / "target_shift.csv"
    model_path = analysis_dir / "model_summary.csv"

    for path in [summary_path, emotion_path, cell_path, target_shift_path, model_path]:
        require(path.exists(), f"missing_output:{path}", errors)
    if errors:
        return {"passed": False, "stage": stage, "errors": errors, "warnings": warnings}

    summary = load_json(summary_path)
    emotion_rows = load_csv(emotion_path)
    cell_rows = load_csv(cell_path)
    target_shift_rows = load_csv(target_shift_path)
    model_rows = load_csv(model_path)

    expected_responses = EXPECTED_RESPONSES[stage]
    expected_emotions = expected_responses * 4
    expected_target_shift = EXPECTED_TARGET_SHIFT_ROWS[stage]
    require(int(summary.get("n_response_rows", -1)) == expected_responses, "unexpected_response_count", errors)
    require(int(summary.get("n_emotion_rows", -1)) == expected_emotions, "unexpected_emotion_row_count", errors)
    require({row["emotion"] for row in emotion_rows} == EMOTIONS, "missing_emotion_dimension", errors)
    require({row["target_mode"] for row in emotion_rows} == TARGET_MODES, "missing_target_mode", errors)
    require(all("valid_output_rate" in row for row in cell_rows), "missing_cell_valid_output_rate", errors)
    require(all("valid_output_rate" in row for row in model_rows), "missing_model_valid_output_rate", errors)

    if stage == "sanity":
        require(int(summary.get("n_target_shift_rows", -1)) == expected_target_shift, "unexpected_target_shift_count", errors)
        require(len(target_shift_rows) == expected_target_shift, "target_shift_csv_count_mismatch", errors)
        require(all(row["ok"] == "True" for row in emotion_rows), "invalid_emotion_rows_present", errors)
        require(all(row["valid_output_rate"] == "1.0" for row in cell_rows), "cell_valid_output_rate_below_1", errors)
        require(all(row["valid_output_rate"] == "1.0" for row in model_rows), "model_valid_output_rate_below_1", errors)
    else:
        observed_target_shift = int(summary.get("n_target_shift_rows", -1))
        require(0 <= observed_target_shift <= expected_target_shift, "target_shift_count_out_of_bounds", errors)
        require(len(target_shift_rows) == observed_target_shift, "target_shift_csv_count_mismatch", errors)
        if observed_target_shift < expected_target_shift:
            warnings.append("target_shift_rows_below_full_design")
        if any(row["ok"] != "True" for row in emotion_rows):
            warnings.append("invalid_emotion_rows_present")
        if any(row["valid_output_rate"] != "1.0" for row in cell_rows):
            warnings.append("cell_valid_output_rate_below_1")
        if any(row["valid_output_rate"] != "1.0" for row in model_rows):
            warnings.append("model_valid_output_rate_below_1")

    return {
        "passed": not errors,
        "stage": stage,
        "analysis_dir": str(analysis_dir),
        "expected_responses": expected_responses,
        "expected_target_shift_rows": expected_target_shift,
        "observed_target_shift_rows": int(summary.get("n_target_shift_rows", -1)),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--analysis-dir", default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--stage", choices=("sanity", "main"), default="sanity")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    result = check_outputs(analysis_dir=repo_root / args.analysis_dir, stage=args.stage)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
