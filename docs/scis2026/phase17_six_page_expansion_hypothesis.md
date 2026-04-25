# SCIS Phase 17 Six-Page Expansion Hypothesis

This document records a working hypothesis for expanding the current SCIS 2026
manuscript from a structurally complete four-page draft to a stronger full
paper that uses the six-page limit effectively without overlength fees.

## Target

Target format:

- SCIS&ISIS full paper.
- Aim for paper-award competitiveness.
- Keep the manuscript within six IEEE-style pages.
- Preserve journal-extension potential without overloading the conference
  paper.

Current local compile status:

- `paper/scis2026/main.pdf`
- 4 pages
- no LaTeX warning blockers in the latest Phase 17 audit

Working page budget:

- current: 4 pages
- target: close to 6 pages
- available expansion: approximately 1.5--2 pages

## Expansion Principle

Do not add material merely to fill pages. Add material that improves the review
criteria most likely to matter for a competitive full paper:

- significance;
- novelty;
- completeness;
- consistency;
- presentation.

The expansion should make the paper feel complete and award-ready while keeping
the main contribution narrow:

> persona-temperature factorial deconfounding for LLM-based fuzzy emotion
> scoring.

## Highest-Value Additions

### 1. Strengthen the Introduction

Estimated budget: 0.3--0.5 pages.

Add:

- a clearer problem statement around design aliasing;
- why persona and temperature are scientifically different controls;
- why diagonal or bundled designs cannot answer the separation question;
- a short paragraph explaining why this matters for LLM-based emotion scoring,
  not only for this dataset.

Purpose:

- improves significance and novelty;
- makes the paper-award pitch easier to see from page 1.

Do not add:

- broad claims that LLM emotion scores are human-grounded;
- claims that API temperature has the same behavioral meaning across providers.

### 2. Expand Related Work into Three Focused Paragraphs

Estimated budget: 0.5--0.7 pages.

Recommended structure:

1. LLM emotion evaluation and affective scoring.
2. Persona prompting and sampling-temperature control.
3. Fuzzy membership functions and entropy-style descriptors.

Purpose:

- improves completeness;
- makes the methodological position more credible;
- prepares the journal-extension path.

Citation categories needed:

- LLM emotion or affect evaluation;
- persona prompting / role prompting / simulated perspectives;
- decoding temperature or sampling control;
- fuzzy sets and membership-function design;
- entropy-style uncertainty or fuzziness descriptors.

Do not invent references. Add only verified citations.

### 3. Add a Short Experimental Design Rationale Subsection

Estimated budget: 0.3--0.4 pages.

Add under Method or Experiments:

- why model and text are treated as selected fixed panels;
- why temperature is categorical in the primary analysis;
- why `r = 5` is used for the conference main run;
- why variance/dispersion is secondary;
- why retry repair is acceptable only because it replaces exactly failed
  manifest rows while preserving `raw.jsonl`.

Purpose:

- improves consistency and completeness;
- preempts reviewer objections about statistical design.

### 4. Expand Fuzzy Entropy Membership Rationale

Estimated budget: 0.3--0.5 pages.

Add:

- explicit contrast between `legacy_linear_v1` and `sigmoid_s_v1`;
- reason for preserving semantic breakpoints;
- reason for normalizing by family-specific `Hmax`;
- statement that the sensitivity baseline is retained to avoid membership
  function overclaiming.

Purpose:

- addresses a known prior reviewer concern;
- makes the fuzzy-method contribution legible to SCIS reviewers.

Do not claim:

- `sigmoid_s_v1` is uniquely correct;
- fuzzy entropy measures true emotional ambiguity.

### 5. Add a Reviewer-Risk / Robustness Paragraph in Results

Estimated budget: 0.3--0.4 pages.

Use Phase 14 diagnostics:

- four original failed rows, all repaired by targeted retry;
- repaired failed rows: 0;
- maximum leave-one-model-out interaction-burden change: 0.034;
- entropy sensitivity correlation: 0.933;
- no need to redesign the `r = 5` main run.

Purpose:

- improves completeness;
- shows that the results are not obviously dominated by one model or by output
  instability.

