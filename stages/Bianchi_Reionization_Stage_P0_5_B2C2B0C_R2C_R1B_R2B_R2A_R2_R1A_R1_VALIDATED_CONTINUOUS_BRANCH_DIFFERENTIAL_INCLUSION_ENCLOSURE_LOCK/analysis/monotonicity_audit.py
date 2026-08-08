"""Signed-Jacobian audit for constant diagonal orthant monotonicity.

A constant orthant change of variables multiplies a fixed Jacobian entry
``J_ij`` by one fixed sign ``s_i s_j``.  Therefore, a robust sign reversal of
one off-diagonal entry across two admissible canonical states excludes every
constant diagonal orthant cone.  It does *not* exclude state-dependent or
nonpolyhedral comparison cones.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

LOW_NODE = 12800
HIGH_NODE = 43452
EPSILONS = (1.0e-6, 2.0e-7)
LANE = "LOCAL_NEUTRAL_HAZARD_PRIMARY"
V_POLICY = "CELL_LOWER_STRICT"
F_VALUE = 0.1


def _load(name: str, path: Path) -> Any:
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _modules(repo_root: Path):
    r1a = repo_root / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_FOUR_CORNER_BRANCH_AND_UNRESOLVED_OTS_ENERGY_PROPAGATION_PREFLIGHT"
    r2a = repo_root / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK/analysis"
    trial = _load("r2_r1a_r1_monotonicity_parent_trial", r1a / "analysis/uncertainty_trial.py")
    thermal = _load("r2_r1a_r1_monotonicity_thermal", r2a / "thermal_backends.py")
    return trial, thermal


def _energy_from_temperature(thermal, populations: np.ndarray, temperature: np.ndarray) -> np.ndarray:
    nhi, nhii, nhei, nheii, nheiii = populations.T
    particles = (nhi + nhii) + (nhei + nheii + nheiii) + nhii + nheii + 2.0 * nheiii
    return 1.5 * thermal.KB_ERG * particles * temperature


def _reduced_rhs(solver, thermal, state, point) -> np.ndarray:
    owner = solver._owner(state, point)
    event, photo, volume = solver._event_evaluation(state, owner, point)
    pop = np.asarray(state.values[:5].T, dtype=np.float64)
    nh = pop[:, 0] + pop[:, 1]
    nhe = pop[:, 2] + pop[:, 3] + pop[:, 4]
    rhs = np.asarray(event.population_rhs, dtype=np.float64)
    thermal_rhs = thermal._thermal_rhs_numpy(
        np.log(state.temperature_K),
        pop,
        volume,
        photo.heating,
        np.full(state.node_count, point.hubble_s_inv),
    )
    particles = nh + nhe + pop[:, 1] + pop[:, 3] + 2.0 * pop[:, 4]
    energy = 1.5 * thermal.KB_ERG * particles * state.temperature_K
    particle_rhs = rhs[:, 1] + rhs[:, 3] + 2.0 * rhs[:, 4]
    return np.ascontiguousarray(
        np.column_stack(
            [
                rhs[:, 1] / nh,
                rhs[:, 3] / nhe,
                rhs[:, 4] / nhe,
                thermal_rhs / energy - particle_rhs / particles,
            ]
        )
    )


def _perturb_xhii(state, thermal, node: int, delta: float):
    trial = state.mutable_copy()
    pop = trial.values[:5, node]
    nh = pop[0] + pop[1]
    x = pop[1] / nh
    target = x + float(delta)
    if not 0.0 < target < 1.0:
        raise ValueError("x_HII perturbation leaves physical interval")
    trial.values[0, node] = nh * (1.0 - target)
    trial.values[1, node] = nh * target
    trial.values[5, node] = _energy_from_temperature(
        thermal,
        trial.values[:5, node][None, :],
        trial.temperature_K[node : node + 1],
    )[0]
    return trial


def _central_derivative(solver, thermal, state, point, node: int, epsilon: float) -> float:
    plus = _reduced_rhs(solver, thermal, _perturb_xhii(state, thermal, node, epsilon), point)
    minus = _reduced_rhs(solver, thermal, _perturb_xhii(state, thermal, node, -epsilon), point)
    # output coordinate 3 is d log(T)/dt; input coordinate is x_HII.
    return float((plus[node, 3] - minus[node, 3]) / (2.0 * epsilon))


def _node_record(solver, thermal, state, point, node: int) -> dict[str, float | int | list[float]]:
    derivatives = [
        _central_derivative(solver, thermal, state, point, node, epsilon)
        for epsilon in EPSILONS
    ]
    scale = max(abs(derivatives[0]), abs(derivatives[1]), 1.0e-300)
    consistency = abs(derivatives[0] - derivatives[1]) / scale
    return {
        "node_index": int(node),
        "temperature_K": float(state.temperature_K[node]),
        "derivative": float(derivatives[-1]),
        "derivatives_by_epsilon": [float(v) for v in derivatives],
        "epsilons": [float(v) for v in EPSILONS],
        "relative_eps_consistency": float(consistency),
    }


def run_audit(repo_root: Path) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    trial_mod, thermal = _modules(repo)
    solver = trial_mod.UncertaintySecondOrderTrial.from_repo(
        repo_root=repo,
        lane=LANE,
        v_policy=V_POLICY,
        f_value=F_VALUE,
    )
    state = solver.inputs.state0.mutable_copy()
    point = solver.forcing.point(interval=0, time_s=0.0)
    low = _node_record(solver, thermal, state, point, LOW_NODE)
    high = _node_record(solver, thermal, state, point, HIGH_NODE)
    sign_reversal = low["derivative"] < 0.0 < high["derivative"]
    robust = (
        sign_reversal
        and low["relative_eps_consistency"] < 1.0e-5
        and high["relative_eps_consistency"] < 1.0e-5
        and abs(low["derivative"]) > 1.0e-14
        and abs(high["derivative"]) > 1.0e-12
    )
    return {
        "classification": "CONSTANT_DIAGONAL_ORTHANT_MONOTONICITY_AUDIT",
        "constant_diagonal_orthant_excluded": bool(robust),
        "scope": (
            "Excludes constant diagonal sign transformations of the reduced "
            "coordinate orthant only; nonlinear/state-dependent cones remain open."
        ),
        "lane": LANE,
        "v_policy": V_POLICY,
        "f_value": F_VALUE,
        "witness": {
            "input_coordinate": "x_HII",
            "output_coordinate": "log_T",
            "jacobian_entry": "d(dlogT_dt)/d(x_HII)",
            "low_node": low,
            "high_node": high,
            "sign_reversal": bool(sign_reversal),
            "orthant_argument": (
                "A fixed diagonal sign transform multiplies both values by the "
                "same s_logT*s_xHII and cannot make opposite signs simultaneously nonnegative."
            ),
        },
    }


def main() -> None:
    repo = Path(__file__).resolve().parents[3]
    print(json.dumps(run_audit(repo), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
