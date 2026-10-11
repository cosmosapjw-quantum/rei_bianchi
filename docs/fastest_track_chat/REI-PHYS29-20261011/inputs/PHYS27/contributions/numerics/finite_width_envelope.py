#!/usr/bin/env python3
"""PHYS27: one preregistered uniform-band numerical experiment, stdlib only.

The degree-three log Taylor jet is explicitly adapted from the read PHYS26
pure code. No historical module, main, suite, or physical root is invoked.
The independent Simpson path uses a separately expressed scalar log derivative
of the same original HI fit. Decimal precision and rule comparisons are
numerical evidence, not directed interval or physical uncertainty certificates.
"""
from __future__ import annotations

import argparse
from decimal import Decimal as D, getcontext
from hashlib import sha256
import json
from math import cos, factorial, pi
from pathlib import Path
import platform

getcontext().prec = 80
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXPECTED_CONTRACT = '46fe6fb98a78ca549f27ed78968850c14bdc12cdd3250892f28e239574005443'
EXPECTED_PROTOCOL = '523b827474b1db4f935a5b79f623cd27ea7dd04f8a0a5b822da33181deecda3b'
ZERO, ONE = D(0), D(1)
A, M, B, DELTA = D('13.61'), D(18), D('24.58'), D('0.05')
AC, BC = A + DELTA, B - DELTA
L, H, L0, H0 = M - AC, BC - M, M - A, B - M
OFFSET, VMAX = DELTA**2 / 3, L * H
WMIN, WMAX = OFFSET, VMAX + OFFSET
SCALE = D('1e-64')
ALG_TOL = D('1e-60')
GL_TOL, SIMPSON_TOL = D('1e-55'), D('1e-22')
NODE_TOL = D('1e-73')
CHECKS = []
COUNTS = {
    'new_scientific_main_invocations': 1,
    'new_physical_root_searches': 0,
    'physical_root_iterations': {},
    'quadrature_node_root_solutions': 0,
    'quadrature_node_newton_iterations': 0,
    'primary_jet_kernel_evaluations': 0,
    'independent_scalar_kernel_evaluations': 0,
    'combined_kernel_evaluations': 0,
    'gauss_average_evaluations_by_order': {'16': 0, '24': 0},
    'gauss_average_lookup_requests': 0,
    'independent_quadrature_centers': 0,
    'physical_variance_cases': 0,
    'mixture_cases': 0,
    'old_module_imports': 0,
    'old_main_invocations': 0,
    'closed_suite_replays': 0,
    'old_physical_root_searches': 0,
    'new_derivative_sign_campaigns': 0,
    'native_runs': 0,
    'gas_IVP_runs': 0,
    'dense_LP_or_multiple_parameter_campaigns': 0,
}


def f64(value):
    return D.from_float(float(value))


N0 = f64('0.05')
SHEAR = (f64('1.01e-14') - f64('0.99e-14')) / 2
Q = 2 * SHEAR**2
KAPPA = f64('29979245800') * f64('1e-4') * (1 - f64('0.9'))
FACTOR = Q * N0 * KAPPA / 180
CHI = f64('13.598434599702')
E0, YA, P = f64('0.4298'), f64('32.88'), f64('2.963')
SIGMA0, AREA = f64('5.475e4'), f64('1e-18')
HI_CUT, HEI_CUT = f64('13.60'), f64('24.59')


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def serial(obj):
    if isinstance(obj, D):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): serial(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serial(v) for v in obj]
    return obj


def check(name, passed, **evidence):
    CHECKS.append({'name': name, 'pass': bool(passed), **evidence})


def close(name, actual, expected, tol=ALG_TOL, scale=None):
    scale = max(ONE, abs(actual), abs(expected)) if scale is None else scale
    error = abs(actual - expected) / scale
    check(name, error <= tol, actual=actual, expected=expected,
          residual=actual-expected, scale=scale, scaled_error=error, tolerance=tol)
    return error


