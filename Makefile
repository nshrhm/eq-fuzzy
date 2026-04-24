PYTHON ?= python

prepare-human:
	$(PYTHON) main.py prepare-human --input data/iceccme2026/raw_private/human/文学短編作品.xlsx --output-dir data/iceccme2026/derived_public

manifest:
	$(PYTHON) main.py build-manifest --config configs/iceccme/experiment.yaml --models configs/shared/models_default.yaml --output data/iceccme2026/manifests/iceccme2026_default_manifest.csv

verify:
	$(PYTHON) verify_results.py

paper:
	cd paper/iceccme2026 && latexmk -pdf main.tex
