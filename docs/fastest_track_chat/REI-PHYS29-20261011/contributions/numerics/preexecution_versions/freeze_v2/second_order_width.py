#!/usr/bin/env python3
"""PHYS29: eight fixed-node joint(k,k',k'') evaluations, no physical root solve.

The degree-four log Taylor kernel explicitly adapts the actually read PHYS28
pure formula code. The scalar kernel and bivariate envelope algebra are separate
expressions. No historical module is imported or executed. Scientific execution
is permitted only after the owner has reviewed the frozen files and given GO.
"""
from __future__ import annotations

import argparse
from decimal import Decimal as D, getcontext
from fractions import Fraction
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import platform
import traceback

getcontext().prec = 80
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXPECTED_CONTRACT = '603e2a30074800edd2226c86cf1f256efe5fd49ad45a2252788059d19a487d10'
EXPECTED_PROTOCOL = 'b3a9962e6df64ff6b1078ef5eac7ae24225581eac348c10984cf6e3a28983092'
ZERO, ONE = D(0), D(1)
A, M, B = D('13.61'), D(18), D('24.58')
L, H, DELTA = M-A, B-M, D('0.05')
S0 = D('1e-64')
S1, S2, S3, S4 = [S0/(D(18)**i) for i in range(1, 5)]
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
    'k_second_component_outputs': 0,
    'combined_k_kprime_ksecond_component_outputs': 0,
    'sigma_auxiliary_outputs': 0,
    'physical_chain_branch_evaluations_from_cached_values': 0,
    'physical_series_branch_evaluations_from_cached_values': 0,
    'moment_series_evaluations_without_physical_kernel': 0,
    'exact_rational_quadratic_toy_branches': 0,
    'exact_rational_quadratic_chain_evaluations': 0,
    'exact_rational_quadratic_series_evaluations': 0,
    'new_physical_root_searches': 0,
    'physical_root_iterations': 0,
    'old_module_imports': 0,
    'old_main_invocations': 0,
    'closed_suite_replays': 0,
    'old_physical_root_searches': 0,
    'quadrature_evaluations': 0,
    'finite_difference_evaluations': 0,
    'width_root_sweep': 0,
    'new_derivative_sign_campaigns': 0,
    'native_runs': 0,
    'gas_IVP_runs': 0,
    'dense_LP_or_multiple_parameter_campaigns': 0,
    'display_new_kernel_derivative_evaluations': 0,
}


def f64(value):
    """Exact Decimal interpretation of the source binary64 literal."""
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
    if isinstance(obj, Fraction):
        return str(obj.numerator) if obj.denominator == 1 else str(obj)
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


class LogJet:
    """c[n]=(E*d/dE)^n f/n!, n=0,...,4; finite Decimal, not intervals."""
    size = 5

    def __init__(self, value):
        if isinstance(value, (list, tuple)):
            if len(value) > self.size:
                raise ValueError('LogJet coefficient overflow')
            self.c = list(value)+[ZERO]*(self.size-len(value))
        else:
            self.c = [D(value)]+[ZERO]*(self.size-1)

    @staticmethod
    def lift(value):
        return value if isinstance(value, LogJet) else LogJet(value)

    def __add__(self, other):
        other = self.lift(other)
        return LogJet([a+b for a, b in zip(self.c, other.c)])

    __radd__ = __add__

    def __neg__(self):
        return LogJet([-c for c in self.c])

    def __sub__(self, other):
        return self+-self.lift(other)

    def __rsub__(self, other):
        return self.lift(other)+-self

    def __mul__(self, other):
        other = self.lift(other)
        return LogJet([sum((self.c[j]*other.c[n-j] for j in range(n+1)), ZERO)
                       for n in range(self.size)])

    __rmul__ = __mul__

    def __truediv__(self, value):
        if isinstance(value, LogJet):
            raise TypeError('LogJet requires only scalar division')
        return LogJet([c/value for c in self.c])

    def __pow__(self, exponent):
        exponent, base = D(exponent), self.c[0]
        if base <= 0:
            raise ValueError('Positive Taylor base required')
        remainder = self/base-1
        coefficient, term, series = ONE, LogJet(1), LogJet(1)
        for degree in range(1, self.size):
            coefficient *= (exponent-degree+1)/degree
            term = term*remainder
            series += coefficient*term
        return power(base, exponent)*series


def count_joint(kind, energy):
    if not A <= energy <= B or not HI_CUT < energy < HEI_CUT:
        raise ValueError('Energy left frozen analytic HI support')
    if COUNTS[kind] >= 4 or COUNTS['combined_kernel_derivative_joint_evaluations'] >= 8:
        raise RuntimeError('Frozen four nodes per path / eight joint calls exceeded')
    COUNTS[kind] += 1
    COUNTS['combined_kernel_derivative_joint_evaluations'] += 1


def record_outputs(result):
    if not all(value.is_finite() for value in result.values()):
        raise ArithmeticError('Nonfinite joint kernel output')
    COUNTS['k_component_outputs'] += 1
    COUNTS['k_prime_component_outputs'] += 1
    COUNTS['k_second_component_outputs'] += 1
    COUNTS['combined_k_kprime_ksecond_component_outputs'] += 3
    COUNTS['sigma_auxiliary_outputs'] += 1
    return result


