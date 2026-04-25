from __future__ import annotations

"""Prepare SCIS factorial run outputs for pilot/main analysis readiness checks."""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev, variance
from typing import Any

from fuzzy_entropy import configured_families, entropy_for_score, hmax_by_family, load_membership_config


EMOTIONS = ("interest", "surprise", "sadness", "anger")
DEFAULT_INPUT = "runs/scis2026/scis2026_factorial_v1_pilot_manifest_v1/raw.jsonl"
DEFAULT_OUTPUT_DIR = "artifacts/scis2026/pilot_analysis_v1"
DEFAULT_MEMBERSHIP_CONFIG = "configs/scis/fuzzy_membership_v1.yaml"
DEFAULT_EXPECTED_RESPONSES = 576
DEFAULT_EXPECTED_EMOTION_ROWS = 2304
DEFAULT_EXPECTED_DECOMPOSITION_UNITS = 48


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def score_value(parsed: dict[str, Any], emotion: str) -> int | None:
    value = (parsed.get("scores") or {}).get(emotion)
    if isinstance(value, int):
        return value
    return None


def reason_value(parsed: dict[str, Any], emotion: str) -> str:
    value = (parsed.get("reasons") or {}).get(emotion)
    if isinstance(value, str):
        return value
    return ""


def expand_emotion_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
        validation_errors = ";".join(str(err) for err in (record.get("validation_errors") or []))
        for emotion in EMOTIONS:
            score = score_value(parsed, emotion)
            rows.append(
                {
                    "run_id": record.get("run_id", ""),
                    "stage": record.get("stage", ""),
                    "design_id": record.get("design_id", ""),
                    "manifest_row": record.get("manifest_row", ""),
                    "model_id": record.get("model_id", ""),
                    "story_id": record.get("story_id", ""),
                    "condition_id": record.get("condition_id", ""),
                    "persona_id": record.get("persona_id", ""),
                    "persona_label": record.get("persona_label", ""),
                    "temperature": record.get("temperature", ""),
                    "temperature_label": record.get("temperature_label", ""),
                    "repetition": record.get("repetition", ""),
                    "emotion": emotion,
                    "score": score if score is not None else "",
                    "reason": reason_value(parsed, emotion),
                    "ok": bool(record.get("ok") is True and score is not None),
                    "response_ok": bool(record.get("ok") is True),
                    "validation_errors": validation_errors,
                }
            )
    return rows


def valid_scores(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row["ok"] is True and row["score"] != ""]


def numeric_scores(rows: list[dict[str, Any]]) -> list[float]:
    return [float(row["score"]) for row in rows if row["score"] != ""]


def numeric_column(rows: list[dict[str, Any]], column: str) -> list[float]:
    return [float(row[column]) for row in rows if row.get(column) not in ("", None)]


def entropy_stats(rows: list[dict[str, Any]], column: str) -> dict[str, Any]:
    values = numeric_column(rows, column)
    if not values:
        return {
            f"n_valid_{column}": 0,
            f"mean_{column}": "",
            f"median_{column}": "",
            f"sd_{column}": "",
            f"min_{column}": "",
            f"max_{column}": "",
        }
    return {
        f"n_valid_{column}": len(values),
        f"mean_{column}": round(mean(values), 9),
        f"median_{column}": round(median(values), 9),
        f"sd_{column}": round(pstdev(values), 9),
        f"min_{column}": round(min(values), 9),
        f"max_{column}": round(max(values), 9),
    }


def summary_stats(scores: list[float]) -> dict[str, Any]:
    if not scores:
        return {
            "n_valid_scores": 0,
            "mean_score": "",
            "median_score": "",
            "sd_score": "",
            "var_score": "",
            "min_score": "",
            "max_score": "",
            "mean_abs_dev_from_median": "",
        }
    med = median(scores)
    return {
        "n_valid_scores": len(scores),
        "mean_score": round(mean(scores), 6),
        "median_score": round(med, 6),
        "sd_score": round(pstdev(scores), 6),
        "var_score": round(variance(scores), 6) if len(scores) >= 2 else "",
        "min_score": round(min(scores), 6),
        "max_score": round(max(scores), 6),
        "mean_abs_dev_from_median": round(mean(abs(score - med) for score in scores), 6),
    }


