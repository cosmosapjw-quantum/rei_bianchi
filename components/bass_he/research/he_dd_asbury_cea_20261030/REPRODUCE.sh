#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/BASS_HE_PR129_mpl}"
python3 src/build_physics.py
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
python3 src/plot_physics.py
echo "SOURCE_SCOPED_REPRODUCE_OK Central28/88 HE14/18"