def jet_kernel(energy, jx, jw):
    count_joint('primary_jet_joint_evaluations', energy)
    ej = LogJet([energy/factorial(n) for n in range(5)])
    xj = ej/E0
    sigma = SIGMA0*(xj-1)**2*xj**(P/2-f64('5.5'))*(
        1+(xj/YA)**D('0.5'))**(-P)*AREA
    product = sigma*(jx+jw*(ej-CHI))
    dn = [product.c[n]*factorial(n) for n in range(5)]
    return record_outputs({
        'sigma_cm2': sigma.c[0],
        'k_s-4': FACTOR*(dn[2]+3*dn[1]),
        'k_prime_s-4_eV-1': FACTOR*(dn[3]+3*dn[2])/energy,
        'k_second_s-4_eV-2': FACTOR*(dn[4]+2*dn[3]-3*dn[2])/(energy*energy),
    })


def scalar_kernel(energy, jx, jw):
    """Explicit D^1..4 log(sigma), Bell polynomials; no LogJet or differences."""
    count_joint('independent_scalar_joint_evaluations', energy)
    x = energy/E0
    z = (x/YA).sqrt()
    r = P/2-f64('5.5')
    sigma = SIGMA0*(x-1)**2*power(x, r)*power(1+z, -P)*AREA
    ell1 = 2*x/(x-1)+r-P*z/(2*(1+z))
    ell2 = -2*x/(x-1)**2-P*z/(4*(1+z)**2)
    ell3 = 2*x*(x+1)/(x-1)**3-P*z*(1-z)/(8*(1+z)**3)
    ell4 = -2*x*(x*x+4*x+1)/(x-1)**4-P*z*(1-4*z+z*z)/(16*(1+z)**4)
    s2 = ell1*ell1+ell2
    s3 = ell1**3+3*ell1*ell2+ell3
    s4 = ell1**4+6*ell1*ell1*ell2+3*ell2*ell2+4*ell1*ell3+ell4
    h, t = jx+jw*(energy-CHI), jw*energy
    return record_outputs({
        'sigma_cm2': sigma,
        'k_s-4': FACTOR*sigma*((s2+3*ell1)*h+(2*ell1+4)*t),
        'k_prime_s-4_eV-1': FACTOR*sigma/energy*((s3+3*s2)*h+(3*s2+9*ell1+4)*t),
        'k_second_s-4_eV-2': FACTOR*sigma/(energy*energy)*(
            (s4+2*s3-3*s2)*h+(4*s3+12*s2+4*ell1)*t),
    })


class BiSeries2:
    """Ordinary coefficients of delta^i * eta^j, i+j<=2, eta=W-w.

    This class does not call LogJet, law_chain or a root postprocessor. Decimal
    and exact Fraction coefficients use the same truncated polynomial algebra.
    """
    powers = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2))

    def __init__(self, value):
        if isinstance(value, dict):
            zero = next(iter(value.values()), 0)*0
            self.c = {p: value.get(p, zero) for p in self.powers}
        else:
            self.c = {p: value if p == (0, 0) else value*0 for p in self.powers}

    @staticmethod
    def lift(value):
        return value if isinstance(value, BiSeries2) else BiSeries2(value)

    def __add__(self, other):
        other = self.lift(other)
        return BiSeries2({p: self.c[p]+other.c[p] for p in self.powers})

    __radd__ = __add__

    def __neg__(self):
        return BiSeries2({p: -self.c[p] for p in self.powers})

    def __sub__(self, other):
        return self+-self.lift(other)

    def __rsub__(self, other):
        return self.lift(other)+-self

    def __mul__(self, other):
        other = self.lift(other)
        result = {p: 0 for p in self.powers}
        for (i, j), x in self.c.items():
            for (k, l), y in other.c.items():
                if i+j+k+l <= 2:
                    result[(i+k, j+l)] += x*y
        return BiSeries2(result)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, BiSeries2):
            return self*other.inverse()
        return BiSeries2({p: value/other for p, value in self.c.items()})

    def __rtruediv__(self, other):
        return self.lift(other)*self.inverse()

    def inverse(self):
        base = self.c[(0, 0)]
        if base == 0:
            raise ZeroDivisionError('Vanishing bivariate series constant')
        tail = (self-base)/base
        return (1-tail+tail*tail)/base

    def __pow__(self, exponent):
        if exponent == 2:
            return self*self
        if exponent == 1:
            return self
        if exponent == 0:
            return self.lift(1)
        raise ValueError('BiSeries2 only needs integer powers 0,1,2')


