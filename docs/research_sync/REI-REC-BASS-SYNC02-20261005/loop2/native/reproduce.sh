#!/bin/sh
# Builds both exact-source stages; no history is executed by this script.
set -eu
sync_native_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
sync_packet_dir=$(CDPATH= cd -- "$sync_native_dir/../.." && pwd)
sync_rustc=${1:-rustc}
python3 "$sync_packet_dir/loop1/peebles_consumer/build_native.py" \
  --rustc "$sync_rustc" --rec-crate "$sync_packet_dir/source_rec"
python3 "$sync_native_dir/build_native.py" --rustc "$sync_rustc"
