#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python code/verify_manifest.py
python -m unittest discover -s tests -v
python code/mpcheck.py >/dev/null
python code/verify_manifest.py
printf 'VERIFIED SCIENCE: source manifest + targeted 13 unittest + MP80 193/193; NO IVP\n'
