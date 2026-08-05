from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

from positive_multirate_cone import (  # noqa: E402
    FAMILY_ORDER,
    active_set_nnls_kkt_certificate,
    build_equilibrium_problem,
    certify_exponential_slack,
    one_mode_equilibrium,
    relative_kkt_stationarity_residual,
    solve_equilibrium_problem,
    two_mode_weight_for_attenuation,
)


def synthetic_endpoints():
    previous = {
        "M": np.array([6.0, 4.0]),
        "I": np.array([3.0, 2.0]),
        "U": np.array([8.0, 5.0]),
        "C": np.array([5.0, 4.0]),
        "J_G1": np.array([2.0, 1.0]),
        "J_G2a": np.array([1.0, 1.0]),
    }
    target = {
        "M": np.array([6.2, 3.8]),
        "I": np.array([3.1, 1.9]),
        "U": np.array([8.1, 5.1]),
        "C": np.array([5.2, 4.1]),
        "J_G1": np.array([2.1, 1.0]),
        "J_G2a": np.array([1.0, 1.1]),
    }
    bounds = {family: (0.05, 0.5) for family in FAMILY_ORDER}
    return previous, target, bounds


def test_equilibrium_lp_finds_macro_shared_rates() -> None:
    previous, target, bounds = synthetic_endpoints()
    problem = build_equilibrium_problem(
        previous, target, bounds, dt_myr=10.0, macro_mass_cap=20.0, macro_volume_cap=20.0
    )
    result = solve_equilibrium_problem(problem)
    assert result["pass"]
    assert result["node_rate_count"] == 0
    for family, rate in result["rates_Myr_inv"].items():
        assert bounds[family][0] <= rate <= bounds[family][1]
    eq = one_mode_equilibrium(previous, target, result["rates_Myr_inv"], 10.0)
    assert np.min(eq["M"] - eq["I"]) >= -1e-10
    assert np.min(eq["C"] - eq["J_G1"] - eq["J_G2a"]) >= -1e-10


def test_infeasible_box_returns_farkas_certificate() -> None:
    previous, target, bounds = synthetic_endpoints()
    target["J_G1"] = np.array([20.0, 20.0])
    target["J_G2a"] = np.array([20.0, 20.0])
    target["C"] = np.array([1.0, 1.0])
    problem = build_equilibrium_problem(
        previous, target, bounds, dt_myr=10.0, macro_mass_cap=20.0, macro_volume_cap=20.0
    )
    result = solve_equilibrium_problem(problem)
    assert not result["pass"]
    assert result["farkas_certificate"]["pass"]
    assert result["farkas_certificate"]["h_dot_y"] < 0.0


def test_interval_slack_certificate_passes_positive_exponential_sum() -> None:
    cert = certify_exponential_slack(
        constant=np.array([1.0, 2.0]),
        amplitudes=np.array([[0.5, -0.2], [0.2, -0.1]]),
        rates_myr_inv=np.array([0.1, 0.2]),
        dt_myr=10.0,
        relative_tolerance=1e-12,
        max_depth=24,
    )
    assert cert["pass"]
    assert cert["unresolved_interval_count"] == 0


def test_interval_slack_certificate_fails_real_negative_region() -> None:
    cert = certify_exponential_slack(
        constant=np.array([-1.0]),
        amplitudes=np.array([[0.0]]),
        rates_myr_inv=np.array([0.1]),
        dt_myr=10.0,
        relative_tolerance=1e-12,
        max_depth=8,
    )
    assert not cert["pass"]
    assert cert["minimum_sampled_slack"] < 0.0


def test_two_mode_weight_reproduces_locked_attenuation() -> None:
    dt = 10.0
    k_eff = 0.2
    k_lo = 0.05
    k_hi = 0.5
    weight = two_mode_weight_for_attenuation(k_eff, k_lo, k_hi, dt)
    target_decay = math.exp(-k_eff * dt)
    mixture = weight * math.exp(-k_lo * dt) + (1.0 - weight) * math.exp(-k_hi * dt)
    assert 0.0 <= weight <= 1.0
    assert math.isclose(mixture, target_decay, rel_tol=2e-15, abs_tol=2e-15)


