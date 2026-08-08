"""Minimal outward-rounded interval arithmetic for the R2-R1A-R1 certificate.

The implementation deliberately uses NumPy ``nextafter`` around every primitive
result.  It is not a replacement for an MPFI/MPFR package, but it provides a
small, reviewable binary64 enclosure layer for the project-specific validated
flow audit.  Independent dense sampling and long-double replays remain required.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

ArrayLike = np.ndarray | float | int | Iterable[float]


def _arr(value: ArrayLike) -> np.ndarray:
    return np.asarray(value, dtype=np.float64)


def _down(value: ArrayLike) -> np.ndarray:
    a = _arr(value)
    return np.nextafter(a, -np.inf)


def _up(value: ArrayLike) -> np.ndarray:
    a = _arr(value)
    return np.nextafter(a, np.inf)


def _guard_broadcast(a: np.ndarray, b: np.ndarray, operation: str) -> None:
    shape = np.broadcast_shapes(a.shape, b.shape)
    if int(np.prod(shape, dtype=np.int64)) > 10_000_000:
        raise MemoryError(f"{operation} broadcast shape explosion: {a.shape} with {b.shape} -> {shape}")


@dataclass(frozen=True)
class Interval:
    """Closed componentwise interval ``[lo, hi]``."""

    __array_priority__ = 10000

    lo: np.ndarray
    hi: np.ndarray

    def __init__(self, lo: ArrayLike, hi: ArrayLike | None = None) -> None:
        lower = _arr(lo)
        upper = lower.copy() if hi is None else _arr(hi)
        lower, upper = np.broadcast_arrays(lower, upper)
        if lower.size > 10_000_000:
            raise MemoryError(f"interval shape explosion: {lower.shape}")
        if np.any(np.isnan(lower)) or np.any(np.isnan(upper)):
            raise ValueError("interval endpoints must not be NaN")
        if np.any(lower > upper):
            raise ValueError("interval lower endpoint exceeds upper endpoint")
        object.__setattr__(self, "lo", np.array(lower, copy=True))
        object.__setattr__(self, "hi", np.array(upper, copy=True))

    @property
    def mid(self) -> np.ndarray:
        # This is a point heuristic, not a certified operation.
        return self.lo + 0.5 * (self.hi - self.lo)

    @property
    def width(self) -> np.ndarray:
        return _up(self.hi - self.lo)

    @property
    def radius(self) -> np.ndarray:
        return _up(0.5 * (self.hi - self.lo))

    def contains(self, value: ArrayLike) -> np.ndarray:
        a = _arr(value)
        return (self.lo <= a) & (a <= self.hi)

    def __neg__(self) -> "Interval":
        return Interval(_down(-self.hi), _up(-self.lo))

    def __add__(self, other: ArrayLike | "Interval") -> "Interval":
        b = as_interval(other)
        _guard_broadcast(self.lo, b.lo, "add")
        return Interval(_down(self.lo + b.lo), _up(self.hi + b.hi))

    __radd__ = __add__

    def __sub__(self, other: ArrayLike | "Interval") -> "Interval":
        b = as_interval(other)
        _guard_broadcast(self.lo, b.lo, "sub")
        return Interval(_down(self.lo - b.hi), _up(self.hi - b.lo))

    def __rsub__(self, other: ArrayLike | "Interval") -> "Interval":
        return as_interval(other).__sub__(self)

    def __mul__(self, other: ArrayLike | "Interval") -> "Interval":
        b = as_interval(other)
        _guard_broadcast(self.lo, b.lo, "mul")
        p = self.lo * b.lo
        lower = np.array(p, copy=True)
        upper = np.array(p, copy=True)
        for q in (self.lo * b.hi, self.hi * b.lo, self.hi * b.hi):
            np.minimum(lower, q, out=lower)
            np.maximum(upper, q, out=upper)
        return Interval(_down(lower), _up(upper))

    __rmul__ = __mul__

    def reciprocal(self) -> "Interval":
        if np.any((self.lo <= 0.0) & (self.hi >= 0.0)):
            raise ZeroDivisionError("interval divisor contains zero")
        values = np.stack([1.0 / self.lo, 1.0 / self.hi], axis=0)
        return Interval(_down(np.min(values, axis=0)), _up(np.max(values, axis=0)))

    def __truediv__(self, other: ArrayLike | "Interval") -> "Interval":
        return self * as_interval(other).reciprocal()

    def __rtruediv__(self, other: ArrayLike | "Interval") -> "Interval":
        return as_interval(other) * self.reciprocal()


def as_interval(value: ArrayLike | Interval) -> Interval:
    return value if isinstance(value, Interval) else Interval(value)


def hull(*values: ArrayLike | Interval) -> Interval:
    if not values:
        raise ValueError("hull needs at least one value")
    intervals = [as_interval(v) for v in values]
    return Interval(
        _down(np.minimum.reduce([v.lo for v in intervals])),
        _up(np.maximum.reduce([v.hi for v in intervals])),
    )


def intersection(a: ArrayLike | Interval, b: ArrayLike | Interval) -> Interval:
    x, y = as_interval(a), as_interval(b)
    lo = np.maximum(x.lo, y.lo)
    hi = np.minimum(x.hi, y.hi)
    if np.any(lo > hi):
        raise ValueError("empty interval intersection")
    return Interval(lo, hi)


def inflate(x: ArrayLike | Interval, relative: float = 0.0, absolute: float = 0.0) -> Interval:
    iv = as_interval(x)
    if relative < 0.0 or absolute < 0.0:
        raise ValueError("inflation amounts must be nonnegative")
    pad = absolute + relative * np.maximum(np.abs(iv.lo), np.abs(iv.hi))
    return Interval(_down(iv.lo - pad), _up(iv.hi + pad))


def exp(x: ArrayLike | Interval) -> Interval:
    iv = as_interval(x)
    return Interval(_down(np.exp(iv.lo)), _up(np.exp(iv.hi)))


def log(x: ArrayLike | Interval) -> Interval:
    iv = as_interval(x)
    if np.any(iv.lo <= 0.0):
        raise ValueError("log interval must be strictly positive")
    return Interval(_down(np.log(iv.lo)), _up(np.log(iv.hi)))


def sqrt(x: ArrayLike | Interval) -> Interval:
    iv = as_interval(x)
    if np.any(iv.lo < 0.0):
        raise ValueError("sqrt interval must be nonnegative")
    return Interval(_down(np.sqrt(iv.lo)), _up(np.sqrt(iv.hi)))


def pow_const(x: ArrayLike | Interval, exponent: float) -> Interval:
    iv = as_interval(x)
    p = float(exponent)
    if not np.isfinite(p):
        raise ValueError("exponent must be finite")
    if p == 0.0:
        return Interval(np.ones_like(iv.lo))
    if np.any(iv.lo < 0.0) and not p.is_integer():
        raise ValueError("fractional powers require a nonnegative interval")
    if p < 0.0 and np.any((iv.lo <= 0.0) & (iv.hi >= 0.0)):
        raise ZeroDivisionError("negative power interval contains zero")

    # Integer powers over sign-changing intervals need explicit extrema at zero.
    if p.is_integer():
        n = int(p)
        if n < 0:
            return pow_const(iv.reciprocal(), -n)
        a = iv.lo**n
        b = iv.hi**n
        if n % 2 == 0:
            lo = np.where((iv.lo <= 0.0) & (iv.hi >= 0.0), 0.0, np.minimum(a, b))
            hi = np.maximum(a, b)
        else:
            lo, hi = a, b
    else:
        a = iv.lo**p
        b = iv.hi**p
        lo, hi = (np.minimum(a, b), np.maximum(a, b))
    return Interval(_down(lo), _up(hi))


def minimum(a: ArrayLike | Interval, b: ArrayLike | Interval) -> Interval:
    x, y = as_interval(a), as_interval(b)
    return Interval(_down(np.minimum(x.lo, y.lo)), _up(np.minimum(x.hi, y.hi)))


def maximum(a: ArrayLike | Interval, b: ArrayLike | Interval) -> Interval:
    x, y = as_interval(a), as_interval(b)
    return Interval(_down(np.maximum(x.lo, y.lo)), _up(np.maximum(x.hi, y.hi)))


def sum_interval(x: ArrayLike | Interval, axis: int | tuple[int, ...] | None = None) -> Interval:
    iv = as_interval(x)
    lo = np.sum(iv.lo.astype(np.longdouble), axis=axis, dtype=np.longdouble)
    hi = np.sum(iv.hi.astype(np.longdouble), axis=axis, dtype=np.longdouble)
    # Convert only after the extended-precision accumulation, then step outward.
    return Interval(_down(np.asarray(lo, dtype=np.float64)), _up(np.asarray(hi, dtype=np.float64)))


__all__ = [
    "Interval",
    "as_interval",
    "exp",
    "hull",
    "inflate",
    "intersection",
    "log",
    "maximum",
    "minimum",
    "pow_const",
    "sqrt",
    "sum_interval",
]
