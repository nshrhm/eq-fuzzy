from __future__ import annotations

"""Build ICICIC primary figure candidates from comparison and analysis artifacts."""

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


DEFAULT_MATRIX = "artifacts/icicic2026/comparison_matrix_v1/benchmark_coverage_matrix.csv"
DEFAULT_ANALYSIS_DIR = "artifacts/icicic2026/matched_subset_stable6_analysis_v1"
DEFAULT_OUTPUT_DIR = "artifacts/icicic2026/main_figures_v1"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_include(path: Path, image_name: str, caption: str, label: str) -> None:
    path.write_text(
        "\n".join(
            [
                r"\begin{figure}[t]",
                r"\centering",
                rf"\includegraphics[width=\linewidth]{{figures/{image_name}}}",
                rf"\caption{{{caption}}}",
                rf"\label{{{label}}}",
                r"\end{figure}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def plot_coverage_map(matrix_rows: list[dict[str, str]], output_dir: Path) -> dict[str, Any]:
    features = ["uncertainty_output", "controllability", "repeatability"]
    labels = [row["benchmark"] for row in matrix_rows]
    values = []
    for row in matrix_rows:
        values.append([
            0 if row[feature].startswith("not a primary") or row[feature].startswith("fixed ") else 1
            for feature in features
        ])

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.imshow(values, cmap="Greens", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(features)), [feature.replace("_", "\n") for feature in features], fontsize=8)
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    for y, row in enumerate(values):
        for x, value in enumerate(row):
            ax.text(x, y, "yes" if value else "no", ha="center", va="center", fontsize=8)
    ax.set_title("Benchmark coverage for ICICIC positioning", fontsize=10)
    fig.tight_layout()
    image_path = output_dir / "figure1_benchmark_coverage_map.png"
    fig.savefig(image_path, dpi=200)
    plt.close(fig)
    tex_path = output_dir / "figure1_benchmark_coverage_map.tex"
    write_include(
        tex_path,
        image_path.name,
        "Coverage map for benchmark-positioning descriptors used in ICICIC.",
        "fig:icicic-coverage-map",
    )
    return {
        "figure": "figure1_benchmark_coverage_map",
        "path": str(image_path),
        "tex": str(tex_path),
        "role": "coverage map",
    }


def plot_added_descriptors(model_rows: list[dict[str, str]], output_dir: Path) -> dict[str, Any]:
    labels = [row["model_id"].split("/")[-1] for row in model_rows]
    metrics = [
        ("mean_within_cell_sd_score", "within-cell SD"),
        ("mean_cell_H_norm", "fuzzy entropy"),
        ("mean_target_shift_abs", "target shift"),
    ]

    fig, axes = plt.subplots(1, len(metrics), figsize=(9, 3.4), sharey=False)
    if len(metrics) == 1:
        axes = [axes]
    for ax, (column, title) in zip(axes, metrics):
        values = [float(row[column]) if row.get(column) not in ("", None) else 0.0 for row in model_rows]
        ax.barh(labels, values, color="#3b7a78")
        ax.set_title(title, fontsize=9)
        ax.tick_params(axis="both", labelsize=8)
        ax.grid(axis="x", alpha=0.25)
    fig.suptitle("EQ-Fuzzy added descriptors by model", fontsize=10)
    fig.tight_layout()
    image_path = output_dir / "figure2_added_descriptor_overview.png"
    fig.savefig(image_path, dpi=200)
    plt.close(fig)
    tex_path = output_dir / "figure2_added_descriptor_overview.tex"
    write_include(
        tex_path,
        image_path.name,
        "Model-level overview of uncertainty, stability, and target-control descriptors.",
        "fig:icicic-added-descriptors",
    )
    return {
        "figure": "figure2_added_descriptor_overview",
        "path": str(image_path),
        "tex": str(tex_path),
        "role": "added descriptor overview",
    }


def build_primary_figures(*, matrix_path: Path, analysis_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix_rows = load_csv(matrix_path)
    model_rows = load_csv(analysis_dir / "model_summary.csv")
    figures = [
        plot_coverage_map(matrix_rows, output_dir),
        plot_added_descriptors(model_rows, output_dir),
    ]
    manifest_path = output_dir / "figure_manifest.csv"
    write_csv(figures, manifest_path)
    summary = {
        "figure_set": "icicic2026_main_figures_v1",
        "matrix_path": str(matrix_path),
        "analysis_dir": str(analysis_dir),
        "output_dir": str(output_dir),
        "n_figures": len(figures),
        "figure_manifest": str(manifest_path),
        "claim_discipline": "descriptive figures only",
    }
    (output_dir / "figure_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--matrix", default=DEFAULT_MATRIX)
    parser.add_argument("--analysis-dir", default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    summary = build_primary_figures(
        matrix_path=repo_root / args.matrix,
        analysis_dir=repo_root / args.analysis_dir,
        output_dir=repo_root / args.output_dir,
    )
    print(f"Wrote {summary['n_figures']} ICICIC primary figures.")


if __name__ == "__main__":
    main()