def add_primary_entropy_columns(
    rows: list[dict[str, Any]],
    *,
    primary_family: str,
    hmax: float,
) -> None:
    for row in rows:
        row["membership_family"] = primary_family
        row["membership_hmax"] = round(hmax, 12)
        if row["score"] == "":
            row["mu_low"] = ""
            row["mu_medium"] = ""
            row["mu_high"] = ""
            row["H_raw"] = ""
            row["H_norm"] = ""
            continue
        entropy = entropy_for_score(primary_family, float(row["score"]), hmax)
        row["mu_low"] = round(entropy["mu_low"], 12)
        row["mu_medium"] = round(entropy["mu_medium"], 12)
        row["mu_high"] = round(entropy["mu_high"], 12)
        row["H_raw"] = round(entropy["H_raw"], 12)
        row["H_norm"] = round(entropy["H_norm"], 12)


def build_entropy_rows(
    emotion_rows: list[dict[str, Any]],
    *,
    families: list[str],
    hmaxes: dict[str, float],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in emotion_rows:
        for family in families:
            out = {
                "run_id": row["run_id"],
                "stage": row["stage"],
                "design_id": row["design_id"],
                "manifest_row": row["manifest_row"],
                "model_id": row["model_id"],
                "story_id": row["story_id"],
                "condition_id": row["condition_id"],
                "persona_id": row["persona_id"],
                "persona_label": row["persona_label"],
                "temperature": row["temperature"],
                "temperature_label": row["temperature_label"],
                "repetition": row["repetition"],
                "emotion": row["emotion"],
                "score": row["score"],
                "ok": row["ok"],
                "response_ok": row["response_ok"],
                "membership_family": family,
                "membership_hmax": round(hmaxes[family], 12),
            }
            if row["score"] == "":
                out.update({"mu_low": "", "mu_medium": "", "mu_high": "", "H_raw": "", "H_norm": ""})
            else:
                entropy = entropy_for_score(family, float(row["score"]), hmaxes[family])
                out.update(
                    {
                        "mu_low": round(entropy["mu_low"], 12),
                        "mu_medium": round(entropy["mu_medium"], 12),
                        "mu_high": round(entropy["mu_high"], 12),
                        "H_raw": round(entropy["H_raw"], 12),
                        "H_norm": round(entropy["H_norm"], 12),
                    }
                )
            rows.append(out)
    return rows


def cell_key(row: dict[str, Any]) -> tuple[str, str, str, float, str]:
    return (
        str(row["model_id"]),
        str(row["story_id"]),
        str(row["persona_id"]),
        float(row["temperature"]),
        str(row["emotion"]),
    )


def build_cell_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, float, str], list[dict[str, Any]]] = defaultdict(list)
    condition_by_cell: dict[tuple[str, str, str, float, str], str] = {}
    label_by_cell: dict[tuple[str, str, str, float, str], str] = {}
    for row in rows:
        key = cell_key(row)
        grouped[key].append(row)
        condition_by_cell[key] = str(row["condition_id"])
        label_by_cell[key] = str(row["temperature_label"])

    out: list[dict[str, Any]] = []
    for key, cell_rows in sorted(grouped.items()):
        model_id, story_id, persona_id, temperature, emotion = key
        scores = numeric_scores(cell_rows)
        out.append(
            {
                "model_id": model_id,
                "story_id": story_id,
                "condition_id": condition_by_cell[key],
                "persona_id": persona_id,
                "temperature": temperature,
                "temperature_label": label_by_cell[key],
                "emotion": emotion,
                "n_attempts": len(cell_rows),
                **summary_stats(scores),
                "n_missing_scores": len(cell_rows) - len(scores),
            }
        )
    return out


def entropy_cell_key(row: dict[str, Any]) -> tuple[str, str, str, float, str, str]:
    return (
        str(row["model_id"]),
        str(row["story_id"]),
        str(row["persona_id"]),
        float(row["temperature"]),
        str(row["emotion"]),
        str(row["membership_family"]),
    )


