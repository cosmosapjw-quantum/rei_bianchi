"""Validated-box Picard audit for continuous full-OTS branch uncertainty.

This module deliberately distinguishes three claims:

* a numerical trajectory exists (already witnessed by the previous stage),
* a componentwise binary64 interval box can certify the complete parameter
  family, and
* the physical family is impossible.

Only the second claim is tested here.  Failure caused by dependency/wrapping is
therefore a fail-closed certificate for this enclosure architecture, not a
physical no-go theorem.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any, Callable, Iterable

import numpy as np

HERE = Path(__file__).resolve().parent


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


iv = _load("r2_r1a_r1_interval_arithmetic", HERE / "interval_arithmetic.py")
rhs_mod = _load("r2_r1a_r1_validated_rhs", HERE / "reduced_interval_rhs.py")


@dataclass(frozen=True)
class PicardStepResult:
    accepted: bool
    classification: str
    endpoint: iv.Interval | None
    tube: iv.Interval | None
    iterations: int
    maximum_width: float
    message: str


def _subset(inner: iv.Interval, outer: iv.Interval) -> bool:
    return bool(np.all(outer.lo <= inner.lo) and np.all(inner.hi <= outer.hi))


def _maximum_width(box: iv.Interval | None) -> float:
    if box is None:
        return float("inf")
    return float(np.max(box.hi - box.lo))


def _failure_classification(exc: Exception, *, wrapping: bool = False) -> str:
    message = str(exc)
    if "above-table Hummer--Seaton" in message:
        return "TABLE_TOPOLOGY_EVENT_UNLOCALIZED"
    return "BOX_PICARD_WRAPPING_FAILURE" if wrapping else "BOX_PICARD_CONE_EXIT"


def _picard_step(
    *,
    initial: iv.Interval,
    time_lower: float,
    time_upper: float,
    rhs: Callable[[iv.Interval, float, float], iv.Interval],
    validate_box: Callable[[iv.Interval], None] | None = None,
    maximum_iterations: int = 5,
    inflation_fraction: float = 0.05,
) -> PicardStepResult:
    """Attempt a componentwise interval Picard enclosure for one time slab."""

    dt = float(time_upper - time_lower)
    if not np.isfinite(dt) or dt <= 0.0:
        raise ValueError("Picard time slab must have positive finite width")
    try:
        seed_rhs = rhs(initial, time_lower, time_upper)
        seed_endpoint = initial + dt * seed_rhs
        tube = iv.inflate(iv.hull(initial, seed_endpoint), relative=inflation_fraction, absolute=1.0e-300)
        if validate_box is not None:
            validate_box(tube)
    except ValueError as exc:
        return PicardStepResult(
            False,
            _failure_classification(exc),
            None,
            None,
            0,
            float("inf"),
            str(exc),
        )

    widest = _maximum_width(tube)
    for iteration in range(1, int(maximum_iterations) + 1):
        try:
            field = rhs(tube, time_lower, time_upper)
            time_interval = iv.Interval(0.0, dt)
            image = initial + time_interval * field
            candidate = iv.hull(initial, image)
            if validate_box is not None:
                validate_box(candidate)
        except ValueError as exc:
            return PicardStepResult(
                False,
                _failure_classification(exc),
                None,
                tube,
                iteration,
                max(widest, _maximum_width(tube)),
                str(exc),
            )
        widest = max(widest, _maximum_width(candidate))
        if _subset(candidate, tube):
            endpoint = initial + dt * field
            if validate_box is not None:
                validate_box(endpoint)
            return PicardStepResult(
                True,
                "BOX_PICARD_CERTIFIED",
                endpoint,
                tube,
                iteration,
                widest,
                "Picard image is contained in the a-priori tube.",
            )
        try:
            tube = iv.inflate(candidate, relative=inflation_fraction, absolute=1.0e-300)
            if validate_box is not None:
                validate_box(tube)
        except ValueError as exc:
            return PicardStepResult(
                False,
                _failure_classification(exc, wrapping=True),
                None,
                candidate,
                iteration,
                max(widest, _maximum_width(candidate)),
                str(exc),
            )

    return PicardStepResult(
        False,
        "BOX_PICARD_INCLUSION_FAILURE",
        None,
        tube,
        int(maximum_iterations),
        max(widest, _maximum_width(tube)),
        "Picard image did not become self-mapping before the locked iteration limit.",
    )


def scalar_linear_demo(*, rate: float, initial: float, duration: float) -> dict[str, float | bool | int]:
    """Small analytic regression proving the Picard machinery can certify a flow."""

    y0 = iv.Interval(float(initial))

    def field(box: iv.Interval, _t0: float, _t1: float) -> iv.Interval:
        return float(rate) * box

    result = _picard_step(
        initial=y0,
        time_lower=0.0,
        time_upper=float(duration),
        rhs=field,
        maximum_iterations=12,
        inflation_fraction=0.15,
    )
    if not result.accepted or result.endpoint is None:
        return {
            "certified": False,
            "endpoint_lower": float("nan"),
            "endpoint_upper": float("nan"),
            "iterations": result.iterations,
        }
    return {
        "certified": True,
        "endpoint_lower": float(result.endpoint.lo),
        "endpoint_upper": float(result.endpoint.hi),
        "iterations": result.iterations,
    }


def _partition_audit(model: Any, *, partition: int) -> dict[str, Any]:
    duration = float(model.solver.forcing.duration_seconds(0)) / 2048.0
    segment_dt = duration / int(partition)
    current = model.point_box(model.initial_coordinates())
    f_interval = model.scalar_interval(0.1)
    f_interval = iv.Interval(f_interval.lo, np.asarray(1.0))
    accepted = 0
    max_width = 0.0
    started = time.perf_counter()

    def field(box: iv.Interval, t0: float, t1: float) -> iv.Interval:
        return model.rhs_interval(
            coordinates=box,
            time_lower_s=t0,
            time_upper_s=t1,
            v_interval=model.source_v_interval(box),
            f_interval=f_interval,
        )

    def validate(box: iv.Interval) -> None:
        # Reconstruction is the cone gate; no clipping/intersection is allowed.
        model.reconstruct_populations(box)
        model.physical_fraction_box(box)

    for segment in range(int(partition)):
        t0 = segment * segment_dt
        t1 = (segment + 1) * segment_dt
        result = _picard_step(
            initial=current,
            time_lower=t0,
            time_upper=t1,
            rhs=field,
            validate_box=validate,
            maximum_iterations=4,
            inflation_fraction=0.05,
        )
        max_width = max(max_width, result.maximum_width)
        if not result.accepted or result.endpoint is None:
            return {
                "partition": int(partition),
                "segment_count": int(partition),
                "accepted_segments": int(accepted),
                "first_failed_segment_zero_based": int(segment),
                "classification": result.classification,
                "message": result.message,
                "picard_iterations_at_failure": int(result.iterations),
                "maximum_internal_coordinate_width": float(max_width),
                "elapsed_s": float(time.perf_counter() - started),
                "certified": False,
            }
        current = result.endpoint
        accepted += 1

    physical = model.physical_fraction_box(current)
    return {
        "partition": int(partition),
        "segment_count": int(partition),
        "accepted_segments": int(accepted),
        "first_failed_segment_zero_based": None,
        "classification": "BOX_PICARD_CERTIFIED",
        "message": "All subsegments have self-mapping Picard tubes.",
        "picard_iterations_at_failure": None,
        "maximum_internal_coordinate_width": float(max_width),
        "final_physical_widths": {
            "x_HII": float(np.max(physical.hi[0] - physical.lo[0])),
            "x_HeII": float(np.max(physical.hi[1] - physical.lo[1])),
            "x_HeIII": float(np.max(physical.hi[2] - physical.lo[2])),
            "log_T": float(np.max(physical.hi[3] - physical.lo[3])),
        },
        "elapsed_s": float(time.perf_counter() - started),
        "certified": True,
    }


def run_project_audit(repo_root: Path, *, partitions: Iterable[int] = (16, 32, 64)) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    model = rhs_mod.ReducedIntervalModel.from_repo(repo)
    rows = [_partition_audit(model, partition=int(p)) for p in partitions]
    certified = any(bool(row["certified"]) for row in rows)
    return {
        "classification": (
            "CONTINUOUS_BRANCH_BOX_CERTIFIED" if certified else
            "CONSTANT_ORTHANT_EXCLUDED_COMPONENTWISE_BOX_WRAPPING_UNCERTIFIED"
        ),
        "continuous_parameter_certified": bool(certified),
        "production_history_authorized": False,
        "physical_nonexistence_claimed": False,
        "method_scope": (
            "Outward-rounded componentwise interval Picard boxes in direct neutral/conditional "
            "coordinates. Failure excludes this box architecture only."
        ),
        "branch_parameter_domain": {
            "v_below_1e4_K": [0.0, 1.0],
            "v_table_domain": "source-node bracketing interval, no continuous interpolant assumed",
            "f": [0.1, 1.0],
        },
        "partition_audits": rows,
    }


def main() -> None:
    repo = Path(__file__).resolve().parents[3]
    print(json.dumps(run_project_audit(repo), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
