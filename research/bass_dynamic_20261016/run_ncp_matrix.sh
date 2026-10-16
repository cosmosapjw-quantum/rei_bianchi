#!/usr/bin/env bash
set -euo pipefail
export PATH=/root/.cargo/bin:$PATH
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
export CARGO_BUILD_JOBS=4
ulimit -v 16777216
root=/root/REI_BASS_DYNAMIC_20261016_001
cd "$root/rust/rei_microphysics"
bin=target/debug/examples/bass_dynamic_trial
source_root="$root/research/bass_dynamic_20261016/source_grids/matched_n121_241_481_retry"
run_one() {
  local grid="$1" case="$2" dln="$3" steps="$4" workers="$5" name="$6"
  local dir="$source_root/n$(printf '%04d' "$grid")"
  local csv="$dir/PROPOSED_REI_BACKGROUND.csv" manifest="$dir/PRODUCER_RECEIPT.json"
  local csv_sha manifest_sha
  csv_sha=$(sha256sum "$csv"); csv_sha=${csv_sha%% *}
  manifest_sha=$(sha256sum "$manifest"); manifest_sha=${manifest_sha%% *}
  /usr/bin/time -f 'wall_s=%e max_rss_kib=%M user_s=%U system_s=%S exit=%x' -o "$root/${name}.time" \
    timeout 1800 taskset -c 0-15 "$bin" "$csv" "$manifest" "$csv_sha" "$manifest_sha" \
    "$case" "$grid" "$dln" "$steps" "$workers" "$root/$name" > "$root/${name}.stdout" 2> "$root/${name}.stderr"
}
run_one 121 COLD_FLRW 0.0001 4 1 cold121_w1
run_one 121 COLD_FLRW 0.0001 4 2 cold121_w2
run_one 121 COLD_FLRW 0.0001 4 4 cold121_w4
run_one 241 COLD_FLRW 0.0001 4 1 cold241_dt100
run_one 481 COLD_FLRW 0.0001 4 1 cold481_dt100
run_one 481 COLD_FLRW 0.00005 8 1 cold481_dt50
run_one 481 COLD_FLRW 0.000025 16 1 cold481_dt25
run_one 121 SIGNED_MINUS 0.0001 4 1 signed121_dt100
run_one 241 SIGNED_MINUS 0.0001 4 1 signed241_dt100
run_one 481 SIGNED_MINUS 0.0001 4 1 signed481_dt100
run_one 481 SIGNED_MINUS 0.00005 8 1 signed481_dt50
