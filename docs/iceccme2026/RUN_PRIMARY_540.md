# Running the 540-row primary manifest

This note assumes you already ran `uv sync` and are using the repository-level
environment defined by `pyproject.toml` and `uv.lock`.

## 1. Confirm the expected private inputs

```text
data/catalogs/texts_private/ja/T1.txt
data/catalogs/texts_private/ja/T2.txt
data/catalogs/texts_private/ja/T3.txt
data/catalogs/texts_private/en/T1.txt
data/catalogs/texts_private/en/T2.txt
data/catalogs/texts_private/en/T3.txt
data/catalogs/texts_private/zh/T1.txt
data/catalogs/texts_private/zh/T2.txt
data/catalogs/texts_private/zh/T3.txt
```

If needed, also place the SurveyMonkey workbook at:

```text
data/iceccme2026/raw_private/human/文学短編作品.xlsx
```

## 2. Build or rebuild the Japanese human reference

```bash
uv run python -m src.iceccme2026.cli prepare-human \
  --input data/iceccme2026/raw_private/human/文学短編作品.xlsx \
  --output-dir data/iceccme2026/derived_public
```

## 3. Build the primary manifest

```bash
uv run python -m src.iceccme2026.cli build-manifest \
  --config configs/iceccme/experiment.yaml \
  --models configs/shared/models_default.yaml \
  --output data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv
```

Expected size: 540 rows.

## 4. Inspect one prompt before the full run

```bash
uv run python scripts/iceccme2026/render_prompt_preview.py \
  --story-id T1 \
  --persona-id p0 \
  --language ja \
  --text-file data/catalogs/texts_private/ja/T1.txt
```

## 5. Export your OpenRouter API key

```bash
export OPENROUTER_API_KEY='YOUR_KEY_HERE'
```

## 6. Dry-run the runner on the first unfinished row

```bash
uv run python -m src.iceccme2026.openrouter_runner \
  --repo-root . \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv \
  --texts-dir data/catalogs/texts_private \
  --output-jsonl data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --limit 1 \
  --dry-run
```

## 7. Run a 6-row smoke test first

```bash
uv run python -m src.iceccme2026.openrouter_runner \
  --repo-root . \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv \
  --texts-dir data/catalogs/texts_private \
  --output-jsonl data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --limit 6 \
  --sleep-sec 1.0 \
  --resume
```

## 8. Normalize the raw JSONL into `model_scores.csv`

```bash
uv run python -m src.iceccme2026.cli normalize-model-scores \
  --input data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv \
  --join-on-order \
  --output data/iceccme2026/interim/model_scores.csv
```

## 9. Score human alignment

```bash
uv run python -m src.iceccme2026.cli score-alignment \
  --human data/iceccme2026/derived_public/human_vas_summary.csv \
  --model-scores data/iceccme2026/interim/model_scores.csv \
  --output-dir results/iceccme2026/csv \
  --primary-language ja
```

## 10. Run the full 540-row manifest

```bash
uv run python -m src.iceccme2026.openrouter_runner \
  --repo-root . \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv \
  --texts-dir data/catalogs/texts_private \
  --output-jsonl data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --sleep-sec 0.7 \
  --resume
```

After completion:

```bash
uv run python -m src.iceccme2026.cli normalize-model-scores \
  --input data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv \
  --join-on-order \
  --output data/iceccme2026/interim/model_scores.csv

uv run python -m src.iceccme2026.cli score-alignment \
  --human data/iceccme2026/derived_public/human_vas_summary.csv \
  --model-scores data/iceccme2026/interim/model_scores.csv \
  --output-dir results/iceccme2026/csv \
  --primary-language ja
```

## Notes

- The main paper endpoint should be Japanese human alignment; EN/ZH are robustness runs.
- The runner uses JSON-schema structured outputs and writes one JSONL record per completed request.
- `--resume` skips manifest rows already present in `openrouter_primary_raw.jsonl`.