def power(value, exponent):
    return (D(exponent) * value.ln()).exp()


class Jet:
    """c[n]=(E d/dE)^n f / n!, n=0,...,3."""
    size = 4

    def __init__(self, value):
        if isinstance(value, (list, tuple)):
            if len(value) > self.size:
                raise ValueError('Jet coefficient overflow')
            self.c = list(value) + [ZERO] * (self.size-len(value))
        else:
            self.c = [D(value)] + [ZERO] * (self.size-1)

    @staticmethod
    def lift(value):
        return value if isinstance(value, Jet) else Jet(value)

    def __add__(self, other):
        other = self.lift(other)
        return Jet([a+b for a, b in zip(self.c, other.c)])

    __radd__ = __add__

    def __neg__(self):
        return Jet([-c for c in self.c])

    def __sub__(self, other):
        return self + -self.lift(other)

    def __rsub__(self, other):
        return self.lift(other) + -self

    def __mul__(self, other):
        other = self.lift(other)
        return Jet([sum((self.c[j]*other.c[n-j] for j in range(n+1)), ZERO)
                    for n in range(self.size)])

    __rmul__ = __mul__

    def __truediv__(self, value):
        if isinstance(value, Jet):
            raise TypeError('Only scalar division is required')
        return Jet([c/value for c in self.c])

    def __pow__(self, exponent):
        exponent = D(exponent)
        base = self.c[0]
        if base <= 0:
            raise ValueError('Positive Taylor base required')
        remainder = self/base - 1
        coefficient, term, series = ONE, Jet(1), Jet(1)
        for degree in range(1, self.size):
            coefficient *= (exponent-degree+1)/degree
            term = term * remainder
            series += coefficient * term
        return power(base, exponent) * series


def count_kernel(kind, energy):
    if not A <= energy <= B or not HI_CUT < energy < HEI_CUT:
        raise ValueError('Kernel left the frozen analytic HI interval')
    COUNTS[kind] += 1
    COUNTS['combined_kernel_evaluations'] += 1
    if COUNTS['combined_kernel_evaluations'] > 20000:
        raise RuntimeError('Frozen kernel budget exceeded')


def jet_kernel(energy, jx, jw):
    count_kernel('primary_jet_kernel_evaluations', energy)
    ej = Jet([energy/factorial(n) for n in range(4)])
    xj = ej/E0
    sigma = SIGMA0 * (xj-1)**2 * xj**(P/2-f64('5.5')) * (
        1+(xj/YA)**D('0.5'))**(-P) * AREA
    product = sigma * (jx+jw*(ej-CHI))
    dn = [product.c[n]*factorial(n) for n in range(4)]
    return {'k': FACTOR*(dn[2]+3*dn[1]),
            'kp': FACTOR*(dn[3]+3*dn[2])/energy,
            'sigma': sigma.c[0]}


def scalar_kernel(energy, jx, jw):
    """Separate scalar log-derivative path; no Jet or finite differences."""
    count_kernel('independent_scalar_kernel_evaluations', energy)
    x = energy/E0
    z = (x/YA).sqrt()
    r = P/2-f64('5.5')
    sigma = SIGMA0*(x-1)**2*power(x, r)*power(1+z, -P)*AREA
    ell1 = 2*x/(x-1)+r-P*z/(2*(1+z))
    ell2 = -2*x/(x-1)**2-P*z/(4*(1+z)**2)
    ell3 = 2*x*(x+1)/(x-1)**3-P*z*(1-z)/(8*(1+z)**3)
    s2, s3 = ell1**2+ell2, ell1**3+3*ell1*ell2+ell3
    h, t = jx+jw*(energy-CHI), jw*energy
    return {'k': FACTOR*sigma*((s2+3*ell1)*h+(2*ell1+4)*t),
            'kp': FACTOR*sigma/energy*((s3+3*s2)*h+(3*s2+9*ell1+4)*t),
            'sigma': sigma}


