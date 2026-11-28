.PHONY: strict debug native test
PYTHON ?= python3

strict:
	$(PYTHON) build.py --mode strict

debug:
	$(PYTHON) build.py --mode debug

native:
	$(PYTHON) build.py --mode strict --native --output-dir build-native

test:
	OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 $(PYTHON) test_native.py
