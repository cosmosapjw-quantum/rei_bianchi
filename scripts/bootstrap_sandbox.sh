#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'The legacy Python/JAX sandbox is retired for this checkout.' 'For the scoped Rust crate: cargo test --manifest-path rust/rei_microphysics/Cargo.toml --locked' >&2
exit 2
