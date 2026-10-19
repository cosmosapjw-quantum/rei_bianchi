#!/usr/bin/env python3
"""Two new five-coordinate source-free prefix solves before the first birth.

This does not repeat RUN13 transport or use any photon/depth ODE coordinates.
It uses the original native gas owner and prescribed geometry. The pair gives
numerical evidence for the initial checkpoint-PCHIP bias, not a rigorous tube.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import sys
import time

sys.dont_write_bytecode = True
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator

POINT_RESULT_SHA = "385f61f57b5d314dbf69d2111f5576bf4be09fc0d94f67682eeb7a95daf25515"
GAS_SHA = "3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", required=True, type=Path)
    ap.add_argument("--gas-binary", required=True, type=Path)
    ap.add_argument("--point-result", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--wall-cap-seconds", type=float, default=20.0)
    args = ap.parse_args()
    if not 0 < args.wall_cap_seconds <= 20:
        raise ValueError("combined prefix solve wall cap must be at most twenty seconds")
    root = args.source_root.resolve()
    binary = args.gas_binary.resolve()
    point_path = args.point_result.resolve()
    out = args.output_dir.resolve()
    if digest(point_path) != POINT_RESULT_SHA or digest(binary) != GAS_SHA:
        raise ValueError("explicit original point/binary identity mismatch")
    point = json.loads(point_path.read_text())
    if digest(root/"SHA256SUMS.txt") != point["original_manifest_sha256"]:
        raise ValueError("different original source manifest")
    for relative, identity in point["verified_source_input_files"].items():
        if digest(root/relative) != identity["sha256"]:
            raise ValueError(f"changed source/input: {relative}")
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    sys.path.insert(0, str(root/"scripts"))
    native = importlib.import_module("retarded_integrator")
    if Path(native.ROOT).resolve() != root:
        raise ValueError("wrong original module imported")
    packet = json.loads((root/"inputs/spectral11/m2.json").read_text())
    model = native.RetardedModel(native.coalesce_reflections(packet))
    z_end = float(model.birth.min())
    if z_end != point["first_birth_z"] or z_end != 0.004989333151072248:
        raise ValueError("unexpected first source activation")
    selected = np.array([2, 4, 11, 12, 13])
    norms = point["coordinate_normalizations"]
    scale = np.array([norms["H_per_initial_H"], norms["D_per_initial_H"],
        norms["He_per_initial_H"], norms["He_per_initial_H"], norms["initial_thermal_eV_per_H"]])
    lift = np.asarray(point["lift_matrix_to_original_gas_14"])
    gas0 = model.y0[:14].copy()
    q0 = gas0[selected]/scale

    def gas_from_q(q):
        return gas0 + lift@(q-q0)

    if not np.array_equal(gas_from_q(q0), gas0):
        raise AssertionError("initial state must remain exactly original")
    gas_knots = np.asarray(point["tight_gas_knots_original_14"])
    if hashlib.sha256(gas_knots.astype("<f8").tobytes()).hexdigest() != point["gas_knots_float64_le_sha256"]:
        raise ValueError("gas knot payload identity mismatch")
    pchip = PchipInterpolator(point["tight_checkpoint_z"], gas_knots,
                               axis=0, extrapolate=False)
    z_check = np.linspace(0, z_end, 5)
    trace_path = out/"NATIVE_PREFIX_RHS_VALUE_TRACE.jsonl"
    native_count = 0
    native_wall = 0.0
    solve_records = []
    solve_start = time.perf_counter()
    with trace_path.open("x") as trace, native.GasServer(path=binary) as server:
        def rhs(z, q):
            nonlocal native_count, native_wall
            if time.perf_counter()-solve_start > args.wall_cap_seconds or native_count >= 1000:
                raise TimeoutError("source-free prefix native call/wall budget")
            if not 0 <= z <= z_end:
                raise ValueError("prefix RHS beyond first-birth domain")
            gas = gas_from_q(q)
            if (gas[:13] < 0).any() or gas[13] <= 0:
                raise ValueError("unphysical prefix stage; no clipping")
            a, _, hubble, _ = model.geometry(float(z))
            volume = (a/model.a0)**3
            proper = gas*model.gscale[:14]/volume
            tcmb = 2.7255/a
            before = time.perf_counter()
            raw = server.rhs(proper, tcmb, mask=7)
            native_wall += time.perf_counter()-before
            native_count += 1
            trace.write(json.dumps({"call": native_count, "z": float(z), "mask": 7,
                "tcmb_K": float(tcmb), "proper_state_14": proper.tolist(),
                "native_payload_28": raw.tolist()}, allow_nan=False)+"\n")
            gas_rate = model.dx*volume/hubble*raw[:14]/model.gscale[:14]
            gas_rate[13] -= 2*model.dx*gas[13]
            return gas_rate[selected]/scale

        for nominal_rtol in (3e-11, 6e-12):
            norm_factor = float(np.sqrt(5))
            effective_rtol = nominal_rtol/norm_factor
            effective_atol = np.full(5, 1e-15)/norm_factor
            first_count = native_count
            before = time.perf_counter()
            solved = solve_ivp(rhs, (0.0, z_end), q0, method="DOP853",
                rtol=effective_rtol, atol=effective_atol, max_step=z_end/4,
                dense_output=True)
            if not solved.success or solved.t[-1] != z_end:
                raise RuntimeError(str(solved.message))
            if solved.y.shape[0] != 5 or model.calls != 0:
                raise AssertionError("only five gas variables and no inherited full RHS allowed")
            accepted_gas = np.array([gas_from_q(q) for q in solved.y.T])
            if (accepted_gas[:, :13] < 0).any() or (accepted_gas[:, 13] <= 0).any():
                raise ValueError("unphysical accepted prefix state")
            evaluated = solved.sol(z_check).T
            gas_values = np.array([gas_from_q(q) for q in evaluated])
            if (gas_values[:, :13] < 0).any() or (gas_values[:, 13] <= 0).any():
                raise ValueError("unphysical sampled dense prefix state")
            temperatures = 2*gas_values[:, 13]*native.EV_J / (
                3*native.KB*(gas_values[:, :13]@(1+native.CHARGE)))
            solve_records.append({"nominal_rtol": nominal_rtol,
                "effective_rtol": effective_rtol, "effective_atol_5": effective_atol.tolist(),
                "error_norm": "component_scaled_L2_in_five_invariant_coordinates",
                "method": "DOP853", "max_step": z_end/4,
                "dimension": 5, "status": "COMPLETE", "nfev": solved.nfev,
                "native_rhs_calls": native_count-first_count,
                "accepted_z": solved.t.tolist(), "accepted_q": solved.y.T.tolist(),
                "sample_z": z_check.tolist(), "sample_q": evaluated.tolist(),
                "sample_gas_14": gas_values.tolist(), "sample_T_K": temperatures.tolist(),
                "minimum_accepted_active_density_per_initial_H": float(accepted_gas[:, [1,2,3,4,10,11,12]].min()),
                "maximum_nuclear_total_drift_per_initial_H": [
                    float(np.max(np.abs(accepted_gas[:, idx].sum(axis=1)-gas0[idx].sum())))
                    for idx in ([1,2],[3,4],[10,11,12])],
                "wall_seconds": time.perf_counter()-before})
        if native_count != server.calls:
            raise AssertionError("native call count mismatch")
    coarse, tight = solve_records
    coarse_gas = np.asarray(coarse["sample_gas_14"])
    tight_gas = np.asarray(tight["sample_gas_14"])
    pchip_gas = pchip(z_check)
    pchip_t = 2*pchip_gas[:, 13]*native.EV_J / (
        3*native.KB*(pchip_gas[:, :13]@(1+native.CHARGE)))
    pair_h = coarse_gas[:, 1]/tight_gas[:, 1]-1
    pair_t = np.asarray(coarse["sample_T_K"])-np.asarray(tight["sample_T_K"])
    if max(np.max(np.abs(pair_h)), np.max(np.abs(pair_t))/1e4) > 1e-10:
        raise AssertionError("prefix tolerance contrast exceeds the predeclared numerical comparison gate")
    comparisons = []
    for j, z in enumerate(z_check):
        comparisons.append({"z": float(z), "fraction_of_prefix": j/4,
            "tight_native_HI_per_initial_H": float(tight_gas[j,1]),
            "pchip_HI_per_initial_H": float(pchip_gas[j,1]),
            "pchip_minus_native_HI_per_initial_H": float(pchip_gas[j,1]-tight_gas[j,1]),
            "pchip_minus_native_HI_relative": float(pchip_gas[j,1]/tight_gas[j,1]-1),
            "tight_native_T_K": float(tight["sample_T_K"][j]),
            "pchip_T_K": float(pchip_t[j]),
            "pchip_minus_native_T_K": float(pchip_t[j]-tight["sample_T_K"][j]),
            "coarse_minus_tight_HI_relative": float(pair_h[j]),
            "coarse_minus_tight_T_K": float(pair_t[j]),
            "pchip_minus_native_DII_fraction": float((pchip_gas[j,4]-tight_gas[j,4])/scale[1])})
    for relative, identity in point["verified_source_input_files"].items():
        if digest(root/relative) != identity["sha256"]:
            raise AssertionError("original source/input changed")
    result = {"schema":"rei.run16.source-free-prefix.v1", "status":"NUMERICALLY_CHECKED",
        "scope":"Two new 5D gas-only prefix solves before the first archived photon birth; no full transport or historical M2 rerun",
        "source_free_domain_z":[0.0,z_end], "right_endpoint_convention":"pre-activation left limit at first birth",
        "source_root":str(root), "packet_sha256":digest(root/"inputs/spectral11/m2.json"),
        "point_result":{"path":str(point_path),"sha256":digest(point_path)},
        "gas_binary":{"path":str(binary),"bytes":binary.stat().st_size,"sha256":digest(binary)},
        "initial_gas_14_exact":gas0.tolist(),"coordinates":point["coordinates"],
        "native_rhs_calls":native_count,"native_call_wall_seconds":native_wall,
        "five_dimensional_gas_only_prefix_solves":2,"full_transport_ivp_solves":0,
        "historical_m2_reruns":0,"historical_test_reruns":0,
        "solution_records":solve_records,"comparisons":comparisons,
        "checks":{"coarse_tight_relative_HI_difference_max":float(np.max(np.abs(pair_h))),
            "coarse_tight_temperature_difference_K_max":float(np.max(np.abs(pair_t))),
            "predeclared_pair_gate_max_relative_HI_or_deltaT_over10000":1e-10,
            "source_input_identities_112_unchanged":True,"original_initial_state_exact":True},
        "interpretation":"Numerical evidence for an initial PCHIP bias; no rigorous enclosed trajectory, error bound, or post-first-birth inference",
        "code_sha256":digest(__file__),"command_argv":sys.argv,
        "environment":{"python":sys.version,"python_executable":sys.executable,
            "numpy":np.__version__,"scipy":scipy.__version__,"platform":platform.platform()},
        "trace":{"file":trace_path.name,"bytes":trace_path.stat().st_size,
            "sha256":digest(trace_path),"encoding":"parsed f64 values; not raw wire bytes"},
        "total_wall_seconds":time.perf_counter()-started}
    save(out/"SOURCE_FREE_PREFIX.json",result)
    print(json.dumps({"status":result["status"],"native_rhs_calls":native_count,
        "native_call_wall_seconds":native_wall,"total_wall_seconds":result["total_wall_seconds"],
        "checks":result["checks"],"comparisons":comparisons},allow_nan=False))


if __name__ == "__main__":
    main()
