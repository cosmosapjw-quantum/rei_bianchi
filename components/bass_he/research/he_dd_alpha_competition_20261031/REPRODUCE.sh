#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m compileall -q src tests
PYTHONPATH="$PWD/src" python src/generate.py
python -m unittest discover -s tests -v
