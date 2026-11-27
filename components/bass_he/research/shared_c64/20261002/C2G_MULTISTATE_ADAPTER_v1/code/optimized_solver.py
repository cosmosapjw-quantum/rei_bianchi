"""Accuracy-preserving HPC spherical hp-FEM fork (research prototype).

Computational units a_A=E_A=hbar=m_e=1.  Nuclear repulsion is omitted.
psi_0=G(r,eta)/sqrt(2*pi), psi_1=G(r,eta)*cos(phi)/sqrt(pi).
G=sum_l u_l(r) A_lm(eta)/r; A_lm has no Condon--Shortley sign.
No Coulomb softening, interpolation of external data, or production claims.
"""
from dataclasses import dataclass, replace
from functools import lru_cache
import math
import time
import hashlib
import numbers
from pathlib import Path

import numpy as np
from numpy.polynomial import Polynomial, Legendre
from numpy.polynomial.legendre import leggauss
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.special import lpmv, gammaln


def _source_files_identity():
    """Observed files; isolated runner additionally binds pre/post process bytes."""
    folder = Path(__file__).resolve().parent
    return {name: hashlib.sha256((folder/name).read_bytes()).hexdigest()
            for name in ("optimized_solver.py", "native_backend.py")}


def _integer(value, name, lower):
    if (isinstance(value, (bool, np.bool_)) or not isinstance(value, numbers.Real)
            or not np.isfinite(value) or int(value) != value or value < lower):
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


def nuclear_positions(R, ZA, ZB, center="B"):
    """Signed nuclear z positions in the selected numerical coordinates."""
    if center == "B":
        return np.array([-R, 0.])
    if center == "O":
        return np.array([-ZB*R/(ZA+ZB), ZA*R/(ZA+ZB)])
    raise ValueError("center must be 'O' or 'B'")


def radial_mesh(R, ZA, ZB, rmax, elements, center="B", boundaries=None):
    """Exponential mesh or a validated explicit partition.

    Explicit boundaries are retained exactly; appending outer cells therefore
    changes only the tail discretization. Nuclear radii must already be knots.
    """
    z = nuclear_positions(R, ZA, ZB, center)
    if rmax <= max(abs(z)):
        raise ValueError("rmax must contain both point nuclei")
    if boundaries is not None:
        mesh = np.array(boundaries, dtype=float, copy=True)
        if (mesh.ndim != 1 or len(mesh) < 3 or not np.all(np.isfinite(mesh))
                or mesh[0] != 0 or mesh[-1] != rmax or np.any(np.diff(mesh) <= 0)):
            raise ValueError("explicit boundaries must strictly increase from 0 to rmax")
        if any(not np.any(mesh == radius) for radius in np.abs(z)):
            raise ValueError("explicit boundaries must contain exact nuclear radii")
        return mesh
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


@lru_cache(maxsize=4)
def angular_table(m, lmax):
    """Read-only exact selection table; bounded 4-entry process-local cache."""
    ls = np.arange(m, lmax+1)
    eta, ew = leggauss(2*lmax+3)
    A = np.stack([angular(int(l), m, eta) for l in ls], axis=1)
    orders = np.arange(2*lmax+1)
    out = np.stack([A.T @ ((ew*Legendre.basis(int(L))(eta))[:, None]*A)
                    for L in orders])
    for il, l in enumerate(ls):
        for jl, lp in enumerate(ls):
            absent = (orders < abs(l-lp)) | (orders > l+lp) | ((orders+l+lp)%2 == 1)
            out[absent, il, jl] = 0.
    out.flags.writeable = False
    return out


