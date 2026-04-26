from __future__ import annotations

"""Run SCIS 2026 Phase 1 temperature smoke-test requests through OpenRouter."""

import argparse
import ast
import copy
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, request

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.text_inputs import read_text_file as read_shared_text_file


DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MANIFEST = "runs/scis2026/phase1_temperature_smoke_v1/manifest.csv"
DEFAULT_OUTPUT = "runs/scis2026/phase1_temperature_smoke_v1/raw.jsonl"
EMOTIONS = ("interest", "surprise", "sadness", "anger")
FORBIDDEN_PROMPT_TERMS = ("temperature",)
JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)
PROVIDER_USER_ID_RE = re.compile(r"user_[A-Za-z0-9]{10,}")
LANGUAGE_NAMES = {"ja": "Japanese", "en": "English", "zh": "Chinese"}
EMOTION_DEFINITIONS = {
    "ja": {
        "interest": "テキストがどの程度おもしろい・愉快・知的に楽しいと感じるか",
        "surprise": "テキストにどの程度意外性・予想外の展開・発見があるか",
        "sadness": "テキストがどの程度悲しい・切ない・哀れを感じさせるか",
        "anger": "テキストがどの程度怒り・憤り・不快感を感じさせるか",
    },
    "en": {
        "interest": "How funny, entertaining, or intellectually enjoyable the text feels",
        "surprise": "How unexpected, novel, or revelatory the text feels",
        "sadness": "How sad, melancholic, or poignant the text feels",
        "anger": "How much anger, indignation, or displeasure the text evokes",
    },
    "zh": {
        "interest": "文本讓你感到多大程度的有趣、愉悅或智識上的享受",
        "surprise": "文本具有多大程度的意外性、出乎意料的發展或發現",
        "sadness": "文本讓你感到多大程度的悲傷、感傷或哀愁",
        "anger": "文本讓你感到多大程度的憤怒、不滿或不悅",
    },
}


class OpenRouterRequestError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str | None = None,
        response_json: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.response_json = response_json


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def redact_sensitive_provider_fields(value: Any) -> Any:
    if isinstance(value, str):
        return PROVIDER_USER_ID_RE.sub("user_[redacted]", value)
    if isinstance(value, list):
        return [redact_sensitive_provider_fields(item) for item in value]
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            if key == "user_id":
                redacted[key] = "user_[redacted]"
            else:
                redacted[key] = redact_sensitive_provider_fields(item)
        return redacted
    return value


def read_text_file(texts_dir: Path, language: str, story_id: str) -> str:
    return read_shared_text_file(texts_dir, language, story_id)


def lookup_text_meta(text_registry: dict[str, Any], story_id: str, language: str) -> dict[str, str]:
    for item in text_registry.get("texts", []):
        if item.get("story_id") == story_id:
            return {
                "title": item[f"title_{language}"],
                "author": item[f"author_{language}"],
            }
    raise KeyError(f"Unknown story_id in text registry: {story_id}")


def lookup_persona(persona_registry: dict[str, Any], persona_id: str, language: str) -> dict[str, str]:
    for item in persona_registry.get("personas", []):
        if item.get("persona_id") == persona_id:
            return {
                "persona_id": persona_id,
                "persona_name": item[f"name_{language}"],
                "persona_description": item[f"description_{language}"],
            }
    raise KeyError(f"Unknown persona_id in persona registry: {persona_id}")


def render_user_prompt(
    *,
    template: str,
    row: dict[str, str],
    repo_root: Path,
    text_registry: dict[str, Any],
    persona_registry: dict[str, Any],
) -> str:
    language = row["language"]
    story_id = row["story_id"]
    persona_id = row["persona_id"]
    text_meta = lookup_text_meta(text_registry, story_id, language)
    persona = lookup_persona(persona_registry, persona_id, language)
    text_body = read_text_file(repo_root / row["texts_dir"], language, story_id)
    definitions = EMOTION_DEFINITIONS[language]
    return template.format(
        persona_id=persona["persona_id"],
        persona_name=persona["persona_name"],
        persona_description=persona["persona_description"],
        language=language,
        language_name=LANGUAGE_NAMES[language],
        story_id=story_id,
        title=text_meta["title"],
        author=text_meta["author"],
        text_body=text_body,
        interest_definition=definitions["interest"],
        surprise_definition=definitions["surprise"],
        sadness_definition=definitions["sadness"],
        anger_definition=definitions["anger"],
    )


def assert_no_forbidden_prompt_terms(system_prompt: str, user_prompt: str) -> None:
    combined = f"{system_prompt}\n{user_prompt}".lower()
    found = [term for term in FORBIDDEN_PROMPT_TERMS if term in combined]
    if found:
        raise ValueError(f"Forbidden prompt term(s) found: {', '.join(found)}")


