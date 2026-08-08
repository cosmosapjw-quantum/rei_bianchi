#!/usr/bin/env python3
"""Locked performance decision and timing helpers for R2B-R2A."""
from __future__ import annotations
from dataclasses import dataclass
import time
import tracemalloc
from typing import Callable, Any

@dataclass(frozen=True)
class BackendDecision:
    promoted: bool
    reason: str
    speedup: float
    memory_reduction_fraction: float
    science_authorization_changed: bool = False


def decide_backend(*, legacy_seconds: float, candidate_seconds: float,
                   legacy_peak_bytes: int, candidate_peak_bytes: int,
                   parity_pass: bool) -> BackendDecision:
    if legacy_seconds <= 0 or candidate_seconds <= 0 or legacy_peak_bytes < 0 or candidate_peak_bytes < 0:
        raise ValueError("benchmark values must be positive/nonnegative")
    speedup = legacy_seconds / candidate_seconds
    memory_reduction = 0.0 if legacy_peak_bytes == 0 else 1.0 - candidate_peak_bytes/legacy_peak_bytes
    if not parity_pass:
        return BackendDecision(False,"PARITY_FAILED",speedup,memory_reduction)
    if speedup >= 5.0:
        return BackendDecision(True,"SPEEDUP_AT_LEAST_5X",speedup,memory_reduction)
    if speedup >= 3.0 and memory_reduction >= 0.5:
        return BackendDecision(True,"SPEEDUP_3X_AND_MEMORY_50_PERCENT",speedup,memory_reduction)
    return BackendDecision(False,"PERFORMANCE_THRESHOLD_NOT_MET",speedup,memory_reduction)

@dataclass(frozen=True)
class Timing:
    seconds: float
    peak_bytes: int
    repetitions: int


def measure(function: Callable[[], Any], *, repetitions: int) -> Timing:
    if repetitions <= 0:
        raise ValueError("repetitions must be positive")
    tracemalloc.start()
    start=time.perf_counter_ns()
    for _ in range(repetitions): function()
    elapsed=(time.perf_counter_ns()-start)*1e-9
    _current,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    return Timing(elapsed,int(peak),int(repetitions))
