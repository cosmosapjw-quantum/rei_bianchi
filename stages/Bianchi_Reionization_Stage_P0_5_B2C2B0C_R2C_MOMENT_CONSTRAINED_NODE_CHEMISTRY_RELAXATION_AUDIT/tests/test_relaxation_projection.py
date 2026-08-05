from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE / "src"))

from relaxation_operator import project_currents  # noqa: E402


def test_current_projection_preserves_group_totals_and_row_caps() -> None:
    prior = np.array([[0.9, 0.7], [0.1, 0.3]], dtype=float)
    totals = np.array([1.0, 1.0])
    capacities = np.array([1.0, 1.2])
    projected, cert = project_currents(prior, totals, capacities)
    np.testing.assert_allclose(projected.sum(axis=0), totals, rtol=1e-12, atol=1e-12)
    assert np.all(projected.sum(axis=1) <= capacities + 1e-12)
    assert cert["pass"] is True
    assert cert["active_set_sha256"]


def test_current_projection_returns_dual_infeasibility_certificate() -> None:
    prior = np.ones((2, 2))
    totals = np.array([1.0, 1.0])
    capacities = np.array([0.4, 0.4])
    projected, cert = project_currents(prior, totals, capacities)
    assert projected is None
    assert cert["pass"] is False
    assert cert["certificate_type"] == "TOTAL_CAPACITY_DEFICIT"
    assert cert["deficit"] > 0.0


def test_projection_reports_scale_free_capacity_violation() -> None:
    scale = 1.0e49
    prior = scale * np.array([[0.9, 0.7], [0.1, 0.3]], dtype=float)
    totals = scale * np.array([1.0, 1.0])
    capacities = scale * np.array([1.0, 1.2])
    projected, cert = project_currents(prior, totals, capacities)
    assert projected is not None
    assert cert["pass"] is True
    assert "max_capacity_relative_violation" in cert
    assert cert["max_capacity_relative_violation"] <= 2.0e-11
