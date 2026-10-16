#!/usr/bin/env bash
set -euo pipefail
base=$(cd "$(dirname "$0")" && pwd)
bin="$base/rust/rei_microphysics/target/release/examples/native_rrdr"
mkdir -p "$base/results/native"
cases=(
  'D1_X1e-5_T15000 1e-5 1 15000'
  'D100_X002_T15000 0.002 100 15000'
  'D1000_X002_T15000 0.002 1000 15000'
  'D10000_X0003_T15000 0.0003 10000 15000'
  'D1000_X002_T22000 0.002 1000 22000'
  'D1e6_X0001_T15000 0.0001 1000000 15000'
)
for spec in "${cases[@]}"; do
  read -r name span density temperature <<< "$spec"
  for n in 8 16 32 64 128; do
    stem="$base/results/native/${name}_N${n}"
    /usr/bin/time -f 'exit=%x wall_s=%e user_s=%U system_s=%S max_rss_kib=%M' \
      -o "$stem.time" "$bin" "$n" "$span" "$density" "$temperature" \
      > "$stem.csv" 2> "$stem.stderr"
  done
done
