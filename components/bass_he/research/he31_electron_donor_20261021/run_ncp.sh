#!/usr/bin/env bash
# Execute only a prepared campaign, using the existing cooperative runner.
set -euo pipefail
HE31_UNIT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
HE31_REPO=$(cd -- "$HE31_UNIT/../.." && pwd)
HE31_PYTHON=${HE31_PYTHON:-python3}
HE31_GRID=${1:-pilot18_on}
case "$HE31_GRID" in
  pilot18_on|joint175_on|light_actual_pair) ;;
  *) echo 'Usage: bash run_ncp.sh [pilot18_on|joint175_on|light_actual_pair] [output_directory]' >&2; exit 2 ;;
esac
HE31_OUT=${2:-"$HE31_UNIT/results/ncp_$HE31_GRID"}
cd -- "$HE31_REPO"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
"$HE31_PYTHON" "$HE31_UNIT/src/campaign.py" run \
  --campaign "$HE31_UNIT/configs/$HE31_GRID.json" --out "$HE31_OUT" \
  --max-workers "${HE31_MAX_WORKERS:-64}" --seconds "${HE31_SECONDS:-1800}" \
  --reserve-cpus "${HE31_RESERVE_CPUS:-2}" --reserve-gib "${HE31_RESERVE_GIB:-16}" \
  --lease-dir "${HE31_LEASE_DIR:-/tmp/cosmosapjw_hpc64_cpu_leases}"
"$HE31_PYTHON" "$HE31_UNIT/src/analyze_saved.py" \
  --campaign "$HE31_UNIT/configs/$HE31_GRID.json" --results "$HE31_OUT" \
  --out "$HE31_OUT/plots"
