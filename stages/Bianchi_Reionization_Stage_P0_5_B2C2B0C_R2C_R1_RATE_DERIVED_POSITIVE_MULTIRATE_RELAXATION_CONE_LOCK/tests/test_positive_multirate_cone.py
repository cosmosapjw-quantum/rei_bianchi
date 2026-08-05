from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

from positive_multirate_cone import (  # noqa: E402
    FAMILY_ORDER,
    build_equilibrium_problem,
    certify_exponential_slack,
    one_mode_equilibrium,
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
