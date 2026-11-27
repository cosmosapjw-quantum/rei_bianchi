"""Analytic proper-time controls for the independent adaptive reference."""

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from reference import solve_reference


class SourceLawModel:
    """H=1/(1+t), dN/dln(a)=s, and a=1+t in normalized seconds."""

    scale = np.array([0.1])
    t_end = 2.0
    breakpoints = ()

    def initial_state(self):
        return np.array([0.0])

    def rhs(self, t, y):
        return np.array([0.1 / (1.0 + t)])

    def result(self, y, metadata):
        return y, metadata


@pytest.mark.parametrize("method", ["Radau", "DOP853"])
def test_proper_time_source_law(method):
    y, metadata = solve_reference(SourceLawModel(), method=method)
    assert abs(y[0] - 0.1 * math.log(3.0)) < 2e-11
    assert metadata["segment_count"] == 1
    assert metadata["t_end_s"] == 2.0


class SwitchedAbsorber:
    """A scalar continuous-birth photon with a discontinuous source at t=0.3."""

    scale = np.array([0.01, 0.1])
    t_end = 0.7
    breakpoints = (0.3,)

    def __init__(self):
        self.active_source = None
        self.intervals = []

    def set_interval(self, left, right):
        self.intervals.append((left, right))
        self.active_source = 0.02 if (left + right) / 2 < 0.3 else 0.0

    def initial_state(self):
        return np.zeros(2)

    def rhs(self, t, y):
        absorbed = 4.0 * y[0]
        return np.array([self.active_source - absorbed, absorbed])

    def jac(self, t, y):
        return sparse.csr_matrix([[-4.0, 0.0], [4.0, 0.0]])

    def result(self, y, metadata):
        return y, metadata


@pytest.mark.parametrize("method", ["Radau", "DOP853"])
def test_source_switch_and_number_ledger(method):
    model = SwitchedAbsorber()
    y, metadata = solve_reference(model, method=method)
    n_at_switch = 0.02 * (-math.expm1(-4.0 * 0.3)) / 4.0
    exact_photons = n_at_switch * math.exp(-4.0 * 0.4)
    assert abs(y[0] - exact_photons) < 2e-10
    assert abs(y.sum() - 0.02 * 0.3) < 2e-10
    assert metadata["segment_count"] == 2
    assert model.intervals == [(0.0, 0.3), (0.3, 0.7)]
    if method == "Radau":
        assert metadata["njev"] > 0


def test_bad_breakpoint_rejected():
    model = SourceLawModel()
    model.breakpoints = (2.0,)
    with pytest.raises(ValueError, match="strictly inside"):
        solve_reference(model)
