"""Auxiliary real-arithmetic transport formulas, evaluated here in binary64.

The functions return ordinary numerical matrices, never interval certificates.
"""
import math
import numpy as np


def energy_nodes():
    edges = [10., 13.598434599702, 13.6, 13.7, 20.]
    return np.array([edges[k] + (edges[k+1]-edges[k])*j/8
                     for k in range(4) for j in range(8)] + [20.])


def _grid(E):
    E = np.asarray(E, dtype=float)
    if E.ndim != 1 or len(E) < 2 or not np.isfinite(E).all() or E[0] <= 0 or np.any(np.diff(E) <= 0):
        raise ValueError('positive strictly increasing grid required')
    return E


def number_generator(E):
    E = _grid(E); n = len(E)-1
    B = np.zeros((n+1, n+1))
    for i, lam in enumerate(E[1:]/np.diff(E)):
        B[i, i] = -lam
        B[i-1 if i else n, i] = lam
    return B


def energy_generator(E):
    E = _grid(E); C = number_generator(E)
    C[-1, 0] *= E[0]
    C[-1, -1] = -1.
    return C


def original_hat_map(E, r):
    """Full nodal transport plus guardN/guardU, for every 0<r<=1.

    Number and energy are independent linear guard coordinates; physical
    states additionally satisfy 0<=guardU<=E0*guardN.
    """
    E = _grid(E)
    if not math.isfinite(r) or not 0 < r <= 1:
        raise ValueError('redshift ratio must be in (0,1]')
    n = len(E); M = np.zeros((n+2, n+2))
    M[n, n] = 1.; M[n+1, n+1] = r
    for j, e in enumerate(E*r):
        if e < E[0]:
            M[n, j] = 1.; M[n+1, j] = e
        elif e >= E[-1]:
            M[n-1, j] = 1.
        else:
            k = int(np.searchsorted(E, e, side='right')-1)
            M[k, j] = (E[k+1]-e)/(E[k+1]-E[k])
            M[k+1, j] = (e-E[k])/(E[k+1]-E[k])
    return M


def projection(E):
    E = _grid(E); n = len(E)
    P = np.eye(n+2); P[0, 0] = 0.; P[n, 0] = 1.; P[n+1, 0] = E[0]
    return P


def projected_number_map(E, r):
    E = _grid(E); n = len(E)
    A = projection(E) @ original_hat_map(E, r)
    keep = list(range(1, n)) + [n]
    return A[np.ix_(keep, keep)]


def projected_energy_map(E, r):
    E = _grid(E); n = len(E)
    A = projection(E) @ original_hat_map(E, r)
    keep = list(range(1, n)) + [n+1]
    return A[np.ix_(keep, keep)]


def cfl_linear_map(E, r, energy=False):
    """Linear CFL expression: explicitly unavailable outside its domain."""
    E = _grid(E)
    if not math.isfinite(r) or not 0 < r <= 1:
        raise ValueError('redshift ratio must be in (0,1]')
    if (1-r)*max(E[1:]/np.diff(E)) > 1:
        raise ValueError('non-CFL: use the original hat map')
    A = energy_generator(E) if energy else number_generator(E)
    return np.eye(len(E)) + (1-r)*A


def local_defect_bound(L, s):
    if not math.isfinite(L) or not math.isfinite(s) or L < 0 or s < 0:
        raise ValueError('finite nonnegative norm and characteristic step required')
    return L*(s+math.expm1(-s)) + .5*L*L*s*s


def column_norm(A, weights=None):
    A = np.asarray(A)
    if weights is None:
        return float(np.max(np.sum(abs(A), axis=0)))
    w = np.asarray(weights)
    return float(np.max(np.sum(abs(A)*w[:, None]/w[None, :], axis=0)))
