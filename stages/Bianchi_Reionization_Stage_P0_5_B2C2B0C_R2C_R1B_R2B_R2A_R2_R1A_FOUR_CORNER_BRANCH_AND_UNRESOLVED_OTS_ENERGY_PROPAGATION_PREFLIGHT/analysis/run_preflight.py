#!/usr/bin/env python3
"""Run the 24-policy first-microstep branch/OTS uncertainty preflight."""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]
DATA = STAGE / "data"
RECEIPTS = STAGE / "receipts"

LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
PARTITION = 2048
LOCAL_ERROR_TOL = 2.0e-4


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


policy_mod = _load("r2b_r2a_r2_r1a_runner_policy", STAGE / "analysis/uncertainty_policy.py")
trial_mod = _load("r2b_r2a_r2_r1a_runner_trial", STAGE / "analysis/uncertainty_trial.py")


def execution_registry_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lane in LANES:
        for policy in policy_mod.policy_registry():
            rows.append(
                {
                    "shape_lane": lane,
                    "policy_id": policy.policy_id,
                    "v_policy": policy.v_policy,
                    "f_value": policy.f_value,
                    "load_bearing": bool(policy.load_bearing),
                    "energy_policy": "UNRESOLVED_OTS_LEDGER_NO_STATE_AXIS",
                }
            )
    return rows


def block_errors(full, half) -> dict[str, float]:
    a = np.asarray(full.values, dtype=np.float64)
    b = np.asarray(half.values, dtype=np.float64)
    nh_a = a[0] + a[1]
    nh_b = b[0] + b[1]
    he_a = a[2] + a[3] + a[4]
    he_b = b[2] + b[3] + b[4]
    return {
        "x_HII": float(np.max(np.abs(a[1] / nh_a - b[1] / nh_b))),
        "x_HeII": float(np.max(np.abs(a[3] / he_a - b[3] / he_b))),
        "x_HeIII": float(np.max(np.abs(a[4] / he_a - b[4] / he_b))),
        "log_T": float(
            np.max(np.abs(np.log(full.temperature_K) - np.log(half.temperature_K)))
        ),
    }


def trial_gates(*trials) -> tuple[bool, dict[str, float]]:
    metrics = {
        "max_H_residual": max(t.hydrogen_residual for t in trials),
        "max_He_residual": max(t.helium_residual for t in trials),
        "max_owner_residual": max(t.owner_residual for t in trials),
        "max_photon_residual": max(t.photon_residual for t in trials),
        "max_thermal_residual": max(t.thermal_residual for t in trials),
        "max_PDS_residual": max(t.pds_reconstruction_residual for t in trials),
        "minimum_species": min(t.minimum_species for t in trials),
        "max_augmented_energy_residual": max(
            float(t.certificate.get("max_augmented_energy_residual", np.inf))
            for t in trials
        ),
        "max_photon_branch_identity_residual": max(
            float(t.certificate.get("max_photon_branch_identity_residual", np.inf))
            for t in trials
        ),
        "max_thermal_event_outer_residual": max(
            float(t.certificate.get("thermal_event_outer_residual", np.inf))
            for t in trials
        ),
        "branch_domain_failure_count": max(
            int(t.certificate.get("branch_domain_failure_count", 1)) for t in trials
        ),
        "legacy_rhs_calls": max(
            int(t.certificate.get("legacy_rhs_calls", 1)) for t in trials
        ),
    }
    passed = (
        all(t.converged for t in trials)
        and metrics["max_H_residual"] <= 1.0e-11
        and metrics["max_He_residual"] <= 1.0e-11
        and metrics["max_owner_residual"] <= 1.0e-11
        and metrics["max_photon_residual"] <= 1.0e-8
        and metrics["max_thermal_residual"] <= 1.0e-10
        and metrics["max_PDS_residual"] <= 1.0e-11
        and metrics["max_augmented_energy_residual"] <= 1.0e-10
        and metrics["max_photon_branch_identity_residual"] <= 1.0e-12
        and metrics["max_thermal_event_outer_residual"] <= 1.0e-10
        and metrics["branch_domain_failure_count"] == 0
        and metrics["legacy_rhs_calls"] == 0
        and metrics["minimum_species"] > 0.0
    )
    return bool(passed), metrics


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _enclosure_arrays(states: list[Any]) -> dict[str, np.ndarray]:
    values = np.stack([np.asarray(s.values, dtype=np.float64) for s in states], axis=0)
    temperature = np.stack([np.asarray(s.temperature_K, dtype=np.float64) for s in states])
    nh = values[:, 0] + values[:, 1]
    nhe = values[:, 2] + values[:, 3] + values[:, 4]
    blocks = {
        "x_HII": values[:, 1] / nh,
        "x_HeII": values[:, 3] / nhe,
        "x_HeIII": values[:, 4] / nhe,
        "log_T": np.log(temperature),
    }
    result: dict[str, np.ndarray] = {}
    for name, array in blocks.items():
        result[f"{name}_lower"] = np.min(array, axis=0)
        result[f"{name}_upper"] = np.max(array, axis=0)
        result[f"{name}_width"] = result[f"{name}_upper"] - result[f"{name}_lower"]
    return result


