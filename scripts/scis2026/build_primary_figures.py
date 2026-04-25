from __future__ import annotations

"""Build SCIS primary figure candidates from main-run table artifacts."""

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "scis2026-matplotlib"))

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

from build_primary_tables import compact_model_label, latex_escape, metric_label
from inspect_main_results import load_csv


DEFAULT_ANALYSIS_DIR = "artifacts/scis2026/main_analysis_v1"
DEFAULT_INSPECTION_DIR = "artifacts/scis2026/main_inspection_v1"
DEFAULT_TABLES_DIR = "artifacts/scis2026/main_tables_v1"
DEFAULT_OUTPUT_DIR = "artifacts/scis2026/main_figures_v1"
DEFAULT_DOC = "docs/scis2026/phase8_primary_figures.md"
DEFAULT_PRIMARY_FAMILY = "sigmoid_s_v1"

TEMPERATURES = [0.1, 0.4, 0.7, 0.9]
PERSONAS = ["p1", "p2", "p3", "p4"]


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def soft_cmap() -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list(
        "scis_soft",
        ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
    )


def draw_design_grid(
    ax: plt.Axes,
    *,
    title: str,
    diagonal_only: bool,
) -> None:
    ax.set_title(title, fontsize=11, pad=8)
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_xticks([0.5, 1.5, 2.5, 3.5], ["0.1", "0.4", "0.7", "0.9"])
    ax.set_yticks([0.5, 1.5, 2.5, 3.5], ["p4", "p3", "p2", "p1"])
    ax.set_xlabel("Temperature")
    ax.set_ylabel("Persona")
    for i in range(4):
        for j in range(4):
            active = (i == 3 - j) if diagonal_only else True
            face = "#2b6cb0" if active else "#eef2f7"
            edge = "#334155" if active else "#cbd5e1"
            ax.add_patch(Rectangle((i, j), 1, 1, facecolor=face, edgecolor=edge, linewidth=1.0))
            if active:
                ax.text(i + 0.5, j + 0.5, "sampled", ha="center", va="center", color="white", fontsize=8)
    ax.set_aspect("equal")
    for spine in ax.spines.values():
        spine.set_visible(False)


def plot_single_design(
    output_dir: Path,
    *,
    figure: str,
    title: str,
    diagonal_only: bool,
    caption_seed: str,
) -> dict[str, Any]:
    fig, ax = plt.subplots(figsize=(3.35, 3.25), constrained_layout=True)
    draw_design_grid(ax, title=title, diagonal_only=diagonal_only)
    path = output_dir / f"{figure}.png"
    save_figure(fig, path)
    return {
        "figure": figure,
        "path": str(path),
        "source": "design specification",
        "caption_seed": caption_seed,
        "main_text": True,
    }


def plot_design_comparison(output_dir: Path) -> dict[str, Any]:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.35), constrained_layout=True)
    draw_design_grid(axes[0], title="Prior bundled diagonal design", diagonal_only=True)
    draw_design_grid(axes[1], title="SCIS fully crossed design", diagonal_only=False)
    fig.suptitle("Separating persona and temperature by independent crossing", fontsize=12)
    path = output_dir / "figure1_design_comparison.png"
    save_figure(fig, path)
    return {
        "figure": "figure1_design_comparison",
        "path": str(path),
        "source": "design specification",
        "caption_seed": "Prior diagonal persona-temperature bundles are contrasted with the SCIS fully crossed persona x temperature design.",
        "main_text": False,
    }


def select_representative_cases(
    *,
    top_relative: list[dict[str, str]],
    top_absolute: list[dict[str, str]],
) -> list[dict[str, str]]:
    relative_entropy = next(row for row in top_relative if row["metric"].startswith("H_norm_"))
    absolute_score = next(row for row in top_absolute if row["metric"] == "score")
    return [relative_entropy, absolute_score]


def story_display_label(story_id: str) -> str:
    if story_id.startswith("T") and story_id[1:].isdigit():
        return f"Text {story_id[1:]}"
    return story_id


