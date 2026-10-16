#!/usr/bin/env bash
set -u
ROOT=/root/REI_BASS_LONGSTEP_20261016_001
OUT="$ROOT/build_evidence"
if test -d /proc/414741; then echo 'BLOCKED: owner still active' >&2; exit 72; fi
test ! -e "$OUT" || { echo 'create-only build evidence exists' >&2; exit 73; }
mkdir "$OUT"
{ date -u; hostname; nproc; free -b; df -B1 /root; ps -eo pid,psr,%cpu,rss,comm,args --sort=-%cpu | head -20; } > "$OUT/resource_preflight.log"
cd "$ROOT/rust/rei_microphysics" || exit 74
export PATH=/root/.cargo/bin:/usr/bin:/bin
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
printf 'gate,exit_code\n' > "$OUT/exits.csv"
for gate in axbi_bass_dynamic axbi_covariant_transport axbi_driver; do
  /usr/bin/time -f 'wall_s=%e max_rss_kib=%M' -o "$OUT/${gate}.time" \
    timeout 1800 taskset -c 0-3 cargo test --offline --test "$gate" \
    > "$OUT/${gate}.stdout" 2> "$OUT/${gate}.stderr"
  rc=$?
  printf '%s,%s\n' "$gate" "$rc" >> "$OUT/exits.csv"
  if test "$rc" -ne 0; then exit "$rc"; fi
done
/usr/bin/time -f 'wall_s=%e max_rss_kib=%M' -o "$OUT/example.time" \
  timeout 1800 taskset -c 0-3 cargo build --offline --example bass_dynamic_trial \
  > "$OUT/example.stdout" 2> "$OUT/example.stderr"
rc=$?
printf 'example,%s\n' "$rc" >> "$OUT/exits.csv"
exit "$rc"
