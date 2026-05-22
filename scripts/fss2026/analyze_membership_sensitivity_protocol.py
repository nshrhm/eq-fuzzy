from __future__ import annotations

"""Build the FSS 2026 score-axis membership-family sensitivity matrix."""

import argparse

from membership_specification_lib import (
    DEFAULT_CONFIG,
    DEFAULT_OUTPUT_DIR,
    build_family_sensitivity_matrix,
    hmax_by_family,
    load_config,
    resolve_repo_path,
    write_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    output_dir = resolve_repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = load_config(args.config)
    rows = build_family_sensitivity_matrix(config, hmax_by_family(config))
    write_csv(rows, output_dir / "family_sensitivity_matrix.csv")
    print(f"Wrote {len(rows)} unordered family-pair sensitivity rows to {output_dir}")


if __name__ == "__main__":
    main()
