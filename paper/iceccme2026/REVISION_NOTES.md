# Revision notes

This revision implements the high-impact additions requested for the remaining-space policy:

- Sharpened the endpoint hierarchy: Japanese human reference is the primary endpoint; EN/ZH are robustness tests only.
- Strengthened the Introduction's research-gap statement without expanding the literature review.
- Preserved the compact methods/reproducibility capsule: 91 responses, 86 complete cases, 3 texts, 4 dimensions, 6 models, 3 languages, 10 repetitions, 540 runs, and 2160 numeric scores.
- Highlighted the distinction between absolute calibration, rank-order agreement, and cross-language robustness.
- Expanded the validity-boundary paragraph to state that EN/ZH drift reflects translated texts plus language-matched task instructions, and that the study is descriptive screening rather than formal significance testing.
- Added a reproducible system/workflow figure that shows the human VAS branch, LLM benchmark branch, OpenRouter execution path, and downstream analysis outputs.
- Expanded the Methods section with the three literary works, the concrete human VAS task, one LLM experimental unit, and the full 6 x 3 x 3 x 10 run grid.
- Added the three PDF figure assets referenced by the TeX source so the package is self-contained for compilation.

No unsupported claims, new experiments, new references, or new numerical results were added.

## ChatGPT Pro review-response pass

This pass addresses the award-level external review while preserving the six-page IEEE constraint and avoiding new experiments.

- Retitled the paper to make the endpoint hierarchy explicit: Japanese-human-grounded primary benchmark with English/Chinese robustness probes.
- Rounded abstract metrics and reframed the Japanese MAE ranking as an observed near-tie cluster rather than a hard superiority claim.
- Added targeted provenance: exact OpenRouter model slugs, collection dates, temperature, repetition policy, JSON-schema/parser handling, targeted repair status, and API replay caveat.
- Added a compact human-reference variability statement from the existing VAS derivatives (mean within-cell SD across the 12 retained cells).
- Repeated the translated-condition qualification across Methods, Results, figure captions, Discussion, and Conclusion.
- Added targeted citations for VAS methodology, cross-lingual evaluation, and Aozora Bunko source-text provenance.
- Removed the workflow figure and converted the practical screening table into prose to keep the revised manuscript at six pages after adding provenance and limitation material.

Owner-supplied ethics/consent update:

- Added the supplied consent/ethical-consideration summary for the original VAS survey: participation was voluntary, data would be anonymized and statistically analyzed, results could be used for international conference presentations or academic papers, and data-use withdrawal was possible after submission by contacting the instructor.
- No institutional approval or exemption statement was added because that status was not supplied.

## Second ChatGPT Pro review-response pass

This pass implements last-mile precision edits from the second external review.

- Updated the human-reference notation from `N_s` to `N_{s,d}` and clarified that the aggregate human reference uses all usable ratings available for each story-by-emotion cell, while 86 complete cases characterize respondent-level completeness.
- Added an interpretive sentence explaining that the mean human within-cell SD of 22.83 VAS points implies substantial reader-level variability, so model MAE should be read as agreement with the aggregate Japanese reader profile rather than individual-reader replacement.
- Replaced abstract and conclusion wording about "rank-order agreement" with "Pearson and Spearman agreement over 12 cells."
- Added the targeted retry count: 90 of 540 rows were covered by the retry manifest, using the same scoring task, with no score imputation.
- Added a limitation that the English and Chinese translations were fixed author-prepared translations and were not independently validated against separate human affect references.
- Added an accessed date to the Aozora Bunko online reference.
- Changed the Satoshi Watanabe email source to `\url{satoshi_watanabe@ieee.org}` for safer underscore rendering.
