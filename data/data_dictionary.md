# Data Dictionary

ICECCME canonical data files live under `data/iceccme2026/`.
Use canonical `data/iceccme2026/...` paths directly. Root-level data compatibility symlinks have been removed.

## `data/iceccme2026/derived_public/human_vas_long.csv`

- `respondent_uid`: local de identified respondent code
- `submitted_at`: ISO timestamp from the export
- `duration_sec`: approximate response duration in seconds
- `story_id`: `T1`, `T2`, or `T3`
- `emotion`: `interest`, `surprise`, `sadness`, `anger`
- `emotion_ja`: Japanese label used in the survey
- `score`: integer VAS score if present
- `is_complete_case`: whether the respondent answered all 12 story by emotion cells

## `data/iceccme2026/derived_public/human_vas_summary.csv`

Aggregated human reference at story by emotion level.

## `data/iceccme2026/manifests/iceccme2026_default_manifest.csv`

Planned LLM experiment grid with one row per model, language, story, persona, and repetition.
