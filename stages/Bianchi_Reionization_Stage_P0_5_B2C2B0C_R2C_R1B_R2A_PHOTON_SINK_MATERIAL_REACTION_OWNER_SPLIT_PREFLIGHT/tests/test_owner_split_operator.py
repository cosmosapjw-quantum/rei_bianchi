from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pytest

SCRIPT = Path(__file__).parents[1] / "analysis" / "owner_split_operator.py"
spec = importlib.util.spec_from_file_location("owner_split_operator", SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_competing_hazard_split_closes_opacity_and_current():
    component_kappa = {
        "EFFECTIVE_HI_SUBGRID": 8.0,
        "EXPLICIT_HI_ATOMIC": 1.0,
        "EXPLICIT_HEI_ATOMIC": 1.0,
        "EXPLICIT_HEII_ATOMIC": 0.0,
    }
    rows = module.split_group_by_owner(
        total_kappa=10.0,
        total_current=40.0,
        component_kappa=component_kappa,
    )
    assert all(r.kappa >= 0 and r.current >= 0 for r in rows)
    assert sum(r.kappa for r in rows) == pytest.approx(10.0, rel=0, abs=1e-14)
    assert sum(r.current for r in rows) == pytest.approx(40.0, rel=0, abs=1e-14)
    for row in rows:
        if row.kappa > 0:
            assert row.current / row.kappa == pytest.approx(4.0)


def test_subgrid_owner_has_exact_zero_resolved_sources():
    sources = module.resolved_source_coefficients("EFFECTIVE_HI_SUBGRID")
    assert sources == {
        "resolved_H": 0,
        "resolved_He": 0,
        "resolved_thermal": 0,
    }


def test_unknown_or_negative_owner_input_fails_closed():
    with pytest.raises(KeyError):
        module.resolved_source_coefficients("NOT_A_COMPONENT")
    with pytest.raises(ValueError):
        module.split_group_by_owner(
            total_kappa=1.0,
            total_current=1.0,
            component_kappa={"EFFECTIVE_HI_SUBGRID": -0.1},
        )


def test_capacity_regression_unsplit_fails_owner_split_passes():
    old = module.capacity_certificate(
        assigned_absorption=20.0,
        initial_reservoir=10.0,
        recombination_supply=5.0,
    )
    corrected = module.capacity_certificate(
        assigned_absorption=4.0,
        initial_reservoir=10.0,
        recombination_supply=5.0,
    )
    assert not old.feasible
    assert corrected.feasible
    assert old.overshoot == pytest.approx(5.0)
    assert corrected.slack == pytest.approx(11.0)


def test_node_disintegration_is_nonnegative_and_conservative():
    q = module.disintegrate_owner_current(
        owner_total=7.0,
        measure=np.array([1.0, 2.0, 0.0, 4.0]),
    )
    assert np.all(q >= 0)
    assert q[2] == 0.0
    assert q.sum() == pytest.approx(7.0, abs=1e-14)


def test_conditional_component_normalization_uses_authoritative_total_without_changing_ratios():
    raw = {
        "EFFECTIVE_HI_SUBGRID": 8.0,
        "EXPLICIT_HI_ATOMIC": 1.0,
        "EXPLICIT_HEI_ATOMIC": 1.0,
        "EXPLICIT_HEII_ATOMIC": 0.0,
    }
    conditioned = module.condition_component_opacities(
        authoritative_total_kappa=12.0,
        raw_component_kappa=raw,
    )
    assert sum(conditioned.values()) == pytest.approx(12.0, rel=0, abs=1e-14)
    assert conditioned["EFFECTIVE_HI_SUBGRID"] / conditioned["EXPLICIT_HI_ATOMIC"] == pytest.approx(8.0)
    assert conditioned["EXPLICIT_HEI_ATOMIC"] / conditioned["EXPLICIT_HI_ATOMIC"] == pytest.approx(1.0)
    assert conditioned["EXPLICIT_HEII_ATOMIC"] == 0.0


def test_conditional_component_normalization_rejects_nonzero_target_on_zero_support():
    with pytest.raises(ValueError, match="zero raw component support"):
        module.condition_component_opacities(
            authoritative_total_kappa=1.0,
            raw_component_kappa={name: 0.0 for name in module.COMPONENT_OWNER},
        )
