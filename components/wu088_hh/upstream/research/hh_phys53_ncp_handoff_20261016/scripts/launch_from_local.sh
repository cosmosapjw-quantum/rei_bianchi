#!/usr/bin/env bash
# Run on cosmosapjw Ubuntu desktop ONLY, not in ChatGPT's isolated runtime.
# Requires existing authorized SSH key; never copies or prints the key.
set -Eeuo pipefail
umask 077
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
KEY='/home/cosmosapjw/.ssh/ncp_key'
HOST='root@49.50.142.2'
P=22
PART='research/hh_phys53_ncp_handoff_20261016'
SOURCE='research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
ORACLE='research/hh_phys53_20261016/results/ISOLATED_COULOMB_27_CASES.json'
EXPECTED='f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
RUST_EXPECTED='c49679cc5d487aa1d360dc2fadce3a1d0f3ae5a4ea00663437eaf643484e1189'
PARENT='8fe647d4e836204f783e91024f81a3f2c8f46b60'
[[ -r "$KEY" ]] || { echo 'authorized private key not available' >&2; exit 2; }
[[ -r "$SOURCE" && -r "$ORACLE" ]] || { echo 'required original NPZ or oracle missing' >&2; exit 2; }
[[ "$(sha256sum "$SOURCE" | awk '{print $1}')" == "$EXPECTED" ]] || { echo 'frozen input SHA256 mismatch' >&2; exit 2; }
[[ "$(sha256sum native/phys53_coulomb_cf.rs | awk '{print $1}')" == "$RUST_EXPECTED" ]] || { echo 'Rust source SHA256 mismatch' >&2; exit 2; }
git merge-base --is-ancestor "$PARENT" HEAD || { echo 'wrong worktree ancestry, refusing run' >&2; exit 2; }
[[ -r native/phys53_coulomb_cf.rs && -r "$PART/scripts/worker_on_ncp.sh" ]] || { echo 'missing source scripts' >&2; exit 2; }
SSH=(ssh -p "$P" -i "$KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=12)
SCP=(scp -P "$P" -i "$KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes)
echo 'REMOTE PREFLIGHT (no scientific mutation)'
"${SSH[@]}" "$HOST" 'source "$HOME/.cargo/env"; hostname; nproc; free -h | head -2; rustc --version; cargo --version; cat /proc/loadavg'
if [[ "${1:-}" == '--preflight-only' ]]; then exit 0; fi
[[ $# -eq 0 ]] || { echo 'only supported arg: --preflight-only' >&2; exit 2; }
# NCP is shared by other active workloads; runs cap at 8 threads and 16 GiB.
REMOTE="$("${SSH[@]}" "$HOST" 'mktemp -d /root/wu088_hh_phys53_XXXXXXXX')"
[[ "$REMOTE" =~ ^/root/wu088_hh_phys53_[A-Za-z0-9]{8}$ ]] || { echo 'untrusted temporary remote directory' >&2; exit 2; }
echo "ISOLATED_NCP_WORKDIR=$REMOTE"
"${SCP[@]}" native/phys53_coulomb_cf.rs "$HOST:$REMOTE/phys53_coulomb_cf.rs"
"${SCP[@]}" "$PART/scripts/worker_on_ncp.sh" "$HOST:$REMOTE/worker_on_ncp.sh"
"${SSH[@]}" "$HOST" "bash '$REMOTE/worker_on_ncp.sh' '$REMOTE'"

HEAD_SHORT="$(git rev-parse --short=12 HEAD)"
LOCAL="${ROOT}/${PART}/results/ncp_${HEAD_SHORT}"
mkdir -p "$LOCAL"
"${SCP[@]}" "$HOST:$REMOTE/RESULTS.tar.gz" "$LOCAL/RESULTS.tar.gz"
"${SCP[@]}" "$HOST:$REMOTE/RESULTS.tar.gz.sha256" "$LOCAL/RESULTS.tar.gz.sha256"
(cd "$LOCAL" && sha256sum -c RESULTS.tar.gz.sha256 && tar -xzf RESULTS.tar.gz && sha256sum -c FILES.sha256)
PYTHONPATH=src python3 "$PART/scripts/verify_ncp.py" \
  --results "$LOCAL" --oracle "$ORACLE" --source "$SOURCE" \
  --output "$LOCAL/VERIFICATION.json"
sha256sum "$LOCAL/VERIFICATION.json" > "$LOCAL/VERIFICATION.json.sha256"
printf 'NCP_RESULT_DIR=%s\n' "$LOCAL"
printf 'NCP_REMOTE_DIR=%s\n' "$REMOTE"
printf '%s\n' 'PHYS53 SCIENTIFIC NUMERIC PARITY VERIFIED FOR CENTRAL COULOMB ONLY'
