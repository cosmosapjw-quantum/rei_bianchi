#!/usr/bin/env python3
"""Add only the missing z=4 -> 2 tail of the immutable REI198 trajectories.

The owner retains its original x=ln(a/(1/21)), href, and eight state variables.
Its src.xmax records the old endpoint; this runner passes an explicit integration
interval to solve_ivp and never calls owner.initial() or owner.solve(). No old
z=20 -> 4 interval is integrated. Completed tails are hash-verified and skipped.

Run --preflight first. --run requires an explicit --max-new-cases. This is a
preliminary continuation, not production admission or a continuum certificate.
"""
from __future__ import annotations

import os
for _env in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_env] = "1"

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import fcntl
import hashlib
import importlib.util
import io
import json
import math
import multiprocessing
from pathlib import Path, PurePosixPath
import platform
import re
import sys
import time
import traceback
import uuid

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
DEFAULT_LOCK = RESEARCH / "hh_phys75_sector_memory_20261021/source/OWNER_LOCK.json"
RESOURCE_SOURCE = RESEARCH / "hh_phys74_rei_pilot_20261021/resources.py"
PREFIX = "repo_payload/research/rei_bianchi_sigma_pi_pilot_20261021/"
PINS = {
    "archive": "2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d",
    "owner_lock": "85991ae90de5041bb1ff967b3abaf426a4787874ba71a3b1290a111317acdd1c",
    "manifest": "3907bc7a228642443178af706e925aedf0e0b0c5e71843569befec552a6586d6",
    "terminal_index": "62f5d96fd323b1ed60c61f4b51e35ab80eb3498d2800c6c04addc1e5e2483115",
    "resources": "7e2902c015aaae0d7ebd496b2f3dc9c5476bb48aff7b5f6d57ad6652313da8a3",
}
EXPECTED_CASES = 1231
AREF = 1 / 21
TARGET_Z = 2.0
TARGET_X = math.log((1 / (1 + TARGET_Z)) / AREF)
TAIL_SAMPLES = 33
SOLVER = {"method": "DOP853", "rtol": 3e-11, "atol": 3e-13}
CUMULATIVE_WALL_LIMIT_S = 290.0  # 10 seconds below the requested 300 s bound.
CLEANUP_RESERVE_S = 5.0
SCOPE = "NEW_Z4_TO_Z2_TAIL_FROM_IMMUTABLE_REI198_ENDPOINT"
FRAME = "same comoving orthonormal normal frame; pi_hat=diag(-p,-p,2p)"
STATE_ORDER = ["tau=href*elapsed_proper_seconds", "b", "q=s/href", "E0", "E2", "E4", "E6", "E8"]
_MODEL = None
_MODEL_ROOT = None


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return sha_bytes(Path(path).read_bytes())


def read_checked(path, expected, label):
    data = Path(path).read_bytes()
    if sha_bytes(data) != expected:
        raise ValueError(f"{label}_SHA256_MISMATCH:{path}")
    return data


def dump_new(path, value):
    """Exclusive creation: neither completed evidence nor failures are replaced."""
    with Path(path).open("xb") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def safe_path(root, relative):
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise ValueError("UNSAFE_OWNER_PATH")
    root = Path(root).resolve()
    path = root.joinpath(*rel.parts)
    if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in [path, *path.parents] if p != root and root in p.parents):
        raise ValueError("SYMLINK_OWNER_PATH")
    return path


def f64_bytes(value):
    return np.asarray(value, dtype="<f8").tobytes(order="C")


def check_owner(owner, files):
    for rel, expected in files.items():
        read_checked(safe_path(owner, rel), expected, "OWNER_SOURCE")


