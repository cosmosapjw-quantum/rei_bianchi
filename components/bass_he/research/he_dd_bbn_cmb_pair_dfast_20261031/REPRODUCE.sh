#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHONPATH="$ROOT/src" python src/generate.py
python src/plot.py
python -m unittest discover -s tests -v
python -m compileall -q src tests
