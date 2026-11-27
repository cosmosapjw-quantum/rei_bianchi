#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
: "${WORK:?export WORK first}"
PY="$WORK/venv/bin/python"
[[ -x "$PY" ]] || { echo "Missing venv Python: $PY" >&2; exit 2; }
export GDRIVE_RCLONE_REMOTE="${GDRIVE_RCLONE_REMOTE:-gdrv:}"
export DROPBOX_RCLONE_REMOTE="${DROPBOX_RCLONE_REMOTE:-dbx:}"
restore=$("$ROOT/scripts/r31n_restore_cp4.sh")
printf '%s\n' "$restore"
CP4="$WORK/r31n_cp4_source/extracted"
OUT="$WORK/r31n_provider_fill"
mkdir -p "$OUT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PY" "$ROOT/scripts/r31n_provider_fill.py" \
  --cp4-root "$CP4" \
  --out-root "$OUT" \
  --workers 12 \
  --drive "$GDRIVE_RCLONE_REMOTE" \
  --dropbox "$DROPBOX_RCLONE_REMOTE"
