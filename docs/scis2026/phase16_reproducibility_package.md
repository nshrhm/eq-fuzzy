# SCIS Phase 16 Reproducibility Package

This document records the reproducibility map for the SCIS 2026 main-run
analysis package. It is intended to make the path from API outputs to manuscript
tables and figures auditable.

## Canonical Main-Run Directory

Run directory:

- `runs/scis2026/scis2026_factorial_v1_main_manifest_v1/`

Files:

- `manifest.csv`: 1440-row main-run manifest.
- `manifest_summary.json`: manifest metadata.
- `raw.jsonl`: original main-run API output, kept immutable.
- `retry_failed_v1_manifest.csv`: manifest containing only the four failed
  rows from the original raw run.
- `raw_retry_failed_v1.jsonl`: successful targeted retry outputs for those four
  rows.
- `raw_repaired.jsonl`: repaired analysis input, created by replacing only the
  four failed original rows with successful retry rows.
- `summary.json`: repaired-run summary.
- `cell_summary.csv`: repaired-run cell summary.

The original `raw.jsonl` should not be overwritten. Downstream analysis uses
`raw_repaired.jsonl` so that the repair step remains explicit.

## Main-Run Scale

Main design:

- 6 models
- 3 texts
- 16 persona-temperature conditions
- 5 repeats
- 1440 response trials
- 5760 emotion-level scores

Analysis readiness from `artifacts/scis2026/main_analysis_v1/analysis_summary.json`:

- response rows: 1440
- valid responses: 1440
- emotion rows: 5760
- missing score rows: 0
- missing structural cells: 0
- non-estimable decomposition units: 0
- readiness passed: true

## Versioned Analysis Settings

Membership configuration:

- path: `configs/scis/fuzzy_membership_v1.yaml`
- SHA-256: `4abff0637807770a8275cb46785a082cee80cbec36ba9ff83557f25edbd689ef`

Primary family:

- `sigmoid_s_v1`

Sensitivity baseline:

- `legacy_linear_v1`

Hmax settings:

- method: dense grid
- grid step: 0.001
- `sigmoid_s_v1`: 1.018502773018
- `legacy_linear_v1`: 1.057697511124

Manifest and prompt inputs:

- factorial config: `configs/scis/factorial_v1.yaml`
- condition table: `configs/scis/condition_table_v1.csv`
- main model panel: `configs/scis/main_panel_v2.yaml`
- text registry: `configs/shared/texts_from_definitions.yaml`
- text source directory: `data/iceccme2026/raw_private/texts`
- persona registry: `configs/shared/personas_from_definitions.yaml`
- response schema: `prompts/shared/response_schema.json`
- system prompt: `prompts/scis/factorial_v1_system.md`
- user prompt template: `prompts/scis/factorial_v1_user_template.md`

The manifest and raw JSONL records store SHA-256 hashes for the prompt,
response schema, condition table, model panel, and factorial config. The raw
JSONL also stores the rendered request payload, so the exact sent prompt is
auditable even if a template is later edited.

## Reproduction Chain

The main table/figure chain is:

1. Build the main manifest:
   ```bash
   python scripts/scis2026/build_factorial_manifest.py --stage main
   ```

2. Run the main manifest with API credentials:
   ```bash
   python scripts/scis2026/run_factorial.py \
     --manifest runs/scis2026/scis2026_factorial_v1_main_manifest_v1/manifest.csv \
     --output-jsonl runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw.jsonl
   ```

3. If failed rows exist, build a retry manifest and run only those rows:
   ```bash
   python scripts/scis2026/build_factorial_retry_manifest.py

   python scripts/scis2026/run_factorial.py \
     --manifest runs/scis2026/scis2026_factorial_v1_main_manifest_v1/retry_failed_v1_manifest.csv \
     --output-jsonl runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw_retry_failed_v1.jsonl
   ```

4. Merge successful retry records into a repaired raw file:
   ```bash
   python scripts/scis2026/merge_factorial_retry.py
   ```

