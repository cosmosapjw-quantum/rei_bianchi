"""Independent charge-center spherical hp-FEM reference (research prototype).

Computational units a_A=E_A=hbar=m_e=1.  Nuclear repulsion is omitted.
psi_0=G(r,eta)/sqrt(2*pi), psi_1=G(r,eta)*cos(phi)/sqrt(pi).
G=sum_l u_l(r) A_lm(eta)/r; A_lm has no Condon--Shortley sign.
No Coulomb softening, interpolation of external data, or production claims.
"""
from dataclasses import dataclass
from functools import lru_cache
import math
import time

import numpy as np
from numpy.polynomial import Polynomial, Legendre
from numpy.polynomial.legendre import leggauss
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.special import lpmv, gammaln


def _integer(value, name, lower):
    if isinstance(value, bool) or int(value) != value or value < lower:
        raise ValueError(f"{name} must be integer >= {lower}")
    return int(value)


def angular(l, m, eta, derivative=False):
    """Normalized associated Legendre function, positive for l=m.

    Derivative is evaluated only for |eta|<1 (m=1 eta derivative is
    coordinate-singular on the axis).  Values themselves allow both axes.
    """
    eta = np.asarray(eta, dtype=float)
    if m not in (0, 1) or l < m or np.any(~np.isfinite(eta)):
        raise ValueError("requires l>=m and m in {0,1}, finite eta")
    if np.any(np.abs(eta) > 1) or (derivative and np.any(np.abs(eta) >= 1)):
        raise ValueError("eta outside angular domain")
    norm = np.exp(0.5*(np.log((2*l+1)/2)+gammaln(l-m+1)-gammaln(l+m+1)))
    p = lpmv(m, l, eta)
    if not derivative:
        return (-1)**m * norm * p
    prev = lpmv(m, l-1, eta) if l > m else np.zeros_like(eta)
    dp = (l*eta*p-(l+m)*prev)/(eta*eta-1)
    return (-1)**m * norm * dp


@lru_cache(maxsize=12)
def _polynomials(degree):
    nodes = np.r_[-1., Legendre.basis(degree).deriv().roots(), 1.]
    polys = []
    for j, node in enumerate(nodes):
        other = np.delete(nodes, j)
        polys.append(Polynomial.fromroots(other)/np.prod(node-other))
    return nodes, tuple(polys)


def radial_mesh(R, ZA, ZB, rmax, elements):
    """Deterministic exponential mesh, augmented by nuclear radii.

    Nuclear-radius element boundaries remove all radial multipole kinks.
    Angular l truncation still limits resolution of off-center cusps.
    """
    z = np.array([-ZB*R/(ZA+ZB), ZA*R/(ZA+ZB)])
    if rmax <= max(abs(z)):
        raise ValueError("rmax must contain both point nuclei")
    alpha = 4.0
    base = rmax*np.expm1(alpha*np.linspace(0, 1, elements+1))/np.expm1(alpha)
    return np.unique(np.r_[base, np.abs(z)])


@dataclass
class PartialWaveState:
    R: float
    ZA: float
    ZB: float
    m: int
    ls: np.ndarray
    boundaries: np.ndarray
    degree: int
    coefficients: np.ndarray
    energy: float
    residual: float
    mass_norm: float
    phase_probe: float
    metadata: dict

    def radial(self, r, derivative=False):
        """u_l(r) or u'_l(r), with output shape (number_l, *r.shape)."""
        r = np.asarray(r, dtype=float)
        if np.any(~np.isfinite(r)) or np.any(r < 0) or np.any(r > self.boundaries[-1]):
            raise ValueError("r outside finite FEM domain")
        idx = np.searchsorted(self.boundaries, r, side="right")-1
        idx = np.clip(idx, 0, len(self.boundaries)-2)
        lo, hi = self.boundaries[idx], self.boundaries[idx+1]
        q = 2*(r-lo)/(hi-lo)-1
        _, polys = _polynomials(self.degree)
        out = np.zeros((len(self.ls),)+r.shape)
        for k, poly in enumerate(polys):
            val = poly.deriv()(q)*2/(hi-lo) if derivative else poly(q)
            out += self.coefficients[:, idx*self.degree+k]*val
        return out

    def evaluate(self, r, eta):
        """Return (G, dG/dr, dG/deta), at broadcast arrays r>0, |eta|<1.

        Azimuthal normalization is NOT included; see module convention.
        """
        r, eta = np.broadcast_arrays(np.asarray(r, float), np.asarray(eta, float))
        if np.any(r <= 0):
            raise ValueError("evaluation requires r>0")
        u, du = self.radial(r), self.radial(r, derivative=True)
        a = np.stack([angular(int(l), self.m, eta) for l in self.ls])
        da = np.stack([angular(int(l), self.m, eta, True) for l in self.ls])
        return (np.sum(u*a, axis=0)/r,
                np.sum((du/r-u/r**2)*a, axis=0),
                np.sum(u*da, axis=0)/r)


