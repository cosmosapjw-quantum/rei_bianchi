"""Independent read-only arithmetic on saved endpoint evidence.

No consumer, provider function, source test suite, quadrature or solver import.
The only third-party use is NumPy's immutable NPZ reader.
"""
import hashlib
import json
import math
import pathlib
import resource
import time
import zipfile

import numpy as np

BASE = pathlib.Path('/workspace/scratch/9d364a030876')
ROOT = BASE / 'release/research/rei_expanded_event_consumer/grid044_endpoint_20261025'
OUT = BASE / 'rei_review/FINAL_REVIEW_ARITHMETIC.json'
start = time.monotonic()
before = resource.getrusage(resource.RUSAGE_SELF)
read = lambda name: json.loads((ROOT / name).read_text())
result = read('results.json')
binding = read('ACTUAL_STATE_BINDING.json')
supplied = read('SOURCE_ABSORBER_MATRIX.json')
payload = read('inputs/AGGREGATE_PAYLOAD.json')
manifest = read('SOURCE_MANIFEST.json')

identities = []
with zipfile.ZipFile(BASE / 'grid044_intake/OPACITY_FINAL_20261025.zip') as archive:
    for row in manifest['files']:
        actual = (ROOT / row['path']).read_bytes()
        provenance = row['source']
        if 'archive_member' in provenance:
            original = archive.read(provenance['archive_member'])
        else:
            original = (BASE / 'supplier_intake' / provenance['repo'] / provenance['path']).read_bytes()
        item = {'path': row['path'], 'bytes': len(actual),
                'sha256': hashlib.sha256(actual).hexdigest(),
                'original_bytes_equal': actual == original,
                'manifest_identity_equal': len(actual) == row['bytes'] and hashlib.sha256(actual).hexdigest() == row['sha256']}
        assert item['original_bytes_equal'] and item['manifest_identity_equal'], item
        identities.append(item)

labels = ('n', 'H1_0', 'H1_1', 'D_0', 'D_1', 'T_0', 'T_1',
          'He3_0', 'He3_1', 'He3_2', 'He4_0', 'He4_1', 'He4_2',
          'Li6_0', 'Li6_1', 'Li6_2', 'Li6_3', 'Li7_0', 'Li7_1', 'Li7_2', 'Li7_3')
assert tuple(result['species']) == labels
with np.load(ROOT / 'inputs/grid044_history.npz', allow_pickle=False) as npz:
    original_labels = tuple(npz['atomic_state_labels'].tolist())
    saved_x = npz['atomic_abundance_per_Href'][:, -1].tolist()
    x = [saved_x[original_labels.index(label)] for label in labels]
    assert x == result['x'] == binding['actual_abundance_per_ref']
    assert binding['reference']['a'] == float(npz['a'][-1])
assert [labels[i] for i, value in enumerate(x) if value == 0] == ['n', 'T_0', 'T_1']

rates = payload['rates_per_source_target']
assert rates == result['saved_rates_per_source_target']
thresholds = [13.60, 24.59, 54.42, 5.392, 75.64, 122.5]
assert payload['thresholds_eV'] == thresholds
edges = []
for lower, label in enumerate(labels):
    if label == 'n':
        continue
    isotope, charge = label.split('_')
    successor = isotope + '_' + str(int(charge) + 1)
    if successor in labels:
        channel = 0 if isotope in ('H1', 'D', 'T') else (1 if isotope.startswith('He') else 3) + int(charge)
        edges.append((lower, labels.index(successor), channel))
assert len(edges) == 13

f_terms = [[] for _ in range(25)]
j_terms = [[[] for _ in range(23)] for _ in range(25)]
source_scales = [0.0] * 22
independent_contributions = []
ev_to_j = 1.602176634e-19
r = payload['nHref_m3']
for lower, upper, channel in edges:
    for si, source in enumerate(('stellar', 'external_IGM')):
        gamma, power, kinetic = rates[si][channel]
        column = {lower: -gamma, upper: gamma, 21: gamma,
                  22: -power, 23: thresholds[channel] * gamma, 24: kinetic}
        for output, coefficient in column.items():
            f_terms[output].append(x[lower] * coefficient)
            j_terms[output][lower].append(coefficient)
            j_terms[output][21 + si].append(x[lower] * coefficient)
            if output < 22:
                source_scales[output] += abs(x[lower] * coefficient)
        independent_contributions.append({
            'event_id': 'photo:' + labels[lower] + '->' + labels[upper],
            'source': source, 'event_rate': x[lower] * gamma,
            'signed_energy': [x[lower] * column[i] for i in (22, 23, 24)]})

f = [math.fsum(values) for values in f_terms]
jacobian = [[math.fsum(values) for values in row] for row in j_terms]
j_scales = [max(abs(value) for value in row) for row in jacobian]
energy_scales = [math.fsum(abs(value) for value in f_terms[i]) for i in (22, 23, 24)]
f_scales = source_scales + energy_scales

def scaled(actual, expected, scales):
    values = []
    for a, b, scale in zip(actual, expected, scales):
        if scale == 0:
            assert a == b
            values.append(0.0)
        else:
            values.append(abs(a - b) / scale)
    return max(values)

def matrix_scaled(actual, expected, scales):
    return max(scaled(a, b, [scale] * len(b)) for a, b, scale in zip(actual, expected, scales))

