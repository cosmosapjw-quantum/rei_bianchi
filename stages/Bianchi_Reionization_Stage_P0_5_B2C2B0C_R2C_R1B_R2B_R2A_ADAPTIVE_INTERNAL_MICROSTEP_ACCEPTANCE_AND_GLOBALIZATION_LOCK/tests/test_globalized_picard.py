from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np

STAGE = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _mods():
    tensor = _load("r2b_r2a_tensorized_picard", STAGE / "analysis/tensorized_inputs.py")
    picard = _load("r2b_r2a_globalized_picard", STAGE / "analysis/globalized_picard.py")
    return tensor, picard


def _state(tensor, x_hii: float = 0.2):
    nh = np.array([1.0, 2.0, 3.0])
    nhe = 0.079 * nh
    values = np.zeros((6, 3), dtype=float)
    values[0] = nh * (1.0 - x_hii)
    values[1] = nh * x_hii
    values[2] = nhe * 0.9
    values[3] = nhe * 0.09
    values[4] = nhe - values[2] - values[3]
    temperature = np.array([5000.0, 6000.0, 7000.0])
    particles = nh + nhe + values[1] + values[3] + 2.0 * values[4]
    values[5] = 1.5 * picard_kb() * particles * temperature
    return tensor.ArrayState(values, temperature)


def picard_kb():
    return 1.380649e-16


def _mapped_state(tensor, parent, x_hii):
    values = parent.values.copy()
    nh = values[0] + values[1]
    values[1] = nh * x_hii
    values[0] = nh - values[1]
    particles = nh + values[2] + values[3] + values[4] + values[1] + values[3] + 2.0 * values[4]
    values[5] = 1.5 * picard_kb() * particles * parent.temperature_K
    return tensor.ArrayState(values, parent.temperature_K.copy())


def test_largest_cone_safe_sufficient_decrease_damping_is_selected():
    tensor, picard = _mods()
    parent = _state(tensor, 0.2)

    def map_state(iterate):
        x = float(np.mean(iterate.values[1] / (iterate.values[0] + iterate.values[1])))
        x_new = 0.5 - 0.45 * np.tanh(4.0 * (x - 0.5))
        return picard.MapEvaluation(state=_mapped_state(tensor, parent, x_new))

    result = picard.GlobalizedPicard(max_iterations=80).solve(parent=parent, map_state=map_state)
    assert result.converged
    assert result.damping_trace
    assert result.damping_trace[0] < 1.0
    assert all(lam in picard.DAMPING_CANDIDATES for lam in result.damping_trace)
    assert result.residual <= 1.0e-10


def test_no_safe_damping_fails_without_parent_mutation():
    tensor, picard = _mods()
    parent = _state(tensor, 0.2)
    before_values = parent.values.tobytes()
    before_temp = parent.temperature_K.tobytes()

    def always_invalid(_iterate):
        return picard.MapEvaluation(
            state=None,
            feasible=False,
            certificate={"classification": "THERMAL_CONE"},
        )

    result = picard.GlobalizedPicard().solve(parent=parent, map_state=always_invalid)
    assert not result.converged
    assert result.certificate["classification"] == "THERMAL_CONE"
    assert parent.values.tobytes() == before_values
    assert parent.temperature_K.tobytes() == before_temp


def test_nuclei_drift_is_rejected_before_damping():
    tensor, picard = _mods()
    parent = _state(tensor, 0.2)

    def bad_nuclei(_iterate):
        values = parent.values.copy()
        values[0, 0] += 1.0e-5
        return picard.MapEvaluation(state=tensor.ArrayState(values, parent.temperature_K.copy()))

    result = picard.GlobalizedPicard().solve(parent=parent, map_state=bad_nuclei)
    assert not result.converged
    assert result.certificate["classification"] == "OWNER_NUCLEI_GATE"


def test_subgrid_exact_zero_violation_fails_closed():
    tensor, picard = _mods()
    parent = _state(tensor, 0.2)

    result = picard.GlobalizedPicard().solve(
        parent=parent,
        map_state=lambda iterate: picard.MapEvaluation(
            state=iterate,
            structural_zero_ok=False,
            certificate={"classification": "STRUCTURAL_ZERO_VIOLATION"},
        ),
    )
    assert not result.converged
    assert result.certificate["classification"] == "STRUCTURAL_ZERO_VIOLATION"


def test_accepted_candidate_map_is_reused_on_next_iteration():
    tensor, picard = _mods()
    parent = _state(tensor, 0.2)
    calls = {"n": 0}

    def contraction(iterate):
        calls["n"] += 1
        x = float(np.mean(iterate.values[1] / (iterate.values[0] + iterate.values[1])))
        x_new = 0.3 + 0.25 * (x - 0.3)
        return picard.MapEvaluation(state=_mapped_state(tensor, parent, x_new))

    result = picard.GlobalizedPicard(max_iterations=80).solve(
        parent=parent, map_state=contraction
    )
    assert result.converged
    assert result.map_calls == result.iterations
    assert calls["n"] == result.map_calls
