#!/usr/bin/env python3
"""PHYS26 bounded fixed-variance implementation checks, standard library only.

The degree-three log Taylor jet is explicitly adapted from the read PHYS25
pure helper. No previous module, main, test suite, or root search is invoked.
The scalar log-derivative expression is separately written from the original
HI cross-section fit. Samples and small residuals are numerical evidence;
they do not certify continuum inequalities or enclose physical uncertainty.
"""
from __future__ import annotations

import argparse
from decimal import Decimal as D, getcontext
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import platform

getcontext().prec = 160
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / 'PROTOCOL.json'
FREEZE = HERE / 'PREEXECUTION_FROZEN.json'
EXPECTED_PROTOCOL = 'd96c4d33ecc6aba557a15b882074b49231acda6665994237943bbf8f47ef51f4'
EXPECTED_CONTRACT = 'd4ff7556332f75447d93e0c6a8da4a0d96cb8a86b257f111809d388b7f2b80ce'
ZERO, ONE = D(0), D(1)
A, M, B = D('13.61'), D(18), D('24.58')
L, H = M - A, B - M
WMAX = L * H
SCALE = D('1e-64')
ALG_TOL, ROOT_RESIDUAL_TOL = D('1e-120'), D('1e-65')
CHECKS = []
COUNTS = {
    'variance_cases': 0,
    'jet_distinct_kernel_evaluations': 0,
    'scalar_log_kernel_evaluations': 0,
    'combined_kernel_evaluations': 0,
    'kernel_lookup_requests': 0,
    'comparison_centers': 0,
    'pointwise_dual_comparisons': 0,
    'mixture_cases': 0,
    'new_root_searches': 0,
    'new_derivative_sign_campaigns': 0,
    'dense_grid_or_LP_campaigns': 0,
    'old_module_imports': 0,
    'old_main_invocations': 0,
    'closed_suite_replays': 0,
    'native_runs': 0,
    'gas_IVP_runs': 0,
}


def binary64_real(value):
    return D.from_float(float(value))


N0 = binary64_real('0.05')
SHEAR = (binary64_real('1.01e-14') - binary64_real('0.99e-14')) / 2
Q = 2 * SHEAR**2
KAPPA = binary64_real('29979245800') * binary64_real('1e-4') * (1 - binary64_real('0.9'))
FACTOR = Q * N0 * KAPPA / 180
CHI = binary64_real('13.598434599702')
E0, YA, P = binary64_real('0.4298'), binary64_real('32.88'), binary64_real('2.963')
SIGMA0, AREA = binary64_real('5.475e4'), binary64_real('1e-18')
HI_CUT, HEI_CUT = binary64_real('13.60'), binary64_real('24.59')


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def jsonable(obj):
    if isinstance(obj, D):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    return obj


def condition(name, passed, **evidence):
    CHECKS.append({'name': name, 'pass': bool(passed), **evidence})


def close(name, actual, expected, tol=ALG_TOL, scale=None):
    if scale is None:
        scale = max(ONE, abs(actual), abs(expected))
    residual = actual - expected
    scaled_error = abs(residual) / scale
    condition(name, scaled_error <= tol, actual=actual, expected=expected,
              residual=residual, scale=scale, scaled_error=scaled_error, tolerance=tol)
    return scaled_error


def power(value, exponent):
    return (exponent * value.ln()).exp()


class Jet:
    """Four coefficients c[n]=D^n f/n!, with D=E d/dE."""
    size = 4

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
            raise TypeError('Only scalar division is needed')
        return Jet([x / scalar for x in self.c])

    def __pow__(self, exponent):
        exponent = D(exponent)
        base = self.c[0]
        if base <= 0:
            raise ValueError('Taylor power needs a positive base')
        remainder = self / base - 1
        binomial, term, series = ONE, Jet(1), Jet(1)
        for degree in range(1, self.size):
            term = term * remainder
            binomial *= (exponent - degree + 1) / degree
            series += binomial * term
        return power(base, exponent) * series


