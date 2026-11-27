"""Create-only, shared-lease PHYS80 isolated runs; never rerun PHYS79 solves."""
from __future__ import annotations
import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"
import argparse
import hashlib
import json
import platform
import time
import traceback
import uuid
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from phys79_bridge import ROOT, PROVENANCE, CASES, atomic, lease_module, parent_controls as old
from reduced import ExactReduction, MODEL_ID

canonical, digest, sha_file = old.canonical, old.digest, old.sha_file
publish_json, publish_bytes, now = old.publish_json, old.publish_bytes, old.now


def source_manifest():
    relatives = ["source/phys79_bridge.py", "source/reduced.py", "source/run_reduced.py",
                 "inputs/REDUCTION_PLAN.json", "vendor/PHYS79_PROVENANCE.json"]
    for relative, meta in PROVENANCE["files"].items():
        p = ROOT/relative
        if p.stat().st_size != meta["bytes"] or sha_file(p) != meta["sha256"]:
            raise RuntimeError("PINNED_PARENT_BYTES_CHANGED:" + relative)
        relatives.append(relative)
    entries = {r: {"bytes": (ROOT/r).stat().st_size, "sha256": sha_file(ROOT/r)}
               for r in sorted(set(relatives))}
    return {"files": entries, "sha256": digest(entries), "parent_head": PROVENANCE["parent_head"]}


def prepare(spec, plan, manifest):
    parent = CASES[spec["parent_task"]]
    physics = parent["binding"]["physics"]
    model = ExactReduction(physics)
    numerics = dict(plan["solver"][spec["tolerance"]])
    numerics.update(method="Radau", analytic_jacobian=True,
                    dimension=len(model.z0), max_step="unbounded_solver_controlled",
                    dense_samples=161, internal_accepted_mesh_saved=True,
                    strict_nonnegative_trials=True, projection="NONE")
    binding = {"schema": "PHYS80_REDUCED_ISOLATED_SCIENCE_ID_V1",
               "model": MODEL_ID, "physics": physics, "numerics": numerics,
               "source": manifest, "parent_physics_id": parent["physics_id"],
               "parent_comparison_science_id": parent["science_id"],
               "dependencies": {"Python": platform.python_version(),
                                "NumPy": np.__version__, "SciPy": scipy.__version__}}
    return {"task_id": spec["id"], "science_id": digest(binding), "binding": binding,
            "model": model, "parent": parent,
            "parent_npz": ROOT/"inputs/phys79_cases"/(parent["science_id"]+".npz")}


def existing(output, task):
    key = task["science_id"]
    receipt = output/"cases"/(key+".json")
    if receipt.exists():
        data = receipt.read_bytes()
        expected = receipt.with_suffix(".json.sha256").read_text().strip()
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError("EXISTING_RECEIPT_SHA_MISMATCH")
        d = json.loads(data)
        if d["binding"] != task["binding"] or d["science_id"] != key:
            raise RuntimeError("EXISTING_BINDING_MISMATCH")
        if d["status"] == "COMPLETE":
            p = output/d["npz"]["path"]
            if p.stat().st_size != d["npz"]["bytes"] or sha_file(p) != d["npz"]["sha256"]:
                raise RuntimeError("EXISTING_NPZ_SHA_MISMATCH")
            return "SKIP_COMPLETE_VERIFIED"
        return "BLOCKED_PREVIOUS_FAILED_IDENTITY"
    if ((output/"cases"/(key+".npz")).exists()
            or receipt.with_suffix(".json.sha256").exists()
            or (output/"claims"/(key+".json")).exists() or (output/"attempts"/key).exists()):
        return "BLOCKED_PREVIOUS_PARTIAL_IDENTITY"
    return "READY"


def full_states(model, zs):
    rows = []
    for z in np.asarray(zs):
        y, u, t, _, _ = model.state(z)
        model.network.rate_coefficients(t)
        rows.append(np.r_[y, u])
    return np.array(rows)


def scalar_diagnostic(task):
    p = task["binding"]["physics"]
    model = task["model"]
    return {"network": model.network, "binding": {"physics": p},
            "initial_state": np.r_[model.y0, model.u0],
            "isotope_totals": atomic.ISOTOPE_SUM@model.y0,
            "scale": np.array(task["parent"]["binding"]["numerics"]["scale_vector"])}


