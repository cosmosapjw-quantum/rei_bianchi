"""RED 4 — the minimal GREEN slab loop and the refinement matrix.

Each slab iterates

    owner-correct averaged opacity
      -> photon-conserving absorbed counts
      -> positive implicit H/He update
      -> resolved thermal update

to a fixed point, then the same slab is re-run at dt, dt/2, dt/4, dt/8.

The owner-fraction law is *injected*, never invented here. R1B-R1 established
that `kappa = J/Phi` is not a state-derived dynamic-opacity law and the input
lock forbids inverting it, so a fraction law authored inside this module would
be exactly the fabrication the lock prohibits. A constant law is the autonomous
special case; a state-dependent law supplied by the caller is what makes the
iteration nonautonomous.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ANALYSIS = Path(__file__).parents[1] / "analysis"


def _load(stem, name):
    spec = importlib.util.spec_from_file_location(name, ANALYSIS / f"{stem}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _mods():
    chem = _load("positive_chemistry", "r2b_positive_chemistry")
    txn = _load("transaction", "r2b_transaction")
    slab = _load("slab_fixed_point", "r2b_slab_fixed_point")
    return chem, txn, slab


def _history(chem, txn):
    state = chem.MaterialState(
        N_HI=1.0e6,
        N_HII=4.0e5,
        N_HeI=8.0e4,
        N_HeII=1.5e4,
        N_HeIII=2.0e3,
        U_resolved=0.0,
    )
    return txn.TransactionalHistory(state=state)


CONSTANT_FRACTIONS = {
    "EFFECTIVE_HI_SUBGRID": 0.25,
    "RESOLVED_HI": 0.55,
    "RESOLVED_HeI": 0.15,
    "RESOLVED_HeII": 0.05,
}

ENERGY_PER_ABSORPTION = {
    "EFFECTIVE_HI_SUBGRID": 3.0,
    "RESOLVED_HI": 2.0,
    "RESOLVED_HeI": 4.0,
    "RESOLVED_HeII": 6.0,
}


def test_slab_conserves_photons_across_owners():
    chem, txn, slab = _mods()
    history = _history(chem, txn)

    result = slab.run_slab(
        history=history,
        total_current=1.0e3,
        dt_seconds=100.0,
        owner_fraction_law=lambda state: dict(CONSTANT_FRACTIONS),
        energy_per_absorption=ENERGY_PER_ABSORPTION,
    )

    assert result.converged
    assert history.ledger.photon_total() == pytest.approx(1.0e5, rel=1e-14)
    assert result.photon_relative_residual < 1e-14


def test_subgrid_absorption_moves_no_resolved_material():
    chem, txn, slab = _mods()
    history = _history(chem, txn)
    before_state = history.state

    slab.run_slab(
        history=history,
        total_current=1.0e3,
        dt_seconds=100.0,
        owner_fraction_law=lambda state: {
            "EFFECTIVE_HI_SUBGRID": 1.0,
            "RESOLVED_HI": 0.0,
            "RESOLVED_HeI": 0.0,
            "RESOLVED_HeII": 0.0,
        },
        energy_per_absorption=ENERGY_PER_ABSORPTION,
    )

    assert history.state.N_HI == before_state.N_HI
    assert history.state.N_HeI == before_state.N_HeI
    assert history.state.U_resolved == 0.0
    assert history.ledger["effective_subgrid_absorption"] == pytest.approx(1.0e5)
    assert history.ledger["unresolved_absorbed_energy"] == pytest.approx(3.0e5)
    assert history.ledger["resolved_photoheating"] == 0.0


def test_state_dependent_law_reaches_a_fixed_point():
    chem, txn, slab = _mods()
    history = _history(chem, txn)

    def law(state):
        # Neutral-fraction weighted: nonautonomous, supplied by the caller.
        f = state.N_HI / state.N_H
        return {
            "EFFECTIVE_HI_SUBGRID": 0.25,
            "RESOLVED_HI": 0.55 * f,
            "RESOLVED_HeI": 0.15,
            "RESOLVED_HeII": 0.05 + 0.55 * (1.0 - f),
        }

    result = slab.run_slab(
        history=history,
        total_current=1.0e3,
        dt_seconds=100.0,
        owner_fraction_law=law,
        energy_per_absorption=ENERGY_PER_ABSORPTION,
    )

    assert result.converged
    assert result.iterations >= 2
    assert result.fixed_point_residual <= result.tolerance


def test_nonconvergent_law_is_rejected_and_history_is_byte_identical():
    chem, txn, slab = _mods()
    history = _history(chem, txn)
    before = history.serialize()
    flip = {"n": 0}

    def oscillating(state):
        flip["n"] += 1
        hi = 0.9 if flip["n"] % 2 else 0.1
        return {
            "EFFECTIVE_HI_SUBGRID": 1.0 - hi,
            "RESOLVED_HI": hi,
            "RESOLVED_HeI": 0.0,
            "RESOLVED_HeII": 0.0,
        }

    with pytest.raises(txn.AttemptRejected):
        slab.run_slab(
            history=history,
            total_current=1.0e3,
            dt_seconds=100.0,
            owner_fraction_law=oscillating,
            energy_per_absorption=ENERGY_PER_ABSORPTION,
            max_iterations=6,
        )

    assert history.serialize() == before
    assert history.failed_attempts[-1].rolled_back is True


def test_infeasible_slab_is_rejected_and_history_is_byte_identical():
    """The classified failure must survive the rollback.

    A rejected substep propagates `InfeasibleReaction`, not a flattened
    `AttemptRejected`, so the offending species stays attached to the failure.
    Case-B triage needs to tell an H/He reaction-map fault from a transaction
    fault, and that distinction is lost if every rejection looks the same.
    """
    chem, txn, slab = _mods()
    history = _history(chem, txn)
    before = history.serialize()

    with pytest.raises(chem.InfeasibleReaction) as excinfo:
        slab.run_slab(
            history=history,
            total_current=1.0e9,  # demand far beyond the HI reservoir
            dt_seconds=100.0,
            owner_fraction_law=lambda state: {
                "EFFECTIVE_HI_SUBGRID": 0.0,
                "RESOLVED_HI": 1.0,
                "RESOLVED_HeI": 0.0,
                "RESOLVED_HeII": 0.0,
            },
            energy_per_absorption=ENERGY_PER_ABSORPTION,
        )

    assert history.serialize() == before
    assert excinfo.value.species == "N_HI"
    assert history.failed_attempts[-1].exception_type == "InfeasibleReaction"
    assert history.failed_attempts[-1].rolled_back is True


def test_refinement_matrix_is_budget_additive_over_1_2_4_8():
    chem, txn, slab = _mods()

    report = slab.run_refinement_matrix(
        make_history=lambda: _history(chem, txn),
        total_current=1.0e3,
        dt_seconds=100.0,
        owner_fraction_law=lambda state: dict(CONSTANT_FRACTIONS),
        energy_per_absorption=ENERGY_PER_ABSORPTION,
    )

    assert [row.refinement for row in report.rows] == [1, 2, 4, 8]
    assert all(row.converged for row in report.rows)
    for row in report.rows:
        assert row.photon_total == pytest.approx(1.0e5, rel=1e-12)
    assert report.max_relative_delta <= slab.REFINEMENT_RELATIVE_DELTA


def test_fractions_that_do_not_close_to_unity_fail_closed():
    chem, txn, slab = _mods()
    history = _history(chem, txn)

    with pytest.raises(ValueError):
        slab.run_slab(
            history=history,
            total_current=1.0e3,
            dt_seconds=100.0,
            owner_fraction_law=lambda state: {
                "EFFECTIVE_HI_SUBGRID": 0.3,
                "RESOLVED_HI": 0.3,
                "RESOLVED_HeI": 0.3,
                "RESOLVED_HeII": 0.3,
            },
            energy_per_absorption=ENERGY_PER_ABSORPTION,
        )
