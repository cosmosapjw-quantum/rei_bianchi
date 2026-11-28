#!/usr/bin/env bash
# Run on authorized Ubuntu local host AFTER NCP native pilot has finished.
# Requires existing ~/.ssh/ncp_key and configured rclone dbx:, gdrv:.
# No deletion or rewriting; creation-only cloud destination.
set -euo pipefail
SRC="${HE22_NCP_HOST:?Set HE22_NCP_HOST=root@NCP_IP on your local machine}"
KEY="${HE22_NCP_KEY:-/home/cosmosapjw/.ssh/ncp_key}"
REMOTE_RUN='/root/HE22_NCP_20261016'
ARCHIVE='HE22_NCP_RESULTS_f7830e2f.tar.gz'
DEST='/home/cosmosapjw/archives/HE22_NATIVE_CASEA_20261016'
CLOUD='BASS_DERIVATION_DOSSIERS_20260912/HE22_NATIVE_CASEA_20261016'
mkdir -p "$DEST"
scp -P 22 -i "$KEY" -o BatchMode=yes "$SRC:$REMOTE_RUN/$ARCHIVE" "$DEST/$ARCHIVE"
scp -P 22 -i "$KEY" -o BatchMode=yes "$SRC:$REMOTE_RUN/$ARCHIVE.sha256" "$DEST/$ARCHIVE.sha256"
(cd "$DEST" && sha256sum -c "$ARCHIVE.sha256")
for provider in dbx gdrv; do
  rclone copyto --ignore-existing "$DEST/$ARCHIVE" "$provider:$CLOUD/$ARCHIVE"
  local_hash=$(sha256sum "$DEST/$ARCHIVE" | cut -d' ' -f1)
  # Full authenticated byte stream readback, NOT only provider metadata.
  remote_hash=$(rclone cat "$provider:$CLOUD/$ARCHIVE" | sha256sum | cut -d' ' -f1)
  test "$local_hash" = "$remote_hash" || {
    echo "BACKUP_SHA_MISMATCH $provider" >&2; exit 5;
  }
  echo "BACKUP_BYTE_VERIFIED $provider $remote_hash"
done
