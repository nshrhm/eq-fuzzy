from __future__ import annotations

"""Build FSS 2026 score-axis figure artifacts."""

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

from membership_specification_lib import (
    DEFAULT_CONFIG,
    DEFAULT_OUTPUT_DIR,
    LABEL_NAMES,
    build_entropy_response_grid,
    build_membership_grid,
    family_ids,
    hmax_by_family,
    load_config,
    read_csv,
    resolve_repo_path,
    write_csv,
)


def ensure_rows(config: dict, output_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    membership_path = output_dir / "membership_grid.csv"
    entropy_path = output_dir / "entropy_response_grid.csv"
    if not membership_path.exists():
        write_csv(build_membership_grid(config), membership_path)
    if not entropy_path.exists():
        write_csv(build_entropy_response_grid(config, hmax_by_family(config)), entropy_path)
    return read_csv(membership_path), read_csv(entropy_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    os.environ.setdefault("MPLCONFIGDIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "fss2026-matplotlib"))
    import matplotlib.pyplot as plt

    config = load_config(args.config)
    output_dir = resolve_repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    membership_rows, entropy_rows = ensure_rows(config, output_dir)

    membership_by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    entropy_by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in membership_rows:
        membership_by_family[row["family_id"]].append(row)
    for row in entropy_rows:
        entropy_by_family[row["family_id"]].append(row)

    families = family_ids(config)
    fig, axes = plt.subplots(len(families), 2, figsize=(10.4, 2.65 * len(families)), sharex=True)
    colors = {"Low": "#2b6cb0", "Medium": "#2f855a", "High": "#c05621"}

    for row_idx, family_id in enumerate(families):
        membership_ax = axes[row_idx][0]
        entropy_ax = axes[row_idx][1]
        family_membership = membership_by_family[family_id]
        family_entropy = entropy_by_family[family_id]
        scores = [float(row["score"]) for row in family_membership]
        for label in LABEL_NAMES:
            membership_ax.plot(scores, [float(row[f"mu_{label}"]) for row in family_membership], label=label, color=colors[label])
        membership_ax.set_title(f"{family_id}: membership")
        membership_ax.set_ylabel("membership")
        membership_ax.set_ylim(-0.03, 1.03)
        membership_ax.grid(True, color="#e5e7eb", linewidth=0.8)

        entropy_ax.plot(
            [float(row["score"]) for row in family_entropy],
            [float(row["H_star"]) for row in family_entropy],
            color="#4c1d95",
            linewidth=1.8,
        )
        entropy_ax.set_title(f"{family_id}: H*(x)")
        entropy_ax.set_ylabel("H*(x)")
        entropy_ax.set_ylim(-0.03, 1.03)
        entropy_ax.grid(True, color="#e5e7eb", linewidth=0.8)

    axes[0][0].legend(loc="upper right", ncols=3, frameon=False)
    axes[-1][0].set_xlabel("score")
    axes[-1][1].set_xlabel("score")
    fig.suptitle("Membership functions and normalized entropy response over the score axis", y=0.997)
    fig.tight_layout()
    figure_path = output_dir / "figure1_membership_and_entropy_response.png"
    fig.savefig(figure_path, dpi=220)
    plt.close(fig)

    summary = {
        "figure": "figure1_membership_and_entropy_response",
        "path": str(figure_path),
        "source": "score-axis membership specification grid",
        "families": families,
        "contains_model_names": False,
        "contains_persona_or_temperature_labels": False,
        "contains_benchmark_or_target_shift_tables": False,
    }
    (output_dir / "figure_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote FSS figure artifacts to {output_dir}")


if __name__ == "__main__":
    main()
