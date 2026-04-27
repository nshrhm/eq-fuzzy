from __future__ import annotations

"""Analyze ICICIC 2026 EQ-Fuzzy matched-subset raw JSONL output."""

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.fuzzy_entropy import entropy_for_score, hmax_by_family, load_membership_config  # noqa: E402


EMOTIONS = ("interest", "surprise", "sadness", "anger")
DEFAULT_INPUT = "runs/icicic2026/icicic2026_benchmark_positioning_v1_stable6_main/raw.jsonl"
DEFAULT_OUTPUT_DIR = "artifacts/icicic2026/matched_subset_stable6_analysis_v1"
DEFAULT_MEMBERSHIP_CONFIG = "configs/scis/fuzzy_membership_v1.yaml"


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


def score_value(parsed: dict[str, Any], emotion: str) -> int | None:
    value = (parsed.get("scores") or {}).get(emotion)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def reason_value(parsed: dict[str, Any], emotion: str) -> str:
    value = (parsed.get("reasons") or {}).get(emotion)
    if isinstance(value, str):
        return value
    return ""


def profile_entropy(scores: list[float]) -> float:
    total = sum(max(score, 0.0) for score in scores)
    if total <= 0.0:
        return 0.0
    entropy = 0.0
    for score in scores:
        p = max(score, 0.0) / total
        if p > 0.0:
            entropy -= p * math.log2(p)
    return entropy / math.log2(len(scores))


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("percentile requires at least one value")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lower = int(math.floor(pos))
    upper = int(math.ceil(pos))
    if lower == upper:
        return ordered[lower]
    weight = pos - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "n_valid": 0,
            "mean": "",
            "median": "",
            "sd": "",
            "iqr": "",
            "min": "",
            "max": "",
        }
    q1 = percentile(values, 0.25)
    q3 = percentile(values, 0.75)
    return {
        "n_valid": len(values),
        "mean": round(mean(values), 6),
        "median": round(median(values), 6),
        "sd": round(pstdev(values), 6),
        "iqr": round(q3 - q1, 6),
        "min": round(min(values), 6),
        "max": round(max(values), 6),
    }


