from __future__ import annotations

"""Shared local text-body path resolution for EQ-Fuzzy workstreams."""

from pathlib import Path


SHARED_TEXTS_DIR = Path("data/catalogs/texts_private")
LEGACY_ICECCME_TEXTS_DIR = Path("data/iceccme2026/raw_private/texts")


def _replace_suffix(path: Path, old_suffix: Path, new_suffix: Path) -> Path | None:
    parts = path.parts
    old_parts = old_suffix.parts
    if len(parts) < len(old_parts) or tuple(parts[-len(old_parts) :]) != old_parts:
        return None
    return Path(*parts[: -len(old_parts)], *new_suffix.parts)


def resolve_text_file(texts_dir: Path, language: str, story_id: str) -> Path:
    """Resolve a text body file, preserving the old ICECCME-local path as an alias."""
    path = texts_dir / language / f"{story_id}.txt"
    if path.exists():
        return path

    shared_texts_dir = _replace_suffix(texts_dir, LEGACY_ICECCME_TEXTS_DIR, SHARED_TEXTS_DIR)
    if shared_texts_dir is not None:
        shared_path = shared_texts_dir / language / f"{story_id}.txt"
        if shared_path.exists():
            return shared_path

    raise FileNotFoundError(f"Missing text file: {path}")


def read_text_file(texts_dir: Path, language: str, story_id: str) -> str:
    return resolve_text_file(texts_dir, language, story_id).read_text(encoding="utf-8")
