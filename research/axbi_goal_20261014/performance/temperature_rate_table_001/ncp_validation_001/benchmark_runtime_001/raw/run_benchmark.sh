#!/usr/bin/env bash
set -u
ncp_root=/root/REI_AXBI_GOAL_20261014_32d11e733155/performance/temperature_rate_table_001/ncp_validation_001
ncp_runtime="$ncp_root/benchmark_runtime_001"
cd "$ncp_runtime" || exit 98
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
/usr/bin/time -v -o "$ncp_runtime/raw/time.log" /usr/bin/timeout --foreground --signal=KILL 299s /usr/bin/taskset -c 0 /usr/bin/prlimit --as=2147483648 --fsize=134217728 -- "$ncp_root/target/release/axbi_temperature_rate_table_benchmark" --contract "$ncp_runtime/AUTHORITY_CONTRACT.json" --table "$ncp_runtime/data/rates.bin" --output "$ncp_runtime/raw/results.json" > "$ncp_runtime/raw/stdout.log" 2> "$ncp_runtime/raw/stderr.log"
ncp_code=$?
printf '%s\n' "$ncp_code" > "$ncp_runtime/raw/exit_code.txt"
exit "$ncp_code"
