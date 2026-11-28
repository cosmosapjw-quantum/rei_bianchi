"""Physical charge-center overlap of real, fixed-m prolate states.

No eigensolver is called.  Finite-domain states are extended by zero.  This
implements a physical L2 overlap, never a coefficient dot product.  The
returned phase suggestion is not a rank-five-cluster transport certificate.
"""
from functools import lru_cache
import math

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import BSpline


@lru_cache(maxsize=16)
def _gauss(order):
    if isinstance(order, bool) or not isinstance(order, int) or order < 2:
        raise ValueError("order must be an integer >= 2")
    nodes, weights = leggauss(order)
    nodes.setflags(write=False)
    weights.setflags(write=False)
    return nodes, weights


def charge_center_positions(R, ZA, ZB):
    """Return z_A,z_B and the prolate midpoint, all relative to O."""
    if (not all(np.isfinite(x) for x in (R, ZA, ZB)) or R <= 0
            or min(ZA, ZB) < 0 or ZA + ZB <= 0):
        raise ValueError("finite R>0 and nonnegative charges are required")
    za = -ZB * R / (ZA + ZB)
    zb = ZA * R / (ZA + ZB)
    return za, zb, (za + zb) / 2


def prolate_to_charge_center(xi, eta, R, ZA, ZB):
    xi, eta = np.broadcast_arrays(np.asarray(xi, float), np.asarray(eta, float))
    if (not np.all(np.isfinite(xi)) or not np.all(np.isfinite(eta))
            or np.any(xi < 1) or np.any(np.abs(eta) > 1)):
        raise ValueError("invalid prolate coordinates")
    _, _, midpoint = charge_center_positions(R, ZA, ZB)
    rho = R / 2 * np.sqrt((xi * xi - 1) * (1 - eta * eta))
    z = R / 2 * xi * eta + midpoint
    return rho, z


def charge_center_to_prolate(rho, z, R, ZA, ZB):
    rho, z = np.broadcast_arrays(np.asarray(rho, float), np.asarray(z, float))
    if (not np.all(np.isfinite(rho)) or not np.all(np.isfinite(z))
            or np.any(rho < 0)):
        raise ValueError("finite cylindrical coordinates with rho >= 0 required")
    za, zb, _ = charge_center_positions(R, ZA, ZB)
    ra = np.hypot(rho, z - za)
    rb = np.hypot(rho, z - zb)
    # Triangle inequalities imply these bounds exactly.  Enforce them only
    # against roundoff in the distance calculation, not physical clipping.
    xi = np.maximum(1.0, (ra + rb) / R)
    eta = np.clip((ra - rb) / R, -1.0, 1.0)
    return xi, eta


class _Values:
    """Scalar BSplines avoid allocating points-by-basis dense arrays."""
    def __init__(self, state):
        self.state = state
        self.splines = []
        for axis, coefficients in ((state._radial, state.radial_coefficients),
                                   (state._angular, state.angular_coefficients)):
            if np.iscomplexobj(coefficients) or not np.all(np.isfinite(coefficients)):
                raise ValueError("finite real coefficients required")
            # Reconstruct the scalar spline including the fixed zero radial
            # boundary coefficient.  This operation is not an overlap.
            c = axis.basis.c @ np.asarray(coefficients)
            self.splines.append(BSpline(axis.basis.t, c, axis.basis.k,
                                        extrapolate=False))

    def __call__(self, xi, eta):
        xi, eta = np.broadcast_arrays(np.asarray(xi, float), np.asarray(eta, float))
        out = np.zeros(xi.shape, dtype=np.float64)
        inside = ((xi >= 1) & (xi <= self.state.xi_max) & (np.abs(eta) <= 1))
        if not np.any(inside):
            return out
        x, y = xi[inside], eta[inside]
        factor = ((x*x-1)*(1-y*y)) ** (self.state.m / 2)
        out[inside] = (self.state.normalization * factor
                       * self.splines[0](x) * self.splines[1](y))
        if not np.all(np.isfinite(out)):
            raise FloatingPointError("nonfinite physical state values")
        return out


def values_at_charge_center(state, rho, z):
    """Evaluate the meridional state in a common O frame; zero outside box."""
    xi, eta = charge_center_to_prolate(rho, z, state.R, state.ZA, state.ZB)
    return _Values(state)(xi, eta)


def _compatible(left, right):
    if (left.ZA, left.ZB, left.m) != (right.ZA, right.ZB, right.m):
        raise ValueError("same charges, fixed m and real azimuthal sector required")
    for state in (left, right):
        charge_center_positions(state.R, state.ZA, state.ZB)
        if isinstance(state.m, bool) or not isinstance(state.m, (int, np.integer)) or state.m < 0:
            raise ValueError("nonnegative integer fixed m required")
        if not np.isfinite(state.normalization) or state.normalization <= 0:
            raise ValueError("positive finite normalization required")


