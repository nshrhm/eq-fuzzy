# SCIS Phase 17 ChatGPT Pro Review Synthesis

This document synthesizes the external ChatGPT Pro review received after the
six-page expansion hypothesis was drafted. It converts the review into an
actionable Codex-side editing plan.

## Overall Judgment

The review agrees with the current direction: the paper has a strong full-paper
core, but the current manuscript is closer to a compact four-page technical note
than an award-targeting six-page SCIS&ISIS full paper.

The strongest framing is:

> A factorial deconfounding protocol for LLM-based emotion scoring, showing
> that mean emotion scores and fuzzy-entropy descriptors have different
> separability profiles under independently crossed persona and temperature
> controls.

This shifts the paper away from "another LLM emotion benchmark" and toward a
methodological contribution in experimental design and fuzzy descriptors.

## Accepted High-Priority Edits

The following recommendations should be implemented before broad stylistic
polish.

### 1. Reframe the Title and Contribution

Consider changing the title to make the factorial-design contribution visible:

- `Persona-Temperature Deconfounding in LLM-Based Fuzzy Emotion Scoring`
- `A Factorial Design for Separating Persona and Temperature Effects in
  LLM-Based Fuzzy Emotion Scoring`

Keep the contribution list focused on:

1. factorial correction of a known persona-temperature confound;
2. interaction burden as a separability diagnostic;
3. metric-specific separability: score is mostly additive/persona-driven,
   while normalized fuzzy entropy has larger interaction burden.

### 2. Fix Conditionality Language

Avoid unqualified claims such as:

- `score variation is dominated by persona effects`

Use conditional wording:

- `within each model-text-emotion persona-temperature subtable, the decomposed
  score variation is dominated by persona main effects`

This prevents readers from confusing the decomposition with a global variance
decomposition across texts, models, and emotions.

### 3. Add Exact Sum-of-Squares Formulas

The Method section should define the balanced decomposition for a 4 x 4
cell-mean table:

- cell mean: `\bar y_{p\tau}`
- persona marginal: `\bar y_{p\cdot}`
- temperature marginal: `\bar y_{\cdot\tau}`
- grand mean: `\bar y_{\cdot\cdot}`

Then add:

- `SS_P = 4 \sum_p (\bar y_{p\cdot} - \bar y_{\cdot\cdot})^2`
- `SS_T = 4 \sum_\tau (\bar y_{\cdot\tau} - \bar y_{\cdot\cdot})^2`
- `SS_{P\times T} = \sum_{p,\tau}(\bar y_{p\tau} - \bar y_{p\cdot} -
  \bar y_{\cdot\tau} + \bar y_{\cdot\cdot})^2`

State that these are computed per model-text-emotion unit from repeat means and
then summarized over the selected panel.

### 4. Clarify Bootstrap Scope

Add language that bootstrap intervals are conditional on the selected panel:

> The bootstrap intervals are conditional on the selected models, texts,
> personas, and temperatures. They quantify repeat-level stability within the
> realized panel, not uncertainty over the population of possible models or
> literary texts.

This is essential because `r = 5` is conference-scale, not journal-scale.

### 5. Specify Fuzzy Membership More Fully

The Method section should define enough of `sigmoid_s_v1` for trust and
reproducibility:

- Low/Medium/High breakpoints;
- how `sigmoid_s_v1` differs from `legacy_linear_v1`;
- why semantic breakpoints are preserved;
- why `Hmax` is family-specific;
- why normalized entropy is interpreted only under a fixed membership family.

Avoid claims that `sigmoid_s_v1` is uniquely correct or that fuzzy entropy
measures true emotional ambiguity.

### 6. Tighten Validity and Retry Wording

State the original failure rate:

- `4 / 1440 = 0.28%`

Use a reproducibility-forward sentence:

> The original raw run is retained unchanged. The repaired dataset replaces
> only the four failed manifest rows by targeted retry records; no valid row was
> rerun or selectively filtered.

### 7. Add Model Provenance Wording

Add a compact provenance statement:

> Models were accessed through provider APIs; display names are used for
> readability, while exact provider identifiers and manifest hashes are recorded
> in the reproducibility artifacts.

If space permits later, add a small model-panel table. For the current artifact
policy, provenance text is enough.

### 8. Expand Related Work with Verified Citations

Related Work needs the largest citation-aware expansion. Required categories:

- LLM emotion / empathy evaluation;
- persona prompting / role prompting / personalization;
- decoding temperature / stochastic sampling;
- fuzzy entropy and fuzziness measures;
- membership-function design;
- factorial design or interaction effects;
- computational literary affect, if a suitable verified source is available.

Do not invent references. Add only verified citations.

### 9. Add One Robustness Paragraph

Use Phase 14 diagnostics in prose, not as a new large table:

- original failed rows: 4;
- repaired failed rows: 0;
- maximum leave-one-model-out interaction-burden change: 0.034;
- entropy sensitivity correlation: 0.933.

This supports completeness without bloating the figure/table set.

### 10. Strengthen Limitations and Journal-Extension Path

Explicit limitations to include:

- selected model panel;
- selected Japanese literary texts;
- no human validation in this conference paper;
- provider-specific temperature semantics;
- `r = 5` repeat depth;
- fixed membership specification;
- API model drift;
- bootstrap intervals are conditional on the selected panel.

Journal extension path:

- increase repeat depth;
- broaden model/text panels;
- add human-reference validation;
- test membership-family and model-update robustness.

## Figure/Table Policy

The review mostly agrees with the current artifact set.

Keep:

- design contrast figure;
- bootstrap CI table;
- representative entropy/score heatmaps;
- model-level interaction-burden figure;
- compact membership sensitivity table.

Do not restore Table 3 unless exact model-level shares are specifically needed
in the main text. Fig. 3 is stronger for the current narrative.

Potential future adjustment:

- combine Fig. 1a and Fig. 1b into a two-panel figure if readability is not
  harmed;
- compress Table 1 into prose if page pressure appears later.

## Codex-Side Implementation Order

Recommended next edits:

1. Update title and abstract to foreground design aliasing and conditional
   decomposition.
2. Expand Introduction with the design-aliasing problem and contribution list.
3. Add exact decomposition formulas and bootstrap-scope caveat in Method.
4. Add fuzzy-membership rationale in Method.
5. Expand Experiments with model/text/persona/emotion details and retry policy.
6. Add robustness paragraph in Results.
7. Expand Discussion/Limitations.
8. Add verified citations and then tighten Related Work.

## Open Question Before Editing

The next blocking decision is citation handling. We should either:

- use only references already known and locally verified in the prior
  EQ-Fuzzy/Mathematics material; or
- perform a fresh citation search and add a carefully verified bibliography.

For an award-targeting six-page paper, the second option is preferable.

