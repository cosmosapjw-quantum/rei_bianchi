#!/usr/bin/env bash
set -eu
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
native=${NATIVE_ROOT:-/tmp/rei-positive-native-intake-20261016/native}
crate="$native/rust/rei_microphysics"
out=${1:-$here/evidence/build}
mkdir -p "$crate/examples" "$out"
cp "$here/matrix_owner.rs" "$crate/examples/matrix_owner.rs"
cp "$here/positive_native.rs" "$crate/examples/positive_native.rs"
python3 "$here/install_accessor.py" "$native"
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 8388608
/usr/bin/time -v -o "$out/build.time" timeout 300s cargo build --release --manifest-path "$crate/Cargo.toml" --example positive_native -j2 > "$out/build.log" 2>&1
