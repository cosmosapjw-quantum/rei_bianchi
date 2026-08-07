#!/usr/bin/env python3
"""Transactional linearly-implicit Picard fixed point for one material step."""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import math
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np


def _load_sibling(stem: str):
    name = f"r2b_r2_{stem}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{stem}.py"))
    if spec is None or spec.loader is None:
        raise ImportError(stem)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


micro = _load_sibling("microphysics")
transaction = _load_sibling("transaction")


@dataclass(frozen=True)
class FixedPointResult:
    state: Any
    converged: bool
    iterations: int
    residual: float
    minimum_species: float
    max_hydrogen_residual: float
    max_helium_residual: float
    certificate: dict[str, Any]


def _state_residual(a: Any, b: Any) -> float:
    nh = np.asarray(a.N_H)
    nhe = np.asarray(a.N_He)
    values = [
        np.max(np.abs(a.N_HII / nh - b.N_HII / nh)),
        np.max(np.abs(a.N_HeII / nhe - b.N_HeII / nhe)),
        np.max(np.abs(a.N_HeIII / nhe - b.N_HeIII / nhe)),
        np.max(np.abs(np.log(a.T_K) - np.log(b.T_K))),
    ]
    return float(max(values))


def solve_picard_step(
    *,
    parent: Any,
    proper_volume_cm3: np.ndarray,
    photo_law: Callable[[Any], Any],
    hubble_s_inv: float,
    dt_seconds: float,
    tolerance: float = 1e-10,
    max_iterations: int = 40,
    damping: float = 0.7,
) -> FixedPointResult:
    if not (0.0 < float(damping) <= 1.0):
        raise ValueError("damping must lie in (0,1]")
    iterate = parent
    last_residual = math.inf
    minimum = math.inf
    max_h = max_he = 0.0
    for iteration in range(1, int(max_iterations) + 1):
        photo = photo_law(iterate)
        update = micro.linearly_implicit_update(
            parent=parent,
            coefficient_state=iterate,
            proper_volume_cm3=proper_volume_cm3,
            photo=photo,
            hubble_s_inv=hubble_s_inv,
            dt_seconds=dt_seconds,
        )
        minimum = float(np.min(update.minimum_species))
        max_h = float(np.max(np.abs(update.hydrogen_residual) / np.maximum(parent.N_H, 1.0)))
        max_he = float(np.max(np.abs(update.helium_residual) / np.maximum(parent.N_He, 1.0)))
        if not np.all(update.feasible):
            bad = int(np.flatnonzero(~update.feasible)[0])
            classification = (
                "THERMAL_CONE" if update.state.U_resolved[bad] <= 0.0 or update.state.T_K[bad] <= 0.0
                else "MATERIAL_CAPACITY"
            )
            return FixedPointResult(
                state=iterate,
                converged=False,
                iterations=iteration,
                residual=math.inf,
                minimum_species=minimum,
                max_hydrogen_residual=max_h,
                max_helium_residual=max_he,
                certificate={
                    "classification": classification,
                    "node_index": bad,
                    "minimum_species": minimum,
                    "clipping_used": False,
                },
            )
        residual = _state_residual(update.state, iterate)
        last_residual = residual
        if residual <= tolerance:
            return FixedPointResult(
                state=update.state,
                converged=True,
                iterations=iteration,
                residual=residual,
                minimum_species=minimum,
                max_hydrogen_residual=max_h,
                max_helium_residual=max_he,
                certificate={},
            )
        iterate = micro.blend_material_states(iterate, update.state, damping)
    return FixedPointResult(
        state=iterate,
        converged=False,
        iterations=int(max_iterations),
        residual=last_residual,
        minimum_species=minimum,
        max_hydrogen_residual=max_h,
        max_helium_residual=max_he,
        certificate={
            "classification": "FIXED_POINT_NONCONVERGENCE",
            "residual": last_residual,
            "iterations": int(max_iterations),
            "clipping_used": False,
        },
    )


def advance_transactionally(
    *,
    history: Any,
    proper_volume_cm3: np.ndarray,
    photo_law: Callable[[Any], Any],
    hubble_s_inv: float,
    dt_seconds: float,
    tolerance: float = 1e-10,
    max_iterations: int = 40,
    damping: float = 0.7,
) -> FixedPointResult:
    with history.attempt("owner-correct-fixed-point") as scratch:
        result = solve_picard_step(
            parent=scratch.state,
            proper_volume_cm3=proper_volume_cm3,
            photo_law=photo_law,
            hubble_s_inv=hubble_s_inv,
            dt_seconds=dt_seconds,
            tolerance=tolerance,
            max_iterations=max_iterations,
            damping=damping,
        )
        if not result.converged:
            raise transaction.StepRejected(
                result.certificate.get("classification", "FIXED_POINT_NONCONVERGENCE"),
                result.certificate,
            )
        scratch.state = result.state
    return result
