from __future__ import annotations

"""Source-of-truth metadata for the ICECCME 2026 repository.

This module is derived from the user-supplied `definitions.py` file from the
`jaciii_iihmsp2025` experiment repository. It preserves the official three texts,
three languages, four emotions, and four original personas, and adds one
ICECCME-specific neutral persona for the primary human-grounded analysis.
"""

SUPPORTED_LANGS = ("ja", "en", "zh")

EMOTIONS = (
    ("Q1", "interest", "Interesting", "面白さ", "趣味性"),
    ("Q2", "surprise", "Surprise", "驚き", "驚訝感"),
    ("Q3", "sadness", "Sadness", "悲しみ", "悲傷感"),
    ("Q4", "anger", "Anger", "怒り", "憤怒感"),
)

PERSONAS = {
    "p0": {
        "persona_id": "p0",
        "source": "iceccme2026",
        "name_by_lang": {
            "ja": "中立的な読者",
            "en": "Neutral Reader",
            "zh": "中立讀者",
        },
        "description_by_lang": {
            "ja": "作品全体を落ち着いて読み、読後感情を過不足なく報告する中立的な読者",
            "en": "a neutral reader who calmly reads the whole work and reports post-reading emotions without exaggeration",
            "zh": "一位冷靜閱讀全文並不誇張地回報讀後情感的中立讀者",
        },
        "base_temperature": 0.4,
        "analysis_role": "primary",
    },
    "p1": {
        "persona_id": "p1",
        "source": "jaciii_iihmsp2025",
        "name_by_lang": {"ja": "大学1年生", "en": "College Freshman", "zh": "大一新生"},
        "description_by_lang": {
            "ja": "若く柔軟な発想を持つ大学1年生",
            "en": "a young, open-minded first-year college student",
            "zh": "一名年輕且思維靈活的大學一年級學生",
        },
        "base_temperature": 0.7,
        "analysis_role": "secondary",
    },
    "p2": {
        "persona_id": "p2",
        "source": "jaciii_iihmsp2025",
        "name_by_lang": {"ja": "文学研究者", "en": "Literary Scholar", "zh": "文學研究者"},
        "description_by_lang": {
            "ja": "論理的で分析的な文学研究者",
            "en": "a logical, analytically minded literary scholar",
            "zh": "一名邏輯縝密、善於分析的文學研究者",
        },
        "base_temperature": 0.4,
        "analysis_role": "secondary",
    },
    "p3": {
        "persona_id": "p3",
        "source": "jaciii_iihmsp2025",
        "name_by_lang": {"ja": "感情豊かな詩人", "en": "The Emotive Poet", "zh": "感性詩人"},
        "description_by_lang": {
            "ja": "繊細で感情豊かな詩人",
            "en": "a sensitive, deeply feeling poet",
            "zh": "一名細膩而情感豐沛的詩人",
        },
        "base_temperature": 0.9,
        "analysis_role": "secondary",
    },
    "p4": {
        "persona_id": "p4",
        "source": "jaciii_iihmsp2025",
        "name_by_lang": {"ja": "無感情なロボット", "en": "The Emotionless Robot", "zh": "無情感機器人"},
        "description_by_lang": {
            "ja": "機械的で論理的なロボット",
            "en": "a mechanical, logic-driven robot",
            "zh": "一台機械化且純粹以邏輯運作的機器人",
        },
        "base_temperature": 0.1,
        "analysis_role": "secondary",
    },
}

TEXTS = {
    "T1": {
        "source_text_id": "t1",
        "title_by_lang": {"ja": "懐中時計", "en": "The Pocket Watch", "zh": "懷中時計"},
        "author_by_lang": {"ja": "夢野久作", "en": "Kyusaku Yumeno", "zh": "夢野久作"},
    },
    "T2": {
        "source_text_id": "t2",
        "title_by_lang": {"ja": "お金とピストル", "en": "The Money and the Pistol", "zh": "錢與手槍"},
        "author_by_lang": {"ja": "夢野久作", "en": "Kyusaku Yumeno", "zh": "夢野久作"},
    },
    "T3": {
        "source_text_id": "t3",
        "title_by_lang": {"ja": "ぼろぼろな駝鳥", "en": "The Tattered Ostrich", "zh": "襤褸的鴕鳥"},
        "author_by_lang": {"ja": "高村光太郎", "en": "Kotaro Takamura", "zh": "高村光太郎"},
    },
}

SYSTEM_PROMPT_TEMPLATES = {
    "ja": 'あなたは「{persona_name}」です。{persona_description}として、日本の文学テキストに対する感情分析を行ってください。',
    "en": 'You are "{persona_name}". As {persona_description}, you will perform a sentiment analysis on a Japanese literary text.',
    "zh": '你是「{persona_name}」。作為{persona_description}，請你對以下日本文學文本進行情感分析。',
}

USER_PROMPT_EXPLANATIONS = {
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

LANGUAGE_NAMES = {"ja": "Japanese", "en": "English", "zh": "Chinese"}


def list_primary_personas() -> list[dict]:
    return [PERSONAS["p0"]]


def list_secondary_personas() -> list[dict]:
    return [PERSONAS[k] for k in ("p1", "p2", "p3", "p4")]


def list_texts() -> list[dict]:
    return [TEXTS[k] for k in ("T1", "T2", "T3")]
