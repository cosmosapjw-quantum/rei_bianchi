"""Read-only R10G run audit; no contour or rotation calls."""
import hashlib
import json
import math
import pathlib
import sys

import numpy as np

RUN = pathlib.Path(sys.argv[1])
PACKAGE = pathlib.Path(sys.argv[2])
OUT = pathlib.Path(sys.argv[3])
sys.path.insert(0, str(PACKAGE))
from endpoint_quadrature import nodes, reduce


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


contract = json.loads((PACKAGE / 'CONTRACT.json').read_text())
report = json.loads((RUN / 'RETURN_REPORT.json').read_text())
diag = json.loads((RUN / 'restored/review/FIXED_GK_DIAGNOSTIC.json').read_text())
assert digest(RUN / 'restored/review/EXACT_NODE_TABLE.json') == contract['r10f_exact_table_sha256']
assert digest(RUN / 'restored/review/FIXED_GK_DIAGNOSTIC.json') == digest(PACKAGE / 'fixtures/FIXED_GK_DIAGNOSTIC.json')
assert report['counts']['new_delta_calls'] == 300
assert report['counts']['r10f_exact_reuse'] == 0
assert report['evaluations'] == 60 and report['leaf_count'] == 3
assert report['converged'] and report['stable_confirmation']

cache = sorted((RUN / 'geometry_cache').glob('*.json'))
assert len(cache) == 300
branch_counts = {}
query_by_branch = {}
B = float.fromhex(contract['endpoint_B_hex'])
for path in cache:
    row = json.loads(path.read_text())
    key, record = row['key'], row['record']
    assert hashlib.sha256(canonical(key)).hexdigest() == path.stem
    assert hashlib.sha256(canonical(record)).hexdigest() == row['record_sha256']
    assert key['source'] == contract['scientific_source_sha256']
    assert key['contract'] == digest(PACKAGE / 'CONTRACT.json')
    assert key['environment'] == ['2.3.5', '3.12.3']
    assert key['endpoint_sha256'] == digest(RUN / 'restored/inputs' / ('R10A_EP_' + key['branch'] + '.json'))
    assert key['depth'] == 96 and key['panels'] == 32
    assert record['panels'] == 32 and record['branch'] == key['branch']
    assert key['rho_hex'] == record['rho_hex']
    assert 0 < float.fromhex(key['rho_hex']) < B
    assert math.isfinite(float.fromhex(record['delta_hex'])) and float.fromhex(record['delta_hex']) >= 0
    b = key['branch']
    branch_counts[b] = branch_counts.get(b, 0) + 1
    query_by_branch.setdefault(b, set()).add(key['rho_hex'])
assert len(branch_counts) == 5 and set(branch_counts.values()) == {60}
assert len({frozenset(v) for v in query_by_branch.values()}) == 1

lookup = {}
for path in sorted((RUN / 'integrands').glob('*.json')):
    data = json.loads(path.read_text())
    assert len(data['rho_hex']) == 30 and len(data['components']) == 30
    assert all(len(row) == 90 for row in data['components'])
    lookup.update(zip(data['rho_hex'], data['components']))
assert len(lookup) == 60
assert set(lookup) == next(iter(query_by_branch.values()))

scale = float.fromhex(contract['q_scale_hex'])
intervals = []
for ax, bx in report['q_intervals']:
    a, b = float.fromhex(ax), float.fromhex(bx)
    q = nodes(a, b)
    rho = scale * np.sinh(q)
    values = np.array([lookup[float(x).hex()] for x in rho])
    transformed = (math.pi * scale * scale * np.sinh(2 * q))[:, None] * values
    high, error = reduce(a, b, transformed)
    intervals.append({'q_left_hex': ax, 'q_right_hex': bx, 'high': high.tolist(), 'error': error.tolist()})
assert len(intervals) == 3
hs = np.array(diag['interval_component_high_estimate'])[1:]
es = np.array(diag['interval_component_error_estimate'])[1:]
assert hs.shape == es.shape == (16, 90)
full_high = hs.sum(0) + sum((np.array(x['high']) for x in intervals), np.zeros(90))
full_error = es.sum(0) + sum((np.array(x['error']) for x in intervals), np.zeros(90))
assert np.array_equal(full_high, np.array(report['integral']))
assert np.array_equal(full_error, np.array(report['error_estimate']))
tolerance = np.array(report['tolerance'])
assert tolerance.shape == (90,)
assert np.all(full_error <= tolerance)
rotation = [json.loads(p.read_text()) for p in sorted(RUN.glob('rotation_gate_*.json'))]
assert len(rotation) == 2 and all(r['status'] == 'PASS' and len(r['records']) == 12 for r in rotation)
assert all(x['embedded_pass'] for x in report['history'])
assert report['history'][-1]['max_normalized_change'] <= 0.25

OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'INTERVALS.json').write_text(json.dumps({'new_q_intervals': intervals,
    'old_outside_interval_count': 16, 'old_outside_high_error_content_sha256': hashlib.sha256(canonical({'high': hs.tolist(), 'error': es.tolist()})).hexdigest(),
    'reassembly_max_high_diff': float(np.max(abs(full_high - np.array(report['integral'])))),
    'reassembly_max_error_diff': float(np.max(abs(full_error - np.array(report['error_estimate']))))}, indent=2) + '\n')
validation = {'status': 'READ_ONLY_REASSEMBLY_PASS', 'package_sha256': '90e5b3a0dbecd9fef6ef82f8cbe30f5440cd77796de615e66e66ce6fea40d6ee',
    'r10f_archive_sha256': contract['r10f_archive_sha256'], 'r10f_exact_table_sha256': contract['r10f_exact_table_sha256'],
    'scientific_source_sha256': contract['scientific_source_sha256'], 'python': sys.version.split()[0], 'numpy': np.__version__,
    'rho_evaluations': report['evaluations'], 'new_delta_calls': len(cache), 'r10f_exact_reuse': report['counts']['r10f_exact_reuse'],
    'branch_cache_counts': branch_counts, 'leaf_count': report['leaf_count'], 'outside_intervals_reused': 16,
    'components_pass': int(np.sum(full_error <= tolerance)), 'components_total': 90,
    'max_normalized_embedded': float(np.max(full_error / tolerance)),
    'max_normalized_grid_change': report['history'][-1]['max_normalized_change'],
    'rotation_batches_pass': len(rotation), 'rotation_auditors': sum(len(r['records']) for r in rotation),
    'max_rotation_128_256_difference': max(x['step_max'] for r in rotation for x in r['records']),
    'max_rotation_dop_difference': max(x['dop_difference'] for r in rotation for x in r['records']),
    'r10f_historical_verdict': report['R10F_historical_verdict'],
    'CODE_I02_CLOSED': True, 'full_certificate_fail_closed': True, 'scientific_PROMOTE': 'HOLD',
    'Eq55_next_node_authorized': False, 'Eq55': 'NOT_RUN',
    'claim': 'R10G_LOCAL_ENDPOINT_NUMERICAL_PASS_NOT_GLOBAL_OR_PHYSICAL_CERTIFICATE'}
(OUT / 'VALIDATION.json').write_text(json.dumps(validation, indent=2, sort_keys=True) + '\n')
print(json.dumps(validation, indent=2, sort_keys=True))
