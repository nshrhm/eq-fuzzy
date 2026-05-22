from __future__ import annotations

"""Local FSS 2026 membership-specification helpers.

The sigmoid-composed family uses exact piecewise endpoints: values at and
outside a transition interval are fixed at 0 or 1. Interior sigmoid-composed
values are clipped to [0, 1] before export.
"""

import csv
import hashlib
import json
import math
from itertools import combinations
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = "configs/fss/membership_specification_v1.yaml"
DEFAULT_OUTPUT_DIR = "artifacts/fss2026/membership_specification_v1"
LABEL_KEYS = ("low", "medium", "high")
LABEL_NAMES = ("Low", "Medium", "High")
WORKFLOW_SCRIPTS = [
    "scripts/fss2026/build_membership_response_curves.py",
    "scripts/fss2026/export_membership_spec_card.py",
    "scripts/fss2026/analyze_membership_sensitivity_protocol.py",
    "scripts/fss2026/build_fss_tables.py",
    "scripts/fss2026/build_fss_figures.py",
]
REQUIRED_ARTIFACTS = {
    "membership_grid": "membership_grid.csv",
    "entropy_response_grid": "entropy_response_grid.csv",
    "membership_specification_card_csv": "membership_specification_card.csv",
    "membership_specification_card_tex": "membership_specification_card.tex",
    "family_sensitivity_matrix_csv": "family_sensitivity_matrix.csv",
    "family_sensitivity_matrix_tex": "family_sensitivity_matrix.tex",
    "figure1": "figure1_membership_and_entropy_response.png",
    "figure_summary": "figure_summary.json",
    "analysis_summary": "analysis_summary.json",
}
TRANSITION_REGIONS = {
    "boundary",
    "low_transition_0_30",
    "low_medium_overlap_10_30",
    "medium_plateau_30_50",
    "medium_high_overlap_50_70",
    "high_transition_50_100",
    "crisp_or_single_membership_region",
}


def resolve_repo_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else REPO_ROOT / path


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict[str, Any]:
    with resolve_repo_path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(resolve_repo_path(path).read_bytes()).hexdigest()


def family_ids(config: dict[str, Any]) -> list[str]:
    return [str(family["family_id"]) for family in config["membership_families"]]


def family_by_id(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(family["family_id"]): family for family in config["membership_families"]}


def score_grid(config: dict[str, Any]) -> list[float]:
    grid = config["score_grid"]
    start = float(grid["start"])
    stop = float(grid["stop"])
    step = float(grid["step"])
    number_of_steps = int(round((stop - start) / step))
    values = [round(start + step * idx, 10) for idx in range(number_of_steps + 1)]
    values[0] = round(start, 10)
    values[-1] = round(stop, 10)
    return values


def clip01(value: float) -> float:
    return min(max(float(value), 0.0), 1.0)


def linear_ramp(x: float, lo: float, hi: float) -> float:
    if x <= lo:
        return 0.0
    if x >= hi:
        return 1.0
    return clip01((x - lo) / (hi - lo))


def zadeh_s_ramp(x: float, lo: float, hi: float) -> float:
    if x <= lo:
        return 0.0
    if x >= hi:
        return 1.0
    mid = (lo + hi) / 2.0
    width = hi - lo
    if x <= mid:
        return clip01(2.0 * ((x - lo) / width) ** 2)
    return clip01(1.0 - 2.0 * ((x - hi) / width) ** 2)


def sigmoid_interval(x: float, lo: float, hi: float) -> float:
    mid = (lo + hi) / 2.0
    gain = 2.0 * math.log(9.0) / (hi - lo)
    return 1.0 / (1.0 + math.exp(-gain * (x - mid)))


def s_basis(z: float, b: float = 0.1, c: float = 0.9) -> float:
    mid = (b + c) / 2.0
    if z <= b:
        return 0.0
    if z <= mid:
        return clip01(2.0 * ((z - b) ** 2) / ((c - b) ** 2))
    if z < c:
        return clip01(1.0 - 2.0 * ((z - c) ** 2) / ((c - b) ** 2))
    return 1.0


