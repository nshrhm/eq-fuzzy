from __future__ import annotations

"""Validate the SCIS 2026 Phase 2 factorial design lock."""

import argparse
import csv
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Phase 2 design validation failed: {message}")


def validate(repo_root: Path, config_path: Path) -> None:
    config = load_yaml(config_path)
    study = config["study"]
    prompt = config["prompt"]

    condition_path = repo_root / study["condition_table"]
    rows = load_csv(condition_path)
    personas = [str(p) for p in study["personas"]]
    temperatures = [float(t) for t in study["temperatures"]]

    require(len(rows) == len(personas) * len(temperatures), "condition table is not 4 x 4")
    require(len({row["condition_id"] for row in rows}) == len(rows), "condition IDs are not unique")

    observed_pairs = {(row["persona_id"], float(row["temperature"])) for row in rows}
    expected_pairs = {(persona_id, temp) for persona_id in personas for temp in temperatures}
    require(observed_pairs == expected_pairs, "condition table is not a full persona x temperature cross")

    for prompt_key in ("system_prompt", "user_template"):
        path = repo_root / prompt[prompt_key]
        text = path.read_text(encoding="utf-8").lower()
        for term in prompt.get("forbidden_prompt_terms", []):
            require(term.lower() not in text, f"forbidden prompt term {term!r} found in {path}")

    panel = load_yaml(repo_root / study["main_panel"])
    models = panel.get("models", [])
    require(len(models) == 6, "main panel must contain exactly six models")
    require(len({model["model_id"] for model in models}) == 6, "main panel model IDs are not unique")

    for stage_name, stage in config["run_stages"].items():
        expected = int(stage["models"]) * len(stage["story_ids"]) * int(stage["conditions"]) * int(stage["repetitions"])
        require(expected == int(stage["expected_trials"]), f"{stage_name} expected_trials mismatch")

    print(f"Validated SCIS Phase 2 design: {config_path}")
    print(f"Conditions: {len(rows)}")
    print(f"Main-panel models: {len(models)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    validate(repo_root, (repo_root / args.config).resolve())


if __name__ == "__main__":
    main()
