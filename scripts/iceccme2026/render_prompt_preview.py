
#!/usr/bin/env python3
from __future__ import annotations

"""
render_prompt_preview.py

Primary 用の完全な日本語 prompt preview を生成する standalone script です。
- repo root を sys.path に追加してから import を試みます
- `src.iceccme2026.source_of_truth` / `external.jaciii_iihmsp2025.definitions` /
  `--definitions` で与えた definitions.py の順に読み込みを試みます
- p0 (中立的な読者) が未定義なら script 内で補います
- 日本語 primary template を既定とし、system/user prompt を分けて preview します
- response schema は prompt 本文に混ぜず、別セクションとして併記できます
"""

import argparse
import importlib
import importlib.util
import json
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any


SUPPORTED_LANGS = ("ja", "en", "zh")
LEGACY_ICECCME_TEXT_PARTS = ("data", "iceccme2026", "raw_private", "texts")
SHARED_TEXT_PARTS = ("data", "catalogs", "texts_private")


PRIMARY_PERSONA_P0 = {
    "persona_id": "p0",
    "name_by_lang": {
        "ja": "中立的な読者",
        "en": "Neutral Reader",
        "zh": "中立讀者",
    },
    "description_by_lang": {
        "ja": "作品全体を落ち着いて読み、読後感情を過不足なく報告する中立的な読者",
        "en": "a neutral reader who calmly reads the whole work and reports post-reading emotions without exaggeration or omission",
        "zh": "一位會冷靜閱讀作品整體，並不誇大也不遺漏地報告讀後情感的中立讀者",
    },
    "base_temperature": 0.4,
}


PRIMARY_SYSTEM_PROMPT_TEMPLATES = {
    "ja": """あなたは「{persona_name}」です。{persona_description}という立場を保ちつつ、日本語の文学作品を読んだ読者として、読後に感じた感情の強さを慎重に評価してください。
感情評価は主観的であってよいですが、必ず作品本文に根拠を置いて判断してください。
回答は必ず日本語で行い、指定されたJSONオブジェクト1個のみを返してください。
Markdown、箇条書き、前置き、後書き、コードフェンスは一切出力しないでください。""",
    "en": """You are "{persona_name}". Maintain the stance of {persona_description} and carefully evaluate the emotional intensity you feel after reading the literary work.
Your judgment may be subjective, but it must be grounded in the text itself.
Reply in English and return exactly one JSON object only.
Do not output markdown, bullet points, prefatory remarks, closing remarks, or code fences.""",
    "zh": """你是「{persona_name}」。請保持{persona_description}這一立場，作為閱讀該文學作品的讀者，審慎評估你在讀後感受到的情感強度。
你的判斷可以帶有主觀性，但必須以作品文本本身為依據。
請用中文回答，且只能回傳一個 JSON 物件。
不要輸出 Markdown、條列、前言、後記或程式碼區塊。""",
}

