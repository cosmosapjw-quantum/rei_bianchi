"""Read-only receipt reconciliation; does not execute the scientific solver."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text())


def verify():
    scope = read('SCOPE.json')
    previous = ROOT.parent / 'production_solver_20261001_v1'
    rows = scope['old_production_source_inventory']
    for row in rows:
        p = previous / row['path']
        assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], row['path']
    central_paths = ['runtime/pilots_baseline/CENTRAL.json',
                     'runtime/pilots_cached/CENTRAL.json',
                     'runtime/pilots_refined_cached/CENTRAL.json']
    central = [read(p) for p in central_paths]
    numerical = ['rectangle', 'dispatched_evaluations', 'integration_calls',
                 'callback_calls', 'callback_refusals', 'analytic_box_refusals']
    for result in central:
        assert result['accepted'] is True and result['status'] == 'RADIUS_MET'
        assert result['index'] == 0 and result['precision_bits'] == 128
        assert result['accepted_component_radius_exp'] == -48
        assert result['scientific_admission'] is False and result['production_admission'] is False
        assert all(result[key] == central[0][key] for key in numerical)
        for part in result['rectangle'].values():
            radius = Fraction(int(part['upper_mantissa']) - int(part['lower_mantissa']), 2)
            radius *= Fraction(2) ** int(part['exponent2'])
            assert 0 <= radius <= Fraction(2) ** -48
    rejection_path = 'runtime/pilots_refined_cached/W1.json'
    rejection = read(rejection_path)
    native = json.loads(rejection['native_stdout'])
    assert rejection['accepted'] is False and rejection['returncode'] == 2
    assert native['status'] == 'INTEGRATOR_NO_CONVERGENCE' and native['rectangle'] is None
    assert native['dispatched_evaluations'] == 11771 and native['integration_calls'] == 126
    assert rejection['native_limits'] == central[-1]['wrapper']['native_limits']
    return {
        'schema': 'WU088_NATIVE_CONTINUATION_RECONCILIATION_V1',
        'status': 'SCOPED_RECEIPTS_AND_OLD_SOURCE_PRESERVATION_PASS',
        'base_commit': scope['base_commit'],
        'old_production_files_unchanged': len(rows),
        'actual_primitive_integral_executions_this_continuation': 4,
        'accepted_executions': 3,
        'accepted_unique_primitive_indices': [0],
        'accepted_unique_windows': [{'l_t': '1', 'T_t': '2', 'l_u': '1', 'T_u': '2'}],
        'accepted_rectangles_and_counters_exactly_equal': True,
        'accepted_precision_bits': 128,
        'accepted_component_radius_exp': -48,
        'wide_W1_rejected': True,
        'wide_W1_status': native['status'],
        'wide_W1_evaluations': native['dispatched_evaluations'],
        'wide_W1_integration_calls': native['integration_calls'],
        'complete_2592_primitive_coverage': False,
        'endpoint_included_in_accepted_integrals': False,
        'full_domain_integral': False,
        'actual_final_D_assembled': False,
        'NCP64_runtime_verified': False,
        'scientific_admission': False,
        'production_admission': False,
        'receipt_sha256': {p: sha(ROOT / p) for p in central_paths + [rejection_path]},
        'verification_does_not_rerun_solver': True,
        'limitation': 'Exact arithmetic and byte checks on source-bound receipts; not a second independent numerical solver.'
    }


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