def law_chain(s, r, w, anchor, mean, pair):
    """Explicit chain rule, endpoint-first ordering; valid off the exact root.

    s=+1,r=L for upper; s=-1,r=H for lower. The geometry part first holds
    center variance V fixed, then V''=-2/3 is added once. Generic scalar
    arithmetic permits the independently known exact quadratic toy.
    """
    den = r*r+w
    p, q = w/den, r*r/den
    center = mean+s*w/r
    pd, pw = 2*r*w/(den*den), r*r/(den*den)
    pdd_geom = 8*r*r*w/(den**3)-2*w/(den*den)
    pdd_var = -2*r*r/(3*den*den)
    pdw, pww = 2*r*(r*r-w)/(den**3), -2*r*r/(den**3)
    cd, cw = s*w/(r*r), s/r
    cdd_geom, cdd_var, cdw = 2*s*w/(r**3), -2*s/(3*r), s/(r*r)
    ke, kep, kepp = pair['anchor']
    kc, kcp, kcpp = pair['center']
    difference = ke-kc
    response = p*ke+q*kc
    first_delta = pd*difference+p*kep*s+q*kcp*cd
    first_W = pw*difference+q*kcp*cw
    fixed_W_terms = {
        'uniform_band_averaging': (p*kepp+q*kcpp)/3,
        'center_variance_V_second': pdd_var*difference+q*kcp*cdd_var,
        'endpoint_curvature': p*kepp*s*s,
        'center_curvature': q*kcpp*cd*cd,
        'endpoint_acceleration': 0*w,
        'center_acceleration_at_fixed_V': q*kcp*cdd_geom,
        'probability_acceleration_at_fixed_V': pdd_geom*difference,
        'probability_endpoint_motion_cross': 2*pd*kep*s,
        'probability_center_motion_cross': -2*pd*kcp*cd,
    }
    second_delta = sum(fixed_W_terms.values(), 0)
    delta_W = (pdw*difference-pd*kcp*cw+pw*(s*kep-cd*kcp)
               +q*(kcpp*cd*cw+kcp*cdw))
    second_W = pww*difference-2*pw*kcp*cw+q*kcpp*cw*cw
    if first_W == 0:
        raise ZeroDivisionError('Stored point has vanishing variance slope')
    coefficient_c = -first_delta/first_W
    coefficient_d = -(second_delta+2*delta_W*coefficient_c
                      +second_W*coefficient_c*coefficient_c)/(2*first_W)
    d_terms = {name: -value/(2*first_W) for name, value in fixed_W_terms.items()}
    d_terms['implicit_root_delta_W_cross'] = -delta_W*coefficient_c/first_W
    d_terms['implicit_root_W_curvature'] = -second_W*coefficient_c*coefficient_c/(2*first_W)
    return {
        'response_s-4': response,
        'B_s-4_eV-1': first_delta,
        'C_s-4_eV-2': first_W,
        'Fdd_s-4_eV-2': second_delta,
        'FdW_s-4_eV-3': delta_W,
        'FWW_s-4_eV-4': second_W,
        'c_eV': coefficient_c,
        'd_dimensionless': coefficient_d,
        'Fdd_decomposition_s-4_eV-2': fixed_W_terms,
        'd_decomposition_dimensionless': d_terms,
        'law': {
            's': s, 'R_eV': r, 'stored_W_eV2': w, 'denominator_eV2': den,
            'anchor_eV': anchor, 'center_eV': center,
            'p_endpoint': p, 'p_center': q,
            'p_delta_eV-1': pd, 'p_W_eV-2': pw,
            'p_dd_fixed_V_eV-2': pdd_geom, 'p_dd_V_second_eV-2': pdd_var,
            'p_dd_fixed_W_eV-2': pdd_geom+pdd_var,
            'p_dW_eV-3': pdw, 'p_WW_eV-4': pww,
            'anchor_delta': s, 'anchor_dd_eV-1': 0*w,
            'center_delta': cd, 'center_W_eV-1': cw,
            'center_dd_fixed_V_eV-1': cdd_geom,
            'center_dd_V_second_eV-1': cdd_var,
            'center_dd_fixed_W_eV-1': cdd_geom+cdd_var,
            'center_dW_eV-2': cdw,
        },
    }


def envelope_series(s, r, w, anchor, mean, pair):
    """Independent bivariate expansion of the exact rational averaged law.

    Coefficients [20],[11],[02] already include their ordinary Taylor factors.
    The implicit root is solved by coefficient matching here, without calling
    law_chain or its derivative/root/decomposition postprocessor.
    """
    delta = BiSeries2({(1, 0): r/r})
    physical_W = BiSeries2({(0, 0): w, (0, 1): r/r})
    radius = r-delta
    variance = physical_W-delta*delta/3
    endpoint = anchor+s*delta
    center = mean+s*variance/radius
    denominator = radius*radius+variance
    p, q = variance/denominator, radius*radius/denominator
    endpoint_displacement = endpoint-anchor
    center_displacement = center-(mean+s*w/r)
    ke, kep, kepp = pair['anchor']
    kc, kcp, kcpp = pair['center']
    endpoint_average = (ke+kep*endpoint_displacement+kepp*endpoint_displacement**2/2
                        +kepp*delta*delta/6)
    center_average = (kc+kcp*center_displacement+kcpp*center_displacement**2/2
                      +kcpp*delta*delta/6)
    response = p*endpoint_average+q*center_average
    numerator = variance*endpoint_average+radius*radius*center_average
    f = response.c
    if f[(0, 1)] == 0:
        raise ZeroDivisionError('Bivariate variance coefficient vanished')
    c = -f[(1, 0)]/f[(0, 1)]
    d = -(f[(2, 0)]+f[(1, 1)]*c+f[(0, 2)]*c*c)/f[(0, 1)]
    mass, first_moment = p+q, p*endpoint+q*center
    actual_variance = p*(endpoint-mean)**2+q*(center-mean)**2+delta*delta/3
    return {
        'response_s-4': f[(0, 0)],
        'B_s-4_eV-1': f[(1, 0)], 'C_s-4_eV-2': f[(0, 1)],
        'Fdd_s-4_eV-2': 2*f[(2, 0)], 'FdW_s-4_eV-3': f[(1, 1)],
        'FWW_s-4_eV-4': 2*f[(0, 2)], 'c_eV': c, 'd_dimensionless': d,
        'response_ordinary_series': f,
        'numerator_ordinary_series': numerator.c,
        'denominator_ordinary_series': denominator.c,
        'moment_series': {'mass': mass.c, 'mean_eV': first_moment.c,
                          'physical_variance_eV2': actual_variance.c},
    }


