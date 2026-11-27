#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m compileall -q src tests
python src/generate.py
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -O -m unittest discover -s tests -v
python verify_manifest.py
