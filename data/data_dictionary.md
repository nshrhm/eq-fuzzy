# Data Dictionary

## `human_vas_long.csv`

- `respondent_uid`: local de identified respondent code
- `submitted_at`: ISO timestamp from the export
- `duration_sec`: approximate response duration in seconds
- `story_id`: `T1`, `T2`, or `T3`
- `emotion`: `interest`, `surprise`, `sadness`, `anger`
- `emotion_ja`: Japanese label used in the survey
- `score`: integer VAS score if present
- `is_complete_case`: whether the respondent answered all 12 story by emotion cells

## `human_vas_summary.csv`

Aggregated human reference at story by emotion level.

## `iceccme2026_default_manifest.csv`

Planned LLM experiment grid with one row per model, language, story, persona, and repetition.
