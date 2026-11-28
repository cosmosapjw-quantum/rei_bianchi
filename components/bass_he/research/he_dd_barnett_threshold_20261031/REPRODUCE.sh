#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m compileall -q src tests
PYTHONPATH="$PWD/src:${PYTHONPATH:-}" python src/generate.py
PYTHONPATH="$PWD/src:${PYTHONPATH:-}" python -m unittest discover -s tests -v
python verify_science.py
