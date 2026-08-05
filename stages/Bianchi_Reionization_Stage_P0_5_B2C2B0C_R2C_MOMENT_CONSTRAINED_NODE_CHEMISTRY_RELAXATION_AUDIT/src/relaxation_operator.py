"""Finite-relaxation and constrained-current primitives for R2C.

The physical reference is the exact first-order relaxation semigroup.  The
backward-Euler family is only a refinement auditor.  No function in this
module clips an infeasible state into the feasible set.
"""
from __future__ import annotations

import hashlib
import math
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from rei_bianchi.node_lift_operator import (  # noqa: E402
    capacity_constrained_group_projection,
)

MYR_S = 1.0e6 * 365.25 * 86400.0
K_B_ERG_PER_K = 1.380649e-16
DEFAULT_REL_TOL = 1.0e-12


def to_builtin(value: Any) -> Any:
    """Recursively convert NumPy/path scalars into JSON-safe built-ins."""
    if isinstance(value, np.ndarray):
        return [to_builtin(v) for v in value.tolist()]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [to_builtin(v) for v in value]
    if isinstance(value, list):
        return [to_builtin(v) for v in value]
    if isinstance(value, set):
        return [to_builtin(v) for v in sorted(value, key=repr)]
    return value


def _finite_array(value: Any, name: str) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite")
    return arr


def relaxation_lambda(dt_myr: float, tau_myr: float) -> float:
    """Return ``1-exp(-dt/tau)`` using a cancellation-safe evaluation."""
    dt = float(dt_myr)
    tau = float(tau_myr)
    if not math.isfinite(dt) or not math.isfinite(tau) or dt < 0.0 or tau <= 0.0:
        raise ValueError("dt_myr must be nonnegative and tau_myr positive")
    return -math.expm1(-dt / tau)


def infer_constant_equilibrium(
    previous: Any,
    target: Any,
    dt_myr: float,
    tau_myr: float,
) -> np.ndarray:
    """Infer the constant equilibrium whose exact map reaches ``target``."""
    y0 = _finite_array(previous, "previous")
    y1 = _finite_array(target, "target")
    if y0.shape != y1.shape:
        raise ValueError("previous and target must have identical shape")
    lam = relaxation_lambda(dt_myr, tau_myr)
    if lam <= 0.0:
        if np.array_equal(y0, y1):
            return y0.copy()
        raise ValueError("zero duration cannot reach a distinct target")
    return y0 + (y1 - y0) / lam


def advance_exact(previous: Any, equilibrium: Any, dt_myr: float, tau_myr: float) -> np.ndarray:
    """Apply the exact first-order relaxation semigroup."""
    y0 = _finite_array(previous, "previous")
    yeq = _finite_array(equilibrium, "equilibrium")
    if y0.shape != yeq.shape:
        raise ValueError("previous and equilibrium must have identical shape")
    decay = math.exp(-float(dt_myr) / float(tau_myr))
    return yeq + (y0 - yeq) * decay


def advance_backward_euler(
    previous: Any,
    equilibrium: Any,
    dt_myr: float,
    tau_myr: float,
) -> np.ndarray:
    """One backward-Euler step for ``dY/dt=(Yeq-Y)/tau``."""
    y0 = _finite_array(previous, "previous")
    yeq = _finite_array(equilibrium, "equilibrium")
    if y0.shape != yeq.shape:
        raise ValueError("previous and equilibrium must have identical shape")
    dt = float(dt_myr)
    tau = float(tau_myr)
    if dt < 0.0 or tau <= 0.0 or not math.isfinite(dt) or not math.isfinite(tau):
        raise ValueError("dt_myr must be nonnegative and tau_myr positive")
    a = dt / tau
    return (y0 + a * yeq) / (1.0 + a)