def build_entropy_cell_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, float, str, str], list[dict[str, Any]]] = defaultdict(list)
    condition_by_cell: dict[tuple[str, str, str, float, str, str], str] = {}
    label_by_cell: dict[tuple[str, str, str, float, str, str], str] = {}
    hmax_by_cell: dict[tuple[str, str, str, float, str, str], Any] = {}
    for row in rows:
        key = entropy_cell_key(row)
        grouped[key].append(row)
        condition_by_cell[key] = str(row["condition_id"])
        label_by_cell[key] = str(row["temperature_label"])
        hmax_by_cell[key] = row["membership_hmax"]

    out: list[dict[str, Any]] = []
    for key, cell_rows in sorted(grouped.items()):
        model_id, story_id, persona_id, temperature, emotion, family = key
        valid_h = numeric_column(cell_rows, "H_norm")
        out.append(
            {
                "model_id": model_id,
                "story_id": story_id,
                "condition_id": condition_by_cell[key],
                "persona_id": persona_id,
                "temperature": temperature,
                "temperature_label": label_by_cell[key],
                "emotion": emotion,
                "membership_family": family,
                "membership_hmax": hmax_by_cell[key],
                "n_attempts": len(cell_rows),
                "n_valid_entropy": len(valid_h),
                "n_missing_entropy": len(cell_rows) - len(valid_h),
                **entropy_stats(cell_rows, "H_raw"),
                **entropy_stats(cell_rows, "H_norm"),
            }
        )
    return out


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2 or len(x) != len(y):
        return None
    mx = mean(x)
    my = mean(y)
    sx = sum((value - mx) ** 2 for value in x)
    sy = sum((value - my) ** 2 for value in y)
    if sx == 0.0 or sy == 0.0:
        return None
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return cov / (sx * sy) ** 0.5


def build_entropy_family_comparison(
    entropy_cell_summary: list[dict[str, Any]],
    *,
    primary_family: str,
    baseline_families: list[str],
) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str, str, float], dict[str, float]] = defaultdict(dict)
    for row in entropy_cell_summary:
        if row["mean_H_norm"] == "":
            continue
        key = (
            str(row["model_id"]),
            str(row["story_id"]),
            str(row["emotion"]),
            str(row["persona_id"]),
            float(row["temperature"]),
        )
        by_key[key][str(row["membership_family"])] = float(row["mean_H_norm"])

    out: list[dict[str, Any]] = []
    for baseline in baseline_families:
        pairs = [
            (values[primary_family], values[baseline])
            for values in by_key.values()
            if primary_family in values and baseline in values
        ]
        diffs = [abs(primary - base) for primary, base in pairs]
        corr = pearson([primary for primary, _ in pairs], [base for _, base in pairs])
        out.append(
            {
                "primary_family": primary_family,
                "baseline_family": baseline,
                "n_cell_pairs": len(pairs),
                "pearson_H_norm_cell_mean": round(corr, 9) if corr is not None else "",
                "mean_abs_H_norm_diff": round(mean(diffs), 9) if diffs else "",
                "max_abs_H_norm_diff": round(max(diffs), 9) if diffs else "",
            }
        )
    return out


def build_heatmap_table(cell_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], dict[float, Any]] = defaultdict(dict)
    for row in cell_summary:
        key = (str(row["model_id"]), str(row["story_id"]), str(row["emotion"]), str(row["persona_id"]))
        grouped[key][float(row["temperature"])] = row["mean_score"]

    temperatures = sorted({float(row["temperature"]) for row in cell_summary})
    out: list[dict[str, Any]] = []
    for key, values in sorted(grouped.items()):
        model_id, story_id, emotion, persona_id = key
        row: dict[str, Any] = {
            "model_id": model_id,
            "story_id": story_id,
            "emotion": emotion,
            "persona_id": persona_id,
        }
        for temperature in temperatures:
            row[f"temp_{str(temperature).replace('.', '_')}"] = values.get(temperature, "")
        out.append(row)
    return out


def expected_cell_keys(rows: list[dict[str, Any]]) -> set[tuple[str, str, str, float, str]]:
    models = sorted({str(row["model_id"]) for row in rows})
    stories = sorted({str(row["story_id"]) for row in rows})
    personas = sorted({str(row["persona_id"]) for row in rows})
    temperatures = sorted({float(row["temperature"]) for row in rows})
    return {
        (model_id, story_id, persona_id, temperature, emotion)
        for model_id in models
        for story_id in stories
        for persona_id in personas
        for temperature in temperatures
        for emotion in EMOTIONS
    }


