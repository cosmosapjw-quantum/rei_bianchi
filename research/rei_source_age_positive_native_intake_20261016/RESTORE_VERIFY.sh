#!/usr/bin/env bash
set -eu
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
research="$root/research/rei_source_age_positive_native_intake_20261016"
native="$root/native_source"
out="$root/replay"
mkdir -p "$out"
NATIVE_ROOT="$native" bash "$research/build.sh" "$out/build"
binary="$native/rust/rei_microphysics/target/release/examples/positive_native"
mkdir -p "$out/q0"
cp "$research/evidence/q0/first_failed_state_event2_retry0.npy" "$out/q0/"
python3 "$research/test_positive_coordinates.py" "$binary" "$out/coordinate_tests"
python3 "$research/positive_solver.py" "$binary" "$out/q0" --q 0
python3 "$research/positive_solver.py" "$binary" "$out/age16" --q 0 --birth-panels 16
python3 - "$research/evidence/matrix/age16/endpoint.json" "$out/age16/endpoint.json" <<'PY'
import json,sys
reference, replay = (json.load(open(path)) for path in sys.argv[1:])
for key in ('N', 'U', 'Gamma_s', 'heat_erg_per_absorber_s'):
    expected, actual = reference[key], replay[key]
    if not isinstance(expected, list):
        expected, actual = [expected], [actual]
    for x,y in zip(expected, actual):
        assert abs(x-y) <= 1e-8 * max(abs(x), abs(y), 1e-300), (key,x,y)
print('fresh age16 source-matched observables: PASS')
PY
