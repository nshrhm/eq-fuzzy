from __future__ import annotations

"""Check the SCIS 2026 Phase 5 pilot-run gate from summary outputs."""

import argparse
import csv
from pathlib import Path
from typing import Any

from check_sanity_run import load_json, load_yaml, require


DEFAULT_SUMMARY = "runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/summary.json"
DEFAULT_CELL_CSV = "runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/cell_summary.csv"
DEFAULT_CONFIG = "configs/scis/factorial_v1.yaml"
DEFAULT_MIN_VALID_RATE = 0.95
DEFAULT_MIN_CELL_VALID_REPEATS = 2


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def expected_cells(stage: dict[str, Any]) -> int:
    return int(stage["models"]) * len(stage["story_ids"]) * int(stage["conditions"])


def check_summary(
    *,
    repo_root: Path,
    summary_path: Path,
    cell_csv: Path,
    config_path: Path,
    min_valid_rate: float,
    min_cell_valid_repeats: int,
) -> tuple[bool, list[str]]:
    summary = load_json(summary_path)
    config = load_yaml(config_path)
    stage = config["run_stages"]["pilot"]
    errors: list[str] = []
    n_expected_cells = expected_cells(stage)

    require(summary.get("stage") == "pilot", "summary stage is not pilot", errors)
    require(summary.get("design_id") == config["study"]["design_id"], "design_id mismatch", errors)
    require(int(summary.get("n_records", -1)) == int(stage["expected_trials"]), "n_records does not match pilot expected_trials", errors)
    require(int(summary.get("n_models", -1)) == int(stage["models"]), "n_models mismatch", errors)
    require(int(summary.get("n_cells", -1)) == n_expected_cells, "n_cells mismatch", errors)
    require(float(summary.get("valid_rate", 0.0)) >= min_valid_rate, "valid_rate below threshold", errors)
    require(not summary.get("validation_errors"), "validation_errors is not empty", errors)
    require(not summary.get("error_status_codes"), "error_status_codes is not empty", errors)
    require(cell_csv.exists(), f"missing cell summary CSV: {cell_csv}", errors)

    if cell_csv.exists():
        cells = load_csv(cell_csv)
        repetitions = int(stage["repetitions"])
        require(len(cells) == n_expected_cells, "cell summary row count mismatch", errors)
        low_repeat_cells = [
            f"{row['model_id']}|{row['story_id']}|{row['condition_id']}"
            for row in cells
            if int(row["n_ok"]) < min_cell_valid_repeats
        ]
        short_attempt_cells = [
            f"{row['model_id']}|{row['story_id']}|{row['condition_id']}"
            for row in cells
            if int(row["n_attempts"]) != repetitions
        ]
        require(not low_repeat_cells, f"cells below min valid repeats: {low_repeat_cells[:10]}", errors)
        require(not short_attempt_cells, f"cells with unexpected attempt counts: {short_attempt_cells[:10]}", errors)

    return not errors, errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--summary-json", default=DEFAULT_SUMMARY)
    parser.add_argument("--cell-csv", default=DEFAULT_CELL_CSV)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--min-valid-rate", type=float, default=DEFAULT_MIN_VALID_RATE)
    parser.add_argument("--min-cell-valid-repeats", type=int, default=DEFAULT_MIN_CELL_VALID_REPEATS)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    ok, errors = check_summary(
        repo_root=repo_root,
        summary_path=repo_root / args.summary_json,
        cell_csv=repo_root / args.cell_csv,
        config_path=repo_root / args.config,
        min_valid_rate=args.min_valid_rate,
        min_cell_valid_repeats=args.min_cell_valid_repeats,
    )
    if not ok:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("SCIS Phase 5 pilot gate passed.")


if __name__ == "__main__":
    main()
