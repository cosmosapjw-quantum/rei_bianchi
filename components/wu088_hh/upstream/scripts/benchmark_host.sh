#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
: "${WORK:?export WORK first}"
: "${RUNTIME:?export RUNTIME first}"
PY="$WORK/venv/bin/python"
[[ -x "$PY" ]] || { echo "Missing venv Python: $PY" >&2; exit 2; }
OUT="$WORK/wu088_hh_bench_$(date -u +%Y%m%dT%H%M%SZ)_$$"
mkdir -p "$OUT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1
"$PY" -c 'import json; from wu088_hh.hardware import inspect_host; print(json.dumps(inspect_host(use_smt=True),indent=2))' > "$OUT/HARDWARE.json"
THREADS=$("$PY" -c 'import json,sys;b=json.load(open(sys.argv[1]))["effective_cpu_budget"];print(",".join(str(n) for n in (1,2,4,6,12,24) if n<=b))' "$OUT/HARDWARE.json")
"$PY" "$ROOT/scripts/benchmark_native.py" --runtime "$RUNTIME" --n 32 --g 80 --z 16 --threads "$THREADS" --repeats 3 --out "$OUT/COMPONENT_Z16.json" | tee "$OUT/COMPONENT_Z16.log"
"$PY" "$ROOT/scripts/benchmark_pool.py" --runtime "$RUNTIME" --n 32 --g 80 --z 64 --pairs 12 --repeats 3 --out "$OUT/POOL_Z64_TOPOLOGY.json" | tee "$OUT/POOL_Z64_TOPOLOGY.log"
"$PY" "$ROOT/scripts/autotune_host.py" --pool-report "$OUT/POOL_Z64_TOPOLOGY.json" --out "$OUT/HOST_TUNING_PROFILE.json" | tee "$OUT/HOST_TUNING_PROFILE.log"
printf 'Benchmark reports: %s\nNo completed anchor pairs were rewritten. No production provider was replaced.\n' "$OUT"