def strip_numeric_bounds_for_schema(obj: Any) -> Any:
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            if key in {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"}:
                continue
            cleaned[key] = strip_numeric_bounds_for_schema(value)
        return cleaned
    if isinstance(obj, list):
        return [strip_numeric_bounds_for_schema(value) for value in obj]
    return obj


def response_format_for_model(schema: dict[str, Any], model_id: str) -> dict[str, Any]:
    model_schema = copy.deepcopy(schema)
    if model_id.startswith("anthropic/"):
        model_schema = strip_numeric_bounds_for_schema(model_schema)
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "emotion_scores",
            "strict": True,
            "schema": model_schema,
        },
    }


def post_chat_completion(
    *,
    endpoint: str,
    api_key: str,
    referer: str | None,
    title: str | None,
    payload: dict[str, Any],
    timeout_sec: int,
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-OpenRouter-Title"] = title

    req = request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8")
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            parsed_body = json.loads(body)
        except json.JSONDecodeError:
            parsed_body = None
        raise OpenRouterRequestError(
            f"HTTP {e.code}: {body}",
            status_code=e.code,
            response_body=body,
            response_json=parsed_body,
        ) from e
    except error.URLError as e:
        raise OpenRouterRequestError(f"Network error: {e}") from e

    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise OpenRouterRequestError(f"Non-JSON response: {body[:500]}", response_body=body) from e


def extract_content(response_json: dict[str, Any]) -> str:
    choices = response_json.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("No choices in response.")
    message = choices[0].get("message", {})
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        pieces: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    pieces.append(text)
        if pieces:
            return "".join(pieces)
    raise RuntimeError("No textual message content found.")


def parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    candidates = [stripped]
    match = JSON_BLOCK_RE.search(stripped)
    if match:
        candidates.append(match.group(0))
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(candidate)
            except (SyntaxError, ValueError):
                continue
        if isinstance(parsed, dict):
            return parsed
    raise RuntimeError("Response content did not contain a JSON object.")


def validate_response_object(obj: dict[str, Any], row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for key in ("story_id", "persona_id", "language", "scores", "reasons"):
        if key not in obj:
            errors.append(f"missing:{key}")
    if obj.get("story_id") != row["story_id"]:
        errors.append("story_id_mismatch")
    if obj.get("persona_id") != row["persona_id"]:
        errors.append("persona_id_mismatch")
    if obj.get("language") != row["language"]:
        errors.append("language_mismatch")

    scores = obj.get("scores")
    if not isinstance(scores, dict):
        errors.append("scores_not_object")
    else:
        for emotion in EMOTIONS:
            value = scores.get(emotion)
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
                errors.append(f"invalid_score:{emotion}")

    reasons = obj.get("reasons")
    if not isinstance(reasons, dict):
        errors.append("reasons_not_object")
    else:
        for emotion in EMOTIONS:
            if not isinstance(reasons.get(emotion), str) or not reasons.get(emotion, "").strip():
                errors.append(f"invalid_reason:{emotion}")
    return errors


def selected_rows(
    manifest: list[dict[str, str]],
    *,
    model_ids: set[str],
    limit: int | None,
    offset: int,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen = 0
    for row in manifest:
        if model_ids and row["model_id"] not in model_ids:
            continue
        if seen < offset:
            seen += 1
            continue
        rows.append(row)
        if limit is not None and len(rows) >= limit:
            break
    return rows


def build_payload(
    *,
    row: dict[str, str],
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": row["model_id"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": float(row["temperature"]),
        "top_p": float(row["top_p"]),
        "max_completion_tokens": int(row["max_completion_tokens"]),
        "response_format": response_format_for_model(schema, row["model_id"]),
        "stream": False,
        "metadata": {
            "workstream": "scis2026",
            "phase": "phase1_temperature_smoke",
            "run_id": row["run_id"],
            "manifest_row": row["manifest_row"],
        },
    }
    reasoning = json.loads(row.get("reasoning_json") or '{"exclude": true}')
    if reasoning:
        payload["reasoning"] = reasoning
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-jsonl", default=DEFAULT_OUTPUT)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--referer", default=None)
    parser.add_argument("--title", default="SCIS2026-temperature-smoke")
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
        payload = build_payload(
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
            payload = build_payload(row=row, system_prompt=system_prompt, user_prompt=user_prompt, schema=schema)
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
                "catalog_id": row["catalog_id"],
                "model_id": row["model_id"],
                "provider": row["provider"],
                "route": row["route"],
                "model_group": row["model_group"],
                "candidate_role": row["candidate_role"],
                "language": row["language"],
                "story_id": row["story_id"],
                "persona_id": row["persona_id"],
                "temperature": float(row["temperature"]),
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
                "prompt_temperature_policy": row["temperature_policy"],
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
                f"[{idx}/{len(rows)}] {status} model={row['model_id']} temp={row['temperature']} row={row['manifest_row']}"
            )
            time.sleep(args.sleep_sec)


if __name__ == "__main__":
    main()
