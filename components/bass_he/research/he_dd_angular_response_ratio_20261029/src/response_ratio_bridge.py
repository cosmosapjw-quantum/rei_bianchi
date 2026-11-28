"""Certified algebraic response-ratio sensitivity; no detector efficiency inference.

Conditionally reweight an already-admitted angular density f by q(theta)>0;
q_max/q_min is externally specified, and not measured by EXFOR.
This module does not change the source data, LP certification, rates, or IVPs.
"""
from fractions import Fraction


def _rational(x):
    if isinstance(x, (bool, float)) or not isinstance(x, (Fraction, int, str)):
        raise TypeError('exact Fraction/int/decimal string required, never float/bool')
    return Fraction(x)


def ratio_from_symmetric_relative_error(delta):
    """If response q is in [1-delta,1+delta] times a constant."""
    d = _rational(delta)
    if not 0 <= d < 1:
        raise ValueError('Require 0<=delta<1, not a detector measurement')
    return (1 + d) / (1 - d)


def reweight_bounds(b_lo, b_hi, response_ratio):
    """Sharp universal *moment-only* algebraic outer bound, exact rationals.

    For 0<=v<=1, b=E[v], q>0, 1<=max q/min q<=r,
        b/(b+r(1-b)) <= E[q*v]/E[q] <= r*b/(1-b+r*b).
    Sharp at 0/1-valued v, not claimed sharp for cos^2 within L-Lipschitz f.
    """
    lo, hi, r = map(_rational, (b_lo, b_hi, response_ratio))
    if not 0 <= lo <= hi <= 1:
        raise ValueError('Expected 0<=b_lo<=b_hi<=1')
    if r < 1:
        raise ValueError('Expected response_ratio>=1')
    return lo / (lo + r * (1-lo)), r*hi / (1-hi + r*hi)


def uniform_difference_bound(response_ratio):
    """Bound using rational squared form; returns algebraic expression only
    when sqrt is irrational. For rational-square ratio return exact Fraction.
    """
    from math import isqrt
    r = _rational(response_ratio)
    if r < 1:
        raise ValueError('ratio<1')
    ns, ds = isqrt(r.numerator), isqrt(r.denominator)
    if ns*ns == r.numerator and ds*ds == r.denominator:
        return Fraction(ns-ds, ns+ds)
    return None


def source_model_status():
    """Explicitly blocks physical admission regardless of response-ratio tests."""
    return {'actual_detector_response_qualified': False,
            'relative_response_envelope_measured': False,
            'kappa': None, 'R_event': None, 'heat_rate': None,
            'physical_activation': False, 'L4': False, 'production': 'HOLD'}
