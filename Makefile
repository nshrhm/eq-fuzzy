PYTHON ?= python

.PHONY: iceccme-prepare-human iceccme-manifest iceccme-verify iceccme-paper

iceccme-prepare-human:
	$(PYTHON) -m src.iceccme2026.cli prepare-human --input data/iceccme2026/raw_private/human/文学短編作品.xlsx --output-dir data/iceccme2026/derived_public

iceccme-manifest:
	$(PYTHON) -m src.iceccme2026.cli build-manifest --config configs/iceccme/experiment.yaml --models configs/shared/models_default.yaml --output data/iceccme2026/manifests/iceccme2026_default_manifest.csv

iceccme-verify:
	$(PYTHON) -m src.iceccme2026.verify

iceccme-paper:
	cd paper/iceccme2026 && latexmk -pdf main.tex
