"""Scaled callbacks for the pinned HE29 model; no replacement physics.

One Rust solve advances one original cutoff interval on u in [0, 1].
F_u = dt S^-1 F, J_u v = dt S^-1 J S v.  The explicit time
derivative differentiates F_u with respect to u at fixed scaled state.
All finite differences stay inside the active physical interval.  They
are numerical derivatives, not certified derivatives or error bounds.
"""
from __future__ import annotations

import math
import numpy as np
from scipy import sparse


class CallbackContractError(ValueError):
    pass


def finite_vector(value, n, label):
    result = np.asarray(value, dtype=np.float64)
    if result.shape != (n,) or not np.isfinite(result).all():
        raise CallbackContractError(label + ": expected finite vector")
    return result


class SegmentCallbacks:
    """Own a single active interval and a one-entry, exact-state Jacobian cache.

    The parent owns the gas finite-difference Jacobian and analytical photon
    columns.  Cache keys include physical time and every scaled-state byte;
    no approximate reuse, tolerance-based state matching or state clipping.
    """

    def __init__(self, model, left, right, scale):
        self.model = model
        self.left, self.right = float(left), float(right)
        self.dt = self.right - self.left
        if not (math.isfinite(self.left) and math.isfinite(self.right)
                and self.dt > 0 and math.isfinite(self.dt)):
            raise CallbackContractError("invalid physical interval")
        self.scale = np.array(scale, dtype=np.float64, copy=True)
        if (self.scale.ndim != 1 or not self.scale.size
                or not np.isfinite(self.scale).all() or np.any(self.scale <= 0)):
            raise CallbackContractError("invalid state scale")
        self.n = self.scale.size
        if not callable(getattr(model, "jac", None)):
            raise CallbackContractError("pinned model Jacobian is required")
        self.counts = dict(rhs=0, jvp=0, jacobian_builds=0, jacobian_cache_hits=0,
                           partial_u=0, two_point_time_derivatives=0,
                           time_roundoff_clamps=0)
        self._jac_key = self._jacobian = None

    def time(self, u):
        u = float(u)
        if not math.isfinite(u):
            raise CallbackContractError("nonfinite normalized time")
        # Only binary64 endpoint roundoff is admitted, and counted.
        if u < 0 or u > 1:
            if not -4 * np.finfo(float).eps <= u <= 1 + 4 * np.finfo(float).eps:
                raise CallbackContractError("normalized time outside interval")
            self.counts["time_roundoff_clamps"] += 1
            u = min(1., max(0., u))
        if u == 0:
            return self.left
        if u == 1:
            return self.right
        return min(self.right, max(self.left, self.left + u * self.dt))

    def _physical_rhs_scaled(self, t, z):
        if not self.left <= t <= self.right:
            raise CallbackContractError("time derivative crossed physical interval")
        z = finite_vector(z, self.n, "scaled state")
        with np.errstate(over="ignore", invalid="ignore"):
            physical = finite_vector(z * self.scale, self.n, "physical state")
        f = finite_vector(self.model.rhs(t, physical), self.n, "physical RHS")
        self.counts["rhs"] += 1
        return finite_vector(self.dt * (f / self.scale), self.n, "normalized RHS")

    def rhs(self, u, z):
        return self._physical_rhs_scaled(self.time(u), z)

    def jvp(self, u, z, v):
        z = finite_vector(z, self.n, "scaled state")
        v = finite_vector(v, self.n, "JVP vector")
        with np.errstate(over="ignore", invalid="ignore"):
            physical = finite_vector(z * self.scale, self.n, "physical state")
            direction = finite_vector(v * self.scale, self.n, "physical JVP direction")
        t = self.time(u)
        key = (t.hex(), z.tobytes(order="C"))
        if key != self._jac_key:
            jac = self.model.jac(t, physical)
            if jac.shape != (self.n, self.n):
                raise CallbackContractError("physical Jacobian shape")
            if sparse.issparse(jac):
                jac = jac.tocsr(copy=True)
                valid = np.isfinite(jac.data).all()
            else:
                jac = np.array(jac, dtype=np.float64, copy=True)
                valid = np.isfinite(jac).all()
            if not valid:
                raise CallbackContractError("nonfinite physical Jacobian")
            self._jacobian, self._jac_key = jac, key
            self.counts["jacobian_builds"] += 1
        else:
            self.counts["jacobian_cache_hits"] += 1
        self.counts["jvp"] += 1
        return finite_vector(self.dt * (self._jacobian @ direction) / self.scale,
                             self.n, "normalized JVP")

    def partial_u(self, u, z):
        """Bounded 3-point time derivative, with explicit 2-point ULP fallback.

        We use actual represented physical times in the derivative weights.
        This matters for short intervals at large proper times.  The base
        value is subtracted before weighting to cancel a constant RHS.
        Table-knot derivatives are finite differences, not smoothness claims.
        """
        t = self.time(u)
        z = finite_vector(z, self.n, "scaled state")
        self.counts["partial_u"] += 1
        physical_ulp = max(math.ulp(t), math.ulp(self.left), math.ulp(self.right))
        h = max(np.cbrt(np.finfo(float).eps) * self.dt, 4 * physical_ulp)
        if t - self.left >= h and self.right - t >= h:
            nodes = [t - h, t, t + h]
        elif self.right - t >= t - self.left:
            h = min(h, (self.right - t) / 2)
            nodes = [t, t + h, min(self.right, t + 2 * h)]
        else:
            h = min(h, (t - self.left) / 2)
            nodes = [max(self.left, t - 2 * h), t - h, t]
        nodes = sorted(set(nodes))
        if len(nodes) < 2:
            nodes = sorted(set([self.left, t, self.right]))
        if len(nodes) < 2:
            raise CallbackContractError("time interval has no representable derivative")
        if len(nodes) == 2:
            self.counts["two_point_time_derivatives"] += 1
            f0, f1 = [self._physical_rhs_scaled(s, z) for s in nodes]
            return finite_vector((f1 - f0) / ((nodes[1] - nodes[0]) / self.dt),
                                 self.n, "two-point time derivative")
        x = np.array([(s - t) / self.dt for s in nodes])
        base = self._physical_rhs_scaled(t, z)
        derivative = np.zeros(self.n)
        for i in range(3):
            if nodes[i] == t:
                continue
            j, k = [q for q in range(3) if q != i]
            weight = -(x[j] + x[k]) / ((x[i] - x[j]) * (x[i] - x[k]))
            derivative += weight * (self._physical_rhs_scaled(nodes[i], z) - base)
        return finite_vector(derivative, self.n, "three-point time derivative")


def validate_model(model):
    scale = np.asarray(model.scale, dtype=np.float64)
    initial = np.asarray(model.initial_state(), dtype=np.float64)
    if (scale.ndim != 1 or initial.shape != scale.shape or not scale.size
            or not np.isfinite(scale).all() or not np.isfinite(initial).all()
            or np.any(scale <= 0)):
        raise CallbackContractError("invalid initial state or positive scale")
    end = float(model.t_end)
    cuts = np.asarray(getattr(model, "breakpoints", ()), dtype=np.float64)
    if (not math.isfinite(end) or end <= 0 or cuts.ndim != 1
            or not np.isfinite(cuts).all() or np.any(cuts <= 0)
            or np.any(cuts >= end) or np.any(np.diff(cuts) <= 0)):
        raise CallbackContractError("invalid endpoint or cutoff order")
    return scale.copy(), initial.copy(), np.r_[0., cuts, end]
