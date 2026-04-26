from __future__ import annotations

"""Claim-neutral OpenRouter runner and prompt-rendering helpers."""

import ast
import copy
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib import error, request

import yaml

from src.core.text_inputs import read_text_file as read_shared_text_file


DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
EMOTIONS = ("interest", "surprise", "sadness", "anger")
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
            "name": "structured_response",
            "strict": True,
            "schema": model_schema,
        },
    }


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
            "workstream": row.get("workstream", ""),
            "run_id": row["run_id"],
            "manifest_row": row["manifest_row"],
        },
    }
    reasoning = json.loads(row.get("reasoning_json") or '{"exclude": true}')
    if reasoning:
        payload["reasoning"] = reasoning
    return payload


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
