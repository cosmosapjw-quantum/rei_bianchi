"""Administrative serialization of manually authored inputs, not science.

Reads fixed rational text and metadata, expands literal repeated triplets,
attaches explicit synthetic declarations, and hashes JSON bytes. It imports
no production/reference/predecessor module and performs no solver or proof
evaluation. Scientific fixture controls are manually authored, not computed
by the implementation under test.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = HERE / 'verification'
definitions = json.loads((V / 'FIXTURE_DEFINITIONS.json').read_text())
fields = ('id', 'states', 'q', 'tau', 'c', 'd', 'initial', 'source_knots', 'observation_knots', 'g_r', 'g_e')
cases, identities = [], {}
for item in definitions['cases']:
    case = deepcopy(definitions['defaults'])
    case.update(deepcopy(item))
    repeated = case.pop('repeat_source_triplets', None)
    if repeated:
        for name in ('g_r', 'g_e'):
            case[name] = [deepcopy(repeated[name]) for _ in range(repeated['count'])]
    binding = {'source_id': 'R14_SYNTHETIC_' + case['id'],
               'clock_id': 'synthetic-normalized-clock', 'clock_unit': 'normalized_time',
               'full_A_family_id': 'conditional-full-A-fixture',
               'state_order': ['s' + str(i) for i in range(case['states'])],
               'source_locator': 'verification/FIXTURE_SOURCE.json',
               'scientific_status': 'ARITHMETIC_CONTROL_PREMISE',
               'whole_forcing_hash_format': 'WU_R14_WHOLE_FORCING_V1'}
    payload = {'schema': 'WU_R14_WHOLE_FORCING_V1',
               **{k: binding[k] for k in ('source_id', 'clock_id', 'clock_unit', 'state_order')},
               'source_knots': case['source_knots'], 'g_r': case['g_r'], 'g_e': case['g_e']}
    encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()
    binding['whole_forcing_source_sha256'] = hashlib.sha256(encoded).hexdigest()
    identities[case['id']] = binding['whole_forcing_source_sha256']
    case['binding'] = binding
    cases.append(case)
source = {'schema': 'WU_R14_ORIGINAL_SYNTHETIC_FIXTURE_SOURCE_V1',
          'scientific_status': 'ARITHMETIC_CONTROL_PREMISE',
          'actual_HD_array': False, 'named_physical_consumer': False,
          'whole_forcing_identities': identities,
          'cases': [{k: case[k] for k in fields} for case in cases],
          'scope': 'Original declared bound functions and clocks; effective splits are implementation-derived.'}
source_bytes = (json.dumps(source, ensure_ascii=False, indent=2) + '\n').encode()
(V / 'FIXTURE_SOURCE.json').write_bytes(source_bytes)
source_sha = hashlib.sha256(source_bytes).hexdigest()
for case in cases:
    case['binding']['source_sha256'] = source_sha
    cert = deepcopy(case['binding'])
    cert.update({'generator': 'A=K+wH;H=pi*d^T-diag(d)', 'q': case['q'], 'tau': case['tau'],
                 't0': case['source_knots'][0], 'T': case['source_knots'][-1], 'w_box': ['0', '1'],
                 'fixed_K_pi_d': True, 'full_w_box': True, 'all_start_times': True,
                 'zero_mass_residual': True, 'short_remainder_nonexpansive': True,
                 'forcing_whole_fine_coarse_domain': True})
    case['certificate'] = cert
    case['input_kind'] = 'SYNTHETIC_CONDITIONAL_FIXTURE'
    case['physical_source_status'] = 'NOT_A_PHYSICAL_HD_DATA_RETURN'
baseline = next(case for case in cases if case['id'] == 'quadratic_q1')
guards = []
for spec in definitions['guards']:
    guard = {k: deepcopy(v) for k, v in spec.items() if k not in ('set', 'nested_set', 'delete')}
    if not spec.get('operation'):
        case = deepcopy(baseline)
        case.update(deepcopy(spec.get('set', {})))
        for key, value in spec.get('nested_set', {}).items():
            outer, inner = key.split('.')
            case[outer][inner] = deepcopy(value)
        for key in spec.get('delete', []):
            case.pop(key, None)
        guard['input'] = case
    guards.append(guard)
output = {'schema': 'WU_R14_FIXED_PRIMARY_CASES_V1', 'input_kind': 'SYNTHETIC_CONDITIONAL_CONTROLS',
          'valid_case_count': len(cases), 'guard_count': len(guards),
          'execution_status_at_authoring': 'NOT_RUN', 'reference_relative_guard': '1e-80',
          'reference_precision': 160, 'primary_majorant_rounding_guard': '2^-110',
          'cases': cases, 'guards': guards, 'relations': definitions['relations'],
          'guard_basis_case': 'quadratic_q1',
          'scope': 'No actual physical HD input; no old scientific replay; declared whole-domain synthetic premises.'}
(V / 'CASES.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'operation': 'ADMINISTRATIVE_INPUT_SERIALIZATION_ONLY', 'valid_cases': len(cases),
                  'guard_cases': len(guards), 'fixture_source_sha256': source_sha,
                  'science_runs': 0, 'production_imports': 0, 'old_code_runs': 0}))
