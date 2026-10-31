#!/bin/sh
set -eu
cd "$(dirname "$0")"
python code/verify_manifest.py
python -m unittest discover -s tests -q
python code/run.py 2100 > evidence/CLEAN_REPLAY_RESULT.json
python code/plot_science.py
python code/verify_outputs.py
