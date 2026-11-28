"""Sparse, batched direct operators for the unchanged binary64 hp-FEM states.

Same angular/radial Gauss orders as reference/partialwave_centered.py.
With positive associated Legendre phases, the angular generator has l=k,
whereas x and its Cartesian derivative have |l-k|=1. Thus only O(lmax)
angular pairs are nonzero. C_lk and D_lk are evaluated by the original
Gauss formulas and cached by the exact integer l tuples; no rounded R keys,
state values, energy gaps, or force matrix elements enter this cache.

For each active pair the radial contractions remain
  pbar = [C integral(ug ub') + (D-C) integral(ug ub/r)]/sqrt(2),
  xbar = C integral(r ug ub)/sqrt(2).
The union partition permits distinct radial meshes without interpolation.
All quadrature nodes are evaluated in one batch. Summation order changes
at binary64 roundoff only; fast-math and reduced precision are not used.
Norms, phases, coefficients, and metadata are never modified here.
"""
from functools import lru_cache
import numpy as np
from numpy.polynomial.legendre import leggauss
from partialwave_centered import angular


def _positive_integer(n, name, lower=1):
    if isinstance(n, bool) or not np.isfinite(n) or int(n) != n or n < lower:
        raise ValueError(f"{name} must be integer >= {lower}")
    return int(n)


def _validate_pair(g, b):
    if g.m != 0 or b.m != 1 or (g.R, g.ZA, g.ZB) != (b.R, b.ZA, b.ZB):
        raise ValueError("requires compatible m=0 and bright m=1 states")
    if not np.all(np.isfinite([g.R, g.ZA, g.ZB])) or g.R < 0 or min(g.ZA, g.ZB) < 0 or g.ZA+g.ZB <= 0:
        raise ValueError("invalid physical parameters")
    center = g.metadata.get("origin_center")
    if center not in ("O", "B") or center != b.metadata.get("origin_center"):
        raise ValueError("states must share a supported numerical origin")
    shift = g.ZA*g.R/(g.ZA+g.ZB) if center == "B" else 0.
    for s in (g, b):
        if s.metadata.get("origin_shift_center_to_O") != shift:
            raise ValueError("origin translation metadata disagrees with physics")
        mesh = np.asarray(s.boundaries)
        if mesh.ndim != 1 or len(mesh) < 2 or not np.all(np.isfinite(mesh)) or mesh[0] != 0 or np.any(np.diff(mesh) <= 0):
            raise ValueError("invalid radial partition")
        degree = _positive_integer(s.degree, "degree")
        ls = np.asarray(s.ls)
        if ls.ndim != 1 or len(ls) == 0 or not np.all(np.isfinite(ls)) or np.any(ls < s.m) or np.any(ls != np.floor(ls)) or np.any(np.diff(ls) <= 0):
            raise ValueError("angular indices must be strictly increasing legal integers")
        coeff = np.asarray(s.coefficients)
        if coeff.shape != (len(ls), (len(mesh)-1)*degree+1) or not np.all(np.isfinite(coeff)) or np.iscomplexobj(coeff):
            raise ValueError("invalid real radial coefficient array")
    if g.boundaries[-1] != b.boundaries[-1]:
        raise ValueError("direct integration requires the same finite radial domain")


@lru_cache(maxsize=32)
def _gauss(n):
    q, w = leggauss(n)
    q.flags.writeable = w.flags.writeable = False
    return q, w


