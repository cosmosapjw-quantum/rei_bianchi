"""RED — the ten separate ledgers.

The stage requires these to be kept apart, never summed into one bucket:

    resolved HI absorption / resolved HeI absorption / resolved HeII absorption
    effective subgrid absorption
    boundary, redshift and storage
    resolved photoheating
    unresolved absorbed energy
    cooling / expansion work / mass-transfer work

The separation is the point. Merging unresolved absorbed energy into resolved
photoheating is exactly the double-ownership defect R1B-R2A diagnosed, and it
would be invisible in any single aggregate energy total.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).parents[1] / "analysis/ledgers.py"

EXPECTED = (
    "resolved_HI_absorption",
    "resolved_HeI_absorption",
    "resolved_HeII_absorption",
    "effective_subgrid_absorption",
    "boundary_redshift_storage",
    "resolved_photoheating",
    "unresolved_absorbed_energy",
    "cooling",
    "expansion_work",
    "mass_transfer_work",
)


def _load():
    spec = importlib.util.spec_from_file_location("r2b_ledgers", MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_exactly_the_ten_required_ledgers_exist():
    m = _load()
    assert tuple(m.LEDGER_NAMES) == EXPECTED
    assert len(set(m.LEDGER_NAMES)) == 10


def test_all_ledgers_start_at_zero():
    m = _load()
    ledger = m.LedgerSet()
    assert all(ledger[name] == 0.0 for name in EXPECTED)


def test_posting_to_one_ledger_leaves_the_others_untouched():
    m = _load()
    ledger = m.LedgerSet()
    ledger.post("resolved_HI_absorption", 3.0e49)

    assert ledger["resolved_HI_absorption"] == 3.0e49
    others = [n for n in EXPECTED if n != "resolved_HI_absorption"]
    assert all(ledger[n] == 0.0 for n in others)


def test_subgrid_absorption_never_reaches_resolved_photoheating():
    m = _load()
    ledger = m.LedgerSet()
    ledger.post_owner_absorption(
        owner="EFFECTIVE_HI_SUBGRID", count=5.0e49, absorbed_energy=8.0e59
    )

    assert ledger["effective_subgrid_absorption"] == 5.0e49
    assert ledger["unresolved_absorbed_energy"] == 8.0e59
    assert ledger["resolved_photoheating"] == 0.0
    assert ledger["resolved_HI_absorption"] == 0.0


def test_resolved_hi_absorption_routes_to_resolved_ledgers():
    m = _load()
    ledger = m.LedgerSet()
    ledger.post_owner_absorption(
        owner="RESOLVED_HI", count=2.0e49, absorbed_energy=4.0e59
    )

    assert ledger["resolved_HI_absorption"] == 2.0e49
    assert ledger["resolved_photoheating"] == 4.0e59
    assert ledger["unresolved_absorbed_energy"] == 0.0
    assert ledger["effective_subgrid_absorption"] == 0.0


def test_photon_closure_sums_absorption_ledgers_against_the_group_total():
    m = _load()
    ledger = m.LedgerSet()
    ledger.post_owner_absorption(owner="RESOLVED_HI", count=3.0e49, absorbed_energy=0.0)
    ledger.post_owner_absorption(owner="RESOLVED_HeI", count=1.0e49, absorbed_energy=0.0)
    ledger.post_owner_absorption(owner="RESOLVED_HeII", count=5.0e48, absorbed_energy=0.0)
    ledger.post_owner_absorption(
        owner="EFFECTIVE_HI_SUBGRID", count=2.0e49, absorbed_energy=0.0
    )
    ledger.post("boundary_redshift_storage", 1.0e48)

    assert ledger.photon_total() == pytest.approx(6.6e49, rel=1e-15)


def test_snapshot_is_immutable_against_later_posts():
    m = _load()
    ledger = m.LedgerSet()
    ledger.post("cooling", 1.0)
    snapshot = ledger.snapshot()
    ledger.post("cooling", 2.0)

    assert snapshot["cooling"] == 1.0
    assert ledger["cooling"] == 3.0


def test_unknown_ledger_name_is_rejected():
    m = _load()
    ledger = m.LedgerSet()
    with pytest.raises(KeyError):
        ledger.post("resolved_metal_absorption", 1.0)


def test_nonfinite_post_fails_closed():
    m = _load()
    ledger = m.LedgerSet()
    with pytest.raises(ValueError):
        ledger.post("cooling", float("nan"))
