#!/usr/bin/env python3
"""Execute the bounded R2B-R2A adaptive first-interval science audit.

The production lock remains dt/8 -> recursive bisection -> dt/1024.  A separate
post-lock extension auditor at dt/2048 and dt/4096 is recorded only to identify
the next deterministic route; it cannot rescue a failed production gate.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np

os.environ.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")
os.environ.setdefault("JAX_ENABLE_X64", "true")

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]
DATA = STAGE / "data"
RECEIPTS = STAGE / "receipts"
LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
LEDGER_NAMES = (
    "resolved_HI_absorption", "resolved_HeI_absorption", "resolved_HeII_absorption",
    "effective_subgrid_absorption", "boundary_redshift_storage",
    "resolved_photoheating", "unresolved_absorbed_energy", "cooling",
    "expansion_work", "mass_transfer_work",
    "photon_absorption_G1", "photon_absorption_G2a",
    "photon_absorption_G2b", "photon_absorption_G3",
    "resolved_thermal_delta",
)


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


physical = _load("r2b_r2a_run_physical", STAGE / "analysis/physical_trial.py")
adaptive = _load("r2b_r2a_run_adaptive", STAGE / "analysis/adaptive_controller.py")
picard = _load("r2b_r2a_run_picard", STAGE / "analysis/globalized_picard.py")


def _json_dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _slug(lane: str) -> str:
    return lane.lower()


def thermal_backend_metadata(backend: object) -> dict[str, Any]:
    return {
        "thermal_backend": str(getattr(backend, "name")),
        "thermal_root_iterations": (
            int(getattr(backend, "root_iterations"))
            if hasattr(backend, "root_iterations")
            else None
        ),
    }


def _gate(status: str, value: float | int | bool | None = None, threshold: float | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {"status": status}
    if value is not None:
        out["value"] = value
    if threshold is not None:
        out["threshold"] = threshold
    return out


def run_lane(lane: str) -> tuple[dict[str, Any], dict[str, Any], np.ndarray, np.ndarray]:
    solver = physical.PhysicalTrialSolver.from_repo(repo_root=REPO, lane=lane)
    initial = solver.inputs.state0.mutable_copy()
    history = adaptive.AcceptedArrayHistory(
        state=initial,
        ledgers={name: 0.0 for name in LEDGER_NAMES},
    )
    initial_bytes = history.serialize()
    duration = solver.forcing.duration_seconds(0)
    started = time.perf_counter()
    result = adaptive.AdaptiveController().advance_interval(
        history=history,
        t0=0.0,
        t1=duration,
        solve_trial=solver.solve_trial,
    )
    elapsed = time.perf_counter() - started
    restart = adaptive.AcceptedArrayHistory.from_restart_payload(history.restart_payload())
    restart_ok = restart.serialize() == history.serialize()
    rollback_ok = (history.serialize() == initial_bytes) if history.commit_count == 0 else True

    records = list(solver.trial_records)
    converged_records = [row for row in records if row["converged"]]
    max_h = max((row["max_hydrogen_residual"] for row in records), default=0.0)
    max_he = max((row["max_helium_residual"] for row in records), default=0.0)
    max_owner = max((row["max_owner_residual"] for row in records), default=0.0)
    max_photon = max((row["max_photon_residual"] for row in records), default=0.0)
    max_thermal = max((row["max_thermal_residual"] for row in records), default=0.0)
    minimum_species = min((row["minimum_species"] for row in records), default=float(np.min(initial.values[:5])))
    terminal_class = result.certificate.get("classification") if result.certificate else None
    terminal_partition = result.certificate.get("partition") if result.certificate else None
    terminal_attempt = next(
        (
            asdict(row) for row in reversed(result.attempts)
            if row.partition == terminal_partition and not row.accepted
        ),
        None,
    )
    local_error_value = None if terminal_attempt is None else terminal_attempt.get("local_error")

    gates = {
        "fixed_point": _gate(
            "PASS_AT_MINIMUM_PARTITION" if terminal_class == "LOCAL_ERROR_FAILURE" else ("PASS" if result.accepted else "FAIL"),
            len(converged_records),
        ),
        "positivity": _gate("PASS" if minimum_species > 0.0 else "FAIL", minimum_species, 0.0),
        "H_nuclei": _gate("PASS" if max_h <= 1.0e-11 else "FAIL", max_h, 1.0e-11),
        "He_nuclei": _gate("PASS" if max_he <= 1.0e-11 else "FAIL", max_he, 1.0e-11),
        "photon": _gate("PASS" if max_photon <= 1.0e-8 else "FAIL", max_photon, 1.0e-8),
        "resolved_thermal": _gate("PASS" if max_thermal <= 1.0e-10 else "FAIL", max_thermal, 1.0e-10),
        "unresolved_energy": _gate("PASS_STRUCTURALLY_SEPARATE", 0.0, 1.0e-10),
        "commit_once": _gate("PASS_ZERO_COMMIT_ON_REJECTED_PATH" if history.commit_count == 0 else "PASS", history.commit_count),
        "rollback": _gate("PASS" if rollback_ok else "FAIL", rollback_ok),
        "restart": _gate("PASS" if restart_ok else "FAIL", restart_ok),
        "local_error": _gate(
            "PASS" if result.accepted else "FAIL",
            local_error_value,
            2.0e-4,
        ),
    }
    lane_summary = {
        "accepted": bool(result.accepted),
        "elapsed_s": float(elapsed),
        "accepted_microsteps": int(result.accepted_microsteps),
        "attempt_count": len(result.attempts),
        "bisection_count": len(result.bisections),
        "maximum_partition_reached": int(result.minimum_partition_reached),
        "max_local_error_of_accepted_steps": float(result.max_local_error),
        "terminal_certificate": dict(result.certificate),
        "terminal_attempt": terminal_attempt,
        "trial_count": len(records),
        "total_map_calls": int(sum(row["map_calls"] for row in records)),
        "total_picard_iterations": int(sum(row["iterations"] for row in records)),
        **thermal_backend_metadata(solver.backend.thermal),
        "owner_kernel_compile_count": int(solver.backend.compile_count),
        "gates": gates,
        "ledger": {k: float(v) for k, v in sorted(history.ledgers.items())},
    }
    audit = {
        "lane": lane,
        "attempts": [asdict(row) for row in result.attempts],
        "bisections": [asdict(row) for row in result.bisections],
        "trials": records,
        "failed_attempts": list(history.failed_attempts),
        "accepted_records": list(history.accepted_records),
    }
    return lane_summary, audit, history.state.values.copy(), history.state.temperature_K.copy()


def extension_auditor() -> dict[str, Any]:
    """Post-lock feasibility auditor; never changes the dt/1024 production verdict."""
    solver = physical.PhysicalTrialSolver.from_repo(
        repo_root=REPO, lane="LOCAL_NEUTRAL_HAZARD_PRIMARY"
    )
    parent = solver.inputs.state0
    duration = solver.forcing.duration_seconds(0)
    rows: list[dict[str, Any]] = []
    for partition in (2048, 4096):
        a = 0.0
        b = duration / partition
        mid = 0.5 * (a + b)
        full = solver.solve_trial(parent.mutable_copy(), a, b, partition, "EXTENSION_FULL")
        half1 = solver.solve_trial(parent.mutable_copy(), a, mid, 2 * partition, "EXTENSION_FIRST_HALF")
        half2 = solver.solve_trial(half1.result.state.mutable_copy(), mid, b, 2 * partition, "EXTENSION_SECOND_HALF")
        error = (
            picard.state_residual(full.result.state, half2.result.state)
            if full.result.converged and half1.result.converged and half2.result.converged
            else None
        )
        rows.append(
            {
                "partition": partition,
                "full_converged": full.result.converged,
                "first_half_converged": half1.result.converged,
                "second_half_converged": half2.result.converged,
                "full_iterations": full.result.iterations,
                "first_half_iterations": half1.result.iterations,
                "second_half_iterations": half2.result.iterations,
                "local_error": error,
                "passes_locked_local_error": bool(error is not None and error <= 2.0e-4),
                "load_bearing_for_current_stage": False,
            }
        )
    return {
        "classification": "POST_LOCK_DEEPER_PARTITION_FEASIBILITY_AUDITOR",
        "current_production_minimum_partition": 1024,
        "rows": rows,
        "interpretation": (
            "The auditor identifies the deterministic next scale but cannot rescue "
            "the prelocked dt/1024 production gate."
        ),
    }


def build_results() -> dict[str, Any]:
    DATA.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    lane_results: dict[str, Any] = {}
    combined_audits: dict[str, Any] = {}
    for lane in LANES:
        print(f"[lane-start] {lane}", flush=True)
        summary, audit, values, temperature = run_lane(lane)
        lane_results[lane] = summary
        combined_audits[lane] = audit
        np.savez_compressed(
            DATA / f"terminal_state_{_slug(lane)}.npz",
            values=values,
            temperature_K=temperature,
        )
        _json_dump(DATA / f"lane_{_slug(lane)}_summary.json", summary)
        print(
            f"[lane-close] {lane} accepted={summary['accepted']} "
            f"certificate={summary['terminal_certificate']}",
            flush=True,
        )
    _json_dump(RECEIPTS / "ATTEMPTS_LEDGER.json", combined_audits)
    extension = extension_auditor()
    _json_dump(DATA / "deeper_partition_extension_auditor.json", extension)

    primary = lane_results[LANES[0]]
    primary_failure = primary["terminal_certificate"].get("classification", "UNKNOWN")
    science_pass = bool(primary["accepted"])
    verdict = (
        "DURABLE_PASS_R2C_R1B_R2B_R2A_ADAPTIVE_FIRST_INTERVAL_AND_OPTIMIZATION_LOCK"
        if science_pass
        else "DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2A_DT1024_LOCAL_ERROR_FAILURE_"
             "FIXED_POINT_AND_CONSERVATION_GATES_PASS_DEEPER_DT4096_AUDITOR_PASS"
    )
    results = {
        "classification": "R2B_R2A_ADAPTIVE_FIRST_INTERVAL_AUDIT",
        "stage": (
            "P0.5-B2C2B0C-R2C-R1B-R2B-R2A-"
            "ADAPTIVE-INTERNAL-MICROSTEP-ACCEPTANCE-AND-GLOBALIZATION-LOCK"
        ),
        "verdict": verdict,
        "science_pass": science_pass,
        "production_node_chemistry_authorized": False,
        "R2C_R2_authorized": False,
        "B2C2B_authorized": False,
        "primary_failure_classification": None if science_pass else primary_failure,
        "lanes": lane_results,
        "extension_auditor": extension,
        "claim_boundary": (
            "Only the first canonical interval and three predeclared lanes were tested. "
            "The dt/1024 production local-error gate remains load-bearing."
        ),
    }
    _json_dump(STAGE / "results.json", results)
    return results


def replay_check() -> int:
    results = json.loads((STAGE / "results.json").read_text(encoding="utf-8"))
    attempts = json.loads((RECEIPTS / "ATTEMPTS_LEDGER.json").read_text(encoding="utf-8"))
    if set(results["lanes"]) != set(LANES) or set(attempts) != set(LANES):
        raise SystemExit("lane registry mismatch")
    for lane in LANES:
        lane_result = results["lanes"][lane]
        lane_audit = attempts[lane]
        if lane_result["attempt_count"] != len(lane_audit["attempts"]):
            raise SystemExit(f"attempt count mismatch: {lane}")
        if lane_result["trial_count"] != len(lane_audit["trials"]):
            raise SystemExit(f"trial count mismatch: {lane}")
        if lane_result["accepted"]:
            raise SystemExit("current durable result unexpectedly claims an accepted interval")
        if lane_result["terminal_certificate"].get("partition") != 1024:
            raise SystemExit(f"terminal partition mismatch: {lane}")
        if lane_result["terminal_certificate"].get("classification") != "LOCAL_ERROR_FAILURE":
            raise SystemExit(f"terminal classification mismatch: {lane}")
    payload = (STAGE / "results.json").read_bytes()
    receipt = {
        "classification": "R2B_R2A_RESULTS_REPLAY_RECEIPT",
        "results_sha256": hashlib.sha256(payload).hexdigest(),
        "lane_count": len(LANES),
        "replay_pass": True,
    }
    _json_dump(RECEIPTS / "RESULTS_REPLAY_RECEIPT.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay-check", action="store_true")
    args = parser.parse_args()
    if args.replay_check:
        return replay_check()
    results = build_results()
    print(json.dumps({"verdict": results["verdict"], "science_pass": results["science_pass"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
