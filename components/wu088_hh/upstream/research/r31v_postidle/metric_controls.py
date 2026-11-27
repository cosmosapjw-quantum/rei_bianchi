"""Moving-metric diagnostics. No symmetrization/repair of authoritative input.

Hermiticity is checked before triangular solves. Numerical checks within the
reported tolerance are not an interval-arithmetic proof for uncertain data.
"""
import math
import numpy as np
from scipy.linalg import solve_triangular


def whiten(overlap, residual):
    o = np.asarray(overlap, dtype=np.complex128)
    r = np.asarray(residual, dtype=np.complex128)
    if o.ndim != 2 or o.shape[0] != o.shape[1] or not o.size or r.shape != o.shape:
        raise ValueError('same nonempty square shape required')
    if not np.isfinite(o).all() or not np.isfinite(r).all():
        raise ValueError('nonfinite matrix')
    for a in (o, r):
        gap = np.linalg.norm(a-a.conj().T, 2)
        if gap > 1e-12*max(1., np.linalg.norm(a, 2)):
            raise ValueError('Hermiticity prerequisite failed')
    try:
        c = np.linalg.cholesky(o).conj().T
    except np.linalg.LinAlgError as e:
        raise ValueError('positive-definite overlap required') from e
    # W=C^{-1}; congruence W† R W, not W R W†.
    w = solve_triangular(c, np.eye(len(c)), lower=False)
    return w.conj().T@r@w


def diagnose(overlap, residual):
    w = whiten(overlap, residual)
    # SVD is used rather than silently treating a nearly Hermitian input as exact.
    eta = float(np.linalg.norm(w, 2))
    return {'eta': eta, 'minimum_connection_correction': .5*eta,
            'whitened_hermiticity_gap': float(np.linalg.norm(w-w.conj().T, 2)),
            'units': 'inverse input time',
            'scope': 'instantaneous represented-matrix diagnostic, not trajectory error'}


def uncertainty_envelope(eta, eps_overlap, eps_residual):
    """Conditional bounds, only when both whitened perturbation bounds hold.

    eps_overlap is dimensionless; eta and eps_residual have units 1/time.
    This function does not estimate these two error bounds from node differences.
    """
    if (any(not math.isfinite(x) for x in (eta, eps_overlap, eps_residual))
        or eta < 0 or not 0 <= eps_overlap < 1 or eps_residual < 0):
        raise ValueError('finite eta>=0, 0<=eps_overlap<1, eps_residual>=0 required')
    return max(0., eta-eps_residual)/(1+eps_overlap), (eta+eps_residual)/(1-eps_overlap)