5. Summarize and gate-check the repaired run:
   ```bash
   python scripts/scis2026/summarize_factorial_run.py \
     --input-jsonl runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw_repaired.jsonl \
     --summary-json runs/scis2026/scis2026_factorial_v1_main_manifest_v1/summary.json \
     --cell-csv runs/scis2026/scis2026_factorial_v1_main_manifest_v1/cell_summary.csv

   python scripts/scis2026/check_main_run.py
   ```

6. Build analysis-ready long tables and decompositions:
   ```bash
   python scripts/scis2026/analyze_factorial_scores.py \
     --input-jsonl runs/scis2026/scis2026_factorial_v1_main_manifest_v1/raw_repaired.jsonl \
     --output-dir artifacts/scis2026/main_analysis_v1 \
     --expected-responses 1440 \
     --expected-emotion-rows 5760 \
     --expected-decomposition-units 72
   ```

   Note: `analyze_factorial_scores.py` defaults to the pilot run. The main-run
   expected counts must be supplied explicitly when regenerating
   `main_analysis_v1`.

7. Inspect main results:
   ```bash
   python scripts/scis2026/inspect_main_results.py
   ```

8. Build primary tables:
   ```bash
   python scripts/scis2026/build_primary_tables.py
   ```

9. Build primary figures:
   ```bash
   python scripts/scis2026/build_primary_figures.py
   ```

10. Build bootstrap confidence intervals:
    ```bash
    python scripts/scis2026/bootstrap_main_effects.py
    ```

11. Build reviewer-risk diagnostics:
    ```bash
    python scripts/scis2026/build_reviewer_diagnostics.py
    ```

12. Compile the manuscript:
    ```bash
    cd paper/scis2026
    pdflatex -interaction=nonstopmode main.tex
    pdflatex -interaction=nonstopmode main.tex
    ```

## Artifact Map

Analysis artifacts:

- `artifacts/scis2026/main_analysis_v1/`
  - `emotion_long.csv`
  - `entropy_long.csv`
  - `cell_score_summary.csv`
  - `entropy_cell_summary.csv`
  - `factorial_decomposition.csv`
  - `entropy_family_comparison.csv`
  - `analysis_summary.json`

Inspection artifacts:

- `artifacts/scis2026/main_inspection_v1/`
  - `metric_decomposition.csv`
  - `decomposition_summary_by_metric_emotion.csv`
  - `top_interaction_burdens.csv`
  - `top_absolute_interactions.csv`

Primary paper artifacts:

- `artifacts/scis2026/main_tables_v1/`
- `artifacts/scis2026/main_figures_v1/`
- `artifacts/scis2026/main_bootstrap_v1/`

Reviewer diagnostics:

- `artifacts/scis2026/main_reviewer_diagnostics_v1/`

Manuscript:

- `paper/scis2026/main.tex`

Generated PDFs and LaTeX auxiliary files are local build products and are not
part of the tracked reproducibility package.

## Current Main-Text Includes

The manuscript currently includes:

- `figure1a_prior_diagonal_design`
- `figure1b_factorial_design`
- `table1_run_validity`
- `effect_summary_bootstrap_ci`
- `figure2a_entropy_heatmap`
- `figure2b_score_heatmap`
- `figure3_model_metric_interaction_heatmap`
- `table4_entropy_sensitivity`

Tracked but currently excluded from the main text:

- `figure1_design_comparison`
- `figure2_representative_heatmaps`
- `table2_effect_summary`
- `table3_model_metric_summary`
- `table5_top_interaction_cases`

## Integrity Notes

- Temperature is configured only as an API parameter and is not included in the
  prompt text.
- Persona is encoded only as an interpretive stance in the prompt.
- `raw.jsonl` and `raw_repaired.jsonl` are both kept so that the retry step is
  auditable.
- The main-paper evidence uses the repaired run, not the failed original rows.
- Reviewer-risk diagnostics did not indicate a need to redesign the `r = 5`
  main run.

## Phase 16 Audit Notes

The reproducibility-chain audit found one important correction: the analysis
script defaults to pilot expected counts, so the main-run regeneration command
must pass the expected main-run counts explicitly. This document now includes
those flags.

No additional missing generated-artifact link was found for the current
main-text tables and figures.
