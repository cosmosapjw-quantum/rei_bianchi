"""Read-only actual PR88 REC candidate and exact stored-quadrature arithmetic.

No recomputed spectrum, provider queries, chemistry or history execution.
"""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[3]
DONOR = ROOT / 'research/igm_rate_export_receiver_20261008'
UPSTREAM = DONOR / 'repo/research/igm_rate_receiver01_20261008/adapter.py'
SPECIES = ('HI', 'HeI', 'HeII')
ARITHMETIC_SCOPE = 'FINITE_STORED_QUADRATURE_ARITHMETIC_ONLY'


def upstream():
    spec = importlib.util.spec_from_file_location('rec_pr88_adapter', UPSTREAM)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load():
    a = upstream()
    packet = a.load_packet()  # Original immutable packet pin and context checks.
    state, chi, context, _ = a.typed_input(packet)
    data = (DONOR / 'observed/samples.binary64.csv').read_bytes()
    if hashlib.sha256(data).hexdigest() != packet['context']['samples_sha256']:
        raise ValueError('IMMUTABLE_SPECTRUM_IDENTITY_MISMATCH')
    bits = [line.split(',') for line in data.decode().splitlines()]
    if len(bits) != 2440 or any(len(row) != 11 for row in bits):
        raise ValueError('SPECTRUM_SHAPE_MISMATCH')
    rows = [[struct.unpack('>d', bytes.fromhex(x))[0] for x in row] for row in bits]
    return a, packet, state, chi, context, data, bits, rows


def candidate():
    a, p, s, chi, context, data, bits, rows = load()
    c = p['context']
    return {
        'schema': 'REC-ACTUAL-INITIAL01/v1',
        'payload_status': 'ACTUAL_ACCEPTED_ENDPOINT_CANDIDATE',
        'source_context': copy.deepcopy(c),
        'context_id': p['context_id'], 'observation_id': p['observation_id'],
        'family_identity': {k: copy.deepcopy(p[k]) for k in
                            ('family_id', 'family_kind', 'generator_ids', 'generators')},
        'epoch_ln_a_exact': str(F.from_float(c['epoch_ln_a'])),
        'gas_state_exact': [str(v) for v in (s.h, s.y, s.z, s.w_erg_h)],
        'gas_state_units': ['HII/H', 'HeII/He', 'HeIII/He', 'erg/H'],
        'n_H': str(s.n_h), 'n_He': str(s.n_he),
        'n_e': str(s.n_h*s.electrons), 'x_e_per_H': str(s.electrons),
        'density_units': 'proper cm^-3', 'density_conversion_count': 0,
        'Tgas': str(s.temperature), 'temperature_units': 'K',
        'gas_temperature_authority': c['EOS'],
        'radiation_components': {
            'CMB_bath': {'Trad': str(F.from_float(c['background'][5])),
                         'temperature_units': 'K', 'model': 'prescribed_CMB_blackbody_bath',
                         'authority': c['background_recovery'] + ';background[5]'},
            'ionizing_finite_grid': {
                'model': 'actual_saved_finite_grid_NOT_whole_radiation_blackbody',
                'density_units': 'photons/H/unit_eta', 'row_count': len(rows),
                'samples_sha256': c['samples_sha256'],
                'columns_binary64_hex': ['eta', 'weight', 'density', 'energy_eV',
                    'sigma_HI_cm2', 'sigma_HeI_cm2', 'sigma_HeII_cm2',
                    'stored_term_HI_s1', 'stored_term_HeI_s1', 'stored_term_HeII_s1', 'c_cm_s'],
                'rows_binary64_hex': bits,
                'epoch_ln_a_exact': str(F.from_float(c['photon_epoch_ln_a'])),
                'photo_provider': c['photo_provider'],
                'provider_source_sha256': c['provider_source_sha256'],
                'chi_ev_exact': [str(v) for v in chi],
                'support_cutoffs_ev_exact': [str(F.from_float(v)) for v in c['provider_cutoffs_ev']],
            },
        },
        'consumer_gate_I': 'HOLD', 'matched_evolution': 'HOLD', 'physical': 'HOLD',
        'whole_radiation_blackbody': False,
        'extra_calls': {'observer': 0, 'provider': 0, 'RHS': 0, 'history': 0},
    }


def validate(packet):
    """This v1 accepts exactly the preserved endpoint, not arbitrary histories."""
    expected = candidate()
    checks = [('epoch_ln_a_exact', 'EPOCH_MISMATCH'),
              ('source_context', 'SOURCE_PROVIDER_STATE_IDENTITY_MISMATCH'),
              ('context_id', 'CONTEXT_MISMATCH'), ('observation_id', 'OBSERVATION_MISMATCH'),
              ('gas_state_exact', 'GAS_STATE_MISMATCH'),
              ('n_H', 'PROPER_DENSITY_MISMATCH'), ('n_He', 'PROPER_DENSITY_MISMATCH'),
              ('density_units', 'DENSITY_UNIT_MISMATCH'),
              ('density_conversion_count', 'DOUBLE_DENSITY_CONVERSION'),
              ('n_e', 'ELECTRON_DENSITY_MISMATCH'), ('x_e_per_H', 'ELECTRON_FRACTION_MISMATCH'),
              ('Tgas', 'EOS_TEMPERATURE_MISMATCH'),
              ('consumer_gate_I', 'UNAUTHORIZED_GATE_PROMOTION'),
              ('matched_evolution', 'UNAUTHORIZED_GATE_PROMOTION'),
              ('physical', 'UNAUTHORIZED_GATE_PROMOTION'),
              ('whole_radiation_blackbody', 'WHOLE_RADIATION_BLACKBODY_FORBIDDEN')]
    for key, code in checks:
        if packet.get(key) != expected[key]:
            raise ValueError(code)
    components = packet.get('radiation_components', {})
    if components.get('CMB_bath') != expected['radiation_components']['CMB_bath']:
        raise ValueError('MISSING_OR_MISMATCHED_CMB_TRAD')
    if components.get('ionizing_finite_grid') != expected['radiation_components']['ionizing_finite_grid']:
        raise ValueError('MISSING_OR_MISMATCHED_ACTUAL_SPECTRUM')
    if packet != expected:
        raise ValueError('REC_INITIAL_METADATA_MISMATCH')
    return copy.deepcopy(packet)