def validate_case(owner, row, files, manifest):
    """Validate saved bytes and exact restart state; perform no ODE or moments."""
    cid = row["case_id"]
    if not re.fullmatch(r"[A-Za-z0-9_.+\-]+", cid) or cid in (".", ".."):
        raise ValueError("UNSAFE_CASE_ID")
    raw_path = safe_path(owner, row["npz_path"])
    receipt_rel = str(PurePosixPath(row["npz_path"]).with_suffix(".json"))
    for rel, expected in ((row["npz_path"], row["npz_sha256"]),
                          (receipt_rel, row["receipt_sha256"])):
        if manifest.get(rel, {}).get("sha256") != expected:
            raise ValueError("CASE_ARCHIVE_MANIFEST_MISMATCH:" + cid)
    raw = read_checked(raw_path, row["npz_sha256"], "RAW_HISTORY")
    receipt_bytes = read_checked(safe_path(owner, receipt_rel), row["receipt_sha256"], "RAW_RECEIPT")
    if len(raw) != manifest[row["npz_path"]]["size_bytes"] or len(receipt_bytes) != manifest[receipt_rel]["size_bytes"]:
        raise ValueError("CASE_ARCHIVE_SIZE_MISMATCH:" + cid)
    receipt = json.loads(receipt_bytes)
    if receipt["status"] != "COMPLETED" or receipt["case"]["id"] != cid or receipt["state_count"] != 8:
        raise ValueError("UNCOMPLETED_OR_WRONG_SAVED_CASE:" + cid)
    parent_files = {k: v for k, v in files.items() if k != "matter_radiation_20261021/component_pilot.py"}
    ident = receipt["identity"]
    if row["group"] == "radiation625":
        if ident["model_files"] != parent_files:
            raise ValueError("RADIATION_OWNER_IDENTITY_MISMATCH")
        amplitude = float(ident["configuration"]["massive_A"])
        if amplitude != 0.0 or row["lane"] != "RADIATION_SLICE":
            raise ValueError("RADIATION_SCOPE_MISMATCH")
    elif row["group"] == "matter600_mixed6":
        if ident["parent_immutable_files"] != parent_files or ident["new_model_sha256"] != files["matter_radiation_20261021/component_pilot.py"]:
            raise ValueError("COMPONENT_OWNER_IDENTITY_MISMATCH")
        amplitude = float(receipt["initial"]["A_m"])
        if receipt["case"]["lane"] != row["lane"]:
            raise ValueError("COMPONENT_LANE_MISMATCH")
    else:
        raise ValueError("WRONG_PHYSICAL_SCOPE")
    if f64_bytes(amplitude) != f64_bytes(row["initial_matter_A"]) or receipt["initial"] != row["initial"]:
        raise ValueError("MATTER_AMPLITUDE_OR_INITIAL_RECEIPT_MISMATCH")
    if not -1 <= amplitude <= 2:
        raise ValueError("MATTER_AMPLITUDE_POSITIVITY")
    with np.load(io.BytesIO(raw), allow_pickle=False) as history:
        state = history["state"]
        x = history["x"]
        z = history["zbar"]
        h = history["H_per_s"]
        if state.shape != (8, 65) or state.dtype != np.dtype("float64") or x.shape != (65,):
            raise ValueError("RAW_STATE_SHAPE_OR_DTYPE")
        if not all(np.isfinite(v).all() for v in (state, x, z, h)) or np.any(h <= 0) or np.any(state[3] <= 0):
            raise ValueError("INVALID_SAVED_STATE")
        if x[0] != 0 or np.any(np.diff(x) <= 0) or z[0] != 20 or z[-1] != 4:
            raise ValueError("NOT_IMMUTABLE_Z20_TO_Z4_HISTORY")
        if f64_bytes(state[:, -1]) != f64_bytes(row["terminal"]["state"]):
            raise ValueError("TERMINAL_STATE_BIT_IDENTITY_MISMATCH:" + cid)
        if f64_bytes(x[-1]) != f64_bytes(row["terminal"]["x"]) or f64_bytes(z[-1]) != f64_bytes(row["terminal"]["zbar"]):
            raise ValueError("TERMINAL_CLOCK_BIT_IDENTITY_MISMATCH:" + cid)
        if f64_bytes(h[-1]) != f64_bytes(row["terminal"]["H_per_s"]):
            raise ValueError("TERMINAL_H_BIT_IDENTITY_MISMATCH:" + cid)
        if not x[-1] < TARGET_X:
            raise ValueError("TAIL_INTERVAL_NOT_FORWARD")
        saved_diagnostics = {k: float(history[k][-1]) for k in history.files
                             if k != "state" and history[k].shape == (65,)}
    diagnostic_source = {"npz_path": row["npz_path"], "npz_sha256": row["npz_sha256"],
                         "kind": "RAW_COMPONENT_TRAJECTORY"}
    if row["group"] == "radiation625":
        rel = "matter_radiation_20261021/decomposition/cases/" + cid + ".npz"
        member = manifest.get(rel)
        if member is None:
            raise ValueError("MISSING_PINNED_RADIATION_COMPONENT_DIAGNOSTICS")
        data = read_checked(safe_path(owner, rel), member["sha256"], "SAVED_COMPONENT_DIAGNOSTICS")
        if len(data) != member["size_bytes"]:
            raise ValueError("SAVED_COMPONENT_DIAGNOSTIC_SIZE")
        with np.load(io.BytesIO(data), allow_pickle=False) as history:
            for key in history.files:
                value = history[key]
                if value.shape != (65,) or not np.isfinite(value).all():
                    raise ValueError("INVALID_SAVED_COMPONENT_DIAGNOSTIC")
                last = float(value[-1])
                if key in saved_diagnostics and f64_bytes(last) != f64_bytes(saved_diagnostics[key]):
                    raise ValueError("RAW_DECOMPOSITION_BOUNDARY_MISMATCH:" + key)
                saved_diagnostics[key] = last
        diagnostic_source = {"npz_path": rel, "npz_sha256": member["sha256"],
                             "kind": "IMMUTABLE_COMPONENT_DECOMPOSITION_OF_RAW_TRAJECTORY"}
    for key in ("signed_Pi_m", "signed_Pi_r"):
        if key in row["terminal"] and f64_bytes(saved_diagnostics[key]) != f64_bytes(row["terminal"][key]):
            raise ValueError("TERMINAL_COMPONENT_DIAGNOSTIC_MISMATCH:" + key)
    return {**row, "amplitude_from_receipt": amplitude, "saved_case": receipt["case"],
            "restart_diagnostics_source": diagnostic_source,
            "saved_restart_diagnostics": saved_diagnostics}