def sigmoid_composed_ramp(x: float, lo: float, hi: float) -> float:
    if x <= lo:
        return 0.0
    if x >= hi:
        return 1.0
    return clip01(s_basis(sigmoid_interval(x, lo, hi)))


def pi_membership(x: float, *, ramp) -> float:
    if x <= 10.0:
        return 0.0
    if x < 30.0:
        return ramp(x, 10.0, 30.0)
    if x <= 50.0:
        return 1.0
    if x < 70.0:
        return 1.0 - ramp(x, 50.0, 70.0)
    return 0.0


def membership_values(family_id: str, score: float) -> dict[str, float]:
    if family_id == "legacy_linear_v1":
        ramp = linear_ramp
    elif family_id == "zadeh_s_z_pi_v1":
        ramp = zadeh_s_ramp
    elif family_id == "sigmoid_composed_s_z_pi_v1":
        ramp = sigmoid_composed_ramp
    else:
        raise ValueError(f"Unknown FSS membership family: {family_id}")

    mu = {
        "low": 1.0 - ramp(score, 0.0, 30.0),
        "medium": pi_membership(score, ramp=ramp),
        "high": ramp(score, 50.0, 100.0),
    }
    return {key: clip01(value) for key, value in mu.items()}


def entropy_raw(mu: dict[str, float]) -> float:
    total = 0.0
    for value in mu.values():
        if value > 0.0:
            total -= value * math.log2(value)
    return float(total)


def hmax_by_family(config: dict[str, Any]) -> dict[str, float]:
    values = score_grid(config)
    hmax: dict[str, float] = {}
    for family_id in family_ids(config):
        hmax[family_id] = max(entropy_raw(membership_values(family_id, score)) for score in values)
    return hmax


def entropy_row(family_id: str, score: float, hmax: float) -> dict[str, float]:
    mu = membership_values(family_id, score)
    h_raw = entropy_raw(mu)
    h_star = h_raw / hmax if hmax else 0.0
    return {
        "H_raw": h_raw,
        "H_star": h_star,
    }


