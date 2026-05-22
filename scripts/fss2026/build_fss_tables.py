from __future__ import annotations

"""Build FSS 2026 manuscript-facing table snippets."""

import argparse

from membership_specification_lib import (
    DEFAULT_CONFIG,
    DEFAULT_OUTPUT_DIR,
    build_family_sensitivity_matrix,
    hmax_by_family,
    load_config,
    read_csv,
    resolve_repo_path,
    write_csv,
    write_latex_table,
)


SENSITIVITY_COLUMNS = [
    "family_a",
    "family_b",
    "max_abs_delta_H_star",
    "mean_abs_delta_H_star",
    "score_at_max_delta",
    "transition_region_at_max_delta",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    output_dir = resolve_repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sensitivity_csv = output_dir / "family_sensitivity_matrix.csv"

    if sensitivity_csv.exists():
        rows = read_csv(sensitivity_csv)
    else:
        config = load_config(args.config)
        rows = build_family_sensitivity_matrix(config, hmax_by_family(config))
        write_csv(rows, sensitivity_csv)

    write_latex_table(
        rows,
        SENSITIVITY_COLUMNS,
        output_dir / "family_sensitivity_matrix.tex",
        caption="Score-axis entropy-response sensitivity across unordered membership-family pairs.",
        label="tab:fss_family_sensitivity_matrix",
    )
    print(f"Wrote FSS table artifacts to {output_dir}")


if __name__ == "__main__":
    main()
