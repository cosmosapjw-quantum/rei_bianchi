#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
REMOTE=${REI_BIANCHI_REMOTE:-https://github.com/cosmosapjw-quantum/rei_bianchi.git}
if git remote get-url origin >/dev/null 2>&1; then git remote set-url origin "$REMOTE"; else git remote add origin "$REMOTE"; fi
git ls-remote origin HEAD
git push -u origin main
git push origin archive/full-history
git push origin --tags
SHA=$(git rev-parse HEAD)
printf '{"remote":"%s","pushed_utc":"%s","main_head":"%s"}
' "$REMOTE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SHA" > REMOTE_PUSH_RECEIPT.json
echo "Pushed main, archive/full-history, tags. main=$SHA"
