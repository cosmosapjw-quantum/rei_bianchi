from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

STAGE = Path(__file__).resolve().parents[1]


def _load(stem: str):
    name = f"r2b_r2_{stem}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, STAGE / "analysis" / f"{stem}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _parent(micro, n=4):
    NH = np.geomspace(1e57, 1e60, n)
    NHe = 0.079 * NH
    return micro.MaterialBatch.from_fractions(
        N_H=NH,
        N_He=NHe,
        x_HII=np.linspace(0.2, 0.99, n),
        x_HeI=np.full(n, 0.2),
        x_HeII=np.full(n, 0.7),
        x_HeIII=np.full(n, 0.1),
        T_K=np.linspace(8e3, 2e4, n),
    )


def test_linearized_implicit_event_step_preserves_nuclei_and_positive_cone():
    micro = _load("microphysics")
    parent = _parent(micro)
    volume = np.geomspace(1e64, 1e67, parent.size)
    photo = micro.PhotoInputs(
        HI=np.geomspace(1e35, 1e42, parent.size),
        HeI=np.geomspace(1e34, 1e41, parent.size),
        HeII=np.geomspace(1e33, 1e40, parent.size),
        heating_erg_s=np.geomspace(1e25, 1e32, parent.size),
    )
    updated = micro.linearly_implicit_update(
        parent=parent,
        coefficient_state=parent,
        proper_volume_cm3=volume,
        photo=photo,
        hubble_s_inv=2e-17,
        dt_seconds=1e8,
    )
    assert updated.feasible.all()
    assert np.all(updated.state.N_HI > 0.0)
    assert np.all(updated.state.N_HeI > 0.0)
    assert updated.state.N_HI + updated.state.N_HII == pytest.approx(parent.N_H, rel=2e-14)
    assert updated.state.N_HeI + updated.state.N_HeII + updated.state.N_HeIII == pytest.approx(
        parent.N_He, rel=2e-14
    )


def test_transaction_rejection_and_rollback_are_byte_identical():
    micro = _load("microphysics")
    transaction = _load("transaction")
    history = transaction.AcceptedHistory(state=_parent(micro), ledgers={"photon": 1.0})
    before = history.serialize()
    with pytest.raises(transaction.StepRejected):
        with history.attempt("deliberate") as scratch:
            scratch.ledgers["photon"] += 7.0
            scratch.state = _parent(micro)
            raise transaction.StepRejected("DELIBERATE_FAILURE", {"node": 2})
    assert history.serialize() == before
    assert history.failed_attempts[-1]["classification"] == "DELIBERATE_FAILURE"
    assert history.failed_attempts[-1]["rolled_back"] is True


def test_successful_transaction_commits_exactly_once_and_restart_is_identical():
    micro = _load("microphysics")
    transaction = _load("transaction")
    history = transaction.AcceptedHistory(state=_parent(micro), ledgers={"photon": 0.0})
    with history.attempt("good") as scratch:
        scratch.ledgers["photon"] = 3.0
    first = history.serialize()
    assert history.commit_count == 1
    payload = history.restart_payload()
    restored = transaction.AcceptedHistory.from_restart_payload(payload)
    assert restored.serialize() == first
    assert restored.commit_count == history.commit_count
    with pytest.raises(transaction.DuplicateCommit):
        history.commit_candidate(history.last_committed_candidate)


def test_picard_fixed_point_converges_with_state_dependent_photo_law():
    micro = _load("microphysics")
    fixed = _load("fixed_point")
    parent = _parent(micro)
    volume = np.geomspace(1e64, 1e67, parent.size)

    def photo_law(state):
        neutral = state.N_HI / state.N_H
        hei = state.N_HeI / state.N_He
        return micro.PhotoInputs(
            HI=2e41 * neutral / neutral.sum(),
            HeI=5e40 * hei / hei.sum(),
            HeII=np.zeros(state.size),
            heating_erg_s=np.full(state.size, 1e30),
        )

    result = fixed.solve_picard_step(
        parent=parent,
        proper_volume_cm3=volume,
        photo_law=photo_law,
        hubble_s_inv=2e-17,
        dt_seconds=5e9,
        tolerance=1e-9,
        max_iterations=40,
    )
    assert result.converged
    assert result.iterations >= 2
    assert result.residual <= 1e-9
    assert np.all(result.state.N_HI >= 0.0)
    assert result.state.N_HI + result.state.N_HII == pytest.approx(parent.N_H, rel=3e-13)


def test_picard_nonconvergence_preserves_parent_and_earliest_certificate():
    micro = _load("microphysics")
    fixed = _load("fixed_point")
    transaction = _load("transaction")
    parent = _parent(micro)
    history = transaction.AcceptedHistory(state=parent, ledgers={"resolved": 0.0})
    before = history.serialize()
    flip = {"n": 0}

    def oscillating(state):
        flip["n"] += 1
        amount = 1e43 if flip["n"] % 2 else 1e35
        return micro.PhotoInputs(
            HI=np.full(state.size, amount),
            HeI=np.zeros(state.size),
            HeII=np.zeros(state.size),
            heating_erg_s=np.zeros(state.size),
        )

    with pytest.raises(transaction.StepRejected) as exc:
        fixed.advance_transactionally(
            history=history,
            proper_volume_cm3=np.geomspace(1e64, 1e67, parent.size),
            photo_law=oscillating,
            hubble_s_inv=2e-17,
            dt_seconds=1e12,
            tolerance=1e-12,
            max_iterations=4,
        )
    assert history.serialize() == before
    assert exc.value.classification in {"FIXED_POINT_NONCONVERGENCE", "MATERIAL_CAPACITY", "THERMAL_CONE"}
    assert history.failed_attempts[0]["classification"] == exc.value.classification


def test_large_expansion_step_uses_positive_implicit_thermal_root():
    micro = _load("microphysics")
    parent = _parent(micro)
    volume = np.full(parent.size, 1.0e120)
    photo = micro.PhotoInputs.zeros(parent.size)
    updated = micro.linearly_implicit_update(
        parent=parent,
        coefficient_state=parent,
        proper_volume_cm3=volume,
        photo=photo,
        hubble_s_inv=1.0e-16,
        dt_seconds=1.0e17,
    )
    assert updated.feasible.all()
    assert np.all(updated.state.U_resolved > 0.0)
    assert np.all(updated.state.T_K > 0.0)
    assert np.max(updated.thermal_balance_relative_residual) < 1.0e-10
    # In the vanishing-density limit the exact implicit expansion-only result is
    # T_{n+1}=T_n/(1+2 H dt), since U=(3/2) N k_B T.
    expected = parent.T_K / (1.0 + 2.0 * 1.0e-16 * 1.0e17)
    assert updated.state.T_K == pytest.approx(expected, rel=2.0e-8)
