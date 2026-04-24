from __future__ import annotations

"""Run an OpenRouter-backed experiment manifest for ICECCME 2026.

This module reads a manifest CSV produced by `python main.py build-manifest`, loads the
validated multilingual text files from `data/iceccme2026/raw_private/texts/<lang>/<story>.txt`,
constructs the system/user prompts, calls OpenRouter's chat completions endpoint with
JSON-schema structured outputs, and writes one JSONL line per completed request.

The repository-root `run_openrouter_manifest.py` remains a compatibility wrapper.
Only standard-library modules are used.
"""

import argparse
import ast
import copy
import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_SYSTEM_PROMPT = (
    "You are a careful evaluator of literary affect.\n"
    "Respect the provided persona framing, but do not add any role-play content beyond what is needed for the judgment.\n"
    "Return valid JSON only.\n"
    "Do not output markdown fences."
)
EMOTIONS = ("interest", "surprise", "sadness", "anger")
Q_TO_EMOTION = {"Q1": "interest", "Q2": "surprise", "Q3": "sadness", "Q4": "anger"}
TRIPLE_PIPE_RE = re.compile(r"Q([1-4])[^|\n]*\|\|\|\s*([0-9]{1,3}(?:\.[0-9]+)?)", re.IGNORECASE)
LINE_Q_SCORE_RE = re.compile(
    r"(?im)^\s*(Q[1-4])\b[^\n0-9]{0,80}([0-9]{1,3}(?:\.[0-9]+)?)\b"
)
JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)
DISABLED_REASONING = {"effort": "none", "exclude": True}
GEMINI_REASONING = {"max_tokens": 256, "exclude": True}


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


def ensure_repo_on_path(repo_root: Path) -> None:
    repo_root = repo_root.resolve()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_completed_manifest_rows(output_jsonl: Path) -> set[int]:
    done: set[int] = set()
    if not output_jsonl.exists():
        return done
    with output_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            row = obj.get("manifest_row")
            if isinstance(row, int) and obj.get("ok") is True:
                done.add(row)
    return done


def load_failed_manifest_rows(output_jsonl: Path) -> set[int]:
    failed: set[int] = set()
    ok: set[int] = set()
    if not output_jsonl.exists():
        return failed
    with output_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            row = obj.get("manifest_row")
            if not isinstance(row, int):
                continue
            if obj.get("ok") is True:
                ok.add(row)
            else:
                failed.add(row)
    return failed - ok


def export_failed_manifest(manifest: list[dict[str, str]], failed_rows: set[int], output_csv: Path) -> int:
    selected = [row for row in manifest if int(row["manifest_row"]) in failed_rows]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if not manifest:
        raise ValueError("Cannot export failed manifest from an empty manifest.")
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(selected)
    return len(selected)


def build_user_prompt(
    *,
    story_id: str,
    language: str,
    persona_id: str,
    text_body: str,
    source_of_truth: Any,
) -> str:
    text_meta = source_of_truth.TEXTS[story_id]
    persona_meta = source_of_truth.PERSONAS[persona_id]
    explanations = source_of_truth.USER_PROMPT_EXPLANATIONS[language]
    language_name = source_of_truth.LANGUAGE_NAMES[language]

    return f"""Task:
Read the literary text below and rate four reader-side emotions on a 0 to 100 integer scale.

Persona:
- persona_id: {persona_id}
- persona_name: {persona_meta['name_by_lang'][language]}
- persona_description: {persona_meta['description_by_lang'][language]}
- temperature: {persona_meta['base_temperature']}

Output language:
{language_name}

Dimensions and definitions:
- interest: {explanations['interest']}
- surprise: {explanations['surprise']}
- sadness: {explanations['sadness']}
- anger: {explanations['anger']}

Scoring rules:
- use integers only
- 0 means the emotion is not felt at all
- 50 means moderately felt
- 100 means extremely strongly felt
- rate the text as a whole after reading it
- keep each reason brief and grounded in the text

Return exactly one JSON object matching the schema.

Text identifier: {story_id}
Title: {text_meta['title_by_lang'][language]}
Author: {text_meta['author_by_lang'][language]}
Language of this prompt: {language}

Text:
{text_body}
"""


