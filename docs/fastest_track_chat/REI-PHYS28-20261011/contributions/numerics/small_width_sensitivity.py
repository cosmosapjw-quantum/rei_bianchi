#!/usr/bin/env python3
"""PHYS28: frozen four-node small-width sensitivity evaluation, stdlib only.

Explicitly adapted degree-three log Taylor Jet and scalar log-derivative
expressions from the actually read PHYS26/27 pure formula sections.
No historical module is imported or executed. No physical root, quadrature,
finite difference, width sweep, native solver, or gas IVP is performed.
"""
from __future__ import annotations

import argparse
from decimal import Decimal as D, getcontext
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import platform
import traceback

getcontext().prec = 80
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXPECTED_CONTRACT = 'd9c50cb43d60bf466eb92e91e8e62791fcf84680025c34fc0c42c899ed16fde2'
EXPECTED_PROTOCOL = '5298c389da5ddd7eb2a5246c3cb472faba93c7d97a39efe7ee99de441200b56a'
ZERO, ONE = D(0), D(1)
A, M, B = D('13.61'), D(18), D('24.58')
L, H, DELTA = M-A, B-M, D('0.05')
SCALE, KPRIME_SCALE, SLOPE_SCALE = D('1e-64'), D('1e-64')/18, D('1e-64')/(18*18)
ALG_TOL, ROOT_TOL = D('1e-60'), D('1e-65')
CHECKS = []
COUNTS = {
    'program_main_invocations_this_process': 1,
    'planned_unique_energy_nodes': 4,
    'actual_unique_energy_nodes': 0,
    'primary_jet_joint_evaluations': 0,
    'independent_scalar_joint_evaluations': 0,
    'combined_kernel_derivative_joint_evaluations': 0,
    'k_component_outputs': 0,
    'k_prime_component_outputs': 0,
    'combined_k_and_k_prime_component_outputs': 0,
    'sigma_auxiliary_outputs': 0,
    'branch_formula_evaluations_from_cached_values': 0,
    'new_physical_root_searches': 0,
    'physical_root_iterations': 0,
    'quadrature_evaluations': 0,
    'quadrature_node_solves': 0,
    'finite_difference_evaluations': 0,
    'width_root_sweep': 0,
    'old_module_imports': 0,
    'old_main_invocations': 0,
    'closed_suite_replays': 0,
    'old_physical_root_searches': 0,
    'new_derivative_sign_campaigns': 0,
    'native_runs': 0,
    'gas_IVP_runs': 0,
    'dense_LP_or_multiple_parameter_campaigns': 0,
    'display_new_kernel_derivative_evaluations': 0,
}


def f64(value):
    """Exact Decimal value of the source binary64 literal, before Decimal ops."""
    return D.from_float(float(value))


N0 = f64('0.05')
SHEAR = (f64('1.01e-14')-f64('0.99e-14'))/2
Q = 2*SHEAR**2
KAPPA = f64('29979245800')*f64('1e-4')*(1-f64('0.9'))
FACTOR = Q*N0*KAPPA/180
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
    error = abs(actual-expected)/scale
    check(name, error <= tol, actual=actual, expected=expected,
          residual=actual-expected, scale=scale, scaled_error=error, tolerance=tol)
    return error


def power(value, exponent):
    return (D(exponent)*value.ln()).exp()


class Jet:
    """c[n]=(E d/dE)^n f/n!, n=0,...,3; not an interval enclosure."""
    size = 4

    def __init__(self, value):
        if isinstance(value, (list, tuple)):
            if len(value) > self.size:
                raise ValueError('Jet coefficient overflow')
            self.c = list(value)+[ZERO]*(self.size-len(value))
        else:
            self.c = [D(value)]+[ZERO]*(self.size-1)

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
        return self+-self.lift(other)

    def __rsub__(self, other):
        return self.lift(other)+-self

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
        remainder = self/base-1
        coefficient, term, series = ONE, Jet(1), Jet(1)
        for degree in range(1, self.size):
            coefficient *= (exponent-degree+1)/degree
            term = term*remainder
            series += coefficient*term
        return power(base, exponent)*series


