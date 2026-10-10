#!/usr/bin/env python3
"""PHYS24 bounded fixed-moment HeIII numerics, using the standard library.

No PHYS23 code is imported or executed.  Its numerical Jacobian, mono-root
bracket and one spectral example are consumed as closed inputs.  New curvature
is computed via original-fit Taylor jets and directly corroborated by original-
fit logarithmic finite differences.  Finite samples do not certify continuum
convexity; the envelope's global interpretation requires the separate proof.
"""
from __future__ import annotations

import argparse
from decimal import Decimal as D, ROUND_FLOOR, getcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import platform

getcontext().prec = 160
ROOT = Path(__file__).resolve().parents[2]
J_INPUT = ROOT / 'inputs/PHYS22_INITIAL_COEFFICIENTS.json'
OLD_INPUT = ROOT / 'inputs/inherited/PHYS23_SPECTRAL_RESPONSE.json'
CONTRACT = ROOT / 'PHYSICS_CONTRACT.json'
PROTOCOL = Path(__file__).with_name('PROTOCOL.json')
EXPECTED = {
    'J_input': '6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79',
    'inherited_spectral_results': '55670faaadc079bf08f2ea5ef98fe765f2d83f74928ebd4862f4d3fee44c0541',
    'contract': 'fd60772fa082a651034b21b965133e57cc0c3e37bb14cdab531a5ca3965266e2',
    'protocol': '4ad6369cfeea29e5860dc72b9d2aef37fcc73845889391940538ecb6107d934a',
}
CHECKS = []
ZERO, ONE = D(0), D(1)
L, U = D('13.61'), D('24.58')
ALG_TOL, ANCHOR_TOL, FD_TOL = D('1e-130'), D('1e-95'), D('1e-42')
FD_H = D('1e-5')
FD_ENERGIES = [L, D(14), D(16), D(18), D(20), D(23), U]
OFFSETS = list(range(-6, 7))


def b(x):
    return D.from_float(float(x))


N0 = b('0.05')
SH = (b('1.01e-14') - b('0.99e-14')) / 2
Q = 2 * SH**2
KAPPA = b('29979245800') * b('1e-4') * (1 - b('0.9'))
FACTOR = Q * N0 * KAPPA / 180
CHI = b('13.598434599702')
E0, YA, PP = b('0.4298'), b('32.88'), b('2.963')
SIG0, CM2 = b('5.475e4'), b('1e-18')
HI_CUT, HEI_CUT = b('13.60'), b('24.59')


def file_hash(p):
    return sha256(p.read_bytes()).hexdigest()


def condition(name, passed, **evidence):
    CHECKS.append({'name': name, 'pass': bool(passed), **evidence})


def close(name, actual, expected, tol=ALG_TOL, scale=None):
    if scale is None:
        scale = max(abs(actual), abs(expected))
    error = abs(actual - expected) / scale if scale else abs(actual - expected)
    condition(name, error <= tol, actual=actual, expected=expected,
              scaled_error=error, tolerance=tol, scale=scale)


def power(x, exponent):
    return (exponent * x.ln()).exp()


def sigma_direct(e):
    if not HI_CUT < e < HEI_CUT:
        raise ValueError('original-fit evaluation left the analytic HI-only band')
    x = e / E0
    return SIG0 * (x - 1)**2 * power(x, PP / 2 - b('5.5')) * power(
        1 + (x / YA).sqrt(), -PP) * CM2


def f_direct(e, jx, jw):
    return sigma_direct(e) * (jx + jw * (e - CHI))


class Jet:
    """Degree-four ordinary Taylor coefficients, c[n]=D^n f/n!."""
    size = 5

    def __init__(self, value):
        if isinstance(value, (list, tuple)):
            self.c = list(value) + [ZERO] * (self.size - len(value))
        else:
            self.c = [D(value), ZERO, ZERO, ZERO, ZERO]

    @staticmethod
    def lift(value):
        return value if isinstance(value, Jet) else Jet(value)

    def __add__(self, other):
        other = self.lift(other)
        return Jet([a + b_ for a, b_ in zip(self.c, other.c)])

    __radd__ = __add__

    def __neg__(self):
        return Jet([-a for a in self.c])

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
            raise TypeError('this implementation only needs scalar division')
        return Jet([a / scalar for a in self.c])

    def __pow__(self, exponent):
        exponent = D(exponent)
        base = self.c[0]
        if base <= 0:
            raise ValueError('Taylor power needs a strictly positive base')
        u = self / base - 1
        binomial, term, series = ONE, Jet(1), Jet(1)
        for degree in range(1, self.size):
            term = term * u
            binomial *= (exponent - degree + 1) / degree
            series += binomial * term
        return power(base, exponent) * series


