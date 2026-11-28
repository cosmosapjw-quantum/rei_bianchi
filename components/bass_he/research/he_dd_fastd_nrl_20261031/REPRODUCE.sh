#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$PWD/src"
export OPENBLAS_NUM_THREADS=1
python -m compileall -q src tests
python src/generate.py
python src/plot.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python src/audit_saved_data.py
python verify_manifest.py
