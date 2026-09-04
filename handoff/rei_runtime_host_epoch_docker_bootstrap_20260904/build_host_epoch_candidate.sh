#!/usr/bin/env bash
# Docker-backed H1/H2 host-epoch reconstruction for REI 03A4.
#
# The interactive host is never apt/dpkg/debootstrap-mutated.  A disposable
# networked builder creates a Snapshot-pinned rootfs archive; an imported image
# is then verified offline, read-only, with all capabilities dropped.

set -euo pipefail
umask 077

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
CONTRACT="$PACKAGE_DIR/CONTRACT.json"
SNAPSHOT_ID='20250115T120000Z'
SNAPSHOT_MIRROR="https://snapshot.ubuntu.com/ubuntu/${SNAPSHOT_ID}"
GCC_VERSION='13.3.0-6ubuntu2~24.04'
BUILDER_IMAGE_REF="${REI_H1H2_BUILDER_IMAGE:-ubuntu:24.04}"
MODE="${1:---build}"

# Machine-auditable safety markers.
HOST_APT_INSTALL_FORBIDDEN=1
HOST_DPKG_INSTALL_FORBIDDEN=1
HOST_ALTERNATIVES_MUTATION_FORBIDDEN=1
HOST_USR_BIND_FORBIDDEN=1
GLOBAL_ATTEMPT_REF_FORBIDDEN=1
LOCAL_LEASE_FORBIDDEN=1
NATIVE_RUNTIME_FORBIDDEN=1
H3_RUST_CLOSURE_NOT_RUN=1
SECTION0_NOT_RUN=1
SCIENTIFIC_PASS_NOT_CLAIMED=1

