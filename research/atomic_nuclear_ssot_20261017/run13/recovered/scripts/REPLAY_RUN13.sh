#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
if [[ -n "${RUST_BIN:-}" ]]; then export PATH="$RUST_BIN:$PATH"; fi
export CARGO_BUILD_JOBS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
case "${1:-verify}" in
 verify) sha256sum -c SHA256SUMS.txt;;
 build|lint) bash scripts/REPLAY_OFFLINE.sh "$1";;
 tests) bash scripts/REPLAY_OFFLINE.sh tests; (cd scripts; python -m unittest test_run13_endpoint_guard -v);;
 compare) python scripts/run13_analyze.py;;
 tail) python scripts/run13_replay.py;;
 *) echo 'Use verify|build|tests|lint|compare|tail in separate bounded calls' >&2; exit 2;;
esac