def grid_values_for_case(
    *,
    case: dict[str, str],
    score_cells: list[dict[str, str]],
    entropy_cells: list[dict[str, str]],
    primary_family: str,
) -> list[list[float]]:
    metric = case["metric"]
    source = entropy_cells if metric.startswith("H_norm_") else score_cells
    value_column = "mean_H_norm" if metric.startswith("H_norm_") else "mean_score"
    values: dict[tuple[str, float], float] = {}
    for row in source:
        if row["model_id"] != case["model_id"]:
            continue
        if row["story_id"] != case["story_id"]:
            continue
        if row["emotion"] != case["emotion"]:
            continue
        if metric.startswith("H_norm_") and row.get("membership_family") != primary_family:
            continue
        values[(row["persona_id"], float(row["temperature"]))] = float(row[value_column])
    return [[values[(persona, temperature)] for temperature in TEMPERATURES] for persona in PERSONAS]


def plot_heatmap(
    ax: plt.Axes,
    values: list[list[float]],
    *,
    title: str,
    value_format: str,
    vmin: float | None = None,
    vmax: float | None = None,
) -> None:
    image = ax.imshow(values, cmap=soft_cmap(), vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_title(title, fontsize=10, pad=8)
    ax.set_xticks(range(len(TEMPERATURES)), [str(t) for t in TEMPERATURES])
    ax.set_yticks(range(len(PERSONAS)), PERSONAS)
    ax.set_xlabel("Temperature")
    ax.set_ylabel("Persona")
    for row_idx, row in enumerate(values):
        for col_idx, value in enumerate(row):
            ax.text(col_idx, row_idx, value_format.format(value), ha="center", va="center", fontsize=8)
    return image


def plot_representative_heatmaps(
    *,
    output_dir: Path,
    cases: list[dict[str, str]],
    score_cells: list[dict[str, str]],
    entropy_cells: list[dict[str, str]],
    primary_family: str,
) -> dict[str, Any]:
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.45), constrained_layout=True)
    captions: list[str] = []
    for ax, case in zip(axes, cases):
        values = grid_values_for_case(
            case=case,
            score_cells=score_cells,
            entropy_cells=entropy_cells,
            primary_family=primary_family,
        )
        is_entropy = case["metric"].startswith("H_norm_")
        metric_name = "$H^*$" if is_entropy else "Score"
        title = (
            f"{metric_name}: {compact_model_label(case['model_id'])}, "
            f"{case['story_id']}, {case['emotion'].title()}"
        )
        image = plot_heatmap(
            ax,
            values,
            title=title,
            value_format="{:.2f}" if is_entropy else "{:.1f}",
            vmin=0.0,
            vmax=1.0 if is_entropy else 100.0,
        )
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.03)
        captions.append(
            f"{case['metric']} {case['model_id']} {case['story_id']} {case['emotion']} "
            f"burden={case['interaction_burden']}"
        )
    path = output_dir / "figure2_representative_heatmaps.png"
    save_figure(fig, path)
    return {
        "figure": "figure2_representative_heatmaps",
        "path": str(path),
        "source": "cell_score_summary.csv and entropy_cell_summary.csv",
        "caption_seed": "; ".join(captions),
        "main_text": False,
    }


def plot_single_representative_heatmap(
    *,
    output_dir: Path,
    case: dict[str, str],
    score_cells: list[dict[str, str]],
    entropy_cells: list[dict[str, str]],
    primary_family: str,
    figure: str,
) -> dict[str, Any]:
    values = grid_values_for_case(
        case=case,
        score_cells=score_cells,
        entropy_cells=entropy_cells,
        primary_family=primary_family,
    )
    is_entropy = case["metric"].startswith("H_norm_")
    metric_name = "$H^*$" if is_entropy else "Score"
    story_label = story_display_label(case["story_id"])
    fig, ax = plt.subplots(figsize=(3.45, 3.15), constrained_layout=True)
    image = plot_heatmap(
        ax,
        values,
        title=f"{metric_name}: {compact_model_label(case['model_id'])}, {story_label}, {case['emotion'].title()}",
        value_format="{:.2f}" if is_entropy else "{:.1f}",
        vmin=0.0,
        vmax=1.0 if is_entropy else 100.0,
    )
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.03)
    path = output_dir / f"{figure}.png"
    save_figure(fig, path)
    burden = float(case["interaction_burden"])
    if is_entropy:
        caption = (
            "Representative high-interaction entropy case. Normalized fuzzy entropy "
            f"\\(H^*\\) for {compact_model_label(case['model_id'])} on {story_label}, "
            f"{case['emotion']}. Axes show four personas and four temperatures; "
            f"cell values are repeat means. This example has B={burden:.3f} "
            "and should not be read as the panel average."
        )
    else:
        caption = (
            "Representative low-interaction score case. Mean score for "
            f"{compact_model_label(case['model_id'])} on {story_label}, "
            f"{case['emotion']}. Axes show four personas and four temperatures; "
            f"cell values are repeat means. This example has B={burden:.3f}."
        )
    return {
        "figure": figure,
        "path": str(path),
        "source": "cell_score_summary.csv and entropy_cell_summary.csv",
        "caption_seed": caption,
        "caption_raw": is_entropy,
        "main_text": True,
    }


