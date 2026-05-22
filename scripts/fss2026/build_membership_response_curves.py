from __future__ import annotations

"""Build FSS 2026 score-axis membership and entropy-response grids."""

import argparse
from pathlib import Path

from membership_specification_lib import (
    DEFAULT_CONFIG,
    DEFAULT_OUTPUT_DIR,
    build_entropy_response_grid,
    build_membership_grid,
    hmax_by_family,
    load_config,
    resolve_repo_path,
    write_analysis_summary,
    write_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    config_path = resolve_repo_path(args.config)
    output_dir = resolve_repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(config_path)
    hmaxes = hmax_by_family(config)
    write_csv(build_membership_grid(config), output_dir / "membership_grid.csv")
    write_csv(build_entropy_response_grid(config, hmaxes), output_dir / "entropy_response_grid.csv")
    write_analysis_summary(Path(config_path), config, output_dir, hmaxes)
    print(f"Wrote membership and entropy-response grids to {output_dir}")


if __name__ == "__main__":
    main()
