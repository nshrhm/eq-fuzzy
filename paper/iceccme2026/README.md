# ICECCME 2026 Paper Folder

This folder is built on the uploaded ICECCME LaTeX template.

## Notes

- `template_reference/` contains the original uploaded template files for reference.
- `main.tex` is the working manuscript source.
- `sections/` holds the editable content blocks.
- `fig/` is for final paper figures.

## Build

```bash
latexmk -pdf main.tex
```

## Style reminders

- Keep the paper within 6 pages.
- Keep the title and abstract free of math and unusual symbols.
- Keep the main question centered on human alignment in Japanese.
- Treat multilingual results as robustness analyses unless human references are available in those languages too.
