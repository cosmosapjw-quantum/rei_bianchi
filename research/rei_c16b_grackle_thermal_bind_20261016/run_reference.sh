#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p evidence/reference
native_root="${C16B_NATIVE_ROOT:-/root/REI_C16B_GRACKLE_SCRATCH_20261016/native}"
cc -std=c11 -O2 -fPIC -shared -I "$native_root/rust/rei_microphysics/tests/data/igm_grackle" reference_c_bridge.c -lm -o evidence/reference/grackle_reference.so
exec "${C16B_PYTHON:-/root/REI_C16B_NATIVE_20261016/venv/bin/python}" reference.py "$@"