def solve(R, ZA=1., ZB=2., m=0, lmax=12, rmax=20., elements=48,
          degree=4, quadrature=None, tol=1e-11, maxiter=2000):
    """Lowest eigenstate in one real m=0 or bright |m|=1 sector.

    Ritz residual is algebraic in the finite generalized matrix problem;
    it is NOT the infinite-space PDE residual or a coupling error bound.
    Default quadrature is overintegrated ordinary Gauss--Legendre, not DVR.
    """
    start = time.perf_counter()
    vals = np.asarray([R, ZA, ZB, rmax, tol], float)
    if np.any(~np.isfinite(vals)) or R < 0 or ZA <= 0 or ZB <= 0 or rmax <= 0 or not 0 < tol < 1:
        raise ValueError("invalid physical or solver parameter")
    if m not in (0, 1):
        raise ValueError("only m=0 and m=1 are implemented")
    lmax = _integer(lmax, "lmax", m)
    elements = _integer(elements, "elements", 4)
    degree = _integer(degree, "degree", 2)
    maxiter = _integer(maxiter, "maxiter", 1)
    quadrature = 2*degree+6 if quadrature is None else _integer(quadrature, "quadrature", degree+2)
    boundaries = radial_mesh(R, ZA, ZB, rmax, elements)
    ne = len(boundaries)-1
    nr = ne*degree-1  # endpoints removed, not penalized
    ls = np.arange(m, lmax+1)
    nl = len(ls)
    _, polys = _polynomials(degree)
    q, qw = leggauss(quadrature)
    B = np.stack([p(q) for p in polys], axis=1)
    dB = np.stack([p.deriv()(q) for p in polys], axis=1)
    z = np.array([-ZB*R/(ZA+ZB), ZA*R/(ZA+ZB)])
    # This many angular quadrature nodes exactly integrates polynomial
    # A_lm A_l'm P_L for m=0,1 and L<=2*lmax in exact arithmetic.
    eta, ew = leggauss(2*lmax+3)
    A = np.stack([angular(int(l), m, eta) for l in ls], axis=1)
    orders = np.arange(2*lmax+1)
    gaunt = np.stack([A.T @ ((ew*Legendre.basis(int(L))(eta))[:, None]*A)
                      for L in orders])
    # Exact triangle/parity zeros prevent cancellation noise in absent blocks.
    for il, l in enumerate(ls):
        for jl, lp in enumerate(ls):
            gaunt[(orders < abs(l-lp)) | (orders > l+lp) | ((orders+l+lp)%2 == 1), il, jl] = 0.
    rows, cols, hdata, mdata = [], [], [], []
    for e in range(ne):
        lo, hi = boundaries[e:e+2]
        jac = (hi-lo)/2
        r = lo+jac*(q+1)
        massloc = B.T @ ((qw*jac)[:, None]*B)
        kinloc = 0.5*dB.T @ ((qw/jac)[:, None]*dB)
        centloc = B.T @ ((qw*jac/(2*r*r))[:, None]*B)
        vl = np.zeros((quadrature, len(orders)))
        for charge, position in zip((ZA, ZB), z):
            radius = abs(position)
            if radius == 0:
                vl[:, 0] -= charge/r
            else:
                ratio = np.minimum(r, radius)/np.maximum(r, radius)
                vl -= (charge/np.maximum(r, radius))[:, None] * ratio[:, None]**orders * np.sign(position)**orders
        vll = np.einsum("qk,kij->qij", vl, gaunt, optimize=True)
        ids = np.arange(e*degree, e*degree+degree+1)-1
        valid = (ids >= 0) & (ids < nr)
        gi = ids[valid]
        for il, l in enumerate(ls):
            for jl in range(nl):
                block = B.T @ ((qw*jac*vll[:, il, jl])[:, None]*B)
                if il == jl:
                    block += kinloc+l*(l+1)*centloc
                sub = block[np.ix_(valid, valid)]
                rr, cc = np.meshgrid(il*nr+gi, jl*nr+gi, indexing="ij")
                rows.extend(rr.ravel()); cols.extend(cc.ravel()); hdata.extend(sub.ravel())
                if il == jl:
                    mdata.extend(massloc[np.ix_(valid, valid)].ravel())
                else:
                    mdata.extend(np.zeros(sub.size))
    shape = (nl*nr, nl*nr)
    H = sparse.coo_matrix((hdata, (rows, cols)), shape=shape).tocsr()
    M = sparse.coo_matrix((mdata, (rows, cols)), shape=shape).tocsr()
    H.eliminate_zeros(); M.eliminate_zeros()
    hskew = sparse.linalg.norm(H-H.T)/max(sparse.linalg.norm(H), 1.)
    if hskew > 1e-12:
        raise ArithmeticError("assembled Hamiltonian is not symmetric")
    # The Coulomb form lower bound is -(ZA+ZB)^2/2.  A lower shift selects
    # the lowest Ritz root without energy sorting across different R.
    shift = -0.5*(ZA+ZB)**2-1.
    v0 = np.cos(np.arange(shape[0], dtype=float)*0.271)+0.25
    eig, vec = eigsh(H, M=M, k=1, sigma=shift, which="LM", tol=tol,
                    maxiter=maxiter, v0=v0)
    c = vec[:, 0]
    c /= np.sqrt(c @ (M @ c))
    energy = float(eig[0])
    res = H@c-energy*(M@c)
    residual = float(np.linalg.norm(res)/(np.linalg.norm(H@c)+abs(energy)*np.linalg.norm(M@c)))
    coeff = np.zeros((nl, nr+2))
    coeff[:, 1:-1] = c.reshape(nl, nr)
    state = PartialWaveState(float(R), float(ZA), float(ZB), int(m), ls, boundaries,
                             degree, coeff, energy, residual, float(c@(M@c)), 0., {})
    # Ground in each meridional sector is strictly positive in the exact
    # problem.  Phase fixing does not certify finite-basis positivity.
    probes = state.evaluate(np.full(9, max(0.1, min(1., rmax/4))), np.linspace(-0.8, 0.8, 9))[0]
    phase = float(np.sum(probes))
    if phase < 0:
        state.coefficients *= -1
        phase *= -1
    state.phase_probe = phase
    state.metadata = {"representation": "charge-center spherical partial-wave hp-FEM",
                      "units": "a_A,E_A", "angular_lmax": lmax,
                      "radial_elements_actual": ne, "degree": degree,
                      "radial_quadrature": quadrature, "angular_quadrature": 2*lmax+3,
                      "matrix_dimension": shape[0], "hamiltonian_nnz": H.nnz,
                      "mass_nnz": M.nnz, "hamiltonian_relative_skew": float(hskew),
                      "rmax": float(rmax), "solver_tol": float(tol),
                      "shift": shift, "elapsed_seconds": time.perf_counter()-start,
                      "residual_scope": "finite-matrix algebraic only",
                      "coulomb_softening": False, "full_space_accuracy_certified": False}
    return state


