from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE / "src"))

from relaxation_audit_core import (  # noqa: E402
    InitialGlobalState,
    NodeEndpoint,
    construct_initial_endpoint,
    infer_endpoint_equilibrium,
    run_refinement,
)


def endpoint(scale: float, x_shift: float = 0.0) -> NodeEndpoint:
    mass = scale * np.array([1.0, 2.0])
    x = np.array([0.70 + x_shift, 0.80 + x_shift])
    temp = np.array([10_000.0, 12_000.0])
    capacity = scale * np.array([1.0, 1.5])
    current = scale * np.array([[0.30, 0.20], [0.45, 0.35]])
    return NodeEndpoint(
        mass=mass,
        x_hii=x,
        temperature_k=temp,
        capacity=capacity,
        current=current,
        phi=np.array([2.0, 3.0]),
        n_h_cm3=np.array([1.0e-4, 2.0e-4]),
        p_mass=np.array([1.0 / 3.0, 2.0 / 3.0]),
        z=6.0,
    )


def test_initial_endpoint_preserves_first_shape_and_global_means() -> None:
    first = endpoint(2.0)
    initial = construct_initial_endpoint(
        first,
        InitialGlobalState(n_h_sink=4.0, x_hii_sink=0.75, temperature_sink_k=11_000.0, z=6.1),
    )
    assert np.isclose(initial.mass.sum(), 4.0)
    assert np.isclose(np.dot(initial.mass, initial.x_hii) / initial.mass.sum(), 0.75)
    assert np.isclose(np.dot(initial.mass, initial.temperature_k) / initial.mass.sum(), 11_000.0)
    np.testing.assert_allclose(initial.mass / initial.mass.sum(), first.mass / first.mass.sum())


def test_feasible_transition_refines_monotonically() -> None:
    previous = endpoint(1.0)
    target = endpoint(1.05, x_shift=0.01)
    dt = 5.0
    tau = 10.0
    equilibrium, certificate = infer_endpoint_equilibrium(
        previous,
        target,
        dt_myr=dt,
        tau_myr=tau,
        macro_mass_cap=10.0,
        macro_volume_cap=10.0,
    )
    assert certificate["pass"] is True
    errors = []
    for refinement in (1, 2, 4):
        result = run_refinement(
            previous,
            target,
            equilibrium,
            dt_myr=dt,
            tau_myr=tau,
            refinement=refinement,
            interval_index=0,
            substep=1,
            macro_index=0,
            shape_lane="TEST",
        )
        assert result["pass"] is True
        assert len(result["substeps"]) == refinement
        errors.append(result["final_errors"]["combined_extensive_l1_relative"])
    assert errors[2] < errors[1] < errors[0]


def test_infeasible_equilibrium_is_not_run_or_clipped() -> None:
    previous = endpoint(1.0)
    target = endpoint(5.0)
    equilibrium, certificate = infer_endpoint_equilibrium(
        previous,
        target,
        dt_myr=1.0,
        tau_myr=100.0,
        macro_mass_cap=6.0,
        macro_volume_cap=6.0,
    )
    assert certificate["pass"] is False
    assert "MACRO_MASS_CAP_EXCEEDED" in certificate["violated_constraints"]
    assert equilibrium.mass.sum() > 6.0


def test_initial_endpoint_projects_current_into_scaled_capacity_cone() -> None:
    first = NodeEndpoint(
        mass=np.array([2.0, 2.0]),
        x_hii=np.array([0.8, 0.8]),
        temperature_k=np.array([10_000.0, 10_000.0]),
        capacity=np.array([2.0, 4.0]),
        current=np.array([[1.7, 0.5], [0.5, 0.5]]),
        phi=np.array([2.0, 3.0]),
        n_h_cm3=np.array([1.0e-4, 1.0e-4]),
        p_mass=np.array([0.5, 0.5]),
        z=6.0,
    )
    expected_totals = first.current.sum(axis=0)
    initial = construct_initial_endpoint(
        first,
        InitialGlobalState(n_h_sink=3.0, x_hii_sink=0.8, temperature_sink_k=10_000.0, z=6.1),
        nodes_per_macro=2,
    )
    np.testing.assert_allclose(initial.current.sum(axis=0), expected_totals, rtol=1e-12, atol=1e-12)
    assert np.all(initial.current.sum(axis=1) <= initial.capacity + 1e-12)
    assert initial.construction_certificate is not None
    assert initial.construction_certificate["pass"] is True
    assert initial.construction_certificate["preprojection_negative_row_count"] == 1
    assert initial.construction_certificate["postprojection_negative_row_count"] == 0
