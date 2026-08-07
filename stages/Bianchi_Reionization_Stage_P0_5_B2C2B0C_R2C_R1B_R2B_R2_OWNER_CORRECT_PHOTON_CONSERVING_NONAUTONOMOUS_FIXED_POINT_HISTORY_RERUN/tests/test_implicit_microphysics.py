from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
import sys

import numpy as np
import pytest

STAGE = Path(__file__).resolve().parents[1]


def _load(stem: str):
    name = f"r2b_r2_{stem}"
    spec = importlib.util.spec_from_file_location(name, STAGE / "analysis" / f"{stem}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _parent(micro, n: int = 3):
    NH = np.array([1.0e60, 2.0e60, 8.0e59])[:n]
    NHe = 0.079 * NH
    xh = np.array([0.999, 0.7, 0.1])[:n]
    he = np.array([[1e-4, 0.998, 0.0019], [0.2, 0.7, 0.1], [0.9, 0.09, 0.01]])[:n]
    T = np.array([1.4e4, 2.0e4, 8.0e3])[:n]
    return micro.MaterialBatch.from_fractions(
        N_H=NH,
        N_He=NHe,
        x_HII=xh,
        x_HeI=he[:, 0],
        x_HeII=he[:, 1],
        x_HeIII=he[:, 2],
        T_K=T,
    )


def test_coordinate_roundtrip_preserves_positive_material_state_and_nuclei():
    micro = _load("microphysics")
    parent = _parent(micro)
    q = micro.state_to_coordinates(parent)
    decoded = micro.coordinates_to_state(q, N_H=parent.N_H, N_He=parent.N_He)

    for name in ("N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII", "U_resolved", "T_K"):
        assert np.asarray(getattr(decoded, name)) == pytest.approx(
            np.asarray(getattr(parent, name)), rel=2e-13, abs=1e-280
        )
    assert np.all(decoded.N_HI > 0.0)
    assert np.all(decoded.N_HeI > 0.0)
    assert decoded.N_HI + decoded.N_HII == pytest.approx(parent.N_H, rel=2e-15)
    assert decoded.N_HeI + decoded.N_HeII + decoded.N_HeIII == pytest.approx(parent.N_He, rel=2e-15)


def test_full_ots_event_rhs_conserves_hydrogen_and_helium_nuclei():
    micro = _load("microphysics")
    parent = _parent(micro)
    volume = np.array([1e67, 2e67, 8e66])
    photo = micro.PhotoInputs(
        HI=np.array([1e45, 2e45, 3e44]),
        HeI=np.array([2e44, 3e44, 1e44]),
        HeII=np.array([1e43, 2e43, 3e42]),
        heating_erg_s=np.zeros(3),
    )
    dpop = micro.full_ots_population_rhs(parent, proper_volume_cm3=volume, photo=photo)
    assert dpop.shape == (3, 5)
    assert dpop[:, 0] + dpop[:, 1] == pytest.approx(np.zeros(3), rel=0.0, abs=1e30)
    assert dpop[:, 2] + dpop[:, 3] + dpop[:, 4] == pytest.approx(
        np.zeros(3), rel=0.0, abs=1e30
    )


def test_implicit_identity_at_zero_duration_is_exact_to_roundoff():
    micro = _load("microphysics")
    implicit = _load("implicit_step")
    parent = _parent(micro)
    volume = np.array([1e67, 2e67, 8e66])
    photo = micro.PhotoInputs.zeros(3)
    result = implicit.solve_implicit_batch(
        parent=parent,
        proper_volume_cm3=volume,
        photo=photo,
        redshift=6.0,
        hubble_s_inv=2.0e-17,
        dt_seconds=0.0,
    )
    assert result.converged.all()
    assert result.max_residual < 2e-13
    for name in ("N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII", "U_resolved"):
        assert np.asarray(getattr(result.state, name)) == pytest.approx(
            np.asarray(getattr(parent, name)), rel=2e-13, abs=1e-250
        )


def test_neutral_zero_electron_null_lane_remains_stationary_without_expansion():
    micro = _load("microphysics")
    implicit = _load("implicit_step")
    parent = micro.MaterialBatch.from_fractions(
        N_H=np.array([1e60]),
        N_He=np.array([7.9e58]),
        x_HII=np.array([1e-12]),
        x_HeI=np.array([1.0 - 2e-12]),
        x_HeII=np.array([1e-12]),
        x_HeIII=np.array([1e-12]),
        T_K=np.array([100.0]),
    )
    result = implicit.solve_implicit_batch(
        parent=parent,
        proper_volume_cm3=np.array([1e67]),
        photo=micro.PhotoInputs.zeros(1),
        redshift=6.0,
        hubble_s_inv=0.0,
        dt_seconds=1e10,
    )
    assert result.converged[0]
    assert result.state.N_HII[0] == pytest.approx(parent.N_HII[0], rel=2e-9, abs=1e15)
    assert result.state.N_HeII[0] == pytest.approx(parent.N_HeII[0], rel=2e-9, abs=1e15)


def test_resolved_heating_is_the_only_external_thermal_source():
    micro = _load("microphysics")
    implicit = _load("implicit_step")
    parent = micro.MaterialBatch.from_fractions(
        N_H=np.array([1e60]),
        N_He=np.array([7.9e58]),
        x_HII=np.array([1e-12]),
        x_HeI=np.array([1.0 - 2e-12]),
        x_HeII=np.array([1e-12]),
        x_HeIII=np.array([1e-12]),
        T_K=np.array([100.0]),
    )
    dt = 1e5
    heating = 3.0e40
    result = implicit.solve_implicit_batch(
        parent=parent,
        proper_volume_cm3=np.array([1e67]),
        photo=micro.PhotoInputs(
            HI=np.zeros(1), HeI=np.zeros(1), HeII=np.zeros(1),
            heating_erg_s=np.array([heating]),
        ),
        redshift=6.0,
        hubble_s_inv=0.0,
        dt_seconds=dt,
    )
    assert result.converged[0]
    assert result.state.U_resolved[0] - parent.U_resolved[0] == pytest.approx(
        heating * dt, rel=3e-8
    )
    assert "subgrid" not in inspect.signature(micro.PhotoInputs).parameters


def test_analytic_jacobian_matches_central_difference_on_regular_state():
    micro = _load("microphysics")
    implicit = _load("implicit_step")
    parent = _parent(micro, n=1)
    volume = np.array([1e67])
    photo = micro.PhotoInputs(
        HI=np.array([1e44]), HeI=np.array([2e43]), HeII=np.array([1e42]),
        heating_erg_s=np.array([5e31]),
    )
    context = implicit.make_context(
        parent=parent,
        proper_volume_cm3=volume,
        photo=photo,
        redshift=5.95,
        hubble_s_inv=2.3e-17,
        dt_seconds=2e12,
    )
    q = micro.state_to_coordinates(parent)[0] + np.array([-0.05, 0.02, -0.01, 0.03])
    analytic = implicit.scalar_jacobian(q, context, index=0)
    numeric = np.empty((4, 4))
    for j in range(4):
        h = 2e-6 * max(1.0, abs(q[j]))
        dq = np.zeros(4); dq[j] = h
        numeric[:, j] = (
            implicit.scalar_residual(q + dq, context, index=0)
            - implicit.scalar_residual(q - dq, context, index=0)
        ) / (2*h)
    scale = max(np.linalg.norm(analytic), np.linalg.norm(numeric), 1.0)
    assert np.linalg.norm(analytic - numeric) / scale < 2e-6


def test_infeasible_or_nonconverged_nodes_return_certificates_not_clipped_states():
    micro = _load("microphysics")
    implicit = _load("implicit_step")
    parent = _parent(micro, n=1)
    result = implicit.solve_implicit_batch(
        parent=parent,
        proper_volume_cm3=np.array([1e67]),
        photo=micro.PhotoInputs(
            HI=np.array([1e100]), HeI=np.zeros(1), HeII=np.zeros(1),
            heating_erg_s=np.zeros(1),
        ),
        redshift=6.0,
        hubble_s_inv=2e-17,
        dt_seconds=1e15,
        max_newton_iterations=2,
        enable_fallback=False,
    )
    assert not result.converged[0]
    assert result.certificates[0]["classification"] in {
        "NEWTON_NONCONVERGENCE", "NONFINITE_RESIDUAL", "MATERIAL_CAPACITY"
    }
    assert result.state is None or np.all(result.state.N_HI >= 0.0)
