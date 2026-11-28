#!/usr/bin/env bash
# Optional configured-rclone restoration lane. No SSH secrets or overwrites.
# This execution used authenticated connectors when rclone was unavailable.
set -euo pipefail
ARCHIVE="${1:?Provide the already-created local HE23 restoration archive}"
NAME="$(basename -- "$ARCHIVE")"
CLOUD='BASS_DERIVATION_DOSSIERS_20260912'
LOCAL_SHA="$(sha256sum "$ARCHIVE" | cut -d' ' -f1)"
for PROVIDER in dbx gdrv; do
  rclone copyto --ignore-existing "$ARCHIVE" "$PROVIDER:$CLOUD/$NAME"
  REMOTE_SHA="$(rclone cat "$PROVIDER:$CLOUD/$NAME" | sha256sum | cut -d' ' -f1)"
  test "$LOCAL_SHA" = "$REMOTE_SHA" || { echo "BACKUP_SHA_MISMATCH $PROVIDER" >&2; exit 5; }
  echo "BACKUP_BYTE_VERIFIED $PROVIDER $REMOTE_SHA"
done
