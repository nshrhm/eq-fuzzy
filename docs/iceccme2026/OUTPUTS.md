# Output Inventory

## Public derived data

- `data/iceccme2026/derived_public/human_vas_long.csv`  
  De-identified respondent-level long-format VAS data.

- `data/iceccme2026/derived_public/human_vas_summary.csv`  
  Story-by-emotion aggregated human reference table.

- `results/iceccme2026/json/human_reference_summary.json`  
  Counts and completeness metadata.

## Source catalogs

- `data/catalogs/text_catalog.csv`
- `data/catalogs/persona_catalog.csv`

## Experiment planning

- `data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv`  
  Main paper manifest.

- `data/iceccme2026/manifests/iceccme2026_secondary_persona_manifest.csv`  
  Secondary persona-sensitivity manifest.

- `results/iceccme2026/json/iceccme2026_primary_neutral_manifest_summary.json`
- `results/iceccme2026/json/iceccme2026_secondary_persona_manifest_summary.json`

## Normalized interim input after model runs

- `data/iceccme2026/interim/model_scores.csv`
  Long-format model outputs used by the alignment scorer.

## Analysis outputs expected after model runs

- `results/iceccme2026/csv/model_language_alignment.csv`  
  Per-model and per-language human alignment metrics.

- `results/iceccme2026/csv/model_language_cell_level.csv`  
  Story-by-emotion aggregated cell values for model profiles.

- `results/iceccme2026/figures/`  
  Final paper figures.

- `results/iceccme2026/tables/`  
  Export-friendly paper tables.
