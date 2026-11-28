#!/usr/bin/env python3
"""Read-only time-resolved attribution of REI198 saved collisionless histories.

Old z=20..4 and optional z=4..2 continuation grids are integrated separately.
Their concatenation is a display coordinate only.  This program does not import
an ODE solver, launch an NCP job, or substitute the short warm REI213 trajectories.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath

import numpy as np

from cumulative_memory import cumulative_memory_budget


FIELDS = ("H_per_s", "S_h", "P_m_h", "P_r_h")
LANES = (
    ("radiation_slice", "matter_radiation_20261021/decomposition/cases"),
    ("new_matter_and_mixed", "matter_radiation_20261021/results/new_sweep/cases"),
)
SCOPE = ("Non-tilted LRS Bianchi I; REI198 collisionless finite-owner closure; "
         "625 original radiation cases and 606 matter/mixed cases. "
         "REI213 warm histories and HH74 controls are separate datasets.")
MEMORY_FIELDS = ("initial_memory", "matter_memory", "radiation_memory",
                 "predicted_signed_shear", "closure_defect")
TAIL_SCOPE = "NEW_Z4_TO_Z2_TAIL_FROM_IMMUTABLE_REI198_ENDPOINT"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value):
    """Match the runner's JSON identity encoding, independently of whitespace."""
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def _source_path(root, relative):
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise ValueError("UNSAFE_SOURCE_PATH")
    root = Path(root).resolve()
    path = root.joinpath(*rel.parts)
    if not path.resolve().is_relative_to(root):
        raise ValueError("SOURCE_PATH_OUTSIDE_ROOT")
    return path


def _json(path, content):
    with Path(path).open("x") as stream:
        json.dump(content, stream, indent=2, allow_nan=False)
        stream.write("\n")


def _csv(path, rows):
    if not rows:
        raise ValueError("NONEMPTY_CSV_ROWS_REQUIRED")
    with Path(path).open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _read_columns(path):
    with np.load(path, allow_pickle=False) as archive:
        names = ("x", "zbar", "H_per_s", "s_over_H", "signed_Pi_m", "signed_Pi_r")
        if any(name not in archive for name in names):
            raise ValueError("SAVED_COLUMN_MAPPING_MISSING:" + str(path))
        raw = {name: np.asarray(archive[name]).copy() for name in names}
    if any(np.iscomplexobj(value) for value in raw.values()):
        raise ValueError("REAL_SAVED_COLUMNS_REQUIRED")
    if raw["x"].ndim != 1 or any(value.shape != raw["x"].shape for value in raw.values()):
        raise ValueError("ONE_DIMENSIONAL_SAVED_COLUMNS_REQUIRED")
    if any(not np.isfinite(value).all() for value in raw.values()):
        raise ValueError("FINITE_SAVED_COLUMNS_REQUIRED")
    x, z = raw["x"], raw["zbar"]
    if not np.allclose(z, 21.0 * np.exp(-x) - 1.0, rtol=2e-13, atol=2e-13):
        raise ValueError("REI198_REDSHIFT_COORDINATE_MISMATCH")
    values = np.stack((raw["H_per_s"], np.sqrt(3.0) * raw["s_over_H"],
                       raw["signed_Pi_m"], raw["signed_Pi_r"]))
    return x, z, values


