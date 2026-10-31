#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
python code/competing_first.py >/dev/null
python code/plot_science.py >/dev/null
python -m unittest discover -s tests -q
python code/verify_manifest.py
