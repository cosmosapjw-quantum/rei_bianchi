#!/usr/bin/env python3
"""Positivity-preserving damped Picard globalization for array material states.

The solver treats the physical one-step operator as a black-box fixed-point map
``G(Y)``.  It never clips or projects a state.  The only globalization is a
convex material-state blend over a predeclared damping set, followed by a fresh
fixed-point-defect evaluation and hard conservation/ledger gates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any, Callable, Mapping

import numpy as np

try:
    from r2b_r2a_tensorized import ArrayState
except ImportError:
    _HERE = Path(__file__).resolve().parent
    _SPEC = importlib.util.spec_from_file_location(
        "r2b_r2a_tensorized", _HERE / "tensorized_inputs.py"
    )
    if _SPEC is None or _SPEC.loader is None:
        raise ImportError("cannot load tensorized_inputs.py")
    _MOD = importlib.util.module_from_spec(_SPEC)
    sys.modules[_SPEC.name] = _MOD
    _SPEC.loader.exec_module(_MOD)
    ArrayState = _MOD.ArrayState

KB_ERG = 1.380649e-16
DAMPING_CANDIDATES = (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625)


@dataclass(frozen=True)
class MapEvaluation:
    state: ArrayState | None
    feasible: bool = True
    owner_residual: float = 0.0
    photon_residual: float = 0.0
    hydrogen_residual: float = 0.0
    helium_residual: float = 0.0
    thermal_residual: float = 0.0
    unresolved_energy_residual: float = 0.0
    structural_zero_ok: bool = True
    certificate: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrialResult:
    state: ArrayState
    converged: bool
    iterations: int
    residual: float
    residual_trace: tuple[float, ...]
    damping_trace: tuple[float, ...]
    map_calls: int
    minimum_species: float
    max_hydrogen_residual: float
    max_helium_residual: float
    max_owner_residual: float
    max_photon_residual: float
    max_thermal_residual: float
    certificate: dict[str, Any]


def _copy_state(state: ArrayState) -> ArrayState:
    return ArrayState(state.values.copy(), state.temperature_K.copy())


def _nuclei(state: ArrayState) -> tuple[np.ndarray, np.ndarray]:
    y = state.values
    return y[0] + y[1], y[2] + y[3] + y[4]


def _temperature_from_values(values: np.ndarray) -> np.ndarray:
    nh = values[0] + values[1]
    nhe = values[2] + values[3] + values[4]
    ne = values[1] + values[3] + 2.0 * values[4]
    particles = nh + nhe + ne
    if np.any(~np.isfinite(particles)) or np.any(particles <= 0.0):
        raise ValueError("material particle count must be finite and positive")
    temperature = 2.0 * values[5] / (3.0 * KB_ERG * particles)
    return temperature


def blend_states(a: ArrayState, b: ArrayState, weight_b: float) -> ArrayState:
    """Convexly blend populations and energy, then derive temperature.

    This is an interior-cone line-search operation, not a projection.  For
    ``0 < weight_b <= 1`` and two positive input states, all populations and
    energy remain nonnegative by convexity.
    """
    w = float(weight_b)
    if not (0.0 < w <= 1.0):
        raise ValueError("damping weight must lie in (0,1]")
    if a.values.shape != b.values.shape:
        raise ValueError("state shape mismatch")
    values = (1.0 - w) * a.values + w * b.values
    temperature = _temperature_from_values(values)
    return ArrayState(np.ascontiguousarray(values), np.ascontiguousarray(temperature))


def state_residual(a: ArrayState, b: ArrayState) -> float:
    """Locked maximum material fixed-point defect."""
    nh, nhe = _nuclei(a)
    if a.values.shape != b.values.shape:
        raise ValueError("state shape mismatch")
    if np.any(nh <= 0.0) or np.any(nhe <= 0.0):
        return math.inf
    terms = (
        np.max(np.abs(a.values[1] / nh - b.values[1] / nh)),
        np.max(np.abs(a.values[3] / nhe - b.values[3] / nhe)),
        np.max(np.abs(a.values[4] / nhe - b.values[4] / nhe)),
        np.max(np.abs(np.log(a.temperature_K) - np.log(b.temperature_K))),
    )
    return float(max(terms))


class GlobalizedPicard:
    def __init__(
        self,
        *,
        tolerance: float = 1.0e-10,
        owner_nuclei_tolerance: float = 1.0e-11,
        photon_tolerance: float = 1.0e-8,
        thermal_tolerance: float = 1.0e-10,
        max_iterations: int = 40,
        damping_candidates: tuple[float, ...] = DAMPING_CANDIDATES,
        armijo_constant: float = 1.0e-4,
    ) -> None:
        self.tolerance = float(tolerance)
        self.owner_nuclei_tolerance = float(owner_nuclei_tolerance)
        self.photon_tolerance = float(photon_tolerance)
        self.thermal_tolerance = float(thermal_tolerance)
        self.max_iterations = int(max_iterations)
        self.damping_candidates = tuple(float(v) for v in damping_candidates)
        self.armijo_constant = float(armijo_constant)
        if self.damping_candidates != DAMPING_CANDIDATES:
            raise ValueError("damping candidates differ from the pre-calculation lock")

    def _gate(
        self, evaluation: MapEvaluation, *, parent_h: np.ndarray, parent_he: np.ndarray
    ) -> tuple[bool, dict[str, Any], dict[str, float]]:
        cert = dict(evaluation.certificate)
        if not evaluation.feasible or evaluation.state is None:
            cert.setdefault("classification", "FIXED_POINT_NONCONVERGENCE")
            return False, cert, {}
        state = evaluation.state
        y = state.values
        if (
            np.any(~np.isfinite(y))
            or np.any(y < 0.0)
            or np.any(~np.isfinite(state.temperature_K))
            or np.any(state.temperature_K <= 0.0)
            or np.any(y[5] <= 0.0)
        ):
            cert.setdefault("classification", "THERMAL_CONE")
            return False, cert, {}
        if not evaluation.structural_zero_ok:
            cert.setdefault("classification", "STRUCTURAL_ZERO_VIOLATION")
            return False, cert, {}
        h, he = _nuclei(state)
        h_res = float(np.max(np.abs(h - parent_h) / np.maximum(np.abs(parent_h), 1.0e-300)))
        he_res = float(np.max(np.abs(he - parent_he) / np.maximum(np.abs(parent_he), 1.0e-300)))
        h_res = max(h_res, float(evaluation.hydrogen_residual))
        he_res = max(he_res, float(evaluation.helium_residual))
        owner_res = float(evaluation.owner_residual)
        photon_res = float(evaluation.photon_residual)
        thermal_res = max(
            float(evaluation.thermal_residual),
            float(evaluation.unresolved_energy_residual),
        )
        metrics = {
            "hydrogen": h_res,
            "helium": he_res,
            "owner": owner_res,
            "photon": photon_res,
            "thermal": thermal_res,
        }
        if max(h_res, he_res, owner_res) > self.owner_nuclei_tolerance:
            cert.setdefault("classification", "OWNER_NUCLEI_GATE")
            cert.update(metrics)
            return False, cert, metrics
        if photon_res > self.photon_tolerance:
            cert.setdefault("classification", "PHOTON_LEDGER")
            cert.update(metrics)
            return False, cert, metrics
        if thermal_res > self.thermal_tolerance:
            cert.setdefault("classification", "THERMAL_BALANCE")
            cert.update(metrics)
            return False, cert, metrics
        return True, cert, metrics

    def solve(
        self,
        *,
        parent: ArrayState,
        map_state: Callable[[ArrayState], MapEvaluation],
    ) -> TrialResult:
        parent_h, parent_he = _nuclei(parent)
        iterate = _copy_state(parent)
        residual_trace: list[float] = []
        damping_trace: list[float] = []
        map_calls = 0
        maxima = {"hydrogen": 0.0, "helium": 0.0, "owner": 0.0, "photon": 0.0, "thermal": 0.0}
        minimum_species = float(np.min(iterate.values[:5]))

        def evaluate(state: ArrayState) -> tuple[MapEvaluation, bool, dict[str, Any], dict[str, float]]:
            nonlocal map_calls, minimum_species
            result = map_state(state)
            map_calls += 1
            ok, cert, metrics = self._gate(result, parent_h=parent_h, parent_he=parent_he)
            if result.state is not None:
                minimum_species = min(minimum_species, float(np.min(result.state.values[:5])))
            for name, value in metrics.items():
                maxima[name] = max(maxima[name], float(value))
            return result, ok, cert, metrics

        cached_evaluation: tuple[MapEvaluation, bool, dict[str, Any], dict[str, float]] | None = None
        for iteration in range(1, self.max_iterations + 1):
            if cached_evaluation is None:
                mapped, ok, cert, _ = evaluate(iterate)
            else:
                mapped, ok, cert, _ = cached_evaluation
                cached_evaluation = None
            if not ok or mapped.state is None:
                return TrialResult(
                    state=_copy_state(parent), converged=False, iterations=iteration,
                    residual=math.inf, residual_trace=tuple(residual_trace),
                    damping_trace=tuple(damping_trace), map_calls=map_calls,
                    minimum_species=minimum_species,
                    max_hydrogen_residual=maxima["hydrogen"],
                    max_helium_residual=maxima["helium"],
                    max_owner_residual=maxima["owner"],
                    max_photon_residual=maxima["photon"],
                    max_thermal_residual=maxima["thermal"], certificate=cert,
                )
            old_residual = state_residual(mapped.state, iterate)
            residual_trace.append(old_residual)
            if old_residual <= self.tolerance:
                return TrialResult(
                    state=_copy_state(mapped.state), converged=True, iterations=iteration,
                    residual=old_residual, residual_trace=tuple(residual_trace),
                    damping_trace=tuple(damping_trace), map_calls=map_calls,
                    minimum_species=minimum_species,
                    max_hydrogen_residual=maxima["hydrogen"],
                    max_helium_residual=maxima["helium"],
                    max_owner_residual=maxima["owner"],
                    max_photon_residual=maxima["photon"],
                    max_thermal_residual=maxima["thermal"], certificate={},
                )

            accepted: ArrayState | None = None
            accepted_lambda: float | None = None
            accepted_defect = math.inf
            last_certificate: dict[str, Any] = {"classification": "FIXED_POINT_NONCONVERGENCE"}
            for lam in self.damping_candidates:
                candidate = blend_states(iterate, mapped.state, lam)
                candidate_map, candidate_ok, candidate_cert, candidate_metrics = evaluate(candidate)
                last_certificate = candidate_cert
                if not candidate_ok or candidate_map.state is None:
                    continue
                defect = state_residual(candidate_map.state, candidate)
                required = (1.0 - self.armijo_constant * lam) * old_residual
                if defect <= self.tolerance or defect <= required:
                    accepted = candidate
                    accepted_lambda = lam
                    accepted_defect = defect
                    cached_evaluation = (
                        candidate_map, candidate_ok, candidate_cert, candidate_metrics
                    )
                    break
            if accepted is None or accepted_lambda is None:
                last_certificate.setdefault("classification", "FIXED_POINT_NONCONVERGENCE")
                last_certificate.update(
                    {"residual": old_residual, "iterations": iteration, "damping_exhausted": True}
                )
                return TrialResult(
                    state=_copy_state(parent), converged=False, iterations=iteration,
                    residual=old_residual, residual_trace=tuple(residual_trace),
                    damping_trace=tuple(damping_trace), map_calls=map_calls,
                    minimum_species=minimum_species,
                    max_hydrogen_residual=maxima["hydrogen"],
                    max_helium_residual=maxima["helium"],
                    max_owner_residual=maxima["owner"],
                    max_photon_residual=maxima["photon"],
                    max_thermal_residual=maxima["thermal"], certificate=last_certificate,
                )
            damping_trace.append(accepted_lambda)
            iterate = accepted
            if accepted_defect <= self.tolerance:
                # Re-evaluate on the next loop so the returned state is G(Y),
                # not merely the line-search candidate.
                continue

        residual = residual_trace[-1] if residual_trace else math.inf
        return TrialResult(
            state=_copy_state(parent), converged=False, iterations=self.max_iterations,
            residual=residual, residual_trace=tuple(residual_trace),
            damping_trace=tuple(damping_trace), map_calls=map_calls,
            minimum_species=minimum_species,
            max_hydrogen_residual=maxima["hydrogen"],
            max_helium_residual=maxima["helium"],
            max_owner_residual=maxima["owner"],
            max_photon_residual=maxima["photon"],
            max_thermal_residual=maxima["thermal"],
            certificate={
                "classification": "FIXED_POINT_NONCONVERGENCE",
                "residual": residual,
                "iterations": self.max_iterations,
            },
        )
