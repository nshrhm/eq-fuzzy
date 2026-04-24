# Quickstart

## 1. Put private inputs in place

- Human workbook: `data/iceccme2026/raw_private/human/文学短編作品.xlsx`
- Validated story texts:
  - `data/iceccme2026/raw_private/texts/ja/T1.txt`
  - `data/iceccme2026/raw_private/texts/ja/T2.txt`
  - `data/iceccme2026/raw_private/texts/ja/T3.txt`
  - `data/iceccme2026/raw_private/texts/en/T1.txt`
  - `data/iceccme2026/raw_private/texts/en/T2.txt`
  - `data/iceccme2026/raw_private/texts/en/T3.txt`
  - `data/iceccme2026/raw_private/texts/zh/T1.txt`
  - `data/iceccme2026/raw_private/texts/zh/T2.txt`
  - `data/iceccme2026/raw_private/texts/zh/T3.txt`

## 2. Create the sanitized human reference

```bash
python -m src.iceccme2026.cli prepare-human   --input data/iceccme2026/raw_private/human/文学短編作品.xlsx   --output-dir data/iceccme2026/derived_public
```

## 3. Review the model panel

Default paper panel:
- `configs/shared/models_default.yaml` (core 6)

Fallback if you need a smaller run:
- `configs/shared/models_budget4.yaml`

## 4. Build the primary neutral manifest

```bash
python -m src.iceccme2026.cli build-manifest   --config configs/iceccme/experiment.yaml   --models configs/shared/models_default.yaml   --output data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv
```

Expected size: **540 rows** (= 6 models × 3 languages × 3 stories × 1 persona × 10 repeats)

## 5. Build the secondary persona-sensitivity manifest

```bash
python -m src.iceccme2026.cli build-manifest   --config configs/iceccme/experiment_secondary_persona.yaml   --models configs/shared/models_default.yaml   --output data/iceccme2026/manifests/iceccme2026_secondary_persona_manifest.csv
```

Expected size: **1080 rows** (= 6 models × 3 languages × 3 stories × 4 personas × 5 repeats)

## 6. Preview a prompt before the run

```bash
python scripts/iceccme2026/render_prompt_preview.py   --story-id T1   --persona-id p0   --language ja   --text-file data/iceccme2026/raw_private/texts/ja/T1.txt
```

## 7. Run or resume the OpenRouter primary collector

Expected output schema is documented in:
- `data/templates/model_scores_template.csv`
- `prompts/shared/response_schema.json`
- `prompts/iceccme/emotion_eval_user_template_multilingual_json.md`
- `data/templates/raw_outputs_json_example.jsonl`
- `data/templates/raw_outputs_legacy_example.jsonl`

Primary run output:

```bash
python -m src.iceccme2026.openrouter_runner \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv \
  --output-jsonl data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --resume
```

Export a retry-only manifest from the existing raw JSONL. Rows are included only when they have at least one failed record and no `ok == true` record:

```bash
python -m src.iceccme2026.openrouter_runner \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv \
  --output-jsonl data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --export-failed-manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_retry_failed.csv
```

Smoke-test one Claude failed row and one Gemini failed row before a larger retry:

```bash
python -m src.iceccme2026.openrouter_runner \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_retry_failed.csv \
  --output-jsonl data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --resume \
  --model-id anthropic/claude-sonnet-4.5 \
  --limit 1 \
  --max-completion-tokens 900

python -m src.iceccme2026.openrouter_runner \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_retry_failed.csv \
  --output-jsonl data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --resume \
  --model-id google/gemini-2.5-pro \
  --limit 1 \
  --max-completion-tokens 1600
```

Retry failed rows only, appending retry records to the same raw JSONL:

```bash
python -m src.iceccme2026.openrouter_runner \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_retry_failed.csv \
  --output-jsonl data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --resume \
  --max-completion-tokens 1600
```

If your collector writes JSON/JSONL or a wide CSV, normalize it first. For the OpenRouter primary raw JSONL, do not use `--join-on-order`; each raw record already carries its manifest metadata, and retry appends can make file order differ from manifest order:

```bash
python -m src.iceccme2026.cli normalize-model-scores \
  --input data/iceccme2026/raw_private/openrouter_primary_raw.jsonl \
  --manifest data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv \
  --output data/iceccme2026/interim/model_scores.csv
```

For a smoke test without running models yet:

```bash
cp data/iceccme2026/interim/model_scores_smoketest.csv data/iceccme2026/interim/model_scores.csv
```

## 8. Score human alignment

```bash
python -m src.iceccme2026.cli score-alignment   --human data/iceccme2026/derived_public/human_vas_summary.csv   --model-scores data/iceccme2026/interim/model_scores.csv   --output-dir results/iceccme2026/csv
```

## 9. Export primary and robustness tables

```bash
python scripts/iceccme2026/export_primary_tables.py \
  --alignment results/iceccme2026/csv/model_language_alignment.csv \
  --output-dir results/iceccme2026/csv \
  --primary-language ja \
  --primary-persona p0
```

Generated outputs:
- `results/iceccme2026/csv/ja_primary_ranking.csv`
- `results/iceccme2026/csv/model_language_drift_vs_ja.csv`

## 10. Regenerate paper figures and Table 2

These commands use the already exported CSV files and do not rerun model calls:

```bash
python scripts/iceccme2026/plot_figure2_ja_ranking.py
python scripts/iceccme2026/plot_figure3_cross_language_drift.py
python scripts/iceccme2026/export_table2_primary.py
```

Generated outputs:
- `paper/iceccme2026/fig/figure2_ja_ranking.png`
- `paper/iceccme2026/fig/figure2_ja_ranking.pdf`
- `paper/iceccme2026/fig/figure3_cross_language_drift.png`
- `paper/iceccme2026/fig/figure3_cross_language_drift.pdf`
- `results/iceccme2026/tables/table2_primary_summary.csv`
- `paper/iceccme2026/tables/table2_primary_summary.tex`

## 11. Final checks before submission

- confirm the title and abstract contain no risky math symbols
- confirm the paper stays within 6 pages
- confirm the core panel does not overlap problematically with any simultaneously submitted paper
- confirm the T1–T3 mapping is checked against `external/jaciii_iihmsp2025/definitions.py`
