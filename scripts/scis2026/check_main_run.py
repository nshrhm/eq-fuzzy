from __future__ import annotations

"""Check the SCIS 2026 Phase 6 main-run gate from summary outputs."""

import argparse
from pathlib import Path

from check_pilot_run import check_summary


DEFAULT_SUMMARY = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/summary.json"
DEFAULT_CELL_CSV = "runs/scis2026/scis2026_factorial_v1_main_manifest_v1/cell_summary.csv"
DEFAULT_CONFIG = "configs/scis/factorial_v1.yaml"
DEFAULT_MIN_VALID_RATE = 0.95
DEFAULT_MIN_CELL_VALID_REPEATS = 4


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
        stage_name="main",
    )
    if not ok:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print("SCIS Phase 6 main gate passed.")


if __name__ == "__main__":
    main()
