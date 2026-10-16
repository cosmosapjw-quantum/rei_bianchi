"""New binding/serialization controls only; no oracle or actual-stage solve."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

unit = Path(__file__).resolve().parents[1]
root = unit.parents[1]
out = Path(sys.argv[1])
summary = json.loads((out / 'SUMMARY.json').read_text())
packets = [json.loads(p.read_text()) for p in sorted(out.glob('stage-*.json'))]
assert len(packets) == summary['packets'] == 2
assert summary['attempts'] == 6 and summary['successes'] == 4
assert summary['max_packets'] <= 6 and summary['max_rhs'] <= 48
assert summary['parallel_policy'] == 'SERIAL_NO_SPECULATIVE_RESERVATIONS'
assert all(p['input_kind'] == 'SYNTHETIC_FIXTURE' for p in packets)
assert all(p['observer_parallel_policy'] == 'SERIAL_NO_SPECULATIVE_RESERVATIONS' for p in packets)
first, missing = packets
assert first['state'] == first['residual_evaluation_state'] == first['jacobian_evaluation_state']
assert first['context_id'] == first['prepared_context_id'] == first['residual_context_id'] == first['jacobian_context_id']
assert first['trajectory_role'] == 'FINAL_TRAJECTORY_HALF_SECOND'
assert missing['jacobian'] is None and missing['jacobian_evaluation_state'] is None
assert missing['jacobian_context_id'] is None and missing['unavailable_reason'].startswith('HOLD_')
assert missing['adaptive_status'] == 'ABORTED'
assert missing['trajectory_role'] == 'DISCARDED_TRIAL'
assert all(e['elapsed_seconds'] >= 0 for p in packets for e in p['evaluations'])
driver = root / 'rust/rei_microphysics/src/axbi_driver.rs'
blob = subprocess.check_output(['git', 'hash-object', str(driver)], text=True).strip()
assert all(p['driver_blob_sha'] == blob for p in packets)
module_path = unit / 'vendor/nonlinear_budget.py'
spec = importlib.util.spec_from_file_location('bounded_migrated_adapter', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.DRIVER_BLOB == blob
assert module.LOCAL_TARGET == 1e-5 and module.NEWTON_THRESHOLD == 1e-11
# Negative guard only: never solve a fabricated ACTUAL_STAGE packet.
for wrong in ['2a16fa8d898588d859eff2c7750a5f8496cadd0c',
              '651e48c9684f0735a0d597cb860d6428a05d8369', '0'*40]:
    guard = dict(first, input_kind='ACTUAL_STAGE', driver_blob_sha=wrong)
    answer = module.analyze_stage(guard)
    assert answer['status'] == 'HOLD' and answer['reason'] == 'HOLD_SOURCE_BINDING_MISMATCH', answer
    assert answer['metrics'] is None
original = Path('/root/flrw-observer-intake-20261016/payload/research/flrw_nonlinear_error_budget_20261016/nonlinear_budget.py')
if original.exists():
    expected = original.read_text().replace("DRIVER_BLOB = '2a16fa8d898588d859eff2c7750a5f8496cadd0c'", f"DRIVER_BLOB = '{blob}'")
    assert module_path.read_text() == expected
print(json.dumps({'status': 'PASS_SYNTHETIC_SERIALIZATION_AND_BINDING_CONTROLS',
                  'producer_blob': blob, 'actual_stage_solves': 0}))
