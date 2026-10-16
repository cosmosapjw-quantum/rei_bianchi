#!/usr/bin/env bash
# Run only inside the staged NCP root containing .venv, rust/, research
# include_str! contracts, and the two lrs_* directories; not repo layout.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
{ hostname; date -u; nproc; free -h; df -h /root; python3 --version;
  /root/.cargo/bin/rustc --version; } > lrs_atomic_native_bridge_20261016/ncp_environment.txt
sha256sum lrs_threshold_oracle_20261015/recomb_thermal.py \
 lrs_atomic_native_bridge_20261016/donor/rate_table.py \
 lrs_atomic_native_bridge_20261016/donor/owner_grackle_rates_129.csv \
 rust/rei_microphysics/src/igm_rates.rs rust/rei_microphysics/src/igm_thermal.rs \
 > lrs_atomic_native_bridge_20261016/ncp_input_sha256.txt
start=$(date +%s%N)
"$root/.venv/bin/python" -m pytest -q \
 lrs_atomic_native_bridge_20261016/test_v5.py \
 lrs_threshold_oracle_20261015/tests/test_recomb_thermal.py \
 > lrs_atomic_native_bridge_20261016/ncp_pytest_stdout.txt 2>&1
"$root/.venv/bin/python" lrs_atomic_native_bridge_20261016/study_v5.py \
 > lrs_atomic_native_bridge_20261016/ncp_study.json 2> lrs_atomic_native_bridge_20261016/ncp_study_stderr.txt
cd rust/rei_microphysics
CARGO_BUILD_JOBS=4 /root/.cargo/bin/cargo build --release --locked --example lrs_v5_native_rates --example lrs_v5_native_point \
 > "$root/lrs_atomic_native_bridge_20261016/ncp_cargo_stdout.txt" \
 2> "$root/lrs_atomic_native_bridge_20261016/ncp_cargo_stderr.txt"
cd ../..
"$root/.venv/bin/python" lrs_atomic_native_bridge_20261016/compare_native.py rust/rei_microphysics \
 > lrs_atomic_native_bridge_20261016/ncp_native_compare_stdout.txt \
 2> lrs_atomic_native_bridge_20261016/ncp_native_compare_stderr.txt
end=$(date +%s%N)
printf 'start_ns=%s\nend_ns=%s\nelapsed_s=%s\nexit=0\n' "$start" "$end" "$(( (end-start)/1000000000 ))" \
 > lrs_atomic_native_bridge_20261016/ncp_exit_receipt.txt
sha256sum lrs_atomic_native_bridge_20261016/ncp_study.json \
 lrs_atomic_native_bridge_20261016/native_comparison.json \
 lrs_atomic_native_bridge_20261016/native_owner_heldout_121.csv \
 lrs_atomic_native_bridge_20261016/native_point_stdout.csv \
 > lrs_atomic_native_bridge_20261016/ncp_output_sha256.txt
