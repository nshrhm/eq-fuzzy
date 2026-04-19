# Shared context for the `eq-fuzzy` monorepo

## Purpose

This document is the canonical shared context for the private KAKENHI-side **EQ-Fuzzy** monorepo.

This repository contains three workstreams:

1. ICECCME 2026: human-grounded multilingual pilot
2. SCIS 2026: persona x temperature factorial deconfounding
3. ICICIC 2026: benchmark positioning / matched comparison

SPReAD1000 is not part of this repository. It should remain a separate application / workflow PoC repository.

## Operating rule

**Share code, not claims.**

The repository exists to share implementation infrastructure and reproducibility assets. It must not merge the scientific novelty claims of the three papers.

## Why the three workstreams belong together

The included workstreams share enough infrastructure to benefit from one private monorepo:

- text registries and translation provenance
- model manifests and provider routing
- prompt templates and response schemas
- execution, retry, and provenance logging
- parsing and validation
- human-alignment, drift, variance, and fuzzy metrics
- figure and table regeneration scripts

Shared code is allowed when it is claim-neutral. Shared manuscript claims are not.

## Scientific boundaries

### ICECCME 2026

- Role: human-grounded multilingual pilot
- Primary question: which contemporary LLMs align best with Japanese human VAS references, and how much EN/ZH drift appears?
- Main outputs: human-alignment ranking, cross-language drift plots, compact engineering benchmark manuscript
- Not in scope: full persona x temperature deconfounding or benchmark-positioning claims

### SCIS 2026

- Role: persona x temperature factorial deconfounding
- Primary question: how much observed variation is attributable to persona, temperature, and their interaction?
- Main outputs: condition tables, interaction plots, main-effect summaries, effect-size analyses
- Not in scope: multilingual human-alignment ranking or matched benchmark positioning

### ICICIC 2026

- Role: benchmark positioning / matched comparison
- Primary question: what does EQ-Fuzzy capture beyond existing emotion benchmarks?
- Main outputs: benchmark comparison matrix, aligned subset results, coverage and additional-value tables
- Not in scope: rerunning ICECCME human alignment as the main claim or SCIS factorial deconfounding as the main claim

## SPReAD1000 boundary

SPReAD1000 stays outside `eq-fuzzy` because it is an application / workflow PoC rather than a benchmark-core workstream. It is expected to involve annotation workflows, review queues, demo or UI layers, expert-operation logs, and different data-governance concerns.

SPReAD1000 may later reuse selected utilities from `eq-fuzzy`, but `eq-fuzzy` must not depend on SPReAD-specific workflow code, UI code, annotation-operation logic, or expert-log formats.

## Shared assets allowed

- registry readers
- model and run manifest utilities
- prompt rendering helpers
- structured-output parsers
- score validators
- MAE / Pearson / Spearman utilities
- drift, variance, fuzzy membership, and fuzzy entropy utilities
- provenance and artifact regeneration helpers

## Assets that must remain workstream-specific

- paper title and abstract
- main research question
- novelty framing
- main figure and table set
- introduction and discussion prose
- limitations language
- submission-ready manuscript structure

## Bootstrap status

The current working implementation is still ICECCME 2026:

- keep `src/iceccme2026/` intact
- keep `paper/iceccme2026/` intact
- keep current root-level commands and scripts runnable

The SCIS and ICICIC directories are placeholders only until their real configs, prompts, analyses, and manuscripts are designed.

## Next shared-core extraction targets

Do not perform a big-bang refactor. The next extraction candidates are:

- `src/iceccme2026/manifest.py`
- `src/iceccme2026/metrics.py`
- `src/iceccme2026/model_scores.py`
- generic pieces of `src/iceccme2026/reporting.py`
- generic pieces of `src/iceccme2026/paper_exports.py`

Only extract code once a second workstream needs it and the behavior can be covered by tests.
