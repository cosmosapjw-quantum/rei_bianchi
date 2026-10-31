#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_manifest.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/run_full.py --combine-only
python code/thermal_port.py
python code/plot_science.py
python code/verify_outputs.py
printf 'CLEAN_RESTORE_VERIFIED_SCOPED\n'
