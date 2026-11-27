#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
: "${ACROPOLIS_SOURCE_DIR:?Set ACROPOLIS_SOURCE_DIR to a byte-pinned v1.3.1 extracted source directory containing acropolis/}"
export PYTHONPATH="$ACROPOLIS_SOURCE_DIR:$HERE/src:$ROOT/he_dd_acropolis_pi0_20261031/src:$ROOT/he_dd_exfor_measured_20261031/src:${PYTHONPATH:-}"
python -m unittest discover -s "$HERE/tests" -v
python "$HERE/src/generate.py"
python "$HERE/verify_manifest.py"
python "$HERE/verify_science.py"
