#!/usr/bin/env bash
# Run after this additive subtree is present in the existing NCP checkout.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
run_stamp=$(date -u +%Y%m%dT%H%M%SZ)
python record_command.py --receipt-dir "receipts/ncp_${run_stamp}" -- \
  python pilot.py sweep --site ncp --max-workers 64 \
  --wall-seconds 900 --child-seconds 3600 --output "results/ncp_${run_stamp}"
python record_command.py --receipt-dir "receipts/ncp_${run_stamp}_plots" -- \
  python plot_pilot.py --run "results/ncp_${run_stamp}" --site-label NCP
