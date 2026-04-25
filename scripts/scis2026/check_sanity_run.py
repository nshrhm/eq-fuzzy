from __future__ import annotations

"""Check the SCIS 2026 Phase 4 sanity-run gate from a summary JSON."""

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


DEFAULT_SUMMARY = "runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/summary.json"
DEFAULT_CELL_CSV = "runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/cell_summary.csv"
DEFAULT_CONFIG = "configs/scis/factorial_v1.yaml"
DEFAULT_MIN_VALID_RATE = 0.95


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_summary(
    *,
    repo_root: Path,
    summary_path: Path,
    cell_csv: Path,
    config_path: Path,
    min_valid_rate: float,
) -> tuple[bool, list[str]]:
    summary = load_json(summary_path)
    config = load_yaml(config_path)
    stage = config["run_stages"]["sanity"]
    errors: list[str] = []

    require(summary.get("stage") == "sanity", "summary stage is not sanity", errors)
    require(summary.get("design_id") == config["study"]["design_id"], "design_id mismatch", errors)
    require(int(summary.get("n_records", -1)) == int(stage["expected_trials"]), "n_records does not match sanity expected_trials", errors)
    require(int(summary.get("n_models", -1)) == int(stage["models"]), "n_models mismatch", errors)
    require(int(summary.get("n_cells", -1)) == int(stage["models"]) * int(stage["conditions"]), "n_cells mismatch", errors)
    require(float(summary.get("valid_rate", 0.0)) >= min_valid_rate, "valid_rate below threshold", errors)
    require(not summary.get("validation_errors"), "validation_errors is not empty", errors)
    require(not summary.get("error_status_codes"), "error_status_codes is not empty", errors)
    require(cell_csv.exists(), f"missing cell summary CSV: {cell_csv}", errors)

    return not errors, errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--summary-json", default=DEFAULT_SUMMARY)
    parser.add_argument("--cell-csv", default=DEFAULT_CELL_CSV)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--min-valid-rate", type=float, default=DEFAULT_MIN_VALID_RATE)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    ok, errors = check_summary(
        repo_root=repo_root,
        summary_path=repo_root / args.summary_json,
        cell_csv=repo_root / args.cell_csv,
        config_path=repo_root / args.config,
        min_valid_rate=args.min_valid_rate,
    )
    if not ok:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("SCIS Phase 4 sanity gate passed.")


if __name__ == "__main__":
    main()