def load_old(root, expected_counts=(625, 606)):
    """Read exactly the two source-bound lanes, preserving IDs and metadata."""
    root = Path(root)
    records, arrays = [], []
    shared_x = shared_z = None
    seen = set()
    for lane_index, (lane, relative) in enumerate(LANES):
        case_dir = root / relative
        files = sorted(case_dir.glob("*.npz"))
        if len(files) != expected_counts[lane_index]:
            raise ValueError("OLD_LANE_CASE_COUNT_MISMATCH:" + lane)
        metadata_path = case_dir.parent / "endpoints.csv"
        metadata_hash = sha256(metadata_path)
        with metadata_path.open() as stream:
            rows = list(csv.DictReader(stream))
        metadata = {}
        for row in rows:
            cid = row.get("case_id") or row.get("id")
            if not cid or cid in metadata:
                raise ValueError("OLD_METADATA_CASE_ID_MISSING_OR_DUPLICATE")
            if row.get("case_id") and row.get("id") and row["case_id"] != row["id"]:
                raise ValueError("OLD_METADATA_ID_CONFLICT")
            metadata[cid] = row
        for path in files:
            cid = path.stem
            if cid in seen or cid not in metadata:
                raise ValueError("OLD_CASE_ID_DUPLICATE_OR_METADATA_MISSING:" + cid)
            seen.add(cid)
            x, z, values = _read_columns(path)
            if shared_x is None:
                shared_x, shared_z = x, z
            if not np.array_equal(shared_x, x) or not np.array_equal(shared_z, z):
                raise ValueError("OLD_SHARED_GRID_MISMATCH")
            record = {"case_id": cid, "source_lane": lane,
                      "source_path": str(path.relative_to(root)),
                      "source_sha256": sha256(path), "metadata": metadata[cid],
                      "metadata_csv_sha256": metadata_hash}
            sidecar = path.with_suffix(".json")
            if sidecar.exists():
                record["source_sidecar_sha256"] = sha256(sidecar)
                content = json.loads(sidecar.read_text())
                record["source_case"] = content.get("case", {})
                record["source_identity"] = content.get("identity", {})
            records.append(record)
            arrays.append(values)
    if not np.isclose(shared_z[0], 20.0, rtol=0, atol=2e-12) or not np.isclose(shared_z[-1], 4.0, rtol=0, atol=2e-12):
        raise ValueError("OLD_SOURCE_MUST_COVER_Z20_TO4")
    return shared_x, shared_z, np.stack(arrays), records


def validate_tail_identity(sidecar, old_record):
    """Require explicit case/old-input binding, never infer a filename match."""
    if not isinstance(sidecar, dict) or sidecar.get("status") != "COMPLETED":
        raise ValueError("COMPLETED_TAIL_RECEIPT_REQUIRED")
    for name, expected in (("case_id", old_record["case_id"]),
                           ("old_source_sha256", old_record["source_sha256"]),
                           ("source_lane", old_record["source_lane"])):
        if sidecar.get(name) != expected:
            raise ValueError("TAIL_IDENTITY_MISMATCH:" + name)
    if not isinstance(sidecar.get("identity"), dict) or not sidecar["identity"]:
        raise ValueError("TAIL_RUNNER_MODEL_IDENTITY_REQUIRED")


def _native_run_context(root, old_root):
    path = root / "run_identity.json"
    run = json.loads(path.read_text())
    required = {"schema": "PHYS76_NEW_TAIL_IDENTITY_V1", "scope": TAIL_SCOPE,
                "target_z": 2.0, "tail_samples_including_restart": 33,
                "HH_R10": "OFF", "production_admission": "NOT_ISSUED"}
    if any(run.get(key) != expected for key, expected in required.items()):
        raise ValueError("NATIVE_RUN_SCOPE_MISMATCH")
    if run.get("target_x") != float(np.log(7.0)):
        raise ValueError("NATIVE_RUN_TARGET_COORDINATE_MISMATCH")
    if run.get("runner_sha256") != sha256(Path(__file__).with_name("continue_saved.py")):
        raise ValueError("NATIVE_RUNNER_SOURCE_HASH_MISMATCH")
    if not isinstance(run.get("owner_files"), dict) or not run["owner_files"]:
        raise ValueError("NATIVE_OWNER_SOURCE_IDENTITY_REQUIRED")
    for relative, expected in run["owner_files"].items():
        if sha256(_source_path(old_root, relative)) != expected:
            raise ValueError("NATIVE_OWNER_SOURCE_HASH_MISMATCH:" + relative)
    return {"identity": run, "identity_sha256": canonical_sha256(run),
            "file_sha256": sha256(path)}


