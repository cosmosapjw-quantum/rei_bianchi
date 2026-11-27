#!/usr/bin/env bash
set -euo pipefail
: "${WORK:?export WORK first}"
DBX="${DROPBOX_RCLONE_REMOTE:-dbx:}"
BASE="$WORK/r31n_cp4_source"
PARTS="$BASE/parts"
ZIP="$BASE/WU088_HH_C21_TRANSFER_CP4_20260923.zip"
ROOT="$BASE/extracted"
REMOTE="BASS_DERIVATION_DOSSIERS_20260912"
mkdir -p "$PARTS" "$BASE"
declare -A SHA=(
 [part01]=10eea2916c107c61c7ddcaa3c418b9635eaa06b4e892a5487b62a46bde47057b
 [part02]=f6b691515b02b3eb2425a0fb2a3b14ee2f9012954e183a053366d470abdbaeb0
 [part03]=6f16acb6d2bb76c68e6dd5a9b4aaa062b64747f13ef4b344e8c03954ca5426f5
)
for p in part01 part02 part03; do
  f="WU088_HH_C21_TRANSFER_CP4_20260923.zip.$p"
  dst="$PARTS/$f"
  if [[ ! -f "$dst" ]] || [[ "$(sha256sum "$dst" | awk '{print $1}')" != "${SHA[$p]}" ]]; then
    rm -f "$dst"
    rclone copyto --immutable "${DBX%/}/$REMOTE/$f" "$dst"
  fi
  got=$(sha256sum "$dst" | awk '{print $1}')
  [[ "$got" == "${SHA[$p]}" ]] || { echo "part SHA mismatch: $p" >&2; exit 70; }
done
cat "$PARTS"/*.part01 "$PARTS"/*.part02 "$PARTS"/*.part03 > "$ZIP.tmp"
got=$(sha256sum "$ZIP.tmp" | awk '{print $1}')
[[ "$got" == "c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9" ]] || { echo "CP4 reconstructed SHA mismatch" >&2; exit 71; }
mv -f "$ZIP.tmp" "$ZIP"
unzip -tq "$ZIP" >/dev/null
if [[ ! -f "$ROOT/.R31N_CP4_SHA256" ]] || [[ "$(cat "$ROOT/.R31N_CP4_SHA256" 2>/dev/null || true)" != "$got" ]]; then
  rm -rf "$ROOT.tmp" "$ROOT"
  mkdir -p "$ROOT.tmp"
  unzip -q "$ZIP" -d "$ROOT.tmp"
  mv "$ROOT.tmp" "$ROOT"
  printf '%s\n' "$got" > "$ROOT/.R31N_CP4_SHA256"
fi
printf '{"status":"CP4_RESTORE_VERIFIED","cp4_root":"%s","archive":"%s","sha256":"%s"}\n' "$ROOT" "$ZIP" "$got"