def solve_many(R, ZA=1., ZB=2., m=0, lmax=12, rmax=20., elements=48,
          degree=4, quadrature=None, tol=1e-11, maxiter=2000,
          center="B", boundaries=None, nroots=1, backend="native", matrix_observer=None):
    """All requested sorted Ritz states from one assembly and one eigensolve.

    Ritz residual is algebraic in the finite generalized matrix problem;
    it is NOT the infinite-space PDE residual or a coupling error bound.
    Default quadrature is overintegrated ordinary Gauss--Legendre, not DVR.
    """
    start = time.perf_counter()
    source_before = _source_files_identity()
    if backend not in ("native", "numpy"):
        raise ValueError("backend must be native or numpy")
    from native_backend import prepare_element_kernel, library_identity
    vals = np.asarray([R, ZA, ZB, rmax, tol], float)
    if np.any(~np.isfinite(vals)) or R < 0 or ZA < 0 or ZB < 0 or ZA+ZB <= 0 or rmax <= 0 or not 0 < tol < 1:
        raise ValueError("invalid physical or solver parameter")
    m = _integer(m, "m", 0)
    if m not in (0, 1):
        raise ValueError("only m=0 and m=1 are implemented")
    lmax = _integer(lmax, "lmax", m)
    elements = _integer(elements, "elements", 4)
    degree = _integer(degree, "degree", 2)
    maxiter = _integer(maxiter, "maxiter", 1)
    quadrature = 2*degree+6 if quadrature is None else _integer(quadrature, "quadrature", degree+2)
    nroots = _integer(nroots, "nroots", 1)
    boundaries = radial_mesh(R, ZA, ZB, rmax, elements, center, boundaries)
    ne = len(boundaries)-1
    nr = ne*degree-1  # endpoints removed, not penalized
    ls = np.arange(m, lmax+1)
    nl = len(ls)
    if nroots >= nl*nr:
        raise ValueError("nroots must be smaller than finite matrix dimension")
    _, polys = _polynomials(degree)
    q, qw = leggauss(quadrature)
    B = np.stack([p(q) for p in polys], axis=1)
    dB = np.stack([p.deriv()(q) for p in polys], axis=1)
    z = nuclear_positions(R, ZA, ZB, center)
    # Angular tables depend only on sector/lmax, not R or radial partition.
    gaunt = angular_table(m, lmax)
    orders = np.arange(2*lmax+1)
    native_kernel = prepare_element_kernel(B, gaunt, ls) if backend == "native" else None
    tabulation_done = time.perf_counter()
    # Preallocate int32 COO when safe; release COO work before eigensolve.
    active_counts = np.full(ne, degree+1, dtype=np.int64)
    active_counts[0] -= 1; active_counts[-1] -= 1
    nnz_coo = int(np.sum((nl*active_counts)**2))
    index_dtype = np.int32 if max(nl*nr, nnz_coo) < 2**31 else np.int64
    rows = np.empty(nnz_coo, dtype=index_dtype)
    cols = np.empty(nnz_coo, dtype=index_dtype)
    hdata = np.empty(nnz_coo, dtype=np.float64)
    mass_count = int(np.sum(active_counts**2))
    mr = np.empty(mass_count, dtype=index_dtype)
    mc = np.empty(mass_count, dtype=index_dtype)
    md = np.empty(mass_count, dtype=np.float64)
    hp = mp = 0
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
        if backend == "native":
            blocks = native_kernel.blocks(vl, qw*jac, kinloc, centloc)
        else:
            vll = np.einsum("qk,kij->qij", vl, gaunt, optimize=True)
            blocks = np.einsum("qa,qij,qb,q->iajb", B, vll, B, qw*jac, optimize=True)
            for il, l in enumerate(ls):
                blocks[il, :, il, :] += kinloc+l*(l+1)*centloc
            del vll
        ids = np.arange(e*degree, e*degree+degree+1)-1
        valid = (ids >= 0) & (ids < nr)
        gi = ids[valid]
        activeids = (np.arange(nl)[:, None]*nr+gi[None, :]).ravel()
        flatvalid = np.tile(valid, nl)
        block = blocks.reshape(nl*(degree+1), nl*(degree+1))[np.ix_(flatvalid, flatvalid)]
        nactive = len(activeids); count = nactive*nactive
        rows[hp:hp+count] = np.repeat(activeids, nactive)
        cols[hp:hp+count] = np.tile(activeids, nactive)
        hdata[hp:hp+count] = block.ravel()
        hp += count
        count = len(gi)**2
        mr[mp:mp+count] = np.repeat(gi, len(gi))
        mc[mp:mp+count] = np.tile(gi, len(gi))
        md[mp:mp+count] = massloc[np.ix_(valid, valid)].ravel()
        mp += count
    assert hp == nnz_coo and mp == mass_count
    shape = (nl*nr, nl*nr)
    H = sparse.coo_matrix((hdata, (rows, cols)), shape=shape).tocsr()
    Mrad = sparse.coo_matrix((md, (mr, mc)), shape=(nr, nr)).tocsr()
    M = sparse.kron(sparse.eye(nl, format="csr"), Mrad, format="csr")
    del rows, cols, hdata, mr, mc, md, blocks, block, Mrad
    H.eliminate_zeros(); M.eliminate_zeros()
    hskew = sparse.linalg.norm(H-H.T)/max(sparse.linalg.norm(H), 1.)
    if hskew > 1e-12:
        raise ArithmeticError("assembled Hamiltonian is not symmetric")
    if matrix_observer is not None:
        matrix_observer(H, M)
    assembly_done = time.perf_counter()
    # The Coulomb form lower bound is -(ZA+ZB)^2/2.  A lower shift selects
    # the lowest Ritz root without energy sorting across different R.
    shift = -0.5*(ZA+ZB)**2-1.
    v0 = np.cos(np.arange(shape[0], dtype=float)*0.271)+0.25
    eig, vec = eigsh(H, M=M, k=nroots, sigma=shift, which="LM", tol=tol,
                    maxiter=maxiter, v0=v0)
    eigensolve_done = time.perf_counter()
    result = _finish_eigenpairs(
        H, M, eig, vec, R=float(R), ZA=float(ZA), ZB=float(ZB), m=int(m),
        ls=ls, boundaries=boundaries, degree=degree, nroots=nroots,
        metadata={
            "representation": "movable-center spherical partial-wave hp-FEM",
            "origin_center": center, "nuclear_positions": z.tolist(),
            "origin_shift_B_to_O": float(ZA*R/(ZA+ZB)),
            "origin_shift_center_to_O": float(ZA*R/(ZA+ZB)) if center == "B" else 0.,
            "gap_scope": "finite-domain finite-basis Ritz roots; not continuum certificate",
            "explicit_boundaries": boundaries.tolist(),
            "units": "a_A,E_A", "energy_convention": "electronic Coulomb Hamiltonian; nuclear repulsion omitted; ionization zero",
            "angular_lmax": lmax, "radial_elements_actual": ne, "degree": degree,
            "radial_quadrature": quadrature, "angular_quadrature": 2*lmax+3,
            "matrix_dimension": shape[0], "hamiltonian_nnz": H.nnz,
            "mass_nnz": M.nnz, "hamiltonian_relative_skew": float(hskew),
            "rmax": float(rmax), "solver_tol": float(tol), "shift": shift,
            "elapsed_seconds": time.perf_counter()-start,
            "residual_scope": "finite-matrix algebraic only",
            "coulomb_softening": False, "full_space_accuracy_certified": False,
            "operator_scope": "real spinless static axial electronic Hamiltonian",
            "dynamic_sector_decoupling_claim": False,
            "backend": backend, "native_library": library_identity() if backend == "native" else None,
            "index_dtype": np.dtype(index_dtype).name,
            "stage_seconds": {"tabulation": tabulation_done-start,
                              "assembly": assembly_done-tabulation_done,
                              "eigensolve": eigensolve_done-assembly_done},
            "angular_table_cache": angular_table.cache_info()._asdict(),
            "source_files_sha256": source_before,
            "source_identity_scope": "source files observed equal before and after solve; runner binds isolated process inputs"})
    if _source_files_identity() != source_before:
        raise RuntimeError("solver source files changed during solve")
    if backend == "native":
        identity = result.metadata["native_library"]
        if hashlib.sha256(Path(identity["library_path"]).read_bytes()).hexdigest() != identity["library_sha256"]:
            raise RuntimeError("native library bytes changed after initial load")
    result.metadata["stage_seconds"]["postprocess"] = time.perf_counter()-eigensolve_done
    result.metadata["elapsed_seconds"] = time.perf_counter()-start
    return result


