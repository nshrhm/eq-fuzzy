# SCIS Phase 13 Result Narrative Draft

This document records the first result-narrative pass after the manuscript
artifact set was locked in Phase 12.

## Purpose

Phase 13 aligns the prose in `paper/scis2026/main.tex` with the selected main
figures and tables. The goal is not to finalize wording, but to make sure that
each manuscript claim is traceable to an included artifact and that unsupported
claims are avoided.

## Drafting Decisions

- The abstract now states the repaired main-run scale directly:
  1440 responses and 5760 emotion-level scores, with four initially invalid
  rows repaired by targeted retry.
- The contribution paragraph now emphasizes that the paper's novelty is the
  factorial persona-temperature design and reproducible entropy specification,
  not a claim that one membership function is uniquely correct.
- The method section now states that the decomposition is descriptive and does
  not imply provider-independent causal effects of API temperature.
- The experiment section now names the six-model panel and restates the
  separation rule: temperature is an API/config parameter, while persona is an
  interpretive stance in the prompt.
- The results narrative now connects the text directly to the bootstrap table:
  score interaction burdens range from 3.4% to 13.2%, whereas normalized fuzzy
  entropy interaction burdens reach 28.3% for anger and 19.8% for surprise.
- The membership sensitivity paragraph now frames `legacy_linear_v1` as a
  sensitivity baseline rather than as a competing primary endpoint.
- The conclusion now includes a clearer limitation statement covering selected
  models, selected Japanese literary texts, and fixed fuzzy-membership
  specification.

## Current Main Claims

The manuscript should keep the following claims stable unless later diagnostics
contradict them:

- fully crossing persona and temperature avoids the design aliasing of bundled
  diagonal settings;
- mean score variation is mostly persona-driven under the selected panel;
- normalized fuzzy entropy has larger persona-temperature interaction burdens
  than score;
- membership-family choice changes entropy magnitude, so entropy claims should
  be comparative under a fixed specification;
- the current evidence is descriptive for the selected models and texts, not a
  universal causal claim.

## Remaining Phase 13 Work

- Add venue-appropriate citations for LLM emotion evaluation, persona
  prompting, and smooth membership-function design.
- Tighten the Related Work section once final citations are selected.
- Decide whether the result section should be split into shorter subsections if
  the page budget allows.
- Revisit title and abstract after Phase 14 diagnostics are complete.

