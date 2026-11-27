#!/usr/bin/env bash
set -euo pipefail
HE32_UNIT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec python3 "$HE32_UNIT_DIR/src/campaign.py" "$@"
