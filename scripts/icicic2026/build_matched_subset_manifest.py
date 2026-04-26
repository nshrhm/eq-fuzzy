from __future__ import annotations

"""Build ICICIC 2026 EQ-Fuzzy matched-subset manifests."""

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG = "configs/icicic/benchmark_positioning_v1.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def default_output_path(repo_root: Path, config: dict[str, Any], stage: str) -> Path:
    outputs = config["outputs"]
    key = f"{stage}_manifest"
    return repo_root / outputs[key]


def selected_models(panel: dict[str, Any], stage: str) -> list[dict[str, Any]]:
    models = [model for model in panel.get("models", []) if model.get("default_include", True)]
    if stage == "sanity":
        return models[:1]
    return models


def selected_story_ids(story_ids: list[str], stage: str) -> list[str]:
    if stage == "sanity":
        return story_ids[:1]
    return story_ids


def build_manifest(
    *,
    repo_root: Path,
    config_path: Path,
    stage: str,
    output_path: Path | None,
) -> list[dict[str, Any]]:
    config = load_yaml(config_path)
    study = config["study"]
    prompts = config["prompts"]
    api_controls = config["api_controls"]
    panel = load_yaml(repo_root / study["model_panel"])

    models = selected_models(panel, stage)
    story_ids = selected_story_ids(list(study["story_ids"]), stage)
    target_modes = list(study["target_modes"])
    repetitions = range(1, int(study["repetitions"][stage]) + 1)
    if output_path is None:
        output_path = default_output_path(repo_root, config, stage)
    run_id = output_path.parent.name
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    required_paths = {
        "config": config_path,
        "model_panel": repo_root / study["model_panel"],
        "system_prompt": repo_root / prompts["system_prompt"],
        "user_template": repo_root / prompts["user_template"],
        "response_schema": repo_root / study["response_schema"],
        "text_registry": repo_root / study["text_registry"],
        "membership_config": repo_root / study["membership_config"],
    }
    hashes = {f"{name}_sha256": file_sha256(path) for name, path in required_paths.items()}
    commit = git_commit(repo_root)

    rows: list[dict[str, Any]] = []
    manifest_row = 0
    for model in models:
        for story_id in story_ids:
            for target in target_modes:
                for repetition in repetitions:
                    rows.append(
                        {
                            "manifest_row": manifest_row,
                            "run_id": run_id,
                            "stage": stage,
                            "design_id": study["design_id"],
                            "created_at_utc": created_at,
                            "model_id": model["model_id"],
                            "provider": model.get("provider", api_controls.get("provider", "openrouter")),
                            "route": model.get("route", "openrouter"),
                            "language": study["primary_language"],
                            "story_id": story_id,
                            "target_mode": target["target_mode"],
                            "target_label": target["target_label"],
                            "target_focus": target["prompt_focus"],
                            "persona_id": "p0",
                            "persona_label": "neutral_reader",
                            "temperature": float(api_controls["temperature"]),
                            "top_p": float(api_controls["top_p"]),
                            "max_completion_tokens": int(api_controls["max_completion_tokens"]),
                            "repetition": int(repetition),
                            "system_prompt": prompts["system_prompt"],
                            "user_template": prompts["user_template"],
                            "prompt_version": prompts["prompt_version"],
                            "response_schema": study["response_schema"],
                            "schema_version": prompts["schema_version"],
                            "text_registry": study["text_registry"],
                            "texts_dir": study["texts_dir"],
                            "model_panel": study["model_panel"],
                            "membership_config": study["membership_config"],
                            "git_commit": commit,
                            "reasoning_json": json.dumps(model.get("reasoning", {"exclude": True}), sort_keys=True),
                            **hashes,
                        }
                    )
                    manifest_row += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "run_id": run_id,
        "design_id": study["design_id"],
        "stage": stage,
        "n_rows": len(rows),
        "n_models": len(models),
        "n_stories": len(story_ids),
        "n_target_modes": len(target_modes),
        "n_repetitions": len(list(repetitions)),
        "output_manifest": str(output_path),
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
    parser.add_argument("--stage", choices=("sanity", "main"), default="sanity")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_path = (repo_root / args.output).resolve() if args.output else None
    rows = build_manifest(
        repo_root=repo_root,
        config_path=(repo_root / args.config).resolve(),
        stage=args.stage,
        output_path=output_path,
    )
    print(f"Wrote {len(rows)} ICICIC matched-subset rows.")


if __name__ == "__main__":
    main()
