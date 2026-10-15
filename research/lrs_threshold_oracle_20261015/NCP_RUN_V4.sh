#!/usr/bin/env bash
# Independent bounded 64-vCPU NCP reference run, not a production solver.
# Requires python3, scipy, numpy, pytest. Does not install packages globally.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
: "${PYTHON_BIN:=python3}"
: "${NCP_WORKERS:=12}"
case "$NCP_WORKERS" in ''|*[!0-9]*) echo 'BLOCKED: workers must be an integer' >&2; exit 2;; esac
if ((NCP_WORKERS<1 || NCP_WORKERS>16));then echo 'BLOCKED: set 1 <= NCP_WORKERS <= 16' >&2;exit 2;fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
if ! "$PYTHON_BIN" -c 'import scipy,numpy,pytest' >/dev/null 2>&1; then
    echo 'BLOCKED_DEPENDENCIES: scipy, numpy, pytest required in isolated Python environment.' >&2
    exit 3
fi
if ! sha256sum -c V4_INPUT_SHA256SUMS.txt;then
    echo 'BLOCKED_INPUT_IDENTITY: tracked source/donor hash differs from frozen bundle' >&2
    exit 4
fi
OUTROOT="${NCP_OUTPUT_ROOT:-$ROOT/evidence/ncp_v4_runs}"
mkdir -p "$OUTROOT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$OUTROOT/$STAMP"
if ! mkdir "$OUT";then echo 'BLOCKED: output directory already exists' >&2;exit 5;fi
printf '%s\n' "runner=NCP_RUN_V4.sh" "time_utc=$STAMP" "workers=$NCP_WORKERS" "hostname=$(hostname)" "python=$($PYTHON_BIN -V 2>&1)" > "$OUT/RUN_ENVIRONMENT.txt"
{ echo '==THROUGHPUT_CHECK==';nproc;free -h | head -3;uptime; } | tee -a "$OUT/RUN_ENVIRONMENT.txt"
# Leave existing live NCP EoR/Microphysics campaigns entirely unmodified.
set -o pipefail
timeout 150s "$PYTHON_BIN" -m pytest -q \
    tests/test_lrs_threshold_oracle.py \
    tests/test_verner_angular.py \
    tests/test_dynamic_chemistry.py \
    tests/test_recomb_thermal.py 2>&1 | tee "$OUT/PYTEST.txt"
timeout 150s "$PYTHON_BIN" run_recomb_thermal_v4.py 2>&1 | tee "$OUT/BENCHMARK.txt"
timeout 150s "$PYTHON_BIN" ncp_recomb_sweep_v4.py \
    --workers 1 --limit 12 --output "$OUT/serial12.csv" 2>&1 | tee "$OUT/SERIAL_SMOKE.txt"
timeout 150s "$PYTHON_BIN" ncp_recomb_sweep_v4.py \
    --workers 4 --limit 12 --output "$OUT/parallel12.csv" 2>&1 | tee "$OUT/PARALLEL_SMOKE.txt"
if ! cmp -s "$OUT/serial12.csv" "$OUT/parallel12.csv";then
    echo 'BLOCKED_PARALLEL_DETERMINISM: smoke CSV bytes disagree' >&2;exit 6
fi
echo 'PASS_SMOKE_PARALLEL_BYTE_IDENTITY' | tee "$OUT/SMOKE_COMPARISON.txt"
if [[ "${NCP_SMOKE_ONLY:-0}" == '1' ]]; then
    sha256sum "$OUT"/* > "$OUT/ALL_FILES_SHA256.txt"
    echo 'COMPLETED BOUNDED SMOKE, FULL NCP SWEEP NOT_ATTEMPTED' | tee "$OUT/STATUS.txt"
    printf 'RESULT_DIRECTORY=%s\n' "$OUT"
    exit 0
fi
# Bound CPU utilization; no GPU, no product deployment or persistent service.
timeout 900s nice -n 5 "$PYTHON_BIN" ncp_recomb_sweep_v4.py \
    --workers "$NCP_WORKERS" --output "$OUT/ncp_full.csv" 2>&1 | tee "$OUT/FULL_SWEEP.txt"
sha256sum "$OUT"/* > "$OUT/ALL_FILES_SHA256.txt"
echo 'COMPLETED NCP reference sweep; NOT production EoR' | tee "$OUT/STATUS.txt"
printf 'RESULT_DIRECTORY=%s\n' "$OUT"