def read_text_file(texts_dir: Path, language: str, story_id: str) -> str:
    path = texts_dir / language / f"{story_id}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Missing text file: {path}")
    return path.read_text(encoding="utf-8")


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
        raise RuntimeError(f"No choices in response: {json.dumps(response_json)[:1000]}")
    msg = choices[0].get("message", {})
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Handle segmented content shape.
        pieces: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    pieces.append(text)
        if pieces:
            return "".join(pieces)
    raise RuntimeError(f"No textual message content found: {json.dumps(response_json)[:1000]}")


def _coerce_score(value: Any) -> int | None:
    if isinstance(value, dict) and "score" in value:
        value = value.get("score")
    try:
        score = int(float(value))
    except (TypeError, ValueError):
        return None
    if 0 <= score <= 100:
        return score
    return None


def _scores_from_object(obj: Any) -> dict[str, int] | None:
    if isinstance(obj, dict):
        if all(emotion in obj for emotion in EMOTIONS):
            scores: dict[str, int] = {}
            for emotion in EMOTIONS:
                score = _coerce_score(obj.get(emotion))
                if score is None:
                    break
                scores[emotion] = score
            else:
                return scores
        for value in obj.values():
            found = _scores_from_object(value)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _scores_from_object(value)
            if found is not None:
                return found
    return None


