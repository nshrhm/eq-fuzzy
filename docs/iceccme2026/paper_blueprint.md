# ICECCME 2026 Paper Blueprint

## Working title

**Human-Grounded Multilingual Benchmarking of Contemporary Large Language Models for Literary Emotion Evaluation**

## Main design fixed in this repository

### Main experiment
- Persona: **p0 Neutral Reader** only
- Languages: ja / en / zh
- Stories: T1 / T2 / T3
- Models: core 6 from `configs/shared/models_default.yaml`
- Repeats: 10

### Secondary sensitivity analysis
- Personas: p1 / p2 / p3 / p4 from `definitions.py`
- Same languages and stories
- Repeats: 5
- Role in paper: appendix or one compact robustness paragraph

## Draft abstract

We present a human-grounded benchmark for literary emotion evaluation in contemporary large language models. Using human visual analogue scale judgments on three short literary works as the reference profile, we compare six current OpenRouter-accessible models on four emotion dimensions: interest, surprise, sadness, and anger. The primary analysis measures how closely each model aligns with human judgments in Japanese under a fixed neutral-reader framing. A secondary robustness analysis tests whether the same models preserve that alignment when the texts are evaluated in English and Chinese. To reduce confounding with prior persona–temperature work, the original four personas from the earlier repository are retained only as a sensitivity analysis rather than the main endpoint. The intended contribution is a compact, human-grounded multilingual benchmark that identifies which current models are closest to human reader judgments and which models exhibit the smallest cross-language drift.

## Three core figures

### Figure 1
**Workflow of the human-grounded multilingual benchmark**

### Figure 2
**Japanese human-alignment ranking for the six-model core panel**

### Figure 3
**Cross-language drift relative to each model's Japanese profile**

## Two core tables

### Table 1
Human dataset, text set, and model panel

### Table 2
Japanese alignment and cross-language drift metrics

## Claims to avoid

- do not claim causal temperature effects
- do not make EN/ZH validity claims beyond robustness unless human references exist in those languages
- do not reuse the previous LLM-only figure logic as the paper's main result