def decompose_two_way(values: dict[tuple[str, float], float]) -> dict[str, Any]:
    personas = sorted({persona_id for persona_id, _ in values})
    temperatures = sorted({temperature for _, temperature in values})
    expected = {(persona_id, temperature) for persona_id in personas for temperature in temperatures}
    missing = sorted(expected - set(values))
    if missing:
        return {
            "is_estimable": False,
            "missing_cells": len(missing),
            "SS_persona": "",
            "SS_temperature": "",
            "SS_persona_x_temperature": "",
            "interaction_burden": "",
            "separability_share": "",
        }

    grand = mean(values.values())
    persona_means = {
        persona_id: mean(values[(persona_id, temperature)] for temperature in temperatures)
        for persona_id in personas
    }
    temperature_means = {
        temperature: mean(values[(persona_id, temperature)] for persona_id in personas)
        for temperature in temperatures
    }
    ss_persona = len(temperatures) * sum((persona_means[persona_id] - grand) ** 2 for persona_id in personas)
    ss_temperature = len(personas) * sum((temperature_means[temperature] - grand) ** 2 for temperature in temperatures)
    ss_interaction = sum(
        (
            values[(persona_id, temperature)]
            - persona_means[persona_id]
            - temperature_means[temperature]
            + grand
        )
        ** 2
        for persona_id in personas
        for temperature in temperatures
    )
    denominator = ss_persona + ss_temperature + ss_interaction
    interaction_burden = ss_interaction / denominator if denominator else 0.0
    return {
        "is_estimable": True,
        "missing_cells": 0,
        "SS_persona": round(ss_persona, 6),
        "SS_temperature": round(ss_temperature, 6),
        "SS_persona_x_temperature": round(ss_interaction, 6),
        "interaction_burden": round(interaction_burden, 6),
        "separability_share": round(1.0 - interaction_burden, 6),
    }


def build_decomposition(cell_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[tuple[str, float], float]] = defaultdict(dict)
    for row in cell_summary:
        if row["mean_score"] == "":
            continue
        key = (str(row["model_id"]), str(row["story_id"]), str(row["emotion"]))
        grouped[key][(str(row["persona_id"]), float(row["temperature"]))] = float(row["mean_score"])

    out: list[dict[str, Any]] = []
    for key, values in sorted(grouped.items()):
        model_id, story_id, emotion = key
        out.append(
            {
                "model_id": model_id,
                "story_id": story_id,
                "emotion": emotion,
                **decompose_two_way(values),
            }
        )
    return out


def build_analysis_summary(
    *,
    records: list[dict[str, Any]],
    emotion_rows: list[dict[str, Any]],
    entropy_rows: list[dict[str, Any]],
    cell_summary: list[dict[str, Any]],
    entropy_cell_summary: list[dict[str, Any]],
    decomposition: list[dict[str, Any]],
    membership_config_path: Path,
    membership_config: dict[str, Any],
    hmaxes: dict[str, float],
    expected_responses: int,
    expected_emotion_rows: int,
    expected_decomposition_units: int,
) -> dict[str, Any]:
    expected_cells = expected_cell_keys(emotion_rows)
    observed_cells = {cell_key(row) for row in emotion_rows}
    missing_structural_cells = expected_cells - observed_cells
    missing_score_cells = [
        row
        for row in cell_summary
        if int(row["n_valid_scores"]) == 0
    ]
    not_estimable = [row for row in decomposition if row["is_estimable"] is not True]
    failure_reasons: list[str] = []
    if len(records) != expected_responses:
        failure_reasons.append("response row count mismatch")
    if len(emotion_rows) != expected_emotion_rows:
        failure_reasons.append("emotion row count mismatch")
    if missing_structural_cells:
        failure_reasons.append("missing structural score cells")
    if missing_score_cells:
        failure_reasons.append("score cells with zero valid scores")
    if len(decomposition) != expected_decomposition_units:
        failure_reasons.append("decomposition unit count mismatch")
    if not_estimable:
        failure_reasons.append("non-estimable decomposition units")
    primary_family = str(membership_config["primary_family"])
    families = configured_families(membership_config)
    expected_entropy_rows = expected_emotion_rows * len(families)
    primary_missing_entropy = [
        row
        for row in entropy_rows
        if row["membership_family"] == primary_family and row["H_norm"] == ""
    ]
    if len(entropy_rows) != expected_entropy_rows:
        failure_reasons.append("entropy row count mismatch")
    if primary_missing_entropy:
        failure_reasons.append("primary entropy rows missing H_norm")

    return {
        "run_id": records[0].get("run_id") if records else "",
        "stage": records[0].get("stage") if records else "",
        "design_id": records[0].get("design_id") if records else "",
        "membership_config": display_path(membership_config_path),
        "membership_config_sha256": file_sha256(membership_config_path),
        "primary_membership_family": primary_family,
        "baseline_membership_families": membership_config.get("baseline_families", []),
        "membership_hmax": {family: round(hmax, 12) for family, hmax in hmaxes.items()},
        "membership_hmax_method": membership_config["entropy"]["normalized"]["hmax_method"],
        "membership_hmax_grid_step": membership_config["entropy"]["normalized"]["grid_step"],
        "n_response_rows": len(records),
        "n_response_ok": sum(1 for record in records if record.get("ok") is True),
        "n_emotion_rows": len(emotion_rows),
        "n_valid_score_rows": len(valid_scores(emotion_rows)),
        "n_missing_score_rows": sum(1 for row in emotion_rows if row["score"] == ""),
        "n_entropy_rows": len(entropy_rows),
        "n_primary_entropy_missing_rows": len(primary_missing_entropy),
        "n_cell_summary_rows": len(cell_summary),
        "n_entropy_cell_summary_rows": len(entropy_cell_summary),
        "n_missing_structural_cells": len(missing_structural_cells),
        "n_zero_valid_score_cells": len(missing_score_cells),
        "n_decomposition_units": len(decomposition),
        "n_non_estimable_decomposition_units": len(not_estimable),
        "expected_responses": expected_responses,
        "expected_emotion_rows": expected_emotion_rows,
        "expected_decomposition_units": expected_decomposition_units,
        "readiness_passed": not failure_reasons,
        "failure_reasons": failure_reasons,
    }


