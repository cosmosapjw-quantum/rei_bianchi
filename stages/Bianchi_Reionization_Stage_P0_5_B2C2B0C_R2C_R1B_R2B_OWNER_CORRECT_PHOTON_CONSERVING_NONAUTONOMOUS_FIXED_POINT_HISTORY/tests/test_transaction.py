"""RED 3 — transactional semantics.

After a failed fixed-point attempt, a rejected substep, or an event rollback,
the parent state and the accepted ledger must be **byte-identical** to what
they were before the attempt started.

Byte equality is asserted deliberately rather than float equality. A rollback
that restores 1.0000000000000002 where 1.0 stood would satisfy `==` on most
comparisons a reviewer would write, yet it means the failed attempt left a
residue in the accepted history. The stage requires no residue at all.

Failed attempts are preserved, per repository policy: rolling back must not
erase the evidence that the attempt happened.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).parents[1] / "analysis/transaction.py"
CHEM = Path(__file__).parents[1] / "analysis/positive_chemistry.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fixture():
    chem = _load(CHEM, "r2b_positive_chemistry")
    txn_mod = _load(MODULE, "r2b_transaction")
    state = chem.MaterialState(
        N_HI=1.0e6,
        N_HII=4.0e5,
        N_HeI=8.0e4,
        N_HeII=1.5e4,
        N_HeIII=2.0e3,
        U_resolved=3.0e10,
    )
    history = txn_mod.TransactionalHistory(state=state)
    history.ledger.post("resolved_HI_absorption", 7.0e48)
    history.ledger.post("cooling", 1.25e33)
    return txn_mod, chem, history


def test_failed_fixed_point_attempt_leaves_parent_state_byte_identical():
    txn_mod, _chem, history = _fixture()
    before = history.serialize()

    with pytest.raises(txn_mod.AttemptRejected):
        with history.attempt("fixed_point_did_not_converge") as scratch:
            scratch.ledger.post("resolved_HI_absorption", 9.9e49)
            raise txn_mod.AttemptRejected("fixed_point_did_not_converge")

    assert history.serialize() == before


def test_rejected_substep_leaves_accepted_ledger_byte_identical():
    txn_mod, chem, history = _fixture()
    before = history.serialize()

    with pytest.raises(chem.InfeasibleReaction):
        with history.attempt("substep_infeasible") as scratch:
            scratch.state = chem.apply_reaction_map(
                state=scratch.state,
                absorbed_HI=1.0e9,  # far beyond capacity
                absorbed_HeI=0.0,
                absorbed_HeII=0.0,
                recombination_HII_to_HI=0.0,
                recombination_HeII_to_HeI=0.0,
                recombination_HeIII_to_HeII=0.0,
                resolved_heating=0.0,
            )

    assert history.serialize() == before


def test_event_rollback_restores_both_state_and_ledger_byte_identically():
    txn_mod, chem, history = _fixture()
    before = history.serialize()

    with pytest.raises(txn_mod.AttemptRejected):
        with history.attempt("event_rollback") as scratch:
            scratch.state = chem.apply_reaction_map(
                state=scratch.state,
                absorbed_HI=1.0e5,
                absorbed_HeI=1.0e3,
                absorbed_HeII=0.0,
                recombination_HII_to_HI=0.0,
                recombination_HeII_to_HeI=0.0,
                recombination_HeIII_to_HeII=0.0,
                resolved_heating=5.0e8,
            )
            scratch.ledger.post("resolved_photoheating", 5.0e8)
            raise txn_mod.AttemptRejected("event_rollback")

    assert history.serialize() == before


def test_repeated_failures_do_not_accumulate_residue():
    txn_mod, _chem, history = _fixture()
    before = history.serialize()

    for i in range(5):
        with pytest.raises(txn_mod.AttemptRejected):
            with history.attempt(f"attempt_{i}") as scratch:
                scratch.ledger.post("cooling", 1.0e30)
                raise txn_mod.AttemptRejected(f"attempt_{i}")

    assert history.serialize() == before


def test_failed_attempts_are_preserved_not_erased():
    txn_mod, _chem, history = _fixture()

    with pytest.raises(txn_mod.AttemptRejected):
        with history.attempt("kept_for_the_record") as scratch:
            scratch.ledger.post("cooling", 1.0)
            raise txn_mod.AttemptRejected("kept_for_the_record")

    assert len(history.failed_attempts) == 1
    assert history.failed_attempts[0].reason == "kept_for_the_record"
    assert history.failed_attempts[0].rolled_back is True


def test_successful_attempt_commits_and_advances_the_accepted_state():
    txn_mod, chem, history = _fixture()
    before = history.serialize()

    with history.attempt("good_substep") as scratch:
        scratch.state = chem.apply_reaction_map(
            state=scratch.state,
            absorbed_HI=1.0e5,
            absorbed_HeI=0.0,
            absorbed_HeII=0.0,
            recombination_HII_to_HI=0.0,
            recombination_HeII_to_HeI=0.0,
            recombination_HeIII_to_HeII=0.0,
            resolved_heating=2.0e8,
        )
        scratch.ledger.post("resolved_HI_absorption", 1.0e5)

    assert history.serialize() != before
    assert history.state.N_HI == pytest.approx(9.0e5, rel=1e-15)
    assert history.ledger["resolved_HI_absorption"] == pytest.approx(
        7.0e48 + 1.0e5, rel=1e-15
    )
    assert history.failed_attempts == []


def test_commit_after_failure_starts_from_the_parent_not_the_failed_scratch():
    txn_mod, chem, history = _fixture()

    with pytest.raises(txn_mod.AttemptRejected):
        with history.attempt("bad") as scratch:
            scratch.ledger.post("resolved_HI_absorption", 5.0e49)
            raise txn_mod.AttemptRejected("bad")

    with history.attempt("good") as scratch:
        scratch.ledger.post("resolved_HI_absorption", 1.0e5)

    assert history.ledger["resolved_HI_absorption"] == pytest.approx(
        7.0e48 + 1.0e5, rel=1e-15
    )
