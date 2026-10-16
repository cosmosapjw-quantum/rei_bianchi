#!/usr/bin/env bash
set -u
ROOT=/root/REI_BASS_LONGSTEP_20261016_001
CRATE="$ROOT/rust/rei_microphysics"
GRID="$ROOT/research/bass_dynamic_20261016/source_grids/matched_n121_241_481_retry/n0481"
OUT="$ROOT/ultrafine_probe"
test ! -e "$OUT" || { echo 'create-only ultrafine output exists' >&2; exit 73; }
if pgrep -f 't4_spectral.py __worker' >/dev/null; then echo 'BLOCKED: REI owner active' >&2; exit 72; fi
mkdir "$OUT"
{ date -u; hostname; free -b; df -B1 /root; ps -eo pid,psr,%cpu,rss,args --sort=-%cpu | head -25; } > "$OUT/resource_preflight.log"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
export BASS_OPTICAL_DETAIL=0 BASS_EXACT_ENDPOINT=1 BASS_TOTAL_DLNA=4e-4
CSV="$GRID/PROPOSED_REI_BACKGROUND.csv"
MANIFEST="$GRID/PRODUCER_RECEIPT.json"
CSHA=1104845a34658b7c99ba4d7731a955c11457cf5c9ab92b1cf49117de462b663f
MSHA=32b9690e3842c5eeeb64e453fabc1895ab6bf5e27678975521e9f945dc5cc67e
test "$(sha256sum "$CSV" | cut -d' ' -f1)" = "$CSHA" || exit 74
test "$(sha256sum "$MANIFEST" | cut -d' ' -f1)" = "$MSHA" || exit 75
printf 'mode,case,steps,exit_code\n' > "$OUT/exits.csv"
for mode in legacy_trace uniform_birth; do
  for case in COLD_FLRW SIGNED_MINUS; do
    steps=2048
    if pgrep -f 't4_spectral.py __worker' >/dev/null; then echo 'BLOCKED: REI owner returned' >&2; exit 72; fi
    if test "$(du -sm "$ROOT" | cut -f1)" -gt 3900; then echo 'BLOCKED: disk cap' >&2; exit 76; fi
    dir="$OUT/${mode}_${case}_${steps}"
    mkdir "$dir" || exit 77
    dln=$(python3 -c "print(repr(0.0004/$steps))")
    export BASS_NUMERICS="$mode"
    /usr/bin/time -f 'wall_s=%e max_rss_kib=%M' -o "$dir/time.txt" \
      timeout 1800 taskset -c 4-7 "$CRATE/target/debug/examples/bass_dynamic_trial.reference_cap_repair" \
      "$CSV" "$MANIFEST" "$CSHA" "$MSHA" "$case" 481 "$dln" "$steps" 1 \
      "$dir/output" > "$dir/stdout.log" 2> "$dir/stderr.log"
    rc=$?
    printf '%s,%s,%s,%s\n' "$mode" "$case" "$steps" "$rc" >> "$OUT/exits.csv"
  done
done