def run_analysis(
    *,
    input_jsonl: Path,
    output_dir: Path,
    membership_config_path: Path,
    expected_responses: int,
    expected_emotion_rows: int,
    expected_decomposition_units: int,
) -> dict[str, Any]:
    records = load_jsonl(input_jsonl)
    membership_config = load_membership_config(membership_config_path)
    families = configured_families(membership_config)
    primary_family = str(membership_config["primary_family"])
    baseline_families = [str(family) for family in membership_config.get("baseline_families", [])]
    hmaxes = hmax_by_family(membership_config)
    emotion_rows = expand_emotion_rows(records)
    add_primary_entropy_columns(emotion_rows, primary_family=primary_family, hmax=hmaxes[primary_family])
    entropy_rows = build_entropy_rows(emotion_rows, families=families, hmaxes=hmaxes)
    cell_summary = build_cell_summary(emotion_rows)
    entropy_cell_summary = build_entropy_cell_summary(entropy_rows)
    entropy_family_comparison = build_entropy_family_comparison(
        entropy_cell_summary,
        primary_family=primary_family,
        baseline_families=baseline_families,
    )
    heatmap = build_heatmap_table(cell_summary)
    decomposition = build_decomposition(cell_summary)
    summary = build_analysis_summary(
        records=records,
        emotion_rows=emotion_rows,
        entropy_rows=entropy_rows,
        cell_summary=cell_summary,
        entropy_cell_summary=entropy_cell_summary,
        decomposition=decomposition,
        membership_config_path=membership_config_path,
        membership_config=membership_config,
        hmaxes=hmaxes,
        expected_responses=expected_responses,
        expected_emotion_rows=expected_emotion_rows,
        expected_decomposition_units=expected_decomposition_units,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(emotion_rows, output_dir / "emotion_long.csv")
    write_csv(entropy_rows, output_dir / "entropy_long.csv")
    write_csv(cell_summary, output_dir / "cell_score_summary.csv")
    write_csv(entropy_cell_summary, output_dir / "entropy_cell_summary.csv")
    write_csv(entropy_family_comparison, output_dir / "entropy_family_comparison.csv")
    write_csv(heatmap, output_dir / "persona_temperature_mean_grid.csv")
    write_csv(decomposition, output_dir / "factorial_decomposition.csv")
    (output_dir / "analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--input-jsonl", default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--membership-config", default=DEFAULT_MEMBERSHIP_CONFIG)
    parser.add_argument("--expected-responses", type=int, default=DEFAULT_EXPECTED_RESPONSES)
    parser.add_argument("--expected-emotion-rows", type=int, default=DEFAULT_EXPECTED_EMOTION_ROWS)
    parser.add_argument("--expected-decomposition-units", type=int, default=DEFAULT_EXPECTED_DECOMPOSITION_UNITS)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    summary = run_analysis(
        input_jsonl=repo_root / args.input_jsonl,
        output_dir=repo_root / args.output_dir,
        membership_config_path=repo_root / args.membership_config,
        expected_responses=args.expected_responses,
        expected_emotion_rows=args.expected_emotion_rows,
        expected_decomposition_units=args.expected_decomposition_units,
    )
    print(f"Wrote analysis artifacts to {repo_root / args.output_dir}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not summary["readiness_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