def jet_kernel(e, jx, jw):
    if not A <= e <= B or not HI_CUT < e < HEI_CUT:
        raise ValueError('Kernel energy left frozen analytic support')
    COUNTS['jet_distinct_kernel_evaluations'] += 1
    COUNTS['combined_kernel_evaluations'] += 1
    if COUNTS['jet_distinct_kernel_evaluations'] > 15:
        raise RuntimeError('Preregistered jet evaluation budget exceeded')
    ej = Jet([e / factorial(n) for n in range(4)])
    xj = ej / E0
    sigj = SIGMA0 * (xj - 1)**2 * xj**(P / 2 - binary64_real('5.5')) * (
        1 + (xj / YA)**D('0.5'))**(-P) * AREA
    fj = sigj * (jx + jw * (ej - CHI))
    dn = [fj.c[n] * factorial(n) for n in range(4)]
    return {'energy_eV': e, 'sigma_cm2': sigj.c[0], 'D_0_to_3_f': dn,
            'k_s-4': FACTOR * (dn[2] + 3 * dn[1]),
            'k_prime_s-4_eV-1': FACTOR * (dn[3] + 3 * dn[2]) / e}


def scalar_log_kernel(e, jx, jw):
    """Separate scalar expression, with no jet or numerical differencing."""
    if not A <= e <= B or not HI_CUT < e < HEI_CUT:
        raise ValueError('Scalar energy left frozen analytic support')
    COUNTS['scalar_log_kernel_evaluations'] += 1
    COUNTS['combined_kernel_evaluations'] += 1
    if COUNTS['scalar_log_kernel_evaluations'] > 5:
        raise RuntimeError('Preregistered scalar evaluation budget exceeded')
    x = e / E0
    z = (x / YA).sqrt()
    exponent = P / 2 - binary64_real('5.5')
    sigma = SIGMA0 * (x - 1)**2 * power(x, exponent) * power(1 + z, -P) * AREA
    ell1 = 2 * x / (x - 1) + exponent - P * z / (2 * (1 + z))
    ell2 = -2 * x / (x - 1)**2 - P * z / (4 * (1 + z)**2)
    ell3 = 2 * x * (x + 1) / (x - 1)**3 - P * z * (1 - z) / (8 * (1 + z)**3)
    h, t = jx + jw * (e - CHI), jw * e
    s2 = ell1**2 + ell2
    s3 = ell1**3 + 3 * ell1 * ell2 + ell3
    kval = FACTOR * sigma * ((s2 + 3 * ell1) * h + (2 * ell1 + 4) * t)
    kprime = FACTOR * sigma / e * ((s3 + 3 * s2) * h + (3 * s2 + 9 * ell1 + 4) * t)
    return {'energy_eV': e, 'sigma_cm2': sigma, 'D_log_sigma': ell1,
            'D2_log_sigma': ell2, 'D3_log_sigma': ell3,
            'k_s-4': kval, 'k_prime_s-4_eV-1': kprime}


def two_law(lower, upper):
    return [(lower, (upper - M) / (upper - lower)),
            (upper, (M - lower) / (upper - lower))]


def law_stats(label, law, target_variance, kernel):
    mass = sum((p for e, p in law), ZERO)
    mean = sum((p * e for e, p in law), ZERO)
    variance = sum((p * (e - M)**2 for e, p in law), ZERO)
    second = sum((p * e**2 for e, p in law), ZERO)
    response = sum((p * kernel(e)['k_s-4'] for e, p in law), ZERO)
    condition(label + '__nonnegative_supported', all(A <= e <= B and p >= 0 for e, p in law))
    close(label + '__mass', mass, ONE)
    close(label + '__mean', mean, M)
    close(label + '__variance', variance, target_variance)
    close(label + '__second_moment', second, M**2 + target_variance)
    close(label + '__photon_number', N0 * mass, N0)
    close(label + '__photon_energy', N0 * mean, N0 * M)
    return {'law': [{'energy_eV': e, 'probability': p, 'photon_number_per_H': N0*p}
                    for e, p in law],
            'positive_mass_support_eV': [e for e, p in law if p > 0],
            'probability_mass': mass, 'mean_energy_eV': mean, 'variance_eV2': variance,
            'raw_second_moment_eV2': second, 'total_photon_number_per_H': N0 * mass,
            'total_energy_eV_per_H': N0 * mean, 'response_s-4': response}


def make_quadratic(anchor, center, kernel):
    kc = kernel(center)
    c0, c1 = kc['k_s-4'], kc['k_prime_s-4_eV-1']
    c2 = (kernel(anchor)['k_s-4'] - c0 - c1 * (anchor - center)) / (anchor - center)**2
    return {'single_contact_eV': anchor, 'double_contact_eV': center,
            'c0_s-4': c0, 'c1_s-4_eV-1': c1, 'c2_s-4_eV-2': c2}


def quadratic(q, e):
    delta = e - q['double_contact_eV']
    return q['c0_s-4'] + q['c1_s-4_eV-1'] * delta + q['c2_s-4_eV-2'] * delta**2