def extensive_measures(
    mass: Any,
    ionized_fraction: Any,
    temperature_k: Any,
    *,
    k_b_erg_per_k: float = K_B_ERG_PER_K,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``I=M*x_HII`` and ``U=(3/2) k_B M T``."""
    m = _finite_array(mass, "mass")
    x = _finite_array(ionized_fraction, "ionized_fraction")
    t = _finite_array(temperature_k, "temperature_k")
    if m.shape != x.shape or m.shape != t.shape:
        raise ValueError("mass, ionized_fraction and temperature_k must match")
    return m * x, 1.5 * float(k_b_erg_per_k) * m * t


def recover_intensives(
    mass: Any,
    ionized_measure: Any,
    thermal_measure: Any,
    *,
    k_b_erg_per_k: float = K_B_ERG_PER_K,
) -> tuple[np.ndarray, np.ndarray]:
    """Recover ``x_HII`` and ``T`` without clipping invalid values."""
    m = _finite_array(mass, "mass")
    i = _finite_array(ionized_measure, "ionized_measure")
    u = _finite_array(thermal_measure, "thermal_measure")
    if m.shape != i.shape or m.shape != u.shape:
        raise ValueError("mass and extensive measures must match")
    x = np.divide(i, m, out=np.full_like(i, np.nan), where=m != 0.0)
    t = np.divide(
        u,
        1.5 * float(k_b_erg_per_k) * m,
        out=np.full_like(u, np.nan),
        where=m != 0.0,
    )
    return x, t


def _normalized_min(values: np.ndarray, scale: float) -> float:
    return float(np.min(values) / max(abs(float(scale)), 1.0))


def equilibrium_certificate(
    mass: Any,
    ionized_measure: Any,
    thermal_measure: Any,
    capacity: Any,
    currents: Any,
    *,
    macro_mass_cap: float,
    macro_volume_cap: float,
    relative_tolerance: float = DEFAULT_REL_TOL,
) -> dict[str, Any]:
    """Audit an inferred node equilibrium in extensive variables.

    The input arrays are never modified.  The result includes normalized
    slacks so enormous comoving number measures and tiny node weights can be
    compared without an arbitrary dimensional absolute tolerance.
    """
    m = _finite_array(mass, "mass").copy()
    i = _finite_array(ionized_measure, "ionized_measure").copy()
    u = _finite_array(thermal_measure, "thermal_measure").copy()
    c = _finite_array(capacity, "capacity").copy()
    j = _finite_array(currents, "currents").copy()
    if m.ndim != 1 or i.shape != m.shape or u.shape != m.shape or c.shape != m.shape:
        raise ValueError("mass, ionized, thermal and capacity must be matching vectors")
    if j.ndim != 2 or j.shape[0] != m.size:
        raise ValueError("currents must be a node-by-group matrix")

    total_mass = float(np.sum(m))
    mass_scale = max(abs(total_mass), abs(float(macro_mass_cap)), abs(float(macro_volume_cap)), 1.0)
    thermal_scale = max(float(np.sum(np.abs(u))), 1.0)
    capacity_scale = max(float(np.sum(np.abs(c))), float(np.sum(np.abs(j))), 1.0)
    group_scales = np.maximum(np.sum(np.abs(j), axis=0), 1.0)
    neutral = m - i
    row_slack = c - np.sum(j, axis=1)

    normalized = {
        "mass_min": _normalized_min(m, mass_scale),
        "ionized_H_min": _normalized_min(i, mass_scale),
        "neutral_H_min": _normalized_min(neutral, mass_scale),
        "thermal_min": _normalized_min(u, thermal_scale),
        "capacity_min": _normalized_min(c, capacity_scale),
        "current_min": float(np.min(j / group_scales[None, :])),
        "mass_cap_slack": float((float(macro_mass_cap) - total_mass) / mass_scale),
        "volume_cap_slack": float((float(macro_volume_cap) - total_mass) / mass_scale),
        "cycling_slack_min": _normalized_min(row_slack, capacity_scale),
    }
    tol = float(relative_tolerance)
    violations: list[str] = []
    if normalized["mass_min"] < -tol:
        violations.append("NEGATIVE_H_MASS")
    if normalized["ionized_H_min"] < -tol:
        violations.append("NEGATIVE_IONIZED_H")
    if normalized["neutral_H_min"] < -tol:
        violations.append("IONIZED_H_EXCEEDS_H")
    if normalized["thermal_min"] < -tol:
        violations.append("NEGATIVE_THERMAL_MEASURE")
    if normalized["capacity_min"] < -tol:
        violations.append("NEGATIVE_CYCLING_CAPACITY")
    if normalized["current_min"] < -tol:
        violations.append("NEGATIVE_PHOTON_CURRENT")
    if normalized["mass_cap_slack"] < -tol:
        violations.append("MACRO_MASS_CAP_EXCEEDED")
    if normalized["volume_cap_slack"] < -tol:
        violations.append("MACRO_VOLUME_CAP_EXCEEDED")
    if normalized["cycling_slack_min"] < -tol:
        violations.append("CYCLING_CAPACITY_DEFICIT")

    positive = m > tol * mass_scale
    temperature_min = math.nan
    temperature_max = math.nan
    if np.any(positive):
        _, temperature = recover_intensives(m[positive], i[positive], u[positive])
        temperature_min = float(np.min(temperature))
        temperature_max = float(np.max(temperature))
        if not np.all(np.isfinite(temperature)) or temperature_min <= 0.0:
            violations.append("NONPOSITIVE_OR_NONFINITE_TEMPERATURE")
    elif total_mass > tol * mass_scale:
        violations.append("NO_POSITIVE_NODE_SUPPORT")

    return to_builtin(
        {
            "pass": len(violations) == 0,
            "violated_constraints": violations,
            "normalized": normalized,
            "temperature_min_K": temperature_min,
            "temperature_max_K": temperature_max,
            "total_mass": total_mass,
            "macro_mass_cap": float(macro_mass_cap),
            "macro_volume_cap": float(macro_volume_cap),
            "minimum_row_capacity_slack": float(np.min(row_slack)),
        }
    )


def active_set_digest(indices: Any) -> str:
    """Hash an ordered active-index vector in a platform-independent format."""
    arr = np.asarray(indices, dtype="<i8").reshape(-1)
    return hashlib.sha256(arr.tobytes(order="C")).hexdigest()


def generalized_kl(x: Any, prior: Any) -> float:
    """Generalized KL/I-divergence for nonnegative measures."""
    a = _finite_array(x, "x")
    p = _finite_array(prior, "prior")
    if a.shape != p.shape or np.any(a < 0.0) or np.any(p < 0.0):
        return math.inf
    if np.any((a > 0.0) & (p == 0.0)):
        return math.inf
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(a > 0.0, a * np.log(a / np.where(p > 0.0, p, 1.0)), 0.0) - a + p
    value = float(np.sum(terms))
    return max(value, 0.0) if value > -1.0e-12 else value


def total_variation_normalized(x: Any, y: Any) -> float:
    """TV distance after independently normalizing two nonnegative measures."""
    a = _finite_array(x, "x")
    b = _finite_array(y, "y")
    if a.shape != b.shape or np.any(a < 0.0) or np.any(b < 0.0):
        return math.inf
    sa = float(np.sum(a))
    sb = float(np.sum(b))
    if sa <= 0.0 and sb <= 0.0:
        return 0.0
    if sa <= 0.0 or sb <= 0.0:
        return 1.0
    return 0.5 * float(np.sum(np.abs(a / sa - b / sb)))


def project_currents(
    prior_matrix: Any,
    group_totals: Any,
    row_capacity: Any,
    *,
    tolerance: float = 2.0e-11,
) -> tuple[np.ndarray | None, dict[str, Any]]:
    """Project currents or return an explicit infeasibility certificate."""
    prior = _finite_array(prior_matrix, "prior_matrix")
    totals = _finite_array(group_totals, "group_totals").reshape(-1)
    caps = _finite_array(row_capacity, "row_capacity").reshape(-1)
    if prior.ndim != 2 or prior.shape != (caps.size, totals.size):
        raise ValueError("prior_matrix shape must match capacities and totals")
    required = float(np.sum(totals))
    available = float(np.sum(caps))
    scale = max(required, available, 1.0)
    if available + float(tolerance) * scale < required:
        return None, {
            "pass": False,
            "certificate_type": "TOTAL_CAPACITY_DEFICIT",
            "required": required,
            "available": available,
            "deficit": required - available,
            "clipping_used": False,
        }
    try:
        projected, raw_cert = capacity_constrained_group_projection(
            prior,
            totals,
            caps,
            tol=float(tolerance),
        )
    except ValueError as exc:
        return None, {
            "pass": False,
            "certificate_type": "PROJECTION_OPERATOR_INFEASIBLE",
            "message": str(exc),
            "required": required,
            "available": available,
            "clipping_used": False,
        }
    lamb = np.asarray(raw_cert.get("lambda", []), dtype=float)
    active = np.flatnonzero(lamb > 1.0e-12).astype(np.int64)
    cert = {k: v for k, v in raw_cert.items() if k != "lambda"}
    row_violation = np.maximum(np.sum(projected, axis=1) - caps, 0.0)
    max_capacity_violation = float(np.max(row_violation)) if row_violation.size else 0.0
    cert.update(
        {
            "pass": True,
            "max_capacity_relative_violation": max_capacity_violation / scale,
            "active_set_count": int(active.size),
            "active_set_sha256": active_set_digest(active),
            "active_lambda_min": float(np.min(lamb[active])) if active.size else 0.0,
            "active_lambda_max": float(np.max(lamb[active])) if active.size else 0.0,
            "projection_generalized_kl_to_raw": generalized_kl(projected, prior),
            "projection_TV_G1": total_variation_normalized(projected[:, 0], prior[:, 0]),
            "projection_TV_G2a": total_variation_normalized(projected[:, 1], prior[:, 1]),
        }
    )
    return projected, to_builtin(cert)


def refinement_convergence(errors: Iterable[float]) -> dict[str, Any]:
    """Summarize the n=1,2,4 error family against an exact reference."""
    e = np.asarray(list(errors), dtype=float)
    if e.shape != (3,) or not np.all(np.isfinite(e)) or np.any(e < 0.0):
        raise ValueError("errors must be three finite nonnegative values for n=1,2,4")
    tiny = np.finfo(float).tiny
    p12 = math.log(max(e[0], tiny) / max(e[1], tiny), 2.0)
    p24 = math.log(max(e[1], tiny) / max(e[2], tiny), 2.0)
    return {
        "monotone": bool(e[2] <= e[1] * (1.0 + 1.0e-12) and e[1] <= e[0] * (1.0 + 1.0e-12)),
        "observed_order_1_to_2": float(p12),
        "observed_order_1_to_2_to_4": float(p24),
        "error_n1": float(e[0]),
        "error_n2": float(e[1]),
        "error_n4": float(e[2]),
    }
