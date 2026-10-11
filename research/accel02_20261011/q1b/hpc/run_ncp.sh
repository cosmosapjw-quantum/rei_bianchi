#!/usr/bin/env bash
# Run on the allocated compute node. This does not provision or rent a server.
set -euo pipefail
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export BLIS_NUM_THREADS=1
HPC_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${REI_PYTHON:-python3}" "${HPC_SCRIPT_DIR}/run_hpc_chunk.py" "$@"
