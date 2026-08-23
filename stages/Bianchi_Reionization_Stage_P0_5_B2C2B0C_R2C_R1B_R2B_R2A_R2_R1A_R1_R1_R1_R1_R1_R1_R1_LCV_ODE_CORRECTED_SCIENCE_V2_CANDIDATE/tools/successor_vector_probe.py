#!/usr/bin/env python3
"""Deterministic cross-module vectors for the additive corrected candidate.

This is a shadow/reference probe.  It does not invoke or route the production
history solver and it emits no scientific trajectory.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


STAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STAGE / "analysis"))
sys.path.insert(0, str(STAGE / "validation"))

import admission_contract as admission
import certificate_adapter as certificate
import corrected_physics as physics
import independent_exact_oracle as oracle
import terminal_fsm as fsm
import verified_backend as verified


def _pair(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def _binary_interval(value: verified.Binary64Interval) -> list[str]:
    return [value.lo.hex(), value.hi.hex()]


def _point_system(name: str, matrix, rhs) -> dict[str, object]:
    result = certificate.certify_point_interval_system(matrix, matrix, rhs, rhs)
    replay = oracle.verify_point_certificate(matrix, matrix, rhs, rhs, result)
    return {
        "canonical_input_digest": result.canonical_input_digest,
        "determinant": None if result.determinant is None else list(result.determinant),
        "independent_failures": list(replay.failures),
        "independent_passed": replay.passed,
        "name": name,
        "residual_exact_zero": result.residual_exact_zero,
        "solution_binary64_hex": (
            None
            if result.solution_binary64 is None
            else [_binary_interval(item) for item in result.solution_binary64]
        ),
        "solution_exact": (
            None
            if result.solution_exact is None
            else [list(item) for item in result.solution_exact]
        ),
        "status": result.status.value,
    }


def _admission() -> dict[str, object]:
    rows = tuple(
        admission.GateEvidence(
            gate=gate,
            verdict=admission.GateVerdict.PASS,
            authority=admission.REQUIRED_AUTHORITY[gate],
            evidence_sha256=hashlib.sha256(
                ("successor-vector:" + gate.value).encode("ascii")
            ).hexdigest(),
        )
        for gate in admission.RequiredGate
    )
    complete = admission.adjudicate(
        outcome=admission.SolverOutcome.SOLVED,
        evidence=rows,
        worker_claimed_success=True,
    )
    missing = admission.adjudicate(
        outcome=admission.SolverOutcome.SOLVED,
        evidence=rows[:-1],
        worker_claimed_success=True,
    )
    return {
        "complete": {
            "digest": complete.evidence_digest,
            "reasons": list(complete.reasons),
            "status": complete.status.value,
        },
        "missing_one": {
            "digest": missing.evidence_digest,
            "reasons": list(missing.reasons),
            "status": missing.status.value,
        },
        "worker_claim_has_authority": False,
    }


def _terminal_absorption() -> dict[str, object]:
    state = fsm.RunState(
        phase=fsm.RunPhase.TERMINAL,
        terminal_outcome=fsm.TerminalOutcome.BLOCKED_EVENT,
        transition_number=7,
        generation_number=3,
        regime_epoch=2,
    )
    before = fsm.canonical_state_bytes(state)
    result = fsm.transition(state, "MALFORMED_ACTION")
    after = fsm.canonical_state_bytes(result.state)
    return {
        "byte_identical": before == after,
        "code": result.code.value,
        "state_sha256": hashlib.sha256(before).hexdigest(),
        "write_required": result.write_required,
    }


def collect() -> dict[str, object]:
    exact_sum = verified.exact_sum_binary64([1.0e20, 1.0, -1.0e20])
    assert exact_sum.value is not None
    opacity = physics.atomic_opacity_per_h(
        absorber_counts=(500, 0, 79),
        hydrogen_nuclei_total=1000,
        helium_nuclei_total=79,
        declared_yhe=Fraction(79, 1000),
        sigma_cm2=(2, 3, 5),
        geometric_scale=7,
    )
    assert opacity.raw_exact is not None and opacity.per_h_abundance_exact is not None
    partition = physics.direct_opacity_partition(
        owner_names=("HI", "HeI", "HeII"), raw_opacity=(3, 5, 2)
    )
    assert partition.shares_exact is not None
    vacuum = physics.direct_opacity_partition(
        owner_names=("HI", "HeI", "HeII"),
        raw_opacity=(0, 0, 0),
        authoritative_current=1,
    )
    return {
        "admission": _admission(),
        "arithmetic": {
            "binary64_hex": _binary_interval(exact_sum.value.binary64),
            "exact": _pair(exact_sum.value.exact),
            "status": exact_sum.status.value,
        },
        "physics": {
            "abundance_exact": [_pair(item) for item in opacity.per_h_abundance_exact],
            "opacity_exact": [_pair(item) for item in opacity.raw_exact],
            "opacity_status": opacity.status.value,
            "partition_shares_exact": [_pair(item) for item in partition.shares_exact],
            "partition_status": partition.status.value,
            "vacuum_status": vacuum.status.value,
        },
        "point_systems": [
            _point_system("simple", [[2, -1], [-5, 3]], [1, 1]),
            _point_system("m_matrix", [[11, -10000], [-10, 10001]], [1, 2]),
        ],
        "probe_schema": "rei-corrected-successor-vector/v1",
        "terminal_fsm": _terminal_absorption(),
    }


def main() -> int:
    print(json.dumps(collect(), allow_nan=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
