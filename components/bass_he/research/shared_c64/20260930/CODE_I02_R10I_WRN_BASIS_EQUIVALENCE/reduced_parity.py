"""Independent CPC Eq.(47) parity reduction in the molecular-axis basis.

No author FORTRAN is imported. The even sector has m=0,...,l and reproduces
DERIVS' coefficient pattern after an explicit x-basis gauge. Straight-line
integration uses an exact angular interaction-picture transformation to remove
the small-rho connection peak. Coulomb uses the finite eccentric anomaly.
"""
from __future__ import annotations
from functools import lru_cache
import math
import numpy as np


def _coupling(l, start):
    m = np.arange(start, l + 1, dtype=float)
    k = np.zeros((len(m), len(m)), dtype=float)
    for j, mj in enumerate(m[:-1]):
        c = math.sqrt((l - mj) * (l + mj + 1)) / 2
        if start == 0 and j == 0:
            c *= math.sqrt(2)
        k[j, j + 1] = k[j + 1, j] = c
    return m * m, k


def reduced_blocks(l, diagonal):
    if type(l) is not int or l < 1 or not math.isfinite(float(diagonal)):
        raise ValueError('finite diagonal and integer l>=1 required')
    ed, ek = _coupling(l, 0)
    od, ok = _coupling(l, 1)
    return np.diag(diagonal * ed) - ek, np.diag(diagonal * od) - ok


def collapsed_from_parity(even_u, odd_u):
    e = np.asarray(even_u, complex)
    o = np.asarray(odd_u, complex)
    if e.ndim != 2 or e.shape[0] != e.shape[1] or o.shape != (len(e)-1, len(e)-1):
        raise ValueError('even/odd parity shapes')
    l = len(e)-1
    p = np.zeros((l+1, l+1), float)
    p[0, 0] = abs(e[0, 0])**2
    p[1:, 0] = abs(e[1:, 0])**2
    p[0, 1:] = abs(e[0, 1:])**2 / 2
    p[1:, 1:] = (abs(e[1:, 1:])**2 + abs(o)**2) / 2
    return p


def _velocity(E):
    return np.sqrt(2 * E / (27.07 * 1.836153))


def _parameters(N, l, energies, rhos, trajectory, cutoff, steps):
    if type(N) is not int or type(l) is not int or not 1 <= l < N:
        raise ValueError('integer 1<=l<N required')
    if type(steps) is not int or steps < 4:
        raise ValueError('integer steps>=4 required')
    if trajectory not in ('STRAIGHT', 'COULOMB') or cutoff not in ('CPC', 'AUTHOR'):
        raise ValueError('trajectory/cutoff policy')
    E, r = np.broadcast_arrays(np.asarray(energies, float), np.asarray(rhos, float))
    E, r = E.ravel(), r.ravel()
    if not len(r) or np.any(~np.isfinite(E)) or np.any(~np.isfinite(r)) or np.any(E <= 0) or np.any(r <= 0):
        raise ValueError('finite energy>0 and rho>0 required')
    cut = ((l + .5)**2 - (.5 if cutoff == 'CPC' else 0)) / 3
    v = _velocity(E)
    eps = 6 * 1 * 2 * (1 + 2)**2 / (N**3 * l * (l + 1) * (2*l - 1) * (2*l + 1) * (2*l + 3))
    a = 2 / (.8 * 1836.153 * v*v)
    b = np.hypot(a, r)
    active = r < cut if trajectory == 'STRAIGHT' else a + b < cut
    return E, r, v, eps, cut, a, b, active


@lru_cache(maxsize=4)
def _basis(l, start):
    diag, coupling = _coupling(l, start)
    eig, vec = np.linalg.eigh(coupling)
    for arr in (diag, coupling, eig, vec): arr.flags.writeable = False
    return diag, coupling, eig, vec


def _magnus(H, count, steps):
    dim = H(0).shape[-1]
    W = np.broadcast_to(np.eye(dim, dtype=complex), (count, dim, dim)).copy()
    h = 2 / steps
    shift = h / (2 * math.sqrt(3))
    for k in range(steps):
        mid = -1 + (k + .5) * h
        H1, H2 = H(mid - shift), H(mid + shift)
        K = .5*h*(H1+H2) + 1j*math.sqrt(3)*h*h/12*(H1@H2-H2@H1)
        eig, vec = np.linalg.eigh(K)
        W = ((vec*np.exp(-1j*eig)[:, None, :]) @ vec.conj().swapaxes(-1, -2)) @ W
    return W


