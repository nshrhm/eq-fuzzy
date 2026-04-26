from __future__ import annotations

"""Build the ICICIC 2026 benchmark-positioning coverage matrix."""

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = "artifacts/icicic2026/comparison_matrix_v1"


COLUMNS = [
    "benchmark",
    "task_type",
    "stimulus_type",
    "language",
    "response_format",
    "scoring_rule",
    "human_reference",
    "repeatability",
    "uncertainty_output",
    "controllability",
    "persona_temperature_handling",
    "reproducibility_license",
    "icicic_role",
]


ROWS: list[dict[str, str]] = [
    {
        "benchmark": "EQ-Bench",
        "task_type": "emotional understanding in dialogue",
        "stimulus_type": "dialogue scenarios",
        "language": "English",
        "response_format": "predicted emotional-state intensities",
        "scoring_rule": "benchmark-native automated score",
        "human_reference": "not the ICICIC human-reference endpoint",
        "repeatability": "reported as benchmark repeatability",
        "uncertainty_output": "not a primary output",
        "controllability": "fixed benchmark task framing",
        "persona_temperature_handling": "not a factorial design in ICICIC",
        "reproducibility_license": "public paper, code, and leaderboard references",
        "icicic_role": "external comparator for emotional-intensity benchmarking",
    },
    {
        "benchmark": "EmoBench",
        "task_type": "emotional understanding and application",
        "stimulus_type": "hand-crafted EI questions",
        "language": "English and Chinese",
        "response_format": "question-answering benchmark outputs",
        "scoring_rule": "benchmark-native correctness score",
        "human_reference": "human performance comparison in source benchmark",
        "repeatability": "controlled item set",
        "uncertainty_output": "not a primary output",
        "controllability": "fixed EI question framing",
        "persona_temperature_handling": "not a factorial design in ICICIC",
        "reproducibility_license": "ACL paper and public code/data references",
        "icicic_role": "external comparator for broader EI capability",
    },
    {
        "benchmark": "SECEU / Emotion Understanding",
        "task_type": "psychometric emotional-understanding test",
        "stimulus_type": "realistic social scenarios",
        "language": "primarily Chinese in the cited study",
        "response_format": "objective performance-test responses",
        "scoring_rule": "psychometric score against human norm",
        "human_reference": "norm frame from more than 500 adults in source study",
        "repeatability": "psychometric test framing",
        "uncertainty_output": "not a primary output",
        "controllability": "fixed psychometric construct",
        "persona_temperature_handling": "not a factorial design in ICICIC",
        "reproducibility_license": "paper and project-site references; item reuse must be checked",
        "icicic_role": "coverage comparator, mini-run only if reuse terms are clear",
    },
    {
        "benchmark": "EQ-Fuzzy matched subset",
        "task_type": "literary affect scoring with matched evaluation target",
        "stimulus_type": "three short literary texts from the EQ-Fuzzy registry",
        "language": "English for ICICIC main analysis",
        "response_format": "four 0-100 emotion scores plus brief reasons",
        "scoring_rule": "cell means, dispersion, fuzzy entropy, profile entropy, target shift",
        "human_reference": "not used as ICICIC primary endpoint",
        "repeatability": "explicit repeated sampling per model and target mode",
        "uncertainty_output": "within-cell dispersion and fuzzy entropy",
        "controllability": "reader-side versus character-side target mode",
        "persona_temperature_handling": "fixed neutral persona and fixed temperature; no SCIS-style deconfounding",
        "reproducibility_license": "private monorepo artifacts under ICICIC paths",
        "icicic_role": "primary method for showing added uncertainty and controllability descriptors",
    },
]


def tex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_tex(rows: list[dict[str, str]], path: Path) -> None:
    selected_columns = [
        "benchmark",
        "task_type",
        "scoring_rule",
        "uncertainty_output",
        "controllability",
        "icicic_role",
    ]
    lines = [
        r"\begin{tabular}{p{0.15\linewidth}p{0.17\linewidth}p{0.18\linewidth}p{0.15\linewidth}p{0.15\linewidth}p{0.18\linewidth}}",
        r"\hline",
        " & ".join(tex_escape(col.replace("_", " ")) for col in selected_columns) + r" \\",
        r"\hline",
    ]
    for row in rows:
        lines.append(" & ".join(tex_escape(row[col]) for col in selected_columns) + r" \\")
    lines.extend([r"\hline", r"\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def build_matrix(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "benchmark_coverage_matrix.csv"
    tex_path = output_dir / "benchmark_coverage_matrix.tex"
    summary_path = output_dir / "comparison_matrix_summary.json"
    write_csv(ROWS, csv_path)
    write_tex(ROWS, tex_path)
    summary = {
        "matrix_id": "icicic2026_comparison_matrix_v1",
        "n_rows": len(ROWS),
        "csv": str(csv_path),
        "tex": str(tex_path),
        "claim_discipline": "positioning matrix only; no benchmark-superiority claim",
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    summary = build_matrix(repo_root / args.output_dir)
    print(f"Wrote {summary['n_rows']} comparison rows to {summary['csv']}")


if __name__ == "__main__":
    main()