def run() -> dict[str, Any]:
    DATA.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    registry = execution_registry_rows()
    _write_csv(DATA / "BRANCH_POLICY_REGISTRY.csv", registry)

    lock = json.loads((STAGE / "INPUT_LOCK.json").read_text(encoding="utf-8"))
    uncertainty_gate = lock["uncertainty_gate"]
    rows: list[dict[str, Any]] = []
    load_states: dict[str, list[Any]] = {lane: [] for lane in LANES}
    load_policy_ids: dict[str, list[str]] = {lane: [] for lane in LANES}
    parent_hashes: dict[str, str] = {}

    for lane in LANES:
        shared_base = trial_mod.fast.base.physical.PhysicalTrialSolver.from_repo(
            repo_root=REPO, lane=lane
        )
        parent = shared_base.inputs.state0.mutable_copy()
        parent_bytes = (parent.values.tobytes(), parent.temperature_K.tobytes())
        parent_hashes[lane] = str(hash(parent_bytes))
        duration = shared_base.forcing.duration_seconds(0)
        t0 = 0.0
        t1 = duration / PARTITION
        midpoint = 0.5 * t1
        for policy in policy_mod.policy_registry():
            solver = trial_mod.UncertaintySecondOrderTrial(
                base=shared_base,
                lane=lane,
                v_policy=policy.v_policy,
                f_value=policy.f_value,
            )
            started = time.perf_counter()
            full = solver.solve(
                state=parent, t0=t0, t1=t1, partition=PARTITION, trial_kind="FULL"
            )
            half1 = solver.solve(
                state=parent,
                t0=t0,
                t1=midpoint,
                partition=2 * PARTITION,
                trial_kind="FIRST_HALF",
            )
            half2 = (
                solver.solve(
                    state=half1.state,
                    t0=midpoint,
                    t1=t1,
                    partition=2 * PARTITION,
                    trial_kind="SECOND_HALF",
                )
                if half1.converged
                else half1
            )
            elapsed = time.perf_counter() - started
            converged = full.converged and half1.converged and half2.converged
            errors = (
                block_errors(full.state, half2.state)
                if converged
                else {name: None for name in ("x_HII", "x_HeII", "x_HeIII", "log_T")}
            )
            local_error = max(errors.values()) if converged else None
            gates, metrics = trial_gates(full, half1, half2)
            row: dict[str, Any] = {
                "shape_lane": lane,
                "policy_id": policy.policy_id,
                "v_policy": policy.v_policy,
                "f_value": policy.f_value,
                "load_bearing": bool(policy.load_bearing),
                "partition": PARTITION,
                "converged": bool(converged),
                "all_hard_gates_pass": bool(gates),
                "local_error": local_error,
                "local_error_pass": bool(local_error is not None and local_error < LOCAL_ERROR_TOL),
                "elapsed_s": elapsed,
                **{f"error_{key}": value for key, value in errors.items()},
                **metrics,
                "full_certificate": json.dumps(full.certificate, sort_keys=True),
                "half1_certificate": json.dumps(half1.certificate, sort_keys=True),
                "half2_certificate": json.dumps(half2.certificate, sort_keys=True),
            }
            for ledger_name, value in sorted(half1.ledger_delta.items()):
                row[f"half1_ledger_{ledger_name}"] = value
            for ledger_name, value in sorted(half2.ledger_delta.items()):
                row[f"half2_ledger_{ledger_name}"] = value
            rows.append(row)
            if policy.load_bearing and converged:
                load_states[lane].append(half2.state)
                load_policy_ids[lane].append(policy.policy_id)
            if parent_bytes != (parent.values.tobytes(), parent.temperature_K.tobytes()):
                raise RuntimeError("branch trials mutated the shared parent state")

    _write_csv(DATA / "MICROSTEP_MATRIX.csv", rows)

    npz_payload: dict[str, np.ndarray] = {}
    summary_rows: list[dict[str, Any]] = []
    uncertainty_pass_by_lane: dict[str, bool] = {}
    for lane in LANES:
        if len(load_states[lane]) != 4:
            uncertainty_pass_by_lane[lane] = False
            summary_rows.append(
                {"shape_lane": lane, "classification": "MISSING_LOAD_BEARING_ENDPOINTS"}
            )
            continue
        arrays = _enclosure_arrays(load_states[lane])
        token = lane.lower()
        for name, array in arrays.items():
            npz_payload[f"{token}__{name}"] = np.asarray(array, dtype=np.float64)
        maxima = {
            "max_width_x_HII": float(np.max(arrays["x_HII_width"])),
            "max_width_x_HeII": float(np.max(arrays["x_HeII_width"])),
            "max_width_x_HeIII": float(np.max(arrays["x_HeIII_width"])),
            "max_width_log_T": float(np.max(arrays["log_T_width"])),
        }
        passed = (
            maxima["max_width_x_HII"] < float(uncertainty_gate["max_abs_width_x_HII"])
            and maxima["max_width_x_HeII"] < float(uncertainty_gate["max_abs_width_x_HeII"])
            and maxima["max_width_x_HeIII"] < float(uncertainty_gate["max_abs_width_x_HeIII"])
            and maxima["max_width_log_T"] < float(uncertainty_gate["max_width_log_T"])
        )
        uncertainty_pass_by_lane[lane] = bool(passed)
        summary_rows.append(
            {
                "shape_lane": lane,
                "load_bearing_policy_ids": ";".join(load_policy_ids[lane]),
                **maxima,
                "uncertainty_gate_pass": bool(passed),
                "classification": "PASS" if passed else "UNCERTAINTY_ENCLOSURE_TOO_WIDE",
            }
        )
    np.savez_compressed(DATA / "NODE_ENCLOSURES.npz", **npz_payload)
    _write_csv(DATA / "ENCLOSURE_SUMMARY.csv", summary_rows)

    all_hard = all(bool(row["all_hard_gates_pass"]) for row in rows)
    all_local = all(bool(row["local_error_pass"]) for row in rows)
    uncertainty_pass = all(uncertainty_pass_by_lane.values())
    if all_hard and all_local and uncertainty_pass:
        verdict = (
            "DURABLE_PASS_R2C_R1B_R2B_R2A_R2_R1A_"
            "ALL_24_BRANCH_POLICY_MICROSTEPS_CLOSE_"
            "LOAD_BEARING_ENCLOSURES_WITHIN_GATE_"
            "FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY_AUTHORIZED"
        )
        next_stage = (
            "P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1B-"
            "UNCERTAINTY-QUALIFIED-FIRST-CANONICAL-INTERVAL-ADAPTIVE-HISTORY"
        )
        authorized = True
    elif all_hard and all_local:
        verdict = (
            "DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2A_R2_R1A_"
            "BRANCH_MICROSTEPS_CLOSE_BUT_SOURCE_UNCERTAINTY_ENCLOSURE_TOO_WIDE"
        )
        next_stage = (
            "P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1B0-"
            "LOW_T_V_AND_F_SOURCE_EXTENSION_CALIBRATION"
        )
        authorized = False
    else:
        verdict = (
            "DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R2A_R2_R1A_"
            "AT_LEAST_ONE_BRANCH_POLICY_FAILS_NUMERICAL_OR_LEDGER_GATE"
        )
        next_stage = (
            "P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-"
            "EARLIEST-BRANCH-FAILURE-ROOT-CAUSE-AUDIT"
        )
        authorized = False

    result = {
        "stage": lock["stage"],
        "verdict": verdict,
        "execution_policy_count": len(rows),
        "load_bearing_policy_count": sum(bool(r["load_bearing"]) for r in rows),
        "all_hard_gates_pass": all_hard,
        "all_local_error_gates_pass": all_local,
        "uncertainty_pass_by_lane": uncertainty_pass_by_lane,
        "uncertainty_gate_pass": uncertainty_pass,
        "first_canonical_interval_authorized": authorized,
        "production_history_authorized": False,
        "production_node_chemistry_authorized": False,
        "R2C_R2_authorized": False,
        "B2C2B_authorized": False,
        "next_stage": next_stage,
        "maximum_metrics": {
            key: max(float(row[key]) for row in rows if row[key] is not None)
            for key in (
                "local_error",
                "max_H_residual",
                "max_He_residual",
                "max_owner_residual",
                "max_photon_residual",
                "max_thermal_residual",
                "max_PDS_residual",
                "max_augmented_energy_residual",
                "max_photon_branch_identity_residual",
                "max_thermal_event_outer_residual",
            )
        },
        "minimum_species": min(float(row["minimum_species"]) for row in rows),
        "enclosure_summary": summary_rows,
        "parent_hashes": parent_hashes,
    }
    (STAGE / "results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    argparse.ArgumentParser().parse_args()
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
