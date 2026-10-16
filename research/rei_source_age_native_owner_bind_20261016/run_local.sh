#!/usr/bin/env bash
set -eu
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
crate=${NATIVE_ROOT:-/tmp/rei-source-age-native-owner-bind/native}/rust/rei_microphysics
out=${1:-$here/evidence/local}
mkdir -p "$crate/examples" "$out"
cp "$here/native_owner.rs" "$crate/examples/native_owner.rs"
cp "$here/source_reference.rs" "$crate/examples/source_reference.rs"
python3 "$here/install_accessor.py" "$(cd "$crate/../.." && pwd)"
cp "$here/campaign.rs" "$crate/examples/source_age_campaign.rs"
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 8388608
/usr/bin/time -v -o "$out/build.time" timeout 300s cargo build --release --manifest-path "$crate/Cargo.toml" --example source_age_campaign -j2 > "$out/build.log" 2>&1
/usr/bin/time -v -o "$out/run.time" timeout 300s "$crate/target/release/examples/source_age_campaign" "$out" > "$out/stdout.log" 2> "$out/stderr.log"