def _straight_sector(l, start, r, v, eps, cut, steps):
    diag, coupling, eig, vec = _basis(l, start)
    xmax = np.sqrt(cut*cut - r*r)
    D = np.diag(diag)
    def G(theta):
        phases = np.exp(1j * theta[:, None] * eig[None, :])
        return (vec[None] * phases[:, None, :]) @ vec.T
    def H(y):
        x = xmax*y
        theta = np.arctan2(x, r)
        g = G(theta)
        radius2 = r*r + x*x
        return (eps*xmax*radius2/v)[:, None, None] * (g.conj().swapaxes(-1, -2) @ D @ g)
    W = _magnus(H, len(r), steps)
    theta_bound = np.arctan2(xmax, r)
    return G(theta_bound) @ W @ G(-theta_bound).conj().swapaxes(-1, -2)


def _coulomb_sector(l, start, r, v, eps, cut, a, b, steps):
    diag, coupling, _, _ = _basis(l, start)
    bound = np.arccosh((cut-a)/b)
    D = np.diag(diag)
    def H(y):
        radius = a + b*np.cosh(bound*y)
        alpha = bound*eps*radius**3/v
        beta = bound*r/radius
        return alpha[:, None, None]*D - beta[:, None, None]*coupling
    return _magnus(H, len(r), steps)


def reduced_rotation_batch(N, l, energies, rhos, *, trajectory, cutoff, steps):
    E, r, v, eps, cut, a, b, active = _parameters(N, l, energies, rhos, trajectory, cutoff, steps)
    even = np.broadcast_to(np.eye(l+1, dtype=complex), (len(r), l+1, l+1)).copy()
    odd = np.broadcast_to(np.eye(l, dtype=complex), (len(r), l, l)).copy()
    ix = np.flatnonzero(active)
    if len(ix):
        sector = _straight_sector if trajectory == 'STRAIGHT' else _coulomb_sector
        args = (r[ix], v[ix], eps, cut, steps) if trajectory == 'STRAIGHT' else (r[ix], v[ix], eps, cut, a[ix], b[ix], steps)
        even[ix] = sector(l, 0, *args)
        odd[ix] = sector(l, 1, *args)
    p = abs(even)**2
    pc = np.array([collapsed_from_parity(e, o) for e, o in zip(even, odd)])
    ue = float(np.max(abs(even.conj().swapaxes(-1, -2)@even - np.eye(l+1))))
    uo = float(np.max(abs(odd.conj().swapaxes(-1, -2)@odd - np.eye(l))))
    return {'P': p, 'P_collapsed': pc, 'U_even': even, 'U_odd': odd, 'entered': active,
            'unitarity_defect': max(ue, uo), 'stochasticity_defect': float(np.max(abs(p.sum(1)-1))),
            'trajectory': trajectory, 'cutoff': cutoff, 'steps': steps}


def reduced_dop853(N, l, energy, rho, *, trajectory, cutoff):
    """Separate direct-amplitude DOP853; no Magnus interaction picture."""
    from scipy.integrate import solve_ivp
    E, r, v, eps, cut, a, b, active = _parameters(N, l, [energy], [rho], trajectory, cutoff, 4)
    if not active[0]: return {'P': np.eye(l+1), 'U_even': np.eye(l+1, dtype=complex), 'unitarity_defect': 0., 'nfev': 0}
    diag, coupling, _, _ = _basis(l, 0)
    D = np.diag(diag)
    if trajectory == 'STRAIGHT':
        xmax = math.sqrt(cut*cut-rho*rho)
        bound = math.atan2(xmax, rho)
        def h(s):
            radius = rho / math.cos(s)
            return eps*rho*radius**4/(v[0]*rho**2)*D - coupling
    else:
        bound = math.acosh((cut-a[0])/b[0])
        def h(s):
            radius = a[0]+b[0]*math.cosh(s)
            return eps*radius**3/v[0]*D - rho/radius*coupling
    dim = l+1
    def rhs(s, y): return (-1j*h(s)@y.reshape(dim, dim)).ravel()
    sol = solve_ivp(rhs, (-bound, bound), np.eye(dim, dtype=complex).ravel(),
                    method='DOP853', rtol=1e-12, atol=1e-14)
    if not sol.success: raise ArithmeticError('REDUCED_DOP853_FAILURE: '+sol.message)
    u = sol.y[:, -1].reshape(dim, dim)
    return {'P': abs(u)**2, 'U_even': u,
            'unitarity_defect': float(np.max(abs(u.conj().T@u - np.eye(dim)))), 'nfev': sol.nfev}
