#!/usr/bin/env bash
# Retrieve only byte-pinned input DATA when absent. Never fetch or run unpinned code.
set -euo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
HELPER="$HERE/ncp/RESTORE_VERIFIED_INPUTS.py"
if ! python3 "$HELPER"; then
  ARCHIVE="${HE29_INPUT_ARCHIVE:-}"
  if [[ -z "$ARCHIVE" ]]; then
    command -v rclone >/dev/null || { echo HE29_NEEDS_AUTHENTICATED_INPUT_DOWNLOAD >&2; exit 10; }
    STAGE="$(mktemp -d "${TMPDIR:-/tmp}/he29-inputs.XXXXXXXX")"
    ARCHIVE="$STAGE/BASS_HE_HE29_RESUME_COMPLETE_20261018.tar.gz"
    NAME=BASS_HE_HE29_RESUME_COMPLETE_20261018_a70d320c.tar.gz
    REMOTE_PATH="BASS_DERIVATION_DOSSIERS_20260912/$NAME"
    printf 'Input retrieval stage: %s\n' "$STAGE"
    if rclone listremotes | grep -Fxq 'dbx:'; then
      rclone copyto "dbx:$REMOTE_PATH" "$ARCHIVE"
    elif rclone listremotes | grep -Fxq 'gdrv:'; then
      rclone copyto "gdrv:$REMOTE_PATH" "$ARCHIVE"
    else
      echo HE29_AUTHENTICATED_DBX_OR_GDRV_NOT_FOUND >&2; exit 10
    fi
  fi
  export HE29_INPUT_ARCHIVE="$ARCHIVE"
  python3 "$HELPER" --archive "$ARCHIVE"
fi
# The already verified core compiler/runner is unchanged.
exec bash "$HERE/ncp/BOOTSTRAP_REFERENCES.sh"
