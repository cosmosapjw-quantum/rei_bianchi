#!/usr/bin/env python3
"""Deterministic, non-production witnesses against immutable predecessors.

The probe loads helper/controller code directly, uses exact rational oracles,
and monkeypatches all controller writes/workers. It never launches the history,
parity, package, BDF, or production paths.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REPO = STAGE.parents[1]
V_ARITH = REPO / "stages" / (
    "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
    "R1_VALIDATED_CONTINUOUS_BRANCH_DIFFERENTIAL_INCLUSION_ENCLOSURE_LOCK"
) / "analysis/interval_arithmetic.py"
C_CERT = REPO / "stages" / (
    "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
    "R1_R1_R1_R1_EVALUATION_SITE_SPARSE_GENERATOR_VALIDATED_MPRK22_"
    "SDIRK2_DISCRETE_MAP_ENCLOSURE_LOCK"
) / "analysis/implicit_certificates.py"
A_STAGE = REPO / "stages" / (
    "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
    "R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_"
    "ADAPTIVE_HISTORY"
)


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _signed_sum(arithmetic: Any) -> dict[str, Any]:
    values = np.array([1.0e20, 1.0, -1.0e20], dtype=np.float64)
    observed = arithmetic.sum_interval(values)
    exact = sum((Fraction.from_float(float(x)) for x in values), Fraction(0))
    lower = float(np.asarray(observed.lo))
    upper = float(np.asarray(observed.hi))
    contained = Fraction.from_float(lower) <= exact <= Fraction.from_float(upper)
    return {
        "contains_exact": contained,
        "exact_fraction": [exact.numerator, exact.denominator],
        "input_decimal": [repr(float(x)) for x in values],
        "input_hex": [float(x).hex() for x in values],
        "returned_decimal": [repr(lower), repr(upper)],
        "returned_hex": [lower.hex(), upper.hex()],
    }


def _krawczyk(certificates: Any) -> list[dict[str, Any]]:
    systems = (
        (
            "simple",
            [[2.0, -1.0], [-5.0, 3.0]],
            [1.0, 1.0],
            [Fraction(4), Fraction(7)],
        ),
        (
            "m_matrix",
            [[11.0, -10000.0], [-10.0, 10001.0]],
            [1.0, 2.0],
            [Fraction(30001, 10011), Fraction(32, 10011)],
        ),
    )
    output: list[dict[str, Any]] = []
    for name, matrix, rhs, exact in systems:
        a = np.asarray(matrix, dtype=np.float64)[None, :, :]
        b = np.asarray(rhs, dtype=np.float64)[None, :]
        cert = certificates.linear_interval_krawczyk(a, a, b, b)
        lower = np.nextafter(cert.center[0] - cert.krawczyk_radius[0], -np.inf)
        upper = np.nextafter(cert.center[0] + cert.krawczyk_radius[0], np.inf)
        exact_float = np.asarray([float(value) for value in exact])
        output.append(
            {
                "certified": cert.certified.tolist(),
                "consumer_lower": [repr(float(value)) for value in lower],
                "consumer_upper": [repr(float(value)) for value in upper],
                "contains_exact": (
                    (lower <= exact_float) & (exact_float <= upper)
                ).tolist(),
                "exact_fraction": [
                    [value.numerator, value.denominator] for value in exact
                ],
                "name": name,
            }
        )
    return output


class _NoFilesystemTemporaryDirectory:
    def __enter__(self) -> str:
        return "/NONEXISTENT_REI_RED_PROBE"

    def __exit__(self, *_: object) -> bool:
        return False


def _terminal_witness(supervisor: Any) -> dict[str, Any]:
    original = supervisor.tempfile.TemporaryDirectory
    supervisor.tempfile.TemporaryDirectory = (
        lambda **_: _NoFilesystemTemporaryDirectory()
    )
    try:
        blocked = supervisor.Coordinator.__new__(supervisor.Coordinator)
        blocked.status = "BLOCKED_TABLE_EVENT"
        blocked.cursor = supervisor.policy.initial_cursor()
        blocked.attempts = 0
        blocked.rejects = 0
        blocked.run_dir = Path("/NONEXISTENT_REI_RED_PROBE")
        blocked.progress = None
        blocked._attempt = lambda task, directory: (
            {},
            [],
            None,
            "BLOCKED_TRANSPORT",
        )
        blocked._receipt = lambda task, jobs, rows, action: {}
        blocked._finish = lambda status, **kwargs: {
            "status": status,
            "finish_kwargs": kwargs,
        }
        blocked_result = blocked.run(max_attempts=1)

        complete = supervisor.Coordinator.__new__(supervisor.Coordinator)
        complete.status = "COMPLETE_UNSEALED"
        complete.cursor = supervisor.policy.Cursor(
            2048, supervisor.policy.TOTAL_TICKS, None, ()
        )
        calls: list[str] = []
        complete._finish = lambda status, **kwargs: (
            calls.append(status) or {"status": status}
        )
        complete_result = complete.run()
        return {
            "blocked_attempts_after_reentry": blocked.attempts,
            "blocked_before": "BLOCKED_TABLE_EVENT",
            "blocked_result": blocked_result["status"],
            "complete_before": "COMPLETE_UNSEALED",
            "complete_finish_calls": calls,
            "complete_result": complete_result["status"],
            "terminal_absorbing": blocked.attempts == 0 and not calls,
        }
    finally:
        supervisor.tempfile.TemporaryDirectory = original


def _incomplete_pass(policy: Any, task: Any, lane: str) -> dict[str, Any]:
    duration = 1.0
    widths = {name: 1.0e-6 for name in policy.WIDTH_KEYS}
    local = {name: 1.0e-7 for name in policy.WIDTH_KEYS}
    ledgers = {
        name: [-1.0e-12, 1.0e-12] for name in policy.EXPECTED_LEDGER_KEYS
    }
    key = policy.job_key(
        lane=lane,
        task=task,
        accepted_index=1,
        parent_state_sha256="INITIAL",
        input_lock_sha256="b" * 64,
        predecessor_kernel_sha256="c" * 64,
        runtime_contract_sha256="d" * 64,
    )
    return {
        "accepted_index": 1,
        "candidate_state": {
            "format": "REIADP1-deterministic-float64",
            "node_count": policy.STATE_NODE_COUNT,
            "path": "/NONEXISTENT_REI_RED_PROBE/candidate.state",
            "sha256": "a" * 64,
            "size_bytes": 1,
        },
        "classification": "PASS",
        "diagnostics": {
            "map_enclosed": True,
            "maximum_validated_local_error": max(local.values()),
            "validated_local_error_bounds": local,
        },
        "duration_seconds_hex": duration.hex(),
        "input_lock_sha256": "b" * 64,
        "interval": task.as_dict(),
        "job_key": key,
        "lane": lane,
        "parent_state_sha256": "INITIAL",
        "predecessor_kernel_sha256": "c" * 64,
        "public_widths": widths,
        "runtime_contract_sha256": "d" * 64,
        "scientific_accept": True,
        "set_ledgers": ledgers,
        "stage_id": policy.STAGE_ID,
        "table_event": {
            "any_event": False,
            "events": [],
            "minimum_distance": 0.25,
            "node_count": 0,
        },
        "time": {
            "t0_hex": 0.0.hex(),
            "t1_hex": (
                duration * task.right_tick / policy.TOTAL_TICKS
            ).hex(),
        },
        "transport_status": "OK",
        "worker_envelope_schema": 1,
    }


def _admission_witness(policy: Any) -> dict[str, Any]:
    task = policy.IntervalTask(0, 64, 0)
    rows = [_incomplete_pass(policy, task, lane) for lane in policy.LANE_ORDER]
    missing = (
        "telemetry",
        "global_error_bound",
        "qoi_error_bound",
        "event_completeness",
    )
    decision = policy.validate_and_decide(
        task=task,
        accepted_index=1,
        parent_state_sha256="INITIAL",
        input_lock_sha256="b" * 64,
        predecessor_kernel_sha256="c" * 64,
        runtime_contract_sha256="d" * 64,
        envelopes=rows,
    )
    return {
        "accepted_without_all_new_predicates": (
            decision.action == "ACCEPT"
            and all(all(name not in row for name in missing) for row in rows)
        ),
        "decision": decision.action,
        "missing_fields": list(missing),
    }


def collect() -> dict[str, Any]:
    arithmetic = _load("integrated_red_arithmetic", V_ARITH)
    certificates = _load("integrated_red_certificates", C_CERT)
    policy = _load("integrated_red_policy", A_STAGE / "analysis/adaptive_policy.py")
    supervisor = _load(
        "integrated_red_supervisor", A_STAGE / "analysis/run_adaptive_history.py"
    )
    yhe = Fraction(79, 1000)
    return {
        "admission": _admission_witness(policy),
        "heii": {
            "current_double_factor": [
                (yhe * yhe).numerator,
                (yhe * yhe).denominator,
            ],
            "declared_yhe": [yhe.numerator, yhe.denominator],
            "number_density_single_factor": [yhe.numerator, yhe.denominator],
            "ratio": [yhe.numerator, yhe.denominator],
        },
        "krawczyk": _krawczyk(certificates),
        "probe_schema": "rei-predecessor-red/v1",
        "signed_sum": _signed_sum(arithmetic),
        "source_sha256": {
            "adaptive_policy.py": _sha256(A_STAGE / "analysis/adaptive_policy.py"),
            "implicit_certificates.py": _sha256(C_CERT),
            "interval_arithmetic.py": _sha256(V_ARITH),
            "run_adaptive_history.py": _sha256(
                A_STAGE / "analysis/run_adaptive_history.py"
            ),
        },
        "terminal_fsm": _terminal_witness(supervisor),
    }


def main() -> int:
    print(json.dumps(collect(), allow_nan=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