stop() {
  local classification="$1"
  shift || true
  printf 'classification=%s\n' "$classification" >&2
  while (($#)); do
    printf '%s\n' "$1" >&2
    shift
  done
  exit 65
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || stop "REQUIRED_COMMAND_UNAVAILABLE:$1"
}

canonical_dir() {
  mkdir -p -- "$1" || stop "OUTPUT_DIRECTORY_CREATION_FAILED:$1"
  realpath -- "$1" || stop "OUTPUT_DIRECTORY_RESOLUTION_FAILED:$1"
}

is_under() {
  local child="$1"
  local parent="$2"
  [[ "$child" == "$parent" || "$child" == "$parent"/* ]]
}

if [[ "$MODE" == '--plan' ]]; then
  cat <<EOF
classification=PASS_03A4_HOST_EPOCH_DOCKER_BOOTSTRAP_SOURCE_PLAN
snapshot_id=$SNAPSHOT_ID
snapshot_mirror=$SNAPSHOT_MIRROR
builder_image_reference=$BUILDER_IMAGE_REF
networked_phase=DISPOSABLE_BOOTSTRAP_ONLY
verification_network=NONE
verification_rootfs=READ_ONLY
verification_capabilities=DROP_ALL
builder_authority_effect=NONE
HOST_APT_INSTALL_FORBIDDEN=$HOST_APT_INSTALL_FORBIDDEN
HOST_DPKG_INSTALL_FORBIDDEN=$HOST_DPKG_INSTALL_FORBIDDEN
HOST_ALTERNATIVES_MUTATION_FORBIDDEN=$HOST_ALTERNATIVES_MUTATION_FORBIDDEN
HOST_USR_BIND_FORBIDDEN=$HOST_USR_BIND_FORBIDDEN
GLOBAL_ATTEMPT_REF_FORBIDDEN=$GLOBAL_ATTEMPT_REF_FORBIDDEN
LOCAL_LEASE_FORBIDDEN=$LOCAL_LEASE_FORBIDDEN
NATIVE_RUNTIME_FORBIDDEN=$NATIVE_RUNTIME_FORBIDDEN
H3_RUST_CLOSURE_NOT_RUN=$H3_RUST_CLOSURE_NOT_RUN
SECTION0_NOT_RUN=$SECTION0_NOT_RUN
SCIENTIFIC_PASS_NOT_CLAIMED=$SCIENTIFIC_PASS_NOT_CLAIMED
EOF
  exit 0
fi
[[ "$MODE" == '--build' ]] || stop "UNKNOWN_MODE:$MODE"

for command_name in docker git realpath sha256sum stat date; do
  require_command "$command_name"
done
[[ -f "$CONTRACT" ]] || stop "CONTRACT_UNAVAILABLE:$CONTRACT"
docker info >/dev/null 2>&1 || stop 'DOCKER_DAEMON_UNAVAILABLE'

REPO_ROOT="$(git -C "$PACKAGE_DIR" rev-parse --show-toplevel 2>/dev/null)" \
  || stop 'GIT_WORKTREE_UNAVAILABLE'
REPO_ROOT="$(realpath -- "$REPO_ROOT")"

REI_HOST_EPOCH_ROOT="${REI_HOST_EPOCH_ROOT:-$HOME/.local/share/rei_bianchi/host_epochs}"
RECEIPT_ROOT="${RECEIPT_ROOT:-$HOME/Dropbox/bianchi/_runtime_receipts}"
ATTEMPT_STATE_ROOT="${ATTEMPT_STATE_ROOT:-}"

HOST_EPOCH_ROOT_REAL="$(canonical_dir "$REI_HOST_EPOCH_ROOT")"
RECEIPT_ROOT_REAL="$(canonical_dir "$RECEIPT_ROOT")"

is_under "$HOST_EPOCH_ROOT_REAL" "$REPO_ROOT" \
  && stop 'HOST_EPOCH_ROOT_INSIDE_GIT_WORKTREE'
is_under "$HOST_EPOCH_ROOT_REAL" '/tmp' \
  && stop 'HOST_EPOCH_ROOT_UNDER_TMP_FORBIDDEN'
if [[ -n "$ATTEMPT_STATE_ROOT" ]]; then
  ATTEMPT_STATE_ROOT_REAL="$(canonical_dir "$ATTEMPT_STATE_ROOT")"
  if is_under "$HOST_EPOCH_ROOT_REAL" "$ATTEMPT_STATE_ROOT_REAL" \
    || is_under "$ATTEMPT_STATE_ROOT_REAL" "$HOST_EPOCH_ROOT_REAL"; then
    stop 'HOST_EPOCH_ROOT_OVERLAPS_ATTEMPT_STATE_ROOT'
  fi
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$$"
LABEL="REI_03A4_HOST_EPOCH_DOCKER_${STAMP}"
CANDIDATE_DIR="$HOST_EPOCH_ROOT_REAL/$LABEL"
RECEIPT_DIR="$RECEIPT_ROOT_REAL/${LABEL}_RECEIPT"
ROOTFS_TAR="$CANDIDATE_DIR/rootfs.tar"
ROOTFS_PART="$CANDIDATE_DIR/rootfs.tar.part"
BUILD_LOG="$RECEIPT_DIR/BUILD.log"
PULL_LOG="$RECEIPT_DIR/BUILDER_PULL.log"
BUILDER_INSPECT="$RECEIPT_DIR/BUILDER_IMAGE_INSPECT.json"
CANDIDATE_RECEIPT="$RECEIPT_DIR/H1_H2_CANDIDATE_RECEIPT.json"
PACKAGE_MANIFEST="$RECEIPT_DIR/PACKAGE_MANIFEST.tsv"
VERIFY_STDERR="$RECEIPT_DIR/VERIFY.stderr"
VERIFY_TAG="rei-03a4-host-epoch-candidate:${STAMP,,}"
VERIFY_IMAGE_ID=''

[[ ! -e "$CANDIDATE_DIR" && ! -e "$RECEIPT_DIR" ]] \
  || stop 'CREATE_ONLY_OUTPUT_ALREADY_EXISTS'
mkdir -m 700 -- "$CANDIDATE_DIR" "$RECEIPT_DIR" \
  || stop 'CREATE_ONLY_OUTPUT_FAILURE'

cleanup() {
  rm -f -- "$ROOTFS_PART" >/dev/null 2>&1 || true
  if [[ -n "$VERIFY_IMAGE_ID" ]]; then
    docker image rm -f "$VERIFY_IMAGE_ID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT HUP INT TERM

printf '===== BUILDER IMAGE =====\n'
docker pull "$BUILDER_IMAGE_REF" >"$PULL_LOG" 2>&1 \
  || stop 'BUILDER_IMAGE_PULL_FAILED' "log=$PULL_LOG"
BUILDER_IMAGE_ID="$(docker image inspect --format '{{.Id}}' "$BUILDER_IMAGE_REF")" \
  || stop 'BUILDER_IMAGE_INSPECT_FAILED'
BUILDER_IMAGE_DIGESTS="$(docker image inspect --format '{{join .RepoDigests ","}}' "$BUILDER_IMAGE_REF")"
docker image inspect "$BUILDER_IMAGE_ID" >"$BUILDER_INSPECT" \
  || stop 'BUILDER_IMAGE_INSPECT_SERIALIZATION_FAILED'
printf 'builder_image_id=%s\n' "$BUILDER_IMAGE_ID"
printf 'builder_authority_effect=NONE\n'

printf '===== NETWORKED DISPOSABLE BOOTSTRAP =====\n'
set +e
docker run --rm \
  --interactive \
  --network=bridge \
  --security-opt=no-new-privileges \
  --env DEBIAN_FRONTEND=noninteractive \
  --env SNAPSHOT_ID="$SNAPSHOT_ID" \
  --env GCC_VERSION="$GCC_VERSION" \
  "$BUILDER_IMAGE_ID" \
  /bin/bash -s >"$ROOTFS_PART" 2>"$BUILD_LOG" <<'BUILDER'
set -euo pipefail
SNAPSHOT_MIRROR="https://snapshot.ubuntu.com/ubuntu/${SNAPSHOT_ID}"
export DEBIAN_FRONTEND=noninteractive

apt-get update >&2
apt-get install -y --no-install-recommends \
  ca-certificates debootstrap ubuntu-keyring xz-utils tar >&2

mkdir -p /rootfs
debootstrap \
  --arch=amd64 \
  --variant=minbase \
  --components=main \
  noble \
  /rootfs \
  "$SNAPSHOT_MIRROR" >&2

cat >/rootfs/etc/apt/sources.list <<EOF
# Exact Ubuntu Snapshot authority for this isolated candidate only.
deb [signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] $SNAPSHOT_MIRROR noble main universe
deb [signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] $SNAPSHOT_MIRROR noble-updates main universe
deb [signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] $SNAPSHOT_MIRROR noble-security main universe
EOF
rm -f /rootfs/etc/apt/sources.list.d/ubuntu.sources
cp -L /etc/resolv.conf /rootfs/etc/resolv.conf
cat >/rootfs/usr/sbin/policy-rc.d <<'EOF'
#!/bin/sh
exit 101
EOF
chmod 0755 /rootfs/usr/sbin/policy-rc.d

chroot /rootfs /usr/bin/env DEBIAN_FRONTEND=noninteractive \
  /usr/bin/apt-get update >&2
chroot /rootfs /usr/bin/env DEBIAN_FRONTEND=noninteractive \
  /usr/bin/apt-get install -y --no-install-recommends \
  ca-certificates \
  git \
  python3 \
  gcc-x86-64-linux-gnu \
  "gcc-13-x86-64-linux-gnu=${GCC_VERSION}" \
  binutils \
  binutils-x86-64-linux-gnu \
  libmpfr6 \
  libgmp10 >&2

rm -f /rootfs/usr/sbin/policy-rc.d
mkdir -p /rootfs/var/lib/rei-03a4-host-epoch
printf '%s\n' "$SNAPSHOT_ID" \
  >/rootfs/var/lib/rei-03a4-host-epoch/snapshot-id
rm -f /rootfs/etc/machine-id /rootfs/var/lib/dbus/machine-id
: >/rootfs/etc/machine-id
rm -f /rootfs/etc/resolv.conf
: >/rootfs/etc/resolv.conf

# The archive records root ownership internally while stdout redirection makes
# the host-side archive itself owned by the invoking unprivileged user.
tar --numeric-owner --xattrs --acls -C /rootfs -cpf - .
BUILDER
BUILD_RC=$?
set -e
[[ "$BUILD_RC" -eq 0 ]] \
  || stop 'SNAPSHOT_ROOTFS_BOOTSTRAP_FAILED' "rc=$BUILD_RC" "log=$BUILD_LOG"
[[ -s "$ROOTFS_PART" ]] || stop 'ROOTFS_ARCHIVE_EMPTY'
mv -- "$ROOTFS_PART" "$ROOTFS_TAR" \
  || stop 'ROOTFS_ARCHIVE_ATOMIC_RENAME_FAILED'
ROOTFS_SHA256="$(sha256sum -- "$ROOTFS_TAR" | awk '{print $1}')"
ROOTFS_SIZE="$(stat -c '%s' -- "$ROOTFS_TAR")"
printf 'rootfs_sha256=%s\n' "$ROOTFS_SHA256"
printf 'rootfs_size_bytes=%s\n' "$ROOTFS_SIZE"

printf '===== IMPORT FOR OFFLINE VERIFICATION =====\n'
VERIFY_IMAGE_ID="$(docker import "$ROOTFS_TAR" "$VERIFY_TAG")" \
  || stop 'ROOTFS_IMPORT_FAILED'
[[ -n "$VERIFY_IMAGE_ID" ]] || stop 'ROOTFS_IMPORT_ID_EMPTY'

COMMON_VERIFY_ARGS=(
  --rm
  --network=none
  --read-only
  --cap-drop=ALL
  --security-opt=no-new-privileges
  --mount "type=bind,src=${PACKAGE_DIR},dst=/rei-bootstrap,readonly"
)

set +e
docker run "${COMMON_VERIFY_ARGS[@]}" \
  "$VERIFY_IMAGE_ID" \
  /usr/bin/python3 -I -S -B \
  /rei-bootstrap/verify_candidate.py \
  --contract /rei-bootstrap/CONTRACT.json \
  --rootfs-sha256 "$ROOTFS_SHA256" \
  --builder-image-id "$BUILDER_IMAGE_ID" \
  --builder-image-digests "$BUILDER_IMAGE_DIGESTS" \
  --archive-label "$LABEL" \
  >"$CANDIDATE_RECEIPT.part" 2>"$VERIFY_STDERR"
VERIFY_RC=$?
set -e
[[ "$VERIFY_RC" -eq 0 ]] \
  || stop 'OFFLINE_CANDIDATE_VERIFICATION_FAILED' "rc=$VERIFY_RC" "log=$VERIFY_STDERR"
mv -- "$CANDIDATE_RECEIPT.part" "$CANDIDATE_RECEIPT"
grep -q '"status": "PASS_03A4_HOST_EPOCH_H1_H2_DOCKER_CANDIDATE"' \
  "$CANDIDATE_RECEIPT" \
  || stop 'OFFLINE_CANDIDATE_RECEIPT_STATUS_MISMATCH'

# A second offline/read-only observation records the exact package set.
docker run "${COMMON_VERIFY_ARGS[@]}" \
  "$VERIFY_IMAGE_ID" \
  /usr/bin/dpkg-query -W \
  '-f=${binary:Package}\t${Version}\t${Architecture}\n' \
  | LC_ALL=C sort >"$PACKAGE_MANIFEST" \
  || stop 'PACKAGE_MANIFEST_EMISSION_FAILED'

{
  sha256sum -- "$ROOTFS_TAR"
  sha256sum -- \
    "$BUILD_LOG" \
    "$PULL_LOG" \
    "$BUILDER_INSPECT" \
    "$CANDIDATE_RECEIPT" \
    "$PACKAGE_MANIFEST" \
    "$VERIFY_STDERR"
} >"$RECEIPT_DIR/SHA256SUMS"
sha256sum -c "$RECEIPT_DIR/SHA256SUMS" \
  >"$RECEIPT_DIR/SHA256SUMS.verify"

printf '===== FINAL =====\n'
printf 'classification=PASS_03A4_HOST_EPOCH_H1_H2_DOCKER_CANDIDATE\n'
printf 'authorization_effect=H1_H2_CANDIDATE_ONLY\n'
printf 'candidate_dir=%s\n' "$CANDIDATE_DIR"
printf 'rootfs_archive=%s\n' "$ROOTFS_TAR"
printf 'receipt_dir=%s\n' "$RECEIPT_DIR"
printf 'H3_RUST_CLOSURE_NOT_RUN=1\n'
printf 'SECTION0_NOT_RUN=1\n'
printf 'global_attempt_ref=NOT_CREATED\n'
printf 'local_lease=NOT_CREATED\n'
printf 'native_runtime=NOT_RUN\n'
printf 'remaining_native_attempts=1\n'
printf 'SCIENTIFIC_PASS_NOT_CLAIMED=1\n'
