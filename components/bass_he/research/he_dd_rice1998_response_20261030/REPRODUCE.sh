#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$ROOT/src/rice_response.py"
python "$ROOT/src/plot_source.py"
python -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
python -m compileall -q "$ROOT/src" "$ROOT/tests"
