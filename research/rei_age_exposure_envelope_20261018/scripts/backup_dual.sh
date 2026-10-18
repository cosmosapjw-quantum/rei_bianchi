#!/usr/bin/env bash
# Requires existing authenticated rclone remotes, never creates public links.
set -euo pipefail
ARCHIVE=${1:?verified archive path required}
NAME=$(basename "$ARCHIVE")
STAGE=$(mktemp -d)
for REMOTE in 'dbx:bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS' 'gdrv:rei_bianchi_research_backups'; do
  PROVIDER=${REMOTE%%:*}
  # A pre-existing different file is not overwritten.
  if rclone lsf "$REMOTE" --files-only | grep -Fxq "$NAME"; then
    rclone copyto "$REMOTE/$NAME" "$STAGE/$PROVIDER.zip"
    cmp "$ARCHIVE" "$STAGE/$PROVIDER.zip"
  else
    rclone copyto --immutable "$ARCHIVE" "$REMOTE/$NAME"
    rclone copyto "$REMOTE/$NAME" "$STAGE/$PROVIDER.zip"
    cmp "$ARCHIVE" "$STAGE/$PROVIDER.zip"
  fi
  sha256sum "$STAGE/$PROVIDER.zip"
  python3 - "$STAGE/$PROVIDER.zip" <<'PY'
import sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
    assert z.testzip() is None
print('FULL_BYTE_READBACK_AND_CRC_PASS; fresh scientific replay remains separate')
PY
done
