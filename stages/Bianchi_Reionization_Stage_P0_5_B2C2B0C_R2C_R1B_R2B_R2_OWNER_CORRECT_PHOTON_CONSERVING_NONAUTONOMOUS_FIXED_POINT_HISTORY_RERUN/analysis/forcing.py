#!/usr/bin/env python3
"""Canonical time-slab forcing for the R2B-R2 history rerun.

The 17 locked BDF dense-output nodes in each redshift interval define a
shape-preserving PCHIP representation.  Authoritative group absorption is
integrated with the exact antiderivative of that interpolant; no endpoint
fitting or post-hoc quadrature choice is used.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

GROUPS = ("G1", "G2a", "G2b", "G3")
SUBGRID_GROUPS = frozenset({"G1", "G2a"})


@dataclass(frozen=True)
class IntervalModel:
    index: int
    times: np.ndarray
    frame: pd.DataFrame
    interpolators: dict[str, PchipInterpolator]
    external_subgrid: dict[str, PchipInterpolator | None]

    @property
    def duration_seconds(self) -> float:
        return float(self.times[-1] - self.times[0])


class CanonicalForcing:
    """PCHIP adapter over the immutable canonical dense-output table."""

    def __init__(self, intervals: dict[int, IntervalModel]) -> None:
        self._intervals = dict(sorted(intervals.items()))
        self.interval_indices = tuple(self._intervals)
        if self.interval_indices != tuple(range(len(self.interval_indices))):
            raise ValueError("canonical intervals must be contiguous from zero")

    @classmethod
    def from_stage_inputs(cls, *, forcing_csv: Path, owner_csv: Path) -> "CanonicalForcing":
        forcing = pd.read_csv(forcing_csv).sort_values(["interval_index", "node_index"])
        owners = pd.read_csv(owner_csv).sort_values(
            ["interval_index", "node_index", "group", "component"]
        )
        intervals: dict[int, IntervalModel] = {}
        numeric_excluded = {"interval_index", "node_index", "node_count"}
        for interval, block0 in forcing.groupby("interval_index", sort=True):
            block = block0.sort_values("node_index").reset_index(drop=True)
            times = block["time_s"].to_numpy(dtype=float)
            if len(times) != 17 or not np.all(np.diff(times) > 0.0):
                raise ValueError(f"interval {interval} does not have 17 strictly increasing nodes")
            if abs(times[0]) > 1.0e-12:
                raise ValueError(f"interval {interval} does not begin at local time zero")
            interpolators: dict[str, PchipInterpolator] = {}
            for column in block.columns:
                if column in numeric_excluded:
                    continue
                values = block[column].to_numpy(dtype=float)
                if np.any(~np.isfinite(values)):
                    raise ValueError(f"nonfinite canonical forcing column {column}")
                interpolators[column] = PchipInterpolator(times, values, extrapolate=False)

            external: dict[str, PchipInterpolator | None] = {}
            for group in GROUPS:
                if group not in SUBGRID_GROUPS:
                    external[group] = None
                    continue
                sub = owners[
                    (owners["interval_index"] == interval)
                    & (owners["group"] == group)
                    & (owners["component"] == "EFFECTIVE_HI_SUBGRID")
                ].sort_values("node_index")
                if len(sub) != len(times):
                    raise ValueError(f"missing effective-HI forcing for interval {interval} {group}")
                if not np.allclose(sub["time_s"].to_numpy(float), times, rtol=0.0, atol=1.0e-8):
                    raise ValueError("effective-HI time grid differs from canonical forcing")
                raw = sub["raw_component_kappa_cMpc_inv"].to_numpy(dtype=float)
                if np.any(~np.isfinite(raw)) or np.any(raw < 0.0):
                    raise ValueError("effective-HI raw response must be finite and nonnegative")
                external[group] = PchipInterpolator(times, raw, extrapolate=False)
            intervals[int(interval)] = IntervalModel(
                index=int(interval),
                times=times,
                frame=block,
                interpolators=interpolators,
                external_subgrid=external,
            )
        return cls(intervals)

    def _interval(self, interval: int) -> IntervalModel:
        try:
            return self._intervals[int(interval)]
        except KeyError as exc:
            raise KeyError(f"unknown canonical interval {interval}") from exc

    def duration_seconds(self, interval: int) -> float:
        return self._interval(interval).duration_seconds

    def evaluate(self, interval: int, time_s: float) -> dict[str, float]:
        model = self._interval(interval)
        t = float(time_s)
        if not math.isfinite(t) or t < model.times[0] or t > model.times[-1]:
            raise ValueError(f"time {t!r} outside interval {interval}")
        out: dict[str, float] = {
            "interval_index": float(interval),
            "time_s": t,
        }
        for column, interpolator in model.interpolators.items():
            value = float(interpolator(t))
            if not math.isfinite(value):
                raise ValueError(f"nonfinite interpolated forcing {column}")
            out[column] = value
        return out

    def integrate(self, interval: int, column: str, t0_s: float, t1_s: float) -> float:
        model = self._interval(interval)
        t0, t1 = float(t0_s), float(t1_s)
        if not (math.isfinite(t0) and math.isfinite(t1) and t0 <= t1):
            raise ValueError("invalid integration bounds")
        if t0 < model.times[0] or t1 > model.times[-1]:
            raise ValueError("integration bounds leave canonical interval")
        try:
            interpolator = model.interpolators[column]
        except KeyError as exc:
            raise KeyError(f"unknown forcing column {column!r}") from exc
        value = float(interpolator.integrate(t0, t1))
        if not math.isfinite(value):
            raise ValueError(f"nonfinite integral for {column}")
        return value

    def average(self, interval: int, column: str, t0_s: float, t1_s: float) -> float:
        dt = float(t1_s) - float(t0_s)
        if dt <= 0.0:
            raise ValueError("average requires positive duration")
        return self.integrate(interval, column, t0_s, t1_s) / dt

    def integrate_group_absorption(
        self, interval: int, group: str, t0_s: float, t1_s: float
    ) -> float:
        if group not in GROUPS:
            raise KeyError(group)
        value = self.integrate(
            interval, f"absorption_{group}_s-1_cMpc-3", t0_s, t1_s
        )
        if value < 0.0:
            raise ValueError("canonical absorbed count became negative")
        return value

    def external_subgrid_raw(self, interval: int, group: str, time_s: float) -> float:
        if group not in GROUPS:
            raise KeyError(group)
        model = self._interval(interval)
        if group not in SUBGRID_GROUPS:
            return 0.0
        interpolator = model.external_subgrid[group]
        assert interpolator is not None
        t = float(time_s)
        if t < model.times[0] or t > model.times[-1]:
            raise ValueError("external subgrid query leaves canonical interval")
        value = float(interpolator(t))
        if not math.isfinite(value) or value < 0.0:
            raise ValueError("external subgrid response became invalid")
        return value

    def average_external_subgrid_raw(
        self, interval: int, group: str, t0_s: float, t1_s: float
    ) -> float:
        if group not in GROUPS:
            raise KeyError(group)
        if group not in SUBGRID_GROUPS:
            return 0.0
        model = self._interval(interval)
        interpolator = model.external_subgrid[group]
        assert interpolator is not None
        dt = float(t1_s) - float(t0_s)
        if dt <= 0.0:
            raise ValueError("average requires positive duration")
        value = float(interpolator.integrate(float(t0_s), float(t1_s))) / dt
        if not math.isfinite(value) or value < 0.0:
            raise ValueError("averaged external subgrid response became invalid")
        return value