@lru_cache(maxsize=32)
def _angular_sparse(gls, bls):
    """Exact structural zeros; nonzero coefficients use reference Gauss order."""
    gl, bl = np.asarray(gls), np.asarray(bls)
    gi, bi = np.nonzero(np.abs(gl[:, None]-bl[None, :]) == 1)
    lg, lb = np.nonzero(gl[:, None] == bl[None, :])
    eta, ew = _gauss(int(max(gl[-1], bl[-1]))+4)
    sq = np.sqrt(1-eta*eta)
    Ag = np.stack([angular(int(l), 0, eta) for l in gl])
    Ab = np.stack([angular(int(l), 1, eta) for l in bl])
    dAb = np.stack([angular(int(l), 1, eta, True) for l in bl])
    C = np.sum((Ag[gi]*(ew*sq))*Ab[bi], axis=1)
    D = np.sum((Ag[gi]*ew)*(-eta*sq*dAb[bi]+Ab[bi]/sq), axis=1)
    L = np.sqrt(gl[lg]*(gl[lg]+1)/2.)
    ans = (gi, bi, C, D, lg, lb, L)
    for arr in ans:
        arr.flags.writeable = False
    return ans


def clear_caches():
    """Explicit cold benchmark support; no states are cached."""
    _angular_sparse.cache_clear()
    _gauss.cache_clear()


def _order(g, b, quadrature, default_extra):
    degree = max(g.degree, b.degree)
    return degree+default_extra if quadrature is None else _positive_integer(quadrature, "quadrature", degree+1)


def _radial_batch(g, b, n, derivative):
    q, qw = _gauss(n)
    mesh = np.union1d(g.boundaries, b.boundaries)
    lo, jac = mesh[:-1], np.diff(mesh)/2
    r = (lo[:, None]+jac[:, None]*(q+1)).ravel()
    w = (jac[:, None]*qw).ravel()
    return r, w, g.radial(r), b.radial(r), b.radial(r, True) if derivative else None


def _cartesian(g, b, n, data=None, angular_data=None):
    gi, bi, C, D, *_ = angular_data if angular_data is not None else _angular_sparse(tuple(g.ls), tuple(b.ls))
    r, w, ug, ub, dub = _radial_batch(g, b, n, True) if data is None else data
    pair = ug[gi]*ub[bi]
    momentum = np.sum(C*np.sum((ug[gi]*dub[bi])*w, axis=1)+(D-C)*np.sum(pair*(w/r), axis=1))/np.sqrt(2.)
    dipole = np.sum(C*np.sum(pair*(w*r), axis=1))/np.sqrt(2.)
    return {"p_x_over_minus_i_hbar": float(momentum), "dipole_x": float(dipole)}


def _angular(g, b, n, data=None, angular_data=None):
    *_, lg, lb, L = angular_data if angular_data is not None else _angular_sparse(tuple(g.ls), tuple(b.ls))
    _, w, ug, ub, _ = _radial_batch(g, b, n, False) if data is None else data
    return float(np.sum(L*np.sum((ug[lg]*ub[lb])*w, axis=1)))


def direct_angular_coupling(g, b, quadrature=None):
    _validate_pair(g, b)
    return _angular(g, b, _order(g, b, quadrature, 2))


def projected_cartesian(g, b, quadrature=None):
    _validate_pair(g, b)
    return _cartesian(g, b, _order(g, b, quadrature, 4))


def direct_observables(g, b, quadrature=None):
    """Drop-in direct result; preserve distinct default quadrature orders."""
    _validate_pair(g, b)
    nl, nc = _order(g, b, quadrature, 2), _order(g, b, quadrature, 4)
    coeff = _angular_sparse(tuple(g.ls), tuple(b.ls))
    cart_data = _radial_batch(g, b, nc, True)
    local = _angular(g, b, nl, cart_data if nl == nc else None, coeff)
    cart = _cartesian(g, b, nc, cart_data, coeff)
    shift = g.metadata["origin_shift_center_to_O"]
    return {"L_center_over_minus_i_hbar": local,
            "L_O_over_minus_i_hbar": float(local+shift*cart["p_x_over_minus_i_hbar"]),
            **cart, "origin_center": g.metadata["origin_center"],
            "origin_shift_center_to_O": shift}


def direct_charge_center_coupling(g, b, quadrature=None):
    return direct_observables(g, b, quadrature)["L_O_over_minus_i_hbar"]
