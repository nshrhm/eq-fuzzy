from __future__ import annotations

"""Run a SCIS 2026 factorial manifest through OpenRouter."""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from run_temperature_smoke import (
    DEFAULT_ENDPOINT,
    OpenRouterRequestError,
    assert_no_forbidden_prompt_terms,
    build_payload,
    extract_content,
    git_commit,
    load_json,
    load_manifest,
    load_yaml,
    parse_json_object,
    post_chat_completion,
    redact_sensitive_provider_fields,
    render_user_prompt,
    selected_rows,
    sha256_text,
    validate_response_object,
)


DEFAULT_MANIFEST = "runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/manifest.csv"
DEFAULT_OUTPUT = "runs/scis2026/scis2026_factorial_v1_sanity_manifest_v1/raw.jsonl"


def build_factorial_payload(
    *,
    row: dict[str, str],
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    payload = build_payload(row=row, system_prompt=system_prompt, user_prompt=user_prompt, schema=schema)
    payload["metadata"] = {
        "workstream": "scis2026",
        "phase": "factorial_run",
        "stage": row["stage"],
        "design_id": row["design_id"],
        "run_id": row["run_id"],
        "manifest_row": row["manifest_row"],
        "condition_id": row["condition_id"],
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-jsonl", default=DEFAULT_OUTPUT)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--referer", default=None)
    parser.add_argument("--title", default="SCIS2026-factorial-run")
    parser.add_argument("--model-id", action="append", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--sleep-sec", type=float, default=0.5)
    parser.add_argument("--timeout-sec", type=int, default=180)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    manifest_path = (repo_root / args.manifest).resolve()
    output_jsonl = (repo_root / args.output_jsonl).resolve()
    manifest = load_manifest(manifest_path)
    rows = selected_rows(
        manifest,
        model_ids=set(args.model_id or []),
        limit=args.limit,
        offset=args.offset,
    )
    if not rows:
        print("No manifest rows selected. Nothing to do.")
        return

    first = rows[0]
    system_prompt = (repo_root / first["system_prompt"]).read_text(encoding="utf-8")
    user_template = (repo_root / first["user_template"]).read_text(encoding="utf-8")
    schema = load_json(repo_root / first["response_schema"])
    text_registry = load_yaml(repo_root / first["text_registry"])
    persona_registry = load_yaml(repo_root / first["persona_registry"])

    preview_user_prompt = render_user_prompt(
        template=user_template,
        row=first,
        repo_root=repo_root,
        text_registry=text_registry,
        persona_registry=persona_registry,
    )
    assert_no_forbidden_prompt_terms(system_prompt, preview_user_prompt)

    if args.dry_run:
        payload = build_factorial_payload(
            row=first,
            system_prompt=system_prompt,
            user_prompt=preview_user_prompt,
            schema=schema,
        )
        print(f"Selected {len(rows)} manifest rows.")
        print("First request payload preview:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    api_key = os.environ.get(args.api_key_env, "")
    if not api_key:
        raise SystemExit(f"Environment variable {args.api_key_env} is not set.")

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    commit = git_commit(repo_root)
    with output_jsonl.open("a", encoding="utf-8") as out:
        for idx, row in enumerate(rows, start=1):
            user_prompt = render_user_prompt(
                template=user_template,
                row=row,
                repo_root=repo_root,
                text_registry=text_registry,
                persona_registry=persona_registry,
            )
            assert_no_forbidden_prompt_terms(system_prompt, user_prompt)
            payload = build_factorial_payload(
                row=row,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
            )
            started = time.time()
            response_json: dict[str, Any] | None = None
            parsed: dict[str, Any] | None = None
            validation_errors: list[str] = []
            error_message = None
            error_status_code = None
            error_body = None
            error_json = None
            ok = False
            try:
                response_json = post_chat_completion(
                    endpoint=args.endpoint,
                    api_key=api_key,
                    referer=args.referer,
                    title=args.title,
                    payload=payload,
                    timeout_sec=args.timeout_sec,
                )
                parsed = parse_json_object(extract_content(response_json))
                validation_errors = validate_response_object(parsed, row)
                ok = not validation_errors
            except Exception as exc:  # noqa: BLE001
                error_message = redact_sensitive_provider_fields(str(exc))
                if isinstance(exc, OpenRouterRequestError):
                    error_status_code = exc.status_code
                    error_body = redact_sensitive_provider_fields(exc.response_body)
                    error_json = redact_sensitive_provider_fields(exc.response_json)

            record = {
                "manifest_row": int(row["manifest_row"]),
                "run_id": row["run_id"],
                "stage": row["stage"],
                "design_id": row["design_id"],
                "model_id": row["model_id"],
                "provider": row["provider"],
                "route": row["route"],
                "panel_role": row["panel_role"],
                "language": row["language"],
                "story_id": row["story_id"],
                "condition_id": row["condition_id"],
                "persona_id": row["persona_id"],
                "persona_label": row["persona_label"],
                "temperature": float(row["temperature"]),
                "temperature_label": row["temperature_label"],
                "top_p": float(row["top_p"]),
                "repetition": int(row["repetition"]),
                "ok": ok,
                "validation_errors": validation_errors,
                "elapsed_sec": round(time.time() - started, 3),
                "git_commit": commit,
                "system_prompt_sha256": row["system_prompt_sha256"],
                "user_template_sha256": row["user_template_sha256"],
                "rendered_user_prompt_sha256": sha256_text(user_prompt),
                "response_schema_sha256": row["response_schema_sha256"],
                "condition_table_sha256": row["condition_table_sha256"],
                "main_panel_sha256": row["main_panel_sha256"],
                "factorial_config_sha256": row["factorial_config_sha256"],
                "temperature_policy": row["temperature_policy"],
                "persona_policy": row["persona_policy"],
                "request": payload,
                "parsed": parsed,
                "response": response_json,
                "error": error_message,
                "error_status_code": error_status_code,
                "error_body": error_body,
                "error_json": error_json,
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            status = "OK" if ok else "ERR"
            print(
                f"[{idx}/{len(rows)}] {status} row={row['manifest_row']} model={row['model_id']} "
                f"story={row['story_id']} condition={row['condition_id']} rep={row['repetition']}"
            )
            time.sleep(args.sleep_sec)


if __name__ == "__main__":
    main()
