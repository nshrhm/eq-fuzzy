# SCIS Phase 10 Manuscript Draft

This document records the first manuscript-level draft state for SCIS 2026.
It is a working draft note, not a final paper claim record.

## Scope

Phase 10 turns the SCIS manuscript from the IEEE template skeleton into a
compileable conference-paper draft with:

- title
- abstract
- keywords
- introduction
- related work
- method
- experiments
- results and discussion
- conclusion
- acknowledgments
- minimal bibliography

The draft includes the generated Phase 7, Phase 8, and Phase 9 artifacts:

- primary effect tables
- bootstrap confidence interval table
- primary figure candidates
- entropy sensitivity table
- top interaction cases

## Current Manuscript Position

The draft makes a conservative method-and-analysis claim:

- persona and temperature are independently crossed rather than bundled;
- score-level variation is mostly persona dominated;
- normalized fuzzy entropy shows larger persona-temperature interaction burden;
- membership-family choice affects entropy magnitude, so entropy claims are
  framed under a fixed membership specification.

The draft does not claim:

- human-grounded validity;
- causal inference;
- cross-lingual generalization;
- benchmark superiority.

## Build Check

The manuscript compiles with:

```bash
cd paper/scis2026
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

As of this phase, the compile check succeeds without unresolved references and
without the previous `table1` overfull warning after shortening the generated
table headers.

## Next Steps

1. Reduce or prioritize tables for the conference page budget.
2. Replace placeholder wording with final SCIS conference framing.
3. Add final related-work references.
4. Decide whether bootstrap CI table stays in the main paper or moves to an
   appendix/supplement.
5. Prepare a figure/table selection pass before submission formatting.