RESIDUAL_DEFINITION = (
    "||H c - E M c||_2 / (||H c||_2 + |E| ||M c||_2); "
    "relative Euclidean finite generalized-matrix residual; "
    "not a dimensional PDE residual or continuum error bound")


@dataclass(frozen=True)
class MultiStateResult:
    """Finite-sector Ritz data; no complete-spectrum or continuum certificate.

    Columns use real azimuth-independent meridional coefficients. m=1 is the
    normalized cosine representative; +/-m construction belongs to embedding.
    Arrays of the result are owned read-only copies. PartialWaveState remains
    compatible with the previous evaluator API.
    """
    states: tuple
    projected_operator: np.ndarray
    mass_gram: np.ndarray
    coefficient_vectors: np.ndarray
    metadata: dict

    def __post_init__(self):
        for name in ("projected_operator", "mass_gram", "coefficient_vectors"):
            value = np.array(getattr(self, name), dtype=np.float64, copy=True)
            if not np.isfinite(value).all():
                raise ValueError(f"{name} contains nonfinite values")
            value.setflags(write=False)
            object.__setattr__(self, name, value)
        k = len(self.states)
        if k < 1 or self.projected_operator.shape != (k, k) or self.mass_gram.shape != (k, k):
            raise ValueError("multistate operator and Gram dimensions disagree")
        if self.coefficient_vectors.ndim != 2 or self.coefficient_vectors.shape[1] != k:
            raise ValueError("multistate coefficient dimensions disagree")