def response(e, jx, jw):
    """Primary path: differentiate the original fit through Taylor algebra."""
    if not L <= e <= U:
        raise ValueError('response mean outside contract interval')
    ej = Jet([e / factorial(n) for n in range(5)])  # e*exp(t)
    xj = ej / E0
    sigj = SIG0 * (xj - 1)**2 * xj**(PP / 2 - b('5.5')) * (
        1 + (xj / YA)**D('0.5'))**(-PP) * CM2
    fj = sigj * (jx + jw * (ej - CHI))
    dn = [fj.c[n] * factorial(n) for n in range(5)]
    k = FACTOR * (dn[2] + 3 * dn[1])
    kp = FACTOR * (dn[3] + 3 * dn[2]) / e
    kpp = FACTOR * (dn[4] + 2 * dn[3] - 3 * dn[2]) / e**2
    return {'energy_eV': e, 'sigma_cm2': sigj.c[0],
            'D_order_0_to_4_f': dn, 'k_s-4': k,
            'k_prime_s-4_eV-1': kp, 'k_second_s-4_eV-2': kpp,
            'g_s-2': k * 45 / (Q * N0)}


def exact_weights(order):
    """Solve exact polynomial moment equations; no imported stencil table."""
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


def fd_second(e, step, jx, jw, weights):
    values = [f_direct(e * (D(offset) * step).exp(), jx, jw) for offset in OFFSETS]
    ders = {}
    for order, ww in weights.items():
        ders[order] = sum((D(w.numerator) / D(w.denominator) * val
                           for w, val in zip(ww, values)), ZERO) / step**order
    return FACTOR * (ders[4] + 2 * ders[3] - 3 * ders[2]) / e**2


def endpoint_law(mean):
    return [(L, (U - mean) / (U - L)), (U, (mean - L) / (U - L))]


def law_values(law, jx, jw):
    mass = sum((p for e, p in law), ZERO)
    mean_numerator = sum((e * p for e, p in law), ZERO)
    kval = sum((p * response(e, jx, jw)['k_s-4'] for e, p in law), ZERO)
    return {'law': [{'energy_eV': e, 'probability': p, 'photon_number_per_H': p * N0}
                    for e, p in law], 'probability_mass': mass,
            'mean_energy_eV': mean_numerator / mass,
            'total_photon_number_per_H': N0 * mass,
            'total_energy_eV_per_H': N0 * mean_numerator, 'k_s-4': kval}


