"""RED 1 — owner conservation.

Two properties are asserted here, both of them ownership statements rather than
numerical tolerances:

    sum_o N_gamma,g,o^abs = N_gamma,g^abs,tot
    S_resolved[EFFECTIVE_HI_SUBGRID] = (S_H, S_He, S_U) = (0, 0, 0)   exactly

The second is exact zero, not "small". A test that accepted 1e-30 there would
pass for an implementation that leaked subgrid absorption into resolved
chemistry at a level no auditor would ever notice, which is exactly the defect
R1B-R2A was created to remove.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).parents[1] / "analysis/owner_conservation.py"


def _load():
    spec = importlib.util.spec_from_file_location("r2b_owner_conservation", MODULE)
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolves string annotations via sys.modules, so the module
    # must be registered before exec_module runs the @dataclass decorator.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_absorbed_counts_sum_exactly_to_the_group_total():
    m = _load()
    owner_currents = {
        "EFFECTIVE_HI_SUBGRID": 4.0e49,
        "RESOLVED_HI": 3.0e50,
        "RESOLVED_HeI": 8.0e49,
        "RESOLVED_HeII": 2.5e48,
    }
    total_current = sum(owner_currents.values())
    dt_seconds = 6.4e14

    counts = m.absorbed_counts_by_owner(
        owner_currents=owner_currents, dt_seconds=dt_seconds
    )
    total = m.absorbed_count_total(
        total_current=total_current, dt_seconds=dt_seconds
    )

    assert m.owner_counts_close(counts, total)
    assert set(counts) == set(owner_currents)


def test_subgrid_owner_has_exactly_zero_resolved_sources():
    m = _load()
    sources = m.resolved_sources_for_owner(
        owner="EFFECTIVE_HI_SUBGRID", absorbed_count=7.3e49
    )

    assert sources.resolved_H == 0.0
    assert sources.resolved_He == 0.0
    assert sources.resolved_U == 0.0
    # Exact zero, not merely small: reject any nonzero float whatsoever.
    assert sources.resolved_H == 0 and not sources.resolved_H
    assert sources.resolved_He == 0 and not sources.resolved_He
    assert sources.resolved_U == 0 and not sources.resolved_U


def test_resolved_hi_owner_sources_hydrogen_but_not_helium():
    m = _load()
    sources = m.resolved_sources_for_owner(
        owner="RESOLVED_HI", absorbed_count=5.0e49
    )

    assert sources.resolved_H == pytest.approx(5.0e49, rel=0.0, abs=0.0)
    assert sources.resolved_He == 0.0


def test_conservation_rejects_a_leaking_owner_decomposition():
    m = _load()
    total = m.absorbed_count_total(total_current=1.0e50, dt_seconds=1.0)
    leaking = {
        "EFFECTIVE_HI_SUBGRID": 1.0e49,
        "RESOLVED_HI": 1.0e49,
        "RESOLVED_HeI": 0.0,
        "RESOLVED_HeII": 0.0,
    }

    assert not m.owner_counts_close(leaking, total)


def test_zero_total_gives_exactly_zero_for_every_owner():
    m = _load()
    counts = m.absorbed_counts_by_owner(
        owner_currents={k: 0.0 for k in m.OWNERS}, dt_seconds=1.0e15
    )

    assert all(value == 0.0 for value in counts.values())


def test_negative_or_nonfinite_current_fails_closed():
    m = _load()
    with pytest.raises(ValueError):
        m.absorbed_counts_by_owner(
            owner_currents={"RESOLVED_HI": -1.0}, dt_seconds=1.0
        )
    with pytest.raises(ValueError):
        m.absorbed_counts_by_owner(
            owner_currents={"RESOLVED_HI": float("nan")}, dt_seconds=1.0
        )


def test_unknown_owner_is_rejected():
    m = _load()
    with pytest.raises(KeyError):
        m.resolved_sources_for_owner(owner="RESOLVED_METALS", absorbed_count=1.0)