def execute_one(output, task, plan, lease, observation):
    key = task["science_id"]
    attempt = output/"attempts"/key/uuid.uuid4().hex
    called = False
    claimed = False
    rhs_count = jac_count = 0
    last = {}
    started = now()
    wall = time.perf_counter()
    try:
        status = existing(output, task)
        if status != "READY":
            return {"task_id": task["task_id"], "science_id": key, "status": status, "new_ODE_calls": 0}
        if source_manifest() != task["binding"]["source"]:
            raise RuntimeError("SOURCE_CHANGED_BEFORE_SOLVE")
        publish_json(output/"claims"/(key+".json"),
                     {"science_id": key, "started_utc": started, "pid": os.getpid(),
                      "attempt": str(attempt.relative_to(output)), "lease": lease})
        claimed = True
        attempt.mkdir(parents=True)
        publish_json(attempt/"STARTED.json",
                     {"task_id": task["task_id"], "science_id": key, "binding": task["binding"],
                      "resources": observation, "lease": lease, "started_utc": started})
        model = task["model"]
        p, num = task["binding"]["physics"], task["binding"]["numerics"]
        def rhs(t, z):
            nonlocal rhs_count
            rhs_count += 1
            last.update(callback="rhs", theta=float(t), z=z.tolist())
            return model.rhs(t, z)
        def jac(t, z):
            nonlocal jac_count
            jac_count += 1
            last.update(callback="jacobian", theta=float(t), z=z.tolist())
            return model.jacobian(t, z)
        publish_json(attempt/"SOLVE_IVP_CALL_0001.json",
                     {"utc": now(), "call_index": 1, "method": "Radau",
                      "dimension": len(model.z0), "new_algorithm_identity": True,
                      "old_completed_identity_replay": False})
        called = True
        solve_start = time.perf_counter()
        sol = solve_ivp(rhs, (0., p["theta_end"]), model.z0, method="Radau",
                        jac=jac, rtol=num["rtol"], atol=num["atol_scaled"],
                        dense_output=True)
        solve_wall = time.perf_counter()-solve_start
        solver = {"success": bool(sol.success), "message": sol.message,
                  "nfev": int(sol.nfev), "njev": int(sol.njev), "nlu": int(sol.nlu),
                  "rhs_calls": rhs_count, "jacobian_calls": jac_count,
                  "accepted_mesh_points": len(sol.t), "solve_wall_s": solve_wall,
                  "new_ODE_calls": 1}
        publish_json(attempt/"SOLVE_IVP_RETURNED.json", solver)
        with (attempt/"RAW_SOLVER_RESULT.npz").open("xb") as stream:
            np.savez_compressed(stream, accepted_theta=sol.t, accepted_z=sol.y.T)
        if not sol.success or sol.t[-1] != p["theta_end"]:
            raise RuntimeError("SOLVER_DID_NOT_REACH_END")
        accepted = full_states(model, sol.y.T)
        theta = np.linspace(0., p["theta_end"], 161)
        z = sol.sol(theta).T
        physical = full_states(model, z)
        legacy_task = scalar_diagnostic(task)
        legacy_plan = json.loads((ROOT/"vendor/phys79/inputs/CONTROL_PLAN.json").read_text())
        arrays, checks, oracle = old.saved_arrays_and_checks(legacy_task, theta, physical, legacy_plan)
        accepted_energy = accepted[:, -1]+accepted[:, :-1]@model.eps
        checks["accepted_mesh_min_species"] = float(accepted[:, :-1].min())
        checks["accepted_mesh_min_u"] = float(accepted[:, -1].min())
        checks["accepted_mesh_energy_relative_max"] = float(
            np.max(abs(accepted_energy/accepted_energy[0]-1)))
        checks["all_accepted_mesh_source_domains"] = "PASS"
        with np.load(task["parent_npz"], allow_pickle=False) as baseline:
            if not np.array_equal(theta, baseline["theta"]):
                raise RuntimeError("PARENT_COMPARISON_GRID_MISMATCH")
            error = physical-np.c_[baseline["Y"], baseline["u_eV_per_H"]]
            scaled_error = error/legacy_task["scale"]
            checks["parent_max_scaled_state_error"] = float(np.max(abs(scaled_error)))
            checks["parent_max_temperature_abs_error_K"] = float(np.max(abs(arrays["T_K"]-baseline["T_K"])))
            arrays["parent_scaled_state_difference"] = scaled_error
        gates = plan["acceptance_fixed_before_execution"]
        checks["passed"] = bool(checks["passed"]
            and checks["parent_max_scaled_state_error"] <= gates["parent_trajectory_max_scaled_error"]
            and checks["accepted_mesh_energy_relative_max"] <= gates["total_u_plus_binding_relative"])
        checks["energy_residual_scope"] = "first-integral construction; independent evidence is lifted RHS and parent trajectory"
        checks["continuum_certificate"] = False
        arrays.update(reduced_z=z, accepted_theta=sol.t, accepted_z=sol.y.T,
                      accepted_raw_states=accepted)
        with (attempt/"RESULT.npz").open("xb") as stream:
            np.savez_compressed(stream, **arrays)
        publish_json(attempt/"POSTFLIGHT.json", {"checks": checks, "oracle": oracle})
        if not checks["passed"]:
            raise ArithmeticError("PREDECLARED_REDUCTION_GATES_FAILED")
        if source_manifest() != task["binding"]["source"]:
            raise RuntimeError("SOURCE_CHANGED_DURING_SOLVE")
        target = output/"cases"/(key+".npz")
        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(attempt/"RESULT.npz", target)
        record = {"status": "COMPLETE", "task_id": task["task_id"], "science_id": key,
                  "binding": task["binding"], "parent_physics_id": task["parent"]["physics_id"],
                  "started_utc": started, "completed_utc": now(), "solver": solver,
                  "wall_s": time.perf_counter()-wall, "checks": checks, "oracle": oracle,
                  "attempt": str(attempt.relative_to(output)),
                  "npz": {"path": str(target.relative_to(output)), "bytes": target.stat().st_size,
                          "sha256": sha_file(target)},
                  "provenance": {"lease": lease, "resources": observation,
                                 "old_completed_replays": 0, "new_cosmological_ODE": 0,
                                 "NCP": 0, "benchmark": 0},
                  "HH_R10": "OFF", "production_admission": "NOT_ISSUED"}
        old.write_case_receipt(output, key, record)
        return {"task_id": task["task_id"], "science_id": key, "status": "COMPLETE",
                "new_ODE_calls": 1, "solver": solver, "checks": checks}
    except Exception as exc:
        failure = {"status": "FAILED", "task_id": task["task_id"], "science_id": key,
                   "binding": task["binding"], "failed_utc": now(),
                   "new_ODE_calls": int(called), "rhs_calls": rhs_count,
                   "jacobian_calls": jac_count, "last_trial": last,
                   "error": repr(exc), "traceback": traceback.format_exc(),
                   "attempt": str(attempt.relative_to(output)),
                   "old_completed_replays": 0}
        if not claimed:
            # A racing process may own this identity. Never write its receipt.
            failure["status"] = "BLOCKED_UNOWNED_ATTEMPT"
            publish_json(output/"diagnostics"/(uuid.uuid4().hex+".json"), failure)
            return {"task_id": task["task_id"], "science_id": key,
                    "status": "BLOCKED_UNOWNED_ATTEMPT", "new_ODE_calls": 0, "error": repr(exc)}
        attempt.mkdir(parents=True, exist_ok=True)
        publish_json(attempt/"FAILED.json", failure)
        if not (output/"cases"/(key+".json")).exists():
            old.write_case_receipt(output, key, failure)
        return {"task_id": task["task_id"], "science_id": key, "status": "FAILED",
                "new_ODE_calls": int(called), "error": repr(exc)}


