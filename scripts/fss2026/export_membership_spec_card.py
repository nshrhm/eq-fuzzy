from __future__ import annotations

"""Export the FSS 2026 membership specification card."""

import argparse

from membership_specification_lib import (
    DEFAULT_CONFIG,
    DEFAULT_OUTPUT_DIR,
    build_specification_card_rows,
    hmax_by_family,
    load_config,
    resolve_repo_path,
    write_csv,
    write_latex_table,
)


CARD_COLUMNS = [
    "family_id",
    "smoothness",
    "endpoint_behavior",
    "low_type",
    "medium_type",
    "high_type",
    "entropy_normalization",
    "Hmax",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    output_dir = resolve_repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = load_config(args.config)
    rows = build_specification_card_rows(config, hmax_by_family(config))
    write_csv(rows, output_dir / "membership_specification_card.csv")
    write_latex_table(
        rows,
        CARD_COLUMNS,
        output_dir / "membership_specification_card.tex",
        caption="FSS 2026 membership specification card.",
        label="tab:fss_membership_specification_card",
    )
    print(f"Wrote membership specification card to {output_dir}")


if __name__ == "__main__":
    main()
