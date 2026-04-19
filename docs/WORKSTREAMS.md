# Workstreams in `eq-fuzzy`

This repository is the implementation and reproducibility home for the **KAKENHI-side EQ-Fuzzy research line**.

## Included workstreams

### 1. ICECCME 2026

Role:
- human-grounded multilingual pilot

Main question:
- which current LLMs are closest to the Japanese human reference, and how much drift appears in EN / ZH?

Primary artifacts:
- human alignment tables
- cross-language drift plots
- compact engineering benchmark manuscript

Implementation note:
- this is the current seed workstream and should remain runnable at all times

### 2. SCIS 2026

Role:
- factorial deconfounding paper

Main question:
- how much of the observed score variation is attributable to persona, temperature, and their interaction?

Primary artifacts:
- condition tables
- interaction plots
- effect-size summaries
- conference-scale reproducible analysis package

### 3. ICICIC 2026

Role:
- benchmark positioning / matched comparison paper

Main question:
- what does EQ-Fuzzy capture beyond existing emotion benchmarks?

Primary artifacts:
- benchmark comparison matrix
- aligned subset / adapter outputs
- coverage and additional-value tables

## Explicitly excluded from this repository

### SPReAD1000

SPReAD1000 is an adjacent project, not a workstream inside this repository.

Reasons:
- application / workflow PoC rather than benchmark core
- likely to require different data governance and UI / demo layers
- should be free to move at its own pace without destabilizing benchmark code

## Common assets shared across included workstreams

- registries for texts, models, and references
- prompt templates and schema definitions
- batch execution and retry logic
- parsing and validation
- alignment metrics and fuzzy metrics
- provenance logging
- paper figure / table regeneration

## Non-shareable assets across workstreams

Even inside one repository, the following stay workstream-specific:

- main research question
- main figure set
- novelty framing
- paper-specific discussion language
- submission-ready manuscript structure

## Rule of thumb

**Share code, not claims.**

If a component is used by two or more KAKENHI-side workstreams and does not encode a paper-specific claim, it probably belongs in shared code.
If it changes the scientific framing of a manuscript, it does not.

The SCIS and ICICIC directories added during the bootstrap are placeholders only. They should stay empty except for `.gitkeep` until real configs, prompts, and analysis plans are specified.