def _validate_native_tail(path, receipt, old_record, run_context, old_root):
    """Bind native output directly to both old diagnostics and restart state.

    The radiation decomposition NPZ is the signed-stress source, whereas its
    full restart state lives in results/pilot.  These hashes are intentionally
    distinct.  Matter/mixed diagnostics and restart state share one raw NPZ.
    """
    cid = old_record["case_id"]
    run = run_context["identity"]
    identity = receipt.get("identity")
    if (receipt.get("schema") != "PHYS76_TAIL_CASE_RECEIPT_V1"
            or receipt.get("status") != "COMPLETED" or not isinstance(identity, dict)):
        raise ValueError("COMPLETED_NATIVE_TAIL_RECEIPT_REQUIRED")
    identity_hash = canonical_sha256(identity)
    if receipt.get("identity_sha256") != identity_hash:
        raise ValueError("NATIVE_CASE_IDENTITY_HASH_MISMATCH")
    if identity.get("run_identity_sha256") != run_context["identity_sha256"]:
        raise ValueError("NATIVE_RUN_IDENTITY_HASH_MISMATCH")
    if identity.get("case_id") != cid or receipt.get("case", {}).get("id") != cid:
        raise ValueError("NATIVE_CASE_ID_MISMATCH")
    if (receipt.get("scope") != TAIL_SCOPE or receipt.get("new_tail_only") is not True
            or receipt.get("old_trajectories_rerun") != 0
            or receipt.get("HH_R10") != "OFF"
            or receipt.get("production_admission") != "NOT_ISSUED"):
        raise ValueError("NATIVE_CASE_SCOPE_MISMATCH")
    for key in ("target_z", "target_x", "solver", "tail_samples_including_restart"):
        if identity.get(key) != run.get(key):
            raise ValueError("NATIVE_CASE_RUN_CONFIGURATION_MISMATCH:" + key)
    if old_record["source_lane"] == "radiation_slice":
        group, lane = "radiation625", "RADIATION_SLICE"
        raw_relative = "results/pilot/cases/" + cid + ".npz"
        kind = "IMMUTABLE_COMPONENT_DECOMPOSITION_OF_RAW_TRAJECTORY"
    elif old_record["source_lane"] == "new_matter_and_mixed":
        group, lane = "matter600_mixed6", old_record["metadata"].get("lane")
        if lane not in ("MATTER_SLICE", "MIXED_CANCELLATION"):
            raise ValueError("NATIVE_COMPONENT_METADATA_LANE_MISMATCH")
        raw_relative = old_record["source_path"]
        kind = "RAW_COMPONENT_TRAJECTORY"
    else:
        raise ValueError("NATIVE_UNKNOWN_OLD_SOURCE_LANE")
    if identity.get("group") != group or identity.get("lane") != lane:
        raise ValueError("NATIVE_CASE_PHYSICAL_LANE_MISMATCH")
    diagnostic_source = {"npz_path": old_record["source_path"],
                         "npz_sha256": old_record["source_sha256"], "kind": kind}
    if identity.get("restart_diagnostics_source") != diagnostic_source:
        raise ValueError("NATIVE_RESTART_DIAGNOSTIC_IDENTITY_MISMATCH")
    for name in ("restart_boundary_before_solver", "restart_boundary_after_solver"):
        boundary = receipt.get(name, {})
        if (boundary.get("status") != "BIT_IDENTICAL_TO_SAVED_DIAGNOSTICS"
                or boundary.get("source") != diagnostic_source
                or boundary.get("recomputation_max_abs_difference") != 0.0
                or boundary.get("checked_fields", 0) < 3):
            raise ValueError("NATIVE_RESTART_BOUNDARY_RECEIPT_MISMATCH:" + name)
    raw_path = _source_path(old_root, raw_relative)
    raw_receipt_path = raw_path.with_suffix(".json")
    raw_hash, raw_receipt_hash = sha256(raw_path), sha256(raw_receipt_path)
    if identity.get("npz_sha256") != raw_hash or identity.get("receipt_sha256") != raw_receipt_hash:
        raise ValueError("NATIVE_ORIGINAL_RAW_RESTART_HASH_MISMATCH")
    raw_receipt = json.loads(raw_receipt_path.read_text())
    if raw_receipt.get("status") != "COMPLETED" or raw_receipt.get("case", {}).get("id") != cid:
        raise ValueError("NATIVE_ORIGINAL_RAW_RECEIPT_CASE_MISMATCH")
    with np.load(raw_path, allow_pickle=False) as saved:
        state = np.asarray(saved["state"])
        old_x = np.asarray(saved["x"])
        if (state.shape != (8, len(old_x)) or state.dtype != np.dtype("float64")
                or not np.isfinite(state).all() or identity.get("x_start") != float(old_x[-1])):
            raise ValueError("NATIVE_ORIGINAL_RESTART_STATE_INVALID")
        restart_hash = hashlib.sha256(np.asarray(state[:, -1], dtype="<f8").tobytes(order="C")).hexdigest()
    if identity.get("restart_state_sha256") != restart_hash:
        raise ValueError("NATIVE_ORIGINAL_RESTART_STATE_HASH_MISMATCH")
    file_hash = sha256(path)
    if receipt.get("history_sha256") != file_hash:
        raise ValueError("NATIVE_HISTORY_HASH_MISMATCH")
    with np.load(path, allow_pickle=False) as tail:
        if ("identity_sha256" not in tail or tail["identity_sha256"].shape != ()
                or str(tail["identity_sha256"].item()) != identity_hash):
            raise ValueError("NATIVE_EMBEDDED_IDENTITY_HASH_MISMATCH")
        if "scope" not in tail or tail["scope"].shape != () or str(tail["scope"].item()) != TAIL_SCOPE:
            raise ValueError("NATIVE_EMBEDDED_SCOPE_MISMATCH")
        tail_state = np.asarray(tail["state"])
        if (tail_state.shape != (8, run["tail_samples_including_restart"])
                or tail_state.dtype != np.dtype("float64") or not np.isfinite(tail_state).all()):
            raise ValueError("NATIVE_TAIL_STATE_SHAPE_OR_DTYPE_MISMATCH")
        tail_restart_hash = hashlib.sha256(np.asarray(tail_state[:, 0], dtype="<f8").tobytes(order="C")).hexdigest()
        if tail_restart_hash != restart_hash:
            raise ValueError("NATIVE_TAIL_RESTART_STATE_HASH_MISMATCH")
        if (tail["x"].shape != (run["tail_samples_including_restart"],)
                or float(tail["x"][0]) != identity["x_start"]
                or float(tail["x"][-1]) != identity["target_x"]):
            raise ValueError("NATIVE_TAIL_CLOCK_OR_SAMPLES_MISMATCH")
    return {"history_sha256": file_hash, "case_identity_sha256": identity_hash,
            "run_identity_sha256": run_context["identity_sha256"],
            "run_identity_file_sha256": run_context["file_sha256"],
            "runner_sha256": run["runner_sha256"],
            "original_raw_restart": {"npz_path": raw_relative, "npz_sha256": raw_hash,
                                     "receipt_sha256": raw_receipt_hash,
                                     "restart_state_sha256": restart_hash},
            "restart_diagnostics_source": diagnostic_source}


