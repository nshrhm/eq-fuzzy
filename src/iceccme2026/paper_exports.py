from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_CSV_DIR = REPO_ROOT / "results" / "csv"
RESULTS_TABLES_DIR = REPO_ROOT / "results" / "tables"
PAPER_FIG_DIR = REPO_ROOT / "paper" / "iceccme2026" / "fig"
PAPER_TABLES_DIR = REPO_ROOT / "paper" / "iceccme2026" / "tables"

MODEL_DISPLAY_NAMES = {
    "openai/gpt-5.4": "GPT-5.4",
    "anthropic/claude-sonnet-4.5": "Claude Sonnet 4.5",
    "google/gemini-2.5-pro": "Gemini 2.5 Pro",
    "x-ai/grok-4.20": "Grok 4.20",
    "deepseek/deepseek-v3.2": "DeepSeek V3.2",
    "qwen/qwen3.6-plus": "Qwen3.6 Plus",
}


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def display_model_name(model_id: str) -> str:
    return MODEL_DISPLAY_NAMES.get(str(model_id), str(model_id))


def require_column(df: pd.DataFrame, aliases: list[str], source: str) -> str:
    for alias in aliases:
        if alias in df.columns:
            return alias
    available = ", ".join(df.columns)
    expected = " or ".join(aliases)
    raise ValueError(f"{source} is missing required column {expected}. Available columns: {available}")


def require_columns(df: pd.DataFrame, schema: dict[str, list[str]], source: str) -> dict[str, str]:
    return {name: require_column(df, aliases, source) for name, aliases in schema.items()}


def numeric_series(df: pd.DataFrame, column: str, source: str) -> pd.Series:
    values = pd.to_numeric(df[column], errors="coerce")
    if values.isna().any():
        bad_count = int(values.isna().sum())
        raise ValueError(f"{source} column {column} contains {bad_count} non-numeric value(s)")
    return values


def latex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)