def preflight(owner_root, terminal_index, owner_lock=DEFAULT_LOCK):
    owner = Path(owner_root).resolve()
    lock = json.loads(read_checked(owner_lock, PINS["owner_lock"], "OWNER_LOCK"))
    if lock["upstream_archive_sha256"] != PINS["archive"]:
        raise ValueError("ARCHIVE_IDENTITY_MISMATCH")
    files = lock["files"]
    check_owner(owner, files)
    manifest_data = json.loads(read_checked(owner / "MATTER_RADIATION_PAYLOAD_MANIFEST.json", PINS["manifest"], "ARCHIVE_MANIFEST"))
    manifest = {}
    for entry in manifest_data["files"]:
        if not entry["path"].startswith(PREFIX):
            raise ValueError("ARCHIVE_MANIFEST_PREFIX")
        rel = entry["path"][len(PREFIX):]
        safe_path(owner, rel)
        if rel in manifest:
            raise ValueError("DUPLICATE_ARCHIVE_MEMBER")
        manifest[rel] = entry
    for rel, expected in files.items():
        if manifest.get(rel, {}).get("sha256") != expected:
            raise ValueError("OWNER_ARCHIVE_MANIFEST_MISMATCH")
    index = json.loads(read_checked(terminal_index, PINS["terminal_index"], "TERMINAL_INDEX"))
    if index["schema"] != "REI198_SAVED_TERMINAL_INDEX_V1" or index["archive_sha256"] != PINS["archive"] or index["state_order"] != STATE_ORDER:
        raise ValueError("TERMINAL_INDEX_SCHEMA_OR_SOURCE")
    if len(index["rows"]) != EXPECTED_CASES or len({r["case_id"] for r in index["rows"]}) != EXPECTED_CASES:
        raise ValueError("TERMINAL_CASE_COUNT_OR_DUPLICATE")
    rows = [validate_case(owner, row, files, manifest) for row in index["rows"]]
    resource_hash = sha(RESOURCE_SOURCE)
    if resource_hash != PINS["resources"]:
        raise ValueError("LEASEPOOL_SOURCE_MISMATCH")
    identity = {
        "schema": "PHYS76_NEW_TAIL_IDENTITY_V1", "scope": SCOPE,
        "archive_sha256": PINS["archive"], "owner_lock_sha256": PINS["owner_lock"],
        "manifest_sha256": PINS["manifest"], "terminal_index_sha256": PINS["terminal_index"],
        "owner_files": files, "runner_sha256": sha(__file__), "resources_sha256": resource_hash,
        "target_z": TARGET_Z, "target_x": TARGET_X, "a_ref_unchanged": AREF,
        "solver": SOLVER, "tail_samples_including_restart": TAIL_SAMPLES,
        "state_order": STATE_ORDER, "frame": FRAME,
        "norms": "half=sqrt(T_ab*T_ab/2); Frobenius=sqrt(2)*half; signed sector tensors summed before norm",
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
    }
    return {"owner_root": str(owner), "identity": identity, "rows": rows, "manifest": manifest,
            "summary": {"status": "PREFLIGHT_PASS_NO_ODE", "source_cases": len(rows),
                        "lane_counts": dict(Counter(r["lane"] for r in rows)),
                        "old_interval": [20, 4], "new_interval": [4, TARGET_Z],
                        "new_ODE_solves": 0, "identity_sha256": sha_bytes(canonical(identity))}}


