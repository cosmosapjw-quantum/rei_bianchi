#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
REMOTE=${REI_BIANCHI_REMOTE:-https://github.com/cosmosapjw-quantum/rei_bianchi.git}
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE"
else
  git remote add origin "$REMOTE"
fi

git ls-remote origin HEAD >/dev/null
LOCAL_MAIN=$(git rev-parse main)
LOCAL_ARCHIVE=$(git rev-parse archive/full-history)

git push -u origin main
git push -u origin archive/full-history
git push origin --tags

REMOTE_MAIN=$(git ls-remote origin refs/heads/main | awk '{print $1}')
REMOTE_ARCHIVE=$(git ls-remote origin refs/heads/archive/full-history | awk '{print $1}')
if [[ "$REMOTE_MAIN" != "$LOCAL_MAIN" ]]; then
  echo "Remote main mismatch: local=$LOCAL_MAIN remote=$REMOTE_MAIN" >&2
  exit 1
fi
if [[ "$REMOTE_ARCHIVE" != "$LOCAL_ARCHIVE" ]]; then
  echo "Remote archive mismatch: local=$LOCAL_ARCHIVE remote=$REMOTE_ARCHIVE" >&2
  exit 1
fi

python - "$REMOTE" "$LOCAL_MAIN" "$LOCAL_ARCHIVE" <<'PY'
import datetime, json, sys
remote, main, archive = sys.argv[1:]
record = {
    "remote": remote,
    "pushed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "remote_main_head": main,
    "remote_archive_head": archive,
    "verified_by_ls_remote": True,
}
with open("REMOTE_PUSH_RECEIPT.json", "w", encoding="utf-8") as fh:
    json.dump(record, fh, indent=2)
PY
printf 'Pushed and verified main=%s archive/full-history=%s\n' "$LOCAL_MAIN" "$LOCAL_ARCHIVE"
