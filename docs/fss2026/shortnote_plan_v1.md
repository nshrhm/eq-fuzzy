# Membership Specification and Sensitivity Reporting for Fuzzy-Entropy-Based LLM Emotion Scoring

Japanese title:

ファジィエントロピー型LLM感情評価におけるメンバシップ関数仕様と感度報告

## Core research question

When fuzzy entropy is computed from 0-100 LLM emotion scores, what
membership-function information must be specified, versioned, and
sensitivity-checked so that the entropy descriptor is reproducible and
interpretable?

## Three-page short-note structure

1. Introduction and problem setting
   - Define the reproducibility problem: fuzzy entropy is not fully specified
     by the score axis alone.
   - Position the note as a fuzzy-systems reporting contribution, not a new
     model-ranking experiment.

2. Fuzzy entropy and membership-dependence
   - Define Low/Medium/High membership degrees over 0-100 scores.
   - Define raw entropy and normalized entropy-response `H*(x)`.
   - Explain why breakpoints, smoothness, endpoint behavior, and normalization
     must be reported.

3. Proposed membership specification card
   - Specify score range, grid, labels, family ID, transition functions,
     breakpoints, smoothness, endpoint behavior, entropy formula, and Hmax
     estimation.
   - Treat the card as the reproducibility unit for fuzzy-entropy descriptors.

4. Entropy-response and sensitivity-reporting protocol
   - Plot membership curves and `H*(x)` over the score axis.
   - Compare unordered family pairs using maximum absolute delta, mean absolute
     delta, score at maximum delta, transition region, and integrated absolute
     difference.
   - Avoid persona-temperature decomposition, model ranking, and benchmark
     positioning outputs.

5. Discussion and conclusion
   - State that sensitivity reporting does not prove one membership family is
     uniquely correct.
   - Argue that entropy claims are interpretable only under a documented and
     versioned membership specification.

## Optional four-page FSS proceedings version

Use the same structure as the three-page version, with one additional
sensitivity-report table:

- family-pair sensitivity matrix over the 0-100 score grid

The optional table should remain score-axis-only and must not reproduce SCIS
Table IV-style cell-mean entropy sensitivity.
