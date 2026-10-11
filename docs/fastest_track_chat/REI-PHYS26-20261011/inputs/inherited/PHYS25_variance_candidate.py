#!/usr/bin/env python3
"""PHYS25 bounded minimum-variance candidate, standard-library implementation.

The original-fit log Taylor-jet and finite-difference utilities are explicitly
adapted from the read-only PHYS24 helper. No old module is imported or executed.
New numerical brackets and sampled dual inequalities are not continuum proofs.
"""
from __future__ import annotations

import argparse
from decimal import Decimal as D, getcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import platform

getcontext().prec = 160
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUT_PATHS = {
    'contract': ROOT / 'PHYSICS_CONTRACT.json',
    'J_input': ROOT / 'inputs/PHYS22_INITIAL_COEFFICIENTS.json',
    'inherited_numerics_code': ROOT / 'inputs/inherited/PHYS24_moment_envelope.py',
    'inherited_numerics_result': ROOT / 'inputs/inherited/PHYS24_MOMENT_ENVELOPE.json',
    'handoff': ROOT / 'inputs/inherited/PHYS25_INTAKE_HANDOFF_KO.md',
    'protocol': HERE / 'PROTOCOL.json',
}
EXPECTED = {
    'contract': '7fce1d8729a22b89b00d8116d237af3ddcddc0951901eaa46ba821d9ed07b1c3',
    'J_input': '6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79',
    'inherited_numerics_code': 'b323494a0e7e9017c431059c0f946b633c9678a22bd2677f5340868ea1890978',
    'inherited_numerics_result': '551ae060d935e5145e54a1c2af9deb5c5b2c4d8d7007d90295eb0bbad5e83d09',
    'handoff': 'adc3aa7644598ac86eeb83b2447bbea11977b2b516dac2b08c0f2e88616d0473',
    'protocol': '5b5c16a41bdbc0136a456ebc99697e6eb0da053532b683c862ed75a300d792d3',
}
ZERO, ONE = D(0), D(1)
L, M, U = D('13.61'), D(18), D('24.58')
K_SCALE = D('1e-64')
ALG_TOL = D('1e-125')
ROOT_TOL, ROOT_WIDTH = D('1e-65'), D('1e-70')
FD_TOL, ANCHOR_TOL, SLACK_TOL = D('1e-38'), D('1e-95'), D('1e-60')
FD_H = D('1e-5')
FD_ENERGIES = [L, D(14), D(16), M, D(20), D(23), U]
OFFSETS = list(range(-6, 7))
ROOT_ITERATIONS = 240
CHECKS = []
COUNTS = {'response_calls': 0, 'unique_response_energies': 0,
          'direct_fit_calls': 0, 'root_searches': 0, 'bisection_iterations': 0}


def b(value):
    return D.from_float(float(value))


N0 = b('0.05')
SH = (b('1.01e-14') - b('0.99e-14')) / 2
Q = 2 * SH**2
KAPPA = b('29979245800') * b('1e-4') * (1 - b('0.9'))
FACTOR = Q * N0 * KAPPA / 180
CHI = b('13.598434599702')
E0, YA, PP = b('0.4298'), b('32.88'), b('2.963')
SIG0, CM2 = b('5.475e4'), b('1e-18')
HI_CUT, HEI_CUT = b('13.60'), b('24.59')


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def condition(name, passed, **evidence):
    CHECKS.append({'name': name, 'pass': bool(passed), **evidence})


def close(name, actual, expected, tol=ALG_TOL, scale=None):
    if scale is None:
        scale = max(abs(actual), abs(expected))
    error = abs(actual - expected) / scale if scale else abs(actual - expected)
    condition(name, error <= tol, actual=actual, expected=expected,
              scaled_error=error, tolerance=tol, scale=scale)
    return error


def power(value, exponent):
    return (exponent * value.ln()).exp()


