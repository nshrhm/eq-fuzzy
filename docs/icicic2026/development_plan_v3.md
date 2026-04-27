# ICICIC 2026 development plan v3

This plan records the next development steps after the benchmark-positioning
v1/v2 implementation, the budget4 pilot, the stable6 model-panel change, and
the shared text-body migration.

ICICIC remains a positioning paper. The central claim is that EQ-Fuzzy adds
uncertainty-aware, stability-oriented, and target-controllable descriptors to
the view provided by existing emotion and EI benchmarks. It must not become a
paper claiming universal benchmark superiority, standalone human validity, or
SCIS-style persona-temperature deconfounding.

## Current baseline

- Comparison matrix v1 exists under `artifacts/icicic2026/comparison_matrix_v1/`.
- Matched-subset tooling exists under `scripts/icicic2026/`.
- The Qwen-containing budget4 pilot has been preserved as pilot evidence. It
  showed schema noncompliance for `qwen/qwen3.6-plus` and should not be treated
  as the final ICICIC main panel.
- The active ICICIC matched-subset panel is
  `configs/icicic/models_stable6_from_scis.yaml`.
- The active text-body directory is `data/catalogs/texts_private`.
- The legacy ICECCME text path `data/iceccme2026/raw_private/texts` is a
  temporary compatibility alias and is planned for future removal.

## Phase A: stable6 main run

- Confirm `runs/icicic2026/icicic2026_benchmark_positioning_v1_stable6_sanity/`
  remains 4/4 valid.
- Run the 360-row stable6 main manifest:
  `runs/icicic2026/icicic2026_benchmark_positioning_v1_stable6_main/manifest.csv`.
- Analyze stable6 raw output into a stable6-specific analysis directory first,
  for example `artifacts/icicic2026/matched_subset_stable6_analysis_v1/`.
- Run `check_matched_subset_run.py --stage main` against that stable6 analysis.
- If failures occur, build a retry manifest for failed rows only. Do not rerun
  completed valid rows.

Acceptance criteria:

- 360 raw response rows are preserved.
- Raw records preserve model id, run id, prompt version, schema version, text id,
  target mode, repetition, timestamp, and git commit.
- Valid-output rate is reported even when it is imperfect.
- No output writes into `results/iceccme2026/`.

## Phase B: stable6 table and figure refresh

- Regenerate primary tables from the stable6 analysis output.
- Regenerate primary figures from the stable6 analysis output.
- Keep the budget4 pilot artifacts available as pilot/provenance material, not
  as the final main result.
- Clearly label stable6-derived artifacts if both pilot and stable6 outputs
  coexist.

Expected outputs:

- `artifacts/icicic2026/main_tables_v1/`
- `artifacts/icicic2026/main_figures_v1/`
- A summary note distinguishing budget4 pilot from stable6 main.

## Phase C: external mini-comparison curation

- Manually curate `configs/icicic/external_benchmark_items_v1.csv`.
- Include source URL, license or reuse note, benchmark name, item id, prompt
  text, expected answer where applicable, and native scoring rule.
- Use only public items whose reuse conditions are clear.
- Keep SECEU matrix-only unless item reuse is explicitly clear.
- Run external mini comparisons descriptively: native score or exact-match and
  valid-output rate only.

Do not synthesize placeholder external items.

## Phase D: manuscript development

- Continue from `paper/icicic2026/main.tex`, using `icicel.cls`.
- Add methods text only after stable6 main results are available.
- Keep all manuscript-facing claims bounded to benchmark positioning.
- Use regenerated tables and figures only; do not manually edit result numbers
  in manuscript source.
- Include limitations around model panel choice, public benchmark item reuse,
  and the fact that human validity is not established by ICICIC alone.

## Phase E: shared text alias retirement

- Keep `data/iceccme2026/raw_private/texts` as a README-only deprecation marker
  for older local notes.
- Historical manifests that mentioned the old path have been migrated to
  `data/catalogs/texts_private`.
- Runner fallback code for the old path has been removed after ICECCME, SCIS,
  and ICICIC dry-runs succeeded using `data/catalogs/texts_private`.

Candidate cleanup targets:

- Remove the README-only deprecation marker in a future cleanup if no local
  notebooks or notes still reference it.

## Deferred work

- Budget4 pilot archival is complete. The pilot remains available as provenance
  through `artifacts/icicic2026/pilot_budget4_archive_v1/`, while script
  defaults and reproducibility notes point to stable6 final materials.
- Add a small model-screening command only if another panel change becomes
  necessary.
- Consider a future public/private data inventory that explains which generated
  raw outputs include prompt-rendered private text.