def test_solver_uses_physical_row_scaling_for_wide_rate_boxes() -> None:
    previous = {
        "M": np.array([10.0]),
        "I": np.array([5.0]),
        "U": np.array([1.0]),
        "C": np.array([1.0]),
        "J_G1": np.array([0.4]),
        "J_G2a": np.array([0.4]),
    }
    target = {
        "M": np.array([10.0]),
        "I": np.array([5.0]),
        "U": np.array([1.0]),
        "C": np.array([1.1]),
        "J_G1": np.array([0.42]),
        "J_G2a": np.array([0.42]),
    }
    bounds = {
        "M": (0.1, 0.2),
        "I": (0.1, 0.2),
        "U": (0.1, 0.2),
        "C": (1.0e-4, 2.0),
        "J_G1": (1.0e-16, 1.0e-2),
        "J_G2a": (1.0e-16, 1.0e-2),
    }
    result = solve_equilibrium_problem(
        build_equilibrium_problem(
            previous,
            target,
            bounds,
            dt_myr=10.0,
            macro_mass_cap=20.0,
            macro_volume_cap=20.0,
        )
    )
    assert result["pass"]
    eq = one_mode_equilibrium(previous, target, result["rates_Myr_inv"], 10.0)
    scale = max(
        float(np.sum(np.abs(eq["C"])))
        + float(np.sum(np.abs(eq["J_G1"])))
        + float(np.sum(np.abs(eq["J_G2a"]))),
        1.0,
    )
    assert float(np.min(eq["C"] - eq["J_G1"] - eq["J_G2a"])) >= -1.0e-11 * scale
    assert result["minimum_physical_scaled_primal_slack"] >= -1.0e-11


def test_solver_returns_exact_locked_rate_at_active_boundary() -> None:
    previous, _, _ = synthetic_endpoints()
    target = {family: values.copy() for family, values in previous.items()}
    bounds = {family: (1.0e-4, 2.0) for family in FAMILY_ORDER}
    result = solve_equilibrium_problem(
        build_equilibrium_problem(
            previous,
            target,
            bounds,
            dt_myr=10.0,
            macro_mass_cap=20.0,
            macro_volume_cap=20.0,
        )
    )
    assert result["pass"]
    for family in FAMILY_ORDER:
        assert result["rates_Myr_inv"][family] == bounds[family][1]


def test_solver_reports_correct_kkt_stationarity_signs() -> None:
    previous, target, bounds = synthetic_endpoints()
    result = solve_equilibrium_problem(
        build_equilibrium_problem(
            previous,
            target,
            bounds,
            dt_myr=10.0,
            macro_mass_cap=20.0,
            macro_volume_cap=20.0,
        )
    )
    assert result["pass"]
    assert result["max_stationarity_residual"] <= 1.0e-8
    assert result["max_complementarity_residual"] <= 1.0e-8


def test_relative_kkt_stationarity_accepts_large_dual_cancellation() -> None:
    c = np.array([1.0])
    inequality_term = np.array([0.0])
    lower_marginal = np.array([1.0e11])
    upper_marginal = np.array([-1.0e11 + 1.0 - 1.0e-7])
    residual = relative_kkt_stationarity_residual(
        c, inequality_term, lower_marginal, upper_marginal
    )
    assert residual <= 1.0e-11


def test_active_set_nnls_kkt_certificate_closes_primal_dual_gap() -> None:
    # min x0+x1 subject to x0>=1/2 and 0<=x<=1.
    A_ub = np.array([[-1.0, 0.0]])
    b_ub = np.array([-0.5])
    z = np.array([0.5, 0.0])
    objective = np.ones(2)
    slack = b_ub - A_ub @ z
    cert = active_set_nnls_kkt_certificate(A_ub, b_ub, z, objective, slack)
    assert cert["pass"]
    assert cert["relative_stationarity_residual"] <= 1.0e-11
    assert cert["relative_duality_gap"] <= 1.0e-11
    assert cert["max_complementarity_residual"] <= 1.0e-11
    assert math.isclose(cert["primal_objective"], 0.5, rel_tol=0.0, abs_tol=1.0e-14)
    assert math.isclose(cert["dual_objective"], 0.5, rel_tol=0.0, abs_tol=1.0e-14)
