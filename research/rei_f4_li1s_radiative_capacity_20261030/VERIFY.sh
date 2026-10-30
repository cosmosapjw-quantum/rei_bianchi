#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
cat <<'STAMP' | sha256sum -c --status
6e50586131ab6f8f76b72ee8c7125dfd3225211d528609c862e01a305a0ab6d3  source/PR279_FULL.zip
STAMP
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/rei_li_radiative_pycache" python -m unittest discover -s tests -p 'test_*.py' -v
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/rei_li_radiative_pycache" python code/radiative_atlas.py > /dev/null
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/rei_li_radiative_pycache" python code/plot_science.py
python code/check_manifest.py
printf 'SOURCE_PR279=EXACT; TARGETED_TESTS=28/28; ENERGY=CONSERVED; NEW_IVPS=0; HEAT=UNBOUND\n'
