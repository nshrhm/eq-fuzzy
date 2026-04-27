# ICICIC 2026 writing plan v1

This plan records the post-experiment writing strategy for the ICICIC 2026
benchmark-positioning paper. It assumes no additional experiments before the
next manuscript pass.

## Data sufficiency decision

The current ICICIC data are sufficient for manuscript writing.

- The accepted stable6 matched-subset main run has 360 response rows and 1440
  emotion rows.
- The stable6 sanity and main gate checks pass with no errors.
- The stable6 valid-output rate is 1.0 for all six matched-subset models.
- The external mini-comparison has 144 response rows and 130 valid rows.
- The invalid external mini-comparison rows are not retried in this phase.
  They are treated as descriptive valid-output evidence and a limitation.

The next work is manuscript development, not data collection.

## Writing target

The ICICIC submission should aim for a strong 7.0 to 7.5 page paper under the
8-page upper limit.

The target is not to fill pages mechanically. The additional space should be
used to make the contribution clear enough for a competitive conference paper:

- explain why benchmark positioning matters;
- make the complementarity claim precise;
- interpret the generated results rather than merely listing artifacts;
- preempt predictable reviewer objections.

## Claim discipline

The paper must keep the ICICIC claim bounded.

Allowed claims:

- EQ-Fuzzy complements existing emotion and emotional-intelligence benchmarks.
- EQ-Fuzzy adds uncertainty-aware, stability-oriented, and target-controllable
  descriptors.
- The stable6 matched subset demonstrates these descriptors in a reproducible
  benchmark-positioning workflow.

Forbidden claims:

- EQ-Fuzzy replaces existing benchmarks.
- ICICIC proves standalone human validity.
- ICICIC resolves persona-temperature deconfounding.
- The external mini-comparison is a universal model leaderboard.

## Manuscript expansion plan

1. Align author and acknowledgment metadata with the ICECCME and SCIS papers.
   Use the same author group and JSPS KAKENHI acknowledgment style unless a
   submission-specific constraint requires otherwise.
2. Strengthen the Introduction around three contributions:
   benchmark coverage positioning, stable6 matched-subset descriptors, and
   reader-side versus character-side target control.
3. Expand the benchmark context section so that EQ-Bench, EmoBench, SECEU, and
   EQ-Fuzzy are compared by task type, scoring output, repeatability,
   uncertainty output, and target controllability.
4. Expand the Results section from artifact description into result
   interpretation:
   valid-output completeness, model-level dispersion and entropy, target-shift
   patterns, and the role of the external mini-comparison.
5. Expand Discussion and Limitations as reviewer defense:
   small English literary subset, public item reuse constraints, external
   invalid rows, no standalone human-validity claim, and no SCIS-style
   persona-temperature claim.
6. Keep figures optional for this writing pass. The current ICICIC class file
   uses a dvips-oriented graphics setup, so PNG figure candidates should not be
   forced into the manuscript unless they are converted and verified in a
   separate formatting pass.

## Review and rebuttal loop

When the manuscript becomes reviewable, prepare a ChatGPT Pro review packet:

- `paper/icicic2026/main.pdf`;
- the stable6 main result summary;
- the external mini-comparison provenance note;
- the claim-boundary summary;
- known limitations and non-claims.

For each ChatGPT Pro review round:

1. Classify comments as must-fix, nice-to-have, or reject.
2. Patch `paper/icicic2026/main.tex` and any supporting docs or artifacts only
   where needed.
3. Rebuild the PDF and rerun the ICICIC gate checks.
4. Draft a concise rebuttal explaining accepted changes and rejected
   suggestions.
5. Repeat until the review is effectively accept-level.

## Acceptance criteria for the next manuscript pass

- PDF builds without LaTeX errors.
- Page count is at most 8 pages, ideally 7.0 to 7.5 pages.
- Stable6 sanity and main gate checks pass.
- `python -m unittest discover -s tests` passes.
- The manuscript uses stable6 final outputs, not budget4 pilot outputs, for
  main claims.
- The paper contains explicit limitations for external invalid rows, human
  validity, and persona-temperature deconfounding.
