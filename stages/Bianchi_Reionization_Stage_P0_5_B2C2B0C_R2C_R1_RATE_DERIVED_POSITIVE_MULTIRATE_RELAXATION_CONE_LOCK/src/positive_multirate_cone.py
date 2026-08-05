"""Bounded macro-shared positive multirate cone solver for R2C-R1."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

import numpy as np
from scipy.optimize import linprog

from rate_interval_model import family_attenuation_inverse

FAMILY_ORDER = ("M", "I", "U", "C", "J_G1", "J_G2a")
FAMILY_INDEX = {name: i for i, name in enumerate(FAMILY_ORDER)}


@dataclass(frozen=True)
class EquilibriumProblem:
    previous: dict[str, np.ndarray]
    target: dict[str, np.ndarray]
    dt_myr: float
    rate_bounds: dict[str, tuple[float, float]]
    a_lower: np.ndarray
    a_upper: np.ndarray
    A_ub: np.ndarray
    b_ub: np.ndarray
    labels: list[dict[str, Any]]
    macro_mass_cap: float
    macro_volume_cap: float


def _arrays(states: Mapping[str, Any]) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}
    n: int | None = None
    for family in FAMILY_ORDER:
        arr = np.asarray(states[family], dtype=float)
        if arr.ndim != 1 or np.any(~np.isfinite(arr)):
            raise ValueError(f"{family} must be a finite vector")
        if n is None:
            n = arr.size
        elif arr.size != n:
            raise ValueError("all state families must have identical node support")
        result[family] = arr
    return result


def _rate_from_a(a: float, dt_myr: float) -> float:
    if not math.isfinite(a) or a <= 1.0:
        if math.isclose(a, 1.0, rel_tol=0.0, abs_tol=2e-15):
            return math.inf
        raise ValueError("attenuation inverse must exceed one")
    return -math.log1p(-1.0 / a) / float(dt_myr)


def build_equilibrium_problem(
    previous: Mapping[str, Any],
    target: Mapping[str, Any],
    rate_bounds: Mapping[str, tuple[float, float]],
    *,
    dt_myr: float,
    macro_mass_cap: float,
    macro_volume_cap: float,
) -> EquilibriumProblem:
    y0 = _arrays(previous)
    y1 = _arrays(target)
    dt = float(dt_myr)
    if dt <= 0.0 or not math.isfinite(dt):
        raise ValueError("dt_myr must be positive")
    bounds: dict[str, tuple[float, float]] = {}
    lower = []
    upper = []
    for family in FAMILY_ORDER:
        lo, hi = map(float, rate_bounds[family])
        if not (0.0 < lo <= hi and math.isfinite(lo) and math.isfinite(hi)):
            raise ValueError(f"invalid rate interval for {family}")
        bounds[family] = (lo, hi)
        lower.append(family_attenuation_inverse(hi, dt))
        upper.append(family_attenuation_inverse(lo, dt))
    a_lower = np.asarray(lower)
    a_upper = np.asarray(upper)
    span = a_upper - a_lower
    delta = {f: y1[f] - y0[f] for f in FAMILY_ORDER}
    rows: list[np.ndarray] = []
    rhs_values: list[float] = []
    labels: list[dict[str, Any]] = []

    def add(coeff_a: np.ndarray, rhs: float, label: str, node: int | None = None) -> None:
        coeff_z = np.asarray(coeff_a, dtype=float) * span
        rhs_z = float(rhs) - float(np.dot(coeff_a, a_lower))
        scale = max(float(np.max(np.abs(coeff_z))) if coeff_z.size else 0.0, abs(rhs_z), np.finfo(float).tiny)
        rows.append(coeff_z / scale)
        rhs_values.append(rhs_z / scale)
        labels.append({"constraint": label, "node_index": node, "row_scale": scale})

    n = y0["M"].size
    for i in range(n):
        coeff = np.zeros(6); coeff[FAMILY_INDEX["M"]] = -delta["M"][i]
        add(coeff, y0["M"][i], "M_NONNEGATIVE", i)
        coeff = np.zeros(6); coeff[FAMILY_INDEX["I"]] = -delta["I"][i]
        add(coeff, y0["I"][i], "I_NONNEGATIVE", i)
        coeff = np.zeros(6); coeff[FAMILY_INDEX["M"]] = -delta["M"][i]; coeff[FAMILY_INDEX["I"]] = delta["I"][i]
        add(coeff, y0["M"][i] - y0["I"][i], "NEUTRAL_NONNEGATIVE", i)
        coeff = np.zeros(6); coeff[FAMILY_INDEX["U"]] = -delta["U"][i]
        add(coeff, y0["U"][i], "U_NONNEGATIVE", i)
        coeff = np.zeros(6); coeff[FAMILY_INDEX["C"]] = -delta["C"][i]
        add(coeff, y0["C"][i], "C_NONNEGATIVE", i)
        coeff = np.zeros(6); coeff[FAMILY_INDEX["J_G1"]] = -delta["J_G1"][i]
        add(coeff, y0["J_G1"][i], "J_G1_NONNEGATIVE", i)
        coeff = np.zeros(6); coeff[FAMILY_INDEX["J_G2a"]] = -delta["J_G2a"][i]
        add(coeff, y0["J_G2a"][i], "J_G2A_NONNEGATIVE", i)
        coeff = np.zeros(6)
        coeff[FAMILY_INDEX["C"]] = -delta["C"][i]
        coeff[FAMILY_INDEX["J_G1"]] = delta["J_G1"][i]
        coeff[FAMILY_INDEX["J_G2a"]] = delta["J_G2a"][i]
        add(coeff, y0["C"][i] - y0["J_G1"][i] - y0["J_G2a"][i], "CYCLING_CAPACITY", i)

    coeff = np.zeros(6); coeff[FAMILY_INDEX["M"]] = float(np.sum(delta["M"]))
    add(coeff, float(macro_mass_cap) - float(np.sum(y0["M"])), "MACRO_MASS_CAP", None)
    add(coeff, float(macro_volume_cap) - float(np.sum(y0["M"])), "MACRO_VOLUME_CAP", None)
    return EquilibriumProblem(
        previous=y0,
        target=y1,
        dt_myr=dt,
        rate_bounds=bounds,
        a_lower=a_lower,
        a_upper=a_upper,
        A_ub=np.vstack(rows),
        b_ub=np.asarray(rhs_values),
        labels=labels,
        macro_mass_cap=float(macro_mass_cap),
        macro_volume_cap=float(macro_volume_cap),
    )


def _farkas_certificate(A: np.ndarray, b: np.ndarray, labels: list[dict[str, Any]]) -> dict[str, Any]:
    nvar = A.shape[1]
    G = np.vstack([A, -np.eye(nvar), np.eye(nvar)])
    h = np.concatenate([b, np.zeros(nvar), np.ones(nvar)])
    Aeq = np.vstack([G.T, np.ones(G.shape[0])])
    beq = np.concatenate([np.zeros(nvar), np.ones(1)])
    result = linprog(h, A_eq=Aeq, b_eq=beq, bounds=[(0.0, None)] * G.shape[0], method="highs")
    if not result.success:
        return {"pass": False, "solver_status": int(result.status), "solver_message": str(result.message)}
    y = np.asarray(result.x)
    hdot = float(h @ y)
    residual = float(np.max(np.abs(G.T @ y)))
    active = np.flatnonzero(y > 1e-9)
    terms = []
    for idx in active[:200]:
        if idx < len(labels):
            label = labels[int(idx)]
        elif idx < len(labels) + nvar:
            label = {"constraint": "LOWER_BOUND", "family": FAMILY_ORDER[int(idx - len(labels))]}
        else:
            label = {"constraint": "UPPER_BOUND", "family": FAMILY_ORDER[int(idx - len(labels) - nvar)]}
        terms.append({"index": int(idx), "weight": float(y[idx]), **label})
    return {
        "pass": bool(hdot < -1e-10 and residual <= 2e-9),
        "h_dot_y": hdot,
        "dual_residual_inf": residual,
        "normalization_residual": float(abs(np.sum(y) - 1.0)),
        "active_term_count": int(active.size),
        "active_terms": terms,
        "solver_status": int(result.status),
        "solver_message": str(result.message),
    }


def one_mode_equilibrium(
    previous: Mapping[str, Any],
    target: Mapping[str, Any],
    rates_myr_inv: Mapping[str, float],
    dt_myr: float,
) -> dict[str, np.ndarray]:
    y0 = _arrays(previous)
    y1 = _arrays(target)
    result = {}
    for family in FAMILY_ORDER:
        a = family_attenuation_inverse(float(rates_myr_inv[family]), float(dt_myr))
        result[family] = y0[family] + a * (y1[family] - y0[family])
    return result


def solve_equilibrium_problem(problem: EquilibriumProblem) -> dict[str, Any]:
    c = np.ones(len(FAMILY_ORDER), dtype=float)
    result = linprog(
        c,
        A_ub=problem.A_ub,
        b_ub=problem.b_ub,
        bounds=[(0.0, 1.0)] * len(FAMILY_ORDER),
        method="highs",
        options={"dual_feasibility_tolerance": 1e-9, "primal_feasibility_tolerance": 1e-9},
    )
    if not result.success:
        return {
            "pass": False,
            "solver_status": int(result.status),
            "solver_message": str(result.message),
            "farkas_certificate": _farkas_certificate(problem.A_ub, problem.b_ub, problem.labels),
            "node_rate_count": 0,
        }
    z = np.asarray(result.x)
    a = problem.a_lower + (problem.a_upper - problem.a_lower) * z
    rates = {family: _rate_from_a(float(a[i]), problem.dt_myr) for i, family in enumerate(FAMILY_ORDER)}
    equilibrium = one_mode_equilibrium(problem.previous, problem.target, rates, problem.dt_myr)
    slack = problem.b_ub - problem.A_ub @ z
    eq_checks = {
        "minimum_M": float(np.min(equilibrium["M"])),
        "minimum_I": float(np.min(equilibrium["I"])),
        "minimum_neutral": float(np.min(equilibrium["M"] - equilibrium["I"])),
        "minimum_U": float(np.min(equilibrium["U"])),
        "minimum_C": float(np.min(equilibrium["C"])),
        "minimum_J_G1": float(np.min(equilibrium["J_G1"])),
        "minimum_J_G2a": float(np.min(equilibrium["J_G2a"])),
        "minimum_cycling_slack": float(np.min(equilibrium["C"] - equilibrium["J_G1"] - equilibrium["J_G2a"])),
        "mass_cap_slack": float(problem.macro_mass_cap - np.sum(equilibrium["M"])),
        "volume_cap_slack": float(problem.macro_volume_cap - np.sum(equilibrium["M"])),
    }
    y_ineq = np.asarray(result.ineqlin.marginals)
    y_lower = np.asarray(result.lower.marginals)
    y_upper = np.asarray(result.upper.marginals)
    stationarity = c + problem.A_ub.T @ y_ineq + y_lower + y_upper
    comp_ineq = y_ineq * slack
    comp_lower = y_lower * z
    comp_upper = y_upper * (z - 1.0)
    active_rows = np.flatnonzero(slack <= 1e-9)
    return {
        "pass": bool(np.min(slack) >= -2e-9),
        "solver_status": int(result.status),
        "solver_message": str(result.message),
        "objective": float(result.fun),
        "z": z.tolist(),
        "a": {family: float(a[i]) for i, family in enumerate(FAMILY_ORDER)},
        "rates_Myr_inv": rates,
        "rate_bounds_Myr_inv": {family: list(problem.rate_bounds[family]) for family in FAMILY_ORDER},
        "minimum_normalized_primal_slack": float(np.min(slack)),
        "max_stationarity_residual": float(np.max(np.abs(stationarity))),
        "max_complementarity_residual": float(max(np.max(np.abs(comp_ineq)), np.max(np.abs(comp_lower)), np.max(np.abs(comp_upper)))),
        "active_constraint_count": int(active_rows.size),
        "active_constraints": [problem.labels[int(i)] for i in active_rows[:200]],
        "equilibrium_checks": eq_checks,
        "farkas_certificate": None,
        "node_rate_count": 0,
    }


def certify_exponential_slack(
    *,
    constant: Any,
    amplitudes: Any,
    rates_myr_inv: Any,
    dt_myr: float,
    relative_tolerance: float = 1e-11,
    max_depth: int = 24,
) -> dict[str, Any]:
    const = np.asarray(constant, dtype=float)
    amps = np.asarray(amplitudes, dtype=float)
    rates = np.asarray(rates_myr_inv, dtype=float)
    if const.ndim != 1 or amps.ndim != 2 or amps.shape[0] != const.size or amps.shape[1] != rates.size:
        raise ValueError("invalid exponential slack shapes")
    if np.any(~np.isfinite(const)) or np.any(~np.isfinite(amps)) or np.any(~np.isfinite(rates)) or np.any(rates <= 0.0):
        raise ValueError("slack inputs must be finite and rates positive")
    dt = float(dt_myr)
    scale = max(float(np.sum(np.abs(const)) + np.sum(np.abs(amps))), 1.0)
    tol = float(relative_tolerance) * scale
    queue: list[tuple[float, float, int]] = [(0.0, dt, 0)]
    certified = 0
    unresolved = 0
    minimum_sampled = math.inf
    minimum_lower = math.inf
    max_used_depth = 0
    while queue:
        lo, hi, depth = queue.pop()
        max_used_depth = max(max_used_depth, depth)
        elo = np.exp(-rates * lo)
        ehi = np.exp(-rates * hi)
        term_lower = np.where(amps >= 0.0, amps * ehi[None, :], amps * elo[None, :])
        lower = const + np.sum(term_lower, axis=1)
        min_lower = float(np.min(lower))
        minimum_lower = min(minimum_lower, min_lower)
        if min_lower >= -tol:
            certified += 1
            continue
        mid = 0.5 * (lo + hi)
        for time in (lo, mid, hi):
            value = const + amps @ np.exp(-rates * time)
            minimum_sampled = min(minimum_sampled, float(np.min(value)))
        if minimum_sampled < -tol:
            return {
                "pass": False,
                "status": "REAL_NEGATIVE_SLACK",
                "minimum_sampled_slack": minimum_sampled,
                "minimum_interval_lower_bound": minimum_lower,
                "relative_minimum_sampled": minimum_sampled / scale,
                "certified_interval_count": certified,
                "unresolved_interval_count": unresolved,
                "maximum_depth_used": max_used_depth,
            }
        if depth >= int(max_depth):
            unresolved += 1
            continue
        queue.append((lo, mid, depth + 1))
        queue.append((mid, hi, depth + 1))
    passed = unresolved == 0
    if minimum_sampled is math.inf:
        minimum_sampled = float(np.min(const + amps @ np.ones(rates.size)))
    return {
        "pass": passed,
        "status": "CERTIFIED" if passed else "CERTIFICATION_AMBIGUOUS",
        "minimum_sampled_slack": minimum_sampled,
        "minimum_interval_lower_bound": minimum_lower,
        "relative_minimum_sampled": minimum_sampled / scale,
        "certified_interval_count": certified,
        "unresolved_interval_count": unresolved,
        "maximum_depth_used": max_used_depth,
    }


def two_mode_weight_for_attenuation(k_effective: float, k_lower: float, k_upper: float, dt_myr: float) -> float:
    ke = float(k_effective); kl = float(k_lower); ku = float(k_upper); dt = float(dt_myr)
    if not (0.0 < kl <= ke <= ku and dt > 0.0):
        raise ValueError("rates must satisfy 0<lower<=effective<=upper")
    dlo = math.exp(-kl * dt)
    dhi = math.exp(-ku * dt)
    deff = math.exp(-ke * dt)
    if math.isclose(dlo, dhi, rel_tol=0.0, abs_tol=1e-15):
        return 0.5
    weight = (deff - dhi) / (dlo - dhi)
    if weight < -2e-13 or weight > 1.0 + 2e-13:
        raise ValueError("effective attenuation is outside the two-mode convex hull")
    return min(1.0, max(0.0, weight))
