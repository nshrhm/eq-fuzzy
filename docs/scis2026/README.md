# SCIS 2026 docs

This directory is reserved for SCIS-specific planning and operational notes.

Do not add fake experiment guides, placeholder configs, or provisional claims before the real SCIS design is fixed.

- `context_jp.md`: Japanese scope memo for SCIS planning discussions.
- `TODO.md`: current implementation TODO for the persona-temperature factorial deconfounding plan.
- `phase1_temperature_smoke_2026-04-25.md`: first Phase 1 smoke-test result note.

## Phase 1 implementation anchors

The Phase 1 model capability smoke test uses:

- `configs/scis/model_candidates_smoke_v1.yaml`
- `configs/scis/main_panel_phase1_passed_v1.yaml`
- `configs/scis/main_panel_v1.yaml`
- `prompts/scis/smoke_v1_system.md`
- `prompts/scis/smoke_v1_user_template.md`
- `scripts/scis2026/build_temperature_smoke_manifest.py`
- `scripts/scis2026/run_temperature_smoke.py`
- `scripts/scis2026/summarize_temperature_smoke.py`

This stage is a model-entry gate only. It checks whether candidate models accept
the configured API temperatures and return the expected structured response. It
is not evidence for the SCIS paper's substantive factorial claims.
