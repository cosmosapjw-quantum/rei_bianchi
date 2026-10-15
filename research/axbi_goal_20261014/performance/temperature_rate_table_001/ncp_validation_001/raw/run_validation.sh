#!/usr/bin/env bash
set -u
ncp_root=/root/REI_AXBI_GOAL_20261014_32d11e733155/performance/temperature_rate_table_001/ncp_validation_001
ncp_task="$ncp_root/stage/research/axbi_goal_20261014/performance/temperature_rate_table_001"
cd "$ncp_root" || exit 98
export RUSTC="$ncp_root/toolchain/bin/rustc"
export RUSTDOC="$ncp_root/toolchain/bin/rustdoc"
export CARGO_BUILD_JOBS=1
export CARGO_TARGET_DIR="$ncp_root/target"
export RUSTFLAGS='-C link-arg=-Wl,--threads=1'
export PATH="$ncp_root/toolchain/bin:$PATH"
export LD_LIBRARY_PATH="$ncp_root/toolchain/lib"
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
/usr/bin/time -v -o "$ncp_root/raw/validation_time.log" /usr/bin/timeout --foreground --signal=KILL 599s /usr/bin/taskset -c 0 /usr/bin/prlimit --as=2147483648 -- "$ncp_root/toolchain/bin/cargo" test --release --locked --offline --manifest-path "$ncp_task/Cargo.toml" --test temperature_tables -- --test-threads=1 --nocapture > "$ncp_root/raw/cargo.stdout" 2> "$ncp_root/raw/cargo.stderr"
ncp_code=$?
printf '%s\n' "$ncp_code" > "$ncp_root/raw/exit_code.txt"
exit "$ncp_code"
