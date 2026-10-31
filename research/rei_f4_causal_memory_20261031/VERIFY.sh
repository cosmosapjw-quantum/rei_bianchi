#!/bin/sh
set -eu
cd "$(dirname "$0")"
python code/build_memory.py >/dev/null
python code/test_memory.py >/dev/null
python code/plot_science.py >/dev/null
python code/verify_transport.py
python code/verify_outputs.py
python code/verify_manifest.py
