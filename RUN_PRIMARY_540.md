# Running the 540-row primary manifest

This note assumes you already fixed:
- `scipy>=1.11` in `requirements.txt`
- standalone scripts adding repo root to `sys.path`

## 1. Confirm the expected private inputs

```text
data/raw_private/texts/ja/T1.txt
data/raw_private/texts/ja/T2.txt
data/raw_private/texts/ja/T3.txt
data/raw_private/texts/en/T1.txt
data/raw_private/texts/en/T2.txt
data/raw_private/texts/en/T3.txt
data/raw_private/texts/zh/T1.txt
data/raw_private/texts/zh/T2.txt
data/raw_private/texts/zh/T3.txt
```

If needed, also place the SurveyMonkey workbook at:

```text
data/raw_private/human/文学短編作品.xlsx
```

## 2. Build or rebuild the Japanese human reference

```bash
python main.py prepare-human \
  --input data/raw_private/human/文学短編作品.xlsx \
  --output-dir data/derived_public
```

## 3. Build the primary manifest

```bash
python main.py build-manifest \
  --config configs/experiment.yaml \
  --models configs/models_default.yaml \
  --output data/manifests/iceccme2026_primary_neutral_manifest.csv
```

Expected size: 540 rows.

## 4. Inspect one prompt before the full run

```bash
python scripts/render_prompt_preview.py \
  --story-id T1 \
  --persona-id p0 \
  --language ja \
  --text-file data/raw_private/texts/ja/T1.txt
```

## 5. Export your OpenRouter API key

```bash
export OPENROUTER_API_KEY='YOUR_KEY_HERE'
```

## 6. Dry-run the runner on the first unfinished row

```bash
python run_openrouter_manifest.py \
  --repo-root . \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --texts-dir data/raw_private/texts \
  --output-jsonl data/raw_private/openrouter_primary_raw.jsonl \
  --limit 1 \
  --dry-run
```

## 7. Run a 6-row smoke test first

```bash
python run_openrouter_manifest.py \
  --repo-root . \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --texts-dir data/raw_private/texts \
  --output-jsonl data/raw_private/openrouter_primary_raw.jsonl \
  --limit 6 \
  --sleep-sec 1.0 \
  --resume
```

## 8. Normalize the raw JSONL into `model_scores.csv`

```bash
python main.py normalize-model-scores \
  --input data/raw_private/openrouter_primary_raw.jsonl \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --join-on-order \
  --output data/interim/model_scores.csv
```

## 9. Score human alignment

```bash
python main.py score-alignment \
  --human data/derived_public/human_vas_summary.csv \
  --model-scores data/interim/model_scores.csv \
  --output-dir results/csv \
  --primary-language ja
```

## 10. Run the full 540-row manifest

```bash
python run_openrouter_manifest.py \
  --repo-root . \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --texts-dir data/raw_private/texts \
  --output-jsonl data/raw_private/openrouter_primary_raw.jsonl \
  --sleep-sec 0.7 \
  --resume
```

After completion:

```bash
python main.py normalize-model-scores \
  --input data/raw_private/openrouter_primary_raw.jsonl \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --join-on-order \
  --output data/interim/model_scores.csv

python main.py score-alignment \
  --human data/derived_public/human_vas_summary.csv \
  --model-scores data/interim/model_scores.csv \
  --output-dir results/csv \
  --primary-language ja
```

## Notes

- The main paper endpoint should be Japanese human alignment; EN/ZH are robustness runs.
- The runner uses JSON-schema structured outputs and writes one JSONL record per completed request.
- `--resume` skips manifest rows already present in `openrouter_primary_raw.jsonl`.
