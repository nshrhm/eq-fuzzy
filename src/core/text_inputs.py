from __future__ import annotations

"""Shared local text-body path resolution for EQ-Fuzzy workstreams."""

from pathlib import Path


SHARED_TEXTS_DIR = Path("data/catalogs/texts_private")


def resolve_text_file(texts_dir: Path, language: str, story_id: str) -> Path:
    """Resolve a text body file from the canonical shared text directory."""
    path = texts_dir / language / f"{story_id}.txt"
    if path.exists():
        return path

    raise FileNotFoundError(f"Missing text file: {path}")


def read_text_file(texts_dir: Path, language: str, story_id: str) -> str:
    return resolve_text_file(texts_dir, language, story_id).read_text(encoding="utf-8")