def case_identity(bundle, row):
    return {"run_identity_sha256": sha_bytes(canonical(bundle["identity"])),
            "case_id": row["case_id"], "group": row["group"], "lane": row["lane"],
            "npz_sha256": row["npz_sha256"], "receipt_sha256": row["receipt_sha256"],
            "restart_diagnostics_source": row["restart_diagnostics_source"],
            "restart_state_sha256": sha_bytes(f64_bytes(row["terminal"]["state"])),
            "x_start": row["terminal"]["x"], "target_z": TARGET_Z, "target_x": TARGET_X,
            "amplitude_from_receipt": row["amplitude_from_receipt"],
            "solver": SOLVER, "tail_samples_including_restart": TAIL_SAMPLES}


def completed_receipt(case_dir, identity):
    case_dir = Path(case_dir)
    path = case_dir / "COMPLETED.json"
    if not path.exists():
        return None
    result = json.loads(path.read_text())
    if result.get("status") != "COMPLETED" or result.get("identity") != identity or result.get("identity_sha256") != sha_bytes(canonical(identity)):
        raise ValueError("COMPLETED_IDENTITY_MISMATCH:" + str(case_dir))
    read_checked(case_dir / "history.npz", result["history_sha256"], "COMPLETED_HISTORY")
    return result


