#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python - <<'PY'
from pathlib import Path
import hashlib
p=Path('VIGILODE_BASS21_SAVED193_SOURCE_REPLAY_20261030_FULL.zip')
expect='19513fec19e53d5f2da8da50ba22aa066c634dee79ff94cff31d07b4cfb8f907'
assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==expect
PY
if [ ! -f donor/original/trajectory.npz ]; then
  mkdir -p donor
  python - <<'PY'
from zipfile import ZipFile
with ZipFile('VIGILODE_BASS21_SAVED193_SOURCE_REPLAY_20261030_FULL.zip') as z:
 assert z.testzip() is None
 z.extractall('donor')
PY
fi
python -m unittest discover -s tests -v
python code/build_atlas.py --dry >/dev/null