def quadratic_prime(q, e):
    return q['c1_s-4_eV-1'] + 2 * q['c2_s-4_eV-2'] * (e - q['double_contact_eV'])


def expected_quadratic(q, variance):
    delta = M - q['double_contact_eV']
    return q['c0_s-4'] + q['c1_s-4_eV-1'] * delta + q['c2_s-4_eV-2'] * (variance + delta**2)


def check_quadratic(label, q, laws, variance, kernel):
    anchor, center = q['single_contact_eV'], q['double_contact_eV']
    close(label + '__single_contact', quadratic(q, anchor), kernel(anchor)['k_s-4'], scale=SCALE)
    close(label + '__double_contact_value', quadratic(q, center), kernel(center)['k_s-4'], scale=SCALE)
    close(label + '__double_contact_tangent', quadratic_prime(q, center),
          kernel(center)['k_prime_s-4_eV-1'], scale=SCALE / center)
    expectation = expected_quadratic(q, variance)
    sums = {}
    for law_label, law in laws.items():
        explicit = sum((p * quadratic(q, e) for e, p in law), ZERO)
        close(label + '__same_moments_' + law_label, explicit, expectation, scale=SCALE)
        sums[law_label] = explicit
    return {'moment_expression_s-4': expectation, 'explicit_law_sums_s-4': sums}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Refusing to overwrite existing scientific evidence')
    if file_hash(PROTOCOL) != EXPECTED_PROTOCOL:
        raise ValueError('Preregistered protocol identity mismatch')
    protocol = json.loads(PROTOCOL.read_text())
    freeze = json.loads(FREEZE.read_text())
    if freeze['first_scientific_execution_performed_at_freeze'] is not False:
        raise ValueError('Preexecution freeze must precede all PHYS26 science execution')
    identities = {}
    for row in freeze['files']:
        path = ROOT / row['path']
        actual = file_hash(path)
        if actual != row['sha256'] or path.stat().st_size != row['bytes']:
            raise ValueError('Frozen dependency mismatch: ' + row['path'])
        identities[row['path']] = actual
    for row in protocol['inputs']:
        if identities.get(row['path']) != row['sha256']:
            raise ValueError('Protocol dependency absent from freeze: ' + row['path'])
    if identities.get('PHYSICS_CONTRACT.json') != EXPECTED_CONTRACT:
        raise ValueError('Contract identity mismatch')
    identities['contributions/numerics/PREEXECUTION_FROZEN.json'] = file_hash(FREEZE)
    jj = json.loads((ROOT / 'inputs/PHYS22_INITIAL_COEFFICIENTS.json').read_text())
    jx, jw = (D(jj['results']['baseline_local']['J_nonphoto'][2][i]) for i in [0, 3])
    old = json.loads((ROOT / 'inputs/inherited/PHYS25_VARIANCE_CANDIDATE.json').read_text())
    comparison_energies = [D(value) for value in protocol['comparison_energy_centers_eV']]
    cases, energies = [], {A, M, B, *comparison_energies}
    for row in protocol['variance_cases']:
        variance = D(row['W_eV2'])
        if not ZERO <= variance <= WMAX:
            raise ValueError('Preregistered variance out of bounds')
        v, u = M + variance / L, M - variance / H
        pa, pb = two_law(A, v), two_law(u, B)
        energies.update(e for e, p in pa + pb)
        cases.append({'label': row['label'], 'variance': variance, 'source': row['source'],
                      'v': v, 'u': u, 'Pa': pa, 'Pb': pb})
    if len(cases) != 7 or len(comparison_energies) != 5 or len(energies) > 15:
        raise RuntimeError('Preregistered case or energy budget violated before evaluation')
    cache = {e: jet_kernel(e, jx, jw) for e in sorted(energies)}

    def kernel(e):
        COUNTS['kernel_lookup_requests'] += 1
        return cache[e]

    condition('fixed_Wmax', WMAX == D('28.8862'), actual_eV2=WMAX)
    condition('frozen_input_signs', jx < 0 < jw, Jx=jx, Jw=jw)
    comparison_rows, independent_errors = [], []
    for index, e in enumerate(comparison_energies):
        primary, separate = kernel(e), scalar_log_kernel(e, jx, jw)
        errors = {
            'sigma': close('separate_expression_' + str(index) + '__sigma',
                           separate['sigma_cm2'], primary['sigma_cm2'], scale=D('1e-18')),
            'k': close('separate_expression_' + str(index) + '__k',
                       separate['k_s-4'], primary['k_s-4'], scale=SCALE),
            'k_prime': close('separate_expression_' + str(index) + '__k_prime',
                             separate['k_prime_s-4_eV-1'], primary['k_prime_s-4_eV-1'], scale=SCALE/e),
        }
        independent_errors.extend(errors.values())
        comparison_rows.append({'energy_eV': e, 'jet': primary, 'scalar_log_expression': separate,
                                'scaled_errors': errors})
        COUNTS['comparison_centers'] += 1

    case_rows, response_by_label = [], {}
    for case in cases:
        label, variance, pa, pb = case['label'], case['variance'], case['Pa'], case['Pb']
        upper = law_stats(label + '__Pa', pa, variance, kernel)
        lower = law_stats(label + '__Pb', pb, variance, kernel)
        qa, qb = make_quadratic(A, case['v'], kernel), make_quadratic(B, case['u'], kernel)
        laws = {'Pa': pa, 'Pb': pb}
        eq_a = check_quadratic(label + '__Qa', qa, laws, variance, kernel)
        eq_b = check_quadratic(label + '__Qb', qb, laws, variance, kernel)
        close(label + '__Qa_attainment', eq_a['moment_expression_s-4'], upper['response_s-4'], scale=SCALE)
        close(label + '__Qb_attainment', eq_b['moment_expression_s-4'], lower['response_s-4'], scale=SCALE)
        point_rows = []
        for e in [A, M, B]:
            ka = kernel(e)['k_s-4']
            high_slack, low_slack = quadratic(qa, e) - ka, ka - quadratic(qb, e)
            condition(label + '__sample_Qa_minus_k__' + str(e), high_slack >= -ALG_TOL * SCALE,
                      energy_eV=e, slack_s_4=high_slack, tolerance_s_4=ALG_TOL*SCALE)
            condition(label + '__sample_k_minus_Qb__' + str(e), low_slack >= -ALG_TOL * SCALE,
                      energy_eV=e, slack_s_4=low_slack, tolerance_s_4=ALG_TOL*SCALE)
            point_rows.append({'energy_eV': e, 'Qa_minus_k_s-4': high_slack,
                               'k_minus_Qb_s-4': low_slack})
            COUNTS['pointwise_dual_comparisons'] += 2
        gap = upper['response_s-4'] - lower['response_s-4']
        if ZERO < variance < WMAX:
            condition(label + '__strict_interior_response_order', gap > 0, gap_s_4=gap)
        else:
            close(label + '__degenerate_equal_responses', gap, ZERO, scale=SCALE)
            target_support = [M] if variance == ZERO else [A, B]
            condition(label + '__degenerate_equal_positive_support',
                      upper['positive_mass_support_eV'] == target_support
                      and lower['positive_mass_support_eV'] == target_support,
                      target_support_eV=target_support)
        case_rows.append({'label': label, 'W_eV2': variance, 'source': case['source'],
                          'u_eV': case['u'], 'v_eV': case['v'], 'Pa': upper, 'Pb': lower,
                          'candidate_interval_s-4': [lower['response_s-4'], upper['response_s-4']],
                          'candidate_interval_width_s-4': gap, 'Qa': qa, 'Qb': qb,
                          'Qa_expectation': eq_a, 'Qb_expectation': eq_b,
                          'pointwise_dual_samples': point_rows,
                          'sample_classification': 'implementation checks at 3 energies, not a continuum proof'})
        response_by_label[label] = {'upper': upper['response_s-4'], 'lower': lower['response_s-4'],
                                    'case': case}
        COUNTS['variance_cases'] += 1

    star = response_by_label['inherited_Vstar']
    reverse = response_by_label['inherited_W0']
    close('inherited_Vstar_stored_variance', star['case']['variance'], D(old['primary_candidate']['variance_eV2']))
    close('inherited_W0_stored_variance', reverse['case']['variance'], D(old['opposite_endpoint_law']['variance_eV2']))
    close('inherited_v_root_formula', star['case']['v'], D(old['primary_anchored_root']['midpoint_eV']))
    close('inherited_u_root_formula', reverse['case']['u'], D(old['opposite_endpoint_root']['midpoint_eV']))
    close('inherited_Vstar_finite_response_residual', star['upper'], ZERO,
          tol=ROOT_RESIDUAL_TOL, scale=SCALE)
    close('inherited_W0_finite_response_residual', reverse['lower'], ZERO,
          tol=ROOT_RESIDUAL_TOL, scale=SCALE)
    close('inherited_Vstar_residual_consistency', star['upper'], D(old['primary_candidate']['response_s-4']), scale=SCALE)
    close('inherited_W0_residual_consistency', reverse['lower'], D(old['opposite_endpoint_law']['response_s-4']), scale=SCALE)
    condition('inherited_finite_boundary_residuals_are_not_exact_zero', star['upper'] != 0 and reverse['lower'] != 0,
              Vstar_response_s_4=star['upper'], W0_response_s_4=reverse['lower'])

    mixed = response_by_label['mixed_19_74']
    high, low, case = mixed['upper'], mixed['lower'], mixed['case']
    condition('W19_74_opposite_candidate_signs', low < 0 < high, lower_s_4=low, upper_s_4=high)
    alpha_zero = -low / (high - low)
    condition('W19_74_zero_mixture_weight_interior', ZERO < alpha_zero < ONE, alpha=alpha_zero)
    mixture_rows = []
    for label, alpha in [('quarter_upper', D('.25')), ('numerical_zero', alpha_zero)]:
        law = [(e, alpha * p) for e, p in case['Pa']] + [(e, (1-alpha)*p) for e, p in case['Pb']]
        stats = law_stats('mixture_' + label, law, case['variance'], kernel)
        affine = alpha * high + (1-alpha) * low
        close('mixture_' + label + '__affine_response', stats['response_s-4'], affine, scale=SCALE)
        condition('mixture_' + label + '__strict_response_between_candidates',
                  low < stats['response_s-4'] < high,
                  lower_s_4=low, response_s_4=stats['response_s-4'], upper_s_4=high)
        if label == 'numerical_zero':
            close('mixture_numerical_zero__response_residual', stats['response_s-4'], ZERO, scale=SCALE)
        mixture_rows.append({'label': label, 'alpha_Pa': alpha, 'alpha_Pb': 1-alpha,
                             'W_eV2': case['variance'], **stats,
                             'affine_response_s-4': affine,
                             'classification': 'Decimal implementation of a constructive convex mixture; finite numerical residual is not exact arithmetic'})
        COUNTS['mixture_cases'] += 1

    condition('preregistered_evaluation_budget', COUNTS['variance_cases'] == 7
              and COUNTS['comparison_centers'] == 5
              and COUNTS['jet_distinct_kernel_evaluations'] <= 15
              and COUNTS['scalar_log_kernel_evaluations'] == 5
              and COUNTS['combined_kernel_evaluations'] <= 20,
              actual_counts=dict(COUNTS))
    failed = [row['name'] for row in CHECKS if not row['pass']]
    result = {
        'task': 'REI-PHYS26-20261011',
        'evidence_class': ['numerically checked', 'implementation-verified'],
        'role': 'NONBLIND numerical-design contributor; not final decision reviewer',
        'python_version': platform.python_version(), 'decimal_precision': getcontext().prec,
        'identity_sha256': identities,
        'constants': {'support_eV': [A, B], 'mean_eV': M, 'L_eV': L, 'H_eV': H, 'Wmax_eV2': WMAX,
                      'N0_per_H': N0, 'q_s-2': Q, 'kappa_s-1_cm-2': KAPPA, 'prefactor': FACTOR,
                      'chi_eV': CHI, 'E0_eV': E0, 'ya': YA, 'P': P, 'J_h2_x': jx, 'J_h2_w': jw},
        'primary_kernel_cache': [cache[e] for e in sorted(cache)],
        'separate_expression_comparisons': comparison_rows,
        'variance_cases': case_rows,
        'inherited_boundary_residuals': {
            'Vstar_eV2': star['case']['variance'], 'Pa_response_s-4': star['upper'],
            'W0_eV2': reverse['case']['variance'], 'Pb_response_s-4': reverse['lower'],
            'source': 'Read PHYS25 stored decimal roots and variances; no search or bracket update',
            'classification': 'Finite numerical residuals only; exact root-defined laws belong to the theorem, not these decimal points'},
        'mixtures_at_W19_74': mixture_rows,
        'checks': CHECKS,
        'summary': {'total_checks': len(CHECKS), 'passed': len(CHECKS)-len(failed), 'failed': len(failed),
                    'failed_names': failed, 'all_pass': not failed,
                    'maximum_scaled_separate_expression_error': max(independent_errors),
                    'actual_counts': COUNTS},
        'claim_ceiling': protocol['claim_ceiling'],
        'global_optimality': 'Requires a separate continuum derivation; samples do not establish global envelopes.',
        'physical_admission': 'HOLD',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(jsonable(result), stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(jsonable(result['summary']), ensure_ascii=False))
    raise SystemExit(0 if not failed else 1)


if __name__ == '__main__':
    main()