def sigma_direct(e):
    if not HI_CUT < e < HEI_CUT:
        raise ValueError('direct fit left the analytic HI-only band')
    x = e / E0
    return SIG0 * (x - 1)**2 * power(x, PP / 2 - b('5.5')) * power(
        1 + (x / YA).sqrt(), -PP) * CM2


def f_direct(e, jx, jw):
    COUNTS['direct_fit_calls'] += 1
    return sigma_direct(e) * (jx + jw * (e - CHI))


class Jet:
    """Degree-five ordinary log Taylor coefficients, c[n]=D^n f/n!."""
    size = 6

    def __init__(self, value):
        if isinstance(value, (list, tuple)):
            if len(value) > self.size:
                raise ValueError('Taylor coefficient overflow')
            self.c = list(value) + [ZERO] * (self.size - len(value))
        else:
            self.c = [D(value)] + [ZERO] * (self.size - 1)

    @staticmethod
    def lift(value):
        return value if isinstance(value, Jet) else Jet(value)

    def __add__(self, other):
        other = self.lift(other)
        return Jet([x + y for x, y in zip(self.c, other.c)])

    __radd__ = __add__

    def __neg__(self):
        return Jet([-x for x in self.c])

    def __sub__(self, other):
        return self + -self.lift(other)

    def __rsub__(self, other):
        return self.lift(other) + -self

    def __mul__(self, other):
        other = self.lift(other)
        return Jet([sum((self.c[j] * other.c[n-j] for j in range(n+1)), ZERO)
                    for n in range(self.size)])

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        if isinstance(scalar, Jet):
            raise TypeError('only scalar division is used')
        return Jet([x / scalar for x in self.c])

    def __pow__(self, exponent):
        exponent = D(exponent)
        base = self.c[0]
        if base <= 0:
            raise ValueError('Taylor power needs a positive base')
        u = self / base - 1
        binomial, term, series = ONE, Jet(1), Jet(1)
        for degree in range(1, self.size):
            term = term * u
            binomial *= (exponent - degree + 1) / degree
            series += binomial * term
        return power(base, exponent) * series


def original_fit_response(e, jx, jw):
    if not L <= e <= U:
        raise ValueError('energy outside the fixed support')
    ej = Jet([e / factorial(n) for n in range(6)])
    xj = ej / E0
    sigj = SIG0 * (xj - 1)**2 * xj**(PP / 2 - b('5.5')) * (
        1 + (xj / YA)**D('0.5'))**(-PP) * CM2
    fj = sigj * (jx + jw * (ej - CHI))
    dn = [fj.c[n] * factorial(n) for n in range(6)]
    return {'energy_eV': e, 'sigma_cm2': sigj.c[0], 'D_0_to_5_f': dn,
            'k_s-4': FACTOR * (dn[2] + 3 * dn[1]),
            'k_prime_s-4_eV-1': FACTOR * (dn[3] + 3 * dn[2]) / e,
            'k_second_s-4_eV-2': FACTOR * (dn[4] + 2 * dn[3] - 3 * dn[2]) / e**2,
            'k_third_s-4_eV-3': FACTOR * (dn[5] - 7 * dn[3] + 6 * dn[2]) / e**3}


def exact_weights(order):
    n = len(OFFSETS)
    a = [[F(offset)**degree for offset in OFFSETS]
         + [F(factorial(order) if degree == order else 0)] for degree in range(n)]
    for col in range(n):
        pivot = next(row for row in range(col, n) if a[row][col])
        a[col], a[pivot] = a[pivot], a[col]
        div = a[col][col]
        a[col] = [v / div for v in a[col]]
        for row in range(n):
            if row != col and a[row][col]:
                fac = a[row][col]
                a[row] = [v - fac * w for v, w in zip(a[row], a[col])]
    return [row[-1] for row in a]


