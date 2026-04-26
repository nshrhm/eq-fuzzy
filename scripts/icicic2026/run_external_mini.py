from __future__ import annotations

"""Run an ICICIC external mini-comparison manifest through OpenRouter."""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.openrouter_runner import (  # noqa: E402
    DEFAULT_ENDPOINT,
    OpenRouterRequestError,
    build_payload,
    extract_content,
    git_commit,
    load_json,
    load_manifest,
    parse_json_object,
    post_chat_completion,
    redact_sensitive_provider_fields,
    selected_rows,
    sha256_text,
)


DEFAULT_MANIFEST = "runs/icicic2026/icicic2026_external_mini_comparison_v1/manifest.csv"
DEFAULT_OUTPUT = "runs/icicic2026/icicic2026_external_mini_comparison_v1/raw.jsonl"
SYSTEM_PROMPT = (
    "You are answering a public emotional-intelligence benchmark item. "
    "Return valid JSON only and do not output markdown fences."
)


def validate_external_response(obj: dict[str, Any], row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for key in ("benchmark_id", "item_id", "answer", "confidence", "reason"):
        if key not in obj:
            errors.append(f"missing:{key}")
    if obj.get("benchmark_id") != row["benchmark_id"]:
        errors.append("benchmark_id_mismatch")
    if obj.get("item_id") != row["item_id"]:
        errors.append("item_id_mismatch")
    if not isinstance(obj.get("answer"), str) or not obj.get("answer", "").strip():
        errors.append("invalid_answer")
    confidence = obj.get("confidence")
    if not isinstance(confidence, int) or isinstance(confidence, bool) or not 0 <= confidence <= 100:
        errors.append("invalid_confidence")
    if not isinstance(obj.get("reason"), str) or not obj.get("reason", "").strip():
        errors.append("invalid_reason")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-jsonl", default=DEFAULT_OUTPUT)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--referer", default=None)
    parser.add_argument("--title", default="ICICIC2026-external-mini")
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
    schema = load_json(repo_root / first["response_schema"])
    if args.dry_run:
        payload = build_payload(
            row=first,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=first["prompt_text"],
            schema=schema,
        )
        payload["metadata"] = {
            "workstream": "icicic2026",
            "phase": "external_mini_comparison",
            "design_id": first["design_id"],
            "run_id": first["run_id"],
            "manifest_row": first["manifest_row"],
            "benchmark_id": first["benchmark_id"],
        }
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
            payload = build_payload(
                row=row,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=row["prompt_text"],
                schema=schema,
            )
            payload["metadata"] = {
                "workstream": "icicic2026",
                "phase": "external_mini_comparison",
                "design_id": row["design_id"],
                "run_id": row["run_id"],
                "manifest_row": row["manifest_row"],
                "benchmark_id": row["benchmark_id"],
            }
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
                validation_errors = validate_external_response(parsed, row)
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
                "design_id": row["design_id"],
                "model_id": row["model_id"],
                "provider": row["provider"],
                "route": row["route"],
                "benchmark_id": row["benchmark_id"],
                "item_id": row["item_id"],
                "source_url": row["source_url"],
                "license_or_reuse_note": row["license_or_reuse_note"],
                "answer_key": row["answer_key"],
                "native_metric": row["native_metric"],
                "temperature": float(row["temperature"]),
                "top_p": float(row["top_p"]),
                "ok": ok,
                "validation_errors": validation_errors,
                "elapsed_sec": round(time.time() - started, 3),
                "git_commit": commit,
                "prompt_version": row["prompt_version"],
                "schema_version": row["schema_version"],
                "rendered_user_prompt_sha256": sha256_text(row["prompt_text"]),
                "response_schema_sha256": row["response_schema_sha256"],
                "curated_items_sha256": row["curated_items_sha256"],
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
                f"benchmark={row['benchmark_id']} item={row['item_id']}"
            )
            time.sleep(args.sleep_sec)


if __name__ == "__main__":
    main()
