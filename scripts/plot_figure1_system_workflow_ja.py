from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(os.environ.get("TMPDIR", "/tmp")) / "iceccme2026-matplotlib"),
)

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from src.iceccme2026.paper_exports import PAPER_FIG_DIR, ensure_dir

OUTPUT_STEM = PAPER_FIG_DIR / "figure1_system_workflow_ja"

plt.rcParams["font.family"] = "Noto Sans CJK JP"


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str,
    edgecolor: str = "#333333",
    fontsize: float = 7.2,
    weight: str = "normal",
) -> None:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.0,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        linespacing=1.25,
    )


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = "#333333",
    connectionstyle: str = "arc3,rad=0.0",
) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=1.0,
        color=color,
        shrinkA=3,
        shrinkB=3,
        connectionstyle=connectionstyle,
    )
    ax.add_patch(arrow)


def save_figure(output_stem: Path = OUTPUT_STEM) -> list[Path]:
    ensure_dir(output_stem.parent)

    fig, ax = plt.subplots(figsize=(7.6, 3.25))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    human_color = "#E8F2FF"
    llm_color = "#FFF2D9"
    analysis_color = "#EAF7EA"
    neutral_color = "#F5F5F5"

    ax.text(0.05, 0.93, "人間VASブランチ", fontsize=8.5, fontweight="bold", ha="left")
    ax.text(0.05, 0.53, "LLMベンチマークブランチ", fontsize=8.5, fontweight="bold", ha="left")

    add_box(
        ax,
        (0.04, 0.72),
        0.18,
        0.12,
        "生データ\n91回答\n3作品 x 4感情",
        facecolor=human_color,
    )
    add_box(
        ax,
        (0.29, 0.72),
        0.18,
        0.12,
        "サニタイズ済み\nVASデータ\n86完全回答",
        facecolor=human_color,
    )
    add_box(
        ax,
        (0.54, 0.72),
        0.18,
        0.12,
        "日本語人間参照\n12セル",
        facecolor=human_color,
        weight="bold",
    )

    add_box(
        ax,
        (0.04, 0.33),
        0.18,
        0.14,
        "定義ファイル\n作品・翻訳\n感情・ペルソナ",
        facecolor=llm_color,
    )
    add_box(
        ax,
        (0.29, 0.33),
        0.18,
        0.14,
        "プロンプト\nマニフェスト\n6モデル x 3言語",
        facecolor=llm_color,
    )
    add_box(
        ax,
        (0.54, 0.33),
        0.18,
        0.14,
        "OpenRouter + JSON\n540実行\n2160スコア",
        facecolor=llm_color,
        weight="bold",
    )

    add_box(
        ax,
        (0.79, 0.53),
        0.17,
        0.20,
        "分析出力\nJA MAE/相関\nEN/ZHドリフト\n図表",
        facecolor=analysis_color,
        weight="bold",
    )
    add_box(
        ax,
        (0.32, 0.07),
        0.34,
        0.12,
        "固定課題\n4感情を0--100で採点\n興味・驚き・悲しみ・怒り",
        facecolor=neutral_color,
        fontsize=7.0,
    )

    add_arrow(ax, (0.22, 0.78), (0.29, 0.78))
    add_arrow(ax, (0.47, 0.78), (0.54, 0.78))
    add_arrow(ax, (0.72, 0.78), (0.79, 0.66), connectionstyle="arc3,rad=-0.10")

    add_arrow(ax, (0.22, 0.40), (0.29, 0.40))
    add_arrow(ax, (0.47, 0.40), (0.54, 0.40))
    add_arrow(ax, (0.72, 0.40), (0.79, 0.58), connectionstyle="arc3,rad=0.10")
    add_arrow(ax, (0.38, 0.33), (0.46, 0.19), color="#777777")

    output_paths = [output_stem.with_suffix(".png"), output_stem.with_suffix(".pdf")]
    for output_path in output_paths:
        fig.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return output_paths


def main() -> None:
    output_paths = save_figure()
    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
