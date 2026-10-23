#!/usr/bin/env python3
"""C1 finite algebra diagnostic; no physical provider, solver or IVP.

Run from any directory: python /absolute/path/check_contract.py
Only Python's standard library is required. Fixtures are small projections of
immutable sources, with copied-byte SHA256 provenance. Manufactured quantities
below are algebra inputs, not applicable physical masses, branch probabilities,
rates, equilibrium fractions, temperature histories or energy partitions.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import resource
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / 'fixtures'
EVIDENCE = HERE / 'evidence'
BASE = '5a1e5220b301a1c497f2863d6fd823e605faba80'
TOL = 64 * sys.float_info.epsilon
ENERGY_KEYS = ('thermal', 'fast', 'excitation', 'gamma_retained', 'gamma_escaped', 'neutrino')
SKILL_CONTEXT = {'skill': 'physmath-research-loop', 'version': '1.3.0',
                 'selected_stage': 'C1 COUPLED_ISOTOPE_NATIVE_CONTRACT',
                 'read': ['SKILL.md', 'references/CODING_LOOP.md:C1',
                          'references/POLICY_INTEGRATION.md', 'AGENTS.md', 'CONTRACT.md'],
                 'native_subagent': 'PARENT_DISPATCHED_THIS_BOUNDED_EXECUTOR',
                 'recursive_delegation': False}


class Unresolved(ValueError):
    """An absent physical input cannot be converted to zero or PASS."""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((FIXTURES / name).read_text())


def balance(terms):
    """Signed additive identity with the contract's term-sum normalization."""
    raw = math.fsum(terms)
    scale = max(math.fsum(abs(v) for v in terms), 1e-300)
    return {'residual': raw, 'sum_abs_terms': scale,
            'normalized_residual': abs(raw) / scale, 'tolerance': TOL,
            'accepted': abs(raw) / scale <= TOL}


def vector(left, right, species):
    return [right.get(s, 0) - left.get(s, 0) for s in species]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def require_probabilities(values):
    if values is None or not values:
        raise Unresolved('UNRESOLVED_DAUGHTER_PROBABILITIES')
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('invalid daughter probability')
    if not balance([*values, -1.0])['accepted']:
        raise ValueError('daughter probabilities do not sum to one')
    return values


def ledger(q0, external, delta_i, partition):
    if partition is None or set(partition) != set(ENERGY_KEYS):
        raise Unresolved('UNRESOLVED_ENERGY_PARTITION')
    if any(not math.isfinite(v) for v in partition.values()):
        raise ValueError('nonfinite signed energy increment')
    return balance([q0, external, -delta_i, *(-partition[k] for k in ENERGY_KEYS)])


def fractions(y):
    total = math.fsum(y)
    if total <= 0:
        raise Unresolved('UNDEFINED_FRACTION_AT_ZERO_INVENTORY')
    return [v / total for v in y]


def unique_beta_owner(owners):
    if len(owners) != 1:
        raise ValueError('BETA_EXCHANGE_REQUIRES_EXACTLY_ONE_OWNER')
    return owners[0]


class Checks:
    def __init__(self):
        self.rows = []

    def add(self, name, inputs, outputs, residuals=None, accepted=True,
            interpretation='manufactured_or_derived_algebra'):
        residuals = residuals or {}
        accepted = accepted and all(v['accepted'] for v in residuals.values())
        self.rows.append({'name': name, 'status': 'PASS' if accepted else 'FAIL',
                          'interpretation': interpretation, 'inputs': inputs,
                          'outputs': outputs, 'residuals': residuals})

    def rejection(self, name, operation, expected, inputs):
        try:
            value = operation()
        except (ValueError, Unresolved) as error:
            self.add(name, inputs, {'observed_exception': type(error).__name__,
                                    'message': str(error)},
                     accepted=str(error) == expected,
                     interpretation='expected_rejection_control')
        else:
            self.add(name, inputs, {'unexpected_value': value}, accepted=False,
                     interpretation='expected_rejection_control')