PRIMARY_USER_PROMPT_TEMPLATES = {
    "ja": """以下の日本語文学テキストを読み、読後に感じた4つの感情の強さを、それぞれ0から100の整数で評価してください。

【評価項目】
- 面白さ（interesting）
  左端: 全く面白くない
  右端: 極めて面白い

- 驚き（surprise）
  左端: 全く驚きがない
  右端: 極めて驚いている

- 悲しみ（sadness）
  左端: 全く悲しくない
  右端: 極めて悲しい

- 怒り（anger）
  左端: 全く怒っていない
  右端: 極めて怒っている

【評価ルール】
- 作品全体を読み終えたうえで、全体としての読後感情を評価してください。
- 各感情の値は必ず0〜100の整数にしてください。
- 0は「全く感じない」、50は「中程度に感じる」、100は「極めて強く感じる」の目安です。
- 各感情について、なぜその数値にしたのかを1〜2文の簡潔な日本語で説明してください。
- 理由は必ず作品本文に根拠を置いてください。
- 指定されたJSON schemaに厳密に従い、JSONオブジェクト1個だけを返してください。
- schemaにないキーは追加しないでください。
- 数値に % や 点 などの単位を付けないでください。

【作品情報】
作品タイトル: {text_title}
著者: {text_author}

【本文】
{text_content}
""",
    "en": """Read the following literary text and rate the intensity of four emotions you felt after reading it on integer scales from 0 to 100.

[Emotion Dimensions]
- Interesting (interest)
  left anchor: not interesting at all
  right anchor: extremely interesting

- Surprise (surprise)
  left anchor: no surprise at all
  right anchor: extremely surprised

- Sadness (sadness)
  left anchor: not sad at all
  right anchor: extremely sad

- Anger (anger)
  left anchor: not angry at all
  right anchor: extremely angry

[Scoring Rules]
- Evaluate the text as a whole after finishing it.
- Use integers between 0 and 100 only.
- 0 means not felt at all, 50 means moderately felt, 100 means extremely strongly felt.
- For each emotion, briefly explain in 1–2 sentences why you chose the score.
- Your reason must be grounded in the text.
- Return exactly one JSON object following the specified schema.
- Do not add keys outside the schema.
- Do not attach units such as "%" or "points" to numbers.

[Work Information]
Title: {text_title}
Author: {text_author}

[Text]
{text_content}
""",
    "zh": """請閱讀以下文學文本，並就你在讀後感受到的四種情感強度，各自以 0 到 100 的整數進行評分。

【評分維度】
- 趣味性（interest）
  左端：完全不有趣
  右端：極其有趣

- 驚訝（surprise）
  左端：完全沒有驚訝
  右端：極其驚訝

- 悲傷（sadness）
  左端：完全不悲傷
  右端：極其悲傷

- 憤怒（anger）
  左端：完全不憤怒
  右端：極其憤怒

【評分規則】
- 讀完整部作品後，對整體讀後感受進行評分。
- 每個情感分數都必須是 0 到 100 的整數。
- 0 表示完全沒有感受到，50 表示中等程度，100 表示極其強烈。
- 請為每個情感用 1–2 句簡潔中文說明理由。
- 理由必須以作品內容為依據。
- 嚴格按照指定的 JSON schema 回傳，且只能回傳一個 JSON 物件。
- 不要新增 schema 以外的鍵。
- 數值後不要附加 "%" 或 "分" 等單位。

【作品資訊】
作品標題: {text_title}
作者: {text_author}

【正文】
{text_content}
""",
}


DEFAULT_TEXT_METADATA = {
    "t1": {
        "text_id": "t1",
        "canonical_story_id": "T1",
        "title_by_lang": {"ja": "懐中時計", "en": "The Pocket Watch", "zh": "懷中時計"},
        "author_by_lang": {"ja": "夢野久作", "en": "Kyusaku Yumeno", "zh": "夢野久作"},
    },
    "t2": {
        "text_id": "t2",
        "canonical_story_id": "T2",
        "title_by_lang": {"ja": "お金とピストル", "en": "The Money and the Pistol", "zh": "錢與手槍"},
        "author_by_lang": {"ja": "夢野久作", "en": "Kyusaku Yumeno", "zh": "夢野久作"},
    },
    "t3": {
        "text_id": "t3",
        "canonical_story_id": "T3",
        "title_by_lang": {"ja": "ぼろぼろな駝鳥", "en": "The Tattered Ostrich", "zh": "襤褸的鴕鳥"},
        "author_by_lang": {"ja": "高村光太郎", "en": "Kotaro Takamura", "zh": "高村光太郎"},
    },
}


DEFAULT_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["interest", "surprise", "sadness", "anger"],
    "properties": {
        "interest": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "reason"],
            "properties": {
                "score": {"type": "integer", "minimum": 0, "maximum": 100},
                "reason": {"type": "string", "minLength": 1},
            },
        },
        "surprise": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "reason"],
            "properties": {
                "score": {"type": "integer", "minimum": 0, "maximum": 100},
                "reason": {"type": "string", "minLength": 1},
            },
        },
        "sadness": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "reason"],
            "properties": {
                "score": {"type": "integer", "minimum": 0, "maximum": 100},
                "reason": {"type": "string", "minLength": 1},
            },
        },
        "anger": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "reason"],
            "properties": {
                "score": {"type": "integer", "minimum": 0, "maximum": 100},
                "reason": {"type": "string", "minLength": 1},
            },
        },
    },
}


def add_repo_root_to_sys_path(repo_root: Path) -> None:
    resolved = str(repo_root.resolve())
    if resolved not in sys.path:
        sys.path.insert(0, resolved)


