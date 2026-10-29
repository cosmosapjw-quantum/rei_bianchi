#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 code/verify_manifest.py
python3 -m unittest discover -s tests -v
python3 code/mp_reference.py >/dev/null
python3 code/off_manifold.py >/dev/null
printf 'BASS_NATIVE_LI_OFFMANIFOLD VERIFY PASS; NO_IVP=1\n'