def fd_responses(e, step, jx, jw, weights):
    values = [f_direct(e * (D(offset) * step).exp(), jx, jw) for offset in OFFSETS]
    dn = {order: sum((D(w.numerator) / D(w.denominator) * val
                     for w, val in zip(ww, values)), ZERO) / step**order
          for order, ww in weights.items()}
    return {'k_s-4': FACTOR * (dn[2] + 3 * dn[1]),
            'k_prime_s-4_eV-1': FACTOR * (dn[3] + 3 * dn[2]) / e,
            'k_second_s-4_eV-2': FACTOR * (dn[4] + 2 * dn[3] - 3 * dn[2]) / e**2,
            'k_third_s-4_eV-3': FACTOR * (dn[5] - 7 * dn[3] + 6 * dn[2]) / e**3}


def bisect_numeric(label, func, lo, hi):
    initial = [lo, hi]
    flo, fhi = func(lo), func(hi)
    if not flo * fhi < 0:
        raise ValueError('no strict initial numerical sign bracket: ' + label)
    initial_values = [flo, fhi]
    COUNTS['root_searches'] += 1
    for _ in range(ROOT_ITERATIONS):
        mid = (lo + hi) / 2
        fm = func(mid)
        if fm == 0:
            raise ArithmeticError('rounded exact zero requires a recorded bracket policy correction')
        if fm * flo > 0:
            lo, flo = mid, fm
        else:
            hi, fhi = mid, fm
        COUNTS['bisection_iterations'] += 1
    midpoint = (lo + hi) / 2
    residual = func(midpoint)
    width = hi - lo
    condition(label + '__strict_final_sign_bracket', flo * fhi < 0,
              bracket_eV=[lo, hi], values=[flo, fhi])
    condition(label + '__bounded_width', width < ROOT_WIDTH,
              width_eV=width, tolerance_eV=ROOT_WIDTH)
    return {'label': label, 'initial_bracket_eV': initial,
            'initial_function_values': initial_values,
            'iterations': ROOT_ITERATIONS, 'final_bracket_eV': [lo, hi],
            'final_function_values': [flo, fhi], 'midpoint_eV': midpoint,
            'midpoint_function_residual': residual, 'width_eV': width,
            'classification': 'numerical sign bracket, not an exact interval certificate'}


