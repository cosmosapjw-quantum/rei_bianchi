#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python crosswalk.py --root . --out results
python independent_audit.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python plot_science.py
python VERIFY_PACKAGE.py