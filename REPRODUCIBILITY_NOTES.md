# Reproducibility Notes

## Scope

This repository is designed for **analysis level reproducibility** of the ICECCME 2026 paper.

It supports:
- human data sanitation
- versioned multilingual run planning
- human alignment scoring
- figure and table generation for the conference paper
- paper source management on the ICECCME template

It does not automatically solve:
- API provider key management
- private translation validation
- final legal review of text redistribution
- author overlap policy review for concurrently submitted manuscripts

## Public vs private boundary

### Keep private
- raw SurveyMonkey export
- raw story texts until release policy is confirmed
- raw free text model justifications if provider terms are uncertain
- API logs containing request IDs or account metadata

### Safe to make public after review
- de identified numeric human summary tables
- numeric model score tables
- figure generation code
- paper source excluding camera ready identifiers
- prompts and response schema

## Versioning rules

1. Record the exact model identifier string.
2. Record collection date and timezone.
3. Version prompts and schema.
4. Lock the story order mapping once verified.
5. Keep Japanese human alignment as the primary endpoint.
6. Treat English and Chinese results as robustness analyses unless new human reference data exist in those languages.

## Story identifier caution

The uploaded human workbook supports a clean three block structure, but it does not itself label the three story blocks by title.
For that reason the derived public data uses `T1`, `T2`, and `T3`.
Map those identifiers to actual titles only after checking the survey instrument and experimental materials.
