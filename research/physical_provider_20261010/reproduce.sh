#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
task_dir=research/physical_provider_20261010
cargo build --release --locked --manifest-path "$task_dir/native/Cargo.toml"
cargo test --locked --manifest-path "$task_dir/native/Cargo.toml"
python3 -m unittest discover -s "$task_dir" -p test_hm12_data.py -v
python3 "$task_dir/background.py"
# Preserve original band evidence and explicit numerical variants.
python3 "$task_dir/run_interval.py" --emax 200 --tag base
python3 "$task_dir/run_interval.py" --emax 200 --tag tight --rtol 2e-12
python3 "$task_dir/run_interval.py" --emax 200 --tag rk32 --method RK4 --steps 32
python3 "$task_dir/run_interval.py" --emax 200 --tag rk64 --method RK4 --steps 64
python3 "$task_dir/run_interval.py" --emax 200 --tag spectral4 --order 4
python3 "$task_dir/run_interval.py" --emax 200 --tag angular8 --order 4 --nmu 8
python3 "$task_dir/run_interval.py" --emax 200 --tag flrw --shear 0
python3 "$task_dir/run_interval.py" --emax 200 --tag source_off --source-scale 0
# D01 supported-spectrum correction; this is the current candidate.
python3 "$task_dir/run_interval.py" --emax 50000 --tag extended
python3 "$task_dir/run_interval.py" --emax 50000 --tag extended_rk64 --method RK4 --steps 64
python3 "$task_dir/run_interval.py" --emax 50000 --tag extended_refine --order 4 --nmu 8
python3 "$task_dir/audit_inputs.py"
python3 "$task_dir/validate_interval.py"
