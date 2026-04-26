from __future__ import annotations

"""Build ICICIC external mini-comparison manifests from curated public items."""

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG = "configs/icicic/external_mini_comparison_v1.yaml"


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


def read_curated_items(path: Path, required_columns: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Curated external benchmark item file is missing: {path}. "
            "Create this file from public items with clear reuse notes before building the manifest."
        )
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = set(required_columns).difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Curated item CSV is missing columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(
            f"Curated external benchmark item file contains no rows: {path}. "
            "Add public items with clear reuse notes before building the manifest."
        )
    for row in rows:
        if not row.get("license_or_reuse_note", "").strip():
            raise ValueError(f"Missing reuse note for {row.get('benchmark_id')}:{row.get('item_id')}")
    return rows


def build_manifest(
    *,
    repo_root: Path,
    config_path: Path,
    output_path: Path | None,
) -> list[dict[str, Any]]:
    config = load_yaml(config_path)
    study = config["study"]
    api_controls = config["api_controls"]
    required_columns = list(config["required_curated_item_columns"])
    curated_path = repo_root / study["curated_items_csv"]
    items = read_curated_items(curated_path, required_columns)
    panel = load_yaml(repo_root / study["model_panel"])
    models = [model for model in panel.get("models", []) if model.get("default_include", True)]
    if output_path is None:
        output_path = repo_root / config["outputs"]["manifest"]
    run_id = output_path.parent.name
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    commit = git_commit(repo_root)

    hashes = {
        "config_sha256": file_sha256(config_path),
        "model_panel_sha256": file_sha256(repo_root / study["model_panel"]),
        "curated_items_sha256": file_sha256(curated_path),
        "response_schema_sha256": file_sha256(repo_root / study["response_schema"]),
    }

    rows: list[dict[str, Any]] = []
    manifest_row = 0
    for model in models:
        for item in items:
            rows.append(
                {
                    "manifest_row": manifest_row,
                    "run_id": run_id,
                    "design_id": study["design_id"],
                    "created_at_utc": created_at,
                    "model_id": model["model_id"],
                    "provider": model.get("provider", api_controls.get("provider", "openrouter")),
                    "route": model.get("route", "openrouter"),
                    "benchmark_id": item["benchmark_id"],
                    "item_id": item["item_id"],
                    "source_url": item["source_url"],
                    "license_or_reuse_note": item["license_or_reuse_note"],
                    "prompt_text": item["prompt_text"],
                    "answer_key": item["answer_key"],
                    "native_metric": item["native_metric"],
                    "temperature": float(api_controls["temperature"]),
                    "top_p": float(api_controls["top_p"]),
                    "max_completion_tokens": int(api_controls["max_completion_tokens"]),
                    "prompt_version": study["prompt_version"],
                    "response_schema": study["response_schema"],
                    "schema_version": study["schema_version"],
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
    (output_path.parent / "manifest_summary.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "design_id": study["design_id"],
                "n_rows": len(rows),
                "n_models": len(models),
                "n_items": len(items),
                "output_manifest": str(output_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_path = (repo_root / args.output).resolve() if args.output else None
    rows = build_manifest(
        repo_root=repo_root,
        config_path=(repo_root / args.config).resolve(),
        output_path=output_path,
    )
    print(f"Wrote {len(rows)} external mini-comparison rows.")


if __name__ == "__main__":
    main()
