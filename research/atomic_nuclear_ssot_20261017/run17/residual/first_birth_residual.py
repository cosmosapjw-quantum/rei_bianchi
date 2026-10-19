#!/usr/bin/env python3
"""Full-source gas-path defect on the completed RUN17 first-birth control.

P is a newly defined invariant q5 PCHIP through archived tight gas knots;
its optical integrals use the same P path and the unchanged native geometry.
R is the saved native control's dense polynomial, differentiated analytically.
All finite quadrature contrasts and sampled maxima remain numerical diagnostics.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import sys
import time

sys.dont_write_bytecode = True
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"native"))
from native_context import load_context, TracedNative, file_identity, save_json, sha256
import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator
from numpy.polynomial.legendre import leggauss
from dense_reconstruction import dense_value_derivative, signed_defect_balance
from comparison_propagator import propagate_comparison

CONTEXT_SHA = "3596fb00de6554c3cc7458b77d68913f272f2ff089da623e89edf864c256eebe"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--run16-root", required=True, type=Path)
    parser.add_argument("--control-result", required=True, type=Path)
    parser.add_argument("--gas-binary", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    context_path = Path(__file__).resolve().parents[1]/"native/native_context.py"
    if sha256(context_path) != CONTEXT_SHA:
        raise ValueError("native context source identity changed")
    ctx = load_context(args.source_root, args.run16_root)
    control_path = args.control_result.resolve()
    control = json.loads(control_path.read_text())
    if (control["status"] != "NUMERICALLY_CHECKED" or
            control["interval_z"] != [ctx.left, ctx.right] or
            control["control"]["max_step_divisor"] != 20):
        raise ValueError("latest completed smaller-step RUN17 control B required")
    state_path = control_path.parent/Path(control["state"]["path"]).name
    if sha256(state_path) != control["state"]["sha256"]:
        raise ValueError("native dense array identity mismatch")
    with np.load(state_path, allow_pickle=False) as source:
        data = {key: source[key].copy() for key in source.files}
    if not np.array_equal(data["initial"], ctx.initial):
        raise ValueError("control initial state differs from prefix C")
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=False)
    knots = np.asarray(ctx.point["tight_checkpoint_z"])
    original_gas_knots = np.asarray(ctx.point["tight_gas_knots_original_14"])
    q_knots = original_gas_knots[:, ctx.pick]/ctx.scale
    path_p = PchipInterpolator(knots, q_knots, axis=0, extrapolate=False)
    path_p_derivative = path_p.derivative()
    path_14 = PchipInterpolator(knots, original_gas_knots, axis=0, extrapolate=False)
    geometry_breaks = (ctx.model.xnodes-ctx.model.x0)/ctx.model.dx
    geometry_breaks = geometry_breaks[(ctx.left < geometry_breaks)&(geometry_breaks < ctx.right)]
    cuts = np.unique(np.r_[data["accepted_z"], geometry_breaks,
                          knots[(ctx.left < knots)&(knots < ctx.right)]])
    legendre = {order: leggauss(order) for order in (6, 10, 12, 20)}
    tau_cache = {}
    rows = []
    arrays = {}

    def reference(z):
        index = min(np.searchsorted(data["accepted_z"], z, side="right")-1,
                    len(data["dense_t_old"])-1)
        return dense_value_derivative(z, data["dense_t_old"][index],
            data["dense_h"][index], data["dense_y_old"][index], data["dense_F"][index])

    def optical_rate(z):
        gas = ctx.gas_from_q(path_p(z))
        energy, _, hubble, a = ctx.model.rays(float(z), ctx.active)
        kappa = (ctx.native.C*ctx.model.dx/hubble*ctx.model.section_sigma(energy)
                 *ctx.model.nh/(a/ctx.model.a0)**3)
        return kappa@gas[ctx.native.LO]

    def optical_integral(z, order):
        key = (float(z), order)
        if key in tau_cache:
            return tau_cache[key]
        if z == ctx.left:
            value = np.zeros(ctx.active)
        else:
            # Include geometry/PCHIP breaks independently of the native step grid.
            local_cuts = np.unique(np.r_[ctx.left, geometry_breaks[geometry_breaks < z],
                                        knots[(ctx.left < knots)&(knots < z)], z])
            x, weights = legendre[order]
            value = np.zeros(ctx.active)
            for left, right in zip(local_cuts[:-1], local_cuts[1:]):
                midpoint, half = (left+right)/2, (right-left)/2
                values = np.asarray([optical_rate(midpoint+half*s) for s in x])
                value += half*(weights@values)
        tau_cache[key] = value
        return value

    def temperature_gradient(q):
        gas = ctx.gas_from_q(q)
        particles = (1+ctx.native.CHARGE)@gas[:13]
        particle_gradient = (1+ctx.native.CHARGE)@ctx.lift[:13]
        coefficient = 2*ctx.native.EV_J/(3*ctx.native.KB)
        return coefficient*(ctx.lift[13]*particles-gas[13]*particle_gradient)/particles**2

    q_p0, q_p1 = path_p(ctx.left), path_p(ctx.right)
    q_r0, q_r1 = data["initial"][:5], data["accepted_y"][-1, :5]
    delta0, delta1 = q_p0-q_r0, q_p1-q_r1
    initial_T_delta = float(ctx.temperature(ctx.gas_from_q(q_p0))-ctx.temperature(ctx.gas_from_q(q_r0)))
    endpoint_T_delta = float(ctx.temperature(ctx.gas_from_q(q_p1))-ctx.temperature(ctx.gas_from_q(q_r1)))
    trace_path = out/"NATIVE_RESIDUAL_RHS_VALUE_TRACE.jsonl"
    with TracedNative(ctx, args.gas_binary, trace_path, call_cap=1000, wall_cap=20.0) as native:
        def evaluate(z, purpose):
            state_r, derivative_r = reference(z)
            state_p = ctx.initial.copy()
            state_p[:5] = path_p(z)
            state_p[ctx.depth_slice] = optical_integral(z, 20)
            part_r = ctx.rhs_parts(z, state_r, native.callable(z, purpose+"_R"))
            part_p = ctx.rhs_parts(z, state_p, native.callable(z, purpose+"_P"))
            qprime_p = path_p_derivative(z)
            rq_r = derivative_r[:5]-part_r["rhs"][:5]
            rq_p = qprime_p-part_p["rhs"][:5]
            gas_difference = (part_p["native_gas_rate_14"]-part_r["native_gas_rate_14"])[ctx.pick]/ctx.scale
            photo_difference = (part_p["photo_gas_rate_14"]-part_r["photo_gas_rate_14"])[ctx.pick]/ctx.scale
            grad_p = temperature_gradient(state_p[:5]); grad_r = temperature_gradient(state_r[:5])
            g_p = part_p["native_gas_rate_14"][ctx.pick]/ctx.scale
            g_r = part_r["native_gas_rate_14"][ctx.pick]/ctx.scale
            phi_p = part_p["photo_gas_rate_14"][ctx.pick]/ctx.scale
            phi_r = part_r["photo_gas_rate_14"][ctx.pick]/ctx.scale
            T_terms = np.array([grad_p@g_p-grad_r@g_r,
                grad_p@phi_p-grad_r@phi_r, grad_p@rq_p, -grad_r@rq_r])
            return {"z": float(z), "state_R": state_r, "q_P": state_p[:5],
                "tau_P_GL20": state_p[ctx.depth_slice],
                "tau_P_GL12": optical_integral(z, 12),
                "qprime_R": derivative_r[:5], "qprime_P": qprime_p,
                "r_q_R": rq_r, "r_q_P": rq_p,
                "r_tau_R": derivative_r[ctx.depth_slice]-part_r["tau_rate"],
                "r_local_ledgers_R": derivative_r[ctx.absorption_slice.start:]-part_r["rhs"][ctx.absorption_slice.start:],
                "native_gas_difference_q": gas_difference,
                "photo_difference_q": photo_difference,
                "T_rate_terms": T_terms,
                "photo_absorption_P": part_p["net_absorption_rate"],
                "photo_absorption_R": part_r["net_absorption_rate"],
                "native_q_R": g_r, "native_q_P": g_p,
                "photo_q_R": phi_r, "photo_q_P": phi_p}

        quadrature_records = []
        for order in (6, 10):
            x, weights = legendre[order]
            observations, quadrature_weights = [], []
            for left, right in zip(cuts[:-1], cuts[1:]):
                midpoint, half = (left+right)/2, (right-left)/2
                for t, weight in zip(midpoint+half*x, half*weights):
                    observations.append(evaluate(float(t), "GL"+str(order)))
                    quadrature_weights.append(weight)
            weights = np.asarray(quadrature_weights)
            for key in observations[0]:
                arrays[f"GL{order}_{key}"] = np.asarray([row[key] for row in observations])
            arrays[f"GL{order}_weights"] = weights
            prefix = f"GL{order}_"
            gas_integral = weights@arrays[prefix+"native_gas_difference_q"]
            photo_integral = weights@arrays[prefix+"photo_difference_q"]
            rp_integral = weights@arrays[prefix+"r_q_P"]
            rr_integral = weights@arrays[prefix+"r_q_R"]
            terms_t = weights@arrays[prefix+"T_rate_terms"]
            balance = signed_defect_balance(delta0, delta1,
                gas_integral+photo_integral, rp_integral-rr_integral)
            tau_contrast = arrays[prefix+"tau_P_GL20"]-arrays[prefix+"tau_P_GL12"]
            native_defects = arrays[prefix+"r_q_R"]
            p_defects = arrays[prefix+"r_q_P"]
            record = {"order": order, "nodes": len(observations),
                "initial_delta_q_P_minus_R": delta0.tolist(), "endpoint_delta_q_P_minus_R": delta1.tolist(),
                "native_gas_difference_integral_q": gas_integral.tolist(),
                "photo_difference_integral_q": photo_integral.tolist(),
                "P_gas_residual_integral_q": rp_integral.tolist(),
                "minus_R_gas_residual_integral_q": (-rr_integral).tolist(),
                "balance_closure_q": balance.tolist(),
                "temperature_initial_difference_K": initial_T_delta,
                "temperature_endpoint_difference_K": endpoint_T_delta,
                "temperature_integral_terms_native_photo_Presidual_minusRresidual_K": terms_t.tolist(),
                "temperature_balance_closure_K": float(endpoint_T_delta-initial_T_delta-terms_t.sum()),
                "sampled_max_abs_native_gas_residual_by_q": np.max(abs(native_defects), axis=0).tolist(),
                "sampled_max_abs_P_gas_residual_by_q": np.max(abs(p_defects), axis=0).tolist(),
                "sampled_max_abs_native_depth_residual": float(abs(arrays[prefix+"r_tau_R"]).max()),
                "sampled_max_abs_native_local_ledger_residual": float(abs(arrays[prefix+"r_local_ledgers_R"]).max()),
                "same_path_tau_GL20_minus_GL12_max_abs": float(abs(tau_contrast).max()),
                "P_photo_absorption_integrals_H_HeI_HeII_D": (weights@arrays[prefix+"photo_absorption_P"]).tolist(),
                "R_photo_absorption_integrals_H_HeI_HeII_D": (weights@arrays[prefix+"photo_absorption_R"]).tolist()}
            quadrature_records.append(record)
        for z in data["sample_z"]:
            observation = evaluate(float(z), "uniform_diagnostic")
            gas_r = ctx.gas_from_q(observation["state_R"][:5])
            gas_p = ctx.gas_from_q(observation["q_P"])
            old = path_14(z)
            rows.append({"z": float(z), "R_HI_per_initial_H": float(gas_r[1]),
                "P_HI_per_initial_H": float(gas_p[1]),
                "P_minus_R_HI_relative": float((gas_p[1]-gas_r[1])/gas_r[1]),
                "R_T_K": float(ctx.temperature(gas_r)), "P_T_K": float(ctx.temperature(gas_p)),
                "P_minus_R_T_K": float(ctx.temperature(gas_p)-ctx.temperature(gas_r)),
                "P_minus_original14_PCHIP_gas_max_abs": float(abs(gas_p-old).max()),
                "P_minus_R_q": (observation["q_P"]-observation["state_R"][:5]).tolist(),
                "native_residual_q": observation["r_q_R"].tolist(),
                "P_residual_q": observation["r_q_P"].tolist(),
                "same_path_tau_GL20_minus_GL12_max_abs": float(abs(observation["tau_P_GL20"]-observation["tau_P_GL12"]).max())})
        # Three pointwise finite-difference gas Jacobians plus analytic photons.
        block_rows = []
        for z in (ctx.left, (ctx.left+ctx.right)/2, ctx.right):
            state, _ = reference(z); q = state[:5]
            part = ctx.photo_parts(z, q, state[ctx.depth_slice])
            gas_matrix = np.zeros((5, 5))
            steps = 1e-6*np.maximum(abs(q), 1e-3)
            for j, step in enumerate(steps):
                variants = []
                for sign in (-1, 1):
                    altered = state.copy(); altered[j] += sign*step
                    evaluated = ctx.rhs_parts(z, altered, native.callable(z, "point_gas_Jacobian"))
                    variants.append(evaluated["native_gas_rate_14"][ctx.pick]/ctx.scale)
                gas_matrix[:, j] = (variants[1]-variants[0])/(2*step)
            kappa = (ctx.native.C*ctx.model.dx/part["hubble"]*part["sigma"]
                     *ctx.model.nh/part["volume"])
            population = part["population"]; lower_lift = ctx.lift[ctx.native.LO]
            events = part["hazard"]*population[:, None]
            heat = part["energy"][:, None]-ctx.model.chi
            channel = (kappa*population[:, None]).sum(axis=0)[:, None]*lower_lift
            h, d, he, _, thermal = ctx.scale
            photo_matrix = np.vstack((channel[0]/h, channel[3]/d,
                (channel[1]-channel[2])/he, channel[2]/he,
                ((kappa*population[:, None]*heat).sum(axis=0)@lower_lift)/thermal))
            B = np.vstack((-events[:, 0]/h, -events[:, 3]/d,
                -(events[:, 1]-events[:, 2])/he, -events[:, 2]/he,
                -np.sum(events*heat, axis=1)/thermal))
            C = kappa@lower_lift; A = gas_matrix+photo_matrix
            logarithmic = float(np.max(np.diag(A)+np.sum(abs(A), axis=1)-abs(np.diag(A))))
            block_rows.append({"z": float(z), "A_matrix": A.tolist(),
                "A_induced_inf_norm": float(np.linalg.norm(A, np.inf)), "A_inf_logarithmic_norm": logarithmic,
                "B_inf_norm": float(np.max(np.sum(abs(B), axis=1))),
                "C_inf_norm": float(np.max(np.sum(abs(C), axis=1))),
                "gas_FD_steps": steps.tolist(), "status": "POINTWISE_NUMERICAL_SCALES"})
    fine, coarse = quadrature_records[1], quadrature_records[0]
    a = max(row["A_inf_logarithmic_norm"] for row in block_rows)
    b = max(row["B_inf_norm"] for row in block_rows)
    c = max(row["C_inf_norm"] for row in block_rows)
    rho_g = float(np.max(abs(arrays["GL10_r_q_P"]-arrays["GL10_r_q_R"])))
    rho_tau = fine["sampled_max_abs_native_depth_residual"]
    comparison = propagate_comparison(a, b, c, [rho_g, rho_tau],
                                     [float(abs(delta0).max()), 0.], ctx.right-ctx.left)
    pure_gas = propagate_comparison(a, 0., c, [rho_g, rho_tau],
                                   [float(abs(delta0).max()), 0.], ctx.right-ctx.left)
    # Numerical polynomial admissibility checks; critical roots are float64.
    q_coefficient = path_p.c[:, 0, :]
    polynomial_margin = []
    for label, column in [("q_H", q_coefficient[:, 0]), ("one_minus_q_H", -q_coefficient[:, 0]),
                          ("q_D", q_coefficient[:, 1]), ("one_minus_q_D", -q_coefficient[:, 1]),
                          ("q_HeII", q_coefficient[:, 2]), ("q_HeIII", q_coefficient[:, 3]),
                          ("one_minus_HeII_minus_HeIII", -q_coefficient[:, 2]-q_coefficient[:, 3]),
                          ("q_thermal", q_coefficient[:, 4])]:
        coeff = column.copy()
        if label.startswith("one_minus"):
            coeff[-1] += 1.
        roots = np.roots(np.polyder(coeff))
        candidates = [ctx.left-knots[0], ctx.right-knots[0]]
        candidates += [float(v.real) for v in roots if abs(v.imag) < 1e-12 and candidates[0] < v.real < candidates[1]]
        values = np.polyval(coeff, candidates)
        polynomial_margin.append({"margin": label, "minimum": float(values.min()),
            "critical_candidates_z": [v+knots[0] for v in candidates], "method": "float64 derivative roots and endpoints"})
    if min(item["minimum"] for item in polynomial_margin) <= 0:
        raise ValueError("nonpositive PCHIP gas domain margin")
    arrays.update(pchip_q_coefficients=path_p.c, pchip_knots=knots,
                  pchip_q_knots=q_knots, quadrature_panel_cuts=cuts)
    raw_path = out/"RESIDUAL_QUADRATURE_ARRAYS.npz"
    with raw_path.open("xb") as stream:
        np.savez_compressed(stream, **arrays)
    p_survivor_end = float(np.sum(ctx.source_population*np.exp(-optical_integral(ctx.right, 20))))
    r_survivor_end = float(np.sum(ctx.source_population*np.exp(-data["accepted_y"][-1, ctx.depth_slice])))
    born = float(ctx.source_population.sum())
    result = {"schema": "rei.run17.first-birth-residual.v1", "status": "NUMERICALLY_CHECKED",
        "orientation": "P-minus-R; P=invariant q5 PCHIP plus same-path optical integrals; R=stored native control B dense polynomial",
        "interval_z": [ctx.left, ctx.right], "source": ctx.identity,
        "input_control": file_identity(control_path), "input_dense_state": file_identity(state_path),
        "definition_P": "PchipInterpolator of original14 selected columns divided by fixed q5 normalizations, followed by original affine lift; distinct reconstructed path",
        "P_knot_lift_minus_original14_max_abs": float(abs(ctx.gas_from_q(q_knots)-original_gas_knots).max()),
        "P_polynomial_domain_margins": polynomial_margin,
        "quadrature_settings": quadrature_records, "uniform_samples": rows,
        "finite_quadrature_contrast_GL10_minus_GL6": {key: (np.asarray(fine[key])-np.asarray(coarse[key])).tolist()
            for key in ("native_gas_difference_integral_q", "photo_difference_integral_q",
                "P_gas_residual_integral_q", "minus_R_gas_residual_integral_q",
                "temperature_integral_terms_native_photo_Presidual_minusRresidual_K")},
        "sampled_Jacobian_blocks": block_rows,
        "constant_comparison_diagnostic": {"a": a, "b": b, "c": c,
            "sampled_rho_g": rho_g, "sampled_rho_tau": rho_tau,
            "initial_radius": [float(abs(delta0).max()), 0.],
            **{key: value.tolist() for key, value in comparison.items()},
            "gas_endpoint_without_depth_feedback": float(pure_gas["endpoint"][0]),
            "gas_feedback_increment": float(comparison["endpoint"][0]-pure_gas["endpoint"][0]),
            "observed_endpoint_q_difference_inf": float(abs(delta1).max()),
            "status": "SAMPLED_COEFFICIENT_DIAGNOSTIC_ONLY",
            "assumptions_not_verified": ["tube-wide Jacobian bounds", "continuous residual bounds", "prefix exact-IVP input enclosure", "rigorous same-path optical quadrature bound"],
            "depth_residual_input_scope": "uses ideal integral P depth residual zero plus sampled native R depth residual; finite GL20 representation uncertainty remains separate"},
        "conditional_first_birth_survivor": {"P_endpoint_per_initial_H": p_survivor_end,
            "R_endpoint_per_initial_H": r_survivor_end,
            "P_minus_R_relative_R_denominator": (p_survivor_end-r_survivor_end)/r_survivor_end,
            "P_minus_R_over_initial_birth": (p_survivor_end-r_survivor_end)/born,
            "P_same_path_local_photon_ledger_R_over_birth": (p_survivor_end-born+sum(fine["P_photo_absorption_integrals_H_HeI_HeII_D"]))/born,
            "scope": "first-birth finite-packet survivor at second-birth incoming endpoint, not full-history sub-H observable"},
        "arrays": file_identity(raw_path), "native_trace": file_identity(trace_path),
        "native_rhs_calls": native.calls, "native_call_wall_seconds": native.native_wall,
        "new_native_IVP_solves": 0, "historical_m2_reruns": 0,
        "source_input_identity_unchanged": True,
        "code": [file_identity(__file__), file_identity(Path(__file__).with_name("dense_reconstruction.py")),
                 file_identity(Path(__file__).with_name("comparison_propagator.py")), file_identity(context_path)],
        "command_argv": sys.argv, "environment": {"python": sys.version, "numpy": np.__version__,
            "scipy": scipy.__version__, "platform": platform.platform()},
        "known_limits": ["quadrature contrast is not a rigorous integration error bound", "sample maxima are not continuous suprema",
            "algebraic defect closure is not spectral convergence", "one first-birth panel with inherited numerical prefix input"],
        "total_wall_seconds": time.perf_counter()-started}
    ctx.verify_original_sources()
    save_json(out/"FIRST_BIRTH_RESIDUAL.json", result)
    print(json.dumps({"status": result["status"], "native_rhs_calls": native.calls,
        "wall_seconds": result["total_wall_seconds"], "endpoint_sample": rows[-1],
        "fine_quadrature": fine, "survivor": result["conditional_first_birth_survivor"],
        "comparison": result["constant_comparison_diagnostic"]}, allow_nan=False))


if __name__ == "__main__":
    main()
