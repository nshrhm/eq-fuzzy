PYTHON ?= python

prepare-human:
	$(PYTHON) main.py prepare-human --input data/raw_private/human/文学短編作品.xlsx --output-dir data/derived_public

manifest:
	$(PYTHON) main.py build-manifest --config configs/experiment.yaml --models configs/models_default.yaml --output data/manifests/iceccme2026_default_manifest.csv

verify:
	$(PYTHON) verify_results.py

paper:
	cd paper/iceccme2026 && latexmk -pdf main.tex