def load_tail(root, old_records, old_root=None):
    """Read native runner output; retain a flat layout for manufactured tests.

    Native and flat layouts cannot be mixed.  Native histories are read in
    place, with no format-converting copy and no solver/model import.
    """
    root = Path(root)
    case_dir = root / "cases"
    native = (root / "run_identity.json").exists()
    if native and old_root is None:
        raise ValueError("NATIVE_OLD_ROOT_REQUIRED_FOR_RESTART_VERIFICATION")
    run_context = _native_run_context(root, old_root) if native else None
    expected = {record["case_id"] for record in old_records}
    flat = {path.stem for path in case_dir.glob("*.npz")}
    nested = {path.name for path in case_dir.iterdir() if path.is_dir()}
    if (native and flat) or (not native and nested):
        raise ValueError("MIXED_OR_UNBOUND_TAIL_LAYOUT")
    present = nested if native else flat
    if present != expected:
        raise ValueError("TAIL_CASE_COVERAGE_MISMATCH:missing=" + str(len(expected - present))
                         + ":extra=" + str(len(present - expected)))
    arrays, receipts = [], []
    shared_x = shared_z = None
    for record in old_records:
        path = (case_dir / record["case_id"] / "history.npz" if native
                else case_dir / (record["case_id"] + ".npz"))
        sidecar_path = path.with_name("COMPLETED.json") if native else path.with_suffix(".json")
        receipt = json.loads(sidecar_path.read_text())
        binding = {}
        if native:
            binding = _validate_native_tail(path, receipt, record, run_context, old_root)
            file_hash = binding["history_sha256"]
        else:
            validate_tail_identity(receipt, record)
            file_hash = sha256(path)
            if receipt.get("npz_sha256") != file_hash:
                raise ValueError("TAIL_NPZ_HASH_MISMATCH:" + record["case_id"])
        x, z, values = _read_columns(path)
        if shared_x is None:
            shared_x, shared_z = x, z
        if not np.array_equal(shared_x, x) or not np.array_equal(shared_z, z):
            raise ValueError("TAIL_SHARED_GRID_MISMATCH")
        arrays.append(values)
        receipts.append({"case_id": record["case_id"],
                         "layout": "native_runner" if native else "flat_manufactured",
                         "source_path": str(path.relative_to(root)),
                         "source_sha256": file_hash,
                         "receipt_sha256": sha256(sidecar_path), "receipt": receipt,
                         "native_binding": binding})
    if native:
        # One shared copy preserves the entire source/model/runtime identity.
        receipts[0]["run_identity"] = run_context["identity"]
    if not np.isclose(shared_z[0], 4.0, rtol=0, atol=2e-12) or not np.isclose(shared_z[-1], 2.0, rtol=0, atol=2e-12):
        raise ValueError("TAIL_SOURCE_MUST_COVER_Z4_TO2")
    return shared_x, shared_z, np.stack(arrays), receipts