def select_pair(cache, anchor_label, center_label):
    fields = ('k_s-4', 'k_prime_s-4_eV-1', 'k_second_s-4_eV-2')
    return {'anchor': tuple(cache[anchor_label][field] for field in fields),
            'center': tuple(cache[center_label][field] for field in fields)}


def validate_branch(label, primary, secondary, pair, old_response, old28):
    errors = []
    for field, scale in (
        ('response_s-4', S0), ('B_s-4_eV-1', S1), ('C_s-4_eV-2', S2),
        ('Fdd_s-4_eV-2', S2), ('FdW_s-4_eV-3', S3), ('FWW_s-4_eV-4', S4),
        ('c_eV', None), ('d_dimensionless', None),
    ):
        errors.append(close(label+'__chain_vs_bivariate__'+field,
                            primary[field], secondary[field], scale=scale))
    a, b, cvar = primary['response_s-4'], primary['B_s-4_eV-1'], primary['C_s-4_eV-2']
    k, mixed, n = primary['Fdd_s-4_eV-2'], primary['FdW_s-4_eV-3'], primary['FWW_s-4_eV-4']
    c, d = primary['c_eV'], primary['d_dimensionless']
    law, terms = primary['law'], primary['Fdd_decomposition_s-4_eV-2']
    s, r, w, den = law['s'], law['R_eV'], law['stored_W_eV2'], law['denominator_eV2']
    ke, kep, kepp = pair['anchor']
    kc, kcp, kcpp = pair['center']
    check(label+'__positive_simple_variance_slope', cvar > 0, C=cvar,
          classification='Fixed stored point consistency; inherited positivity premise, not a new certificate')
    check(label+'__supported_positive_law',
          0 < w < L*H and A <= law['center_eV'] <= B
          and 0 < law['p_endpoint'] < 1 and 0 < law['p_center'] < 1)
    close(label+'__stored_root_response_small', a, ZERO, tol=ROOT_TOL, scale=S0)
    close(label+'__stored_PHYS26_residual_consistency', a, old_response, scale=S0)
    close(label+'__PHYS28_residual_consistency', a, D(old28['baseline_response_s-4']), scale=S0)
    close(label+'__PHYS28_B_consistency', b, D(old28['B_partial_delta_compact_s-4_eV-1']), scale=S1)
    close(label+'__PHYS28_C_consistency', cvar, D(old28['S_partial_W_secant_s-4_eV-2']), scale=S2)
    close(label+'__PHYS28_c_consistency', c, D(old28['coefficient_c_eV']))
    close(label+'__V_second_independent_C_identity', terms['center_variance_V_second'], -2*cvar/3, scale=S2)
    close(label+'__d_V_second_is_one_third', primary['d_decomposition_dimensionless']['center_variance_V_second'], ONE/3)
    close(label+'__band_average_weighted_ksecond', terms['uniform_band_averaging'],
          (w*kepp+r*r*kcpp)/(3*den), scale=S2)
    compact_mixed = (s*r*r*kep/(den*den)+s*(r*r-2*w)*kcp/(den*den)
                     +w*kcpp/(r*den)+2*r*(r*r-w)*(ke-kc)/(den**3))
    compact_WW = kcpp/den-2*s*r*kcp/(den*den)-2*r*r*(ke-kc)/(den**3)
    close(label+'__mixed_compact_identity', mixed, compact_mixed, scale=S3)
    close(label+'__WW_compact_identity', n, compact_WW, scale=S4)
    close(label+'__Fdd_decomposition', sum(terms.values(), ZERO), k, scale=S2)
    close(label+'__d_decomposition', sum(primary['d_decomposition_dimensionless'].values(), ZERO), d)
    close(label+'__root_first_coefficient_cancels', b+cvar*c, ZERO, scale=S1)
    close(label+'__root_second_coefficient_cancels', k+2*mixed*c+n*c*c+2*cvar*d, ZERO, scale=S2)
    prev_c = D(old28['coefficient_c_eV'])
    d_prev_c = -(k+2*mixed*prev_c+n*prev_c*prev_c)/(2*cvar)
    close(label+'__d_using_serialized_PHYS28_c_consistency', d, d_prev_c)
    primary['d_using_serialized_PHYS28_c_dimensionless'] = d_prev_c
    primary['difference_new_c_minus_PHYS28_c_eV'] = c-prev_c
    primary['local_response_linearized_displacement_eV2'] = -a/cvar
    primary['stored_PHYS26_response_s-4'] = old_response
    primary['stored_point_interpretation'] = 'Numerical point; c,d describe its same-response local level curve. Exact zero-level theorem requires an exact root. No root correction is performed.'
    numerator = secondary['numerator_ordinary_series']
    for monomial, actual, expected, scale in (
        ('00', numerator[(0, 0)], den*a, S0*18*18),
        ('10', numerator[(1, 0)], den*b-2*r*a, S0*18),
        ('01', numerator[(0, 1)], den*cvar+a, S0),
        ('20', 2*numerator[(2, 0)], den*k-4*r*b+4*a/3, S0),
        ('11', numerator[(1, 1)], den*mixed-2*r*cvar+b, S1),
        ('02', 2*numerator[(0, 2)], den*n+2*cvar, S2),
    ):
        close(label+'__off_root_numerator_identity__'+monomial, actual, expected, scale=scale)
    nd, nw = numerator[(1, 0)], numerator[(0, 1)]
    ndd, ndw, nww = 2*numerator[(2, 0)], numerator[(1, 1)], 2*numerator[(0, 2)]
    d_residual = -(ndd+2*ndw*c+nww*c*c-4*a/3)/(2*(nw-a))
    close(label+'__residual_preserving_numerator_d', d_residual, d)
    primary['off_root_numerator_d_with_residual_dimensionless'] = d_residual
    moments = secondary['moment_series']
    COUNTS['moment_series_evaluations_without_physical_kernel'] += 1
    for name, reference in (
        ('mass', {(0, 0): ONE}), ('mean_eV', {(0, 0): M}),
        ('physical_variance_eV2', {(0, 0): w, (0, 1): ONE}),
    ):
        for ij in BiSeries2.powers:
            close(label+'__moment_series__'+name+'__'+str(ij), moments[name][ij], reference.get(ij, ZERO))
    return max(errors)


