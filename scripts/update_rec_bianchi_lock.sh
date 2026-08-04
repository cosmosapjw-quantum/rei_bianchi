#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
REMOTE=${REC_BIANCHI_REMOTE:-https://github.com/cosmosapjw-quantum/rec_bianchi.git}
OUT="$ROOT/external/rec_bianchi.lock.json"
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if HEAD_LINE=$(git ls-remote "$REMOTE" HEAD 2>"$ROOT/external/rec_bianchi.last_error.log"); then
  SHA=${HEAD_LINE%%[[:space:]]*}
  python - "$OUT" "$REMOTE" "$NOW" "$SHA" <<'PY2'
import json,sys
out,remote,now,sha=sys.argv[1:]
json.dump({'repository':remote,'role':'PRIMORDIAL_RECOMBINATION_ONLY','last_checked_utc':now,'status':'REMOTE_HEAD_LOCKED','head_sha':sha,'contains_astrophysical_reionization_required':False},open(out,'w'),indent=2)
PY2
  echo "Locked rec_bianchi HEAD: $SHA"
else
  python - "$OUT" "$REMOTE" "$NOW" <<'PY2'
import json,sys
out,remote,now=sys.argv[1:]
old={}
try: old=json.load(open(out))
except Exception: pass
old.update({'repository':remote,'role':'PRIMORDIAL_RECOMBINATION_ONLY','last_checked_utc':now,'status':'REMOTE_UNAVAILABLE','head_sha':None})
json.dump(old,open(out,'w'),indent=2)
PY2
  echo "Could not access rec_bianchi; lock records REMOTE_UNAVAILABLE" >&2
  exit 2
fi