def count_joint(kind, energy):
    if not A <= energy <= B or not HI_CUT < energy < HEI_CUT:
        raise ValueError('Energy left frozen analytic HI support')
    if COUNTS[kind] >= 4 or COUNTS['combined_kernel_derivative_joint_evaluations'] >= 8:
        raise RuntimeError('Planned four nodes per path / eight joint calls exceeded')
    COUNTS[kind] += 1
    COUNTS['combined_kernel_derivative_joint_evaluations'] += 1


def record_outputs(result):
    if not all(value.is_finite() for value in result.values()):
        raise ArithmeticError('Nonfinite kernel output')
    COUNTS['k_component_outputs'] += 1
    COUNTS['k_prime_component_outputs'] += 1
    COUNTS['combined_k_and_k_prime_component_outputs'] += 2
    COUNTS['sigma_auxiliary_outputs'] += 1
    return result


def jet_kernel(energy, jx, jw):
    count_joint('primary_jet_joint_evaluations', energy)
    ej = Jet([energy/factorial(n) for n in range(4)])
    xj = ej/E0
    sigma = SIGMA0*(xj-1)**2*xj**(P/2-f64('5.5'))*(
        1+(xj/YA)**D('0.5'))**(-P)*AREA
    product = sigma*(jx+jw*(ej-CHI))
    dn = [product.c[n]*factorial(n) for n in range(4)]
    return record_outputs({
        'sigma_cm2': sigma.c[0],
        'k_s-4': FACTOR*(dn[2]+3*dn[1]),
        'k_prime_s-4_eV-1': FACTOR*(dn[3]+3*dn[2])/energy,
    })


def scalar_kernel(energy, jx, jw):
    """Separate analytic log-derivative expression, without Jet/differencing."""
    count_joint('independent_scalar_joint_evaluations', energy)
    x = energy/E0
    z = (x/YA).sqrt()
    r = P/2-f64('5.5')
    sigma = SIGMA0*(x-1)**2*power(x, r)*power(1+z, -P)*AREA
    ell1 = 2*x/(x-1)+r-P*z/(2*(1+z))
    ell2 = -2*x/(x-1)**2-P*z/(4*(1+z)**2)
    ell3 = 2*x*(x+1)/(x-1)**3-P*z*(1-z)/(8*(1+z)**3)
    s2, s3 = ell1**2+ell2, ell1**3+3*ell1*ell2+ell3
    h, t = jx+jw*(energy-CHI), jw*energy
    return record_outputs({
        'sigma_cm2': sigma,
        'k_s-4': FACTOR*sigma*((s2+3*ell1)*h+(2*ell1+4)*t),
        'k_prime_s-4_eV-1': FACTOR*sigma/energy*((s3+3*s2)*h+(3*s2+9*ell1+4)*t),
    })