def exact_quadratic_toy(label, s, r, w, anchor):
    """Exact rational known limit k(E)=(E-m)^2-w, A(delta,W)=W-w.

    This is a dimensionless mathematical toy, not the physical kernel. The
    analytically known root stays W=w, and all delta derivatives vanish.
    """
    r, w, anchor, mean = Fraction(r), Fraction(w), Fraction(anchor), Fraction(M)
    center = mean+s*w/r
    pair = {'anchor': ((anchor-mean)**2-w, 2*(anchor-mean), Fraction(2)),
            'center': ((center-mean)**2-w, 2*(center-mean), Fraction(2))}
    COUNTS['exact_rational_quadratic_toy_branches'] += 1
    chain = law_chain(s, r, w, anchor, mean, pair)
    COUNTS['exact_rational_quadratic_chain_evaluations'] += 1
    series = envelope_series(s, r, w, anchor, mean, pair)
    COUNTS['exact_rational_quadratic_series_evaluations'] += 1
    expected = {'response_s-4': 0, 'B_s-4_eV-1': 0, 'C_s-4_eV-2': 1,
                'Fdd_s-4_eV-2': 0, 'FdW_s-4_eV-3': 0, 'FWW_s-4_eV-4': 0,
                'c_eV': 0, 'd_dimensionless': 0}
    for path, values in (('chain', chain), ('bivariate', series)):
        for key, truth in expected.items():
            check(label+'__exact_quadratic__'+path+'__'+key,
                  values[key] == truth, actual=values[key], expected=truth,
                  arithmetic='Exact fractions, equality; physical unit suffixes are shared field names only')
    dterms = chain['d_decomposition_dimensionless']
    check(label+'__exact_quadratic_average_d', dterms['uniform_band_averaging'] == Fraction(-1, 3),
          actual=dterms['uniform_band_averaging'], expected=Fraction(-1, 3))
    check(label+'__exact_quadratic_V_d', dterms['center_variance_V_second'] == Fraction(1, 3),
          actual=dterms['center_variance_V_second'], expected=Fraction(1, 3))
    check(label+'__exact_quadratic_d_sum_zero', sum(dterms.values(), 0) == 0,
          actual=sum(dterms.values(), 0), expected=0)
    return {'definition': 'ktoy=(E-m)^2-w, exact Atoy(delta,W)=W-w',
            'arithmetic': 'Exact Fraction; no physical kernel or new point',
            'chain_coefficients': {key: chain[key] for key in expected},
            'series_coefficients': {key: series[key] for key in expected},
            'd_decomposition': dterms, 'has_physical_unit_interpretation': False}


