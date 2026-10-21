#!/usr/bin/env bash
set -euo pipefail
# Preparation only. Run from a copy of this complete package. This script performs no SSH.
# Resumes exactly fixed checkpoints, preserving earlier attempts and shared phase debit.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
package_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
phase="${1:?Usage: run_ncp.sh b1-or-b2 path-to-independent-review.json}"
review="${2:?Independent frozen-contract review is required}"
python3 "$package_root/components/unified_pilot.py" run --phase "$phase" --profile ncp --max-workers 63 --resume --review-approval "$review"
python3 "$package_root/components/unified_pilot.py" check --phase "$phase" --profile ncp