def stitch_segments(old_x, old_values, tail_x=None, tail_values=None):
    """Compose two *separately uniform* sampled quadratures at a shared node.

    Values have shape (cases,4,time), ordered H,S,P_m,P_r.  Boundary data must
    be exactly equal numeric values; an inconsistent continuation is not
    silently repaired.  Return display coordinates, merged values, global
    memory, and a separate tail residual budget.  No uniform quadrature is
    applied to the concatenated display grid.
    """
    old_values = np.asarray(old_values)
    if old_values.ndim != 3 or old_values.shape[1] != 4:
        raise ValueError("CASE_FOUR_FIELD_TIME_SHAPE_REQUIRED")
    old = cumulative_memory_budget(old_x, *[old_values[:, k] for k in range(4)])
    if tail_x is None and tail_values is None:
        return np.asarray(old_x).copy(), old_values.copy(), old, None
    if tail_x is None or tail_values is None:
        raise ValueError("BOTH_TAIL_COORDINATE_AND_VALUES_REQUIRED")
    tail_values = np.asarray(tail_values)
    if (tail_values.ndim != 3 or tail_values.shape[:2] != old_values.shape[:2]
            or np.asarray(tail_x).ndim != 1):
        raise ValueError("TAIL_CASE_FIELD_SHAPE_MISMATCH")
    if float(old_x[-1]) != float(tail_x[0]):
        raise ValueError("TAIL_COORDINATE_BOUNDARY_MISMATCH")
    if not np.array_equal(old_values[:, :, -1], tail_values[:, :, 0]):
        raise ValueError("TAIL_OBSERVED_BOUNDARY_MISMATCH")
    local = cumulative_memory_budget(tail_x, *[tail_values[:, k] for k in range(4)])
    H = tail_values[:, 0]
    factor = np.ones_like(H, dtype=np.float64)
    with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
        log_h = np.log(H)
        for k in range(1, len(tail_x)):
            factor[:, k] = factor[:, k - 1] * np.exp(
                3.0 * (tail_x[k - 1] - tail_x[k]) + log_h[:, k - 1] - log_h[:, k]
            )
        after = {}
        after["initial_memory"] = factor * old["initial_memory"][:, -1, None]
        for name in ("matter_memory", "radiation_memory"):
            after[name] = factor * old[name][:, -1, None] + local[name]
        after["predicted_signed_shear"] = (after["initial_memory"]
                                            + after["matter_memory"] + after["radiation_memory"])
        after["closure_defect"] = tail_values[:, 1] - after["predicted_signed_shear"]
        transported_old = factor * old["closure_defect"][:, -1, None]
        stitch_defect = after["closure_defect"] - local["closure_defect"] - transported_old
    merged = {name: np.concatenate((old[name], after[name][:, 1:]), axis=-1)
              for name in MEMORY_FIELDS}
    if any(not np.isfinite(value).all() for value in merged.values()):
        raise FloatingPointError("NONFINITE_STITCHED_OUTPUT")
    budget = {"transport_factor": factor, "local_closure_defect": local["closure_defect"],
              "transported_old_closure_defect": transported_old,
              "stitch_identity_defect": stitch_defect,
              "old_final_closure_defect": old["closure_defect"][:, -1]}
    return (np.concatenate((old_x, np.asarray(tail_x)[1:])),
            np.concatenate((old_values, tail_values[:, :, 1:]), axis=-1), merged, budget)


