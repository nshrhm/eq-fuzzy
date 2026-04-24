from __future__ import annotations

from pathlib import Path
import itertools
import json
from typing import Any

import pandas as pd
import yaml


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _manifest_summary_path(output_path: Path) -> Path:
    resolved_output = output_path.resolve()
    if resolved_output.parent.name == "manifests" and resolved_output.parent.parent.name == "iceccme2026":
        return resolved_output.parent.parent / "results" / "json" / f"{output_path.stem}_summary.json"
    return output_path.parents[2] / "results" / "json" / f"{output_path.stem}_summary.json"


def build_manifest(config_path: str | Path, models_path: str | Path, output_path: str | Path) -> pd.DataFrame:
    config = _load_yaml(config_path)
    models_cfg = _load_yaml(models_path)

    study = config["study"]
    story_ids = study["story_ids"]
    languages = [study["primary_language"], *study.get("secondary_languages", [])]
    personas = study["personas"]
    repetitions = list(range(1, int(study["repetitions"]) + 1))
    models = [m for m in models_cfg["models"] if m.get("default_include", True)]

    run_id = f"{study['paper_short_name']}_v1"

    rows = []
    row_counter = 0
    for model, language, story_id, persona, repetition in itertools.product(
        models, languages, story_ids, personas, repetitions
    ):
        rows.append(
            {
                "manifest_row": row_counter,
                "run_id": run_id,
                "model_id": model["model_id"],
                "provider": model["provider"],
                "language": language,
                "story_id": story_id,
                "persona_id": persona["persona_id"],
                "persona_label": persona["persona_label"],
                "temperature": float(persona["temperature"]),
                "repetition": int(repetition),
                "prompt_template": config.get("prompts", {}).get("user_template", "prompts/emotion_eval_user_template_multilingual_json.md"),
                "response_schema": config.get("prompts", {}).get("response_schema", "prompts/response_schema.json"),
                "should_compare_to_human_primary": language == study["primary_language"],
                "notes": "Review overlap against any simultaneously submitted paper before execution.",
            }
        )
        row_counter += 1

    manifest = pd.DataFrame(rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(output_path, index=False)

    summary_path = _manifest_summary_path(output_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": run_id,
        "n_models": int(len(models)),
        "n_languages": int(len(languages)),
        "n_stories": int(len(story_ids)),
        "n_personas": int(len(personas)),
        "n_repetitions": int(len(repetitions)),
        "n_rows": int(len(manifest)),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
