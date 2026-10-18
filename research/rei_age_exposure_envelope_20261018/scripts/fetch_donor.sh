#!/usr/bin/env bash
# Fetch the already-authorized immutable PR171 fixture without human downloads.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
NAME=REI_POSITIVE_NATIVE_C9_20261016_v1.zip
DEST="$ROOT/donors/$NAME"
EXPECTED=535a4fce4b52660bc3025fdab8e4159cd9a41173f9c1cf1fa0dc524a099de83a
check() { python3 - "$1" "$EXPECTED" <<'PY'
import hashlib,sys
assert hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()==sys.argv[2], 'DONOR_SHA_MISMATCH'
PY
}
if [[ -f "$DEST" ]]; then check "$DEST"; exit 0; fi
command -v rclone >/dev/null || { echo 'BLOCKED_DONOR_DOWNLOAD_NO_AUTHENTICATED_RCLONE' >&2; exit 2; }
mkdir -p "$ROOT/donors"
TMP=$(mktemp "$ROOT/donors/donor-intake.XXXXXX")
for REMOTE in 'dbx:bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS' 'gdrv:rei_bianchi_research_backups'; do
  if rclone copyto --retries 1 --low-level-retries 1 --contimeout 15s --timeout 120s "$REMOTE/$NAME" "$TMP"; then
    check "$TMP"
    test ! -e "$DEST"
    mv "$TMP" "$DEST"
    exit 0
  fi
done
echo "BLOCKED_DONOR_DOWNLOAD; partial intake preserved at $TMP" >&2
exit 2