def run(checks):
    provenance = load('PROVENANCE.json')
    for name, expected in provenance['fixtures'].items():
        observed = sha(FIXTURES / name)
        checks.add('fixture_byte_identity:' + name, {'expected_sha256': expected},
                   {'observed_sha256': observed}, accepted=expected == observed,
                   interpretation='immutable_input_byte_identity')
    # Available source readback is useful but standalone fixture execution does
    # not require access to the rest of either historical checkout.
    for source in provenance['sources']:
        path = Path(source['source_path'])
        observed = sha(path) if path.exists() else None
        checks.add('source_provenance:' + path.name,
                   source, {'observed_sha256': observed,
                            'readback': 'BYTE_MATCH' if observed == source['sha256']
                            else 'SOURCE_NOT_LOCAL' if observed is None
                            else 'BYTE_IDENTITY_MISMATCH'},
                   accepted=observed is None or observed == source['sha256'],
                   interpretation='provenance_identity_only_not_physics_accuracy')
    network = load('frozen18.json')
    species, aa, zz = (network[k] for k in ('nuclear_state_order', 'A', 'Z'))
    families = network['families']
    by_id = {f['id']: f for f in families}
    directions = []
    for f in families:
        for sign in ((1,) if f['kind'] == 'beta_minus' else (1, -1)):
            nu = [sign*v for v in vector(f['reactants'], f['products'], species)]
            electrons = sign*f.get('electrons_created', 0)
            ar, zr = dot(aa, nu), dot(zz, nu)-electrons
            name = f['id'] + (':forward' if sign == 1 else ':reverse')
            directions.append((name, f, sign, nu))
            checks.add('integer_stoichiometry:' + name,
                       {'species': species, 'A': aa, 'Z': zz, 'nu': nu,
                        'beta_electrons': electrons},
                       {'A_dot_nu': ar, 'Z_dot_nu_minus_electrons': zr,
                        'bare_charge_residual': zr},
                       accepted=ar == zr == 0,
                       interpretation='exact_integer_nuclear_conservation')
    for beta_id in ('t_beta', 'n_beta'):
        declarations = [f for f in families if f['id'] == beta_id]
        active = [name for name, f, sign, nu in directions if f['id'] == beta_id]
        beta_family = by_id[beta_id]
        checks.add('beta_catalogue_single_forward_owner:' + beta_id,
                   {'expected_owner': 'EVALUATED_DECAY_INPUTS.json',
                    'required_reverse_status': 'not_in_this_lowT_neutrino_free_model'},
                   {'declaration_count': len(declarations), 'active_entries': active,
                    'model': beta_family['model'], 'provider': beta_family['provider'],
                    'reverse_status': beta_family['reverse']},
                   accepted=len(declarations) == 1 and active == [beta_id+':forward']
                   and beta_family['model'] == 'decay'
                   and beta_family['provider'].startswith('EVALUATED_DECAY_INPUTS.json:')
                   and beta_family['reverse'] == 'not_in_this_lowT_neutrino_free_model',
                   interpretation='exact_inherited_beta_catalogue_no_inverse_weak_provider')
    expected_zeros = {'he3_n_gamma', 'p_t_gamma', 'd_d_gamma', 'p_d_gamma',
                      'p_n_gamma', 't_alpha_gamma', 'd_alpha_gamma', 'd_n_gamma'}
    zeros = {f['id'] for f in families if f['reverse'] == 'external_photo_zero'}
    aliases = sorted(i for f in families for i in f['dossier_ids'])
    checks.add('family_direction_and_external_support_labels',
               {'expected_families': 18, 'expected_directed_entries': 34,
                'expected_external_zero_families': sorted(expected_zeros)},
               {'family_count': len(families), 'directed_count': len(directions),
                'external_zero_families': sorted(zeros),
                'external_field': network['external_photon_field'], 'aliases': aliases},
               accepted=len(families) == 18 and len(directions) == 34 and
               zeros == expected_zeros and aliases == list(range(4, 20)),
               interpretation='inherited_labels_only_no_new_rate_evaluation')
    for row in network['dossier_rows']:
        canonical = lambda table: {'H1' if k == 'p' else k: v for k, v in table.items()}
        original = vector(canonical(row['reactants']), canonical(row['products']), species)
        f = next(f for f in families if row['id'] in f['dossier_ids'])
        forward = vector(f['reactants'], f['products'], species)
        orientation = 1 if original == forward else -1 if original == [-v for v in forward] else 0
        checks.add('source_alias:' + str(row['id']), row,
                   {'family': f['id'], 'source_vector': original,
                    'canonical_forward_vector': forward, 'source_orientation': orientation},
                   accepted=orientation != 0,
                   interpretation='exact_source_alias_and_direction')

    slots = [(s, q) for s, z in zip(species, zz) for q in range(z+1)]
    a_slot = [aa[species.index(s)] for s, q in slots]
    z_slot = [zz[species.index(s)] for s, q in slots]
    q_slot = [q for s, q in slots]
    checks.add('ordered_21_slot_state', {}, {'slots': slots, 'count': len(slots)},
               accepted=len(slots) == 21)
    beta = [('n_continuum', ('n', 0), ('H1', 1), 1, 0),
            ('T_neutral_spectator', ('T', 0), ('He3', 1), 1, 0),
            ('T_bare_continuum', ('T', 1), ('He3', 2), 1, 0),
            ('T_neutral_shakeoff', ('T', 0), ('He3', 2), 2, -1)]
    for name, initial, final, expected_e, expected_bound in beta:
        nu = [int(s == final)-int(s == initial) for s in slots]
        free = dot(q_slot, nu)
        bound = dot([z-q for z, q in zip(z_slot, q_slot)], nu)
        dz = dot(z_slot, nu)
        checks.add('beta_endpoint:' + name, {'initial': initial, 'final': final, 'nu': nu,
                                           'physical_branch_probability': None},
                   {'delta_free_electrons': free, 'delta_bound_electrons': bound,
                    'delta_nuclear_charge': dz, 'A_residual': dot(a_slot, nu),
                    'free_plus_bound_minus_delta_Z': free+bound-dz},
                   accepted=free == expected_e and bound == expected_bound and
                   dz == 1 and dot(a_slot, nu) == 0 and free+bound-dz == 0)

    # Exact dyadic artificial rest/binding energies keep this a reference-algebra
    # test; no empirical mass or ionization-energy accuracy is being asserted.
    unit = 2.0**-60  # J
    mass = {s: (a*1000+z*19+i*7)*unit
            for i, (s, a, z) in enumerate(zip(species, aa, zz))}
    electron_rest = 13*unit
    b0 = {s: z*(z+1)*unit for s, z in zip(species, zz)}
    neutral = {s: mass[s]+z*electron_rest-b0[s] for s, z in zip(species, zz)}
    checks.add('manufactured_mass_binding_table',
               {'unit_J': unit, 'physical_mass_validation': False},
               {'M_c2_J': mass, 'electron_rest_J': electron_rest, 'B0_J': b0,
                'neutral_rest_J': neutral,
                'B_Aq_definition': '(Z-q)*(Z-q+1)*unit_J'})
    for name, f, sign, nu in directions:
        qbare = -dot([mass[s] for s in species], nu)-electron_rest*dot(zz, nu)
        q0 = -dot([neutral[s] for s in species], nu)
        for endpoint in ('neutral', 'bare', 'one_spectator'):
            qs = [0 if endpoint == 'neutral' else z if endpoint == 'bare'
                  else max(z-1, 0) for z in zz]
            binding = [(z-q)*(z-q+1)*unit for z, q in zip(zz, qs)]
            ii = [b0[s]-b for s, b in zip(species, binding)]
            ionic = [mass[s]+(z-q)*electron_rest-b
                     for s, z, q, b in zip(species, zz, qs, binding)]
            delta_i = dot(ii, nu)
            available = -dot(ionic, nu)-electron_rest*dot(qs, nu)
            residuals = {'neutral_vs_bare': balance([q0, -qbare, -dot([b0[s] for s in species], nu)]),
                         'available_vs_neutral': balance([available, -q0, delta_i]),
                         'available_vs_bare': balance([available, -qbare, -dot(binding, nu)])}
            checks.add('mass_reference:' + name + ':' + endpoint,
                       {'nu': nu, 'q_assignment': qs, 'manufactured_J_only': True},
                       {'Q_bare_J': qbare, 'Q0_J': q0, 'Delta_I_J': delta_i,
                        'Q_available_J': available}, residuals)
    # Atomic isotope vector vanishes although the charge-resolved vector does not.
    checks.add('atomic_mass_reference_threshold', {'initial': ['H1', 0], 'final': ['H1', 1]},
               {'Q0_J': 0.0, 'Delta_I_J': b0['H1'], 'Q_available_J': -b0['H1']},
               {'identity': balance([-b0['H1'], b0['H1']])})

    def partition(**overrides):
        return {k: overrides.get(k, 0.0) for k in ENERGY_KEYS}

    energy_cases = [
        ('threshold_photo', 0., 13*unit, 13*unit, partition()),
        ('above_threshold_photo', 0., 21*unit, 13*unit, partition(thermal=8*unit)),
        ('threshold_RR', 0., 0., -13*unit, partition(gamma_escaped=13*unit)),
        ('RR_with_supplied_energy_moment', 0., 0., -13*unit,
         partition(thermal=-8*unit, gamma_escaped=21*unit)),
        ('synthetic_nuclear_partition', 64*unit, 0., 4*unit,
         partition(fast=28*unit, gamma_retained=20*unit, neutrino=12*unit)),
        ('fast_to_thermal_transfer', 0., 0., 0., partition(thermal=7*unit, fast=-7*unit))]
    for name, q0, external, delta_i, part in energy_cases:
        checks.add('energy:' + name,
                   {'Q0_J': q0, 'W_J': external, 'Delta_I_J': delta_i,
                    'partition_J': part, 'not_physical_energy_model': True},
                   {'ledger': ledger(q0, external, delta_i, part)},
                   {'energy': ledger(q0, external, delta_i, part)})
    double = ledger(64*unit, 0., 0., partition(thermal=64*unit, fast=64*unit))
    checks.add('energy:intentional_double_Q_rejected',
               {'Q0_J': 64*unit, 'partition_J': partition(thermal=64*unit, fast=64*unit)},
               {'observed_failed_ledger': double, 'expected_rejection': True},
               accepted=not double['accepted'], interpretation='expected_failure_preserved')
    checks.add('beta_single_owner', {'owners': ['nuclear_events']},
               {'owner': unique_beta_owner(['nuclear_events'])})
    checks.rejection('beta_duplicate_owner_rejected',
                     lambda: unique_beta_owner(['atomic_D', 'nuclear_events']),
                     'BETA_EXCHANGE_REQUIRES_EXACTLY_ONE_OWNER',
                     {'owners': ['atomic_D', 'nuclear_events'], 'scope': 'future composition hazard'})
    checks.rejection('missing_daughter_probabilities_rejected', lambda: require_probabilities(None),
                     'UNRESOLVED_DAUGHTER_PROBABILITIES', {'physical_probabilities': None})
    checks.rejection('missing_energy_partition_rejected', lambda: ledger(unit, 0., 0., None),
                     'UNRESOLVED_ENERGY_PARTITION', {'energy_partition': None})

    capture_nu = [int(s == ('D', 1))-int(s in (('H1', 1), ('n', 0))) for s in slots]
    delta_n, delta_e = sum(capture_nu), dot(q_slot, capture_nu)
    delta_c = dot([1+q for q in q_slot], capture_nu)
    checks.add('EOS_capture_particle_source_without_electron_source',
               {'branch': 'H1II+n->DII', 'nu': capture_nu},
               {'delta_nuclei': delta_n, 'delta_electrons': delta_e, 'delta_C_th': delta_c,
                'incorrect_electron_only_delta_C': delta_e},
               accepted=delta_n == -1 and delta_e == 0 and delta_c == -1)
    kb = 1.380649e-23  # exact SI definition, J/K
    temp, cth, hubble, dc = 8192., .75, 2.0**-10, -.0625
    heat_per_baryon = 48*kb  # manufactured instantaneous J/(baryon s)
    dt = -2*hubble*temp-temp*dc/cth+2*heat_per_baryon/(3*kb*cth)
    de = 1.5*kb*(cth*dt+temp*dc)
    energy_residual = balance([de, 3*hubble*kb*temp*cth, -heat_per_baryon])
    checks.add('EOS_variable_C_temperature_identity',
               {'T_K': temp, 'C_th': cth, 'H_s-1': hubble, 'dot_C_s-1': dc,
                'Qth_over_nB_J_per_baryon_s': heat_per_baryon,
                'single_instantaneous_algebra_fixture_no_history': True},
               {'dot_T_K_s': dt, 'dot_eth_J_per_baryon_s': de}, {'energy_equation': energy_residual})
    initial_c, final_c, initial_t = 1., 2., 8192.
    eth = 1.5*kb*initial_t*initial_c
    final_t = eth/(1.5*kb*final_c)
    checks.add('EOS_threshold_H_photoionization_halves_T',
               {'initial_Y_HI': 1., 'final_Y_HII': 1., 'final_Y_e': 1.,
                'C_initial': initial_c, 'C_final': final_c, 'T_initial_K': initial_t,
                'external_photon_exactly_threshold': True, 'Delta_eth_J': 0.},
               {'T_final_K': final_t, 'ratio': final_t/initial_t},
               {'half_temperature': balance([final_t, -initial_t/2]),
                'thermal_energy': balance([eth, -1.5*kb*final_t*final_c])})
    fixed_dt = -2*hubble*temp
    checks.add('EOS_fixed_composition_adiabatic_identity',
               {'dot_C': 0., 'Qth': 0., 'H_s-1': hubble, 'T_K': temp},
               {'dot_T': fixed_dt, 'd_log_T_d_log_a': fixed_dt/(hubble*temp)},
               {'slope': balance([fixed_dt/(hubble*temp), 2.])})

    # The old lift's image fixes both n and T at zero. Use an inherited exact
    # D+D -> H1+T event vector as a tangent, without inventing a nuclear rate.
    t_source = vector(by_id['d_d_p']['reactants'], by_id['d_d_p']['products'], species)
    outside = [s for s in ('n', 'T') if t_source[species.index(s)] != 0]
    checks.add('quotient_fixed_lift_positive_T_source_rejected',
               {'old_lift_constraints': {'n': 0, 'T': 0},
                'event_tangent': t_source, 'event': 'D+D->H1+T'},
               {'outside_image_components': outside, 'positive_T_source': t_source[3],
                'old_lift_accepts': not outside},
               accepted=outside == ['T'] and t_source[3] == 1,
               interpretation='exact_fixed_lift_image_counterexample')
    checks.rejection('quotient_no_division_by_absent_T', lambda: fractions([0., 0.]),
                     'UNDEFINED_FRACTION_AT_ZERO_INVENTORY', {'Y_TI': 0., 'Y_TII': 0.})
    shared_f = [.25, .75]  # manufactured vector for algebra, no equilibrium claim
    injection_rows = []
    for label, inventory, source in [('H1', .5, .125), ('D', .125, .0625), ('T', .0625, .03125)]:
        aligned = [v*source for v in shared_f]
        residual = [(s-f*source)/inventory for f, s in zip(shared_f, aligned)]
        injection_rows.append({'isotope': label, 'Y': inventory, 'S_total': source,
                               'S_charge': aligned, 'fraction_source': residual})
    checks.add('quotient_source_aligned_common_fractions',
               {'manufactured_shared_f': shared_f, 'pointwise_only_no_source_history': True},
               {'rows': injection_rows},
               accepted=all(all(v == 0 for v in row['fraction_source']) for row in injection_rows))
    mismatched = [(s-f*.125)/.0625 for s, f in zip([0., .125], shared_f)]
    checks.add('quotient_electronic_equality_insufficient',
               {'shared_f': shared_f, 'Y_T': .0625, 'S_Tq': [0., .125],
                'reference_source_aligned_fraction_term': [0., 0.]},
               {'T_fraction_source': mismatched, 'common_fraction_invariance': False},
               accepted=any(v != 0 for v in mismatched))

    evaluated, old = load('evaluated_decay_inputs.json'), load('legacy_atomic_decay.json')
    evaluated_half = evaluated['tritium_half_life_years']*evaluated['year_days']*evaluated['seconds_per_day']
    old_half = old['tritium_half_life_years']*old['julian_year_s']
    ln2 = math.log(2)
    new_lambda, old_lambda = ln2/evaluated_half, ln2/old_half
    ratio = new_lambda/old_lambda-1
    checks.add('legacy_and_evaluated_tritium_measured_separately',
               {'legacy_half_life_years': old['tritium_half_life_years'],
                'legacy_julian_year_s': old['julian_year_s'],
                'evaluated_half_life_years': evaluated['tritium_half_life_years'],
                'evaluated_year_days': evaluated['year_days'],
                'seconds_per_day': evaluated['seconds_per_day']},
               {'legacy_half_life_s': old_half, 'evaluated_half_life_s': evaluated_half,
                'legacy_lambda_s-1': old_lambda, 'evaluated_lambda_s-1': new_lambda,
                'delta_lambda_s-1': new_lambda-old_lambda,
                'lambda_evaluated_over_legacy_minus_one': ratio,
                'relative_difference_percent': 100*ratio,
                'conditional_coupled_owner': 'evaluated_decay_inputs.json',
                'old_zero_T_pilot_error_claimed': False},
               {'ratio_identity': balance([new_lambda/old_lambda, -old_half/evaluated_half])},
               accepted=new_lambda != old_lambda and new_lambda > old_lambda,
               interpretation='separate_inherited_definitions_not_historical_result_invalidation')