def jsonable(obj):
    if isinstance(obj, D):
        return str(obj)
    if isinstance(obj, F):
        return {'numerator': str(obj.numerator), 'denominator': str(obj.denominator)}
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    return obj


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('refusing to overwrite first evidence')
    identities = {label: file_hash(path) for label, path in INPUT_PATHS.items()}
    if identities != EXPECTED:
        raise ValueError('frozen input mismatch: ' + repr(identities))
    identities['code'] = file_hash(Path(__file__))
    jj = json.loads(INPUT_PATHS['J_input'].read_text())['results']['baseline_local']['J_nonphoto']
    jx, jw = D(jj[2][0]), D(jj[2][3])
    old = json.loads(INPUT_PATHS['inherited_numerics_result'].read_text())
    old18 = next(row for row in old['envelope_samples'] if row['label'] == 'mean_18')
    condition('frozen_J_signs', jx < 0 < jw, jx=jx, jw=jw)
    cache = {}

    def response(e):
        COUNTS['response_calls'] += 1
        if e not in cache:
            cache[e] = original_fit_response(e, jx, jw)
            COUNTS['unique_response_energies'] += 1
        return cache[e]

    def k(e):
        return response(e)['k_s-4']

    ka, km, kb = k(L), k(M), k(U)
    response_scale = max(abs(ka), abs(km), abs(kb))
    condition('inherited_feasibility_signs', ka > 0 > km and kb < 0,
              ka_s_4=ka, km_s_4=km, kb_s_4=kb)
    close('one_inherited_mean18_mono_anchor', km, D(old18['lower_candidate_k_s-4']), ANCHOR_TOL)

    def two_law(lo, hi):
        return [(lo, (hi-M)/(hi-lo)), (hi, (M-lo)/(hi-lo))]

    def law_values(label, law):
        mass = sum((p for e, p in law), ZERO)
        mean = sum((e*p for e, p in law), ZERO)
        variance = sum(((e-M)**2*p for e, p in law), ZERO)
        kval = sum((k(e)*p for e, p in law), ZERO)
        second = sum((e**2*p for e, p in law), ZERO)
        close(label + '__mass', mass, ONE)
        close(label + '__mean', mean, M)
        close(label + '__number', N0*mass, N0)
        close(label + '__energy', N0*mean, N0*M)
        close(label + '__variance_identity', variance, second-M**2)
        condition(label + '__nonnegative_support_law',
                  all(L <= e <= U and p >= 0 for e, p in law))
        return {'label': label,
                'law': [{'energy_eV': e, 'probability': p, 'photon_number_per_H': N0*p}
                        for e, p in law],
                'probability_mass': mass, 'mean_energy_eV': mean,
                'total_photon_number_per_H': N0*mass,
                'total_energy_eV_per_H': N0*mean,
                'variance_eV2': variance, 'rms_width_eV': variance.sqrt(),
                'response_s-4': kval}

    endpoint = law_values('endpoint_law', two_law(L, U))
    close('one_inherited_mean18_upper_anchor', endpoint['response_s-4'],
          D(old18['upper_candidate_k_s-4']), ANCHOR_TOL)
    condition('positive_endpoint_response', endpoint['response_s-4'] > 0)

    def upper_root(lower, label):
        def numerator(v):
            return (v-M)*k(lower)+(M-lower)*k(v)
        root = bisect_numeric(label, numerator, M, U)
        v = root['midpoint_eV']
        law = law_values(label + '__law', two_law(lower, v))
        close(label + '__response_zero', law['response_s-4'], ZERO, ROOT_TOL, response_scale)
        close(label + '__two_point_variance', law['variance_eV2'], (M-lower)*(v-M))
        return root, law

    root, candidate = upper_root(L, 'primary_anchored_root')
    v = root['midpoint_eV']
    r, d, h = v-M, M-L, v-L
    kv, kpv = k(v), response(v)['k_prime_s-4_eV-1']
    denominator = ka-kv+h*kpv
    lambda2 = h**2 / denominator
    lambda1 = 2*r-lambda2*kpv
    lambda0 = -r**2+lambda2*(r*kpv-kv)
    condition('dual_contact_positive_denominator', denominator > 0,
              denominator_s_4=denominator)
    condition('dual_nonnegative_response_multiplier', lambda2 > 0,
              lambda2_eV2_s4=lambda2)
    close('contact_value_equals_candidate_variance', lambda0,
          candidate['variance_eV2'], SLACK_TOL, ONE)

    def slack(e):
        return (e-M)**2-lambda0-lambda1*(e-M)-lambda2*k(e)

    def slack_prime(e):
        return 2*(e-M)-lambda1-lambda2*response(e)['k_prime_s-4_eV-1']

    close('dual_contact_a', slack(L), ZERO, SLACK_TOL, ONE)
    close('dual_contact_v', slack(v), ZERO, SLACK_TOL, ONE)
    close('dual_tangency_v', slack_prime(v), ZERO, SLACK_TOL, ONE)
    condition('dual_left_endpoint_inward_slope_positive', slack_prime(L) > 0,
              slope_eV=slack_prime(L))
    condition('dual_interior_contact_second_positive',
              2-lambda2*response(v)['k_second_s-4_eV-2'] > 0,
              second=2-lambda2*response(v)['k_second_s-4_eV-2'])
    slack_energies = [L, D(14), D(16), M, D(20), D(22), U, v-D('.1'), v, v+D('.1')]
    slack_rows = []
    for e in slack_energies:
        q = slack(e)
        condition('sampled_dual_slack__'+str(e), q >= -SLACK_TOL,
                  energy_eV=e, slack_eV2=q, tolerance_eV2=SLACK_TOL)
        slack_rows.append({'energy_eV': e, 'slack_eV2': q,
                           'slack_prime_eV': slack_prime(e),
                           'slack_second': 2-lambda2*response(e)['k_second_s-4_eV-2']})

    def lower_numerator(u):
        return (U-M)*k(u)+(M-u)*kb
    reverse_root = bisect_numeric('opposite_endpoint_root', lower_numerator, L, M)
    reverse_law = law_values('opposite_endpoint_root__law', two_law(reverse_root['midpoint_eV'], U))
    close('opposite_endpoint_root__response_zero', reverse_law['response_s-4'],
          ZERO, ROOT_TOL, response_scale)
    condition('opposite_endpoint_variance_exceeds_primary_candidate',
              reverse_law['variance_eV2'] > candidate['variance_eV2'])

    lower14_root, lower14_law = upper_root(D(14), 'lower14_root')
    condition('lower14_variance_exceeds_primary_candidate',
              lower14_law['variance_eV2'] > candidate['variance_eV2'])
    feasibility_rows = []
    for lower in [D('14.5'), D(15)]:
        ep = law_values('lower'+str(lower)+'_upper_endpoint', two_law(lower, U))
        feasibility_rows.append({**ep, 'feasible_in_anchored_upper_line_family': ep['response_s-4'] >= 0,
                                  'basis_if_negative': 'closed PHYS24 strict convexity: endpoint response is the family maximum',
                                  'new_root_searches': 0})

    theta = -km/(endpoint['response_s-4']-km)
    triples = [(e, theta*p) for e, p in two_law(L, U)] + [(M, 1-theta)]
    triple = law_values('active_three_line_endpoint_mono', triples)
    close('three_line_active_response', triple['response_s-4'], ZERO, ALG_TOL, response_scale)
    condition('three_line_variance_exceeds_primary_candidate',
              triple['variance_eV2'] > candidate['variance_eV2'])
    half_law = [(e, p/2) for e, p in two_law(L, v)]+[(M, D('.5'))]
    half = law_values('half_candidate_half_mono', half_law)
    close('half_candidate_variance', half['variance_eV2'], candidate['variance_eV2']/2)
    close('half_candidate_response', half['response_s-4'],
          (candidate['response_s-4']+km)/2)
    condition('half_candidate_response_negative', half['response_s-4'] < 0)

    weights = {order: exact_weights(order) for order in range(1, 6)}
    moments = []
    for order, ww in weights.items():
        for degree in range(13):
            val = sum((w*F(offset)**degree for offset, w in zip(OFFSETS, ww)), F(0))
            target = F(factorial(order) if degree == order else 0)
            moments.append({'derivative_order': order, 'power': degree,
                            'actual': val, 'expected': target, 'pass': val == target})
    condition('exact_FD_polynomial_moments', all(row['pass'] for row in moments),
              count=len(moments))
    minimum_node, maximum_node = L*(-6*FD_H).exp(), U*(6*FD_H).exp()
    condition('all_FD_nodes_in_original_HI_band', HI_CUT < minimum_node <= maximum_node < HEI_CUT,
              minimum_eV=minimum_node, maximum_eV=maximum_node,
              HI_cut_eV=HI_CUT, HeI_cut_eV=HEI_CUT)
    fd_rows, fd_errors = [], []
    for e in FD_ENERGIES:
        primary = response(e)
        coarse = fd_responses(e, FD_H, jx, jw, weights)
        fine = fd_responses(e, FD_H/2, jx, jw, weights)
        extrapolated = {key: (256*fine[key]-coarse[key])/255 for key in coarse}
        errors = {key: close('direct_FD__'+str(e)+'__'+key, extrapolated[key], primary[key], FD_TOL)
                  for key in coarse}
        fd_errors += list(errors.values())
        condition('sampled_negative_third__'+str(e),
                  primary['k_third_s-4_eV-3'] < 0 and extrapolated['k_third_s-4_eV-3'] < 0,
                  primary=primary['k_third_s-4_eV-3'], FD=extrapolated['k_third_s-4_eV-3'])
        fd_rows.append({'energy_eV': e, 'primary': primary, 'FD_h': coarse,
                        'FD_h_over_2': fine, 'FD_Richardson': extrapolated,
                        'relative_errors': errors})

    condition('root_budget', COUNTS['root_searches'] <= 3 and COUNTS['bisection_iterations'] <= 720,
              searches=COUNTS['root_searches'], iterations=COUNTS['bisection_iterations'])
    failed = [row['name'] for row in CHECKS if not row['pass']]
    result = {
        'task': 'REI-PHYS25-20261011',
        'evidence_class': ['numerically checked', 'implementation-verified'],
        'python_version': platform.python_version(), 'decimal_precision': getcontext().prec,
        'identity_sha256': identities,
        'constants': {'mean_eV': M, 'support_eV': [L, U], 'N0_per_H': N0,
                      'q_s-2': Q, 'kappa_s-1_cm-2': KAPPA, 'prefactor': FACTOR,
                      'chi_eV': CHI, 'E0_eV': E0, 'ya': YA, 'P': PP,
                      'J_h2_x': jx, 'J_h2_w': jw},
        'original_kernel_samples': {'left': response(L), 'mean': response(M), 'right': response(U)},
        'primary_anchored_root': root,
        'primary_candidate': candidate,
        'dual_contact_candidate': {
            'Q': '(E-m)^2-lambda0-lambda1(E-m)-lambda2*k(E)',
            'lambda0_eV2': lambda0, 'lambda1_eV': lambda1,
            'lambda2_eV2_s4': lambda2,
            'scaled_kernel_unit_s-4': K_SCALE,
            'multiplier_for_k_divided_by_1e-64_eV2': lambda2*K_SCALE,
            'positive_denominator_s-4': denominator,
            'contact_slack_a_eV2': slack(L), 'contact_slack_v_eV2': slack(v),
            'contact_prime_v_eV': slack_prime(v),
            'candidate_variance_minus_dual_value_eV2': candidate['variance_eV2']-lambda0,
            'global_validity': 'requires separate continuum proof; sample checks alone do not establish it'},
        'sampled_dual_slack': slack_rows,
        'opposite_endpoint_root': reverse_root,
        'opposite_endpoint_law': reverse_law,
        'lower14_root': lower14_root, 'lower14_law': lower14_law,
        'additional_lower_endpoint_feasibility': feasibility_rows,
        'three_line_active_law': triple, 'endpoint_mono_mixing_weight': theta,
        'subcritical_mixture_law': half,
        'exact_FD_weights': weights, 'exact_FD_moments': moments,
        'new_derivative_samples': fd_rows,
        'checks': CHECKS,
        'summary': {'total_checks': len(CHECKS), 'passed': len(CHECKS)-len(failed),
                    'failed': len(failed), 'failed_names': failed,
                    'all_pass': not failed, 'maximum_relative_FD_error': max(fd_errors),
                    'actual_counts': COUNTS,
                    'old_module_imports': 0, 'old_main_invocations': 0,
                    'native_runs': 0, 'gas_IVP_runs': 0, 'closed_suite_replays': 0,
                    'dense_grid_campaigns': 0,
                    'physical_admission': 'HOLD',
                    'optimizer_status': 'feasible root-defined candidate; global optimality needs separate proof',
                    'root_precision': 'numerical only; no rigorous interval enclosure or physical uncertainty claim'},
    }
    with args.output.open('x') as out:
        json.dump(jsonable(result), out, indent=2, ensure_ascii=False)
        out.write('\n')
    print(json.dumps(jsonable({'summary': result['summary'],
          'candidate': candidate, 'dual_contact': result['dual_contact_candidate'],
          'output_sha256': file_hash(args.output)}), indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
