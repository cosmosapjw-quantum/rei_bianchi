#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)";cd "$ROOT"
if [[ -n "${RUST_BIN:-}" ]];then export PATH="$RUST_BIN:$PATH";fi
export CARGO_BUILD_JOBS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
M=code/rei_bass_coupled/Cargo.toml
case "${1:-verify}" in
verify) sha256sum -c SHA256SUMS.txt;;
build) rustc --version; cargo build --release --offline --locked --manifest-path "$M" --example gas_rhs_server --example spectral_edge_server --example spectral_scalar_probe;;
tests) cargo test --offline --locked --all-targets --manifest-path "$M"; (cd scripts;python -m unittest test_spectral11 test_retarded -v);;
lint) cargo clippy --offline --locked --all-targets --manifest-path "$M" -- -D warnings;rustfmt --check --edition 2024 code/rei_bass_coupled/src/spectral_edge_support.rs code/rei_bass_coupled/src/spectral_native.rs code/rei_bass_coupled/tests/spectral_native.rs code/rei_bass_coupled/examples/spectral_edge_server.rs code/rei_bass_coupled/examples/spectral_scalar_probe.rs;;
baseline|tail) python scripts/replay11.py "$1";;
*) echo 'Use separate bounded calls: verify|build|tests|lint|baseline|tail' >&2;exit 2;;
esac
