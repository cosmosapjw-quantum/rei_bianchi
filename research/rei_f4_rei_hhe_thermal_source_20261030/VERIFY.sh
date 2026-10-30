#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m pip --version >/dev/null
python code/verify_package.py manifest
python code/build_physics.py >/dev/null
python code/plot_science.py
python -m unittest discover -s tests -v
python code/verify_package.py outputs
printf 'CLEAN_RESTORE_REPLAY=PASS; R6/C9_distinct_author=NOT_RUN; physical_fast=4/7; no_IVP=TRUE\n'