def differentiated_law(label, branch, variance):
    """Moments and fixed-W first derivatives: arithmetic only, no kernels."""
    if branch == 'plus':
        denominator = L*L+variance
        energies = [A, M+variance/L]
        probabilities = [variance/denominator, L*L/denominator]
        de = [ONE, variance/(L*L)]
        dp = [2*L*variance/(denominator*denominator),
              -2*L*variance/(denominator*denominator)]
    else:
        denominator = H*H+variance
        energies = [M-variance/H, B]
        probabilities = [H*H/denominator, variance/denominator]
        de = [-variance/(H*H), -ONE]
        dp = [-2*H*variance/(denominator*denominator),
              2*H*variance/(denominator*denominator)]
    mass = sum(probabilities, ZERO)
    mean = sum((p*e for e, p in zip(energies, probabilities)), ZERO)
    actual_variance = sum((p*(e-M)**2 for e, p in zip(energies, probabilities)), ZERO)
    mass_prime = sum(dp, ZERO)
    mean_prime = sum((dprob*e+p*denergy for e, p, dprob, denergy
                      in zip(energies, probabilities, dp, de)), ZERO)
    variance_prime = sum((dprob*(e-M)**2+2*p*(e-M)*denergy for e, p, dprob, denergy
                          in zip(energies, probabilities, dp, de)), ZERO)
    check(label+'__interior_supported_positive',
          ZERO < variance < L*H and all(A <= e <= B for e in energies)
          and all(ZERO < p < ONE for p in probabilities))
    for field, actual, expected in (
        ('mass', mass, ONE), ('mean', mean, M), ('variance', actual_variance, variance),
        ('mass_first_derivative', mass_prime, ZERO),
        ('mean_first_derivative', mean_prime, ZERO),
        ('actual_W_first_derivative', variance_prime, ZERO),
    ):
        close(label+'__'+field, actual, expected)
    return {
        'energies_eV': energies, 'probabilities': probabilities,
        'endpoint_center_first_derivatives': de,
        'probability_first_derivatives_eV-1': dp,
        'mass': mass, 'mean_eV': mean, 'variance_eV2': actual_variance,
        'mass_first_derivative_eV-1': mass_prime,
        'mean_first_derivative': mean_prime,
        'physical_variance_first_derivative_eV': variance_prime,
        'center_variance_partial_delta_at_fixed_W_eV': ZERO,
        'uniform_band_internal_variance_first_derivative_eV': ZERO,
        'zero_term_basis': 'Exact derivative of +/-delta^2/3 at zero; theory input, not an extra numerical derivative',
    }


def sensitivity(label, branch, variance, cache, law, stored_response):
    """General finite-W formulas: never substitutes a numerical response as 0."""
    COUNTS['branch_formula_evaluations_from_cached_values'] += 1
    if branch == 'plus':
        anchor, center = A, M+variance/L
        ka, kc = cache['a']['k_s-4'], cache['v_star']['k_s-4']
        kpa, kpc = cache['a']['k_prime_s-4_eV-1'], cache['v_star']['k_prime_s-4_eV-1']
        denominator = L*L+variance
        span = center-anchor
        trapezoid_gap = kpa+kpc-2*(kc-ka)/span
        compact = variance/denominator*trapezoid_gap
        endpoint = variance/denominator*kpa
        moving_center = L*L/denominator*kpc*(variance/(L*L))
        weights = 2*L*variance/(denominator*denominator)*(ka-kc)
        slope = (ka-kc-kpc*(anchor-center))/(anchor-center)**2
        numerator = variance*ka+L*L*kc
        numerator_prime = ka+L*kpc
        direct_response = law['probabilities'][0]*ka+law['probabilities'][1]*kc
    else:
        anchor, center = B, M-variance/H
        ka, kc = cache['b']['k_s-4'], cache['u_zero']['k_s-4']
        kpa, kpc = cache['b']['k_prime_s-4_eV-1'], cache['u_zero']['k_prime_s-4_eV-1']
        denominator = H*H+variance
        span = anchor-center
        trapezoid_gap = kpc+kpa-2*(ka-kc)/span
        compact = -variance/denominator*trapezoid_gap
        endpoint = -variance/denominator*kpa
        moving_center = H*H/denominator*kpc*(-variance/(H*H))
        weights = 2*H*variance/(denominator*denominator)*(ka-kc)
        slope = (ka-kc-kpc*(anchor-center))/(anchor-center)**2
        numerator = H*H*kc+variance*ka
        numerator_prime = ka-H*kpc
        direct_response = law['probabilities'][0]*kc+law['probabilities'][1]*ka
    decomposed = endpoint+moving_center+weights
    quotient_slope = (numerator_prime*denominator-numerator)/(denominator*denominator)
    response = numerator/denominator
    check(label+'__slope_positive', slope > ZERO, slope=slope)
    check(label+'__trapezoid_gap_negative', trapezoid_gap < ZERO, gap=trapezoid_gap,
          interpretation='Four-node numerical consistency with inherited strict k-prime concavity; not a new sign certificate')
    close(label+'__B_terms_equal_compact', decomposed, compact, scale=KPRIME_SCALE)
    close(label+'__S_secant_equal_quotient', slope, quotient_slope, scale=SLOPE_SCALE)
    close(label+'__response_formula_equal_probability_sum', response, direct_response, scale=SCALE)
    close(label+'__stored_root_response_small', response, ZERO, tol=ROOT_TOL, scale=SCALE)
    close(label+'__stored_root_residual_consistency', response, stored_response, scale=SCALE)
    if slope == ZERO:
        raise ZeroDivisionError('Simple-root slope vanished at stored root')
    coefficient = -compact/slope
    c_terms = {name: -value/slope for name, value in (
        ('endpoint_motion', endpoint), ('moving_center_motion', moving_center),
        ('weight_motion', weights))}
    close(label+'__c_terms_equal_total', sum(c_terms.values(), ZERO), coefficient)
    check(label+'__expected_coefficient_sign',
          coefficient > ZERO if branch == 'plus' else coefficient < ZERO,
          coefficient_eV=coefficient, blind_prediction_test=False)
    return {
        'branch': branch, 'stored_zero_width_variance_eV2': variance,
        'anchor_energy_eV': anchor, 'moving_center_energy_eV': center,
        'baseline_response_s-4': response,
        'stored_PHYS26_response_s-4': stored_response,
        'response_difference_from_PHYS26_s-4': response-stored_response,
        'root_input_classification': 'Stored numerical root, not exact zero; full general B/S formulas used',
        'trapezoid_gap_s-4_eV-1': trapezoid_gap,
        'B_partial_delta_compact_s-4_eV-1': compact,
        'B_partial_delta_terms_s-4_eV-1': {
            'endpoint_motion': endpoint, 'moving_center_motion': moving_center,
            'weight_motion': weights, 'center_variance_shift': ZERO,
            'uniform_kernel_averaging': ZERO, 'sum': decomposed,
        },
        'zero_first_order_terms_basis': 'At fixed W, Vprime(0)=0; symmetric uniform average partial_delta f_delta(c)|0=0, supplied by separate derivation',
        'S_partial_W_secant_s-4_eV-2': slope,
        'S_partial_W_quotient_s-4_eV-2': quotient_slope,
        'coefficient_c_eV': coefficient,
        'coefficient_decomposition_eV': c_terms,
        'local_root_residual_linearized_displacement_eV2': -response/slope,
        'root_residual_displacement_status': 'Local finite diagnostic only, not a rigorous root-error bound',
    }


