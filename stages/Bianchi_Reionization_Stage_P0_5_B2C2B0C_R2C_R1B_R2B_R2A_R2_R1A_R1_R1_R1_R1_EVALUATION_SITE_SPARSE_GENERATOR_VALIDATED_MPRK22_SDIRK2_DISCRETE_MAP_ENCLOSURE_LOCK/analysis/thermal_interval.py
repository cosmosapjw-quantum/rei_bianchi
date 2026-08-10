#!/usr/bin/env python3
"""Outward binary64 interval bound for the thermal RHS log-T derivative.

The implementation mirrors ``ThermalContext.rhs_and_derivative`` term by term.
It deliberately certifies only the scalar thermal root with populations,
volumes, photoheating and Hubble rate frozen at a source-evaluation site.  It is
not a certificate for the full four-site state-feedback map.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class Interval:
    lower: np.ndarray
    upper: np.ndarray

    def __post_init__(self) -> None:
        lo = np.asarray(self.lower, dtype=np.float64)
        hi = np.asarray(self.upper, dtype=np.float64)
        if lo.shape != hi.shape or np.any(np.isnan(lo)) or np.any(np.isnan(hi)):
            raise ValueError("invalid interval shape or NaN")
        if np.any(lo > hi):
            raise ValueError("interval lower bound exceeds upper bound")
        object.__setattr__(self, "lower", np.ascontiguousarray(lo))
        object.__setattr__(self, "upper", np.ascontiguousarray(hi))


def _down(value) -> np.ndarray:
    return np.nextafter(np.asarray(value, dtype=np.float64), -np.inf)


def _up(value) -> np.ndarray:
    return np.nextafter(np.asarray(value, dtype=np.float64), np.inf)


def _point(value, shape: tuple[int, ...] | None = None) -> Interval:
    arr = np.asarray(value, dtype=np.float64)
    if shape is not None:
        arr = np.broadcast_to(arr, shape)
    return Interval(arr, arr)


def _add(a: Interval, b: Interval) -> Interval:
    return Interval(_down(a.lower + b.lower), _up(a.upper + b.upper))


def _neg(a: Interval) -> Interval:
    return Interval(_down(-a.upper), _up(-a.lower))


def _sub(a: Interval, b: Interval) -> Interval:
    return _add(a, _neg(b))


def _mul(a: Interval, b: Interval) -> Interval:
    products = np.stack(
        (
            a.lower * b.lower,
            a.lower * b.upper,
            a.upper * b.lower,
            a.upper * b.upper,
        ),
        axis=0,
    )
    return Interval(_down(np.min(products, axis=0)), _up(np.max(products, axis=0)))


def _reciprocal(a: Interval) -> Interval:
    if np.any((a.lower <= 0.0) & (a.upper >= 0.0)):
        raise ValueError("reciprocal interval contains zero")
    lo = 1.0 / a.upper
    hi = 1.0 / a.lower
    return Interval(_down(np.minimum(lo, hi)), _up(np.maximum(lo, hi)))


def _div(a: Interval, b: Interval) -> Interval:
    return _mul(a, _reciprocal(b))


def _exp(a: Interval) -> Interval:
    lo = np.exp(a.lower)
    hi = np.exp(a.upper)
    # exp is positive.  Zero is a valid outward lower bound after underflow.
    return Interval(np.maximum(_down(lo), 0.0), _up(hi))


def _sqrt(a: Interval) -> Interval:
    if np.any(a.lower < 0.0):
        raise ValueError("sqrt interval crosses the negative real axis")
    return Interval(np.maximum(_down(np.sqrt(a.lower)), 0.0), _up(np.sqrt(a.upper)))


def _pow_positive(a: Interval, exponent: float) -> Interval:
    if np.any(a.lower <= 0.0):
        raise ValueError("positive power base must be strictly positive")
    p = float(exponent)
    if not math.isfinite(p):
        raise ValueError("power exponent must be finite")
    if p >= 0.0:
        lo = np.power(a.lower, p)
        hi = np.power(a.upper, p)
    else:
        lo = np.power(a.upper, p)
        hi = np.power(a.lower, p)
    return Interval(_down(np.minimum(lo, hi)), _up(np.maximum(lo, hi)))


def _square(a: Interval) -> Interval:
    lo2 = a.lower * a.lower
    hi2 = a.upper * a.upper
    crosses = (a.lower <= 0.0) & (a.upper >= 0.0)
    lower = np.where(crosses, 0.0, np.minimum(lo2, hi2))
    upper = np.maximum(lo2, hi2)
    return Interval(np.maximum(_down(lower), 0.0), _up(upper))


def _constant(value: float, shape: tuple[int, ...]) -> Interval:
    return _point(np.full(shape, float(value), dtype=np.float64))


def rhs_derivative_interval(context, log_temperature_lower, log_temperature_upper):
    """Return an outward interval for ``d thermal_rhs / d log(T)``.

    Parameters in ``context`` are held fixed.  The output arrays have the same
    shape as ``context.photoheat`` and enclose every derivative over the supplied
    componentwise log-temperature box.
    """
    xlo = np.asarray(log_temperature_lower, dtype=np.float64)
    xhi = np.asarray(log_temperature_upper, dtype=np.float64)
    shape = np.asarray(context.photoheat).shape
    if xlo.shape != shape or xhi.shape != shape:
        raise ValueError("log-temperature interval must have the context shape")
    if np.any(~np.isfinite(xlo)) or np.any(~np.isfinite(xhi)) or np.any(xlo > xhi):
        raise ValueError("invalid log-temperature interval")

    x = Interval(xlo, xhi)
    one = _constant(1.0, shape)
    T = _exp(x)
    invT = _reciprocal(T)

    ll_h = _mul(_constant(315614.0, shape), invT)
    ll_hei = _mul(_constant(570670.0, shape), invT)
    ll_heii = _mul(_constant(1263030.0, shape), invT)

    x_rec_h = _pow_positive(_div(ll_h, _constant(2.250, shape)), 0.376)
    rec_h = _div(
        _mul(
            _mul(_constant(3.435e-30, shape), T),
            _pow_positive(ll_h, 1.970),
        ),
        _pow_positive(_add(one, x_rec_h), 3.720),
    )
    dlog_rec_h = _add(
        _constant(-0.970, shape),
        _mul(
            _constant(3.720 * 0.376, shape),
            _div(x_rec_h, _add(one, x_rec_h)),
        ),
    )

    rec_heii = _mul(
        _mul(_constant(1.380649e-16 * 1.26e-14, shape), T),
        _pow_positive(ll_hei, 0.750),
    )
    dlog_rec_heii = _constant(0.250, shape)

    x_rec_heiii = _pow_positive(_div(ll_heii, _constant(2.250, shape)), 0.376)
    rec_heiii = _div(
        _mul(
            _mul(_constant(8.0 * 3.435e-30, shape), T),
            _pow_positive(ll_heii, 1.970),
        ),
        _pow_positive(_add(one, x_rec_heiii), 3.720),
    )
    dlog_rec_heiii = _add(
        _constant(-0.970, shape),
        _mul(
            _constant(3.720 * 0.376, shape),
            _div(x_rec_heiii, _add(one, x_rec_heiii)),
        ),
    )

    sqrt_t = _sqrt(_div(T, _constant(1.0e5, shape)))
    exc_h = _div(
        _mul(
            _constant(7.5e-19, shape),
            _exp(_neg(_mul(_constant(118348.0, shape), invT))),
        ),
        _add(one, sqrt_t),
    )
    dlog_exc_h = _sub(
        _mul(_constant(118348.0, shape), invT),
        _mul(
            _constant(0.5, shape),
            _div(sqrt_t, _add(one, sqrt_t)),
        ),
    )

    exc_heii = _div(
        _mul(
            _mul(_constant(5.54e-17, shape), _pow_positive(T, -0.397)),
            _exp(_neg(_mul(_constant(473638.0, shape), invT))),
        ),
        _add(one, sqrt_t),
    )
    dlog_exc_heii = _sub(
        _add(
            _constant(-0.397, shape),
            _mul(_constant(473638.0, shape), invT),
        ),
        _mul(
            _constant(0.5, shape),
            _div(sqrt_t, _add(one, sqrt_t)),
        ),
    )

    sqrt_T = _sqrt(T)
    beta_h = _mul(
        _mul(_constant(5.835e-11, shape), sqrt_T),
        _exp(_neg(_mul(_constant(157804.0, shape), invT))),
    )
    beta_hei = _mul(
        _mul(_constant(2.71e-11, shape), sqrt_T),
        _exp(_neg(_mul(_constant(285331.0, shape), invT))),
    )
    beta_heii = _mul(
        _mul(_constant(5.707e-12, shape), sqrt_T),
        _exp(_neg(_mul(_constant(631495.0, shape), invT))),
    )
    dlog_beta_h = _add(_constant(0.5, shape), _mul(_constant(157804.0, shape), invT))
    dlog_beta_hei = _add(_constant(0.5, shape), _mul(_constant(285331.0, shape), invT))
    dlog_beta_heii = _add(_constant(0.5, shape), _mul(_constant(631495.0, shape), invT))

    q = _sub(
        _constant(5.5, shape),
        _div(x, _constant(math.log(10.0), shape)),
    )
    gaussian = _exp(_neg(_div(_square(q), _constant(3.0, shape))))
    gaunt = _add(_constant(1.1, shape), _mul(_constant(0.34, shape), gaussian))
    ff = _mul(_mul(_constant(1.42e-27, shape), sqrt_T), gaunt)
    dlog_gaussian = _mul(_constant(2.0 / (3.0 * math.log(10.0)), shape), q)
    dlog_ff = _add(
        _constant(0.5, shape),
        _mul(
            _div(_mul(_constant(0.34, shape), gaussian), gaunt),
            dlog_gaussian,
        ),
    )

    terms = (
        _mul(_point(context.factor_rec_h), rec_h),
        _mul(_point(context.factor_rec_heii), rec_heii),
        _mul(_point(context.factor_rec_heiii), rec_heiii),
        _mul(_point(context.factor_exc_h), exc_h),
        _mul(_point(context.factor_exc_heii), exc_heii),
        _mul(_point(context.factor_ion_h), beta_h),
        _mul(_point(context.factor_ion_hei), beta_hei),
        _mul(_point(context.factor_ion_heii), beta_heii),
        _mul(_point(context.factor_ff), ff),
    )
    slopes = (
        dlog_rec_h,
        dlog_rec_heii,
        dlog_rec_heiii,
        dlog_exc_h,
        dlog_exc_heii,
        dlog_beta_h,
        dlog_beta_hei,
        dlog_beta_heii,
        dlog_ff,
    )

    dcooling = _constant(0.0, shape)
    for term, slope in zip(terms, slopes):
        dcooling = _add(dcooling, _mul(term, slope))
    expansion = _mul(_point(context.expansion_coefficient), T)
    derivative = _sub(_neg(dcooling), expansion)
    return derivative.lower, derivative.upper
