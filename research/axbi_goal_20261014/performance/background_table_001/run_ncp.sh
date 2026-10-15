#!/usr/bin/env bash
set -euo pipefail
root=/root/REI_AXBI_GOAL_20261014_32d11e733155/performance/background_table_001
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
exec /usr/bin/time -v -o "$root/raw/time.log" /usr/bin/timeout --foreground --signal=KILL 599s /usr/bin/taskset -c 0 /usr/bin/prlimit --as=2147483648 --fsize=134217728 -- "$root/axbi_background_table_benchmark" --contract "$root/AUTHORITY_CONTRACT.json" --output "$root/raw/results.json"
