# Source this file to use the locally installed Rust 1.94.1 toolchain.
export RUST_1_94_1_PREFIX=/mnt/data/rust-1.94.1-prefix
export PATH="$RUST_1_94_1_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$RUST_1_94_1_PREFIX/lib:${LD_LIBRARY_PATH:-}"
