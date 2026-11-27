from __future__ import annotations
import numpy as np

def integrate_probability_matrix(rho, probability_matrices):
    """Numerically implement paper Eq. (54).

        sigma(v) = 2*pi integral_0^infty P(rho,v) rho d rho

    The caller controls the rho truncation/grid. Trapezoidal integration is
    used deliberately here; convergence is a separate scientific test.
    """
    rho = np.asarray(rho, dtype=float)
    P = np.asarray(probability_matrices, dtype=float)
    if rho.ndim != 1 or len(rho) < 2:
        raise ValueError("rho must be a 1D grid with >=2 points")
    if P.ndim != 3 or P.shape[0] != len(rho) or P.shape[1] != P.shape[2]:
        raise ValueError("P must have shape (nrho,jmax,jmax)")
    if np.any(np.diff(rho) <= 0) or rho[0] < 0:
        raise ValueError("rho must be strictly increasing and non-negative")
    weighted = P * rho[:,None,None]
    return 2.0*np.pi*np.trapezoid(weighted, rho, axis=0)

def projectile_velocity_au(E_keV_per_amu: float) -> float:
    """Paper input/output convention for velocity used by CR_SECTION."""
    if E_keV_per_amu <= 0:
        raise ValueError("energy must be positive")
    return (2.0*E_keV_per_amu/(27.07*1.836153))**0.5