def _load_owner(owner, files):
    global _MODEL, _MODEL_ROOT
    check_owner(owner, files)
    if _MODEL is not None:
        if _MODEL_ROOT != str(Path(owner).resolve()):
            raise ValueError("WORKER_OWNER_CHANGED")
        return _MODEL
    expected_modules = {"pilot": "pilot.py", "canonical_fv": "vendor/canonical_fv.py",
                        "lrs_boltzmann": "vendor/lrs_boltzmann.py", "species_hierarchy": "vendor/species_hierarchy.py"}
    for name, rel in expected_modules.items():
        if name in sys.modules and Path(sys.modules[name].__file__).resolve() != safe_path(owner, rel).resolve():
            raise ValueError("FOREIGN_OWNER_IMPORT:" + name)
    path = safe_path(owner, "matter_radiation_20261021/component_pilot.py")
    spec = importlib.util.spec_from_file_location("_phys76_pinned_component_owner", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, rel in expected_modules.items():
        if name in sys.modules and Path(sys.modules[name].__file__).resolve() != safe_path(owner, rel).resolve():
            raise ValueError("OWNER_IMPORT_PATH_MISMATCH:" + name)
    model = module.ComponentReduced()
    if model.src.aref != AREF or model.L != 8 or not math.isfinite(model.src.href) or model.src.href <= 0:
        raise ValueError("OWNER_CLOCK_OR_STATE_CONFIGURATION")
    _MODEL, _MODEL_ROOT = model, str(Path(owner).resolve())
    return model


def _load_resources():
    read_checked(RESOURCE_SOURCE, PINS["resources"], "LEASEPOOL_SOURCE")
    spec = importlib.util.spec_from_file_location("_phys76_hh74_resources", RESOURCE_SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_boundary_diagnostics(diagnostics, row):
    checked = 0
    for key, expected in row["saved_restart_diagnostics"].items():
        if key in diagnostics:
            if f64_bytes(np.asarray(diagnostics[key])[0]) != f64_bytes(expected):
                raise ArithmeticError("RESTART_DIAGNOSTIC_NOT_BIT_IDENTICAL:" + key)
            checked += 1
    if checked < 3:
        raise ArithmeticError("MISSING_RESTART_DIAGNOSTIC_COMPARISON")
    return {"status": "BIT_IDENTICAL_TO_SAVED_DIAGNOSTICS", "checked_fields": checked,
            "source": row["restart_diagnostics_source"], "recomputation_max_abs_difference": 0.0}


def execute_case(task, *, solver=None, model=None):
    """One create-only case. Keyword injection is for fake-solver unit tests only."""
    bundle, row = task["bundle"], task["row"]
    identity = case_identity(bundle, row)
    case_dir = Path(task["case_dir"])
    done = completed_receipt(case_dir, identity)
    if done is not None:
        return {**done, "dispatch_status": "SKIPPED_COMPLETED_NO_ODE"}
    case_dir.mkdir(parents=False, exist_ok=False)
    start, cpu_start = time.monotonic(), time.process_time()
    base = {"schema": "PHYS76_TAIL_CASE_RECEIPT_V1", "identity": identity,
            "identity_sha256": sha_bytes(canonical(identity)), "scope": SCOPE,
            "case": row["saved_case"], "new_tail_only": True, "old_trajectories_rerun": 0,
            "cost_snapshot_at_dispatch": task.get("cost_snapshot", {}),
            "HH_R10": "OFF", "production_admission": "NOT_ISSUED"}
    dump_new(case_dir / "STARTED.json", {**base, "status": "STARTED"})
    try:
        check_owner(bundle["owner_root"], bundle["identity"]["owner_files"])
        checked = validate_case(bundle["owner_root"], row, bundle["identity"]["owner_files"], bundle["manifest"])
        model = model if model is not None else _load_owner(bundle["owner_root"], bundle["identity"]["owner_files"])
        model.set_amplitude(checked["amplitude_from_receipt"])
        populations = np.asarray(model.momentum.cell_numbers)
        if not np.isfinite(populations).all() or np.any(populations < 0):
            raise ArithmeticError("NONFINITE_OR_NEGATIVE_MATTER_POPULATION")
        y0 = np.asarray(row["terminal"]["state"], dtype=np.float64).copy()
        x_start = float(row["terminal"]["x"])
        samples = np.linspace(x_start, TARGET_X, TAIL_SAMPLES)
        if f64_bytes(y0) != f64_bytes(row["terminal"]["state"]):
            raise ValueError("RESTART_COPY_BIT_IDENTITY")
        # Match the saved/tail batch diagnostic arithmetic. A one-column GEMV
        # can differ from GEMM by one ulp in sampled brightness; no time advances.
        restart_x = np.full(TAIL_SAMPLES, x_start)
        restart_state = np.repeat(y0[:, None], TAIL_SAMPLES, axis=1)
        boundary_before = check_boundary_diagnostics(model.diagnostics(restart_x, restart_state), checked)
        deadline = task["deadline_monotonic"]

        def rhs(x, y):
            if time.monotonic() >= deadline:
                raise TimeoutError("CUMULATIVE_WALL_DEADLINE_OWN_CASE_ONLY")
            if np.asarray(y).shape != (8,) or not np.isfinite(y).all() or y[3] <= 0 or abs(y[1]) > 1:
                raise ArithmeticError("INVALID_RHS_STATE")
            derivative = model.rhs(x, y)  # Pinned original eight-state equations.
            if not np.isfinite(derivative).all() or derivative[0] <= 0:
                raise ArithmeticError("NONFINITE_RHS_OR_NONPOSITIVE_H")
            return derivative

        if solver is None:
            from scipy.integrate import solve_ivp
            solver = solve_ivp
        solve_start = time.monotonic()
        solution = solver(rhs, (x_start, TARGET_X), y0, t_eval=samples, **SOLVER)
        solve_wall = time.monotonic() - solve_start
        if not solution.success:
            raise ArithmeticError("SOLVER_FAILED:" + str(solution.message))
        state, x = np.asarray(solution.y), np.asarray(solution.t)
        if state.shape != (8, TAIL_SAMPLES) or x.shape != (TAIL_SAMPLES,) or not np.isfinite(state).all() or not np.array_equal(x, samples):
            raise ArithmeticError("TAIL_SHAPE_FINITE_OR_SAMPLE_GRID")
        if f64_bytes(state[:, 0]) != f64_bytes(row["terminal"]["state"]) or f64_bytes(x[0]) != f64_bytes(x_start):
            raise ArithmeticError("RESTART_STATE_OR_CLOCK_NOT_BIT_IDENTICAL")
        d = model.diagnostics(x, state)
        boundary_after = check_boundary_diagnostics(d, checked)
        if not all(np.isfinite(v).all() for v in d.values()) or np.any(d["H_per_s"] <= 0) or np.any(state[3] <= 0):
            raise ArithmeticError("NONFINITE_OR_NONPOSITIVE_TAIL")
        if np.any(d["sampled_min_angular_brightness"] < 0):
            raise ArithmeticError("NEGATIVE_SAMPLED_RADIATION_BRIGHTNESS")
        if abs(float(d["zbar"][-1]) - TARGET_Z) > 2e-14:
            raise ArithmeticError("TARGET_REDSHIFT_NOT_REACHED")
        if not np.array_equal(d["signed_Pi_total"], d["signed_Pi_m"] + d["signed_Pi_r"]):
            raise ArithmeticError("SIGNED_SECTOR_SUM_MISMATCH")
        # Preserve signed tensors. Only then take the half-contraction or full norm.
        d["p_total_J_m3"] = d["p_m_J_m3"] + d["p_r_J_m3"]
        for sector in ("m", "r", "total"):
            p = d[f"p_{sector}_J_m3"]
            for component, factor in (("11", -1), ("22", -1), ("33", 2)):
                d[f"pi_{sector}_{component}_J_m3"] = factor * p
            d[f"Pi_{sector}_half"] = np.abs(d[f"signed_Pi_{sector}"])
            d[f"Pi_{sector}_frobenius"] = math.sqrt(2) * d[f"Pi_{sector}_half"]
        d["signed_Sigma_half"] = math.sqrt(3) * d["s_over_H"]
        d["Sigma_half"] = d["Sigma"].copy()
        d["Sigma_frobenius"] = math.sqrt(2) * d["Sigma_half"]
        check_owner(bundle["owner_root"], bundle["identity"]["owner_files"])
        evidence = {**base, "frame": FRAME, "state_order": STATE_ORDER,
                    "scope_note": "33 new-tail samples include the saved z4 restart; concatenate old[:, :-1] plus tail, or old plus tail[:, 1:]",
                    "normalization": bundle["identity"]["norms"],
                    "sampled_positivity_is_not_continuum_certificate": True,
                    "restart_boundary_before_solver": boundary_before, "restart_boundary_after_solver": boundary_after,
                    "original_src_xmax_unchanged": float(model.src.xmax),
                    "global_aref_unchanged": float(model.src.aref), "global_href_unchanged": float(model.src.href),
                    "solve_wall_s": solve_wall, "case_cpu_s_to_serialization": time.process_time() - cpu_start,
                    "min_matter_cell_population": float(populations.min()),
                    "minimum_sampled_angular_brightness": float(np.min(d["sampled_min_angular_brightness"]))}
        with (case_dir / "history.npz").open("xb") as stream:
            np.savez_compressed(stream, state=state, **d, scope=np.array(SCOPE),
                                identity_sha256=np.array(base["identity_sha256"]),
                                provenance_json=np.array(canonical(evidence).decode()))
            stream.flush()
            os.fsync(stream.fileno())
        result = {**evidence, "status": "COMPLETED", "history_sha256": sha(case_dir / "history.npz"),
                  "nfev": int(solution.nfev), "new_ODE_solves": 1,
                  "case_wall_s": time.monotonic() - start, "case_cpu_s": time.process_time() - cpu_start,
                  "endpoint": {k: float(np.asarray(v)[-1]) for k, v in d.items()}}
        dump_new(case_dir / "COMPLETED.json", result)
        return result
    except BaseException as exc:
        failure = {**base, "status": "FAILED_PRESERVED_NO_AUTOMATIC_RETRY", "error_type": type(exc).__name__,
                   "error": str(exc), "traceback": traceback.format_exc(),
                   "case_wall_s": time.monotonic() - start, "case_cpu_s": time.process_time() - cpu_start,
                   "new_ODE_solves": int("solve_start" in locals())}
        dump_new(case_dir / "FAILED.json", failure)
        return failure


def _costs(output):
    """An interrupted invocation consumes its reservation; never silently resets."""
    wall = 0.0
    for start_path in sorted((output / "invocations").glob("*/STARTED.json")):
        start = json.loads(start_path.read_text())
        final = start_path.with_name("FINISHED.json")
        if final.exists():
            value = json.loads(final.read_text())["invocation_wall_s"]
        else:
            value = start["wall_reservation_s"]
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError("INVALID_CUMULATIVE_WALL_LEDGER")
        wall += value
    rows = [json.loads(p.read_text()) for name in ("COMPLETED.json", "FAILED.json") for p in (output / "cases").glob("*/" + name)]
    return {"run_wall_s": wall, "case_wall_s": sum(r["case_wall_s"] for r in rows),
            "case_cpu_s": sum(r["case_cpu_s"] for r in rows),
            "new_ODE_solves": sum(r["new_ODE_solves"] for r in rows)}


def schedule(bundle, output, *, max_new_cases, max_workers=2, site="local", case_ids=None,
             lease_dir="/tmp/rei-bianchi-cooperative-leases", invocation_start=None, pool=None):
    if site not in ("local", "ncp") or not 1 <= max_workers <= (2 if site == "local" else 64):
        raise ValueError("SITE_WORKER_CAP")
    if not 0 <= max_new_cases <= EXPECTED_CASES:
        raise ValueError("MAX_NEW_CASES_CAP")
    start = time.monotonic() if invocation_start is None else invocation_start
    output = Path(output).resolve()
    if output == Path(bundle["owner_root"]) or output.is_relative_to(Path(bundle["owner_root"])):
        raise ValueError("OUTPUT_INSIDE_IMMUTABLE_OWNER")
    output.mkdir(parents=True, exist_ok=True)
    for name in ("cases", "invocations", "checkpoints"):
        (output / name).mkdir(exist_ok=True)
    with (output / "scheduler.lock").open("a+") as lock_stream:
        try:
            fcntl.flock(lock_stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            pending = {"status": "PENDING_SAME_OUTPUT_SCHEDULER_ACTIVE", "new_ODE_solves": 0}
            dump_new(output / "checkpoints" / (uuid.uuid4().hex + ".json"), pending)
            return pending
        identity_path = output / "run_identity.json"
        if identity_path.exists():
            if json.loads(identity_path.read_text()) != bundle["identity"]:
                raise ValueError("RUN_IDENTITY_MISMATCH")
        else:
            dump_new(identity_path, bundle["identity"])
        if case_ids is not None and set(case_ids) - {r["case_id"] for r in bundle["rows"]}:
            raise ValueError("UNKNOWN_SELECTED_CASE")
        selected = [r for r in bundle["rows"] if case_ids is None or r["case_id"] in case_ids]
        pending, completed, blocked = [], [], []
        for row in selected:
            path = output / "cases" / row["case_id"]
            done = completed_receipt(path, case_identity(bundle, row))
            if done is not None:
                completed.append(row["case_id"])
            elif path.exists():
                blocked.append(row["case_id"])
            else:
                pending.append(row)
        prior = _costs(output)
        reserve = max(0.0, CUMULATIVE_WALL_LIMIT_S - prior["run_wall_s"])
        invocation_dir = output / "invocations" / uuid.uuid4().hex
        invocation_dir.mkdir()
        dump_new(invocation_dir / "STARTED.json", {"status": "STARTED", "wall_reservation_s": reserve,
                 "prior_costs": prior, "site": site, "max_workers": max_workers,
                 "max_new_cases": max_new_cases, "selected_case_count": len(selected),
                 "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        result = {"scope": SCOPE, "status": "PENDING", "completed_skipped_no_ODE": completed,
                  "failed_or_interrupted_preserved": blocked, "new_results": [], "resource_observations": [],
                  "HH_R10": "OFF", "production_admission": "NOT_ISSUED"}
        deadline = start + reserve - CLEANUP_RESERVE_S
        dispatched = 0
        active = {}
        resources = _load_resources()
        workers = min(max_workers, resources.cpu_limit())
        pool = pool if pool is not None else resources.LeasePool(
            lease_dir, max_cpus=workers, memory_gib=128., reserve_gib=2. if site == "local" else 16., job_gib=.25)
        # acquire() uses capacity (not cap). Bound the instance's allocation to
        # 64 even on a larger host; the shared source stays unchanged. The separate
        # worker ceiling remains 2 locally or <=64 on NCP. No peers are signalled.
        if hasattr(pool, "capacity"):
            pool.capacity = min(pool.capacity, 64)
        try:
            if reserve <= CLEANUP_RESERVE_S or time.monotonic() >= deadline:
                result["deferral"] = "CUMULATIVE_WALL_BUDGET_EXHAUSTED"
            elif max_new_cases == 0:
                result["deferral"] = "ZERO_NEW_CASE_ADMISSION"
            elif pending:
                with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn")) as executor:
                    while (pending and dispatched < max_new_cases) or active:
                        while pending and dispatched < max_new_cases and len(active) < workers and time.monotonic() < deadline:
                            row = pending[0]
                            key, observation = pool.acquire("PHYS76_NEW_TAIL:" + row["case_id"])
                            result["resource_observations"].append(observation)
                            if key is None:
                                result["deferral"] = "PENDING_RESOURCE_SHARE_NO_FOREIGN_JOB_STOP"
                                break
                            # Send only this case's two manifest rows, not all 1231
                            # trajectories/5747 archive entries, through process IPC.
                            receipt_rel = str(PurePosixPath(row["npz_path"]).with_suffix(".json"))
                            case_bundle = {"owner_root": bundle["owner_root"], "identity": bundle["identity"],
                                           "manifest": {rel: bundle["manifest"][rel] for rel in (row["npz_path"], receipt_rel, row["restart_diagnostics_source"]["npz_path"])}}
                            task = {"bundle": case_bundle, "row": row, "case_dir": str(output / "cases" / row["case_id"]),
                                    "deadline_monotonic": deadline,
                                    "cost_snapshot": {"committed_prior_run_wall_s": prior["run_wall_s"],
                                                      "run_wall_s_at_dispatch": prior["run_wall_s"] + time.monotonic() - start,
                                                      "finished_case_cpu_s_at_dispatch": prior["case_cpu_s"] + sum(r.get("case_cpu_s", 0) for r in result["new_results"]),
                                                      "concurrent_unfinished_cases_excluded": len(active)}}
                            try:
                                future = executor.submit(execute_case, task)
                            except BaseException:
                                pool.release(key)
                                raise
                            active[future] = (key, row["case_id"])
                            pending.pop(0)
                            dispatched += 1
                        if not active:
                            break
                        done, _ = wait(active, timeout=.5, return_when=FIRST_COMPLETED)
                        for future in done:
                            key, cid = active.pop(future)
                            try:
                                case_result = future.result()
                                result["new_results"].append({k: case_result[k] for k in ("status", "identity", "case_wall_s", "case_cpu_s", "new_ODE_solves")})
                            except BaseException as exc:
                                result["new_results"].append({"status": "WORKER_FAILURE_PRESERVED", "case_id": cid, "error": repr(exc)})
                            finally:
                                pool.release(key)
        finally:
            for key, _ in active.values():
                pool.release(key)
            result["invocation_wall_s"] = time.monotonic() - start
            result["new_cases_dispatched"] = dispatched
            result["pending_selected_cases"] = [r["case_id"] for r in pending]
            result["cumulative_costs"] = {"run_wall_s": prior["run_wall_s"] + result["invocation_wall_s"],
                "case_cpu_s": prior["case_cpu_s"] + sum(r.get("case_cpu_s", 0) for r in result["new_results"]),
                "case_wall_s": prior["case_wall_s"] + sum(r.get("case_wall_s", 0) for r in result["new_results"]),
                "new_ODE_solves": prior["new_ODE_solves"] + sum(r.get("new_ODE_solves", 0) for r in result["new_results"])}
            success = sum(r["status"] == "COMPLETED" for r in result["new_results"])
            if not pending and not blocked and len(completed) + success == len(selected):
                result["status"] = "COMPLETE_SELECTED_PRELIMINARY_TAILS"
            elif any(r["status"] != "COMPLETED" for r in result["new_results"]) or blocked:
                result["status"] = "PARTIAL_FAILURE_PRESERVED"
            else:
                result["status"] = "PENDING_CHECKPOINT"
            result["costs_are_execution_accounting_not_benchmark"] = True
            dump_new(invocation_dir / "FINISHED.json", result)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--preflight", action="store_true")
    action.add_argument("--run", action="store_true")
    parser.add_argument("--owner-root", type=Path, required=True)
    parser.add_argument("--terminal-index", type=Path, required=True)
    parser.add_argument("--owner-lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-new-cases", type=int)
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument("--site", choices=("local", "ncp"), default="local")
    parser.add_argument("--case-id", action="append")
    parser.add_argument("--lease-dir", default="/tmp/rei-bianchi-cooperative-leases")
    args = parser.parse_args()
    start = time.monotonic()
    bundle = preflight(args.owner_root, args.terminal_index, args.owner_lock)
    if args.preflight:
        print(json.dumps({**bundle["summary"], "identity": bundle["identity"]}, indent=2, sort_keys=True))
        return 0
    if args.output is None or args.max_new_cases is None:
        parser.error("--run requires --output and explicit --max-new-cases")
    result = schedule(bundle, args.output, max_new_cases=args.max_new_cases,
                      max_workers=args.max_workers, site=args.site, case_ids=args.case_id,
                      lease_dir=args.lease_dir, invocation_start=start)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["status"] == "PARTIAL_FAILURE_PRESERVED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