metrics = {
    'REC_output_25_vs_independent_saved_moment_sum': scaled(result['rec_output_25'], f, f_scales),
    'WU_source_22_vs_independent_saved_moment_sum': scaled(result['wu_source_22'], f[:22], source_scales),
    'REC_J_25x23_vs_independent_coefficients': matrix_scaled(result['rec_jacobian_25_by_23'], jacobian, j_scales),
    'complex_step_J_25x23_vs_independent_coefficients': matrix_scaled(result['complex_step_Jacobian_raw'], jacobian, j_scales),
    'Rust_rhs_21_vs_independent_saved_moment_sum': scaled(result['rust']['raw']['actual_rhs'], f[:21], source_scales[:21]),
    'Rust_J_21x21_vs_independent_coefficients': matrix_scaled(result['rust']['raw']['actual_jacobian'], [row[:21] for row in jacobian[:21]], j_scales[:21]),
}
for value in metrics.values():
    assert value <= 3e-13
assert len(supplied['source_contributions']) == 26
for independently, actual in zip(independent_contributions, supplied['source_contributions']):
    assert independently['event_id'] == actual['event_id'] and independently['source'] == actual['source']
    assert independently['signed_energy'] == actual['energy_eV_per_ref_s']
    expected_rate = independently['event_rate']
    if expected_rate:
        assert abs(actual['event_rate_per_ref_s'] / expected_rate - 1) < 3e-15
    else:
        assert actual['event_rate_per_ref_s'] == 0

balance_scaled = []
for item in independent_contributions:
    powers = item['signed_energy']
    denominator = math.fsum(abs(value) for value in powers)
    balance_scaled.append(abs(math.fsum(powers)) / denominator if denominator else 0.0)
metrics['independent_collision_energy_components'] = max(balance_scaled)
assert metrics['independent_collision_energy_components'] < 3e-12
primary_number = f[21]
number_by_source = {source: math.fsum(row['event_rate'] for row in independent_contributions if row['source'] == source) for source in ('stellar', 'external_IGM')}

raw = result['rust']['raw']
wrong_j_error = matrix_scaled(raw['wrong_finite_jacobian'], [row[:21] for row in jacobian[:21]], j_scales[:21])
assert raw['wrong_finite_jacobian_gate_admitted'] and abs(wrong_j_error - 0.5) < 1e-15
assert all(raw[key] for key in ('negative_state_rejected', 'outside_time_rejected', 'outside_upper_rejected', 'time_derivative_stencil_rejected'))
assert raw['rhs_calls'] == raw['jac_calls'] == raw['pairs'] == 4

control = result['normalization_controls']
reference_f = [(s - xx * control['R']) / control['r'] for xx, s in zip(control['x'], control['S'])]
reference_df = [(ds - control['R'] * dx - xx * control['dR']) / control['r'] - ff * control['dr'] / control['r']
                for ds, dx, xx, ff in zip(control['dS'], control['dx'], control['x'], reference_f)]
assert all(abs(a-b) < 1e-16 for a,b in zip(reference_df, control['computed_derivative']))
assert control['omitted_density_derivative_quotient_mutation_row_scaled'] > 0.2

snapshots = {}
for name in ('consumer.py', 'test_consumer.py', 'write_rust_client.py', 'render_sources.py',
             'results.json', 'SOURCE_ABSORBER_MATRIX.json', 'ACTUAL_STATE_BINDING.json',
             'SOURCE_MANIFEST.json', 'HE_RECEIVER_INPUT.json', 'BASS_INPUT_JOIN.json',
             'VIGILODE_CLIENT_CONTRACT.json', 'rust/client.rs',
             'figures/GRID044_ACTUAL_ENDPOINT_SOURCES.png'):
    data = (ROOT / name).read_bytes()
    snapshots[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
after = resource.getrusage(resource.RUSAGE_SELF)
report = {
    'reviewer': '/root/supplier_intake', 'status': 'PASS_SCOPED_SAVED_EVIDENCE_ARITHMETIC',
    'mode': 'read immutable bytes and saved data; no reused scientific function, suite or solver import/call',
    'immutable_source_identity_count': len(identities), 'identities': identities,
    'actual_state_selection': 'atomic_abundance_per_Href[:, -1], mapped by exact labels',
    'actual_zero_labels': ['n', 'T_0', 'T_1'], 'event_count': len(edges), 'source_contributions': len(independent_contributions),
    'metrics': metrics, 'source_scaling': 'sum absolute independent event contributions, no unit floor',
    'jacobian_scaling': 'max absolute independent row coefficient across 23 columns; exact-zero row rule',
    'primary_electron_number_per_ref_s': primary_number,
    'primary_electron_number_m3_s': primary_number * r,
    'number_by_source_per_ref_s': number_by_source,
    'signed_energy_eV_per_ref_s': f[22:25],
    'signed_energy_J_m3_s': [value * r * ev_to_j for value in f[22:25]],
    'wrong_finite_J_row_scaled': wrong_j_error,
    'normalization_directional_algebra': 'matches saved helper; source and derivative quotient omission controls present',
    'scientific_provider_runs': 0, 'new_opacity_integrals': 0, 'new_IVPs': 0,
    'viewed_png': True, 'image_review': 'actual zero label, signs, source legend, units and scope visibly retained',
    'snapshots': snapshots,
    'arithmetic_loop_observed_cpu_s': after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
    'arithmetic_loop_observed_wall_s': time.monotonic()-start,
    'timing_scope': 'starts after Python/NumPy import; startup and review reading/image overhead unmeasured, not zero'}
OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
print(json.dumps({key: report[key] for key in ('status','immutable_source_identity_count','metrics','primary_electron_number_per_ref_s','primary_electron_number_m3_s','number_by_source_per_ref_s','signed_energy_J_m3_s','arithmetic_loop_observed_cpu_s','arithmetic_loop_observed_wall_s')}, indent=2))
