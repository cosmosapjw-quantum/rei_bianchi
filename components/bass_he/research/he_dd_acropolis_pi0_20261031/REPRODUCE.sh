#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# In a restored private archive, if source ZIP exists, extract without touching parent tree.
if [[ -z "${ACROPOLIS_SOURCE_DIR:-}" && -f "${HERE}/../../sources/acropolis-main.zip" ]]; then
  mkdir -p "${HERE}/../../vendor_unpack"
  unzip -q -n "${HERE}/../../sources/acropolis-main.zip" -d "${HERE}/../../vendor_unpack"
  export ACROPOLIS_SOURCE_DIR="${HERE}/../../vendor_unpack/acropolis-main"
fi
if [[ -z "${ACROPOLIS_SOURCE_DIR:-}" || ! -f "$ACROPOLIS_SOURCE_DIR/VERSION" ]]; then
  echo 'Requires original ACROPOLIS v1.3.1 source directory in ACROPOLIS_SOURCE_DIR' >&2; exit 2
fi
if [[ "$(cat "$ACROPOLIS_SOURCE_DIR/VERSION")" != '1.3.1' ]]; then echo WRONG_SOURCE_VERSION >&2; exit 3; fi
export PYTHONPATH="$ACROPOLIS_SOURCE_DIR:${PYTHONPATH:-}"
export NUMBA_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
python -m unittest discover -s "$HERE/tests" -v
python "$HERE/src/generate.py"
python "$HERE/verify_manifest.py"