def _directed_overlap(source, target, order):
    """Integrate over source support; target is evaluated in the same O frame."""
    q, w = _gauss(order)
    source_values, target_values = _Values(source), _Values(target)
    ye = np.asarray(source._angular.edges)
    eta = (((ye[1:] + ye[:-1])[:, None]
             + (ye[1:] - ye[:-1])[:, None] * q) / 2).ravel()
    we = ((ye[1:] - ye[:-1])[:, None] * w / 2).ravel()
    pieces = []
    points = 0
    # One radial element at a time bounds temporary array size by
    # order**2 * n_angular_elements, independent of the radial mesh size.
    for lo, hi in zip(source._radial.edges[:-1], source._radial.edges[1:]):
        xi = ((hi + lo) + (hi - lo) * q) / 2
        wx = (hi - lo) * w / 2
        x, y = np.broadcast_arrays(xi[:, None], eta[None, :])
        rho, z = prolate_to_charge_center(x, y, source.R, source.ZA, source.ZB)
        tx, ty = charge_center_to_prolate(rho, z, target.R, target.ZA, target.ZB)
        measure = (source.R**3 / 8 * (x*x-y*y)
                   * wx[:, None] * we[None, :])
        integrand = measure * source_values(x, y) * target_values(tx, ty)
        pieces.append(float(np.sum(integrand, dtype=np.float64)))
        points += integrand.size
    return float(math.fsum(pieces)), points


def pair_overlap(left, right, order):
    """Both integration directions and self norms at one quadrature order.

    Call independently at preregistered low/high orders.  The directional
    discrepancy detects failures hidden by one support parametrization;
    neither discrepancy nor refinement is a rigorous error enclosure.
    """
    _compatible(left, right)
    lr, nlr = _directed_overlap(left, right, order)
    rl, nrl = _directed_overlap(right, left, order)
    nl, _ = _directed_overlap(left, left, order)
    nr, _ = _directed_overlap(right, right, order)
    if min(nl, nr) <= 0 or not np.all(np.isfinite([lr, rl, nl, nr])):
        raise FloatingPointError("invalid quadrature overlap or self norm")
    norm = math.sqrt(nl * nr)
    mean = (lr + rl) / 2
    return {
        "R_left": float(left.R), "R_right": float(right.R), "m": int(left.m),
        "order": order, "overlap": float(mean),
        "normalized_overlap": float(mean / norm),
        "left_domain_overlap": lr, "right_domain_overlap": rl,
        "directional_difference_abs": abs(lr-rl),
        "self_norm_left": nl, "self_norm_right": nr,
        "max_self_norm_error_abs": max(abs(nl-1), abs(nr-1)),
        "phase_factor_suggestion": 1 if mean >= 0 else -1,
        "quadrature_points": {"left_domain": nlr, "right_domain": nrl},
        "measure": "rho d(rho) dz in common charge-center O; same real azimuthal factor",
        "domain": "each finite prolate state extended by zero",
        "selection_scope": "two separately lowest fixed-m branches; rank-five cluster NOT_VERIFIED",
    }


def refinement_audit(low, high, tolerance=1e-7, minimum_overlap=0.5):
    """Apply preregistered gates without changing states or hidden retries."""
    for key in ("R_left", "R_right", "m"):
        if low[key] != high[key]:
            raise ValueError("refinement records describe different state pairs")
    if low["order"] >= high["order"]:
        raise ValueError("high order must be strictly greater than low order")
    if not (np.isfinite(tolerance) and tolerance > 0
            and np.isfinite(minimum_overlap) and 0 < minimum_overlap <= 1):
        raise ValueError("invalid audit tolerances")
    increment = max(abs(high[k]-low[k]) for k in
                    ("left_domain_overlap", "right_domain_overlap", "normalized_overlap"))
    quadrature_pass = (increment <= tolerance
                       and high["directional_difference_abs"] <= tolerance
                       and high["max_self_norm_error_abs"] <= tolerance)
    magnitude = abs(high["normalized_overlap"])
    transport_pass = (quadrature_pass and minimum_overlap <= magnitude <= 1+tolerance)
    return {"quadrature_increment_abs": increment,
            "quadrature_tolerance_abs": tolerance,
            "minimum_normalized_overlap": minimum_overlap,
            "quadrature_pass": bool(quadrature_pass),
            "transport_pass": bool(transport_pass),
            "phase_factor": high["phase_factor_suggestion"] if transport_pass else None,
            "status": "PASS_FIXED_M_LOCAL_STEP" if transport_pass else "HOLD",
            "certificate": "empirical finite-state quadrature and local transport only"}
