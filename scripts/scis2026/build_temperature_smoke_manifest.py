from __future__ import annotations

"""Build the SCIS 2026 Phase 1 temperature smoke-test manifest."""

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG = "configs/scis/model_candidates_smoke_v1.yaml"
DEFAULT_OUTPUT = "runs/scis2026/phase1_temperature_smoke_v1/manifest.csv"


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


def flatten_models(config: dict[str, Any], include_groups: set[str]) -> list[dict[str, Any]]:
    groups = config.get("models", {})
    rows: list[dict[str, Any]] = []
    for group_name, models in groups.items():
        if include_groups and group_name not in include_groups:
            continue
        for model in models or []:
            row = dict(model)
            row["model_group"] = group_name
            rows.append(row)
    return rows


def build_manifest(
    *,
    repo_root: Path,
    config_path: Path,
    include_groups: set[str],
    output_path: Path,
) -> list[dict[str, Any]]:
    config = load_yaml(config_path)
    smoke = config["smoke_test"]
    models = flatten_models(config, include_groups)
    if not models:
        raise ValueError("No models selected for the smoke manifest.")

    temperatures = [float(t) for t in smoke["temperatures"]]
    repetitions = range(1, int(smoke.get("repetitions", 1)) + 1)
    run_id = output_path.parent.name
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    system_prompt = repo_root / smoke["system_prompt"]
    user_template = repo_root / smoke["user_template"]
    response_schema = repo_root / smoke["response_schema"]
    text_registry = repo_root / smoke["text_registry"]
    persona_registry = repo_root / smoke["persona_registry"]

    rows: list[dict[str, Any]] = []
    manifest_row = 0
    for model in models:
        for temp in temperatures:
            for repetition in repetitions:
                rows.append(
                    {
                        "manifest_row": manifest_row,
                        "run_id": run_id,
                        "created_at_utc": created_at,
                        "catalog_id": config["catalog_id"],
                        "model_id": model["model_id"],
                        "provider": model.get("provider", "openrouter"),
                        "route": model.get("route", "openrouter"),
                        "model_group": model["model_group"],
                        "candidate_role": model.get("candidate_role", ""),
                        "temperature": temp,
                        "top_p": float(smoke.get("top_p", 1.0)),
                        "max_completion_tokens": int(smoke.get("max_completion_tokens", 700)),
                        "reasoning_json": json.dumps(model.get("reasoning", {"exclude": True}), sort_keys=True),
                        "language": smoke["language"],
                        "story_id": smoke["story_id"],
                        "persona_id": smoke["persona_id"],
                        "repetition": int(repetition),
                        "system_prompt": smoke["system_prompt"],
                        "user_template": smoke["user_template"],
                        "response_schema": smoke["response_schema"],
                        "texts_dir": smoke["texts_dir"],
                        "text_registry": smoke["text_registry"],
                        "persona_registry": smoke["persona_registry"],
                        "system_prompt_sha256": file_sha256(system_prompt),
                        "user_template_sha256": file_sha256(user_template),
                        "response_schema_sha256": file_sha256(response_schema),
                        "text_registry_sha256": file_sha256(text_registry),
                        "persona_registry_sha256": file_sha256(persona_registry),
                        "git_commit": git_commit(repo_root),
                        "temperature_policy": "api_parameter_only_not_prompt_text",
                    }
                )
                manifest_row += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--include-group",
        action="append",
        default=None,
        help="Model group to include. Repeat to include reserve or bridge groups.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_path = (repo_root / args.output).resolve()
    rows = build_manifest(
        repo_root=repo_root,
        config_path=(repo_root / args.config).resolve(),
        include_groups=set(args.include_group or ["main_panel_candidates"]),
        output_path=output_path,
    )
    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
