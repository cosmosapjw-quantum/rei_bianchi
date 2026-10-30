#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
export PYTHONDONTWRITEBYTECODE=1
python code/verify.py
python -m unittest discover -s tests -v
python code/science.py >/dev/null
python code/plot_science.py
python code/verify_outputs.py
printf 'CLEAN_RESTORE_VERIFY_PASS\n'