def plot_model_metric_heatmap(
    *,
    output_dir: Path,
    model_metric_rows: list[dict[str, str]],
) -> dict[str, Any]:
    models = sorted({row["model_id"] for row in model_metric_rows}, key=compact_model_label)
    metrics = ["score", "H_norm_sigmoid_s_v1"]
    matrix = []
    by_key = {(row["model_id"], row["metric"]): float(row["mean_interaction_burden"]) for row in model_metric_rows}
    for model in models:
        matrix.append([by_key[(model, metric)] for metric in metrics])

    fig, ax = plt.subplots(figsize=(5.8, 3.65), constrained_layout=True)
    image = ax.imshow(matrix, cmap=soft_cmap(), vmin=0.0, vmax=max(max(row) for row in matrix))
    ax.set_xticks(range(len(metrics)), ["Score", "$H^*$"])
    ax.set_yticks(range(len(models)), [compact_model_label(model) for model in models])
    ax.set_title("Mean persona-temperature interaction burden by model", fontsize=11)
    for row_idx, row in enumerate(matrix):
        for col_idx, value in enumerate(row):
            ax.text(col_idx, row_idx, f"{value * 100:.1f}%", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.03, label="Interaction burden")
    path = output_dir / "figure3_model_metric_interaction_heatmap.png"
    save_figure(fig, path)
    return {
        "figure": "figure3_model_metric_interaction_heatmap",
        "path": str(path),
        "source": "table3_model_metric_summary.csv",
        "caption_seed": (
            "Mean persona-temperature interaction burden by model, averaged over "
            "texts and emotions. Score and normalized fuzzy entropy \\(H^*\\) are summarized "
            "under the same crossed cell structure."
        ),
        "caption_raw": True,
        "main_text": True,
    }


def latex_figure_snippet(*, figure: dict[str, Any], label: str, width: str = r"\linewidth") -> str:
    path = Path(str(figure["path"]))
    try:
        latex_path = path.relative_to(Path("paper/scis2026"))
    except ValueError:
        latex_path = Path("../..") / path
    caption = str(figure["caption_seed"]) if figure.get("caption_raw") else latex_escape(figure["caption_seed"])
    return "\n".join(
        [
            r"\begin{figure}[t]",
            r"\centering",
            rf"\includegraphics[width={width}]{{{latex_path.as_posix()}}}",
            rf"\caption{{{caption}}}",
            rf"\label{{{label}}}",
            r"\end{figure}",
            "",
        ]
    )


def write_latex_snippets(figures: list[dict[str, Any]], output_dir: Path) -> None:
    labels = {
        "figure1_design_comparison": "fig:scis-design",
        "figure1a_prior_diagonal_design": "fig:scis-prior-diagonal",
        "figure1b_factorial_design": "fig:scis-factorial-design",
        "figure2_representative_heatmaps": "fig:scis-representative-heatmaps",
        "figure2a_entropy_heatmap": "fig:scis-entropy-heatmap",
        "figure2b_score_heatmap": "fig:scis-score-heatmap",
        "figure3_model_metric_interaction_heatmap": "fig:scis-model-metric-heatmap",
    }
    for figure in figures:
        (output_dir / f"{figure['figure']}.tex").write_text(
            latex_figure_snippet(figure=figure, label=labels[figure["figure"]]),
            encoding="utf-8",
        )


