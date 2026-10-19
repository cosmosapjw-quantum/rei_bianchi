"""Finite-time two-block comparison with constant forcing, including singular M.

If a,b,c and rho are certified tube bounds, the exact-arithmetic map defines
the conditional comparison enclosure. Returned float64 expm values also need
a rounding-error enclosure before they serve as rigorous radii. Sampled input
scales produce a sampled-coefficient diagnostic only; no status is promoted.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm


def propagate_comparison(a, b, c, rho, radius0, duration):
    """Solve u' = [[a,b],[c,0]]u + rho by a three-by-three augmented exponential.

    ``a`` may be negative; b,c,rho,radius0,duration must be nonnegative.
    Gas and optical-depth coordinates have the fixed norm/units supplied by
    the caller. Time-dependent changes of norm are not silently performed.
    """
    rho = np.asarray(rho, dtype=float)
    radius0 = np.asarray(radius0, dtype=float)
    if rho.shape != (2,) or radius0.shape != (2,):
        raise ValueError("two forcing components and two initial radii required")
    if not np.isfinite([a, b, c, duration]).all():
        raise ValueError("finite matrix coefficients and duration required")
    if min(b, c, duration) < 0 or not np.isfinite(rho).all() or not np.isfinite(radius0).all():
        raise ValueError("invalid comparison domain")
    if np.any(rho < 0) or np.any(radius0 < 0):
        raise ValueError("comparison forcing and radii must be nonnegative")
    augmented = np.array([[a, b, rho[0]], [c, 0., rho[1]], [0., 0., 0.]])
    exponential = expm(duration*augmented)
    homogeneous = exponential[:2, :2]@radius0
    forced = exponential[:2, 2]
    endpoint = homogeneous+forced
    if not np.isfinite(endpoint).all():
        raise OverflowError("nonfinite comparison result; no clipping")
    return {"endpoint": endpoint, "initial_contribution": homogeneous,
            "forcing_contribution": forced, "propagator": exponential[:2, :2]}