This should be a paragraph, not a new large table.

### 6. Strengthen Discussion and Limitations

Estimated budget: 0.4--0.6 pages.

Add:

- what the score versus entropy contrast means;
- why the result is design-relevant rather than only metric-specific;
- limitations about selected models, selected Japanese texts, no human
  validation, provider-specific temperature semantics, and `r = 5`;
- journal-extension plan: repeat-depth increase, human validation, broader text
  panel, and model-update robustness.

Purpose:

- improves presentation and consistency;
- makes the journal-extension path explicit without weakening the conference
  paper.

## Lower-Priority Additions

These can be considered only if space remains:

- a compact pseudo-code block for the decomposition workflow;
- a one-sentence explanation of each persona stance;
- a short note on why Table 3 and top-interaction cases are retained as
  reproducibility artifacts rather than main-text tables.

Avoid adding:

- another large table;
- additional figures unless they directly improve readability;
- raw qualitative examples from model responses unless page budget remains
  after the core narrative is complete.

## Main-Text Artifact Policy

Keep the current main-text artifact set for now:

- Fig. 1a / Fig. 1b: design contrast;
- Table 1: validity;
- bootstrap CI table: primary decomposition;
- Fig. 2a / Fig. 2b: representative entropy and score heatmaps;
- Fig. 3: model-level score versus entropy interaction burden;
- Table 4: membership sensitivity.

Do not restore Table 3 unless a reviewer or coauthor specifically requests
exact model-level shares in the main text. Fig. 3 is the better main-text
artifact for the current narrative.

## Proposed Six-Page Allocation

Approximate target allocation:

- Title, authors, abstract, keywords: 0.45 pages.
- Introduction: 0.8--1.0 pages.
- Related Work: 0.6--0.8 pages.
- Method: 1.0--1.2 pages.
- Experiments: 0.6--0.8 pages.
- Results and Discussion: 1.7--2.0 pages.
- Conclusion, acknowledgment, references: 0.7--0.9 pages.

This allocation should bring the manuscript close to six pages while keeping
the paper readable.

## Suggested Prompt for ChatGPT Pro Review

Use this after Codex expands the manuscript or after a detailed expansion plan
is drafted:

```text
You are acting as a strict SCIS&ISIS 2026 full-paper reviewer and
award-committee-aware editor.

Goal:
The paper targets a SCIS&ISIS full paper, aims for paper-award competitiveness,
and should fit within six IEEE-style pages without overlength fees. It should
also remain suitable for a later journal extension.

Core contribution:
Persona × temperature factorial deconfounding for LLM-based fuzzy emotion
scoring. Persona is encoded only as an interpretive stance in the prompt.
Temperature is used only as an API/config parameter.

Main run:
6 models × 3 Japanese literary texts × 4 personas × 4 temperatures × 5 repeats
= 1440 responses and 5760 emotion-level scores.

Main result:
Score variation is mostly persona-driven, while normalized fuzzy entropy has
larger persona-temperature interaction burden, especially for anger and
surprise.

Constraints:
- no strong causal claims;
- no claim that fuzzy entropy universally measures true emotional ambiguity;
- claims are descriptive under a fixed membership specification;
- primary fuzzy membership family is sigmoid_s_v1;
- legacy_linear_v1 is a sensitivity baseline;
- target length is close to six pages, not over six pages.

Please review the manuscript and answer:
1. What should be expanded to make it award-competitive?
2. What should remain concise?
3. Which claims are too strong or under-supported?
4. Which missing citations are essential?
5. Is the current figure/table set appropriate for a six-page full paper?
6. What changes would best improve significance, novelty, completeness,
   consistency, and presentation?

Manuscript:
[PASTE main.tex]
```

## Working Decision

The next Codex-side writing task should be citation-aware expansion planning,
then manuscript expansion toward six pages. The safest first edits are:

1. expand Introduction;
2. expand Related Work after citation selection;
3. add Method/Experiment design-rationale paragraphs;
4. add one compact robustness paragraph from Phase 14;
5. strengthen Discussion and Limitations.

