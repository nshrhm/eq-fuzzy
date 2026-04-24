# Interim model outputs

Place normalized long-format model scores here:

- expected final file: `data/iceccme2026/interim/model_scores.csv`
- required columns:
  - `model_id`
  - `provider`
  - `language`
  - `story_id`
  - `persona_id`
  - `repetition`
  - `emotion`
  - `score`

You can generate the file with:

```bash
python -m src.iceccme2026.cli normalize-model-scores \
  --input path/to/raw_outputs.jsonl \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv \
  --join-on-order \
  --output data/iceccme2026/interim/model_scores.csv
```

Supported raw inputs:

- already-long CSV
- wide CSV with `interest/surprise/sadness/anger` columns
- JSON / JSONL with a `scores` object
- JSON / JSONL whose raw text contains the legacy `Q1...|||score|||reason` format