def science(result):
    protocol = json.loads((HERE/'PROTOCOL.json').read_bytes())
    freeze = json.loads((HERE/'PREEXECUTION_FROZEN.json').read_bytes())
    check('contract_expected_sha256', digest(ROOT/'PHYSICS_CONTRACT.json') == EXPECTED_CONTRACT)
    check('protocol_expected_sha256', digest(HERE/'PROTOCOL.json') == EXPECTED_PROTOCOL)
    identities = {}
    for item in freeze['files']:
        path = ROOT/item['path']
        actual_hash, actual_size = digest(path), path.stat().st_size
        check('frozen_identity__'+item['path'],
              actual_hash == item['sha256'] and actual_size == item['bytes'],
              actual_sha256=actual_hash, expected_sha256=item['sha256'],
              actual_bytes=actual_size, expected_bytes=item['bytes'])
        identities[item['path']] = actual_hash
    identities['contributions/numerics/PREEXECUTION_FROZEN.json'] = digest(HERE/'PREEXECUTION_FROZEN.json')
    result['identity_sha256'] = identities
    if any(not item['pass'] for item in CHECKS):
        raise RuntimeError('Preexecution identity check failed before any kernel call')
    jdata = json.loads((ROOT/'inputs/PHYS22_INITIAL_COEFFICIENTS.json').read_bytes())
    old = json.loads((ROOT/'inputs/PHYS26/contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json').read_bytes())
    finite = json.loads((ROOT/'inputs/PHYS27/contributions/numerics/FINITE_WIDTH_FIRST.json').read_bytes())
    root_data = old['inherited_boundary_residuals']
    finite_data = finite['threshold_comparison']
    jx, jw = [D(jdata['results']['baseline_local']['J_nonphoto'][2][i]) for i in (0, 3)]
    wstar, wzero = D(root_data['Vstar_eV2']), D(root_data['W0_eV2'])
    new_star = D(finite['new_physical_roots']['W_star_delta']['midpoint_physical_variance_eV2'])
    new_zero = D(finite['new_physical_roots']['W_0_delta']['midpoint_physical_variance_eV2'])
    check('inherited_PHYS26_all_pass', old['summary']['all_pass'])
    check('inherited_PHYS27_all_pass', finite['summary']['all_pass'])
    check('PHYS27_copied_PHYS26_root_strings_unchanged',
          root_data['Vstar_eV2'] == finite_data['PHYS26_Vstar0_eV2']
          and root_data['W0_eV2'] == finite_data['PHYS26_W00_eV2'])
    check('PHYS27_root_summary_equals_raw_root_record',
          new_star == D(finite_data['W_star_delta_eV2'])
          and new_zero == D(finite_data['W_0_delta_eV2']))
    check('frozen_half_width_and_support',
          finite['constants']['half_width_eV'] == str(DELTA)
          and [D(x) for x in finite['constants']['photon_support_eV']] == [A, B]
          and D(finite['constants']['mean_eV']) == M)
    check('frozen_analytic_support', HI_CUT < A < M < B < HEI_CUT)
    check('source_manifest_identity', digest(ROOT/'SOURCE_MANIFEST.json') ==
          next(item['sha256'] for item in protocol['inputs'] if item['path'] == 'SOURCE_MANIFEST.json'))
    for key, actual in (('N0_per_H', N0), ('q_s-2', Q), ('kappa_s-1_cm-2', KAPPA),
                        ('prefactor', FACTOR), ('chi_eV', CHI), ('E0_eV', E0),
                        ('ya', YA), ('P', P), ('J_h2_x', jx), ('J_h2_w', jw)):
        expected = D(old['constants'][key])
        close('PHYS26_constant__'+key, actual, expected, scale=max(abs(actual), abs(expected)))
    result['constants'] = {
        'support_eV': [A, B], 'mean_eV': M, 'L_eV': L, 'H_eV': H,
        'comparison_half_width_eV': DELTA, 'N0_per_H': N0, 'q_s-2': Q,
        'kappa_s-1_cm-2': KAPPA, 'factor_q_N0_kappa_over_180': FACTOR,
        'chi_eV': CHI, 'E0_eV': E0, 'ya': YA, 'P': P,
        'sigma0': SIGMA0, 'area_cm2': AREA, 'J_h2_x': jx, 'J_h2_w': jw,
        'PHYS26_root_strings_consumed_exactly': {
            'W_star_zero_eV2': root_data['Vstar_eV2'], 'W_zero_zero_eV2': root_data['W0_eV2']},
        'arithmetic_interpretation': 'Source literals are exact-real binary64 values; subsequent arithmetic Decimal80, no native equivalence',
    }
    nodes = {'a': A, 'v_star': M+wstar/L, 'u_zero': M-wzero/H, 'b': B}
    COUNTS['actual_unique_energy_nodes'] = len(set(nodes.values()))
    check('exactly_four_distinct_supported_nodes', len(set(nodes.values())) == 4
          and all(A <= e <= B for e in nodes.values()))
    result['energy_nodes_eV'] = nodes
    cache = {}
    for path, kernel in (('jet', jet_kernel), ('scalar', scalar_kernel)):
        cache[path] = {label: kernel(energy, jx, jw) for label, energy in nodes.items()}
    result['joint_kernel_outputs'] = cache
    expression_errors = []
    for label in nodes:
        for field, scale in (('sigma_cm2', D('1e-18')), ('k_s-4', SCALE),
                             ('k_prime_s-4_eV-1', KPRIME_SCALE)):
            expression_errors.append(close('kernel_expression__'+label+'__'+field,
                                           cache['jet'][label][field], cache['scalar'][label][field],
                                           scale=scale))
    laws = {'upper_root': differentiated_law('upper_root_law', 'plus', wstar),
            'lower_root': differentiated_law('lower_root_law', 'minus', wzero)}
    result['fixed_W_differentiated_laws'] = laws
    responses = {'upper_root': D(root_data['Pa_response_s-4']),
                 'lower_root': D(root_data['Pb_response_s-4'])}
    sensitivity_results = {}
    for path in ('jet', 'scalar'):
        sensitivity_results[path] = {
            'upper_root': sensitivity(path+'__upper_root', 'plus', wstar, cache[path],
                                      laws['upper_root'], responses['upper_root']),
            'lower_root': sensitivity(path+'__lower_root', 'minus', wzero, cache[path],
                                      laws['lower_root'], responses['lower_root']),
        }
    result['sensitivity'] = sensitivity_results
    sensitivity_errors = []
    for branch in ('upper_root', 'lower_root'):
        for field, scale in (('B_partial_delta_compact_s-4_eV-1', KPRIME_SCALE),
                             ('S_partial_W_secant_s-4_eV-2', SLOPE_SCALE),
                             ('coefficient_c_eV', None)):
            sensitivity_errors.append(close('sensitivity_expression__'+branch+'__'+field,
                                              sensitivity_results['jet'][branch][field],
                                              sensitivity_results['scalar'][branch][field],
                                              scale=scale))
    comparison = {}
    for label, old_w, new_w, shift_key in (
        ('upper_root', wstar, new_star, 'W_star_shift_from_PHYS26_eV2'),
        ('lower_root', wzero, new_zero, 'W_0_shift_from_PHYS26_eV2'),
    ):
        coefficient = sensitivity_results['jet'][label]['coefficient_c_eV']
        shift = new_w-old_w
        linear = DELTA*coefficient
        residual = shift-linear
        close(label+'__stored_actual_shift_consistency', shift, D(finite_data[shift_key]))
        close(label+'__shift_decomposition', linear+residual, shift)
        comparison[label] = {
            'PHYS26_zero_width_root_eV2': old_w,
            'PHYS27_delta_005_root_eV2': new_w,
            'coefficient_c_eV': coefficient,
            'linear_shift_at_delta_005_eV2': linear,
            'predicted_root_at_delta_005_eV2': old_w+linear,
            'actual_shift_at_delta_005_eV2': shift,
            'residual_actual_minus_linear_eV2': residual,
            'absolute_residual_relative_to_actual_shift': abs(residual/shift),
            'absolute_residual_relative_to_actual_shift_percent': 100*abs(residual/shift),
            'single_width_effective_slope_eV': shift/DELTA,
            'comparison_status': 'Single inherited width diagnostic; no tolerance or convergence-rate/validity-window certificate',
        }
    old_width, new_width = wzero-wstar, new_zero-new_star
    width_slope = (sensitivity_results['jet']['lower_root']['coefficient_c_eV']
                   - sensitivity_results['jet']['upper_root']['coefficient_c_eV'])
    reduction_slope = -width_slope
    reduction = old_width-new_width
    linear_reduction = DELTA*reduction_slope
    reduction_residual = reduction-linear_reduction
    close('coexistence_width_PHYS26_consistency', old_width, D(finite_data['coexistence_width_PHYS26_eV2']))
    close('coexistence_width_PHYS27_consistency', new_width, D(finite_data['coexistence_width_delta_eV2']))
    close('coexistence_reduction_equals_threshold_shift_difference', reduction,
          comparison['upper_root']['actual_shift_at_delta_005_eV2']
          - comparison['lower_root']['actual_shift_at_delta_005_eV2'])
    close('coexistence_reduction_residual_identity', reduction_residual,
          comparison['upper_root']['residual_actual_minus_linear_eV2']
          - comparison['lower_root']['residual_actual_minus_linear_eV2'])
    comparison['coexistence_width'] = {
        'PHYS26_width_eV2': old_width, 'PHYS27_delta_005_width_eV2': new_width,
        'width_first_derivative_eV': width_slope, 'reduction_first_derivative_eV': reduction_slope,
        'linear_reduction_at_delta_005_eV2': linear_reduction,
        'actual_reduction_at_delta_005_eV2': reduction,
        'predicted_width_at_delta_005_eV2': old_width-linear_reduction,
        'reduction_residual_actual_minus_linear_eV2': reduction_residual,
        'absolute_reduction_residual_relative_to_actual': abs(reduction_residual/reduction),
        'absolute_reduction_residual_relative_to_actual_percent': 100*abs(reduction_residual/reduction),
        'actual_reduction_fraction': reduction/old_width,
        'linear_reduction_fraction': linear_reduction/old_width,
    }
    result['delta_005_comparison'] = comparison
    check('actual_joint_evaluation_counts_match_preregistered', COUNTS['primary_jet_joint_evaluations'] == 4
          and COUNTS['independent_scalar_joint_evaluations'] == 4
          and COUNTS['combined_kernel_derivative_joint_evaluations'] == 8)
    check('actual_component_output_counts', COUNTS['k_component_outputs'] == 8
          and COUNTS['k_prime_component_outputs'] == 8
          and COUNTS['combined_k_and_k_prime_component_outputs'] == 16)
    check('all_forbidden_execution_counts_zero',
          all(COUNTS[key] == 0 for key in (
              'new_physical_root_searches', 'physical_root_iterations', 'quadrature_evaluations',
              'quadrature_node_solves', 'finite_difference_evaluations', 'width_root_sweep',
              'old_module_imports', 'old_main_invocations', 'closed_suite_replays',
              'old_physical_root_searches', 'new_derivative_sign_campaigns', 'native_runs',
              'gas_IVP_runs', 'dense_LP_or_multiple_parameter_campaigns',
              'display_new_kernel_derivative_evaluations')))
    result['maximum_scaled_kernel_expression_error'] = max(expression_errors)
    result['maximum_scaled_sensitivity_expression_error'] = max(sensitivity_errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    output = Path(parser.parse_args().output)
    if output.exists():
        raise FileExistsError('Fresh output required; existing evidence is never overwritten')
    result = {
        'task': 'REI-PHYS28-20261011',
        'evidence_class': ['numerically checked', 'implementation-verified within frozen formulas'],
        'role': 'NONBLIND numerical designer/generator; not final decision reviewer',
        'python_version': platform.python_version(),
        'decimal_precision': getcontext().prec,
        'coefficient_definition': 'Exact-root theorem c=-partial_delta A/partial_W A; numerical values below evaluate the general expressions at stored PHYS26 root approximations',
        'claim_ceiling': [
            'Finite Decimal comparisons are not directed interval or physical uncertainty enclosures.',
            'Stored PHYS26/27 roots are numerical approximations; no new search or correction.',
            'At most 12 significant digits in prose; full decimals are reproducibility data only.',
            'Single delta=.05 comparison does not certify rate, error bound, width window, or nesting/monotonicity between arbitrary positive widths.',
            'Two algebraic paths share original HI fit, source-real constants, serialized J and Decimal transcendental operations.',
            'No J/atomic/gas uncertainty, native equivalence, finite-time/finite-epsilon remainder, emitter admission, or novelty priority.',
        ],
        'physical_admission': 'HOLD',
    }
    error = False
    try:
        science(result)
    except Exception as exc:
        error = True
        traceback.print_exc()
        result['execution_failure'] = {
            'type': type(exc).__name__, 'message': str(exc),
            'classification': 'Observed execution failure; scientific layer requires diagnosis',
            'fallback_or_hidden_rerun': False,
        }
    failures = [item['name'] for item in CHECKS if not item['pass']]
    result['checks'] = CHECKS
    result['summary'] = {
        'total_checks': len(CHECKS),
        'passed': len(CHECKS)-len(failures), 'failed': len(failures),
        'failed_names': failures, 'all_pass': not error and not failures,
        'actual_counts': COUNTS,
    }
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(serial(result), stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(serial({'summary': result['summary'],
                             'sensitivity_coefficients_eV': {
                                 label: values['coefficient_c_eV']
                                 for label, values in result.get('sensitivity', {}).get('jet', {}).items()},
                             'result_sha256': digest(output)}), ensure_ascii=False))
    return 0 if result['summary']['all_pass'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