def arithmetic():
    a, p, state, chi, context, data, bits, rows = load()
    # Import the original PR87 algebra already imported by original PR88.
    vendor = __import__('upstream_bridge.vendor.source_transfer', fromlist=['spectral_moments'])
    exact_rows = [{'index': j, 'weight': F.from_float(r[1]), 'density': F.from_float(r[2]),
                   'energy_eV': F.from_float(r[3]),
                   **{'sigma_'+k: F.from_float(r[4+i]) for i,k in enumerate(SPECIES)}}
                  for j,r in enumerate(rows)]
    c = F.from_float(p['context']['constants']['c_cm_s'])
    if any(F.from_float(r[10]) != c for r in rows):
        raise ValueError('ROW_C_CONSTANT_MISMATCH')
    exact = vendor.spectral_moments(exact_rows, c, state.n_h)
    # Reproduce only the stored ordered arithmetic, never call the observer.
    gamma, energy = [0.0]*3, [0.0]*3
    for r in rows:
        for i in range(3):
            if r[7+i] != float(c)*float(state.n_h)*r[4+i]*r[2]*r[1]:
                raise ValueError('STORED_PRODUCT_ORDER_MISMATCH')
            gamma[i] += r[7+i]
            energy[i] += r[7+i]*r[3]
    if gamma != p['Gamma'] or energy != p['incident_Ecal']:
        raise ValueError('ORDERED_MOMENT_PARITY_MISMATCH')
    observed = vendor.Moments(tuple(map(F.from_float,gamma)), tuple(map(F.from_float,energy)))
    defect = observed-exact
    point = vendor.project(state, observed, chi)
    exact_projection = vendor.project(state, exact, chi)
    delta = vendor.project(state, defect, chi)
    if any(point[k]-exact_projection[k] != delta[k] for k in point):
        raise ValueError('SAME_STATE_LINEAR_PROPAGATION_FAILURE')
    control = json.loads((DONOR/'observed/PHOTO_ALGEBRA.json').read_text())['native_per_second']
    if any(point[k] != F(control[k]) for k in point):
        raise ValueError('PR87_PHOTO_MAP_PARITY_MISMATCH')
    values = lambda m: {'Gamma': [str(v) for v in m.gamma],
                        'incident_Ecal': [str(v) for v in m.energy_ev_s]}
    u = F(1,2**53); bound_factor = (len(rows)+5)*u/(1-(len(rows)+5)*u)
    within = all(abs(d) <= bound_factor*abs(e) for d,e in
                 zip((*defect.gamma,*defect.energy_ev_s),(*exact.gamma,*exact.energy_ev_s)))
    assert within
    return {'scope': ARITHMETIC_SCOPE, 'context_id': p['context_id'],
            'observation_id': p['observation_id'], 'samples_sha256': p['context']['samples_sha256'],
            'row_count': len(rows), 'species': list(SPECIES), 'units': p['units'],
            'exact_six_moments': values(exact), 'ordered_binary64_moments': values(observed),
            'signed_binary64_minus_exact': values(defect),
            'same_state_photo_map_exact': {k:str(v) for k,v in exact_projection.items()},
            'same_state_photo_map_signed_defect': {k:str(v) for k,v in delta.items()},
            'finite_positive_sum_roundoff_factor': str(bound_factor),
            'six_finite_arithmetic_bounds_pass': within,
            'nonlinear_state_remainder': 'NOT_EVALUATED_NO_STATE_PERTURBATION',
            'continuum_error': 'UNKNOWN', 'provider_fit_error': 'UNKNOWN',
            'temporal_error': 'UNKNOWN', 'physical': 'HOLD',
            'extra_calls': {'observer':0,'provider':0,'RHS':0,'history':0}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): parser.error('fresh output directory required')
    packet = validate(candidate()); result = arithmetic()
    args.output.mkdir(parents=True)
    for name, value in [('REC_INITIAL.json', packet), ('EXACT_MOMENT_ARITHMETIC.json', result)]:
        (args.output/name).write_text(json.dumps(value, indent=2)+'\n')
    (args.output/'samples.binary64.csv').write_bytes((DONOR/'observed/samples.binary64.csv').read_bytes())
    print('PASS_ACTUAL_REC_CANDIDATE; FINITE_STORED_QUADRATURE_ARITHMETIC_ONLY; physical HOLD')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
