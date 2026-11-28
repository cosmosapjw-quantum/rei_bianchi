#!/usr/bin/env bash
# Run this ONLY inside a new isolated /root/wu088_hh_phys53_XXXXXXXX directory.
# All computations are CENTRAL_COULOMB_REFERENCE_ONLY, not screened H-H production.
set -Eeuo pipefail
umask 077
[[ $# -eq 1 ]] || { echo 'usage: worker_on_ncp.sh ABSOLUTE_ISOLATED_DIR' >&2; exit 2; }
WORK="$1"
[[ "$WORK" =~ ^/root/wu088_hh_phys53_[A-Za-z0-9]{8}$ ]] || { echo 'unsafe remote workdir' >&2; exit 2; }
[[ -f "$WORK/phys53_coulomb_cf.rs" ]] || { echo 'missing Rust source' >&2; exit 2; }
[[ -e "$HOME/.cargo/env" ]] && . "$HOME/.cargo/env"
command -v rustc >/dev/null
command -v cargo >/dev/null
[[ "$(nproc)" -ge 8 ]] || { echo 'fewer than 8 NCP CPUs available' >&2; exit 2; }
[[ -x /usr/bin/time ]] || { echo '/usr/bin/time unavailable: benchmark NOT_RUN' >&2; exit 2; }
cd "$WORK"
mkdir -p results
{
  printf 'date_utc='; date -u +%FT%TZ
  printf 'hostname='; hostname
  printf 'nproc='; nproc
  printf 'available_ram='; free -h | sed -n '2p'
  printf 'loadavg='; cat /proc/loadavg
  printf 'rustc='; rustc --version
  printf 'cargo='; cargo --version
  printf 'kernel='; uname -sr
  printf 'rust_source_sha256='; sha256sum phys53_coulomb_cf.rs
} > results/ENVIRONMENT.txt

# Constrain CPU/memory and never kill other existing processes.
ulimit -v 16777216  # 16 GiB virtual address limit, far below 125 GiB NCP RAM
export RUST_BACKTRACE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
/usr/bin/time -f 'wall_s=%e\npeak_rss_KiB=%M' -o results/COMPILER.time \
  rustc --edition=2021 -C opt-level=3 phys53_coulomb_cf.rs -o phys53_cf
rustc --edition=2021 --test -C opt-level=2 phys53_coulomb_cf.rs -o phys53_cf_tests
./phys53_cf_tests --nocapture > results/RUST_UNIT_TEST.stdout 2> results/RUST_UNIT_TEST.stderr
printf '%s\n' 0 > results/RUST_UNIT_TEST.exit
sha256sum phys53_cf phys53_cf_tests > results/BINARIES.sha256

run_one() {
  local first="$1" last="$2" radius="$3" depth="$4" workers="$5" prefix="$6"
  # Every calculation is synchronous with explicit bounded elapsed time.
  timeout --signal=TERM --kill-after=5s 180s nice -n 10 \
    /usr/bin/time -f 'wall_s=%e\npeak_rss_KiB=%M' -o "results/$prefix.time" \
    ./phys53_cf "$first" "$last" "$radius" "$depth" "$workers" \
    > "results/$prefix.csv" 2> "results/$prefix.stderr"
}

# Scientific reference sweep: exactly comparable serial/depth/parallel paths.
for r in 27 30 43; do
  run_one 21 256 "$r" 768 1 "ref_r${r}_d768_w1"
  run_one 21 256 "$r" 1152 1 "ref_r${r}_d1152_w1"
  run_one 21 256 "$r" 1152 8 "ref_r${r}_d1152_w8"
done

# Matched-output benchmark: 3 repeats each, four worker counts. No promise of speedup.
for w in 1 2 4 8; do
  for rep in 1 2 3; do
    run_one 21 4096 27 2048 "$w" "bench_r27_d2048_w${w}_rep${rep}"
  done
done

# Integrity of every returned scientific and execution file.
(cd results && sha256sum -- *.csv *.time *.stderr RUST_UNIT_TEST.stdout RUST_UNIT_TEST.stderr \
  RUST_UNIT_TEST.exit ENVIRONMENT.txt BINARIES.sha256 COMPILER.time > FILES.sha256)
tar -czf "$WORK/RESULTS.tar.gz" -C results .
(cd "$WORK" && sha256sum RESULTS.tar.gz > RESULTS.tar.gz.sha256)
echo "NCP_PAYLOAD_READY $WORK/RESULTS.tar.gz"
