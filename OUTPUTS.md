# Output Inventory

## Public derived data

- `data/derived_public/human_vas_long.csv`  
  De-identified respondent-level long-format VAS data.

- `data/derived_public/human_vas_summary.csv`  
  Story-by-emotion aggregated human reference table.

- `results/json/human_reference_summary.json`  
  Counts and completeness metadata.

## Source catalogs

- `data/catalogs/text_catalog.csv`
- `data/catalogs/persona_catalog.csv`

## Experiment planning

- `data/manifests/iceccme2026_primary_neutral_manifest.csv`  
  Main paper manifest.

- `data/manifests/iceccme2026_secondary_persona_manifest.csv`  
  Secondary persona-sensitivity manifest.

- `results/json/iceccme2026_primary_neutral_manifest_summary.json`
- `results/json/iceccme2026_secondary_persona_manifest_summary.json`

## Normalized interim input after model runs

- `data/interim/model_scores.csv`
  Long-format model outputs used by the alignment scorer.

## Analysis outputs expected after model runs

- `results/csv/model_language_alignment.csv`  
  Per-model and per-language human alignment metrics.

- `results/csv/model_language_cell_level.csv`  
  Story-by-emotion aggregated cell values for model profiles.

- `results/figures/`  
  Final paper figures.

- `results/tables/`  
  Export-friendly paper tables.
