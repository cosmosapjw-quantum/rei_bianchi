#!/usr/bin/env python3
"""One bounded C2 binding diagnostic on pinned inputs; no ODE or rate sweep.

The donor number-rate implementation and recovered VF comparison stay intact.
RR lambda below is a conditional derivative-of-fit moment for RR alone, never
for Gne=RR+DR. The saved nuclear NPZ arrays are read, not recomputed.
"""
from __future__ import annotations

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
import hashlib
import importlib.util
import inspect
import json
import math
import platform
import resource
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))
import numpy as np

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parents[1]
EVIDENCE = HERE/'evidence'
FLOAT_TOL = 128*np.finfo(float).eps
SLOPE_TOL = 1e-8
FD_H = 1e-3
K_B = 1.380649e-23
RR_KEYS = ('1:1', '2:1', '2:2', '3:1', '3:2', '3:3')
RECOVERED_LABELS = ('H I', 'HeI a', 'HeII', 'LiI', 'LiII', 'LiIII')
SKILL = {'skill': 'physmath-research-loop', 'version': '1.3.0',
         'selected_stage': 'C2 formula-data-code mapping',
         'read_context': ['SKILL.md', 'references/CODING_LOOP.md:C2',
                          'references/POLICY_INTEGRATION.md', 'AGENTS.md',
                          'C2_EXECUTION_CONTRACT.md'],
         'recursive_agents': False}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def clean(value):
    """JSON has no numeric infinity; applicability remains separate metadata."""
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, np.generic):
        return clean(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        if value == -math.inf:
            return '-Infinity'
        raise ValueError('unexpected nonfinite value other than a saved log zero')
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def write(path, value):
    path.write_text(json.dumps(clean(value), indent=2, allow_nan=False)+'\n')


def relative(a, b):
    return abs(a-b)/max(abs(a), abs(b), 1e-300)


def norm(a):
    return float(np.linalg.norm(np.asarray(a).ravel()))


def normalized_difference(actual, expected, constituents):
    raw = norm(np.asarray(actual)-np.asarray(expected))
    denominator = max(math.fsum(norm(t) for t in constituents), 1e-300)
    return {'raw_norm': raw, 'sum_constituent_norms': denominator,
            'normalized_residual': raw/denominator, 'tolerance': FLOAT_TOL,
            'accepted': raw/denominator <= FLOAT_TOL}


def fit(row, temperature, include_b_dot=True):
    """Scalar direct formula, separate from both unmodified provider APIs."""
    t = float(temperature)
    a, b, t0, t1, c, t2 = [row[k] for k in ('A_cm3_s', 'B', 'T0_K', 'T1_K', 'C', 'T2_K')]
    u, v = math.sqrt(t/t0), math.sqrt(t/t1)
    correction = c*math.exp(-t2/t)
    effective_b = b+correction
    alpha = 1e-6*a/(u*(1+u)**(1-effective_b)*(1+v)**(1+effective_b))
    log_alpha = math.log(1e-6*a)-math.log(u)-(1-effective_b)*math.log1p(u)-(1+effective_b)*math.log1p(v)
    b_dot_term = correction*t2/t*math.log((1+u)/(1+v))
    slope_without_b_dot = -.5-(1-effective_b)*u/(2*(1+u))-(1+effective_b)*v/(2*(1+v))
    slope = slope_without_b_dot+(b_dot_term if include_b_dot else 0.)
    return {'alpha_m3_s': alpha, 'log_alpha': log_alpha,
            'D': slope, 'b_dot_term': b_dot_term,
            'lambda_J_m3_s': K_B*t*alpha*(1.5+slope),
            'moment_status': 'CONDITIONAL_DERIVATIVE_OF_SAME_RR_FIT'}


def slope_fd(row, temperature):
    # Mathematical-fit probes are not calls beyond either public API boundary.
    values = {j: fit(row, temperature*math.exp(j*FD_H))['log_alpha'] for j in (-2, -1, 1, 2)}
    derivative = (values[-2]-8*values[-1]+8*values[1]-values[2])/(12*FD_H)
    return derivative, values


def recovered_row(row):
    _label, _z, _n, a, b, t0, t1 = row
    return {'A_cm3_s': a, 'B': b, 'T0_K': t0, 'T1_K': t1, 'C': 0., 'T2_K': 0.}


class Results:
    def __init__(self):
        self.tests = []
        self.provider_calls = {'AtomicNetwork_constructor': 0, 'donor_rates': 0,
                               'donor_evaluate': 0, 'recovered_rr_rate': 0}

    def check(self, name, inputs, outputs, accepted, residual=None, tolerance=None,
              interpretation='finite_binding_check'):
        self.tests.append({'name': name, 'status': 'PASS' if accepted else 'FAIL',
                           'inputs': clean(inputs), 'outputs': clean(outputs),
                           'residual': clean(residual), 'tolerance': tolerance,
                           'interpretation': interpretation})


def source_checks(result, identity):
    for source in identity['sources']:
        if 'local_copy' in source:
            path = HERE/source['local_copy']
        else:
            path = Path(source['source_path'])
        observed = sha(path)
        result.check('source_byte_identity:'+str(path.relative_to(HERE) if path.is_relative_to(HERE) else path),
                     {'expected_sha256': source['sha256'], 'source': source},
                     {'observed_sha256': observed}, observed == source['sha256'])
        if observed != source['sha256']:
            raise ValueError('BYTE_IDENTITY_MISMATCH: '+str(path))
    for name, expected in identity['fixtures'].items():
        observed = sha(HERE/name)
        result.check('fixture_identity:'+name, expected, {'observed_sha256': observed}, observed == expected['sha256'])
        if observed != expected['sha256']:
            raise ValueError('BYTE_IDENTITY_MISMATCH: '+name)


def build_bindings(net, recovered, nuclear, signature):
    roman = ('I', 'II', 'III', 'IV')
    isotope = {i: name for name, indices in net.isotope_groups.items() for i in indices}
    slots = [{'index': i, 'name': name, 'isotope': isotope[i], 'A': int(net.A[i]),
              'Z': int(net.Z[i]), 'q': int(net.q[i]), 'Y_definition': 'n_i/n_B'}
             for i, name in enumerate(net.names)]
    rr_rows, photo_rows, dr_rows = [], [], []
    recovered_by_key = dict(zip(RR_KEYS, recovered['rows']))
    for i in net.recombination_indices:
        i = int(i); z, q = int(net.Z[i]), int(net.q[i]); key = f'{z}:{q}'
        row = net.coefficients['rr'][key]
        original = {'provider_id': row['source_id'], 'initial_Z': z, 'initial_q': q,
                    'Badnell_initial_target_N': z-q if z == 3 else None,
                    'source_line': row.get('source_line'), 'M': row.get('M'), 'W': row.get('W'),
                    'donor_selected_extract': 'vendor/atomic_reused/badnell_lithium_rr_rows.txt' if z == 3 else 'vendor/atomic_primary/selected_HHe_RR_DR_rows.json',
                    'donor_extract_line_1based': (4-q) if z == 3 else None}
        rr_rows.append({'initial_index': i, 'final_index': i-1, 'initial': net.names[i],
                        'final': net.names[i-1], 'roman_transition': f'{isotope[i]} {roman[q]} -> {isotope[i]} {roman[q-1]}',
                        'coefficient_key': key, 'json_pointer': '/rr/'+key, 'source': original,
                        'donor_parameters': row,
                        'recovered_VF_row_label': recovered_by_key[key][0],
                        'recovered_VF_product_N': z-q+1,
                        'comparison_status': 'SAME_VF_HHe_PROVIDER' if z < 3 else 'DIFFERENT_VF_VS_BADNELL_LI_PROVIDERS',
                        'number_unit': 'm^3 s^-1', 'moment_unit': 'J m^3 s^-1',
                        'moment_status': 'CONDITIONAL_DERIVATIVE_OF_FIT_RR_ONLY_NO_DR'})
    for i in net.photo_indices:
        i = int(i); z, q = int(net.Z[i]), int(net.q[i]); key = f'{z}:{q}'
        photo_rows.append({'initial_index': i, 'final_index': i+1,
                           'initial': net.names[i], 'final': net.names[i+1],
                           'coefficient_key': key, 'json_pointer': '/photo_VF1996/'+key,
                           'source_Z_N': [z, z-q], 'source_extract_numeric_row_1based': list(net.coefficients['photo_VF1996']).index(key)+1,
                           'source_extract': 'vendor/atomic_primary/selected_photo_rows.txt',
                           'threshold_eV': net.coefficients['photo_VF1996'][key]['Eth_eV'],
                           'Li_neutral_partial_rule': net.coefficients['LiI_partial']['branch_rule'] if key == '3:0' else None,
                           'rate_unit': 's^-1', 'power_unit': 'J s^-1 per target ion',
                           'yield_status': 'ONE_ELECTRON_FINITE_MODEL; Li1s_q+1_COARSE_GRAINING'})
    for i in net._dr_indices:
        i = int(i); key = f'{int(net.Z[i])}:{int(net.q[i])}'
        dr_rows.append({'initial_index': i, 'final_index': i-1, 'initial': net.names[i], 'final': net.names[i-1],
                        'coefficient_key': key, 'json_pointer': '/dr/'+key,
                        'source': net.coefficients['dr'][key], 'rate_unit': 'm^3 s^-1',
                        'energy_moment': 'UNRESOLVED; do not multiply Gdr by RR kinetic factor'})
    nuclear_rows = []
    for family in nuclear['families']:
        for direction in ('forward', 'reverse'):
            beta = family['kind'] == 'beta_minus'
            applicable = ('CONDITIONAL_ALL_BARE_FORWARD' if not beta else 'CONDITIONAL_EVALUATED_DECAY; CHARGE_BRANCH_UNRESOLVED') if direction == 'forward' else (
                'ABSENT_REVERSE_WEAK_BATH_NOT_A_PHYSICAL_ENTRY' if beta else
                'EXTERNAL_SUPPORT_ZERO_PR219_5_60_EV_ONLY' if family['reverse'] == 'external_photo_zero' else
                'CONDITIONAL_ALL_BARE_BINARY_DETAILED_BALANCE')
            nuclear_rows.append({'family': family['id'], 'direction': direction,
                                 'physical_entry': not (beta and direction == 'reverse'),
                                 'source_registry': 'vendor/nuclear/NUCLEAR_NETWORK_CONTRACT.json',
                                 'source_provider': family['provider'], 'applicability': applicable,
                                 'coefficient_unit': ('s^-1' if beta or (direction == 'reverse' and family['reverse'] == 'external_photo_zero') else 'm^3 s^-1'),
                                 'event_flux_unit': 'events baryon^-1 s^-1',
                                 'cumulative_unit': 'events baryon^-1',
                                 'physical_charge_branches': 'UNRESOLVED_REQUIRED_INPUT',
                                 'energy_partitions': 'UNRESOLVED_REQUIRED_INPUT'})
    return {'schema': 'rei-c2-bindings-v1', 'scope': 'C2 mapping and finite diagnostic, not production adapter',
            'normalization': 'absolute Y_i=n_i/n_B; A dot Y=1', 'slots': slots,
            'constructor_signature': str(signature),
            'photo_edges': photo_rows, 'RR_edges': rr_rows, 'DR_edges': dr_rows,
            'row_conventions': {'donor_RR_key_Z:q': 'initial positive ionic charge q',
                                'recovered_VF_N': 'recombined product electron count N=Z-q+1',
                                'Badnell_N': 'initial recombining target electron count N=Z-q',
                                'lithium_examples': ['Li II -> Li I', 'Li III -> Li II', 'Li IV -> Li III']},
            'RR_moment': {'formula': 'lambda=k_B*T*alpha_RR*(3/2+D)',
                          'D_has_b_dot': True, 'applies_to': 'rr_m3_s only, not Gne=Grr+Gdr',
                          'status': 'CONDITIONAL_DERIVATIVE_OF_FIT; NOT EMPIRICAL_ENERGY_TABLE'},
            'nuclear_directions': nuclear_rows, 'physical_directed_entries': 34,
            'beta_ownership': {'coupled_owner': 'nuclear evaluated decay inputs', 'atomic_assembly': 'G0+ne*Gne; omit donor D',
                               'old_evaluate': 'includes D in both dY_dt and jac; preserve historical code'},
            'outer_x_mapping': {'source': 'PR220 rec_hheli/code/coupled.py:CoupledSystem.rhs/jac',
                                'physical_source': 'dY/dt in proper seconds',
                                'outer_rhs': 'd(Y/scale)/dx=F/(scale*H), once',
                                'abundance_jacobian': 'J_ij*scale_j/(scale_i*H)',
                                'x': 'ln(a/a_ref), H>0'},
            'initial_data': {'source': 'AtomicNetwork._prepare_inventory', 'Y': net.initial_Y,
                             'scales': net.scales, 'isotope_inventory': net.isotope_inventory,
                             'model': net.model},
            'fixed_spectrum': net.uv_config,
            'quotient_boundary': {'source': 'PR220 code/compact_system.py:require_eligible and P',
                                  'restriction': 'fixed isotope inventory; n=T=0; common electronic fractions',
                                  'positive_n_T_injection': 'OUTSIDE_FIXED_LIFT_IMAGE'},
            'remaining_physical_providers': ['charge-resolved nuclear/decay applicability and daughter probabilities',
                                             'state-dependent beta endpoints', 'consistent physical mass/binding reference',
                                             'RR/DR energy/spectral moments', 'nonthermal transport/stopping/stress',
                                             'nuclear recoil/gamma/neutrino partitions', 'generated-photon closure']}


def binding_checks(result, net, bindings):
    counts = {'slots': len(bindings['slots']), 'photo_edges': len(bindings['photo_edges']),
              'RR_edges': len(bindings['RR_edges']), 'DR_edges': len(bindings['DR_edges'])}
    expected = {'slots': 21, 'photo_edges': 13, 'RR_edges': 13, 'DR_edges': 6}
    result.check('ordered_state_and_atomic_edges', expected, counts, counts == expected)
    for kind in ('photo_edges', 'RR_edges', 'DR_edges'):
        for edge in bindings[kind]:
            i, j = edge['initial_index'], edge['final_index']
            expected_delta_q = 1 if kind == 'photo_edges' else -1
            valid = net.A[i] == net.A[j] and net.Z[i] == net.Z[j] and net.q[j]-net.q[i] == expected_delta_q
            result.check('edge_binding:'+kind+':'+net.names[i], {'edge': edge},
                         {'delta_A': int(net.A[j]-net.A[i]), 'delta_Z': int(net.Z[j]-net.Z[i]),
                          'delta_q': int(net.q[j]-net.q[i])}, bool(valid))
    nphys = sum(row['physical_entry'] for row in bindings['nuclear_directions'])
    result.check('complete_nuclear_registry', {'expected_families': 18, 'expected_directed_entries': 34},
                 {'family_count': len(set(row['family'] for row in bindings['nuclear_directions'])),
                  'physical_directed_entries': nphys, 'array_slots': len(bindings['nuclear_directions'])},
                 len(bindings['nuclear_directions']) == 36 and nphys == 34)


def rr_checks(result, net, rr_module, recovered):
    comparison_rows = []
    sample_temperatures = (100., 1000., 10000.)
    donor_indices = {key: next(int(i) for i in net.recombination_indices
                              if f'{net.Z[i]}:{net.q[i]}' == key) for key in RR_KEYS}
    for temperature in sample_temperatures:
        rates = net.rates(temperature, 1.); result.provider_calls['donor_rates'] += 1
        for key, label, recovered_values in zip(RR_KEYS, RECOVERED_LABELS, recovered['rows']):
            donor = fit(net.coefficients['rr'][key], temperature)
            old = rr_module.rr_rate(label, temperature); result.provider_calls['recovered_rr_rate'] += 1
            from_api = float(rates['rr_m3_s'][donor_indices[key]])
            direct_error = relative(donor['alpha_m3_s'], from_api)
            result.check('donor_alpha_direct_formula:'+key+':'+str(temperature),
                         {'T_K': temperature, 'coefficient_key': key},
                         {'direct_formula': donor, 'donor_api_alpha_m3_s': from_api},
                         direct_error <= FLOAT_TOL, direct_error, FLOAT_TOL)
            recovered_direct = fit(recovered_row(recovered_values), temperature)
            recovered_error = relative(recovered_direct['alpha_m3_s'], old['alpha_m3_s'])
            result.check('recovered_alpha_direct_formula:'+label+':'+str(temperature),
                         {'T_K': temperature, 'label': label},
                         {'direct_formula': recovered_direct, 'recovered_api': old},
                         recovered_error <= FLOAT_TOL, recovered_error, FLOAT_TOL)
            alpha_ratio = from_api/old['alpha_m3_s']
            moment_ratio = donor['lambda_J_m3_s']/old['lambda_J_m3_s']
            sample = {'key': key, 'recovered_label': label, 'T_K': temperature,
                      'donor_api_alpha_m3_s': from_api, 'donor_own_fit_moment': donor,
                      'recovered_api': old, 'donor_over_recovered_alpha': alpha_ratio,
                      'donor_over_recovered_lambda': moment_ratio,
                      'provider_relation': 'SAME_VF_HHe' if key[0] != '3' else 'DIFFERENT_BADNELL_VS_VF_LI'}
            comparison_rows.append(sample)
            if key[0] != '3':
                residual = max(relative(from_api, old['alpha_m3_s']), relative(donor['lambda_J_m3_s'], old['lambda_J_m3_s']))
                result.check('same_VF_HHe_roundoff:'+key+':'+str(temperature),
                             {'same_provider': True}, sample, residual <= FLOAT_TOL, residual, FLOAT_TOL)
            else:
                result.check('distinct_Li_providers_measured:'+key+':'+str(temperature),
                             {'equality_required': False}, sample,
                             math.isfinite(alpha_ratio) and math.isfinite(moment_ratio) and alpha_ratio > 0 and moment_ratio > 0,
                             interpretation='provider_difference_measurement_not_equality_gate')
    # Formula controls include T=1e6 for donor Li only, never recovered API calls
    # or donor calls at a finite-difference probe beyond its public domain.
    for provider in ('donor', 'recovered_VF'):
        for key, label, recovered_values in zip(RR_KEYS, RECOVERED_LABELS, recovered['rows']):
            row = net.coefficients['rr'][key] if provider == 'donor' else recovered_row(recovered_values)
            temps = (*sample_temperatures, 1e6) if provider == 'donor' and key.startswith('3:') else sample_temperatures
            for temperature in temps:
                direct = fit(row, temperature)
                numerical, probes = slope_fd(row, temperature)
                residual = abs(direct['D']-numerical)
                result.check('five_point_log_slope:'+provider+':'+key+':'+str(temperature),
                             {'provider': provider, 'T_K': temperature, 'h_logT': FD_H,
                              'formula_only_auxiliary_outside_pilot': temperature == 1e6,
                              'public_provider_calls_at_probe_T': False},
                             {'analytic': direct, 'five_point_D': numerical, 'probe_log_alpha': probes},
                             residual <= SLOPE_TOL, residual, SLOPE_TOL)
    row = net.coefficients['rr']['3:1']
    wrong = fit(row, 1e6, include_b_dot=False)
    correct = fit(row, 1e6)
    numerical, probes = slope_fd(row, 1e6)
    residual = abs(wrong['D']-numerical)
    result.check('negative_control_missing_b_dot_Li_plus_1e6',
                 {'coefficient_key': '3:1', 'T_K': 1e6, 'h': FD_H},
                 {'wrong_D': wrong['D'], 'correct_D': correct['D'], 'five_point_D': numerical,
                  'omitted_b_dot_term': correct['b_dot_term'], 'wrong_formula_accepted': residual <= SLOPE_TOL},
                 residual > SLOPE_TOL, residual, SLOPE_TOL,
                 interpretation='EXPECTED_REJECTION_NOT_PRODUCT_FAILURE')
    write(EVIDENCE/'RR_PROVIDER_COMPARISON.json', {'rows': comparison_rows,
          'ratio_orientation': 'donor_Badnell_or_VF / recovered_VF',
          'RR_only': True, 'moment_interpretation': 'conditional own-fit derivative; no empirical energy-loss accuracy claim'})


def photo_checks(result, networks, atomic):
    for cutoff, net in networks.items():
        rates = net.rates(10000., 1.); result.provider_calls['donor_rates'] += 1
        for i in net.photo_indices:
            i = int(i)
            threshold = float(net.transition_energy_eV[i])*atomic.EV_J*float(rates['photo_s'][i])
            absorbed = float(rates['absorbed_power_per_ion_W'][i])
            primary = float(rates['primary_kinetic_power_per_ion_W'][i])
            core = float(rates['unresolved_core_power_per_ion_W'][i])
            raw = math.fsum([absorbed, -threshold, -primary, -core])
            denominator = max(math.fsum(map(abs, [absorbed, threshold, primary, core])), 1e-300)
            residual = abs(raw)/denominator
            result.check('photo_energy_partition:'+str(cutoff)+':'+net.names[i],
                         {'cutoff_eV': cutoff, 'index': i, 'Gamma_s-1': float(rates['photo_s'][i]),
                          'threshold_eV': float(net.transition_energy_eV[i])},
                         {'absorbed_W_per_ion': absorbed, 'threshold_times_Gamma_W_per_ion': threshold,
                          'primary_W_per_ion': primary, 'core_W_per_ion': core,
                          'raw_residual_W_per_ion': raw, 'sum_abs_terms': denominator},
                         residual <= FLOAT_TOL, residual, FLOAT_TOL)
        for isotope in ('Li6', 'Li7'):
            indices = net.isotope_groups[isotope]
            values = {'Li1s': float(rates['li1s_photo_s'][indices[0]]),
                      'LiII': float(rates['photo_s'][indices[1]]),
                      'LiIII': float(rates['photo_s'][indices[2]])}
            accepted = all(v == 0 for v in values.values()) if cutoff == 60 else all(v > 0 for v in values.values())
            result.check('Li_external_support:'+str(cutoff)+':'+isotope,
                         {'cutoff_eV': cutoff, 'field_identity': 'donor finite quadrature with requested cutoff',
                          'expected': 'exact support zeros' if cutoff == 60 else 'positive support'},
                         {'rates_s-1': values, 'scope': 'external field only, no hard nuclear photons'}, accepted)


def assembly_checks(result, net):
    fixture = load(HERE/'fixtures/manufactured_state.json')
    raw = np.array(fixture['raw_positive_vector'], dtype=float)
    population = raw/float(net.A@raw)
    nb, temperature, uv = fixture['nb_m-3'], fixture['T_K'], fixture['uv_scale']
    rates = net.rates(temperature, uv); result.provider_calls['donor_rates'] += 1
    old = net.evaluate(population, temperature, uv, nb)
    result.provider_calls['donor_evaluate'] += 1
    # evaluate internally invokes rates exactly once in the pinned donor source.
    result.provider_calls['donor_rates'] += 1
    ne = nb*float(net.q@population)
    photo, rr, dr, decay = rates['G0']@population, ne*(rates['Grr']@population), ne*(rates['Gdr']@population), rates['D']@population
    fatom = (rates['G0']+ne*rates['Gne'])@population
    g0, gne, charge_jac, dd = rates['G0'], ne*rates['Gne'], nb*np.outer(rates['Gne']@population, net.q), rates['D']
    jatom = g0+gne+charge_jac
    fcomparison = normalized_difference(fatom+decay, old['dY_dt'], [photo, rr, dr, decay])
    jcomparison = normalized_difference(jatom+dd, old['jac'], [g0, gne, charge_jac, dd])
    bad = normalized_difference(fatom+decay, fatom, [photo, rr, dr, decay])
    result.check('manufactured_positive_baryon_normalization', fixture,
                 {'population_Y': population, 'A_dot_Y': float(net.A@population), 'ne_m-3': ne},
                 bool(np.all(population > 0)) and abs(float(net.A@population)-1) <= FLOAT_TOL,
                 abs(float(net.A@population)-1), FLOAT_TOL)
    result.check('beta_free_atomic_RHS_plus_old_D_matches_evaluate',
                 {'nb_m-3': nb, 'T_K': temperature, 'uv': uv, 'Y': population},
                 {'Fatom': fatom, 'D_times_Y': decay, 'sum': fatom+decay, 'old_evaluate_dY_dt': old['dY_dt'],
                  'constituents': {'photo': photo, 'RR': rr, 'DR': dr, 'beta': decay}, 'comparison': fcomparison},
                 fcomparison['accepted'], fcomparison['normalized_residual'], FLOAT_TOL)
    result.check('beta_free_atomic_J_plus_old_D_matches_evaluate', {},
                 {'Jatom': jatom, 'D': dd, 'sum': jatom+dd, 'old_evaluate_jac': old['jac'], 'comparison': jcomparison},
                 jcomparison['accepted'], jcomparison['normalized_residual'], FLOAT_TOL)
    result.check('negative_control_beta_retained_in_beta_free_source',
                 {'allegedly_beta_free': '(G0+D+ne*Gne)Y', 'true_beta_free': '(G0+ne*Gne)Y'},
                 {'comparison': bad, 'bad_assembly_accepted': bad['accepted']},
                 not bad['accepted'], bad['normalized_residual'], FLOAT_TOL,
                 interpretation='EXPECTED_REJECTION_NOT_PRODUCT_FAILURE')


def nuclear_checks(result, identity, nuclear, bindings):
    source_paths = {Path(row['source_path']).name: Path(row['source_path'])
                    for row in identity['sources'] if 'source_path' in row}
    paths = [source_paths['NUCLEAR_NETWORK_HISTORIES.npz'], source_paths['NUCLEAR_NETWORK_LOG_RATE_TABLE.npz']]
    expected = {
      'hist': {'case_names': (82,), 'family_ids': (18,), 'species': (8,), 'x': (257,), 'T_K': (257,),
               'elapsed_s': (82,257), 'nB_m3': (82,257), 'log_T_n': (82,257,2),
               'log_fast_source': (82,257,2), 'log_forward_reverse_flux': (82,257,18,2),
               'log_forward_reverse_cumulative': (82,257,18,2)},
      'rate': {'T_K': (257,), 'family_ids': (18,), 'log_forward_rate_m3_s_or_s_inv': (257,18),
               'log_reverse_rate_m3_s': (257,18)}}
    arrays, shapes = {}, {}
    # Only direct NPZ reads. No nuclear module is imported, nor any saved result rewritten.
    for prefix, path in zip(('hist', 'rate'), paths):
        with np.load(path, allow_pickle=False) as saved:
            arrays[prefix] = {key: saved[key] for key in saved.files}
        shapes[prefix] = {key: list(a.shape) for key, a in arrays[prefix].items()}
        result.check('saved_NPZ_shapes:'+prefix, {'expected': expected[prefix]},
                     {'observed': shapes[prefix]}, set(arrays[prefix]) == set(expected[prefix]) and
                     all(a.shape == expected[prefix][key] for key, a in arrays[prefix].items()))
    names = [f['id'] for f in nuclear['families']]
    shared = np.array_equal(arrays['hist']['T_K'], arrays['rate']['T_K'])
    ordered = arrays['hist']['family_ids'].tolist() == names == arrays['rate']['family_ids'].tolist()
    result.check('saved_family_order_and_shared_temperature_grid', {'contract_order': names},
                 {'hist_family_order': arrays['hist']['family_ids'], 'rate_family_order': arrays['rate']['family_ids'],
                  'temperature_grid_identical': shared, 'T_first_K': arrays['hist']['T_K'][0],
                  'T_last_K': arrays['hist']['T_K'][-1]}, shared and ordered)
    metadata = load(HERE/'fixtures/nuclear_saved_metadata.json')
    rate_array = arrays['rate']['log_forward_rate_m3_s_or_s_inv']
    for family_id, constant_key in [('t_beta', 'lambda_t_s-1'), ('n_beta', 'lambda_n_s-1')]:
        index = names.index(family_id)
        recorded_lambda = metadata['constants'][constant_key]
        expected_log = math.log(recorded_lambda)
        residual = float(np.max(np.abs(rate_array[:,index]-expected_log)))
        result.check('saved_natural_log_convention:'+family_id,
                     {'saved_lambda_s-1': recorded_lambda, 'natural_log_of_saved_lambda': expected_log},
                     {'all_saved_log_rates': rate_array[:,index]}, residual <= FLOAT_TOL,
                     residual, FLOAT_TOL, interpretation='saved_constant/log_binding_not_rate_recomputation')
    indices = identity['sample']['epoch_indices']
    case_index = identity['sample']['case_index']
    sample_arrays = {}
    for prefix, rows in arrays.items():
        for key, a in rows.items():
            sample_arrays[prefix+'__'+key] = a[case_index,indices] if a.ndim>=2 and a.shape[:2] == (82,257) else a[indices] if a.shape[0] == 257 else a
    with np.load(HERE/identity['sample']['sample_fixture'], allow_pickle=False) as fixture:
        sample_equal = set(fixture.files) == set(sample_arrays) and all(np.array_equal(fixture[key], a) for key,a in sample_arrays.items())
    result.check('extracted_nuclear_fixture_equals_direct_saved_slices',
                 {'case_index': case_index, 'epoch_indices': indices},
                 {'array_keys': list(sample_arrays), 'exact_array_equality': sample_equal}, sample_equal)
    for j, family in enumerate(nuclear['families']):
        reverse = arrays['rate']['log_reverse_rate_m3_s'][:,j]
        if family['reverse'] == 'binary_detailed_balance':
            accepted = bool(np.isfinite(reverse).all())
        else:
            accepted = bool(np.isneginf(reverse).all())
        result.check('saved_reverse_applicability:'+family['id'],
                     {'declared_reverse': family['reverse']},
                     {'saved_reverse_log_values_at_sample': reverse[indices],
                      'status': bindings['nuclear_directions'][2*j+1]['applicability']}, accepted)
    epochs = []
    for epoch in indices:
        families = []
        for j, family in enumerate(nuclear['families']):
            directions = []
            for d, direction in enumerate(('forward', 'reverse')):
                direction_binding = bindings['nuclear_directions'][2*j+d]
                directions.append({'direction': direction, 'applicability': direction_binding['applicability'],
                                   'physical_entry': direction_binding['physical_entry'],
                                   'coefficient_unit': direction_binding['coefficient_unit'],
                                   'log_coefficient': arrays['rate']['log_forward_rate_m3_s_or_s_inv' if d == 0 else 'log_reverse_rate_m3_s'][epoch,j],
                                   'log_flux_events_per_baryon_s': arrays['hist']['log_forward_reverse_flux'][case_index,epoch,j,d],
                                   'log_cumulative_events_per_baryon': arrays['hist']['log_forward_reverse_cumulative'][case_index,epoch,j,d]})
            families.append({'family': family['id'], 'directions': directions})
        epochs.append({'epoch_index': epoch, 'x': arrays['hist']['x'][epoch],
                       'T_K': arrays['hist']['T_K'][epoch], 'nB_m-3': arrays['hist']['nB_m3'][case_index,epoch],
                       'elapsed_s': arrays['hist']['elapsed_s'][case_index,epoch],
                       'log_T_n': {'order': ['T','n'], 'values': arrays['hist']['log_T_n'][case_index,epoch]},
                       'families': families})
    write(EVIDENCE/'NUCLEAR_SAVED_SAMPLE.json',
          {'case_index': case_index, 'case_name': arrays['hist']['case_names'][case_index],
           'epoch_indices': indices, 'full_shapes': shapes, 'log_convention': 'natural logarithms',
           'negative_infinity_encoding': 'tagged string -Infinity; applicability always read separately from registry, never inferred from value alone',
           'epochs': epochs, 'saved_sample_only': True, 'rate_or_event_recomputations': 0})


def run(result):
    identity = load(HERE/'SOURCE_IDENTITY.json')
    source_checks(result, identity)
    atomic = module('pinned_c2_atomic', HERE/'vendor/donor_atomic/code/atomic_network.py')
    recovered_module = module('pinned_c2_recovered_rr', HERE/'vendor/recovered_rr/code/rr_adapter.py')
    recovered = load(HERE/'vendor/recovered_rr/code/rr_rows.json')
    nuclear = load(HERE/'vendor/nuclear/NUCLEAR_NETWORK_CONTRACT.json')
    signature = inspect.signature(atomic.AtomicNetwork)
    result.check('actual_constructor_signature', {'expected_parameter': 'uv_cutoff_eV'},
                 {'observed_signature': str(signature)}, list(signature.parameters) == ['uv_cutoff_eV'])
    networks = {cutoff: atomic.AtomicNetwork(uv_cutoff_eV=cutoff) for cutoff in (60,200)}
    result.provider_calls['AtomicNetwork_constructor'] += 2
    net = networks[200]
    bindings = build_bindings(net, recovered, nuclear, signature)
    write(HERE/'BINDINGS.json', bindings)
    binding_checks(result, net, bindings)
    rr_checks(result, net, recovered_module, recovered)
    photo_checks(result, networks, atomic)
    assembly_checks(result, net)
    nuclear_checks(result, identity, nuclear, bindings)


def main():
    wall0, cpu0 = time.perf_counter(), time.process_time()
    result, error = Results(), None
    try:
        run(result)
    except Exception:
        error = traceback.format_exc()
    failures = [row['name'] for row in result.tests if row['status'] != 'PASS']
    exit_code = int(bool(failures or error))
    resources = {'wall_s': time.perf_counter()-wall0, 'cpu_s': time.process_time()-cpu0,
                 'max_rss_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 'cpu_cap_s': 60, 'address_space_cap_MiB': 256, 'ODE_calls': 0, 'IVP_calls': 0,
                 'historical_campaigns_rerun': 0, 'nuclear_rate_recomputations': 0,
                 'nuclear_propagator_calls': 0, 'diagnostic_invocations': 1}
    report = {'schema': 'rei-c2-finite-binding-checks-v1',
              'status': 'PASS_FINITE_C2_BINDINGS' if not exit_code else 'FAIL_PRESERVED',
              'test_count': len(result.tests), 'failed_tests': failures,
              'float_tolerance': FLOAT_TOL, 'slope_absolute_tolerance': SLOPE_TOL,
              'tests': result.tests, 'provider_call_counts': result.provider_calls,
              'exception': error, 'resources': resources,
              'skill_context_used': SKILL,
              'claim_boundary': 'C2 finite input/code/formula binding only; no production-provider or thermal/cosmological solution admission'}
    execution = {'schema': 'rei-c2-execution-v1', 'utc': datetime.now(timezone.utc).isoformat(),
                 'command': [sys.executable, str(Path(__file__).resolve())],
                 'working_directory': str(Path.cwd()), 'python_version': sys.version,
                 'numpy_version': np.__version__, 'platform': platform.platform(),
                 'requested_model_identity': 'lower-tier routine implementation/execution under Astra frozen contract',
                 'observed_model_identity': 'UNAVAILABLE_FROM_RUNTIME_TOOL_OUTPUT',
                 'script_sha256': sha(Path(__file__).resolve()),
                 'execution_contract_sha256': sha(HERE/'C2_EXECUTION_CONTRACT.md'),
                 'source_identity_sha256': sha(HERE/'SOURCE_IDENTITY.json'),
                 'bindings_sha256': sha(HERE/'BINDINGS.json') if (HERE/'BINDINGS.json').exists() else None,
                 'resources': resources, 'provider_call_counts': result.provider_calls,
                 'skill_context_used': SKILL, 'exit_code': exit_code, 'exception': error}
    write(EVIDENCE/'BINDING_CHECKS.json', report)
    write(EVIDENCE/'EXECUTION.json', execution)
    print(json.dumps({'status': report['status'], 'test_count': len(result.tests),
                      'failed_tests': failures, 'resources': resources,
                      'provider_call_counts': result.provider_calls, 'exception': error}, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
