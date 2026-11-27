#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
: "${WORK:?export WORK first}"
: "${RUNTIME:?export RUNTIME first}"
PY="$WORK/venv/bin/python"
[[ -x "$PY" ]] || { echo "Missing venv Python: $PY" >&2; exit 2; }
export GDRIVE_RCLONE_REMOTE="${GDRIVE_RCLONE_REMOTE:-gdrv:}"
export DROPBOX_RCLONE_REMOTE="${DROPBOX_RCLONE_REMOTE:-dbx:}"
"$ROOT/scripts/r31n_restore_cp4.sh"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PY" "$ROOT/scripts/r31r_z2_discriminator.py" \
  --work "$WORK" \
  --runtime "$RUNTIME" \
  --cp4-root "$WORK/r31n_cp4_source/extracted" \
  --drive "$GDRIVE_RCLONE_REMOTE" \
  --dropbox "$DROPBOX_RCLONE_REMOTE"
