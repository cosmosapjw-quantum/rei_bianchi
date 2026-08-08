#!/usr/bin/env python3
"""Transactional full/two-half adaptive internal-microstep controller.

The canonical interval is first partitioned into exactly eight equal internal
steps.  Only a failed step is recursively bisected, never a previously accepted
sibling.  Each attempt evaluates one full trial and two sequential half trials
on detached states.  The two-half result is committed exactly once only after
all trial gates and the locked local-error gate close.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import importlib.util
import io
import json
import math
from pathlib import Path
import struct
import sys
from typing import Callable, Mapping, Any

import numpy as np

_HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, _HERE / filename)
    if spec is None or spec.loader is None:
        raise ImportError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


tensor = _load("r2b_r2a_tensorized_controller", "tensorized_inputs.py")
picard = _load("r2b_r2a_globalized_controller", "globalized_picard.py")
ArrayState = tensor.ArrayState
TrialResult = picard.TrialResult


@dataclass(frozen=True)
class MicroTrial:
    result: TrialResult
    ledger_delta: Mapping[str, float]


@dataclass(frozen=True)
class AttemptRecord:
    partition: int
    t0: float
    t1: float
    full_converged: bool
    first_half_converged: bool
    second_half_converged: bool
    local_error: float | None
    accepted: bool
    classification: str | None
    failed_trial: str | None


@dataclass(frozen=True)
class BisectionRecord:
    parent_partition: int
    child_partition: int
    t0: float
    t1: float
    reason: str


@dataclass(frozen=True)
class AdaptiveIntervalResult:
    accepted: bool
    accepted_microsteps: int
    attempts: tuple[AttemptRecord, ...]
    bisections: tuple[BisectionRecord, ...]
    max_local_error: float
    minimum_partition_reached: int
    certificate: dict[str, Any]


def _copy_state(state: ArrayState) -> ArrayState:
    return ArrayState(state.values.copy(), state.temperature_K.copy())


def _combine_ledgers(a: Mapping[str, float], b: Mapping[str, float]) -> dict[str, float]:
    keys = set(a) | set(b)
    return {key: math.fsum((float(a.get(key, 0.0)), float(b.get(key, 0.0)))) for key in sorted(keys)}


class AcceptedArrayHistory:
    """Accepted material state and ledgers with deterministic restart bytes."""

    MAGIC = b"R2B-R2A-ADAPTIVE\0"

    def __init__(self, *, state: ArrayState, ledgers: Mapping[str, float], commit_count: int = 0) -> None:
        self.state = _copy_state(state)
        self.ledgers = {str(k): float(v) for k, v in ledgers.items()}
        self.commit_count = int(commit_count)
        self.failed_attempts: list[dict[str, Any]] = []
        self.accepted_records: list[dict[str, Any]] = []

    def commit(self, *, state: ArrayState, ledger_delta: Mapping[str, float], metadata: Mapping[str, Any]) -> None:
        self.state = _copy_state(state)
        for key in sorted(set(self.ledgers) | set(ledger_delta)):
            self.ledgers[key] = math.fsum((self.ledgers.get(key, 0.0), float(ledger_delta.get(key, 0.0))))
        self.commit_count += 1
        self.accepted_records.append(dict(metadata))

    def record_failure(self, payload: Mapping[str, Any]) -> None:
        self.failed_attempts.append(dict(payload))

    def serialize(self) -> bytes:
        return self.restart_payload()

    def restart_payload(self) -> bytes:
        header = json.dumps(
            {
                "commit_count": self.commit_count,
                "ledgers": {k: float(v).hex() for k, v in sorted(self.ledgers.items())},
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        values = np.ascontiguousarray(self.state.values, dtype="<f8")
        temperature = np.ascontiguousarray(self.state.temperature_K, dtype="<f8")
        out = bytearray(self.MAGIC)
        out += struct.pack("<Q", len(header)) + header
        out += struct.pack("<QQ", values.shape[0], values.shape[1]) + values.tobytes()
        out += struct.pack("<Q", temperature.size) + temperature.tobytes()
        return bytes(out)

    @classmethod
    def from_restart_payload(cls, payload: bytes) -> "AcceptedArrayHistory":
        stream = io.BytesIO(payload)
        if stream.read(len(cls.MAGIC)) != cls.MAGIC:
            raise ValueError("invalid adaptive restart magic")
        (header_size,) = struct.unpack("<Q", stream.read(8))
        header = json.loads(stream.read(header_size).decode("utf-8"))
        rows, cols = struct.unpack("<QQ", stream.read(16))
        raw = stream.read(8 * rows * cols)
        if len(raw) != 8 * rows * cols:
            raise ValueError("truncated state values")
        values = np.frombuffer(raw, dtype="<f8").reshape(rows, cols).copy()
        (n_temperature,) = struct.unpack("<Q", stream.read(8))
        raw_t = stream.read(8 * n_temperature)
        if len(raw_t) != 8 * n_temperature or stream.read(1):
            raise ValueError("truncated or trailing restart data")
        temperature = np.frombuffer(raw_t, dtype="<f8").copy()
        ledgers = {k: float.fromhex(v) for k, v in header["ledgers"].items()}
        return cls(
            state=ArrayState(values, temperature),
            ledgers=ledgers,
            commit_count=int(header["commit_count"]),
        )


class AdaptiveController:
    def __init__(
        self,
        *,
        initial_partition: int = 8,
        minimum_partition: int = 1024,
        local_error_tolerance: float = 2.0e-4,
    ) -> None:
        self.initial_partition = int(initial_partition)
        self.minimum_partition = int(minimum_partition)
        self.local_error_tolerance = float(local_error_tolerance)
        if self.initial_partition != 8:
            raise ValueError("production controller must start at dt/8")
        if self.minimum_partition != 1024:
            raise ValueError("production minimum partition must be dt/1024")
        if self.minimum_partition < self.initial_partition or (
            self.minimum_partition & (self.minimum_partition - 1)
        ):
            raise ValueError("minimum partition must be a power of two >= initial")

    @staticmethod
    def _trial_copy(state: ArrayState) -> ArrayState:
        return _copy_state(state)

    def advance_interval(
        self,
        *,
        history: AcceptedArrayHistory,
        t0: float,
        t1: float,
        solve_trial: Callable[[ArrayState, float, float, int, str], MicroTrial],
    ) -> AdaptiveIntervalResult:
        start = float(t0); stop = float(t1)
        if not (math.isfinite(start) and math.isfinite(stop) and stop > start):
            raise ValueError("invalid interval")
        attempts: list[AttemptRecord] = []
        bisections: list[BisectionRecord] = []
        max_local_error = 0.0
        min_partition_reached = self.initial_partition
        accepted_at_start = history.commit_count
        terminal_certificate: dict[str, Any] = {}

        def attempt_segment(a: float, b: float, partition: int) -> bool:
            nonlocal max_local_error, min_partition_reached, terminal_certificate
            min_partition_reached = max(min_partition_reached, partition)
            parent_bytes = history.serialize()
            parent_state = self._trial_copy(history.state)
            mid = 0.5 * (a + b)

            full = solve_trial(self._trial_copy(parent_state), a, b, partition, "FULL")
            if not full.result.converged:
                classification = full.result.certificate.get("classification", "FIXED_POINT_NONCONVERGENCE")
                attempts.append(AttemptRecord(partition,a,b,False,False,False,None,False,classification,"FULL"))
                return bisect_or_fail(a,b,partition,classification,"FULL",parent_bytes)

            half1 = solve_trial(self._trial_copy(parent_state), a, mid, 2*partition, "FIRST_HALF")
            if not half1.result.converged:
                classification = half1.result.certificate.get("classification", "FIXED_POINT_NONCONVERGENCE")
                attempts.append(AttemptRecord(partition,a,b,True,False,False,None,False,classification,"FIRST_HALF"))
                return bisect_or_fail(a,b,partition,classification,"FIRST_HALF",parent_bytes)

            half2 = solve_trial(self._trial_copy(half1.result.state), mid, b, 2*partition, "SECOND_HALF")
            if not half2.result.converged:
                classification = half2.result.certificate.get("classification", "FIXED_POINT_NONCONVERGENCE")
                attempts.append(AttemptRecord(partition,a,b,True,True,False,None,False,classification,"SECOND_HALF"))
                return bisect_or_fail(a,b,partition,classification,"SECOND_HALF",parent_bytes)

            local_error = picard.state_residual(full.result.state, half2.result.state)
            if not math.isfinite(local_error) or local_error > self.local_error_tolerance:
                attempts.append(AttemptRecord(partition,a,b,True,True,True,local_error,False,"LOCAL_ERROR_FAILURE",None))
                return bisect_or_fail(a,b,partition,"LOCAL_ERROR_FAILURE",None,parent_bytes)

            if history.serialize() != parent_bytes:
                raise RuntimeError("trial mutated accepted history before commit")
            delta = _combine_ledgers(half1.ledger_delta, half2.ledger_delta)
            history.commit(
                state=half2.result.state,
                ledger_delta=delta,
                metadata={"t0":a,"t1":b,"partition":partition,"local_error":local_error},
            )
            attempts.append(AttemptRecord(partition,a,b,True,True,True,local_error,True,None,None))
            max_local_error = max(max_local_error, local_error)
            return True

        def bisect_or_fail(
            a: float,
            b: float,
            partition: int,
            classification: str,
            failed_trial: str | None,
            parent_bytes: bytes,
        ) -> bool:
            nonlocal terminal_certificate
            if history.serialize() != parent_bytes:
                raise RuntimeError("rejected trial changed accepted parent bytes")
            history.record_failure(
                {"t0":a,"t1":b,"partition":partition,"classification":classification,"failed_trial":failed_trial}
            )
            if partition >= self.minimum_partition:
                terminal_certificate = {
                    "classification": classification,
                    "failed_trial": failed_trial,
                    "partition": partition,
                    "t0": a,
                    "t1": b,
                }
                return False
            child = 2 * partition
            bisections.append(BisectionRecord(partition,child,a,b,classification))
            mid = 0.5 * (a + b)
            if not attempt_segment(a, mid, child):
                return False
            return attempt_segment(mid, b, child)

        width = (stop - start) / self.initial_partition
        accepted = True
        for i in range(self.initial_partition):
            a = start + i * width
            b = stop if i == self.initial_partition - 1 else start + (i + 1) * width
            if not attempt_segment(a, b, self.initial_partition):
                accepted = False
                break

        return AdaptiveIntervalResult(
            accepted=accepted,
            accepted_microsteps=history.commit_count - accepted_at_start,
            attempts=tuple(attempts),
            bisections=tuple(bisections),
            max_local_error=max_local_error,
            minimum_partition_reached=min_partition_reached,
            certificate={} if accepted else terminal_certificate,
        )
