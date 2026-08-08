"""Certified Bernstein enclosures for SciPy piecewise cubics."""
from __future__ import annotations

import numpy as np


def _outward_pair(lo: float, hi: float) -> tuple[float, float]:
    return (float(np.nextafter(lo, -np.inf)), float(np.nextafter(hi, np.inf)))


def cubic_power_range(coefficients, lower: float, upper: float) -> tuple[float, float]:
    """Enclose ``c0*x^3+c1*x^2+c2*x+c3`` over ``[lower,upper]``.

    The power polynomial is mapped to the unit interval and converted exactly
    (up to outward-rounded binary64 arithmetic) to cubic Bernstein form.  A
    Bernstein polynomial lies in the convex hull of its control coefficients.
    """

    c = np.asarray(coefficients, dtype=np.float64)
    if c.shape != (4,):
        raise ValueError("cubic coefficients must have shape (4,)")
    l, u = float(lower), float(upper)
    if not np.isfinite(l + u) or l > u:
        raise ValueError("invalid finite interval")
    if l == u:
        value = ((c[0] * l + c[1]) * l + c[2]) * l + c[3]
        return _outward_pair(float(value), float(value))

    w = u - l
    # p(l+w t) = A t^3 + B t^2 + C t + D.
    A = c[0] * w**3
    B = (3.0 * c[0] * l + c[1]) * w**2
    C = (3.0 * c[0] * l**2 + 2.0 * c[1] * l + c[2]) * w
    D = ((c[0] * l + c[1]) * l + c[2]) * l + c[3]
    bernstein = np.asarray(
        [D, D + C / 3.0, D + 2.0 * C / 3.0 + B / 3.0, D + C + B + A],
        dtype=np.float64,
    )
    return _outward_pair(float(np.min(bernstein)), float(np.max(bernstein)))


def ppoly_range(ppoly, lower: float, upper: float) -> tuple[np.ndarray | float, np.ndarray | float]:
    """Enclose a SciPy ``PPoly``/``PchipInterpolator`` on a closed interval.

    SciPy stores each polynomial in powers of ``x-x_i``.  We split at every
    breakpoint, call :func:`cubic_power_range` in local coordinates, and take
    the componentwise hull.  Vector-valued interpolants are supported.
    """

    l, u = float(lower), float(upper)
    if not np.isfinite(l + u) or l > u:
        raise ValueError("invalid finite interval")
    breaks = np.asarray(ppoly.x, dtype=np.float64)
    if l < breaks[0] or u > breaks[-1]:
        raise ValueError("requested interval lies outside PPoly support")

    # Include only segments touching [l,u].  At the right endpoint select the
    # preceding segment, matching SciPy's continuous polynomial evaluation.
    segs = []
    for i in range(len(breaks) - 1):
        a, b = breaks[i], breaks[i + 1]
        left, right = max(l, a), min(u, b)
        if left <= right and not (right == a and i > 0 and l == u):
            segs.append((i, left - a, right - a))
    if not segs:
        raise ValueError("no PPoly segment intersects the interval")

    c = np.asarray(ppoly.c, dtype=np.float64)
    if c.shape[0] > 4:
        raise ValueError("only polynomial degree <= 3 is supported")
    if c.shape[0] < 4:
        pad = [(4 - c.shape[0], 0)] + [(0, 0)] * (c.ndim - 1)
        c = np.pad(c, pad)

    lows = []
    highs = []
    for i, local_l, local_u in segs:
        coeff = c[:, i]
        if coeff.ndim == 1:
            lo, hi = cubic_power_range(coeff, local_l, local_u)
        else:
            flat = coeff.reshape(4, -1)
            pairs = [cubic_power_range(flat[:, j], local_l, local_u) for j in range(flat.shape[1])]
            lo = np.asarray([p[0] for p in pairs]).reshape(coeff.shape[1:])
            hi = np.asarray([p[1] for p in pairs]).reshape(coeff.shape[1:])
        lows.append(lo)
        highs.append(hi)

    lo = np.minimum.reduce(lows)
    hi = np.maximum.reduce(highs)
    lo = np.nextafter(lo, -np.inf)
    hi = np.nextafter(hi, np.inf)
    if np.ndim(lo) == 0:
        return float(lo), float(hi)
    return lo, hi


__all__ = ["cubic_power_range", "ppoly_range"]