def _finish_eigenpairs(H, M, eig, vec, *, R, ZA, ZB, m, ls, boundaries,
                       degree, nroots, metadata):
    """Validated numerical postprocessing, also usable in manufactured tests."""
    eig = np.asarray(eig, dtype=np.float64)
    vec = np.array(vec, dtype=np.float64, copy=True)
    if (eig.shape != (nroots,) or vec.shape != (H.shape[0], nroots)
            or not np.isfinite(eig).all() or not np.isfinite(vec).all()):
        raise ArithmeticError("eigensolver returned invalid eigenpair dimensions or values")
    if H.shape != M.shape or H.shape[0] != H.shape[1]:
        raise ValueError("H and M must be equally sized square matrices")
    order = np.argsort(eig, kind="stable")
    eig, vec = eig[order], vec[:, order]
    norms = np.einsum("ij,ij->j", vec, M @ vec)
    if np.any(~np.isfinite(norms)) or np.any(norms <= 0):
        raise ArithmeticError("eigenvectors require positive finite mass norms")
    vec /= np.sqrt(norms)[None, :]
    # The first largest-magnitude coefficient fixes sign deterministically.
    # An excited eigenstate is not assumed positive. Degenerate subspaces may
    # still undergo an orthogonal basis rotation across libraries/iterations.
    probes = vec[np.argmax(np.abs(vec), axis=0), np.arange(nroots)]
    vec *= np.where(probes < 0, -1., 1.)[None, :]
    Hv, Mv = H @ vec, M @ vec
    denominator = np.linalg.norm(Hv, axis=0) + np.abs(eig)*np.linalg.norm(Mv, axis=0)
    numerator = np.linalg.norm(Hv-Mv*eig[None, :], axis=0)
    if np.any(denominator <= 0):
        raise ArithmeticError("relative algebraic residual has zero denominator")
    residuals = numerator/denominator
    if not np.isfinite(residuals).all():
        raise ArithmeticError("nonfinite algebraic residual")
    gram = vec.T @ Mv
    hsmall = vec.T @ Hv
    metadata = dict(metadata)
    metadata.update(
        ritz_eigenvalues=eig.tolist(), ritz_residuals=residuals.tolist(),
        discrete_sector_gap=float(eig[1]-eig[0]) if nroots >= 2 else None,
        root_count=nroots, residual_definition=RESIDUAL_DEFINITION,
        eigenstate_phase_rule="first largest-absolute finite coefficient is positive",
        projected_operator_definition="C.T @ H @ C, measured from assembled finite Hamiltonian",
        mass_gram_definition="C.T @ M @ C, measured from assembled FEM mass matrix",
        hsmall_is_nominal_diagonal=False)
    nr = (len(boundaries)-1)*degree-1
    if len(ls)*nr != H.shape[0]:
        raise ValueError("finite matrix dimensions disagree with FEM mesh")
    states = []
    for j in range(nroots):
        coeff = np.zeros((len(ls), nr+2), dtype=np.float64)
        coeff[:, 1:-1] = vec[:, j].reshape(len(ls), nr)
        state_meta = {**metadata, "source_ordinal": j}
        state = PartialWaveState(R, ZA, ZB, m, np.array(ls, copy=True),
            np.array(boundaries, copy=True), degree, coeff, float(eig[j]),
            float(residuals[j]), float(gram[j, j]),
            float(np.max(np.abs(vec[:, j]))), state_meta)
        states.append(state)
    return MultiStateResult(tuple(states), hsmall, gram, vec, metadata)