def run(output, execute=False):
    output = Path(output)
    plan = json.loads((ROOT/"inputs/REDUCTION_PLAN.json").read_text())
    manifest = source_manifest()
    tasks = [prepare(s, plan, manifest) for s in plan["tasks"]]
    entries = []
    pool_module = lease_module()
    pool = pool_module.LeasePool(path="/tmp/rei-bianchi-cooperative-leases", site="local")
    for task in tasks:
        status = existing(output, task)
        if status != "READY" or not execute:
            entries.append({"task_id": task["task_id"], "science_id": task["science_id"],
                            "status": status, "new_ODE_calls": 0})
            continue
        lease, observation = pool.acquire("PHYS80:"+task["science_id"])
        if lease is None:
            entries.append({"task_id": task["task_id"], "science_id": task["science_id"],
                            "status": "WAITING_NO_LEASE", "new_ODE_calls": 0, "resources": observation})
            break
        try:
            result = execute_one(output, task, plan, lease, observation)
            entries.append(result)
        finally:
            pool_module.release_lease(lease)
        if result["status"] != "COMPLETE":
            break
    refinement = None
    byid = {t["task_id"]: t for t in tasks}
    a, b = byid["C01_REDUCED_BASE"], byid["C01_REDUCED_REFINED"]
    if existing(output, a) == existing(output, b) == "SKIP_COMPLETE_VERIFIED":
        with np.load(output/"cases"/(a["science_id"]+".npz")) as aa, np.load(output/"cases"/(b["science_id"]+".npz")) as bb:
            diff = float(np.max(abs(aa["scaled_states"]-bb["scaled_states"])))
        refinement = {"max_scaled_state_difference": diff,
                      "gate": plan["acceptance_fixed_before_execution"]["reduced_refinement_max_scaled_error"],
                      "passed": diff <= plan["acceptance_fixed_before_execution"]["reduced_refinement_max_scaled_error"],
                      "extra_ODE_calls": 0, "continuum_certificate": False}
    summary = {"utc": now(), "entries": entries, "refinement": refinement,
               "new_ODE_calls": sum(x["new_ODE_calls"] for x in entries),
               "old_completed_replays": 0, "NCP": 0, "benchmark": 0,
               "source": manifest, "HH_R10": "OFF", "production_admission": "NOT_ISSUED"}
    publish_json(output/"invocations"/(uuid.uuid4().hex+".json"), summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", default=str(ROOT/"results/reduced"))
    args = parser.parse_args()
    summary = run(args.output, args.execute)
    print(json.dumps(summary, indent=2))
    statuses = {e["status"] for e in summary["entries"]}
    if any(s == "FAILED" or s.startswith("BLOCKED") for s in statuses):
        raise SystemExit(1)
    if summary["refinement"] and not summary["refinement"]["passed"]:
        raise SystemExit(1)
