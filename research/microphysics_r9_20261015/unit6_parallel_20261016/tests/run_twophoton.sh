#!/usr/bin/env bash
set -eu
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
task_root="$(cd "$(dirname "$0")/.." && pwd)"
timeout 30s python "$task_root/code/twophoton_driver.py" > "$task_root/results/laneB/execution.log" 2>&1
timeout 30s python "$task_root/tests/test_twophoton.py" > "$task_root/results/laneB/test.log" 2>&1
