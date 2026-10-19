#!/usr/bin/env python3
"""RUN16 recorded-state coupling scales; no trajectory solve or continuum claim.

All native calls use the immutable RUN13 gas server. The source packet, gas,
and depths are archived values. Central gas derivatives are point estimates;
the photon blocks are differentiated analytically on the recorded event side.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import re
import sys
import time

sys.dont_write_bytecode = True
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"

import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator

GAS_SHA = "3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b"
PACKET_SHA = "67ec6958ac6f662125e049003d785c917c89e832b6bcbbd026ab8a332870b88a"
COORDINATES = ["x_HII", "x_DII", "x_HeII", "x_HeIII", "thermal_per_H_over_initial"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def matrix_scales(matrix):
    matrix = np.asarray(matrix)
    return {
        "matrix": matrix.tolist(),
        "induced_inf_norm": float(np.linalg.norm(matrix, ord=np.inf)),
        "inf_logarithmic_norm": float(np.max(np.diag(matrix) +
            np.abs(matrix).sum(axis=1) - np.abs(np.diag(matrix)))),
        "eigenvalues": [[float(v.real), float(v.imag)] for v in np.linalg.eigvals(matrix)],
        "units": "per normalized z",
        "status": "POINTWISE_NUMERICAL_SCALE_ONLY",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--gas-binary", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--native-budget-seconds", type=float, default=20.0)
    args = parser.parse_args()
    if not 0 < args.native_budget_seconds <= 20.0:
        raise ValueError("native call budget must be positive and at most 20 seconds")
    root = args.source_root.resolve()
    binary = args.gas_binary.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    source_identity = {}
    sealed = {}
    for line in (root / "SHA256SUMS.txt").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        if relative in sealed:
            raise ValueError("duplicate original manifest path")
        sealed[relative] = digest

    def verify(relative):
        path = root / relative
        actual = sha(path)
        if actual != sealed.get(relative):
            raise ValueError(f"original manifest mismatch: {relative}")
        source_identity[relative] = {"bytes": path.stat().st_size, "sha256": actual}
        return path

    # Verify every original native source/configuration file because the gas
    # executable is bound to this exact recovered source owner by its hash.
    for relative in sorted(sealed):
        if relative.startswith("code/"):
            verify(relative)
    for relative in (
        "scripts/retarded_integrator.py", "scripts/gas_integrator_parent.py",
        "scripts/spectral_joint11.py", "inputs/source_table.py",
        "inputs/bass164/PRODUCER_RECEIPT.json",
        "inputs/bass164/PROPOSED_REI_BACKGROUND.csv",
    ):
        verify(relative)
    if sha(binary) != GAS_SHA:
        raise ValueError("gas executable differs from exact original rebuild")
    packet_path = verify("inputs/spectral11/m2.json")
    if sha(packet_path) != PACKET_SHA:
        raise ValueError("wrong original packet")
    events = json.loads(verify("inputs/spectral11/m2_events.json").read_text())
    directory = "evidence/joint11_sided_m2_6e-12"
    metadata = json.loads(verify(directory + "/checkpoint.json").read_text())
    if (metadata["status"] != "COMPLETE" or metadata["next_segment"] != 6241 or
            metadata["dimension"] != 40357 or metadata["packet_sha256"] != PACKET_SHA or
            metadata["rtol"] != 6e-12 or events["packet_sha256"] != PACKET_SHA):
        raise ValueError("complete original tight M2 identity required")
    sys.path.insert(0, str(root / "scripts"))
    native = importlib.import_module("retarded_integrator")
    spectral = importlib.import_module("spectral_joint11")
    if Path(native.ROOT).resolve() != root or Path(spectral.R).resolve() != root:
        raise ValueError("import resolved to another source tree")
    packet = json.loads(packet_path.read_text())
    model = spectral.SpectralModel(native.coalesce_reflections(packet))
    if model.dim != metadata["dimension"] or model.m != 40320:
        raise ValueError("original full-state dimensions differ")
    points = np.asarray(events["points"])
    if len(points) != 6242:
        raise ValueError("original event count differs")
    snapshots = []
    for path in (root / directory).glob("checkpoint_*.npz"):
        match = re.fullmatch(r"checkpoint_(\d+)\.npz", path.name)
        if not match:
            continue
        segment = int(match.group(1))
        if not 1 <= segment <= 6241:
            raise ValueError("checkpoint outside completed history")
        z = float(metadata["segments"][segment-1][1])
        if z != points[segment]:
            raise ValueError("saved checkpoint time does not match original event partition")
        snapshots.append((segment, z, str(path.relative_to(root))))
    snapshots.sort()
    if len(snapshots) != 12 or snapshots[-1][0] != 6241:
        raise ValueError("expected complete twelve-checkpoint tight history")
    chosen = [snapshots[0], snapshots[-1]]
    states = [{"label": "initial", "segment": 0, "z": 0.0,
               "state_file": "inputs/spectral11/m2.json", "state": model.y0.copy()}]
    for segment, z, relative in chosen:
        path = verify(relative)
        with np.load(path, allow_pickle=False) as archive:
            state = archive["state"].copy()
        if state.shape != (model.dim,) or not np.isfinite(state).all():
            raise ValueError("invalid saved state")
        if segment == 6241 and sha(path) != metadata["state_sha256"]:
            raise ValueError("final state commit-marker mismatch")
        states.append({"label": "first_checkpoint" if segment != 6241 else "endpoint",
                       "segment": segment, "z": z, "state_file": relative, "state": state})
    knots = np.r_[0., [s[1] for s in snapshots]]
    gas_knots = [model.y0[:14].copy()]
    for _, _, relative in snapshots:
        with np.load(verify(relative), allow_pickle=False) as archive:
            stored = archive["state"]
            if stored.shape != (model.dim,) or not np.isfinite(stored).all():
                raise ValueError("invalid archived PCHIP gas knot")
            gas_knots.append(stored[:14].copy())
    gas_knots = np.asarray(gas_knots)
    gas_pchip = PchipInterpolator(knots, gas_knots, axis=0, extrapolate=False)
    h_total = float(model.y0[1:3].sum())
    d_total = float(model.y0[3:5].sum())
    he_total = float(model.y0[10:13].sum())
    u_initial = float(model.y0[13])
    scales = np.array([h_total, d_total, he_total, he_total, u_initial])
    pick = np.array([2, 4, 11, 12, 13])
    lift = np.zeros((14, 5))
    for column, low, high, total in (
        (0, 1, 2, h_total), (1, 3, 4, d_total),
        (2, 10, 11, he_total), (3, 10, 12, he_total),
    ):
        lift[low, column] = -total
        lift[high, column] = total
    lift[13, 4] = u_initial
    lower_lift = lift[native.LO]
    native_calls = 0
    native_wall = 0.0
    trace_path = out / "NATIVE_RHS_VALUE_TRACE.jsonl"
    rows = []

    with trace_path.open("x") as trace, native.GasServer(path=binary) as server:
        def native_call(state, tcmb, mask=7):
            nonlocal native_calls, native_wall
            if native_calls >= 100 or native_wall >= args.native_budget_seconds:
                raise TimeoutError("bounded native RHS budget reached")
            before = time.perf_counter()
            answer = server.rhs(state, tcmb, mask)
            native_wall += time.perf_counter() - before
            native_calls += 1
            trace.write(json.dumps({"call": native_calls, "mask": mask,
                "tcmb_K": float(tcmb), "proper_state_14": state.tolist(),
                "native_payload_28": answer.tolist()}, allow_nan=False) + "\n")
            return answer

        class RecordedServer:
            def rhs(self, state, tcmb, mask=7):
                return native_call(state, tcmb, mask)

        model.server = RecordedServer()
        for saved in states:
            state = saved.pop("state")
            z = saved["z"]
            segment = saved["segment"]
            # Saved gas/depth is continuous at these events. Use the outgoing
            # original section, except at the terminal point (incoming side).
            section = segment if segment < 6241 else 6240
            left, right = points[section:section+2]
            active = int(np.searchsorted(model.birth, left, side="right"))
            model.set_interval(float(left), float(right), active)
            a, _, hubble, _ = model.geometry(z)
            volume = (a / model.a0)**3
            tcmb = 2.7255 / a
            y = state[:14].copy()
            q = y[pick] / scales
            if (y[:13] < 0).any() or y[13] <= 0:
                raise ValueError("recorded state outside gas domain")
            first_call = native_calls

            def gas_rhs(gas, mask=7, expansion=True):
                raw = native_call(gas * model.gscale[:14] / volume, tcmb, mask)
                value = model.dx * volume / hubble * raw[:27] / model.gscale
                if expansion:
                    value[13] -= 2 * model.dx * gas[13]
                return value

            gas_value = gas_rhs(y)
            component_values = {str(mask): gas_rhs(y, mask, expansion=False)
                                for mask in (1, 2, 4)}
            component_sum = sum(component_values.values())
            component_sum[13] -= 2 * model.dx * y[13]
            additivity = float(np.max(np.abs(component_sum-gas_value)))

            def gas_jacobian(relative_step, mask=7, expansion=True):
                matrix = np.zeros((5, 5))
                steps = relative_step * np.maximum(np.abs(q), 1e-3)
                for j, step in enumerate(steps):
                    plus = gas_rhs(y + step * lift[:, j], mask, expansion)
                    minus = gas_rhs(y - step * lift[:, j], mask, expansion)
                    matrix[:, j] = (plus[pick]-minus[pick])/(2*step*scales)
                return matrix, steps

            coarse, fd_steps = gas_jacobian(2e-6)
            fine, _ = gas_jacobian(1e-6)
            fd_error = float(np.linalg.norm(coarse-fine, ord=np.inf) /
                             max(np.linalg.norm(fine, ord=np.inf), 1e-300))
            cx_matrix = gas_jacobian(2e-6, mask=2, expansion=False)[0] if segment == 0 else None
            if active:
                energy, _, _, _ = model.rays(z, active)
                sigma = model.section_sigma(energy)
                kappa = native.C * model.dx / hubble * sigma * model.nh / volume
                population = model.B[:active] * np.exp(-state[27:27+active])
                heat = energy[:, None] - model.chi
            else:
                energy = np.empty(0)
                kappa = np.empty((0, 4))
                population = np.empty(0)
                heat = np.empty((0, 4))

            def photo_rhs(gas):
                events_now = kappa * gas[native.LO][None, :] * population[:, None]
                total = events_now.sum(axis=0)
                return np.array([total[0]/h_total, total[3]/d_total,
                    (total[1]-total[2])/he_total, total[2]/he_total,
                    np.sum(events_now*heat)/u_initial])

            events_now = kappa * y[native.LO][None, :] * population[:, None]
            rates_per_lower = (kappa * population[:, None]).sum(axis=0)
            channel_derivative = rates_per_lower[:, None] * lower_lift
            photo_jac = np.vstack((channel_derivative[0]/h_total,
                channel_derivative[3]/d_total,
                (channel_derivative[1]-channel_derivative[2])/he_total,
                channel_derivative[2]/he_total,
                ((kappa*population[:, None]*heat).sum(axis=0) @ lower_lift)/u_initial))
            b_depth = np.vstack((-events_now[:, 0]/h_total,
                -events_now[:, 3]/d_total,
                -(events_now[:, 1]-events_now[:, 2])/he_total,
                -events_now[:, 2]/he_total,
                -np.sum(events_now*heat, axis=1)/u_initial))
            c_depth = kappa @ lower_lift
            photo_fd = np.zeros((5, 5))
            for j, step in enumerate(fd_steps):
                photo_fd[:, j] = (photo_rhs(y+step*lift[:, j]) -
                    photo_rhs(y-step*lift[:, j]))/(2*step)
            photo_fd_error = float(np.linalg.norm(photo_jac-photo_fd, ord=np.inf) /
                max(np.linalg.norm(photo_jac, ord=np.inf), 1e-300))
            original_full_rhs = model.section_rhs(z, state, active)
            joint = original_full_rhs[pick]/scales
            assembled = gas_value[pick]/scales + photo_rhs(y)
            assembly_error = float(np.max(np.abs(joint-assembled)))
            if not (fd_error < 5e-6 and photo_fd_error < 5e-6 and
                    assembly_error < 1e-12*max(1.0, np.max(np.abs(joint)))):
                raise AssertionError("new diagnostic finite-difference/assembly consistency failed")
            b_rows = np.abs(b_depth).sum(axis=1)
            c_columns = np.abs(c_depth).max(axis=0) if active else np.zeros(5)
            interpolated = gas_pchip(z)
            path_derivative = gas_pchip.derivative()(z)
            defect = path_derivative - original_full_rhs[:14]
            if not np.array_equal(interpolated, y):
                # PCHIP evaluation at its last knot can have floating Horner
                # roundoff. Admit only roundoff-scale interpolation discrepancy.
                if np.max(np.abs(interpolated-y)/np.maximum(np.abs(y), 1e-300)) > 5e-15:
                    raise AssertionError("PCHIP does not reproduce archived gas knot")
            particle_weight = 1 + native.CHARGE
            particles = float(particle_weight @ y[:13])
            def ln_temperature_rate(derivative):
                return float(derivative[13]/y[13] -
                             (particle_weight @ derivative[:13])/particles)
            path_defect = {
                "status": "POINTWISE_CHECKPOINT_PCHIP_DEFECT_ONLY",
                "definition": "componentwise fourteen-gas-coordinate PCHIP derivative minus exact archived full finite-packet RHS at the same knot and recorded event side",
                "derivative_original_gas_14_per_z": path_derivative.tolist(),
                "actual_full_rhs_gas_14_per_z": original_full_rhs[:14].tolist(),
                "defect_original_gas_14_per_z": defect.tolist(),
                "defect_in_five_coordinates_per_z": (defect[pick]/scales).tolist(),
                "HI_relative_pchip_rate_per_z": float(path_derivative[1]/y[1]),
                "HI_relative_full_rhs_rate_per_z": float(original_full_rhs[1]/y[1]),
                "HI_relative_defect_per_z": float(defect[1]/y[1]),
                "DI_relative_defect_per_z": float(defect[3]/y[3]),
                "lnT_pchip_rate_per_z": ln_temperature_rate(path_derivative),
                "lnT_full_rhs_rate_per_z": ln_temperature_rate(original_full_rhs),
                "lnT_defect_per_z": ln_temperature_rate(defect),
                "pchip_nuclear_total_derivatives_per_z": [float(path_derivative[1:3].sum()),
                    float(path_derivative[3:5].sum()), float(path_derivative[10:13].sum())],
                "max_knot_reconstruction_absolute_difference": float(np.max(np.abs(interpolated-y))),
                "not_a_between_knot_supremum_or_trajectory_bound": True,
            }
            row = dict(saved, event_side="outgoing" if segment < 6241 else "incoming",
                interval=[float(left), float(right)], active=active, gas_coordinates=q.tolist(),
                temperature_K=float(2*y[13]*native.EV_J/(3*native.KB*((1+native.CHARGE)@y[:13]))),
                gas_species_total_drift=[float(y[1:3].sum()-h_total),
                    float(y[3:5].sum()-d_total), float(y[10:13].sum()-he_total)],
                z_to_proper_seconds=float(model.dx/hubble),
                native_plus_expansion_rhs=gas_value[pick].__truediv__(scales).tolist(),
                native_mask_rhs_without_expansion={key: (value[pick]/scales).tolist()
                    for key, value in component_values.items()},
                actual_archived_photo_rhs=photo_rhs(y).tolist(),
                gas_jacobian=matrix_scales(fine), direct_photo_jacobian=matrix_scales(photo_jac),
                fixed_depth_gas_block=matrix_scales(fine+photo_jac),
                checkpoint_pchip_defect=path_defect,
                depth_coupling={"B_row_l1": b_rows.tolist(),
                    "B_inf_norm": float(b_rows.max()),
                    "C_column_max_abs": c_columns.tolist(),
                    "C_inf_norm": float(np.abs(c_depth).sum(axis=1).max()) if active else 0.0,
                    "BC_matrix_per_z_squared": (b_depth @ c_depth).tolist(),
                    "BC_induced_inf_norm_per_z_squared": float(np.linalg.norm(b_depth @ c_depth, ord=np.inf)),
                    "gas_to_depth_has_direct_thermal_column": bool(np.any(c_depth[:, 4])),
                    "max_active_optical_depth": float(np.max(state[27:27+active])) if active else 0.0,
                    "positive_saved_births_with_exp_underflow": int(np.sum(population == 0))},
                checks={"gas_two_step_relative_matrix_difference": fd_error,
                    "photo_analytic_vs_central_fd_relative_difference": photo_fd_error,
                    "original_section_rhs_vs_block_assembly_max_abs": assembly_error,
                    "native_mask_additivity_max_abs_in_original_27_coordinates": additivity},
                central_fd_steps=fd_steps.tolist(), native_rhs_calls=native_calls-first_call)
            if cx_matrix is not None:
                row["charge_exchange_only_jacobian"] = matrix_scales(cx_matrix)
            rows.append(row)
        model.server = None
        if server.calls != native_calls:
            raise AssertionError("native call count mismatch")

    # Read identities again after imports and native calls: original source,
    # selected inputs and checkpoints must remain byte-identical.
    for relative, value in source_identity.items():
        if sha(root / relative) != value["sha256"]:
            raise AssertionError("original input/source changed during diagnostic")
    gaps = np.diff(knots)
    result = {
        "schema": "rei.run16.recorded-state-feedback.v1",
        "status": "NUMERICALLY_CHECKED",
        "scope": "Three original tight M2 recorded states; point derivatives and exact finite-packet photon blocks; no trajectory or continuum error bound",
        "coordinates": COORDINATES,
        "coordinate_normalizations": {"H_per_initial_H": h_total,
            "D_per_initial_H": d_total, "He_per_initial_H": he_total,
            "initial_thermal_eV_per_H": u_initial},
        "lift_matrix_to_original_gas_14": lift.tolist(),
        "full_state_dimension": model.dim, "cohorts_after_exact_reflection": model.m,
        "tight_checkpoint_z": knots.tolist(),
        "tight_gas_knots_original_14": gas_knots.tolist(),
        "gas_knots_float64_le_sha256": hashlib.sha256(gas_knots.astype("<f8").tobytes()).hexdigest(),
        "largest_checkpoint_gap": {"left": float(knots[np.argmax(gaps)]),
            "right": float(knots[np.argmax(gaps)+1]), "width": float(gaps.max())},
        "first_birth_z": float(model.birth.min()),
        "native_rhs_calls": native_calls, "native_calls_wall_seconds": native_wall,
        "native_ivp_solves": 0, "historical_test_reruns": 0,
        "derived_trajectory_solve_count": 0,
        "records": rows,
        "gas_binary": {"path": str(binary), "bytes": binary.stat().st_size, "sha256": sha(binary)},
        "source_root": str(root), "original_manifest_sha256": sha(root/"SHA256SUMS.txt"),
        "verified_source_input_files": source_identity,
        "source_bytes_unchanged_after_execution": True,
        "environment": {"python": sys.version, "executable": sys.executable,
            "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform()},
        "command_argv": sys.argv, "code_sha256": sha(__file__),
        "value_trace": {"file": trace_path.name, "bytes": trace_path.stat().st_size,
            "sha256": sha(trace_path), "encoding": "parsed native f64 values, not an exact raw protocol-wire recording"},
        "wall_seconds": time.perf_counter()-started,
        "unresolved": ["continuous residual envelopes", "admissible tube Jacobian enclosures",
            "between-checkpoint gas error", "continuous spectral photo-forcing defect",
            "birth and angular continuum", "coupled continuum survivor error"],
    }
    write_json(out/"RECORDED_STATE_FEEDBACK.json", result)
    print(json.dumps({"status": result["status"], "native_rhs_calls": native_calls,
        "native_calls_wall_seconds": native_wall, "wall_seconds": result["wall_seconds"],
        "records": [{"z": r["z"], "gas_norm_inf": r["gas_jacobian"]["induced_inf_norm"],
            "gas_log_norm_inf": r["gas_jacobian"]["inf_logarithmic_norm"],
            "gas_eigenvalues": r["gas_jacobian"]["eigenvalues"],
            "photo_norm_inf": r["direct_photo_jacobian"]["induced_inf_norm"],
            "checks": r["checks"]} for r in rows]}, allow_nan=False))


if __name__ == "__main__":
    main()