def legendre(n, x):
    previous, current = ONE, x
    if n == 0:
        return ONE, ZERO
    for degree in range(2, n+1):
        previous, current = current, ((2*degree-1)*x*current-(degree-1)*previous)/degree
    derivative = n*(x*current-previous)/(x*x-1)
    return current, derivative


def gauss_rule(n):
    """Decimal Newton roots; binary64 cosine is an initial seed only."""
    nodes, node_records = [], []
    for index in range(1, n//2+1):
        seed = D(str(cos(pi*(index-0.25)/(n+0.5))))
        z = seed
        for iteration in range(1, 31):
            value, derivative = legendre(n, z)
            correction = value/derivative
            z -= correction
            COUNTS['quadrature_node_newton_iterations'] += 1
            if abs(correction) <= NODE_TOL:
                break
        else:
            raise RuntimeError('Gauss node Newton limit exceeded')
        value, derivative = legendre(n, z)
        weight = 2/((1-z*z)*derivative**2)
        nodes.extend([(-z, weight), (z, weight)])
        node_records.append({'positive_node': z, 'seed': seed, 'iterations': iteration,
                             'polynomial_residual': value, 'weight': weight})
        COUNTS['quadrature_node_root_solutions'] += 1
    nodes.sort()
    check('GL'+str(n)+'__distinct_supported_positive',
          len(set(x for x, w in nodes)) == n and all(-1 < x < 1 and w > 0 for x, w in nodes))
    moment_errors = []
    for degree in range(2*n):
        actual = sum((w*x**degree for x, w in nodes), ZERO)
        expected = D(2)/D(degree+1) if degree % 2 == 0 else ZERO
        moment_errors.append(close('GL'+str(n)+'__polynomial_degree_'+str(degree), actual, expected))
    return nodes, {'order': n, 'nodes_and_weights': [{'x': x, 'w': w} for x, w in nodes],
                   'positive_node_solutions': node_records,
                   'maximum_polynomial_exactness_scaled_error': max(moment_errors),
                   'checked_degrees': [0, 2*n-1],
                   'weight_sum': sum((w for x, w in nodes), ZERO),
                   'classification': 'Numerical polynomial checks; not directed interval node enclosures'}


def bisect_physical(label, function, lo, hi, physical_map):
    COUNTS['new_physical_root_searches'] += 1
    if COUNTS['new_physical_root_searches'] > 2:
        raise RuntimeError('Physical root count exceeded')
    flo, fhi = function(lo), function(hi)
    initial = {'center_eV': [lo, hi], 'F_values_s-4_eV': [flo, fhi]}
    check(label+'__initial_opposite_signs', flo*fhi < 0, **initial)
    if flo*fhi >= 0:
        raise RuntimeError('Preregistered physical root bracket failed')
    history = []
    for iteration in range(1, 81):
        mid = (lo+hi)/2
        value = function(mid)
        history.append({'iteration': iteration, 'center_eV': mid, 'F_s-4_eV': value})
        if value == 0:
            lo = hi = mid
            flo = fhi = value
            break
        if flo*value < 0:
            hi, fhi = mid, value
        else:
            lo, flo = mid, value
    mid = (lo+hi)/2
    fmid = function(mid)
    COUNTS['physical_root_iterations'][label] = iteration
    ordered_w = sorted([physical_map(lo), physical_map(hi)])
    check(label+'__final_numerical_bracket', flo*fhi <= 0, F_low=flo, F_high=fhi)
    check(label+'__iteration_budget', iteration <= 100, actual_iterations=iteration)
    check(label+'__narrow_center_bracket', hi-lo <= D('1e-22'), width_eV=hi-lo)
    return {'name': label, 'midpoint_center_eV': mid, 'midpoint_F_s-4_eV': fmid,
            'midpoint_physical_variance_eV2': physical_map(mid),
            'initial_numerical_bracket': initial,
            'final_center_bracket_eV': [lo, hi], 'final_F_values_s-4_eV': [flo, fhi],
            'final_center_bracket_width_eV': hi-lo,
            'final_physical_variance_bracket_eV2': ordered_w,
            'final_physical_variance_bracket_width_eV2': ordered_w[1]-ordered_w[0],
            'iterations': iteration, 'history': history,
            'classification': 'Finite Decimal quadrature root bracket; not a certified interval enclosure'}


def two_law(left, right):
    return [(left, (right-M)/(right-left)), (right, (M-left)/(right-left))]


def band_law_stats(label, law, physical_variance, averaged):
    mass = sum((p for c, p in law), ZERO)
    mean = sum((p*c for c, p in law), ZERO)
    variance = sum((p*(c-M)**2 for c, p in law), ZERO)
    direct_mass = direct_mean = direct_var = direct_second = ZERO
    bands = []
    response = ZERO
    for center, probability in law:
        lower, upper = center-DELTA, center+DELTA
        density = probability/(2*DELTA)
        direct_mass += density*(upper-lower)
        direct_mean += density*(upper**2-lower**2)/2
        direct_var += density*((upper-M)**3-(lower-M)**3)/3
        direct_second += density*(upper**3-lower**3)/3
        kbar = averaged(center)['k']
        response += probability*kbar
        bands.append({'center_eV': center, 'band_eV': [lower, upper],
                      'probability': probability, 'density_eV-1': density,
                      'photon_number_per_H': N0*probability,
                      'photon_density_per_H_eV': N0*density, 'kbar_s-4': kbar})
    check(label+'__nonnegative_supported_bands', all(
        AC <= c <= BC and p >= 0 and A <= c-DELTA and c+DELTA <= B for c, p in law))
    close(label+'__center_mass', mass, ONE)
    close(label+'__center_mean', mean, M)
    close(label+'__center_variance', variance, physical_variance-OFFSET)
    close(label+'__band_integrated_mass', direct_mass, ONE)
    close(label+'__band_integrated_mean', direct_mean, M)
    close(label+'__band_integrated_variance', direct_var, physical_variance)
    close(label+'__variance_decomposition', direct_var, variance+OFFSET)
    close(label+'__band_integrated_second_moment', direct_second, M**2+physical_variance)
    close(label+'__total_photons', N0*direct_mass, N0)
    close(label+'__total_energy', N0*direct_mean, N0*M)
    return {'bands': bands, 'positive_mass_centers_eV': [c for c, p in law if p > 0],
            'center_mass': mass, 'center_mean_eV': mean, 'center_variance_eV2': variance,
            'band_integrated_mass': direct_mass, 'band_integrated_mean_eV': direct_mean,
            'band_integrated_variance_eV2': direct_var,
            'band_integrated_second_moment_eV2': direct_second,
            'total_photon_number_per_H': N0*direct_mass,
            'total_energy_eV_per_H': N0*direct_mean, 'response_s-4': response}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Refusing to overwrite scientific evidence')
    protocol_path, freeze_path = HERE/'PROTOCOL.json', HERE/'PREEXECUTION_FROZEN.json'
    if digest(protocol_path) != EXPECTED_PROTOCOL:
        raise ValueError('Preregistered protocol identity mismatch')
    protocol, freeze = json.loads(protocol_path.read_text()), json.loads(freeze_path.read_text())
    if freeze['first_scientific_execution_performed_at_freeze'] is not False:
        raise ValueError('Freeze did not precede first science')
    identities = {}
    for record in freeze['files']:
        path = ROOT/record['path']
        if digest(path) != record['sha256'] or path.stat().st_size != record['bytes']:
            raise ValueError('Frozen input mismatch: '+record['path'])
        identities[record['path']] = record['sha256']
    if identities.get('PHYSICS_CONTRACT.json') != EXPECTED_CONTRACT:
        raise ValueError('Wrong physics contract')
    for record in protocol['inputs']:
        if identities.get(record['path']) != record['sha256']:
            raise ValueError('Protocol input absent from freeze')
    identities['contributions/numerics/PREEXECUTION_FROZEN.json'] = digest(freeze_path)
    input_j = json.loads((ROOT/'inputs/PHYS22_INITIAL_COEFFICIENTS.json').read_text())
    jx, jw = (D(input_j['results']['baseline_local']['J_nonphoto'][2][i]) for i in [0, 3])
    old_summary = json.loads((ROOT/'inputs/PHYS26/report/PHYS26_RESULTS_SUMMARY.json').read_text())
    old_values = old_summary['boundary_numerical_approximations']
    old_star, old_zero = D(old_values['Vstar_eV2']), D(old_values['W0_eV2'])
    rules, rule_records = {}, []
    for n in [16, 24]:
        rules[n], record = gauss_rule(n)
        rule_records.append(record)
    kernel_cache, average_cache = {}, {}

    def primary(energy):
        if energy not in kernel_cache:
            kernel_cache[energy] = jet_kernel(energy, jx, jw)
        return kernel_cache[energy]

    def averaged(center, order=16):
        COUNTS['gauss_average_lookup_requests'] += 1
        if not AC <= center <= BC:
            raise ValueError('Uniform center outside frozen center support')
        key = (order, center)
        if key not in average_cache:
            values = [(weight, primary(center+DELTA*node)) for node, weight in rules[order]]
            average_cache[key] = {field: sum((w*value[field] for w, value in values), ZERO)/2
                                  for field in ['k', 'kp']}
            COUNTS['gauss_average_evaluations_by_order'][str(order)] += 1
        return average_cache[key]

    ka, km, kb = (averaged(c)['k'] for c in [AC, M, BC])
    endpoint = (H*ka+L*kb)/(L+H)
    check('fixed_feasible_geometry', AC == D('13.66') and BC == D('24.53')
          and L == D('4.34') and H == D('6.53') and VMAX == D('28.3402'))
    check('frozen_J_signs', jx < 0 < jw, J_h2x=jx, J_h2w=jw)
    check('minimum_variance_endpoint_sign', km < 0, kbar_at_mean_s_4=km)
    check('maximum_variance_endpoint_sign', endpoint > 0, endpoint_response_s_4=endpoint)
    star = bisect_physical('W_star_delta', lambda c: (c-M)*ka+L*averaged(c)['k'],
                           M, BC, lambda c: L*(c-M)+OFFSET)
    zero = bisect_physical('W_0_delta', lambda c: H*averaged(c)['k']+(M-c)*kb,
                           AC, M, lambda c: H*(M-c)+OFFSET)
    wstar, wzero = star['midpoint_physical_variance_eV2'], zero['midpoint_physical_variance_eV2']
    cstar, czero = star['midpoint_center_eV'], zero['midpoint_center_eV']
    check('new_root_order_and_old_threshold_shifts', old_star < wstar < wzero < old_zero,
          old_Vstar=old_star, W_star_delta=wstar, W_0_delta=wzero, old_W0=old_zero)
    for root, center, anchor, sign, span in [
        (star, cstar, AC, 1, L), (zero, czero, BC, -1, H)]:
        kc, kp, kanchor = averaged(center)['k'], averaged(center)['kp'], averaged(anchor)['k']
        slope_w = (kanchor-kc-kp*(anchor-center))/(anchor-center)**2
        check(root['name']+'__local_response_slope_positive', slope_w > 0,
              slope_s_4_eV_minus2=slope_w)
        root['local_response_slope_s-4_eV-2'] = slope_w
        root['F_center_derivative_s-4'] = kanchor+span*kp if sign == 1 else span*kp-kanchor
        root['center_variance_eV2'] = root['midpoint_physical_variance_eV2']-OFFSET

    # Seven centers fixed by a prior selection rule, including all root anchors.
    vmixed = M+(D('19.74')-OFFSET)/L
    umixed = M-(D('19.74')-OFFSET)/H
    centers = [AC, M, BC, cstar, czero, vmixed, umixed]
    if len(set(centers)) != 7:
        raise RuntimeError('Independent center selection unexpectedly degenerate')
    comparison_rows, gl_errors, richardson_errors, raw_simpson_errors = [], [], [], []
    for index, center in enumerate(centers):
        low, high = averaged(center), averaged(center, 24)
        scalar_values = [scalar_kernel(center-DELTA+D(j)*2*DELTA/128, jx, jw)
                         for j in range(129)]
        simpson = {}
        for n in [32, 64, 128]:
            stride = 128//n
            simpson[n] = {}
            for field in ['k', 'kp']:
                total = scalar_values[0][field]+scalar_values[128][field]
                total += sum(((4 if j % 2 else 2)*scalar_values[j*stride][field]
                              for j in range(1, n)), ZERO)
                simpson[n][field] = total/(3*n)
        richardson6 = {
            64: {f: (16*simpson[64][f]-simpson[32][f])/15 for f in ['k', 'kp']},
            128: {f: (16*simpson[128][f]-simpson[64][f])/15 for f in ['k', 'kp']}}
        richardson8 = {f: (64*richardson6[128][f]-richardson6[64][f])/63 for f in ['k', 'kp']}
        errors = {}
        for field, scale in [('k', SCALE), ('kp', SCALE/M)]:
            errors[field] = {
                'GL16_vs_GL24': close('center_'+str(index)+'__GL16_vs_24_'+field,
                    low[field], high[field], GL_TOL, scale),
                'GL16_vs_scalar_Simpson_R8': close('center_'+str(index)+'__GL_vs_scalar_R8_'+field,
                    low[field], richardson8[field], SIMPSON_TOL, scale)}
            gl_errors.append(errors[field]['GL16_vs_GL24'])
            richardson_errors.append(errors[field]['GL16_vs_scalar_Simpson_R8'])
            raw_errors = [abs(simpson[n][field]-low[field])/scale for n in [32, 64, 128]]
            raw_simpson_errors.extend(raw_errors)
            check('center_'+str(index)+'__Simpson_refinement_'+field,
                  raw_errors[2] < raw_errors[1] < raw_errors[0], scaled_errors_32_64_128=raw_errors)
        comparison_rows.append({'center_eV': center, 'GL16': low, 'GL24': high,
                                'scalar_Simpson': simpson, 'scalar_Richardson6': richardson6,
                                'scalar_Richardson8': richardson8, 'scaled_errors': errors})
        COUNTS['independent_quadrature_centers'] += 1

    specs = [
        ('minimum_physical_variance', WMIN), ('W8', D(8)),
        ('old_PHYS26_Vstar', old_star), ('new_W_star_delta', wstar),
        ('mixed_W19_74', D('19.74')), ('new_W_0_delta', wzero),
        ('old_PHYS26_W0', old_zero), ('W26', D(26)), ('maximum_physical_variance', WMAX)]
    rows, laws_by_label = [], {}
    for label, w in specs:
        v = ZERO if w == WMIN else VMAX if w == WMAX else w-OFFSET
        moving_upper = BC if v == VMAX else M+v/L
        moving_lower = AC if v == VMAX else M-v/H
        pa, pb = two_law(AC, moving_upper), two_law(moving_lower, BC)
        upper = band_law_stats(label+'__upper', pa, w, averaged)
        lower = band_law_stats(label+'__lower', pb, w, averaged)
        formula_upper = (v*ka+L**2*averaged(moving_upper)['k'])/(L**2+v)
        formula_lower = (H**2*averaged(moving_lower)['k']+v*kb)/(H**2+v)
        close(label+'__upper_formula', upper['response_s-4'], formula_upper, scale=SCALE)
        close(label+'__lower_formula', lower['response_s-4'], formula_lower, scale=SCALE)
        delta_upper = (w*primary(A)['k']+L0**2*primary(M+w/L0)['k'])/(L0**2+w)
        delta_lower = (H0**2*primary(M-w/H0)['k']+w*primary(B)['k'])/(H0**2+w)
        gap = upper['response_s-4']-lower['response_s-4']
        check(label+'__strict_same_W_containment', delta_lower < lower['response_s-4']
              and upper['response_s-4'] < delta_upper,
              lower_gap_s_4=lower['response_s-4']-delta_lower,
              upper_gap_s_4=delta_upper-upper['response_s-4'])
        if v in [ZERO, VMAX]:
            close(label+'__degenerate_response_interval', gap, ZERO, scale=SCALE)
            target = [M] if v == ZERO else [AC, BC]
            check(label+'__degenerate_positive_centers',
                  upper['positive_mass_centers_eV'] == target and lower['positive_mass_centers_eV'] == target)
        else:
            check(label+'__strict_interior_envelope_gap', gap > 0, gap_s_4=gap)
        rows.append({'label': label, 'W_photon_eV2': w, 'V_center_eV2': v,
                     'moving_upper_center_eV': moving_upper, 'moving_lower_center_eV': moving_lower,
                     'upper': upper, 'lower': lower,
                     'interval_s-4': [lower['response_s-4'], upper['response_s-4']],
                     'PHYS26_delta_allowed_same_W_interval_s-4': [delta_lower, delta_upper],
                     'classification': 'Preregistered finite samples of the separately derived all-W theorem'})
        laws_by_label[label] = (pa, pb, lower['response_s-4'], upper['response_s-4'])
        COUNTS['physical_variance_cases'] += 1
    for label in ['new_W_star_delta', 'new_W_0_delta']:
        index = 3 if label == 'new_W_star_delta' else 5
        value = rows[index]['upper' if index == 3 else 'lower']['response_s-4']
        close(label+'__finite_root_response_residual', value, ZERO, D('1e-22'), SCALE)
        (star if index == 3 else zero)['finite_midpoint_response_s-4'] = value

    pa, pb, low, high = laws_by_label['mixed_W19_74']
    check('W19_74_opposite_signs', low < 0 < high, lower_s_4=low, upper_s_4=high)
    alpha = -low/(high-low)
    check('W19_74_zero_mixture_weight', ZERO < alpha < ONE, alpha_upper=alpha)
    mixture_rows = []
    for label, weight in [('quarter_upper', D('0.25')), ('numerical_zero', alpha)]:
        law = [(c, weight*p) for c, p in pa]+[(c, (1-weight)*p) for c, p in pb]
        stats = band_law_stats('mixture_'+label, law, D('19.74'), averaged)
        affine = weight*high+(1-weight)*low
        close('mixture_'+label+'__affine_response', stats['response_s-4'], affine, scale=SCALE)
        if label == 'numerical_zero':
            close('mixture_numerical_zero__residual', stats['response_s-4'], ZERO, scale=SCALE)
        mixture_rows.append({'label': label, 'alpha_upper': weight, 'alpha_lower': 1-weight,
                             **stats, 'affine_response_s-4': affine,
                             'classification': 'Finite numerical response; exact zero mixture uses exact bound responses'})
        COUNTS['mixture_cases'] += 1
    root_comparisons = {str(row['center_eV']): row for row in comparison_rows}
    for root, center, endpoint_center, span, upper_branch in [
        (star, cstar, AC, L, True), (zero, czero, BC, H, False)]:
        delta_center = root_comparisons[str(center)]['scalar_Richardson8']['k']-averaged(center)['k']
        delta_anchor = root_comparisons[str(endpoint_center)]['scalar_Richardson8']['k']-averaged(endpoint_center)['k']
        delta_f = ((center-M)*delta_anchor+span*delta_center if upper_branch
                   else span*delta_center+(M-center)*delta_anchor)
        root['independent_quadrature_F_difference_s-4_eV'] = delta_f
        root['local_linearized_physical_variance_shift_estimate_eV2'] = (
            span*abs(delta_f/root['F_center_derivative_s-4']))
        root['linearized_shift_status'] = 'Local conditioning diagnostic, not a rigorous error bound'
    check('execution_budgets', COUNTS['new_physical_root_searches'] == 2
          and COUNTS['physical_variance_cases'] == 9 and COUNTS['independent_quadrature_centers'] == 7
          and COUNTS['combined_kernel_evaluations'] <= 20000, actual_counts=COUNTS)
    failed = [row['name'] for row in CHECKS if not row['pass']]
    result = {
        'task': 'REI-PHYS27-20261011',
        'evidence_class': ['numerically checked', 'implementation-verified'],
        'role': 'NONBLIND numerical designer and candidate generator; not final decision reviewer',
        'python_version': platform.python_version(), 'decimal_precision': getcontext().prec,
        'identity_sha256': identities,
        'constants': {'photon_support_eV': [A, B], 'center_support_eV': [AC, BC],
                      'mean_eV': M, 'half_width_eV': DELTA, 'full_width_eV': 2*DELTA,
                      'L_delta_eV': L, 'H_delta_eV': H, 'variance_offset_eV2': OFFSET,
                      'V_center_max_eV2': VMAX, 'W_photon_min_eV2': WMIN, 'W_photon_max_eV2': WMAX,
                      'N0_per_H': N0, 'q_s-2': Q, 'kappa_s-1_cm-2': KAPPA,
                      'factor_q_N0_kappa_over_180': FACTOR, 'chi_eV': CHI,
                      'E0_eV': E0, 'ya': YA, 'P': P, 'sigma0': SIGMA0, 'area_cm2': AREA,
                      'J_h2_x': jx, 'J_h2_w': jw},
        'numerical_endpoint_signs': {'minimum_W_response_s-4': km, 'maximum_W_response_s-4': endpoint},
        'quadrature_rules': rule_records, 'independent_quadrature_comparisons': comparison_rows,
        'new_physical_roots': {'W_star_delta': star, 'W_0_delta': zero},
        'threshold_comparison': {'PHYS26_Vstar0_eV2': old_star, 'PHYS26_W00_eV2': old_zero,
                                 'W_star_delta_eV2': wstar, 'W_0_delta_eV2': wzero,
                                 'V_star_delta_center_eV2': wstar-OFFSET,
                                 'V_0_delta_center_eV2': wzero-OFFSET,
                                 'W_star_shift_from_PHYS26_eV2': wstar-old_star,
                                 'W_0_shift_from_PHYS26_eV2': wzero-old_zero,
                                 'coexistence_width_delta_eV2': wzero-wstar,
                                 'coexistence_width_PHYS26_eV2': old_zero-old_star,
                                 'printed_digits_policy': 'At most 12 significant digits for new numerical thresholds; no physical uncertainty claim'},
        'physical_variance_cases': rows, 'mixtures_at_W19_74': mixture_rows,
        'checks': CHECKS,
        'summary': {'total_checks': len(CHECKS), 'passed': len(CHECKS)-len(failed), 'failed': len(failed),
                    'failed_names': failed, 'all_pass': not failed,
                    'maximum_scaled_GL16_vs_GL24_error': max(gl_errors),
                    'maximum_scaled_GL_vs_scalar_Richardson8_error': max(richardson_errors),
                    'maximum_scaled_raw_Simpson_error': max(raw_simpson_errors),
                    'actual_counts': COUNTS},
        'claim_ceiling': protocol['claim_ceiling'],
        'global_theorem_status': 'Numerical samples support implementation only; continuum proof is a separate theory artifact',
        'physical_admission': 'HOLD',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(serial(result), stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(serial(result['summary']), ensure_ascii=False))
    raise SystemExit(0 if not failed else 1)


if __name__ == '__main__':
    main()
