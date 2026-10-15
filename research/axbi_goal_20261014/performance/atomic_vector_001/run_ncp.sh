#!/usr/bin/env bash
set -euo pipefail
cd /root/REI_AXBI_GOAL_20261014_32d11e733155/performance/atomic_vector_001
export AXBI_PRIOR_POINT_CALLS=13152 AXBI_PRIOR_PHOTON_CELLS=896592 AXBI_PRIOR_VALIDATION_POINT_CALLS=13152
/usr/bin/time -v -o /root/REI_AXBI_GOAL_20261014_32d11e733155/performance/atomic_vector_001/raw/time.log /usr/bin/timeout --foreground --signal=KILL 299s /usr/bin/taskset -c 1 /usr/bin/prlimit --as=2147483648 --fsize=67108864 -- /root/REI_AXBI_GOAL_20261014_32d11e733155/performance/atomic_vector_001/axbi_atomic_vector_benchmark --contract /root/REI_AXBI_GOAL_20261014_32d11e733155/performance/atomic_vector_001/AUTHORITY_CONTRACT.json --output /root/REI_AXBI_GOAL_20261014_32d11e733155/performance/atomic_vector_001/raw/results.json > raw/benchmark.stdout 2> raw/benchmark.stderr
