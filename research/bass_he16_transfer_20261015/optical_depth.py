"""Research-only Thomson optical-depth adapter; proper time s, nH cm^-3."""
import numpy as np
C_M_S = 299792458.0
SIGMA_T_M2 = 6.6524587321e-29

def electron_density_cm3(n_h_cm3, x_hii, x_heii, x_heiii, he_to_h):
    n, x, y, z = np.broadcast_arrays(n_h_cm3, x_hii, x_heii, x_heiii)
    h = float(he_to_h)
    if not np.isfinite(h) or h < 0 or not all(np.all(np.isfinite(a)) for a in (n, x, y, z)):
        raise ValueError("Nonfinite input or negative helium ratio")
    if np.any(n < 0) or np.any((x < 0) | (x > 1)) or np.any(y < 0) or np.any(z < 0) or np.any(y + z > 1):
        raise ValueError("Densities and fractions must lie in the physical simplex")
    return n * (x + h * (y + 2*z))

def cumulative_tau_trapezoid(t_s, n_h_cm3, x_hii, x_heii, x_heiii, he_to_h):
    """Composite trapezoid, not a rigorous error enclosure."""
    t = np.asarray(t_s, dtype=np.float64)
    if t.ndim != 1 or len(t) < 2 or not np.all(np.isfinite(t)) or np.any(np.diff(t) <= 0):
        raise ValueError("Proper times must be finite and strictly increasing")
    ne = np.asarray(electron_density_cm3(n_h_cm3, x_hii, x_heii, x_heiii, he_to_h), dtype=np.float64)
    if ne.shape != t.shape:
        raise ValueError("Species arrays must provide one value per time")
    rate = SIGMA_T_M2 * C_M_S * 1e6 * ne
    return np.r_[0.0, np.cumsum(np.diff(t) * 0.5 * (rate[:-1] + rate[1:]))]

def cumulative_tau_bounds(t_s, electron_lower_cm3, electron_upper_cm3):
    """Assumes lower/upper ne bounds hold over each WHOLE cell.
    Binary64 sums are NOT outward-rounded certified intervals.
    """
    t = np.asarray(t_s, dtype=np.float64)
    lo, hi = map(lambda a: np.asarray(a, dtype=np.float64), (electron_lower_cm3, electron_upper_cm3))
    if t.ndim != 1 or len(t) < 2 or not np.all(np.isfinite(t)) or np.any(np.diff(t) <= 0):
        raise ValueError("Invalid proper-time grid")
    if lo.shape != (len(t)-1,) or hi.shape != lo.shape or np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)) or np.any(lo < 0) or np.any(hi < lo):
        raise ValueError("Invalid cell-wise electron enclosures")
    fac = SIGMA_T_M2 * C_M_S * 1e6
    widths = np.diff(t)
    return np.r_[0., np.cumsum(fac*widths*lo)], np.r_[0., np.cumsum(fac*widths*hi)]
