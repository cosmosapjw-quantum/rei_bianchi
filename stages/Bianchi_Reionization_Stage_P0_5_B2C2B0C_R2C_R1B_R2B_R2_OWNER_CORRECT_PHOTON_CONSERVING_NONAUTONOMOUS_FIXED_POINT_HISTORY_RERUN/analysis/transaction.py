#!/usr/bin/env python3
"""Accepted-step transaction and deterministic restart semantics for R2B-R2."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import importlib.util
import io
import json
from pathlib import Path
import struct
import sys
from typing import Any, Iterator, Mapping

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
STATE_FIELDS = ("N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII", "U_resolved", "T_K")


class StepRejected(RuntimeError):
    def __init__(self, classification: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(classification)
        self.classification = str(classification)
        self.details = dict(details or {})


class DuplicateCommit(RuntimeError):
    pass


@dataclass
class Candidate:
    identifier: int
    state: Any
    ledgers: dict[str, float]


class AcceptedHistory:
    def __init__(
        self,
        *,
        state: Any,
        ledgers: Mapping[str, float],
        commit_count: int = 0,
    ) -> None:
        self.state = self._copy_state(state)
        self.ledgers = {str(k): float(v) for k, v in ledgers.items()}
        self.commit_count = int(commit_count)
        self.failed_attempts: list[dict[str, Any]] = []
        self._next_identifier = self.commit_count + 1
        self._committed_ids: set[int] = set()
        self.last_committed_candidate: Candidate | None = None

    @staticmethod
    def _copy_state(state: Any) -> Any:
        return micro.MaterialBatch(
            **{field: np.asarray(getattr(state, field), dtype=float).copy() for field in STATE_FIELDS}
        )

    def _candidate(self) -> Candidate:
        candidate = Candidate(
            identifier=self._next_identifier,
            state=self._copy_state(self.state),
            ledgers=dict(self.ledgers),
        )
        self._next_identifier += 1
        return candidate

    def commit_candidate(self, candidate: Candidate | None) -> None:
        if candidate is None:
            raise ValueError("missing candidate")
        if candidate.identifier in self._committed_ids:
            raise DuplicateCommit(candidate.identifier)
        self.state = self._copy_state(candidate.state)
        self.ledgers = dict(candidate.ledgers)
        self.commit_count += 1
        self._committed_ids.add(candidate.identifier)
        self.last_committed_candidate = candidate

    @contextmanager
    def attempt(self, reason: str) -> Iterator[Candidate]:
        before = self.serialize()
        candidate = self._candidate()
        try:
            yield candidate
        except BaseException as exc:
            if self.serialize() != before:
                raise RuntimeError("accepted state mutated during rejected attempt") from exc
            classification = getattr(exc, "classification", type(exc).__name__)
            details = getattr(exc, "details", {})
            self.failed_attempts.append(
                {
                    "reason": str(reason),
                    "classification": str(classification),
                    "details": dict(details),
                    "rolled_back": True,
                }
            )
            raise
        else:
            self.commit_candidate(candidate)

    def serialize(self) -> bytes:
        return self.restart_payload()

    def restart_payload(self) -> bytes:
        header = json.dumps(
            {"ledgers": self.ledgers, "commit_count": self.commit_count},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        out = bytearray(b"R2B-R2-RESTART\0")
        out += struct.pack("<Q", len(header)) + header
        for field in STATE_FIELDS:
            array = np.ascontiguousarray(np.asarray(getattr(self.state, field), dtype="<f8"))
            name = field.encode("ascii")
            out += struct.pack("<I", len(name)) + name
            out += struct.pack("<Q", array.size)
            out += array.tobytes()
        return bytes(out)

    @classmethod
    def from_restart_payload(cls, payload: bytes) -> "AcceptedHistory":
        stream = io.BytesIO(payload)
        if stream.read(len(b"R2B-R2-RESTART\0")) != b"R2B-R2-RESTART\0":
            raise ValueError("invalid restart magic")
        (header_size,) = struct.unpack("<Q", stream.read(8))
        header = json.loads(stream.read(header_size).decode("utf-8"))
        arrays: dict[str, np.ndarray] = {}
        for expected in STATE_FIELDS:
            (name_size,) = struct.unpack("<I", stream.read(4))
            name = stream.read(name_size).decode("ascii")
            if name != expected:
                raise ValueError("restart state-field order mismatch")
            (size,) = struct.unpack("<Q", stream.read(8))
            data = stream.read(8 * size)
            if len(data) != 8 * size:
                raise ValueError("truncated restart payload")
            arrays[name] = np.frombuffer(data, dtype="<f8").copy()
        if stream.read(1):
            raise ValueError("trailing restart bytes")
        return cls(
            state=micro.MaterialBatch(**arrays),
            ledgers=header["ledgers"],
            commit_count=int(header["commit_count"]),
        )