def finite_width_diagnostics(primary, old28, old26_roots, finite_roots, finite_summary):
    comparison = {}
    for label, root_key, finite_key, shift_key in (
        ('upper_root', 'Vstar_eV2', 'W_star_delta', 'W_star_shift_from_PHYS26_eV2'),
        ('lower_root', 'W0_eV2', 'W_0_delta', 'W_0_shift_from_PHYS26_eV2'),
    ):
        w = D(old26_roots[root_key])
        finite_w = D(finite_roots[finite_key]['midpoint_physical_variance_eV2'])
        prior = old28['delta_005_comparison'][label]
        c = D(prior['coefficient_c_eV'])
        d = primary[label]['d_dimensionless']
        actual_shift = finite_w-w
        linear = D(prior['linear_shift_at_delta_005_eV2'])
        residual_linear = D(prior['residual_actual_minus_linear_eV2'])
        quadratic_increment = d*DELTA*DELTA
        quadratic_shift = linear+quadratic_increment
        residual_quadratic = residual_linear-quadratic_increment
        close(label+'__comparison_inherited_actual_shift', actual_shift, D(finite_summary[shift_key]))
        close(label+'__comparison_old_c_and_linear', linear, c*DELTA)
        close(label+'__comparison_old_linear_residual', residual_linear, actual_shift-linear)
        close(label+'__comparison_quadratic_residual_identity', residual_quadratic, actual_shift-quadratic_shift)
        check(label+'__comparison_nonzero_observed_denominators', actual_shift != 0 and residual_linear != 0)
        comparison[label] = {
            'PHYS26_zero_width_root_eV2': w,
            'PHYS27_delta_005_root_eV2': finite_w,
            'serialized_PHYS28_c_eV': c,
            'PHYS29_d_dimensionless': d,
            'actual_shift_at_delta_005_eV2': actual_shift,
            'linear_shift_from_PHYS28_eV2': linear,
            'quadratic_increment_d_delta_squared_eV2': quadratic_increment,
            'quadratic_predicted_shift_eV2': quadratic_shift,
            'quadratic_predicted_root_eV2': w+quadratic_shift,
            'linear_residual_from_PHYS28_eV2': residual_linear,
            'residual_actual_minus_quadratic_eV2': residual_quadratic,
            'signed_fraction_of_linear_residual_accounted_for': quadratic_increment/residual_linear,
            'absolute_quadratic_to_linear_residual_ratio': abs(residual_quadratic/residual_linear),
            'absolute_quadratic_residual_relative_to_actual_shift': abs(residual_quadratic/actual_shift),
            'absolute_quadratic_residual_relative_to_actual_shift_percent': 100*abs(residual_quadratic/actual_shift),
            'observed_quadratic_residual_smaller': abs(residual_quadratic) < abs(residual_linear),
            'classification': 'One inherited positive width diagnostic, no accuracy, improvement or convergence acceptance criterion',
            'prediction_coefficient_sources': 'Exactly serialized PHYS28 linear shift and c; new PHYS29 primary d using its internally recomputed c, checked against stored c without root refinement',
        }
    upper, lower = comparison['upper_root'], comparison['lower_root']
    previous = old28['delta_005_comparison']['coexistence_width']
    old_width = D(previous['PHYS26_width_eV2'])
    new_width = D(previous['PHYS27_delta_005_width_eV2'])
    linear_reduction = D(previous['linear_reduction_at_delta_005_eV2'])
    actual_reduction = D(previous['actual_reduction_at_delta_005_eV2'])
    linear_residual = D(previous['reduction_residual_actual_minus_linear_eV2'])
    d_reduction = primary['upper_root']['d_dimensionless']-primary['lower_root']['d_dimensionless']
    second_reduction = d_reduction*DELTA*DELTA
    quadratic_reduction = linear_reduction+second_reduction
    quadratic_residual = linear_residual-second_reduction
    close('coexistence__stored_width_difference', old_width-new_width, actual_reduction)
    close('coexistence__quadratic_increment', second_reduction,
          upper['quadratic_increment_d_delta_squared_eV2']-lower['quadratic_increment_d_delta_squared_eV2'])
    close('coexistence__residual_difference', quadratic_residual,
          upper['residual_actual_minus_quadratic_eV2']-lower['residual_actual_minus_quadratic_eV2'])
    close('coexistence__quadratic_reduction_identity', quadratic_reduction+quadratic_residual, actual_reduction)
    comparison['coexistence_width'] = {
        'PHYS26_width_eV2': old_width, 'PHYS27_delta_005_width_eV2': new_width,
        'width_second_order_coefficient_dimensionless': -d_reduction,
        'reduction_second_order_coefficient_dimensionless': d_reduction,
        'linear_reduction_from_PHYS28_eV2': linear_reduction,
        'quadratic_reduction_increment_eV2': second_reduction,
        'quadratic_predicted_reduction_eV2': quadratic_reduction,
        'quadratic_predicted_width_eV2': old_width-quadratic_reduction,
        'actual_reduction_from_PHYS28_eV2': actual_reduction,
        'linear_reduction_residual_from_PHYS28_eV2': linear_residual,
        'residual_actual_minus_quadratic_reduction_eV2': quadratic_residual,
        'signed_fraction_of_linear_residual_accounted_for': second_reduction/linear_residual,
        'absolute_quadratic_to_linear_residual_ratio': abs(quadratic_residual/linear_residual),
        'absolute_quadratic_reduction_residual_relative_to_actual': abs(quadratic_residual/actual_reduction),
        'absolute_quadratic_reduction_residual_relative_to_actual_percent': 100*abs(quadratic_residual/actual_reduction),
        'observed_quadratic_residual_smaller': abs(quadratic_residual) < abs(linear_residual),
        'classification': 'Single stored width diagnostic only, no remainder or rate certificate',
    }
    return comparison