def _parse_json_like(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    candidates = [text]
    match = JSON_BLOCK_RE.search(text)
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
    return None


def _parse_legacy_q_scores(text: str) -> dict[str, int] | None:
    matches = TRIPLE_PIPE_RE.findall(text) or LINE_Q_SCORE_RE.findall(text)
    if not matches:
        return None
    scores: dict[str, int] = {}
    for qid, value in matches:
        emotion = Q_TO_EMOTION.get(qid.upper())
        score = _coerce_score(value)
        if emotion and score is not None:
            scores[emotion] = score
    return scores if len(scores) == 4 else None


def parse_assistant_content(content: str) -> tuple[dict[str, Any] | None, str | None]:
    parsed_json = _parse_json_like(content)
    if parsed_json is not None:
        if _scores_from_object(parsed_json) is not None:
            return parsed_json, "json"
    q_scores = _parse_legacy_q_scores(content)
    if q_scores is not None:
        return {"scores": q_scores, "raw_legacy_text": content}, "legacy_q_text"
    return None, None


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


def reasoning_for_model(model_id: str) -> dict[str, Any]:
    if model_id.startswith("google/gemini-"):
        return dict(GEMINI_REASONING)
    if model_id.startswith(("openai/gpt-5", "x-ai/grok-")):
        return dict(DISABLED_REASONING)
    return {"exclude": True}


def _is_mandatory_reasoning_error(exc: OpenRouterRequestError) -> bool:
    body = exc.response_body or str(exc)
    return exc.status_code == 400 and "Reasoning is mandatory" in body


def _uses_disabled_reasoning(payload: dict[str, Any]) -> bool:
    reasoning = payload.get("reasoning")
    return isinstance(reasoning, dict) and reasoning.get("effort") == "none"


def _attempt_snapshot(
    *,
    attempt: int,
    status: str,
    payload: dict[str, Any],
    error_message: str | None = None,
    error_status_code: int | None = None,
    error_body: str | None = None,
) -> dict[str, Any]:
    return {
        "attempt": attempt,
        "status": status,
        "reasoning": copy.deepcopy(payload.get("reasoning")),
        "error": error_message,
        "error_status_code": error_status_code,
        "error_body": error_body,
    }


def fetch_and_parse_completion(
    *,
    endpoint: str,
    api_key: str,
    referer: str | None,
    title: str | None,
    payload: dict[str, Any],
    timeout_sec: int,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    response_json = post_chat_completion(
        endpoint=endpoint,
        api_key=api_key,
        referer=referer,
        title=title,
        payload=payload,
        timeout_sec=timeout_sec,
    )
    content = extract_content(response_json)
    normalized_content, parse_method = parse_assistant_content(content)
    if normalized_content is None or parse_method is None:
        raise RuntimeError("Response content did not contain parsable emotion scores.")
    return response_json, normalized_content, parse_method


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ICECCME primary manifest on OpenRouter")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", default="data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv")
    parser.add_argument("--texts-dir", default="data/iceccme2026/raw_private/texts")
    parser.add_argument("--schema", default="prompts/shared/response_schema.json")
    parser.add_argument("--output-jsonl", default="data/iceccme2026/raw_private/openrouter_primary_raw.jsonl")
    parser.add_argument("--limit", type=int, default=None, help="Run only the first N unfinished manifest rows")
    parser.add_argument("--offset", type=int, default=0, help="Skip the first N manifest rows")
    parser.add_argument(
        "--model-id",
        action="append",
        default=None,
        help="Restrict selection to this model_id. Repeat the option for multiple models.",
    )
    parser.add_argument("--sleep-sec", type=float, default=0.5)
    parser.add_argument("--timeout-sec", type=int, default=180)
    parser.add_argument("--max-completion-tokens", type=int, default=700)
    parser.add_argument("--temperature-override", type=float, default=None)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--referer", default=None)
    parser.add_argument("--title", default="ICECCME2026-human-grounded-run")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--export-failed-manifest",
        default=None,
        help="Write a manifest CSV containing only rows with failed raw records and no ok==true record, then exit.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    ensure_repo_on_path(repo_root)

    from src.iceccme2026 import source_of_truth

    manifest_path = (repo_root / args.manifest).resolve()
    texts_dir = (repo_root / args.texts_dir).resolve()
    schema_path = (repo_root / args.schema).resolve()
    output_jsonl = (repo_root / args.output_jsonl).resolve()

    manifest = load_manifest(manifest_path)
    schema = load_json(schema_path)

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    if args.export_failed_manifest:
        failed_rows = load_failed_manifest_rows(output_jsonl)
        n_exported = export_failed_manifest(manifest, failed_rows, (repo_root / args.export_failed_manifest).resolve())
        print(f"Exported {n_exported} failed manifest rows to {args.export_failed_manifest}")
        return

    done = load_completed_manifest_rows(output_jsonl) if args.resume else set()

    api_key = os.environ.get(args.api_key_env, "")
    if not args.dry_run and not api_key:
        raise SystemExit(
            f"Environment variable {args.api_key_env} is not set. Export your OpenRouter API key first."
        )

    selected_rows: list[dict[str, str]] = []
    unfinished_seen = 0
    model_filter = set(args.model_id or [])
    for row in manifest:
        manifest_row = int(row["manifest_row"])
        if model_filter and row["model_id"] not in model_filter:
            continue
        if manifest_row in done:
            continue
        if unfinished_seen < args.offset:
            unfinished_seen += 1
            continue
        selected_rows.append(row)
        if args.limit is not None and len(selected_rows) >= args.limit:
            break

    if not selected_rows:
        print("No manifest rows selected. Nothing to do.")
        return

    print(f"Selected {len(selected_rows)} manifest rows from {manifest_path}")
    if args.dry_run:
        preview = selected_rows[0]
        print("First selected row:")
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return

    with output_jsonl.open("a", encoding="utf-8") as out:
        for idx, row in enumerate(selected_rows, start=1):
            manifest_row = int(row["manifest_row"])
            language = row["language"]
            story_id = row["story_id"]
            persona_id = row["persona_id"]
            model_id = row["model_id"]
            provider = row.get("provider", "openrouter")
            repetition = int(row["repetition"])
            temp = args.temperature_override
            if temp is None:
                temp = float(row["temperature"])

            text_body = read_text_file(texts_dir, language, story_id)
            user_prompt = build_user_prompt(
                story_id=story_id,
                language=language,
                persona_id=persona_id,
                text_body=text_body,
                source_of_truth=source_of_truth,
            )

            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temp,
                "max_completion_tokens": args.max_completion_tokens,
                "response_format": response_format_for_model(schema, model_id),
                "stream": False,
                "reasoning": reasoning_for_model(model_id),
                "metadata": {
                    "run_id": row.get("run_id", ""),
                    "manifest_row": str(manifest_row),
                    "paper": "iceccme2026",
                },
            }

            started = time.time()
            ok = True
            error_message = None
            error_status_code = None
            error_body = None
            error_json = None
            response_json: dict[str, Any] | None = None
            normalized_content: dict[str, Any] | None = None
            parse_method: str | None = None
            retry_attempts: list[dict[str, Any]] = []
            try:
                response_json, normalized_content, parse_method = fetch_and_parse_completion(
                    endpoint=args.endpoint,
                    api_key=api_key,
                    referer=args.referer,
                    title=args.title,
                    payload=payload,
                    timeout_sec=args.timeout_sec,
                )
            except Exception as e:  # noqa: BLE001
                ok = False
                error_message = str(e)
                if isinstance(e, OpenRouterRequestError):
                    error_status_code = e.status_code
                    error_body = e.response_body
                    error_json = e.response_json
                    if _is_mandatory_reasoning_error(e) and _uses_disabled_reasoning(payload):
                        retry_attempts.append(
                            _attempt_snapshot(
                                attempt=1,
                                status="err",
                                payload=payload,
                                error_message=error_message,
                                error_status_code=error_status_code,
                                error_body=error_body,
                            )
                        )
                        payload["reasoning"] = dict(GEMINI_REASONING)
                        try:
                            response_json, normalized_content, parse_method = fetch_and_parse_completion(
                                endpoint=args.endpoint,
                                api_key=api_key,
                                referer=args.referer,
                                title=args.title,
                                payload=payload,
                                timeout_sec=args.timeout_sec,
                            )
                            retry_attempts.append(
                                _attempt_snapshot(attempt=2, status="ok", payload=payload)
                            )
                            ok = True
                            error_message = None
                            error_status_code = None
                            error_body = None
                            error_json = None
                        except Exception as retry_error:  # noqa: BLE001
                            ok = False
                            error_message = str(retry_error)
                            if isinstance(retry_error, OpenRouterRequestError):
                                error_status_code = retry_error.status_code
                                error_body = retry_error.response_body
                                error_json = retry_error.response_json
                            retry_attempts.append(
                                _attempt_snapshot(
                                    attempt=2,
                                    status="err",
                                    payload=payload,
                                    error_message=error_message,
                                    error_status_code=error_status_code,
                                    error_body=error_body,
                                )
                            )

            record = {
                "manifest_row": manifest_row,
                "run_id": row.get("run_id", ""),
                "model_id": model_id,
                "provider": provider,
                "language": language,
                "story_id": story_id,
                "persona_id": persona_id,
                "repetition": repetition,
                "temperature": temp,
                "ok": ok,
                "elapsed_sec": round(time.time() - started, 3),
                "request": payload,
                "parsed": normalized_content,
                "parse_method": parse_method,
                "response": response_json,
                "error": error_message,
                "error_status_code": error_status_code,
                "error_body": error_body,
                "error_json": error_json,
                "retry_attempts": retry_attempts,
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()

            status = "OK" if ok else "ERR"
            print(
                f"[{idx}/{len(selected_rows)}] {status} row={manifest_row} model={model_id} lang={language} story={story_id} rep={repetition}"
            )
            time.sleep(args.sleep_sec)


if __name__ == "__main__":
    main()
