"""Constructive audit of within-step branch-control freedom.

A source-safe differential inclusion supplies an admissible interval at each
source evaluation.  One fixed pair ``(theta_v[i], theta_f[i])`` per node and
substep does not represent a schedule that switches between the interval
endpoints at a localized internal time.  This module runs such a schedule
through the locked MPRK22/SDIRK2 solver and compares the accepted endpoint with
the hull of the four static branch corners.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib.util
import math
from pathlib import Path
import sys

import numpy as np

COORDINATES = ("x_HII", "x_HeII", "x_HeIII", "log_T")


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class TemporalControlAudit:
    lane: str
    schedule: str
    full_converged: bool
    first_half_converged: bool
    second_half_converged: bool
    all_trial_hard_gates_pass: bool
    local_error: float
    maximum_hydrogen_residual: float
    maximum_helium_residual: float
    maximum_owner_residual: float
    maximum_photon_residual: float
    maximum_thermal_residual: float
    maximum_ots_energy_residual: float
    minimum_species: float
    outside_coordinate: str
    outside_node: int
    outside_node_count: int
    maximum_outside_absolute: float
    maximum_outside_fraction_of_static_width: float
    static_parameter_enclosure_certified: bool
    stagewise_control_generators_required: bool
    source_regularization_assumed: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _strict_corner_hull(repo: Path, lane: str) -> tuple[np.ndarray, np.ndarray]:
    prior = next(repo.glob("stages/*R2_R1A_FOUR_CORNER*"))
    token = lane.lower()
    with np.load(prior / "data/strict_corner_envelopes.npz", allow_pickle=False) as data:
        lower = np.vstack([data[f"{token}__{name}_lower"] for name in COORDINATES])
        upper = np.vstack([data[f"{token}__{name}_upper"] for name in COORDINATES])
    return np.ascontiguousarray(lower), np.ascontiguousarray(upper)


def run_temporal_control_audit(
    repo_root: Path,
    *,
    lane: str,
    schedule: str = "UPPER_TO_LOWER_AT_HALF_STEP",
) -> TemporalControlAudit:
    repo = Path(repo_root).resolve()
    affine_stage = next(repo.glob("stages/*R2_R1A_R1_R1_AFFINE_SET*"))
    field = _load("sparse_temporal_field_trial", affine_stage / "analysis/field_trial.py")
    trial_mod, policy_mod, picard = field.load_parent_modules(repo)
    base_class = field.make_trial_class(repo)

    base = trial_mod.fast.base.physical.PhysicalTrialSolver.from_repo(
        repo_root=repo, lane=lane
    )
    full_step = float(base.forcing.duration_seconds(0) / 2048.0)
    switch_time = 0.5 * full_step

    class StagewiseTrial(base_class):
        def __init__(self) -> None:
            super().__init__(base=base, lane=lane, alpha=0.0, beta=0.0)

        def _event_evaluation(self, state, owner, point):
            y = np.asarray(state.values, dtype=np.float64)
            volume = self.inputs.comoving_volume_cm3 / (1.0 + point.z) ** 3
            photo = self.backend.photo_fields(owner)
            lower = policy_mod.build_v_field_from_temperature(
                "CELL_LOWER_STRICT", state.temperature_K
            )
            upper = policy_mod.build_v_field_from_temperature(
                "CELL_UPPER_STRICT", state.temperature_K
            )
            # The switch is an explicitly localized admissible control event.
            # At the event itself use the left trace; right-stage evaluations
            # use the lower endpoint.
            early = bool(point.time_s <= switch_time * (1.0 + 1.0e-12))
            if schedule != "UPPER_TO_LOWER_AT_HALF_STEP":
                raise KeyError(schedule)
            selector_v = 1.0 if early else 0.0
            selector_f = 1.0 if early else 0.0
            v = lower + selector_v * (upper - lower)
            f = np.full(state.node_count, 0.1 + 0.9 * selector_f, dtype=np.float64)
            event = trial_mod.event_mod.evaluate_event_flux(
                populations=y[:5].T,
                temperature_K=state.temperature_K,
                proper_volume_cm3=volume,
                photo_hi=photo.HI,
                photo_hei=photo.HeI,
                photo_heii=photo.HeII,
                v=v,
                f=f,
            )
            adjusted = trial_mod.fast.base.physical.PhotoFields(
                HI=photo.HI,
                HeI=photo.HeI,
                HeII=photo.HeII,
                heating=np.ascontiguousarray(
                    photo.heating + event.resolved_ots_heating_erg_s
                ),
                unresolved_heating=np.ascontiguousarray(
                    photo.unresolved_heating + event.unresolved_ots_energy_erg_s
                ),
            )
            return event, adjusted, volume

    solver = StagewiseTrial()
    parent = base.inputs.state0.mutable_copy()
    midpoint = switch_time
    full = solver.solve(
        state=parent.mutable_copy(),
        t0=0.0,
        t1=full_step,
        partition=2048,
        trial_kind="FULL",
    )
    first = solver.solve(
        state=parent.mutable_copy(),
        t0=0.0,
        t1=midpoint,
        partition=4096,
        trial_kind="FIRST_HALF",
    )
    second = (
        solver.solve(
            state=first.state.mutable_copy(),
            t0=midpoint,
            t1=full_step,
            partition=4096,
            trial_kind="SECOND_HALF",
        )
        if first.converged and first.state is not None
        else None
    )
    trials = [full, first] + ([] if second is None else [second])
    all_converged = bool(
        full.converged and first.converged and second is not None and second.converged
    )
    local_error = (
        float(picard.state_residual(full.state, second.state))
        if all_converged
        else math.inf
    )
    all_hard = bool(
        all_converged
        and local_error < 2.0e-4
        and all(field.gate_trial(item) for item in trials)
    )
    if second is None or second.state is None:
        raise RuntimeError("stagewise audit did not produce an endpoint")
    observables = field.state_observables(second.state)
    lower, upper = _strict_corner_hull(repo, lane)
    below = np.maximum(lower - observables, 0.0)
    above = np.maximum(observables - upper, 0.0)
    outside = np.maximum(below, above)
    width = upper - lower
    roundoff = 128.0 * np.finfo(np.float64).eps * np.maximum(
        np.maximum(np.abs(lower), np.abs(upper)), np.finfo(np.float64).tiny
    )
    significant = outside > roundoff
    count = int(np.count_nonzero(significant))
    flat = int(np.argmax(outside))
    coordinate, node = np.unravel_index(flat, outside.shape)
    valid_width = width > roundoff
    relative = np.zeros_like(outside)
    np.divide(outside, width, out=relative, where=valid_width)

    return TemporalControlAudit(
        lane=lane,
        schedule=schedule,
        full_converged=bool(full.converged),
        first_half_converged=bool(first.converged),
        second_half_converged=bool(second.converged),
        all_trial_hard_gates_pass=all_hard,
        local_error=local_error,
        maximum_hydrogen_residual=float(max(item.hydrogen_residual for item in trials)),
        maximum_helium_residual=float(max(item.helium_residual for item in trials)),
        maximum_owner_residual=float(max(item.owner_residual for item in trials)),
        maximum_photon_residual=float(max(item.photon_residual for item in trials)),
        maximum_thermal_residual=float(max(item.thermal_residual for item in trials)),
        maximum_ots_energy_residual=float(
            max(
                float(item.certificate.get("max_augmented_energy_residual", math.inf))
                for item in trials
            )
        ),
        minimum_species=float(min(item.minimum_species for item in trials)),
        outside_coordinate=COORDINATES[coordinate],
        outside_node=int(node),
        outside_node_count=count,
        maximum_outside_absolute=float(outside[coordinate, node]),
        maximum_outside_fraction_of_static_width=float(np.max(relative)),
        static_parameter_enclosure_certified=False,
        stagewise_control_generators_required=True,
        source_regularization_assumed=False,
    )


__all__ = ["TemporalControlAudit", "run_temporal_control_audit"]
