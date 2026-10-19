#!/usr/bin/env python3
"""Bounded first-birth native coupled control with lossless dense coefficients."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import sys
import time
import traceback

sys.dont_write_bytecode = True
from native_context import load_context, TracedNative, file_identity, save_json
import numpy as np
import scipy
from scipy.integrate import DOP853


def original_assembly_check(context, z, state, parts):
    """Replay one actual native payload through original section_rhs, no new call."""
    class Replay:
        calls = 0
        def rhs(self, proper, tcmb, mask=7):
            if (not np.array_equal(proper, parts["proper_state_14"]) or
                    tcmb != parts["tcmb_K"] or mask != 7):
                raise AssertionError("original native input differs from reduced assembly")
            self.calls += 1
            return parts["native_payload_28"].copy()
    replay = Replay()
    model = context.model
    full = model.y0.copy()
    full[:14] = context.gas_from_q(state[:5])
    full[27:27+context.active] = state[context.depth_slice]
    old_server = model.server
    model.server = replay
    try:
        value = model.section_rhs(z, full, context.active)
    finally:
        model.server = old_server
    packed = np.r_[value[context.pick]/context.scale,
        value[27:27+context.active], value[model.p:model.p+8]]
    delta = packed-parts["rhs"]
    if replay.calls != 1 or not np.allclose(packed, parts["rhs"], rtol=1e-14, atol=1e-18):
        raise AssertionError("original section_rhs compatibility failed")
    tangent_delta = context.lift @ parts["rhs"][:5] - parts["gas_rate_14"]
    return {"z": z, "replayed_original_native_payloads": replay.calls,
        "new_native_calls_for_original_replay": 0, "packed_rhs_max_abs_difference": float(abs(delta).max()),
        "packed_rhs_exact_float_equality": bool(np.array_equal(packed, parts["rhs"])),
        "gas_tangent_max_abs_roundoff": float(abs(tangent_delta).max())}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--run16-root", type=Path, required=True)
    ap.add_argument("--gas-binary", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--max-step-divisor", type=int, required=True)
    ap.add_argument("--reference-result", type=Path)
    ap.add_argument("--native-call-cap", type=int, default=250)
    ap.add_argument("--wall-cap-seconds", type=float, default=20.0)
    args = ap.parse_args()
    if args.max_step_divisor < 1:
        raise ValueError("positive maximum-step divisor required")
    start = time.perf_counter()
    context = load_context(args.source_root, args.run16_root)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    save_json(out/"INPUT_IDENTITY.json", context.input_record())
    width = context.right-context.left
    max_step = width/args.max_step_divisor
    factor = float(np.sqrt(context.dimension))
    nominal_rtol = 6e-12
    atol = np.r_[np.full(5, 1e-15), np.full(context.active, 1e-11), np.full(8, 1e-19)] / factor
    records, times, values, dense_pieces = [], [context.left], [context.initial.copy()], []
    trace = out/"NATIVE_RHS_VALUE_TRACE.jsonl"
    checks = []
    failure = None
    with TracedNative(context, args.gas_binary, trace, args.native_call_cap, args.wall_cap_seconds) as server:
        def rhs(z, state):
            return context.rhs_parts(z, state, server.callable(z, "DOP853_stage_or_dense"))["rhs"]
        try:
            solver = DOP853(rhs, context.left, context.initial.copy(), context.right,
                rtol=nominal_rtol/factor, atol=atol, max_step=max_step)
            while solver.status == "running":
                message = solver.step()
                if solver.status == "failed":
                    raise RuntimeError(message)
                dense = solver.dense_output()
                dense_pieces.append(dense)
                times.append(float(solver.t))
                values.append(solver.y.copy())
                gas = context.gas_from_q(solver.y[:5])
                if (gas[:13] < 0).any() or gas[13] <= 0 or solver.y[context.depth_slice].min() < -1e-12:
                    raise ValueError("nonphysical accepted coupled state")
            for z, y in [(context.left, context.initial), (context.right, solver.y)]:
                parts = context.rhs_parts(z, y, server.callable(z, "original_assembly_compatibility"))
                checks.append(original_assembly_check(context, z, y, parts))
        except Exception as error:
            failure = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
    accepted_z = np.asarray(times)
    accepted_y = np.asarray(values)
    dense_t_old = np.array([p.t_old for p in dense_pieces])
    dense_h = np.array([p.h for p in dense_pieces])
    dense_y_old = np.array([p.y_old for p in dense_pieces])
    dense_F = np.array([p.F for p in dense_pieces])
    gas_accepted = context.gas_from_q(accepted_y[:, :5])
    data = {"accepted_z": accepted_z, "accepted_y": accepted_y,
        "accepted_gas_14": gas_accepted, "dense_t_old": dense_t_old, "dense_h": dense_h,
        "dense_y_old": dense_y_old, "dense_F": dense_F,
        "initial": context.initial, "section_mask": context.model.section_mask,
        "active_cohorts_original_columns": context.model.coh[:context.active]}
    if failure is None:
        samples = np.linspace(context.left, context.right, 17)
        sampled = []
        for z in samples:
            i = min(np.searchsorted(accepted_z, z, side="right")-1, len(dense_pieces)-1)
            sampled.append(dense_pieces[i](z))
        sampled = np.asarray(sampled)
        data.update(sample_z=samples, sample_y=sampled, sample_gas_14=context.gas_from_q(sampled[:, :5]))
    state_path = out/"ACCEPTED_AND_DENSE_STATE.npz"
    with state_path.open("xb") as stream:
        np.savez_compressed(stream, **data)
    population = np.sum(context.source_population*np.exp(-accepted_y[:, context.depth_slice]), axis=1)
    born = float(context.source_population.sum())
    absorptions = accepted_y[:, context.absorption_slice].sum(axis=1)
    # New local initial time is immediately after the first discrete source birth.
    ledger = population-born+absorptions
    source_before_after = context.verify_original_sources()
    result = {"schema": "rei.run17.first-birth-control.v1",
        "status": "FAILED" if failure else "NUMERICALLY_CHECKED", "failure": failure,
        "scope": "one new first-birth coupled panel; exact active restriction with local passive ledgers; no historical M2/full-history rerun",
        "interval_z": [context.left, context.right], "active_pairs": context.active,
        "dimension": context.dimension, "all_48_spectral_cells": True,
        "control": {"method": "DOP853", "nominal_rtol": nominal_rtol,
            "effective_rtol": nominal_rtol/factor, "effective_atol": atol.tolist(),
            "max_step": max_step, "max_step_divisor": args.max_step_divisor,
            "norm_factor": factor, "error_norm": "component-scaled L2 in reduced q5/depth252/local-ledger8 chart",
            "original_full_40357_effective_error_norm_equivalence_claimed": False},
        "native_rhs_calls": server.calls, "native_call_wall_seconds": server.native_wall,
        "native_call_cap": args.native_call_cap, "wall_cap_seconds": args.wall_cap_seconds,
        "accepted_steps": len(dense_pieces), "accepted_z": accepted_z.tolist(),
        "accepted_step_sizes": np.diff(accepted_z).tolist(),
        "full_history_transport_ivp_solves": 0, "historical_m2_reruns": 0,
        "new_first_birth_coupled_panel_ivp_solves": 1,
        "new_prefix_ivp_solves": 0, "original_test_reruns": 0,
        "original_section_rhs_replay_checks": checks,
        "input": file_identity(out/"INPUT_IDENTITY.json"), "state": file_identity(state_path),
        "trace": {**file_identity(trace), "encoding": "parsed native f64 values; not raw wire bytes"},
        "gas_binary": file_identity(args.gas_binary),
        "code": [file_identity(__file__), file_identity(Path(__file__).with_name("native_context.py"))],
        "dense_layout": {"dense_F": [len(dense_pieces), 7, context.dimension],
            "state_axis": "last", "coefficients": "unaltered scipy.integrate._ivp.rk.Dop853DenseOutput.F",
            "endpoint_sides": ["outgoing first birth", "incoming second birth"]},
        "local_photon_ledger": {"initial_birth_per_initial_H": born,
            "delta_B_inside_panel": 0.0, "origin": "immediately after first activation",
            "identity": "P(z)-P(left)+sum(A_local(z))-0 = R_local(z)",
            "accepted_R_per_initial_H": ledger.tolist(),
            "accepted_R_over_initial_birth_max_abs": float(np.max(np.abs(ledger))/born),
            "endpoint_survivor_per_initial_H": float(population[-1]),
            "endpoint_absorption_H_HeI_HeII_D_per_initial_H": accepted_y[-1, context.absorption_slice].tolist(),
            "endpoint_heat_H_HeI_HeII_D_eV_per_initial_H": accepted_y[-1, context.heat_slice].tolist(),
            "spectral_error_bound_claimed": False},
        "gas_endpoint_14": gas_accepted[-1].tolist(), "q_endpoint": accepted_y[-1, :5].tolist(),
        "T_endpoint_K": float(context.temperature(gas_accepted[-1])),
        "minimum_accepted_active_density": float(gas_accepted[:, [1,2,3,4,10,11,12]].min()),
        "minimum_accepted_depth": float(accepted_y[:, context.depth_slice].min()),
        "maximum_accepted_depth": float(accepted_y[:, context.depth_slice].max()),
        "maximum_nuclear_drift": [float(np.max(np.abs(gas_accepted[:, ii].sum(axis=1)-context.gas0[ii].sum())))
            for ii in ([1,2], [3,4], [10,11,12])],
        "source_input_identity_unchanged": True,
        "proof_scope": "sampled/accepted numerical control only; no rigorous gas tube, full-domain trajectory, or continuum spectral bound",
        "command_argv": sys.argv, "environment": {"python": sys.version, "numpy": np.__version__,
            "scipy": scipy.__version__, "python_executable": sys.executable, "platform": platform.platform()},
        "total_wall_seconds": time.perf_counter()-start}
    if args.reference_result and failure is None:
        reference_path = args.reference_result.resolve()
        reference = json.loads(reference_path.read_text())
        ref_state = reference_path.parent / Path(reference["state"]["path"]).name
        if file_identity(ref_state)["sha256"] != reference["state"]["sha256"]:
            raise ValueError("reference state byte identity mismatch")
        with np.load(ref_state, allow_pickle=False) as old:
            if not np.array_equal(old["sample_z"], data["sample_z"]) or not np.array_equal(old["initial"], context.initial):
                raise ValueError("reference uses different times/initial state")
            old_gas = old["sample_gas_14"]
            new_gas = data["sample_gas_14"]
            new_p = (context.source_population*np.exp(-data["sample_y"][:, context.depth_slice])).sum(axis=1)
            old_p = (context.source_population*np.exp(-old["sample_y"][:, context.depth_slice])).sum(axis=1)
            result["step_halving_comparison"] = {
                "reference": file_identity(reference_path), "sample_count": len(data["sample_z"]),
                "sample_z": data["sample_z"].tolist(),
                "new_minus_reference_q_max_abs": float(np.max(abs(data["sample_y"][:, :5]-old["sample_y"][:, :5]))),
                "new_minus_reference_depth_max_abs": float(np.max(abs(data["sample_y"][:, context.depth_slice]-old["sample_y"][:, context.depth_slice]))),
                "new_minus_reference_HI_relative": (new_gas[:, 1]/old_gas[:, 1]-1).tolist(),
                "new_minus_reference_T_K": (context.temperature(new_gas)-context.temperature(old_gas)).tolist(),
                "new_minus_reference_survivor_over_initial_birth": ((new_p-old_p)/born).tolist(),
                "distinct_accepted_grid": not np.array_equal(accepted_z, old["accepted_z"]),
                "supremum_error_bound_claimed": False}
    save_json(out/"FIRST_BIRTH_CONTROL.json", result)
    print(json.dumps({"status": result["status"], "native_rhs_calls": server.calls,
        "accepted_steps": len(dense_pieces), "native_call_wall_seconds": server.native_wall,
        "total_wall_seconds": result["total_wall_seconds"], "T_endpoint_K": result["T_endpoint_K"],
        "ledger_max_relative": result["local_photon_ledger"]["accepted_R_over_initial_birth_max_abs"],
        "step_halving_comparison": result.get("step_halving_comparison"), "failure": failure}, allow_nan=False))
    if failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