def build_membership_grid(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family_id in family_ids(config):
        for score in score_grid(config):
            mu = membership_values(family_id, score)
            rows.append(
                {
                    "score": score,
                    "family_id": family_id,
                    "mu_Low": round(mu["low"], 12),
                    "mu_Medium": round(mu["medium"], 12),
                    "mu_High": round(mu["high"], 12),
                }
            )
    return rows


def build_entropy_response_grid(config: dict[str, Any], hmaxes: dict[str, float] | None = None) -> list[dict[str, Any]]:
    hmaxes = hmaxes or hmax_by_family(config)
    rows: list[dict[str, Any]] = []
    for family_id in family_ids(config):
        for score in score_grid(config):
            entropy = entropy_row(family_id, score, hmaxes[family_id])
            rows.append(
                {
                    "score": score,
                    "family_id": family_id,
                    "H_raw": round(entropy["H_raw"], 12),
                    "Hmax": round(hmaxes[family_id], 12),
                    "H_star": round(entropy["H_star"], 12),
                }
            )
    return rows


def transition_region(score: float) -> str:
    boundaries = (0.0, 10.0, 30.0, 50.0, 70.0, 100.0)
    if any(math.isclose(score, boundary, abs_tol=1e-10) for boundary in boundaries):
        return "boundary"
    if 10.0 < score < 30.0:
        return "low_medium_overlap_10_30"
    if 0.0 < score < 30.0:
        return "low_transition_0_30"
    if 30.0 < score < 50.0:
        return "medium_plateau_30_50"
    if 50.0 < score < 70.0:
        return "medium_high_overlap_50_70"
    if 70.0 < score < 100.0:
        return "high_transition_50_100"
    return "crisp_or_single_membership_region"


def integrated_abs_delta(scores: list[float], deltas: list[float]) -> float:
    if len(scores) < 2:
        return 0.0
    total = 0.0
    for idx in range(len(scores) - 1):
        width = scores[idx + 1] - scores[idx]
        total += width * (abs(deltas[idx]) + abs(deltas[idx + 1])) / 2.0
    return total


def build_family_sensitivity_matrix(config: dict[str, Any], hmaxes: dict[str, float] | None = None) -> list[dict[str, Any]]:
    scores = score_grid(config)
    hmaxes = hmaxes or hmax_by_family(config)
    hstar_by_family = {
        family_id: [entropy_row(family_id, score, hmaxes[family_id])["H_star"] for score in scores]
        for family_id in family_ids(config)
    }

    rows: list[dict[str, Any]] = []
    for family_a, family_b in combinations(family_ids(config), 2):
        deltas = [hstar_by_family[family_b][idx] - hstar_by_family[family_a][idx] for idx in range(len(scores))]
        abs_deltas = [abs(delta) for delta in deltas]
        max_idx = max(range(len(abs_deltas)), key=lambda idx: (abs_deltas[idx], -scores[idx]))
        score_at_max = scores[max_idx]
        rows.append(
            {
                "family_a": family_a,
                "family_b": family_b,
                "max_abs_delta_H_star": round(abs_deltas[max_idx], 12),
                "mean_abs_delta_H_star": round(sum(abs_deltas) / len(abs_deltas), 12),
                "score_at_max_delta": round(score_at_max, 10),
                "transition_region_at_max_delta": transition_region(score_at_max),
                "integrated_abs_delta_H_star": round(integrated_abs_delta(scores, deltas), 12),
            }
        )
    return rows


def build_specification_card_rows(config: dict[str, Any], hmaxes: dict[str, float] | None = None) -> list[dict[str, Any]]:
    hmaxes = hmaxes or hmax_by_family(config)
    rows: list[dict[str, Any]] = []
    for family_id, family in family_by_id(config).items():
        rows.append(
            {
                "family_id": family_id,
                "description": family["description"],
                "smoothness": family["smoothness"],
                "endpoint_behavior": family["endpoint_behavior"],
                "low_type": family["low"]["type"],
                "low_transition": str(family["low"]["transition"]),
                "medium_type": family["medium"]["type"],
                "medium_rise": str(family["medium"]["rise"]),
                "medium_plateau": str(family["medium"]["plateau"]),
                "medium_fall": str(family["medium"]["fall"]),
                "high_type": family["high"]["type"],
                "high_transition": str(family["high"]["transition"]),
                "entropy_formula": config["entropy_formula"],
                "entropy_normalization": config["entropy_normalization"],
                "Hmax": round(hmaxes[family_id], 12),
            }
        )
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def latex_escape(value: Any) -> str:
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
    return "".join(replacements.get(char, char) for char in text)


def write_latex_table(rows: list[dict[str, Any]], columns: list[str], path: Path, *, caption: str, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        rf"\caption{{{latex_escape(caption)}}}",
        rf"\label{{{latex_escape(label)}}}",
        r"\begin{tabular}{" + "l" * len(columns) + r"}",
        r"\hline",
        " & ".join(latex_escape(column) for column in columns) + r" \\",
        r"\hline",
    ]
    for row in rows:
        lines.append(" & ".join(latex_escape(row.get(column, "")) for column in columns) + r" \\")
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def required_artifact_paths(output_dir: Path) -> dict[str, str]:
    return {name: str(output_dir / filename) for name, filename in REQUIRED_ARTIFACTS.items()}


def write_analysis_summary(config_path: Path, config: dict[str, Any], output_dir: Path, hmaxes: dict[str, float]) -> None:
    grid = config["score_grid"]
    summary = {
        "config_path": str(config_path),
        "config_sha256": file_sha256(config_path),
        "workflow_scripts": WORKFLOW_SCRIPTS,
        "score_grid": {
            "start": grid["start"],
            "stop": grid["stop"],
            "step": grid["step"],
            "n_points": len(score_grid(config)),
        },
        "family_ids": family_ids(config),
        "Hmax_by_family": {family_id: round(value, 12) for family_id, value in hmaxes.items()},
        "generated_artifacts": required_artifact_paths(output_dir),
        "no_api_calls_made": True,
        "no_raw_jsonl_files_read_or_copied": True,
        "no_submitted_pdfs_modified": True,
        "artifact_content_scope": "score_axis_only",
    }
    (output_dir / "analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
