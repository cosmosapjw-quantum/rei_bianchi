"""Exact rational transcription helpers for T1 synthetic theory checks only.

These helpers do not evaluate a source integral, a special function or HH data.
The mathematical proof, not finite test sampling, establishes the inequalities.
"""
from fractions import Fraction as Q


def rational(x):
    if type(x) not in (int, Q):
        raise TypeError('explicit integer/Fraction required')
    return Q(x)


def rectangle(value):
    if len(value) != 4:
        raise ValueError('four exact rectangle endpoints required')
    lo, hi, imlo, imhi = map(rational, value)
    if lo > hi or imlo > imhi:
        raise ValueError('unordered rectangle')
    return lo, hi, imlo, imhi


def inverse(z):
    x, y = map(rational, z)
    square = x*x+y*y
    if not square:
        raise ValueError('zero denominator')
    return x/square, -y/square


def shifted_bounds(a, box):
    a = rational(a)
    lo, hi, imlo, imhi = rectangle(box)
    alpha, xmax = a+lo, a+hi
    if a <= 0 or alpha <= 0:
        raise ValueError('positive source exponent/shifted margin required')
    ymax = max(abs(imlo), abs(imhi))
    q = xmax*xmax+ymax*ymax
    return {'alpha': alpha, 'q': q, 'inverse_real_lower': alpha/q,
            'inverse_modulus_upper': 1/alpha}


def sigma_bounds(a, t, b, u):
    aa, bb = shifted_bounds(a, t), shifted_bounds(b, u)
    lower = (aa['inverse_real_lower']+bb['inverse_real_lower'])/2
    upper = (aa['inverse_modulus_upper']+bb['inverse_modulus_upper'])/2
    return lower, upper


def density_geometry(box):
    lo, hi, imlo, imhi = rectangle(box)
    if not (lo > 0 or imlo > 0 or imhi < 0):
        raise ValueError('rectangle meets principal branch cut')
    dx, dy = max(lo, -hi, Q(0)), max(imlo, -imhi, Q(0))
    tau2 = dx*dx+dy*dy
    assert tau2 > 0
    return {'tau_squared': tau2, 'exponential_growth_per_lambda': max(Q(0), -lo)/tau2}


def source_geometry(a, box, D):
    a, D = rational(a), rational(D)
    lo, hi, _, _ = rectangle(box)
    shifted = shifted_bounds(a, box)
    if D < 0:
        raise ValueError('nonnegative center norm bound required')
    alpha = shifted['alpha']
    return {'alpha': alpha, 'mean_factor': a/alpha,
            'displacement_factor': max(abs(lo/(a+lo)), abs(hi/(a+hi))),
            'attenuation_log_upper': a*max(Q(0), -lo)*D*D/alpha}


def dyadic_radius(positive_left):
    left = rational(positive_left)
    if left <= 0:
        raise ValueError('positive real left endpoint required')
    radius = Q(1)
    while radius > left/4:
        radius /= 2
    return radius
