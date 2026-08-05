from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE / "src"))

from relaxation_operator import (  # noqa: E402
    K_B_ERG_PER_K,
    active_set_digest,
    advance_backward_euler,
    advance_exact,
    equilibrium_certificate,
    extensive_measures,
    infer_constant_equilibrium,
    recover_intensives,
    refinement_convergence,
    relaxation_lambda,
    to_builtin,
)


def test_numpy_scalars_are_recursively_json_serializable() -> None:
    payload = {
        "ok": np.bool_(True),
        "count": np.int64(3),
        "value": np.float64(1.25),
        "array": np.array([1.0, 2.0]),
        "nested": [np.bool_(False)],
    }
    converted = to_builtin(payload)
    assert converted == {
        "ok": True,
        "count": 3,
        "value": 1.25,
        "array": [1.0, 2.0],
        "nested": [False],
    }
    assert json.loads(json.dumps(converted)) == converted


def test_inferred_equilibrium_reaches_the_hard_endpoint_exactly() -> None:
    y0 = np.array([1.0, 3.0, 7.0])
    y1 = np.array([2.0, 2.5, 9.0])
    dt = 12.0
    tau = 10.0
    yeq = infer_constant_equilibrium(y0, y1, dt, tau)
    reached = advance_exact(y0, yeq, dt, tau)
    np.testing.assert_allclose(reached, y1, rtol=2e-15, atol=2e-15)


def test_exact_relaxation_has_the_semigroup_property() -> None:
    y0 = np.array([0.2, 1.5, 9.0])
    yeq = np.array([1.0, 0.5, 4.0])
    tau = 33.0
    direct = advance_exact(y0, yeq, 17.0, tau)
    split = advance_exact(advance_exact(y0, yeq, 5.0, tau), yeq, 12.0, tau)
    np.testing.assert_allclose(split, direct, rtol=2e-15, atol=2e-15)


def test_backward_euler_refinement_converges_to_exact_relaxation() -> None:
    y0 = np.array([1.0, 4.0])
    target = np.array([2.0, 3.0])
    dt = 10.0
    tau = 10.0
    yeq = infer_constant_equilibrium(y0, target, dt, tau)
    exact = advance_exact(y0, yeq, dt, tau)
    errors = []
    for n in (1, 2, 4):
        y = y0.copy()
        for _ in range(n):
            y = advance_backward_euler(y, yeq, dt / n, tau)
        errors.append(float(np.linalg.norm(y - exact)))
    assert errors[2] < errors[1] < errors[0]
    conv = refinement_convergence(errors)
    assert conv["monotone"] is True
    assert conv["observed_order_1_to_2_to_4"] > 0.5


def test_extensive_round_trip_keeps_kb_explicit() -> None:
    mass = np.array([2.0, 3.0])
    x = np.array([0.25, 0.75])
    temperature = np.array([10_000.0, 20_000.0])
    ionized, thermal = extensive_measures(mass, x, temperature)
    np.testing.assert_allclose(ionized, mass * x)
    np.testing.assert_allclose(thermal, 1.5 * K_B_ERG_PER_K * mass * temperature)
    xr, tr = recover_intensives(mass, ionized, thermal)
    np.testing.assert_allclose(xr, x)
    np.testing.assert_allclose(tr, temperature)


def test_equilibrium_certificate_fails_without_clipping_overionized_state() -> None:
    mass = np.array([1.0, 2.0])
    ionized = np.array([1.1, 1.0])
    thermal = 1.5 * K_B_ERG_PER_K * mass * np.array([10_000.0, 10_000.0])
    capacity = np.array([1.0, 1.0])
    currents = np.array([[0.4, 0.2], [0.5, 0.4]])
    cert = equilibrium_certificate(
        mass,
        ionized,
        thermal,
        capacity,
        currents,
        macro_mass_cap=4.0,
        macro_volume_cap=4.0,
    )
    assert cert["pass"] is False
    assert "IONIZED_H_EXCEEDS_H" in cert["violated_constraints"]
    assert ionized[0] == pytest.approx(1.1)  # no clipping/mutation


def test_equilibrium_certificate_passes_physical_state() -> None:
    mass = np.array([1.0, 2.0])
    ionized = np.array([0.8, 1.7])
    thermal = 1.5 * K_B_ERG_PER_K * mass * np.array([10_000.0, 20_000.0])
    capacity = np.array([1.0, 2.0])
    currents = np.array([[0.4, 0.2], [0.5, 0.4]])
    cert = equilibrium_certificate(
        mass,
        ionized,
        thermal,
        capacity,
        currents,
        macro_mass_cap=4.0,
        macro_volume_cap=4.0,
    )
    assert cert["pass"] is True
    assert cert["violated_constraints"] == []


def test_active_set_digest_is_deterministic_and_order_sensitive() -> None:
    indices = np.array([1, 4, 9], dtype=np.int64)
    expected = hashlib.sha256(indices.astype("<i8").tobytes()).hexdigest()
    assert active_set_digest(indices) == expected
    assert active_set_digest(indices[::-1]) != expected


def test_relaxation_lambda_is_stable_for_small_step() -> None:
    value = relaxation_lambda(1.0e-9, 100.0)
    assert value > 0.0
    assert value == pytest.approx(1.0e-11, rel=1e-10)
