from __future__ import annotations

import csv
import ast
import json
import re
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

EMOTIONS = ["interest", "surprise", "sadness", "anger"]
REQUIRED_LONG_COLUMNS = [
    "model_id",
    "provider",
    "language",
    "story_id",
    "persona_id",
    "repetition",
    "emotion",
    "score",
]
META_FIELDS = ["model_id", "provider", "language", "story_id", "persona_id", "repetition"]
ALT_META_KEYS: dict[str, list[str]] = {
    "model_id": ["model_id", "model", "model_name", "openrouter_model", "model_slug"],
    "provider": ["provider", "vendor", "service"],
    "language": ["language", "lang"],
    "story_id": ["story_id", "text_id", "story", "storyId", "stimulus_id", "text"],
    "persona_id": ["persona_id", "persona", "role_id", "role", "personaId"],
    "repetition": ["repetition", "repeat", "trial", "trial_id", "iteration", "seed_index"],
}

STRING_FIELDS_TO_PARSE = [
    "response_text",
    "raw_response",
    "assistant_text",
    "assistant_content",
    "content",
    "text",
    "message",
    "output_text",
]

Q_TO_EMOTION = {"Q1": "interest", "Q2": "surprise", "Q3": "sadness", "Q4": "anger"}
TRIPLE_PIPE_RE = re.compile(r"Q([1-4])[^|\n]*\|\|\|\s*([0-9]{1,3}(?:\.[0-9]+)?)", re.IGNORECASE)
LINE_Q_SCORE_RE = re.compile(
    r"(?im)^\s*(Q[1-4])\b[^\n0-9]{0,80}([0-9]{1,3}(?:\.[0-9]+)?)\b"
)
JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


class ModelScoreNormalizationError(ValueError):
    pass



