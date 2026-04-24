# ICECCME 2026 context

## Role

ICECCME 2026 is the **human-grounded multilingual pilot** inside the private `eq-fuzzy` monorepo.

It must remain the stable seed workstream. The existing implementation, manuscript path, commands, and generated outputs should not be moved or renamed during the documentation-first bootstrap.

## Main question

Which contemporary LLMs align best with Japanese human VAS-based literary emotion judgments, and how robust is that alignment across Japanese, English, and Chinese conditions?

## Scope

Use:

- neutral-reader primary condition
- three literary texts
- Japanese human reference as the primary endpoint
- English and Chinese as robustness conditions
- contemporary core model panel
- MAE, Pearson, Spearman, and cross-language drift

Do not use ICECCME to claim:

- full persona x temperature deconfounding
- a complete EQ-Fuzzy benchmark framework
- benchmark superiority over existing emotion benchmarks
- annotation-workflow value for SPReAD1000

## Current implementation anchors

Keep these paths and commands stable:

- `src/iceccme2026/`
- `src/iceccme2026/cli.py`
- `src/iceccme2026/openrouter_runner.py`
- `src/iceccme2026/verify.py`
- `paper/iceccme2026/`
- `configs/iceccme/experiment.yaml`
- `configs/iceccme/experiment_secondary_persona.yaml`
- `python -m src.iceccme2026.cli`
- `python -m src.iceccme2026.openrouter_runner`
- `python -m src.iceccme2026.verify`
- `scripts/iceccme2026/plot_figure2_ja_ranking.py`
- `scripts/iceccme2026/plot_figure3_cross_language_drift.py`
- `scripts/iceccme2026/export_table2_primary.py`

## Differentiation

SCIS should own persona x temperature interaction claims. ICECCME should keep persona as a secondary sensitivity analysis rather than the main result.

ICICIC should own matched benchmark comparison. ICECCME should not become a benchmark-positioning paper.

SPReAD1000 stays outside this repository. ICECCME should not discuss review queues, annotation-support UI, or workflow efficiency.

## Manuscript discipline

ICECCME can say:

- small human-grounded benchmarks are useful for model screening
- Japanese human alignment and cross-language robustness are related but not identical
- multilingual drift is a robustness signal, not proof of general emotional understanding

ICECCME should not say:

- this is a definitive human-grounded benchmark
- this proves general multilingual emotional intelligence
- this resolves persona, temperature, ambiguity, and benchmark-positioning questions
