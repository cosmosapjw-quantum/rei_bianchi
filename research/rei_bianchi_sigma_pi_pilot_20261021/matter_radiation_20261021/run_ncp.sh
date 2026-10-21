#!/usr/bin/env bash
# Requires this new extension plus published parent code/vendor and reference/plot tables.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
run_stamp=$(date -u +%Y%m%dT%H%M%SZ)
python ../record_command.py --receipt-dir "receipts/ncp_${run_stamp}" -- \
  python component_pilot.py sweep --site ncp --max-workers 64 --wall-seconds 900 --child-seconds 3600 --output "results/ncp_${run_stamp}"
python ../record_command.py --receipt-dir "receipts/ncp_${run_stamp}_plots" -- \
  python plot_components.py --run "results/ncp_${run_stamp}" --site-label NCP