def direct_angular_coupling(g, b, quadrature=None):
    """Return real L/(-i*hbar) about the common charge center.

    Independent angular-generator lane, with exactly integrated piecewise
    polynomial radial products.  No torque, energy gap, or force used.
    """
    if g.m != 0 or b.m != 1 or (g.R, g.ZA, g.ZB) != (b.R, b.ZA, b.ZB):
        raise ValueError("requires compatible m=0 and bright m=1 states")
    if g.boundaries[-1] != b.boundaries[-1]:
        raise ValueError("direct integration requires the same finite radial domain")
    n = max(g.degree, b.degree)+2 if quadrature is None else _integer(quadrature, "quadrature", max(g.degree, b.degree)+1)
    q, qw = leggauss(n)
    boundaries = np.unique(np.r_[g.boundaries, b.boundaries])
    total = 0.
    for lo, hi in zip(boundaries[:-1], boundaries[1:]):
        jac = (hi-lo)/2
        r = lo+jac*(q+1)
        ug, ub = g.radial(r), b.radial(r)
        for il, l in enumerate(g.ls):
            hit = np.flatnonzero(b.ls == l)
            if len(hit):
                total += np.sqrt(l*(l+1)/2)*np.dot(qw*jac, ug[il]*ub[hit[0]])
    return float(total)