def check_law(label, law, mean, jx, jw, tol=ALG_TOL):
    ans = law_values(law, jx, jw)
    close(label + '__mass', ans['probability_mass'], ONE, tol)
    close(label + '__mean', ans['mean_energy_eV'], mean, tol)
    close(label + '__N0', ans['total_photon_number_per_H'], N0, tol)
    close(label + '__U0', ans['total_energy_eV_per_H'], N0 * mean, tol)
    condition(label + '__nonnegative_probabilities', all(p >= 0 for e, p in law))
    return ans


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
        raise FileExistsError('refusing to overwrite first evidence: ' + str(args.output))
    identities = {'J_input': file_hash(J_INPUT),
                  'inherited_spectral_results': file_hash(OLD_INPUT),
                  'contract': file_hash(CONTRACT), 'protocol': file_hash(PROTOCOL)}
    if identities != EXPECTED:
        raise ValueError('frozen input identity mismatch: ' + repr(identities))
    identities['code'] = file_hash(Path(__file__))
    old = json.loads(OLD_INPUT.read_text())
    jj = json.loads(J_INPUT.read_text())['results']['baseline_local']['J_nonphoto']
    jx, jw = D(jj[2][0]), D(jj[2][3])
    condition('inherited_J_signs', jx < 0 < jw, jx=jx, jw=jw)

    weights = {order: exact_weights(order) for order in [2, 3, 4]}
    moment_rows = []
    for order, ww in weights.items():
        for degree in range(13):
            val = sum((w * F(i)**degree for i, w in zip(OFFSETS, ww)), F(0))
            expected = F(factorial(order) if degree == order else 0)
            moment_rows.append({'order': order, 'degree': degree,
                                'actual': val, 'expected': expected, 'pass': val == expected})
    condition('new_FD_exact_polynomial_moments', all(r['pass'] for r in moment_rows),
              count=len(moment_rows))
    stencil_min = L * (-6 * FD_H).exp()
    stencil_max = U * (6 * FD_H).exp()
    condition('all_FD_stencils_inside_analytic_HI_band',
              HI_CUT < stencil_min <= stencil_max < HEI_CUT,
              minimum_eV=stencil_min, maximum_eV=stencil_max,
              lower_cutoff_eV=HI_CUT, upper_cutoff_eV=HEI_CUT)
    curvatures = []
    for e in FD_ENERGIES:
        primary = response(e, jx, jw)
        coarse = fd_second(e, FD_H, jx, jw, weights)
        fine = fd_second(e, FD_H / 2, jx, jw, weights)
        extrapolated = (1024 * fine - coarse) / 1023
        before = len(CHECKS)
        close('curvature__' + str(e), extrapolated,
              primary['k_second_s-4_eV-2'], FD_TOL)
        err = CHECKS[before]['scaled_error']
        condition('positive_curvature_in_both_paths__' + str(e),
                  primary['k_second_s-4_eV-2'] > 0 and extrapolated > 0)
        curvatures.append({**primary, 'FD_h': coarse, 'FD_h_over_2': fine,
                           'FD_Richardson': extrapolated, 'scaled_error': err})

    left, right = response(L, jx, jw), response(U, jx, jw)
    kl, ku = left['k_s-4'], right['k_s-4']
    chord_slope = (ku - kl) / (U - L)

    def chord(mean):
        return ((U - mean) * kl + (mean - L) * ku) / (U - L)

    condition('endpoint_signs_and_decreasing_chord', kl > 0 > ku and chord_slope < 0,
              left_k_s_4=kl, right_k_s_4=ku, chord_slope_s_4_eV_1=chord_slope)
    eplus = L + (U - L) * kl / (kl - ku)
    grid = D('1e-20')
    eplus_left = (eplus / grid).to_integral_value(rounding=ROUND_FLOOR) * grid
    eplus_right = eplus_left + grid
    close('chord_zero_residual', chord(eplus), ZERO,
          scale=max(abs(kl), abs(ku)))
    condition('chord_zero_focused_numeric_bracket',
              L < eplus_left < eplus < eplus_right < U
              and chord(eplus_left) > 0 > chord(eplus_right),
              bracket_eV=[eplus_left, eplus_right],
              endpoint_chord_s_4=[chord(eplus_left), chord(eplus_right)])

    inherited_root = old['HeIII_numerical_roots'][0]
    emin_left, emin_right = map(D, inherited_root['final_bracket_eV'])
    eminus = D(inherited_root['midpoint_eV'])
    k_emin_left = response(emin_left, jx, jw)['k_s-4']
    k_emin_right = response(emin_right, jx, jw)['k_s-4']
    condition('one_focused_inherited_mono_bracket_consistency',
              L < emin_left < emin_right < eplus < U
              and k_emin_left > 0 > k_emin_right,
              inherited_bracket_eV=[emin_left, emin_right],
              primary_endpoint_k_s_4=[k_emin_left, k_emin_right],
              root_search_iterations=0)

    inherited_anchor = old['same_mean_HeIII_sign_counterexample']
    anchor_mean = D(inherited_anchor['mixture']['mean_energy_eV'])
    means = [('left_endpoint', L), ('soft_example_14', D(14)),
             ('inherited_mono_root_midpoint', eminus), ('mean_16', D(16)),
             ('inherited_same_N_U_mean', anchor_mean), ('mean_18', D(18)),
             ('mean_19', D(19)), ('computed_chord_zero_mean', eplus),
             ('mean_20', D(20)), ('mean_22', D(22)), ('right_endpoint', U)]
    envelope_rows = []
    for label, mean in means:
        mono = response(mean, jx, jw)
        ep = check_law('endpoint_law__' + label, endpoint_law(mean), mean, jx, jw)
        close('endpoint_law_chord__' + label, ep['k_s-4'], chord(mean),
              scale=max(abs(kl), abs(ku)))
        gap = chord(mean) - mono['k_s-4']
        condition('sample_envelope_gap__' + label,
                  abs(gap) <= ALG_TOL * max(abs(kl), abs(ku))
                  if mean in [L, U] else gap > 0, gap_s_4=gap)
        envelope_rows.append({'label': label, 'mean_energy_eV': mean,
                              'lower_candidate_k_s-4': mono['k_s-4'],
                              'upper_candidate_k_s-4': chord(mean),
                              'candidate_width_s-4': gap,
                              'endpoint_probability_L': (U-mean)/(U-L),
                              'endpoint_probability_U': (mean-L)/(U-L)})

    # Fixed moments and response linearity across the full candidate interval.
    m = D(18)
    km, bm = response(m, jx, jw)['k_s-4'], chord(m)
    theta_zero = -km / (bm - km)
    condition('attainability_mean_has_both_candidate_signs', km < 0 < bm,
              mean_eV=m, lower_candidate=km, upper_candidate=bm,
              theta_zero=theta_zero)
    attainable = []
    for theta in [ZERO, D('0.25'), D('0.5'), D('0.75'), ONE, theta_zero]:
        law = [(m, 1-theta)] + [(e, theta*p) for e, p in endpoint_law(m)]
        val = check_law('attainability_theta_' + str(theta), law, m, jx, jw)
        expected = (1-theta)*km + theta*bm
        close('attainability_response_theta_' + str(theta), val['k_s-4'], expected,
              scale=max(abs(km), abs(bm)))
        attainable.append({'theta': theta, **val, 'linear_target_k_s-4': expected})
    close('attainability_zero_response', attainable[-1]['k_s-4'], ZERO,
          scale=max(abs(km), abs(bm)))

    distinct_laws = [
        ('interior_two_line_14_24', [(D(14), D('0.6')), (D(24), D('0.4'))]),
        ('interior_three_line_14_18_24', [(D(14), D('0.3')), (D(18), D('0.5')),
                                       (D(24), D('0.2'))]),
    ]
    distinct = []
    for label, law in distinct_laws:
        val = check_law(label, law, m, jx, jw)
        condition(label + '__strict_candidate_bounds', km < val['k_s-4'] < bm,
                  lower_gap_s_4=val['k_s-4'] - km, upper_gap_s_4=bm - val['k_s-4'])
        distinct.append({'label': label, **val})

    # Exactly one inherited PHYS23 anchor, no other closed-suite replay.
    oldmix = inherited_anchor['mixture']
    law = [(D(e), D(n)/N0) for e, n in zip(oldmix['energies_eV'],
                                         oldmix['photon_number_weights_per_H'])]
    anchor = check_law('single_inherited_counterexample', law, anchor_mean, jx, jw, ANCHOR_TOL)
    anchor_mono = response(anchor_mean, jx, jw)['k_s-4']
    close('single_inherited_counterexample__mixture_response', anchor['k_s-4'],
          D(oldmix['HeIII_t4_s-4']), ANCHOR_TOL)
    close('single_inherited_counterexample__mono_response', anchor_mono,
          D(inherited_anchor['same_N_and_U_mean_energy_monoenergetic']['HeIII_t4_s-4']),
          ANCHOR_TOL)
    condition('single_inherited_counterexample__opposite_signs_inside_candidates',
              anchor_mono < 0 < anchor['k_s-4'] < chord(anchor_mean))

    failed = [row['name'] for row in CHECKS if not row['pass']]
    result = {
        'task': 'REI-PHYS24-20261011',
        'evidence_class': 'new focused numerical corroboration; continuum envelope conditional on separate curvature certificate',
        'python_version': platform.python_version(),
        'decimal_precision': getcontext().prec,
        'identity_sha256': identities,
        'constants': {'N0_per_H': N0, 'q_s-2': Q, 'kappa_cm-2_s-1': KAPPA,
                      'prefactor_q_N0_kappa_over_180': FACTOR,
                      'chi_eV': CHI, 'J_h2_x_s-1': jx, 'J_h2_w_H_eV-1_s-1': jw,
                      'HI_cutoff_eV': HI_CUT, 'HeI_cutoff_eV': HEI_CUT},
        'derivative_identity': "k''=(q N0 kappa/(180 E^2)) (D^4+2D^3-3D^2) f; f=sigma[Jx+Jw(E-chi)]",
        'exact_stencil_weights': weights,
        'exact_stencil_moments': moment_rows,
        'new_curvature_samples': curvatures,
        'endpoint_values': {'left': left, 'right': right},
        'endpoint_chord': {'formula': '[(U-mean) k(L)+(mean-L) k(U)]/(U-L)',
                           'slope_s-4_eV-1': chord_slope},
        'mono_zero_inherited': {**inherited_root,
                               'use': 'closed numerical bracket; one focused endpoint consistency, no new root search',
                               'PHYS24_endpoint_k_s-4': [k_emin_left, k_emin_right]},
        'endpoint_chord_zero': {
            'mean_eV': eplus, 'formula': 'L+(U-L) k(L)/(k(L)-k(U))',
            'numerical_bracket_eV': [eplus_left, eplus_right],
            'bracket_width_eV': grid,
            'bracket_chord_s-4': [chord(eplus_left), chord(eplus_right)],
            'residual_k_s-4': chord(eplus),
            'probability_L': (U-eplus)/(U-L), 'probability_U': (eplus-L)/(U-L),
            'claim_level': 'numerical evaluation conditional on numerical J; bracket is not a rigorous interval proof'},
        'envelope_samples': envelope_rows,
        'full_interval_attainability_samples': attainable,
        'additional_moment_laws': distinct,
        'single_inherited_anchor': {'new_mixture': anchor, 'new_mono_k_s-4': anchor_mono,
                                    'candidate_upper_k_s-4': chord(anchor_mean)},
        'sign_partition_conditional_on_continuum_convexity': [
            {'mean_region': '[L,E_minus)', 'attainable_signs': ['positive'],
             'equality_law': None},
            {'mean_region': 'E_minus', 'attainable_signs': ['zero','positive'],
             'equality_law': 'mono delta_E_minus uniquely gives zero'},
            {'mean_region': '(E_minus,E_plus)', 'attainable_signs': ['negative','zero','positive'],
             'equality_law': 'convex mixture of mono and endpoint law gives a zero'},
            {'mean_region': 'E_plus', 'attainable_signs': ['negative','zero'],
             'equality_law': 'endpoint law uniquely gives zero'},
            {'mean_region': '(E_plus,U]', 'attainable_signs': ['negative'],
             'equality_law': None}],
        'checks': CHECKS,
        'summary': {'passed': len(CHECKS)-len(failed), 'total': len(CHECKS),
                    'failed': failed, 'maximum_FD_scaled_error': max(
                        row['scaled_error'] for row in curvatures),
                    'minimum_sampled_k_second_s-4_eV-2': min(
                        row['k_second_s-4_eV-2'] for row in curvatures),
                    'new_FD_curvature_samples': len(curvatures),
                    'new_iterative_root_searches': 0,
                    'new_native_runs': 0, 'new_gas_IVP_runs': 0,
                    'old_code_imports': 0, 'old_main_invocations': 0,
                    'closed_proof_suite_replays': 0,
                    'continuum_convexity_claim_from_sampling': False,
                    'physical_status': 'HOLD'},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(jsonable(result), indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(jsonable(result['summary']), indent=2))
    print('endpoint_chord_zero_mean_eV=' + str(eplus))
    print('output_sha256=' + file_hash(args.output))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
