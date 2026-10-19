#!/usr/bin/env python3
"""One additional 5D source-free solve with half the maximum step.

The earlier two tolerance settings used identical grids. This separate unit
preserves them and supplies the requested discretization contrast. No transport
or post-first-birth trajectory is evaluated.
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
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import numpy as np
import scipy
from scipy.integrate import solve_ivp

EXPECTED_POINT = "385f61f57b5d314dbf69d2111f5576bf4be09fc0d94f67682eeb7a95daf25515"
EXPECTED_PREFIX = "617059f5f170f74f95f1fa9822a3bc31d5acb7c213add7aae760334a5a784d92"
EXPECTED_GAS = "3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", required=True, type=Path)
    ap.add_argument("--gas-binary", required=True, type=Path)
    ap.add_argument("--point-result", required=True, type=Path)
    ap.add_argument("--prefix-result", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    root = args.source_root.resolve()
    binary = args.gas_binary.resolve()
    point_path = args.point_result.resolve()
    prefix_path = args.prefix_result.resolve()
    if (sha(point_path), sha(prefix_path), sha(binary)) != (
            EXPECTED_POINT, EXPECTED_PREFIX, EXPECTED_GAS):
        raise ValueError("point/prefix/original executable identity mismatch")
    point = json.loads(point_path.read_text())
    prior = json.loads(prefix_path.read_text())
    if sha(root/"SHA256SUMS.txt") != point["original_manifest_sha256"]:
        raise ValueError("original manifest identity mismatch")
    for relative, item in point["verified_source_input_files"].items():
        if sha(root/relative) != item["sha256"]:
            raise ValueError(f"original source/input mismatch: {relative}")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    sys.path.insert(0, str(root/"scripts"))
    native = importlib.import_module("retarded_integrator")
    if Path(native.ROOT).resolve() != root:
        raise ValueError("wrong original source import")
    packet = json.loads((root/"inputs/spectral11/m2.json").read_text())
    model = native.RetardedModel(native.coalesce_reflections(packet))
    z_end = float(model.birth.min())
    reference = prior["solution_records"][1]
    if (prior["source_free_domain_z"] != [0.0, z_end] or
            z_end != 0.004989333151072248 or reference["nominal_rtol"] != 6e-12):
        raise ValueError("wrong prior prefix reference")
    selected = np.array([2,4,11,12,13])
    nc = point["coordinate_normalizations"]
    scale = np.array([nc["H_per_initial_H"], nc["D_per_initial_H"],
        nc["He_per_initial_H"], nc["He_per_initial_H"], nc["initial_thermal_eV_per_H"]])
    lift = np.asarray(point["lift_matrix_to_original_gas_14"])
    gas0 = model.y0[:14].copy()
    if not np.array_equal(gas0, np.asarray(prior["initial_gas_14_exact"])):
        raise ValueError("initial state changed")
    q0 = gas0[selected]/scale
    def unpack(q):
        return gas0 + lift@(q-q0)
    n_calls = 0
    call_wall = 0.0
    trace_path = out/"NATIVE_STEPHALF_RHS_VALUE_TRACE.jsonl"
    solve_start = time.perf_counter()
    with trace_path.open("x") as trace, native.GasServer(path=binary) as server:
        def rhs(z, q):
            nonlocal n_calls, call_wall
            if n_calls >= 1000 or time.perf_counter()-solve_start > 20:
                raise TimeoutError("bounded source-free half-step solve")
            if not 0 <= z <= z_end:
                raise ValueError("outside pre-birth domain")
            gas = unpack(q)
            if (gas[:13] < 0).any() or gas[13] <= 0:
                raise ValueError("negative gas stage; no clipping")
            a, _, hubble, _ = model.geometry(float(z))
            volume = (a/model.a0)**3
            proper = gas*model.gscale[:14]/volume
            tcmb = 2.7255/a
            before = time.perf_counter()
            answer = server.rhs(proper, tcmb, mask=7)
            call_wall += time.perf_counter()-before
            n_calls += 1
            trace.write(json.dumps({"call":n_calls,"z":float(z),"mask":7,
                "tcmb_K":float(tcmb),"proper_state_14":proper.tolist(),
                "native_payload_28":answer.tolist()},allow_nan=False)+"\n")
            value = model.dx*volume/hubble*answer[:14]/model.gscale[:14]
            value[13] -= 2*model.dx*gas[13]
            return value[selected]/scale
        norm_factor = float(np.sqrt(5))
        rtol = 6e-12/norm_factor
        atol = np.full(5,1e-15)/norm_factor
        solved = solve_ivp(rhs,(0,z_end),q0,method="DOP853",rtol=rtol,atol=atol,
                           max_step=z_end/8,dense_output=True)
        if not solved.success or solved.t[-1] != z_end:
            raise RuntimeError(str(solved.message))
        if server.calls != n_calls or model.calls != 0 or solved.y.shape[0] != 5:
            raise AssertionError("native counter or five-dimensional scope mismatch")
    z_sample = np.asarray(reference["sample_z"])
    q_sample = solved.sol(z_sample).T
    gas_sample = np.asarray([unpack(q) for q in q_sample])
    gas_accepted = np.asarray([unpack(q) for q in solved.y.T])
    if (gas_accepted[:,:13] < 0).any() or (gas_accepted[:,13] <= 0).any():
        raise ValueError("negative accepted gas")
    if (gas_sample[:,:13] < 0).any() or (gas_sample[:,13] <= 0).any():
        raise ValueError("negative sampled gas")
    temperature = 2*gas_sample[:,13]*native.EV_J / (
        3*native.KB*(gas_sample[:,:13]@(1+native.CHARGE)))
    old_gas = np.asarray(reference["sample_gas_14"])
    old_t = np.asarray(reference["sample_T_K"])
    rel_h = gas_sample[:,1]/old_gas[:,1]-1
    delta_t = temperature-old_t
    delta_q = q_sample-np.asarray(reference["sample_q"])
    max_check = float(max(np.max(np.abs(rel_h)),np.max(np.abs(delta_t))/1e4))
    if not max_check < 1e-10:
        raise AssertionError("predeclared prefix step-halving numerical gate failed")
    comparisons=[]
    for j,z in enumerate(z_sample):
        old_comparison = prior["comparisons"][j]
        comparisons.append({"z":float(z),"halfstep_minus_prior_HI_relative":float(rel_h[j]),
            "halfstep_minus_prior_T_K":float(delta_t[j]),
            "halfstep_minus_prior_q":delta_q[j].tolist(),
            "pchip_minus_halfstep_HI_relative":float(old_comparison["pchip_HI_per_initial_H"]/gas_sample[j,1]-1),
            "pchip_minus_halfstep_T_K":float(old_comparison["pchip_T_K"]-temperature[j]),
            "halfstep_HI_per_initial_H":float(gas_sample[j,1]),"halfstep_T_K":float(temperature[j])})
    for relative,item in point["verified_source_input_files"].items():
        if sha(root/relative) != item["sha256"]:
            raise AssertionError("original source/input changed")
    result={"schema":"rei.run16.source-free-prefix-step-halving.v1",
        "status":"NUMERICALLY_CHECKED","source_free_domain_z":[0.0,z_end],
        "right_endpoint_convention":"pre-activation left limit at first birth",
        "reason":"Earlier two tolerance settings had identical accepted grids and sampled states; this new solve halves max_step",
        "native_rhs_calls":n_calls,"native_call_wall_seconds":call_wall,
        "five_dimensional_prefix_solves_this_unit":1,
        "prefix_solves_including_prior":3,"prefix_native_calls_including_prior":n_calls+prior["native_rhs_calls"],
        "full_transport_ivp_solves":0,"historical_m2_reruns":0,"historical_test_reruns":0,
        "method":"DOP853","nominal_rtol":6e-12,"effective_rtol":rtol,
        "effective_atol_5":atol.tolist(),"max_step":z_end/8,"dimension":5,
        "nfev":solved.nfev,"accepted_z":solved.t.tolist(),"accepted_q":solved.y.T.tolist(),
        "sample_z":z_sample.tolist(),"sample_q":q_sample.tolist(),
        "sample_gas_14":gas_sample.tolist(),"sample_T_K":temperature.tolist(),
        "comparisons":comparisons,
        "checks":{"max_relative_HI_difference":float(np.max(np.abs(rel_h))),
            "max_T_difference_K":float(np.max(np.abs(delta_t))),
            "max_coordinate_difference":float(np.max(np.abs(delta_q))),
            "predeclared_gate_relative_HI_or_deltaT_over10000":1e-10,
            "original_source_input_112_unchanged":True,
            "nuclear_total_drift_per_initial_H":[float(np.max(np.abs(gas_accepted[:,ids].sum(axis=1)-gas0[ids].sum())))
                for ids in ([1,2],[3,4],[10,11,12])]},
        "point_result":{"file":str(point_path),"sha256":sha(point_path)},
        "prior_prefix_result":{"file":str(prefix_path),"sha256":sha(prefix_path)},
        "source_root":str(root),"packet_sha256":sha(root/"inputs/spectral11/m2.json"),
        "gas_binary":{"file":str(binary),"sha256":sha(binary),"bytes":binary.stat().st_size},
        "code_sha256":sha(__file__),"command_argv":sys.argv,
        "environment":{"python":sys.version,"python_executable":sys.executable,
            "numpy":np.__version__,"scipy":scipy.__version__,"platform":platform.platform()},
        "trace":{"file":trace_path.name,"bytes":trace_path.stat().st_size,"sha256":sha(trace_path),
            "encoding":"parsed native f64 values, not raw protocol bytes"},
        "proof_scope":"sampled numerical step-size contrast only; no rigorous trajectory enclosure or post-birth extrapolation",
        "total_wall_seconds":time.perf_counter()-started}
    with (out/"PREFIX_STEP_HALVING.json").open("x") as stream:
        json.dump(result,stream,indent=2,allow_nan=False);stream.write("\n")
    print(json.dumps({"status":result["status"],"native_rhs_calls":n_calls,
        "accepted_z":result["accepted_z"],"checks":result["checks"],
        "total_wall_seconds":result["total_wall_seconds"],"comparisons":comparisons},allow_nan=False))


if __name__ == "__main__":
    main()
