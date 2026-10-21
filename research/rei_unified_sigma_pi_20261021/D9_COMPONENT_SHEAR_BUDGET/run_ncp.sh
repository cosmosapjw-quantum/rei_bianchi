#!/usr/bin/env bash
# Data-only reproduction after pulling this directory; no historical IVPs.
set -euo pipefail
if [[ $# -ne 1 ]]; then
  printf 'Usage: bash %s NEW_OUTPUT_DIRECTORY\n' "$0" >&2
  exit 64
fi
d9_script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
d9_output_dir=$1
if [[ -e "$d9_output_dir" ]]; then
  printf 'Output already exists; choose a new directory: %s\n' "$d9_output_dir" >&2
  exit 65
fi
d9_python=${D9_PYTHON:-python3}
if ! command -v -- "$d9_python" >/dev/null 2>&1; then
  printf 'Python interpreter not found: %s. Install/use an existing Python 3 interpreter, or set D9_PYTHON to its executable path.\n' "$d9_python" >&2
  exit 69
fi
command -v timeout >/dev/null || { printf 'GNU timeout is required for the finite wall limit.\n' >&2; exit 69; }
# Values affect only this process and its child; no host configuration is changed.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export MPLCONFIGDIR="${TMPDIR:-/tmp}/rei-d9-matplotlib-${UID}"
exec timeout 120s "$d9_python" -B "$d9_script_dir/analyze_d9.py" \
  --portable-input "$d9_script_dir/results/portable_input/D9_COMPACT_INPUT.npz" \
  --portable-manifest "$d9_script_dir/results/portable_input/D9_COMPACT_IDENTITY.json" \
  --portable-manifest-sha 97a28d989b5b18148924effb1d45869960fd33ec8e083158db79fcf9e5689a15 \
  --contract "$d9_script_dir/EXECUTION_CONTRACT.md" \
  --out "$d9_output_dir"