def _pr128_endpoint(x, values):
    path = Path(__file__).resolve().parents[2] / "hh_phys75_sector_memory_20261021/source/stress_memory.py"
    spec = importlib.util.spec_from_file_location("phys75_endpoint_reference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.memory_budget(x, *[values[:, k] for k in range(4)])
    return result, {"path": str(path.relative_to(Path(__file__).resolve().parents[3])),
                    "sha256": sha256(path)}


def select_cases(records):
    ids = [record["case_id"] for record in records]
    preferences = ("mixed_s+0_m+1", "mixed_s+0_m-1", "m_s00_+0_p12_+1",
                   "m_s00_+0_p12_-1", "s00_+0_p12_+1", "s00_+0_p12_-1")
    selected = [ids.index(cid) for cid in preferences if cid in ids]
    if not selected:
        selected = list(range(min(3, len(ids))))
    return selected


def analyze(old_root, out, tail_dir=None, expected_counts=(625, 606)):
    old_x, old_z, old_values, records = load_old(old_root, expected_counts)
    tail_x = tail_z = tail_values = None
    tail_receipts = []
    if tail_dir is not None:
        tail_x, tail_z, tail_values, tail_receipts = load_tail(tail_dir, records, old_root)
    x, values, memory, budget = stitch_segments(old_x, old_values, tail_x, tail_values)
    z = old_z.copy() if tail_z is None else np.concatenate((old_z, tail_z[1:]))
    baseline, baseline_identity = _pr128_endpoint(old_x, old_values)
    old_index = len(old_x) - 1
    match = {name: float(np.max(np.abs(memory[name][:, old_index] - baseline[name])))
             for name in MEMORY_FIELDS}
    ids = np.array([record["case_id"] for record in records])
    lanes = np.array([record["source_lane"] for record in records])
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    packet = {"x": x, "zbar": z, "values": values, "case_ids": ids, "source_lanes": lanes,
              "old_samples": np.array(len(old_x)), "tail_samples": np.array(0 if tail_x is None else len(tail_x)),
              "boundary_index": np.array(old_index), **{name: memory[name] for name in MEMORY_FIELDS}}
    if budget is not None:
        packet.update({"tail_" + name: value for name, value in budget.items()})
        packet["tail_x"] = tail_x
        packet["tail_zbar"] = tail_z
    np.savez_compressed(out / "TIME_PACKET.npz", **packet)
    root2 = np.sqrt(2.0)
    endpoints = []
    for j, record in enumerate(records):
        H, S, Pm, Pr = values[j]
        row = {"case_id": record["case_id"], "source_lane": record["source_lane"],
               "metadata_lane": record["metadata"].get("lane", "RADIATION_SLICE"),
               "initial_S_h": float(S[0]), "initial_P_m_h": float(Pm[0]),
               "initial_P_r_h": float(Pr[0]), "initial_S_F_signed": float(root2 * S[0]),
               "initial_Pi_m_F_signed": float(root2 * Pm[0]), "initial_Pi_r_F_signed": float(root2 * Pr[0]),
               "z_final": float(z[-1]), "S_final_F_signed": float(root2 * S[-1]),
               "Sigma_final_F": float(root2 * abs(S[-1])),
               "Pi_m_final_F_signed": float(root2 * Pm[-1]), "Pi_r_final_F_signed": float(root2 * Pr[-1]),
               "Pi_total_final_F": float(root2 * abs(Pm[-1] + Pr[-1])),
               "initial_memory_final_F_signed": float(root2 * memory["initial_memory"][j, -1]),
               "matter_memory_final_F_signed": float(root2 * memory["matter_memory"][j, -1]),
               "radiation_memory_final_F_signed": float(root2 * memory["radiation_memory"][j, -1]),
               "combined_closure_final_F_signed": float(root2 * memory["closure_defect"][j, -1]),
               "old_z4_closure_F_signed": float(root2 * memory["closure_defect"][j, old_index]),
               "tail_present": budget is not None,
               "tail_local_closure_final_F_signed": "" if budget is None else float(root2 * budget["local_closure_defect"][j, -1]),
               "transported_old_closure_final_F_signed": "" if budget is None else float(root2 * budget["transported_old_closure_defect"][j, -1])}
        endpoints.append(row)
    _csv(out / "ENDPOINTS.csv", endpoints)
    selected = select_cases(records)
    curve_rows = []
    for j in selected:
        H, S, Pm, Pr = values[j]
        denominator = np.abs(Pm) + np.abs(Pr)
        cancellation = 1.0 - np.divide(np.abs(Pm + Pr), denominator,
                                       out=np.ones_like(Pm), where=denominator > 0)
        for k in range(len(x)):
            curve_rows.append({"case_id": str(ids[j]), "source_lane": str(lanes[j]),
                               "sample": k, "x": float(x[k]), "zbar": float(z[k]),
                               "S_F_signed": float(root2 * S[k]), "Sigma_F": float(root2 * abs(S[k])),
                               "Pi_m_F_signed": float(root2 * Pm[k]), "Pi_r_F_signed": float(root2 * Pr[k]),
                               "Pi_m_F": float(root2 * abs(Pm[k])), "Pi_r_F": float(root2 * abs(Pr[k])),
                               "Pi_total_F": float(root2 * abs(Pm[k] + Pr[k])),
                               "stress_cancellation": float(cancellation[k]),
                               **{name + "_F_signed": float(root2 * memory[name][j, k]) for name in MEMORY_FIELDS}})
    _csv(out / "SELECTED_CURVES.csv", curve_rows)
    summary = {"schema": "PHYS76_TIME_ATTRIBUTION_V1", "scope": SCOPE,
               "status": "SAMPLED_SAME_TRAJECTORY_DIAGNOSTIC",
               "cases": len(records), "original_lane_counts": list(expected_counts),
               "old_samples_per_case": len(old_x), "tail_samples_per_case": 0 if tail_x is None else len(tail_x),
               "display_samples_per_case": len(x), "z_start": float(z[0]), "z_end": float(z[-1]),
               "coverage_target_z2_complete": tail_dir is not None,
               "quadrature": "Separate odd uniform Simpson grids; concatenation is display-only",
               "normalization": "signed half-contraction inputs; every F coordinate is sqrt(2) times half coordinate; total norm after signed tensor sum",
               "boundary_contract": "exact coordinate and observed-field equality at shared z4 node",
               "old_pr128_endpoint_max_abs_difference_half": match,
               "old_pr128_reference": baseline_identity,
               "max_abs_combined_closure_F": float(root2 * np.max(np.abs(memory["closure_defect"]))),
               "max_abs_combined_endpoint_closure_F": float(root2 * np.max(np.abs(memory["closure_defect"][:, -1]))),
               "selected_case_ids": [str(ids[j]) for j in selected],
               "new_ode_integrations_by_this_analysis": 0, "benchmark_runs": 0, "new_NCP_runs": 0,
               "HH_R10": "OFF", "production": "NOT_ISSUED",
               "packet_sha256": sha256(out / "TIME_PACKET.npz"),
               "endpoints_sha256": sha256(out / "ENDPOINTS.csv"),
               "selected_curves_sha256": sha256(out / "SELECTED_CURVES.csv")}
    if budget is not None:
        summary["tail_residual_budget"] = {
            "max_abs_tail_local_endpoint_closure_F": float(root2 * np.max(np.abs(budget["local_closure_defect"][:, -1]))),
            "max_abs_transported_old_endpoint_closure_F": float(root2 * np.max(np.abs(budget["transported_old_closure_defect"][:, -1]))),
            "max_abs_stitch_identity_defect_F": float(root2 * np.max(np.abs(budget["stitch_identity_defect"]))),
            "identity": "combined_defect = tail_local_defect + T_tail * old_z4_defect"}
    else:
        summary["tail_status"] = "NOT_SUPPLIED; figures stop at z4"
    _json(out / "INPUT_INDEX.json", {"schema": "PHYS76_TIME_INPUT_INDEX_V1", "fields": FIELDS,
                                     "old_root": str(Path(old_root).resolve()), "old_cases": records,
                                     "tail_root": None if tail_dir is None else str(Path(tail_dir).resolve()),
                                     "tail_cases": tail_receipts})
    _json(out / "SUMMARY.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-root", type=Path, required=True)
    parser.add_argument("--tail-dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.old_root, args.out, args.tail_dir), indent=2))
