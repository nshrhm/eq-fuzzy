from __future__ import annotations

"""Build SCIS 2026 factorial run manifests from the locked Phase 2 design."""

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG = "configs/scis/factorial_v1.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
    return result.stdout.strip()


def default_output_path(repo_root: Path, design_id: str, stage: str) -> Path:
    run_id = f"{design_id}_{stage}_manifest_v1"
    return repo_root / "runs" / "scis2026" / run_id / "manifest.csv"


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def selected_models(panel: dict[str, Any], count: int) -> list[dict[str, Any]]:
    models = list(panel.get("models", []))
    if len(models) < count:
        raise ValueError(f"Panel contains {len(models)} models, but stage requires {count}.")
    return models[:count]


def build_manifest(
    *,
    repo_root: Path,
    config_path: Path,
    stage_name: str,
    output_path: Path | None,
) -> list[dict[str, Any]]:
    config = load_yaml(config_path)
    study = config["study"]
    prompt = config["prompt"]
    api_controls = config["api_controls"]
    stage = config["run_stages"][stage_name]
    design_id = study["design_id"]

    if output_path is None:
        output_path = default_output_path(repo_root, design_id, stage_name)
    run_id = output_path.parent.name

    panel = load_yaml(repo_root / study["main_panel"])
    models = selected_models(panel, int(stage["models"]))
    condition_rows = load_csv(repo_root / study["condition_table"])
    story_ids = list(stage["story_ids"])
    repetitions = range(1, int(stage["repetitions"]) + 1)
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    required_paths = {
        "factorial_config": config_path,
        "condition_table": repo_root / study["condition_table"],
        "main_panel": repo_root / study["main_panel"],
        "system_prompt": repo_root / prompt["system_prompt"],
        "user_template": repo_root / prompt["user_template"],
        "response_schema": repo_root / study["response_schema"],
        "text_registry": repo_root / study["text_registry"],
        "persona_registry": repo_root / study["persona_registry"],
    }
    hashes = {f"{name}_sha256": file_sha256(path) for name, path in required_paths.items()}
    commit = git_commit(repo_root)

    rows: list[dict[str, Any]] = []
    manifest_row = 0
    for model in models:
        for story_id in story_ids:
            for condition in condition_rows:
                for repetition in repetitions:
                    rows.append(
                        {
                            "manifest_row": manifest_row,
                            "run_id": run_id,
                            "stage": stage_name,
                            "design_id": design_id,
                            "created_at_utc": created_at,
                            "model_id": model["model_id"],
                            "provider": model.get("provider", api_controls.get("provider", "openrouter")),
                            "route": model.get("route", "openrouter"),
                            "panel_role": model.get("panel_role", ""),
                            "reasoning_json": json.dumps(model.get("reasoning", {"exclude": True}), sort_keys=True),
                            "language": study["primary_language"],
                            "story_id": story_id,
                            "condition_id": condition["condition_id"],
                            "persona_id": condition["persona_id"],
                            "persona_label": condition["persona_label"],
                            "temperature": float(condition["temperature"]),
                            "temperature_label": condition["temperature_label"],
                            "top_p": float(api_controls.get("top_p", 1.0)),
                            "max_completion_tokens": int(api_controls.get("max_completion_tokens", 700)),
                            "repetition": int(repetition),
                            "system_prompt": prompt["system_prompt"],
                            "user_template": prompt["user_template"],
                            "response_schema": study["response_schema"],
                            "texts_dir": study["texts_dir"],
                            "text_registry": study["text_registry"],
                            "persona_registry": study["persona_registry"],
                            "main_panel": study["main_panel"],
                            "factorial_config": str(config_path.relative_to(repo_root)),
                            "temperature_policy": prompt["temperature_policy"],
                            "persona_policy": prompt["persona_policy"],
                            "git_commit": commit,
                            **hashes,
                        }
                    )
                    manifest_row += 1

    if len(rows) != int(stage["expected_trials"]):
        raise ValueError(f"Built {len(rows)} rows, expected {stage['expected_trials']} for {stage_name}.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "run_id": run_id,
        "design_id": design_id,
        "stage": stage_name,
        "n_rows": len(rows),
        "n_models": len(models),
        "n_stories": len(story_ids),
        "n_conditions": len(condition_rows),
        "n_repetitions": len(list(repetitions)),
        "output_manifest": display_path(output_path, repo_root),
        "git_commit": commit,
    }
    (output_path.parent / "manifest_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--stage", choices=("sanity", "pilot", "main"), default="sanity")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_path = (repo_root / args.output).resolve() if args.output else None
    rows = build_manifest(
        repo_root=repo_root,
        config_path=(repo_root / args.config).resolve(),
        stage_name=args.stage,
        output_path=output_path,
    )
    print(f"Wrote {len(rows)} rows.")


if __name__ == "__main__":
    main()