def _coerce_score(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    if not (0 <= x <= 100):
        return None
    return x



def _maybe_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None



def _search_nested(obj: Any, target_keys: Iterable[str]) -> Any:
    if isinstance(obj, dict):
        for key in target_keys:
            if key in obj:
                return obj[key]
        for value in obj.values():
            found = _search_nested(value, target_keys)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _search_nested(value, target_keys)
            if found is not None:
                return found
    return None



def _find_scores_dict(obj: Any) -> dict[str, float] | None:
    if isinstance(obj, dict):
        if all(k in obj for k in EMOTIONS):
            out: dict[str, float] = {}
            for k in EMOTIONS:
                value = obj.get(k)
                if isinstance(value, dict) and "score" in value:
                    value = value.get("score")
                score = _coerce_score(value)
                if score is None:
                    break
                out[k] = score
            else:
                return out
        for value in obj.values():
            found = _find_scores_dict(value)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _find_scores_dict(value)
            if found is not None:
                return found
    return None



def _extract_json_block(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    candidates = [text]
    m = JSON_BLOCK_RE.search(text)
    if m:
        candidates.append(m.group(0))
    for cand in candidates:
        try:
            parsed = json.loads(cand)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(cand)
            except (SyntaxError, ValueError):
                continue
        if isinstance(parsed, dict):
            return parsed
    return None



def _parse_textual_scores(text: str) -> dict[str, float] | None:
    matches = TRIPLE_PIPE_RE.findall(text) or LINE_Q_SCORE_RE.findall(text)
    if not matches:
        return None
    out: dict[str, float] = {}
    for qnum, value in matches:
        qid = qnum.upper()
        if not qid.startswith("Q"):
            qid = f"Q{qid}"
        emotion = Q_TO_EMOTION.get(qid)
        score = _coerce_score(value)
        if emotion and score is not None:
            out[emotion] = score
    return out if len(out) == 4 else None



def _extract_scores_from_record(record: dict[str, Any]) -> dict[str, float] | None:
    scores = _find_scores_dict(record)
    if scores is not None:
        return scores

    for field in STRING_FIELDS_TO_PARSE:
        raw = _search_nested(record, [field])
        if isinstance(raw, str):
            parsed_json = _extract_json_block(raw)
            if parsed_json is not None:
                scores = _find_scores_dict(parsed_json)
                if scores is not None:
                    return scores
            textual_scores = _parse_textual_scores(raw)
            if textual_scores is not None:
                return textual_scores

    # OpenRouter-ish fallback
    choices = record.get("choices")
    if isinstance(choices, list) and choices:
        choice0 = choices[0]
        if isinstance(choice0, dict):
            content = _search_nested(choice0, ["content"])
            if isinstance(content, str):
                parsed_json = _extract_json_block(content)
                if parsed_json is not None:
                    scores = _find_scores_dict(parsed_json)
                    if scores is not None:
                        return scores
                textual_scores = _parse_textual_scores(content)
                if textual_scores is not None:
                    return textual_scores
    return None



def _extract_meta_from_record(record: dict[str, Any]) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    for target, keys in ALT_META_KEYS.items():
        value = _search_nested(record, keys)
        if value is not None:
            meta[target] = value
    if "provider" not in meta:
        meta["provider"] = "openrouter"
    if "repetition" in meta:
        rep = _maybe_int(meta["repetition"])
        if rep is not None:
            meta["repetition"] = rep
    return meta



def _read_json_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    text = text.strip()
    if not text:
        return []
    if path.suffix.lower() == ".jsonl":
        out = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if isinstance(obj, dict):
                out.append(obj)
            else:
                raise ModelScoreNormalizationError("Each JSONL line must be an object.")
        return out
    parsed = json.loads(text)
    if isinstance(parsed, list):
        if not all(isinstance(x, dict) for x in parsed):
            raise ModelScoreNormalizationError("JSON array input must contain objects only.")
        return parsed
    if isinstance(parsed, dict):
        # common wrappers
        for key in ["records", "items", "data", "responses"]:
            value = parsed.get(key)
            if isinstance(value, list) and all(isinstance(x, dict) for x in value):
                return value
        return [parsed]
    raise ModelScoreNormalizationError("Unsupported JSON shape.")



def _normalize_from_long_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    missing = set(REQUIRED_LONG_COLUMNS).difference(out.columns)
    if missing:
        raise ModelScoreNormalizationError(f"Long CSV is missing columns: {sorted(missing)}")
    out = out[REQUIRED_LONG_COLUMNS].copy()
    out["score"] = out["score"].apply(_coerce_score)
    out = out.dropna(subset=["score"])
    out["repetition"] = out["repetition"].apply(_maybe_int)
    return out



def _normalize_from_wide_csv(df: pd.DataFrame) -> pd.DataFrame:
    needed_meta = ["model_id", "provider", "language", "story_id", "persona_id", "repetition"]
    missing_meta = set(needed_meta).difference(df.columns)
    if missing_meta:
        raise ModelScoreNormalizationError(f"Wide CSV is missing metadata columns: {sorted(missing_meta)}")
    if not all(e in df.columns for e in EMOTIONS):
        missing_emotions = [e for e in EMOTIONS if e not in df.columns]
        raise ModelScoreNormalizationError(f"Wide CSV is missing emotion columns: {missing_emotions}")
    out = df.melt(id_vars=needed_meta, value_vars=EMOTIONS, var_name="emotion", value_name="score")
    out["score"] = out["score"].apply(_coerce_score)
    out = out.dropna(subset=["score"])
    out = out[REQUIRED_LONG_COLUMNS].copy()
    out["repetition"] = out["repetition"].apply(_maybe_int)
    return out



def _normalize_from_records(records: list[dict[str, Any]], manifest: pd.DataFrame | None = None, join_on_order: bool = False) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    manifest_records = manifest.to_dict(orient="records") if manifest is not None else None

    for idx, record in enumerate(records):
        meta = _extract_meta_from_record(record)
        if manifest_records is not None:
            manifest_row = manifest_records[idx] if join_on_order and idx < len(manifest_records) else None
            if manifest_row is not None:
                for field in META_FIELDS:
                    if field not in meta or meta[field] in (None, ""):
                        meta[field] = manifest_row.get(field)

        scores = _extract_scores_from_record(record)
        if scores is None:
            continue

        row_meta = {field: meta.get(field) for field in META_FIELDS}
        if any(v in (None, "") for v in row_meta.values()):
            missing_fields = [k for k, v in row_meta.items() if v in (None, "")]
            raise ModelScoreNormalizationError(
                f"Record {idx} is missing metadata fields {missing_fields}. Provide them in the raw records or use --manifest --join-on-order."
            )
        row_meta["repetition"] = _maybe_int(row_meta["repetition"])
        if row_meta["repetition"] is None:
            raise ModelScoreNormalizationError(f"Record {idx} has non-numeric repetition: {meta.get('repetition')}")

        for emotion, score in scores.items():
            rows.append({**row_meta, "emotion": emotion, "score": score})

    if not rows:
        raise ModelScoreNormalizationError(
            "No parsable model scores were found. Supported inputs are: long CSV, wide CSV, JSON/JSONL with a scores object, or raw text containing the Q1|||... format."
        )
    return pd.DataFrame(rows, columns=REQUIRED_LONG_COLUMNS)



def normalize_model_scores(
    input_path: str | Path,
    output_path: str | Path,
    manifest_path: str | Path | None = None,
    join_on_order: bool = False,
) -> pd.DataFrame:
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    manifest_df = None
    if manifest_path is not None:
        manifest_df = pd.read_csv(manifest_path)

    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(input_path)
        if set(REQUIRED_LONG_COLUMNS).issubset(df.columns):
            out = _normalize_from_long_csv(df)
        else:
            out = _normalize_from_wide_csv(df)
    elif suffix in {".json", ".jsonl"}:
        records = _read_json_records(input_path)
        out = _normalize_from_records(records, manifest=manifest_df, join_on_order=join_on_order)
    else:
        raise ModelScoreNormalizationError(
            f"Unsupported input type: {suffix}. Use .csv, .json, or .jsonl."
        )

    out["emotion"] = out["emotion"].str.lower()
    bad_emotions = sorted(set(out["emotion"]) - set(EMOTIONS))
    if bad_emotions:
        raise ModelScoreNormalizationError(f"Unexpected emotion labels: {bad_emotions}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL)
    return out
