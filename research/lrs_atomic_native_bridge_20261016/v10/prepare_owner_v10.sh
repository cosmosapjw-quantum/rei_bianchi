#!/usr/bin/env bash
# Usage: prepare_owner_v10.sh REI_REPO NEW_EMPTY_OUTPUT_DIR
set -euo pipefail
repo=$1
out=$2
here=$(cd "$(dirname "$0")" && pwd)
owner=6ea2b1b4b3875c9163cafc45efe720afded43fc4
test "$(git -C "$repo" cat-file -t "$owner")" = commit
mkdir "$out" # create-only
git -C "$repo" archive --format=tar "$owner" \
  rust/rei_microphysics \
  docs/fastest_track_chat/REI-AXBI-GOAL-20261014/OUTPUT_CONTRACT.json \
  research/axbi_goal_20261014/scenario/AX05_NUMERICAL_CONTRACT.md \
  research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json \
  research/bass_source007_20261016/CONTRACT.json \
  research/bass_source008_20261016/CONTRACT.json \
  research/flrw_covariant_transport_20261015/BACKGROUND_CACHE_CONTRACT.md \
  research/flrw_covariant_transport_20261015/HPC_CONTRACT.md \
  research/flrw_covariant_transport_20261015/INACTIVE_POOL_CONTRACT.md \
  research/flrw_covariant_transport_20261015/NATIVE_CONTRACT.md \
  research/flrw_covariant_transport_20261015/OUTPUT_ALLOCATION_005_CONTRACT.md \
  research/flrw_jacobian_columns_20261016/CONTRACT.json \
  | tar -xf - -C "$out"
echo "363ab3532db262e869ad481302eb33b7012b51ef7000f956c3081df7836f1d0e  $out/rust/rei_microphysics/src/axbi_driver.rs" | sha256sum -c -
echo "310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf  $out/rust/rei_microphysics/src/igm_rates.rs" | sha256sum -c -
(
  cd "$out"
  patch -p1 < "$here/pr167_driver.patch"
  patch -p1 < "$here/pr167_transport.patch"
)
python3 "$here/prepare_native.py" "$out"
python3 "$here/prepare_controls.py" "$out"
python3 "$here/prepare_rrmp.py" "$out"
python3 "$here/prepare_tight.py" "$out"
cp "$here/native_v10.rs" "$out/rust/rei_microphysics/examples/native_v10.rs"
sha256sum "$out/rust/rei_microphysics/src/axbi_driver.rs" \
  "$out/rust/rei_microphysics/src/axbi_covariant_transport.rs" \
  "$out/rust/rei_microphysics/src/v10_rrmp.rs" \
  "$out/rust/rei_microphysics/examples/native_v10.rs"