def write_doc(*, path: Path, summary: dict[str, Any], figures: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(
        f"| `{figure['figure']}` | `{figure['path']}` | {figure['caption_seed']} |"
        for figure in figures
    )
    body = f"""# SCIS Phase 8 Primary Figures

This document records the first primary figure candidates for the SCIS 2026
main paper. The figures are descriptive and should be paired with bootstrap
confidence intervals in a later phase before final claims are fixed.

## Generated Figures

| Figure | Path | Caption seed |
| --- | --- | --- |
{rows}

## Construction Summary

```json
{json.dumps(summary, ensure_ascii=False, indent=2)}
```
"""
    path.write_text(body, encoding="utf-8")


def build_primary_figures(
    *,
    analysis_dir: Path,
    inspection_dir: Path,
    tables_dir: Path,
    output_dir: Path,
    doc_path: Path,
    primary_family: str,
) -> dict[str, Any]:
    top_relative = load_csv(inspection_dir / "top_interaction_burdens.csv")
    top_absolute = load_csv(inspection_dir / "top_absolute_interactions.csv")
    score_cells = load_csv(analysis_dir / "cell_score_summary.csv")
    entropy_cells = load_csv(analysis_dir / "entropy_cell_summary.csv")
    model_metric_rows = load_csv(tables_dir / "table3_model_metric_summary.csv")

    output_dir.mkdir(parents=True, exist_ok=True)
    cases = select_representative_cases(top_relative=top_relative, top_absolute=top_absolute)
    figures = [
        plot_design_comparison(output_dir),
        plot_single_design(
            output_dir,
            figure="figure1a_prior_diagonal_design",
            title="Prior diagonal design",
            diagonal_only=True,
            caption_seed="Prior work bundled each persona with one temperature, producing diagonal-only coverage.",
        ),
        plot_single_design(
            output_dir,
            figure="figure1b_factorial_design",
            title="SCIS fully crossed design",
            diagonal_only=False,
            caption_seed="SCIS independently crosses persona and temperature to estimate main effects and interaction.",
        ),
        plot_representative_heatmaps(
            output_dir=output_dir,
            cases=cases,
            score_cells=score_cells,
            entropy_cells=entropy_cells,
            primary_family=primary_family,
        ),
        plot_single_representative_heatmap(
            output_dir=output_dir,
            case=cases[0],
            score_cells=score_cells,
            entropy_cells=entropy_cells,
            primary_family=primary_family,
            figure="figure2a_entropy_heatmap",
        ),
        plot_single_representative_heatmap(
            output_dir=output_dir,
            case=cases[1],
            score_cells=score_cells,
            entropy_cells=entropy_cells,
            primary_family=primary_family,
            figure="figure2b_score_heatmap",
        ),
        plot_model_metric_heatmap(output_dir=output_dir, model_metric_rows=model_metric_rows),
    ]
    metadata_rows = [
        {
            "figure": figure["figure"],
            "path": figure["path"],
            "source": figure["source"],
            "caption_seed": figure["caption_seed"],
            "main_text": figure["main_text"],
        }
        for figure in figures
    ]
    write_csv(metadata_rows, output_dir / "figure_manifest.csv")
    write_latex_snippets(figures, output_dir)
    summary = {
        "analysis_dir": str(analysis_dir),
        "inspection_dir": str(inspection_dir),
        "tables_dir": str(tables_dir),
        "output_dir": str(output_dir),
        "primary_family": primary_family,
        "n_figures": len(figures),
        "figures": [figure["figure"] for figure in figures],
        "main_text_figures": [figure["figure"] for figure in figures if figure["main_text"]],
        "representative_cases": [
            {
                "metric": case["metric"],
                "model_id": case["model_id"],
                "story_id": case["story_id"],
                "emotion": case["emotion"],
                "interaction_burden": case["interaction_burden"],
            }
            for case in cases
        ],
    }
    (output_dir / "figure_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_doc(path=doc_path, summary=summary, figures=figures)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--inspection-dir", default=DEFAULT_INSPECTION_DIR)
    parser.add_argument("--tables-dir", default=DEFAULT_TABLES_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--doc", default=DEFAULT_DOC)
    parser.add_argument("--primary-family", default=DEFAULT_PRIMARY_FAMILY)
    args = parser.parse_args()

    summary = build_primary_figures(
        analysis_dir=Path(args.analysis_dir),
        inspection_dir=Path(args.inspection_dir),
        tables_dir=Path(args.tables_dir),
        output_dir=Path(args.output_dir),
        doc_path=Path(args.doc),
        primary_family=args.primary_family,
    )
    print(f"Wrote primary figures to {Path(args.output_dir).resolve()}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
