#!/usr/bin/env bash
set -euo pipefail
UNIT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$(mktemp -d /tmp/rei-coupled-local-flow.XXXXXX)"
mkdir -p "$RUN_DIR/code" "$RUN_DIR/inputs" "$RUN_DIR/results" "$RUN_DIR/figures"
cp "$UNIT_DIR"/code/*.py "$RUN_DIR/code/"
cp "$UNIT_DIR"/inputs/*.json "$RUN_DIR/inputs/"
cd "$RUN_DIR"
printf 'Fresh run directory: %s\n' "$RUN_DIR"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export MPLCONFIGDIR="${TMPDIR:-/tmp}/rei_coupled_local_flow_mpl"
ulimit -t 120
ulimit -v 1048576
if [[ "${1:-}" == "--prepare-only" ]]; then
    python3 code/prepare_only.py
else
    timeout --signal=TERM 180s python3 code/run_diagnostic.py "$@"
fi
