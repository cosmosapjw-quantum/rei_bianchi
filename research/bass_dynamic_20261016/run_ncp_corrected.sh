#!/usr/bin/env bash
set -euo pipefail
export PATH=/root/.cargo/bin:$PATH
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 16777216
root=/root/REI_BASS_DYNAMIC_20261016_001
cd "$root/rust/rei_microphysics"
source_root="$root/research/bass_dynamic_20261016/source_grids/matched_n121_241_481_retry"
while IFS=: read -r case grid dln steps name; do
  dir="$source_root/n$(printf '%04d' "$grid")"
  csv="$dir/PROPOSED_REI_BACKGROUND.csv"
  manifest="$dir/PRODUCER_RECEIPT.json"
  csv_sha=$(sha256sum "$csv"); csv_sha=${csv_sha%% *}
  manifest_sha=$(sha256sum "$manifest"); manifest_sha=${manifest_sha%% *}
  /usr/bin/time -f 'wall_s=%e max_rss_kib=%M user_s=%U system_s=%S exit=%x' -o "$root/${name}.time" \
    timeout 1800 taskset -c 0-3 target/debug/examples/bass_dynamic_trial \
    "$csv" "$manifest" "$csv_sha" "$manifest_sha" "$case" "$grid" "$dln" "$steps" 1 "$root/$name" \
    > "$root/${name}.stdout" 2> "$root/${name}.stderr"
done <<'CASES'
COLD_FLRW:121:0.0001:4:corrected_cold_long_g121
COLD_FLRW:241:0.0001:4:corrected_cold_long_g241
COLD_FLRW:481:0.0001:4:corrected_cold_long_g481
COLD_FLRW:481:0.00005:8:corrected_cold_long_t8
COLD_FLRW:481:0.000025:16:corrected_cold_long_t16
SIGNED_MINUS:121:0.0001:4:corrected_signed_long_g121
SIGNED_MINUS:241:0.0001:4:corrected_signed_long_g241
SIGNED_MINUS:481:0.0001:4:corrected_signed_long_g481
SIGNED_MINUS:481:0.00005:8:corrected_signed_long_t8
SIGNED_MINUS:481:0.000025:16:corrected_signed_long_t16
COLD_FLRW:121:0.0000001:4:corrected_cold_short_g121
COLD_FLRW:241:0.0000001:4:corrected_cold_short_g241
COLD_FLRW:481:0.0000001:4:corrected_cold_short_g481
COLD_FLRW:481:0.00000005:8:corrected_cold_short_t8
COLD_FLRW:481:0.000000025:16:corrected_cold_short_t16
COLD_FLRW:481:0.0000000125:32:corrected_cold_short_t32
SIGNED_MINUS:121:0.0000001:4:corrected_signed_short_g121
SIGNED_MINUS:241:0.0000001:4:corrected_signed_short_g241
SIGNED_MINUS:481:0.0000001:4:corrected_signed_short_g481
SIGNED_MINUS:481:0.00000005:8:corrected_signed_short_t8
SIGNED_MINUS:481:0.000000025:16:corrected_signed_short_t16
SIGNED_MINUS:481:0.0000000125:32:corrected_signed_short_t32
CASES