def expand_emotion_rows(
    records: list[dict[str, Any]],
    *,
    primary_family: str,
    hmax: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
        validation_errors = ";".join(str(err) for err in (record.get("validation_errors") or []))
        for emotion in EMOTIONS:
            score = score_value(parsed, emotion)
            row: dict[str, Any] = {
                "run_id": record.get("run_id", ""),
                "stage": record.get("stage", ""),
                "design_id": record.get("design_id", ""),
                "manifest_row": record.get("manifest_row", ""),
                "model_id": record.get("model_id", ""),
                "provider": record.get("provider", ""),
                "language": record.get("language", ""),
                "story_id": record.get("story_id", ""),
                "target_mode": record.get("target_mode", ""),
                "target_label": record.get("target_label", ""),
                "persona_id": record.get("persona_id", ""),
                "temperature": record.get("temperature", ""),
                "repetition": record.get("repetition", ""),
                "emotion": emotion,
                "score": score if score is not None else "",
                "reason": reason_value(parsed, emotion),
                "ok": bool(record.get("ok") is True and score is not None),
                "response_ok": bool(record.get("ok") is True),
                "validation_errors": validation_errors,
                "membership_family": primary_family,
                "membership_hmax": round(hmax, 12),
            }
            if score is None:
                row.update({"mu_low": "", "mu_medium": "", "mu_high": "", "H_raw": "", "H_norm": ""})
            else:
                entropy = entropy_for_score(primary_family, float(score), hmax)
                row.update(
                    {
                        "mu_low": round(entropy["mu_low"], 12),
                        "mu_medium": round(entropy["mu_medium"], 12),
                        "mu_high": round(entropy["mu_high"], 12),
                        "H_raw": round(entropy["H_raw"], 12),
                        "H_norm": round(entropy["H_norm"], 12),
                    }
                )
            rows.append(row)
    return rows


def build_profile_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
        scores = [score_value(parsed, emotion) for emotion in EMOTIONS]
        valid = bool(record.get("ok") is True and all(score is not None for score in scores))
        rows.append(
            {
                "run_id": record.get("run_id", ""),
                "stage": record.get("stage", ""),
                "design_id": record.get("design_id", ""),
                "manifest_row": record.get("manifest_row", ""),
                "model_id": record.get("model_id", ""),
                "provider": record.get("provider", ""),
                "language": record.get("language", ""),
                "story_id": record.get("story_id", ""),
                "target_mode": record.get("target_mode", ""),
                "repetition": record.get("repetition", ""),
                "ok": valid,
                "profile_entropy": round(profile_entropy([float(score) for score in scores if score is not None]), 9)
                if valid
                else "",
            }
        )
    return rows


def build_cell_summary(emotion_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in emotion_rows:
        key = (
            str(row["model_id"]),
            str(row["provider"]),
            str(row["story_id"]),
            str(row["target_mode"]),
            str(row["emotion"]),
        )
        grouped[key].append(row)

    out: list[dict[str, Any]] = []
    for (model_id, provider, story_id, target_mode, emotion), rows in sorted(grouped.items()):
        valid_scores = [float(row["score"]) for row in rows if row["ok"] is True and row["score"] != ""]
        valid_entropy = [float(row["H_norm"]) for row in rows if row["ok"] is True and row["H_norm"] != ""]
        score_stats = stats(valid_scores)
        entropy_stats = stats(valid_entropy)
        out.append(
            {
                "model_id": model_id,
                "provider": provider,
                "story_id": story_id,
                "target_mode": target_mode,
                "emotion": emotion,
                "n_attempts": len(rows),
                "n_ok": len([row for row in rows if row["response_ok"] is True]),
                "valid_output_rate": round(
                    len([row for row in rows if row["response_ok"] is True]) / len(rows),
                    6,
                ),
                "n_valid_scores": score_stats["n_valid"],
                "mean_score": score_stats["mean"],
                "median_score": score_stats["median"],
                "sd_score": score_stats["sd"],
                "iqr_score": score_stats["iqr"],
                "mean_H_norm": entropy_stats["mean"],
                "median_H_norm": entropy_stats["median"],
                "sd_H_norm": entropy_stats["sd"],
            }
        )
    return out


def build_target_shift(cell_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in cell_summary:
        key = (row["model_id"], row["provider"], row["story_id"], row["emotion"])
        by_key[key][row["target_mode"]] = row

    out: list[dict[str, Any]] = []
    for (model_id, provider, story_id, emotion), modes in sorted(by_key.items()):
        reader = modes.get("reader_side")
        character = modes.get("character_side")
        if not reader or not character or reader["mean_score"] == "" or character["mean_score"] == "":
            continue
        out.append(
            {
                "model_id": model_id,
                "provider": provider,
                "story_id": story_id,
                "emotion": emotion,
                "reader_mean_score": reader["mean_score"],
                "character_mean_score": character["mean_score"],
                "target_shift_abs": round(abs(float(reader["mean_score"]) - float(character["mean_score"])), 6),
            }
        )
    return out


def build_model_summary(
    records: list[dict[str, Any]],
    cell_summary: list[dict[str, Any]],
    profile_rows: list[dict[str, Any]],
    target_shift_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    models = sorted({str(record.get("model_id", "")) for record in records})
    out: list[dict[str, Any]] = []
    for model_id in models:
        model_records = [record for record in records if record.get("model_id") == model_id]
        model_cells = [row for row in cell_summary if row["model_id"] == model_id]
        model_profiles = [row for row in profile_rows if row["model_id"] == model_id and row["profile_entropy"] != ""]
        model_shifts = [row for row in target_shift_rows if row["model_id"] == model_id]
        valid_rates = [float(row["valid_output_rate"]) for row in model_cells]
        sd_scores = [float(row["sd_score"]) for row in model_cells if row["sd_score"] != ""]
        h_norm = [float(row["mean_H_norm"]) for row in model_cells if row["mean_H_norm"] != ""]
        profile_values = [float(row["profile_entropy"]) for row in model_profiles]
        shifts = [float(row["target_shift_abs"]) for row in model_shifts]
        out.append(
            {
                "model_id": model_id,
                "provider": model_records[0].get("provider", "") if model_records else "",
                "n_responses": len(model_records),
                "valid_output_rate": round(
                    len([record for record in model_records if record.get("ok") is True]) / len(model_records),
                    6,
                )
                if model_records
                else "",
                "mean_cell_valid_output_rate": round(mean(valid_rates), 6) if valid_rates else "",
                "mean_within_cell_sd_score": round(mean(sd_scores), 6) if sd_scores else "",
                "mean_cell_H_norm": round(mean(h_norm), 6) if h_norm else "",
                "mean_profile_entropy": round(mean(profile_values), 6) if profile_values else "",
                "mean_target_shift_abs": round(mean(shifts), 6) if shifts else "",
            }
        )
    return out


def run_analysis(
    *,
    input_jsonl: Path,
    output_dir: Path,
    membership_config_path: Path,
) -> dict[str, Any]:
    records = load_jsonl(input_jsonl)
    config = load_membership_config(membership_config_path)
    primary_family = str(config["primary_family"])
    hmaxes = hmax_by_family(config)
    primary_hmax = hmaxes[primary_family]
    emotion_rows = expand_emotion_rows(records, primary_family=primary_family, hmax=primary_hmax)
    profile_rows = build_profile_rows(records)
    cell_summary = build_cell_summary(emotion_rows)
    target_shift = build_target_shift(cell_summary)
    model_summary = build_model_summary(records, cell_summary, profile_rows, target_shift)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(emotion_rows, output_dir / "emotion_long.csv")
    write_csv(profile_rows, output_dir / "response_profile_entropy.csv")
    write_csv(cell_summary, output_dir / "cell_summary.csv")
    write_csv(target_shift, output_dir / "target_shift.csv")
    write_csv(model_summary, output_dir / "model_summary.csv")
    summary = {
        "analysis_id": "icicic2026_matched_subset_analysis_v1",
        "input_jsonl": str(input_jsonl),
        "n_response_rows": len(records),
        "n_emotion_rows": len(emotion_rows),
        "n_cell_rows": len(cell_summary),
        "n_target_shift_rows": len(target_shift),
        "n_model_rows": len(model_summary),
        "primary_membership_family": primary_family,
        "claim_discipline": "descriptive uncertainty, stability, and target-control analysis only",
    }
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
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    summary = run_analysis(
        input_jsonl=repo_root / args.input_jsonl,
        output_dir=repo_root / args.output_dir,
        membership_config_path=repo_root / args.membership_config,
    )
    print(f"Wrote ICICIC matched-subset analysis with {summary['n_response_rows']} response rows.")


if __name__ == "__main__":
    main()
