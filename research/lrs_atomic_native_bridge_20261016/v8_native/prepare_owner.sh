#!/usr/bin/env bash
# Usage: prepare_owner.sh REPOSITORY NEW_EMPTY_RUN_DIRECTORY
set -euo pipefail
repo=$1
out=$2
src=$(cd "$(dirname "$0")" && pwd)
owner=6ea2b1b4b3875c9163cafc45efe720afded43fc4
test "$(git -C "$repo" cat-file -t "$owner")" = commit
mkdir "$out" # create-only; an existing run path is an error
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
echo '310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf  '"$out"'/rust/rei_microphysics/src/igm_rates.rs' | sha256sum -c -
cp "$src/native_rrdr.rs" "$out/rust/rei_microphysics/examples/native_rrdr.rs"
cp "$src/run_native.sh" "$out/run_native.sh"