def science(result):
    protocol = json.loads((HERE/'PROTOCOL.json').read_bytes())
    freeze = json.loads((HERE/'PREEXECUTION_FROZEN.json').read_bytes())
    check('contract_expected_sha256', digest(ROOT/'PHYSICS_CONTRACT.json') == EXPECTED_CONTRACT)
    check('protocol_expected_sha256', digest(HERE/'PROTOCOL.json') == EXPECTED_PROTOCOL)
    identities = {}
    for item in freeze['files']:
        relative = Path(item['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Frozen input path must remain within this portable root')
        path = ROOT/relative
        actual_hash, actual_size = digest(path), path.stat().st_size
        check('frozen_identity__'+item['path'], actual_hash == item['sha256'] and actual_size == item['bytes'],
              actual_sha256=actual_hash, expected_sha256=item['sha256'],
              actual_bytes=actual_size, expected_bytes=item['bytes'])
        identities[item['path']] = actual_hash
    identities['contributions/numerics/PREEXECUTION_FROZEN.json'] = digest(HERE/'PREEXECUTION_FROZEN.json')
    result['identity_sha256'] = identities
    if any(not row['pass'] for row in CHECKS):
        raise RuntimeError('Preexecution identity failed before any physical kernel call')
    jdata = json.loads((ROOT/'inputs/PHYS22_INITIAL_COEFFICIENTS.json').read_bytes())
    old26 = json.loads((ROOT/'inputs/PHYS26/contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json').read_bytes())
    finite = json.loads((ROOT/'inputs/PHYS27/contributions/numerics/FINITE_WIDTH_FIRST.json').read_bytes())
    old28 = json.loads((ROOT/'inputs/PHYS28/contributions/numerics/SMALL_WIDTH_FIRST.json').read_bytes())
    roots = old26['inherited_boundary_residuals']
    finite_summary = finite['threshold_comparison']
    jx, jw = [D(jdata['results']['baseline_local']['J_nonphoto'][2][i]) for i in (0, 3)]
    wstar, wzero = D(roots['Vstar_eV2']), D(roots['W0_eV2'])
    for name, data in (('PHYS26', old26), ('PHYS27', finite), ('PHYS28', old28)):
        check('inherited_'+name+'_all_pass', data['summary']['all_pass'], replayed=False)
    check('PHYS26_root_strings_unchanged_in_PHYS27', roots['Vstar_eV2'] == finite_summary['PHYS26_Vstar0_eV2']
          and roots['W0_eV2'] == finite_summary['PHYS26_W00_eV2'])
    check('PHYS26_root_strings_unchanged_in_PHYS28',
          roots['Vstar_eV2'] == old28['constants']['PHYS26_root_strings_consumed_exactly']['W_star_zero_eV2']
          and roots['W0_eV2'] == old28['constants']['PHYS26_root_strings_consumed_exactly']['W_zero_zero_eV2'])
    check('finite_root_raw_records_equal_summary',
          finite['new_physical_roots']['W_star_delta']['midpoint_physical_variance_eV2'] == finite_summary['W_star_delta_eV2']
          and finite['new_physical_roots']['W_0_delta']['midpoint_physical_variance_eV2'] == finite_summary['W_0_delta_eV2'])
    check('frozen_half_width_support_mean', D(finite['constants']['half_width_eV']) == DELTA
          and [D(x) for x in finite['constants']['photon_support_eV']] == [A, B]
          and D(finite['constants']['mean_eV']) == M)
    check('analytic_HI_support', HI_CUT < A < M < B < HEI_CUT)
    check('source_manifest_identity', digest(ROOT/'SOURCE_MANIFEST.json') ==
          next(item['sha256'] for item in protocol['inputs'] if item['path'] == 'SOURCE_MANIFEST.json'))
    for key, value in (('N0_per_H', N0), ('q_s-2', Q), ('kappa_s-1_cm-2', KAPPA),
                       ('prefactor', FACTOR), ('chi_eV', CHI), ('E0_eV', E0),
                       ('ya', YA), ('P', P), ('J_h2_x', jx), ('J_h2_w', jw)):
        expected = D(old26['constants'][key])
        close('inherited_constant__'+key, value, expected, scale=max(abs(value), abs(expected)))
    result['constants'] = {
        'support_eV': [A, B], 'mean_eV': M, 'L_eV': L, 'H_eV': H,
        'comparison_half_width_eV': DELTA, 'N0_per_H': N0, 'q_s-2': Q,
        'kappa_s-1_cm-2': KAPPA, 'factor_q_N0_kappa_over_180': FACTOR,
        'chi_eV': CHI, 'E0_eV': E0, 'ya': YA, 'P': P,
        'sigma0': SIGMA0, 'area_cm2': AREA, 'J_h2_x': jx, 'J_h2_w': jw,
        'stored_PHYS26_root_strings': {'upper_root': roots['Vstar_eV2'], 'lower_root': roots['W0_eV2']},
        'arithmetic_interpretation': 'Exact-real source binary64 literals followed by Decimal80 operations, not native arithmetic emulation',
    }
    nodes = {'a': A, 'v_star': M+wstar/L, 'u_zero': M-wzero/H, 'b': B}
    COUNTS['actual_unique_energy_nodes'] = len(set(nodes.values()))
    check('exactly_four_distinct_supported_nodes', len(set(nodes.values())) == 4 and all(A <= e <= B for e in nodes.values()))
    check('four_nodes_match_serialized_PHYS28', all(value == D(old28['energy_nodes_eV'][key]) for key, value in nodes.items()))
    result['energy_nodes_eV'] = nodes
    if any(not row['pass'] for row in CHECKS):
        raise RuntimeError('Frozen inherited-input consistency failed before physical kernel calls')
    cache = {}
    for path, kernel in (('jet', jet_kernel), ('scalar', scalar_kernel)):
        cache[path] = {label: kernel(energy, jx, jw) for label, energy in nodes.items()}
    result['joint_kernel_outputs'] = cache
    kernel_errors = []
    for label in nodes:
        for field, scale in (('sigma_cm2', D('1e-18')), ('k_s-4', S0),
                             ('k_prime_s-4_eV-1', S1), ('k_second_s-4_eV-2', S2)):
            kernel_errors.append(close('kernel_expression__'+label+'__'+field,
                                       cache['jet'][label][field], cache['scalar'][label][field], scale=scale))
        for path in ('jet', 'scalar'):
            for field, scale in (('k_s-4', S0), ('k_prime_s-4_eV-1', S1)):
                close('cached_PHYS28_consistency__'+path+'__'+label+'__'+field,
                      cache[path][label][field], D(old28['joint_kernel_outputs'][path][label][field]), scale=scale)
    primary, secondary, toys, branch_errors = {}, {}, {}, []
    for label, s, r, w, anchor, anchor_label, center_label, residual_key in (
        ('upper_root', 1, L, wstar, A, 'a', 'v_star', 'Pa_response_s-4'),
        ('lower_root', -1, H, wzero, B, 'b', 'u_zero', 'Pb_response_s-4'),
    ):
        primary_pair = select_pair(cache['jet'], anchor_label, center_label)
        secondary_pair = select_pair(cache['scalar'], anchor_label, center_label)
        primary[label] = law_chain(s, r, w, anchor, M, primary_pair)
        COUNTS['physical_chain_branch_evaluations_from_cached_values'] += 1
        secondary[label] = envelope_series(s, r, w, anchor, M, secondary_pair)
        COUNTS['physical_series_branch_evaluations_from_cached_values'] += 1
        branch_errors.append(validate_branch(label, primary[label], secondary[label], primary_pair,
                                              D(roots[residual_key]), old28['sensitivity']['jet'][label]))
        toys[label] = exact_quadratic_toy(label, s, r, w, anchor)
    result['second_order'] = {'jet_chain': primary, 'scalar_bivariate': secondary}
    result['exact_quadratic_toys'] = toys
    result['delta_005_comparison'] = finite_width_diagnostics(primary, old28, roots, finite['new_physical_roots'], finite_summary)
    check('actual_joint_evaluation_counts_match_freeze', COUNTS['primary_jet_joint_evaluations'] == 4
          and COUNTS['independent_scalar_joint_evaluations'] == 4
          and COUNTS['combined_kernel_derivative_joint_evaluations'] == 8)
    check('actual_separate_component_output_counts', COUNTS['k_component_outputs'] == 8
          and COUNTS['k_prime_component_outputs'] == 8 and COUNTS['k_second_component_outputs'] == 8
          and COUNTS['combined_k_kprime_ksecond_component_outputs'] == 24)
    check('actual_cached_and_exact_toy_counts', COUNTS['physical_chain_branch_evaluations_from_cached_values'] == 2
          and COUNTS['physical_series_branch_evaluations_from_cached_values'] == 2
          and COUNTS['moment_series_evaluations_without_physical_kernel'] == 2
          and COUNTS['exact_rational_quadratic_toy_branches'] == 2
          and COUNTS['exact_rational_quadratic_chain_evaluations'] == 2
          and COUNTS['exact_rational_quadratic_series_evaluations'] == 2)
    check('forbidden_execution_counts_zero', all(COUNTS[key] == 0 for key in (
        'new_physical_root_searches', 'physical_root_iterations', 'old_module_imports',
        'old_main_invocations', 'closed_suite_replays', 'old_physical_root_searches',
        'quadrature_evaluations', 'finite_difference_evaluations', 'width_root_sweep',
        'new_derivative_sign_campaigns', 'native_runs', 'gas_IVP_runs',
        'dense_LP_or_multiple_parameter_campaigns', 'display_new_kernel_derivative_evaluations')))
    result['maximum_scaled_kernel_expression_error'] = max(kernel_errors)
    result['maximum_scaled_independent_envelope_error'] = max(branch_errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    output = Path(parser.parse_args().output)
    if output.exists():
        raise FileExistsError('Fresh output required; earlier evidence is never overwritten')
    result = {
        'task': 'REI-PHYS29-20261011',
        'evidence_class': ['numerically checked', 'implementation-verified within frozen formulas'],
        'role': 'NONBLIND numerical designer/generator, not final decision reviewer',
        'python_version': platform.python_version(), 'decimal_precision': getcontext().prec,
        'coefficient_definition': 'd=Wsecond(0)/2. Exact-root theorem evaluated here at stored numerical points, with nonzero residual and same-level interpretation retained.',
        'claim_ceiling': [
            'Finite Decimal agreement is not a directed interval or physical uncertainty enclosure.',
            'Stored PHYS26/27 roots remain uncorrected numerical approximations.',
            'No sign or nonzero premise or acceptance test is imposed on d.',
            'Two kernel expressions and two envelope/root algorithms share fit, source constants, J and Decimal transcendental operations; they are not independent physical data.',
            'The Fraction quadratic toy is exact mathematical validation, with no physical kernel evaluations.',
            'At most 12 significant digits in prose; full stored decimals support reproduction only.',
            'One inherited delta=.05 comparison supplies no quantitative Taylor remainder, convergence rate, validity window or positive-width nesting claim.',
            'No J/atomic/gas uncertainty, native equivalence, finite-time/epsilon remainder, emitter/history admission or novelty priority.',
        ],
        'physical_admission': 'HOLD',
    }
    error = False
    try:
        science(result)
    except Exception as exc:
        error = True
        traceback.print_exc()
        result['execution_failure'] = {'type': type(exc).__name__, 'message': str(exc),
                                       'classification': 'Observed execution failure; no silent fallback or hidden rerun',
                                       'posthoc_tolerance_relaxation': False}
    failures = [row['name'] for row in CHECKS if not row['pass']]
    result['checks'] = CHECKS
    result['summary'] = {'total_checks': len(CHECKS), 'passed': len(CHECKS)-len(failures),
                         'failed': len(failures), 'failed_names': failures,
                         'all_pass': not error and not failures, 'actual_counts': COUNTS}
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(serial(result), stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(serial({'summary': result['summary'],
                             'second_order_coefficients': {
                                 label: {'c_eV': data['c_eV'], 'd_dimensionless': data['d_dimensionless']}
                                 for label, data in result.get('second_order', {}).get('jet_chain', {}).items()},
                             'result_sha256': digest(output)}), ensure_ascii=False))
    return 0 if result['summary']['all_pass'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
