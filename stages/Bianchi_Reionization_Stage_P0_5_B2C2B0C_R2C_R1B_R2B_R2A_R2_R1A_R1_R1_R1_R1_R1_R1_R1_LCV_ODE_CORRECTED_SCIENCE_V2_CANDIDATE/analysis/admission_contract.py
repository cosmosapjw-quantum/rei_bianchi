#!/usr/bin/env python3
"""Closed, fail-closed admission for corrected-solver shadow evidence.

This module does not run a solver and does not promote a scientific result.  It
only decides whether a complete, independently bound evidence set is eligible
for the corrected-candidate tier.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Iterable, Mapping


class SolverOutcome(str, Enum):
    SOLVED = "SOLVED"
    FAILED = "FAILED"
    UNRESOLVED = "UNRESOLVED"


class RequiredGate(str, Enum):
    FINITE_STATE = "FINITE_STATE"
    PHYSICAL_DOMAIN = "PHYSICAL_DOMAIN"
    RESIDUAL = "RESIDUAL"
    ENCLOSURE = "ENCLOSURE"
    EXPECTED_TERMINAL = "EXPECTED_TERMINAL"
    EVENT_COMPLETENESS = "EVENT_COMPLETENESS"
    PHYSICAL_INVARIANTS = "PHYSICAL_INVARIANTS"
    DIAGNOSTICS_COMPLETE = "DIAGNOSTICS_COMPLETE"
    EXECUTION_IDENTITY = "EXECUTION_IDENTITY"
    CORRECTED_LINEAGE = "CORRECTED_LINEAGE"


class GateVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    MISSING = "MISSING"
    INCONCLUSIVE = "INCONCLUSIVE"


class EvidenceAuthority(str, Enum):
    WORKER = "WORKER"
    CONTROLLER = "CONTROLLER"
    INDEPENDENT = "INDEPENDENT"


class AdmissionStatus(str, Enum):
    ADMITTED = "ADMITTED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


_REQUIRED_AUTHORITY: dict[RequiredGate, EvidenceAuthority] = {
    RequiredGate.FINITE_STATE: EvidenceAuthority.CONTROLLER,
    RequiredGate.PHYSICAL_DOMAIN: EvidenceAuthority.CONTROLLER,
    RequiredGate.RESIDUAL: EvidenceAuthority.INDEPENDENT,
    RequiredGate.ENCLOSURE: EvidenceAuthority.INDEPENDENT,
    RequiredGate.EXPECTED_TERMINAL: EvidenceAuthority.CONTROLLER,
    RequiredGate.EVENT_COMPLETENESS: EvidenceAuthority.INDEPENDENT,
    RequiredGate.PHYSICAL_INVARIANTS: EvidenceAuthority.INDEPENDENT,
    RequiredGate.DIAGNOSTICS_COMPLETE: EvidenceAuthority.CONTROLLER,
    RequiredGate.EXECUTION_IDENTITY: EvidenceAuthority.CONTROLLER,
    RequiredGate.CORRECTED_LINEAGE: EvidenceAuthority.CONTROLLER,
}
REQUIRED_AUTHORITY: Mapping[RequiredGate, EvidenceAuthority] = MappingProxyType(
    _REQUIRED_AUTHORITY
)
REQUIRED_GATES = frozenset(RequiredGate)


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


@dataclass(frozen=True)
class GateEvidence:
    gate: RequiredGate
    verdict: GateVerdict
    authority: EvidenceAuthority
    evidence_sha256: str

    def __post_init__(self) -> None:
        if type(self.gate) is not RequiredGate:
            raise TypeError("gate must be a RequiredGate")
        if type(self.verdict) is not GateVerdict:
            raise TypeError("verdict must be a GateVerdict")
        if type(self.authority) is not EvidenceAuthority:
            raise TypeError("authority must be an EvidenceAuthority")
        if not _is_sha256(self.evidence_sha256):
            raise ValueError("evidence_sha256 must be lowercase SHA-256")


@dataclass(frozen=True)
class AdmissionDecision:
    status: AdmissionStatus
    reasons: tuple[str, ...]
    evidence_digest: str
    worker_claimed_success: bool

    def __post_init__(self) -> None:
        if type(self.status) is not AdmissionStatus:
            raise TypeError("status must be an AdmissionStatus")
        if not isinstance(self.reasons, tuple) or not all(
            isinstance(reason, str) and reason for reason in self.reasons
        ):
            raise TypeError("reasons must be a tuple of nonempty strings")
        if not _is_sha256(self.evidence_digest):
            raise ValueError("evidence_digest must be lowercase SHA-256")
        if type(self.worker_claimed_success) is not bool:
            raise TypeError("worker_claimed_success must be boolean")


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _evidence_digest(
    outcome: SolverOutcome, evidence: tuple[GateEvidence, ...]
) -> str:
    rows = [
        {
            "authority": item.authority.value,
            "evidence_sha256": item.evidence_sha256,
            "gate": item.gate.value,
            "verdict": item.verdict.value,
        }
        for item in sorted(
            evidence,
            key=lambda item: (
                item.gate.value,
                item.authority.value,
                item.verdict.value,
                item.evidence_sha256,
            ),
        )
    ]
    payload = {
        "evidence": rows,
        "outcome": outcome.value,
        "schema": "LCV_ODE_ADMISSION_EVIDENCE_V1",
    }
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def adjudicate(
    *,
    outcome: SolverOutcome,
    evidence: Iterable[GateEvidence],
    worker_claimed_success: bool = False,
) -> AdmissionDecision:
    """Return a deterministic decision; a worker success flag has no authority."""

    if type(outcome) is not SolverOutcome:
        raise TypeError("outcome must be a SolverOutcome")
    if type(worker_claimed_success) is not bool:
        raise TypeError("worker_claimed_success must be boolean")
    if isinstance(evidence, (str, bytes, bytearray)):
        raise TypeError("evidence must be an iterable of GateEvidence")
    rows = tuple(evidence)
    if not all(type(item) is GateEvidence for item in rows):
        raise TypeError("every evidence item must be GateEvidence")

    digest = _evidence_digest(outcome, rows)
    reasons: list[str] = []
    by_gate: dict[RequiredGate, GateEvidence] = {}
    duplicates: set[RequiredGate] = set()
    for item in rows:
        if item.gate in by_gate:
            duplicates.add(item.gate)
        else:
            by_gate[item.gate] = item
    for gate in sorted(duplicates, key=lambda item: item.value):
        reasons.append(f"DUPLICATE_GATE:{gate.value}")
    for gate in RequiredGate:
        item = by_gate.get(gate)
        if item is None:
            reasons.append(gate.value)
            continue
        if item.authority is not REQUIRED_AUTHORITY[gate]:
            reasons.append(f"WRONG_AUTHORITY:{gate.value}")
        if item.verdict is not GateVerdict.PASS:
            reasons.append(gate.value)

    if outcome is SolverOutcome.FAILED:
        status = AdmissionStatus.REJECTED
        reasons.insert(0, "OUTCOME:FAILED")
    elif outcome is SolverOutcome.UNRESOLVED:
        status = AdmissionStatus.BLOCKED
        reasons.insert(0, "OUTCOME:UNRESOLVED")
    elif duplicates or set(by_gate) != REQUIRED_GATES or any(
        item.authority is not REQUIRED_AUTHORITY[item.gate] for item in rows
    ):
        status = AdmissionStatus.BLOCKED
    elif any(item.verdict is GateVerdict.FAIL for item in rows):
        status = AdmissionStatus.REJECTED
    elif any(
        item.verdict in {GateVerdict.MISSING, GateVerdict.INCONCLUSIVE}
        for item in rows
    ):
        status = AdmissionStatus.BLOCKED
    elif reasons:
        status = AdmissionStatus.BLOCKED
    else:
        status = AdmissionStatus.ADMITTED

    return AdmissionDecision(
        status=status,
        reasons=tuple(dict.fromkeys(reasons)),
        evidence_digest=digest,
        worker_claimed_success=worker_claimed_success,
    )
