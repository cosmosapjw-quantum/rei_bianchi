#!/usr/bin/env bash
# Run this in an isolated NCP scratch AFTER inspecting existing workloads.
# No SSH, authentication changes, remote mutation, or unrelated process control.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
REPO=${1:?usage: run_ncp.sh REPOSITORY_COPY NEW_SCRATCH [case_csv]}
SCRATCH=${2:?new task scratch required}
CASES=${3:-age64,time8,time16,time32,spectral128}
mkdir -p "$SCRATCH"
export PATH="$HOME/.cargo/bin:$PATH"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
{ date -u +%FT%TZ; hostname; nproc; free -h; df -h "$SCRATCH"; command -v cargo; cargo --version; ps -eo pid,etime,pcpu,rss,comm --sort=-pcpu | sed -n '1,20p'; } > "$SCRATCH/inventory.txt"
bash "$ROOT/scripts/fetch_donor.sh"
python3 "$ROOT/src/prepare_native.py" --archive "$ROOT/donors/REI_POSITIVE_NATIVE_C9_20261016_v1.zip" --dest "$SCRATCH/native"
python3 "$ROOT/src/build_native.py" --prepared "$SCRATCH/native"
python3 "$ROOT/src/run_refinement.py" --prepared "$SCRATCH/native" --out "$SCRATCH/results" --cases "$CASES" --case-wall-s 1800 --total-wall-s 5400