def solve(R, ZA=1., ZB=2., m=0, lmax=12, rmax=20., elements=48,
          degree=4, quadrature=None, tol=1e-11, maxiter=2000,
          center="B", boundaries=None, nroots=1, backend="native", matrix_observer=None):
    """Compatibility API: return only the sector ground state.

    All nroots requested are actually computed once, and their sorted energies
    and residuals remain in metadata. Use solve_many to retain their vectors.
    The prior sector-ground probe sign convention is retained here only.
    """
    result = solve_many(R, ZA, ZB, m, lmax, rmax, elements, degree,
        quadrature, tol, maxiter, center, boundaries, nroots, backend, matrix_observer)
    original = result.states[0]
    state = replace(original, coefficients=original.coefficients.copy(),
                    metadata=dict(original.metadata))
    probes = state.evaluate(np.full(9, max(0.1, min(1., rmax/4))), np.linspace(-0.8, 0.8, 9))[0]
    phase = float(np.sum(probes))
    if phase < 0:
        state.coefficients *= -1
        phase *= -1
    state.phase_probe = phase
    state.metadata["eigenstate_phase_rule"] = "sector ground meridional probe sum nonnegative (legacy solve only)"
    return state


def direct_angular_coupling(g, b, quadrature=None):
    """Return real L/(-i*hbar) about the common numerical center.

    Independent angular-generator lane, with exactly integrated piecewise
    polynomial radial products.  No torque, energy gap, or force used.
    """
    _compatible_pair(g, b)
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


def _compatible_pair(g, b):
    if g.m != 0 or b.m != 1 or (g.R, g.ZA, g.ZB) != (b.R, b.ZA, b.ZB):
        raise ValueError("requires compatible m=0 and bright m=1 states")
    if g.metadata["origin_center"] != b.metadata["origin_center"]:
        raise ValueError("states must share a numerical origin")
    if g.boundaries[-1] != b.boundaries[-1]:
        raise ValueError("direct integration requires the same finite radial domain")


def projected_cartesian(g, b, quadrature=None):
    """Independent radial derivative lane for p_x/(-i hbar/a_A) and x/a_A.

    No energies, gaps, or force matrix elements enter either expression.
    Exact angular selection is |l-k|=1. Products with u_g u_b/r are regular
    at the origin because the Dirichlet FEM functions both vanish there.
    """
    _compatible_pair(g, b)
    n = max(g.degree, b.degree)+4 if quadrature is None else _integer(quadrature, "quadrature", max(g.degree, b.degree)+1)
    eta, ew = leggauss(int(max(g.ls[-1], b.ls[-1]))+4)
    sq = np.sqrt(1-eta*eta)
    Ag = np.stack([angular(int(l), 0, eta) for l in g.ls])
    Ab = np.stack([angular(int(l), 1, eta) for l in b.ls])
    dAb = np.stack([angular(int(l), 1, eta, True) for l in b.ls])
    C = (Ag*(ew*sq))@Ab.T
    D = (Ag*ew)@(-eta*sq*dAb+Ab/sq).T
    absent = np.abs(g.ls[:, None]-b.ls[None, :]) != 1
    C[absent] = 0.
    D[absent] = 0.
    q, qw = leggauss(n)
    mesh = np.unique(np.r_[g.boundaries, b.boundaries])
    momentum = dipole = 0.
    for lo, hi in zip(mesh[:-1], mesh[1:]):
        jac = (hi-lo)/2
        r, w = lo+jac*(q+1), qw*jac
        ug, ub, dub = g.radial(r), b.radial(r), b.radial(r, True)
        momentum += np.sum(C*((ug*w)@dub.T)+(D-C)*((ug*(w/r))@ub.T))/np.sqrt(2)
        dipole += np.sum(C*((ug*(w*r))@ub.T))/np.sqrt(2)
    return {"p_x_over_minus_i_hbar": float(momentum), "dipole_x": float(dipole)}


def direct_charge_center_coupling(g, b, quadrature=None):
    """Return L_O/(-i hbar) via the exact origin translation."""
    local = direct_angular_coupling(g, b, quadrature)
    cart = projected_cartesian(g, b, quadrature)
    shift = g.metadata["origin_shift_center_to_O"]
    return float(local+shift*cart["p_x_over_minus_i_hbar"])


def direct_observables(g, b, quadrature=None):
    """All direct lanes, with explicit operator origin and units."""
    local = direct_angular_coupling(g, b, quadrature)
    cart = projected_cartesian(g, b, quadrature)
    shift = g.metadata["origin_shift_center_to_O"]
    return {"L_center_over_minus_i_hbar": local,
            "L_O_over_minus_i_hbar": float(local+shift*cart["p_x_over_minus_i_hbar"]),
            **cart, "origin_center": g.metadata["origin_center"],
            "origin_shift_center_to_O": shift}