def normalize_story_id(story_id: str) -> str:
    sid = story_id.strip()
    if sid.lower() in {"t1", "t2", "t3"}:
        return sid.lower()
    raise ValueError(f"Unsupported story_id: {story_id!r}. Use T1/T2/T3 or t1/t2/t3.")


def build_temp_package_for_definitions(definitions_path: Path) -> str:
    tmpdir = Path(tempfile.mkdtemp(prefix="defs_pkg_"))
    pkgdir = tmpdir / "defs_pkg"
    pkgdir.mkdir(parents=True, exist_ok=True)
    (pkgdir / "__init__.py").write_text("", encoding="utf-8")
    (pkgdir / "models.py").write_text(
        textwrap.dedent(
            """
            from dataclasses import dataclass
            from typing import Dict

            @dataclass
            class PersonaDefinition:
                persona_id: str
                name_by_lang: Dict[str, str]
                description_by_lang: Dict[str, str]
                base_temperature: float

            @dataclass
            class TextDefinition:
                text_id: str
                title_by_lang: Dict[str, str]
                author_by_lang: Dict[str, str]
                content_by_lang: Dict[str, str]
                temperature_modifier: float
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    shutil.copy(definitions_path, pkgdir / "definitions.py")
    sys.path.insert(0, str(tmpdir))
    return "defs_pkg.definitions"


def try_import_source_of_truth(repo_root: Path) -> Any | None:
    add_repo_root_to_sys_path(repo_root)
    candidates = [
        "src.iceccme2026.source_of_truth",
        "external.jaciii_iihmsp2025.definitions",
        "definitions",
    ]
    for name in candidates:
        try:
            return importlib.import_module(name)
        except Exception:
            continue
    return None


def load_definitions_module(repo_root: Path, definitions_path: Path | None) -> Any | None:
    mod = try_import_source_of_truth(repo_root)
    if mod is not None:
        return mod
    if definitions_path is not None and definitions_path.exists():
        module_name = build_temp_package_for_definitions(definitions_path)
        try:
            return importlib.import_module(module_name)
        except Exception:
            return None
    return None


def persona_to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    return {
        "persona_id": getattr(obj, "persona_id"),
        "name_by_lang": getattr(obj, "name_by_lang"),
        "description_by_lang": getattr(obj, "description_by_lang"),
        "base_temperature": getattr(obj, "base_temperature", None),
    }


def text_to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    return {
        "text_id": getattr(obj, "text_id"),
        "title_by_lang": getattr(obj, "title_by_lang"),
        "author_by_lang": getattr(obj, "author_by_lang"),
        "content_by_lang": getattr(obj, "content_by_lang"),
        "temperature_modifier": getattr(obj, "temperature_modifier", 0.0),
    }


def build_resource_maps(module: Any | None) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    personas: dict[str, dict[str, Any]] = {}
    texts: dict[str, dict[str, Any]] = {}

    if module is not None:
        module_personas = getattr(module, "PERSONAS", {})
        for pid, pobj in module_personas.items():
            personas[pid] = persona_to_dict(pobj)

        module_texts = getattr(module, "TEXTS", {})
        for tid, tobj in module_texts.items():
            texts[tid.lower()] = text_to_dict(tobj)

    if "p0" not in personas:
        personas["p0"] = PRIMARY_PERSONA_P0

    for tid, meta in DEFAULT_TEXT_METADATA.items():
        if tid not in texts:
            texts[tid] = meta.copy()
        else:
            # canonical_story_id を補う
            texts[tid].setdefault("canonical_story_id", meta["canonical_story_id"])

    return personas, texts


def read_text_content(
    *,
    story_key: str,
    language: str,
    text_file: Path | None,
    texts_map: dict[str, dict[str, Any]],
) -> str:
    if text_file is not None:
        if text_file.exists():
            return text_file.read_text(encoding="utf-8").strip()
        parts = text_file.parts
        legacy_len = len(LEGACY_ICECCME_TEXT_PARTS)
        for index in range(0, len(parts) - legacy_len + 1):
            if tuple(parts[index : index + legacy_len]) == LEGACY_ICECCME_TEXT_PARTS:
                shared_file = Path(*parts[:index], *SHARED_TEXT_PARTS, *parts[index + legacy_len :])
                if shared_file.exists():
                    return shared_file.read_text(encoding="utf-8").strip()
                break
        return text_file.read_text(encoding="utf-8").strip()
    text_meta = texts_map[story_key]
    content_by_lang = text_meta.get("content_by_lang", {})
    if language in content_by_lang and content_by_lang[language]:
        return str(content_by_lang[language]).strip()
    raise FileNotFoundError(
        f"Text content for story {story_key} / language {language} was not found. "
        "Pass --text-file explicitly."
    )


def find_default_schema_path(repo_root: Path) -> Path | None:
    candidates = [
        repo_root / "prompts" / "shared" / "response_schema.json",
        repo_root / "prompts" / "response_schema.json",
        repo_root / "response_schema.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def load_schema(schema_path: Path | None) -> dict[str, Any]:
    if schema_path is None:
        return DEFAULT_RESPONSE_SCHEMA
    return json.loads(schema_path.read_text(encoding="utf-8"))


def render_preview(
    *,
    story_key: str,
    persona_id: str,
    language: str,
    texts_map: dict[str, dict[str, Any]],
    personas_map: dict[str, dict[str, Any]],
    text_content: str,
    schema: dict[str, Any] | None,
    include_schema: bool,
) -> str:
    if language not in SUPPORTED_LANGS:
        raise ValueError(f"Unsupported language: {language!r}. Choose from {SUPPORTED_LANGS}.")
    if persona_id not in personas_map:
        raise KeyError(f"Unknown persona_id: {persona_id!r}. Available: {sorted(personas_map.keys())}")

    text_meta = texts_map[story_key]
    persona = personas_map[persona_id]

    system_prompt = PRIMARY_SYSTEM_PROMPT_TEMPLATES[language].format(
        persona_name=persona["name_by_lang"][language],
        persona_description=persona["description_by_lang"][language],
    )

    user_prompt = PRIMARY_USER_PROMPT_TEMPLATES[language].format(
        text_title=text_meta["title_by_lang"][language],
        text_author=text_meta["author_by_lang"][language],
        text_content=text_content,
    )

    canonical_story_id = text_meta.get("canonical_story_id", story_key.upper())

    lines = [
        "# Prompt Preview",
        "",
        "[metadata]",
        f"story_id = {canonical_story_id}",
        f"persona_id = {persona_id}",
        f"language = {language}",
        f"temperature_for_api_only = {persona.get('base_temperature')}",
        "",
        "===SYSTEM_PROMPT===",
        system_prompt.strip(),
        "",
        "===USER_PROMPT===",
        user_prompt.strip(),
    ]

    if include_schema and schema is not None:
        lines.extend(
            [
                "",
                "===RESPONSE_SCHEMA===",
                json.dumps(schema, ensure_ascii=False, indent=2),
            ]
        )

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a primary human-alignment prompt preview (Japanese-first)."
    )
    parser.add_argument("--story-id", required=True, help="T1/T2/T3 or t1/t2/t3")
    parser.add_argument("--persona-id", required=True, help="e.g., p0, p1, p2, p3, p4")
    parser.add_argument("--language", default="ja", choices=SUPPORTED_LANGS)
    parser.add_argument("--text-file", type=Path, default=None, help="Optional plain-text file to override text content")
    parser.add_argument("--definitions", type=Path, default=None, help="Optional path to definitions.py")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--schema-file", type=Path, default=None, help="Optional response_schema.json")
    parser.add_argument("--show-schema", action="store_true", help="Include response schema in the preview output")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    story_key = normalize_story_id(args.story_id)
    repo_root = args.repo_root.resolve()
    add_repo_root_to_sys_path(repo_root)

    module = load_definitions_module(repo_root, args.definitions)
    personas_map, texts_map = build_resource_maps(module)

    text_content = read_text_content(
        story_key=story_key,
        language=args.language,
        text_file=args.text_file,
        texts_map=texts_map,
    )

    schema_path = args.schema_file
    if schema_path is None and args.show_schema:
        schema_path = find_default_schema_path(repo_root)
    schema = load_schema(schema_path) if args.show_schema else None

    preview = render_preview(
        story_key=story_key,
        persona_id=args.persona_id,
        language=args.language,
        texts_map=texts_map,
        personas_map=personas_map,
        text_content=text_content,
        schema=schema,
        include_schema=args.show_schema,
    )

    if args.output is not None:
        args.output.write_text(preview, encoding="utf-8")
    else:
        print(preview, end="")


if __name__ == "__main__":
    main()