def main():
    wall0, cpu0 = time.perf_counter(), time.process_time()
    # This process neither invokes child processes nor runs a numerical ODE.
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))
    EVIDENCE.mkdir(exist_ok=True)
    checks, failure = Checks(), None
    try:
        run(checks)
    except Exception:
        failure = traceback.format_exc()
    failed = [c['name'] for c in checks.rows if c['status'] != 'PASS']
    exit_code = int(bool(failed or failure))
    resources = {'wall_s': time.perf_counter()-wall0,
                 'cpu_s': time.process_time()-cpu0,
                 'max_rss_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 'cpu_cap_s': 60, 'address_space_cap_MiB': 256,
                 'new_cosmological_IVPs': 0, 'subprocesses_launched': 0}
    report = {'schema': 'rei-c1-algebra-checks-v1', 'base_head': BASE,
              'status': 'PASS_FINITE_C1_ALGEBRA' if exit_code == 0 else 'FAIL_PRESERVED',
              'claim_boundary': 'C1 derived/manufactured algebra only; physical coupled production HOLD_DEPENDENCIES',
              'skill_context_used': SKILL_CONTEXT, 'binary64_epsilon': sys.float_info.epsilon,
              'float_tolerance': TOL, 'integer_acceptance': 'exact zero',
              'test_count': len(checks.rows), 'failed_tests': failed,
              'tests': checks.rows, 'exception': failure, 'resources': resources}
    execution = {'schema': 'rei-c1-execution-v1', 'utc': datetime.now(timezone.utc).isoformat(),
                 'command': [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                 'working_directory': str(Path.cwd()), 'base_head': BASE,
                 'python_version': sys.version, 'platform': platform.platform(),
                 'dependencies': 'Python standard library only',
                 'requested_executor_role': 'bounded lower-tier implementation under frozen Astra contract',
                 'observed_executor_model': 'not exposed by runtime tool output; no model identity inferred',
                 'script_sha256': sha(Path(__file__).resolve()),
                 'contract_sha256': sha(HERE/'CONTRACT.md'),
                 'fixture_manifest_sha256': sha(FIXTURES/'PROVENANCE.json'),
                 'skill_context_used': SKILL_CONTEXT, 'exit_code': exit_code,
                 'resources': resources, 'failure': failure}
    (EVIDENCE/'ALGEBRA_CHECKS.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    (EVIDENCE/'EXECUTION.json').write_text(json.dumps(execution, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'status': report['status'], 'test_count': len(checks.rows),
                      'failed_tests': failed, 'resources': resources, 'exception': failure}, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
