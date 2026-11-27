#!/usr/bin/env python3
"""Freeze the pinned finite-L8 owner's binary64 coefficient tables exactly.

Only the approved PHYS76 loader and its pinned original files are imported.
One selected saved case supplies the original matter amplitude.  The original
constructor and set_amplitude are used; initial/rhs/solve are never called.
This exports a finite-coefficient model, not a solution or interval certificate.
"""
from __future__ import annotations

import argparse
import copy
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path, PurePosixPath
import platform
import re
import sys

import numpy as np


SCHEMA = "PHYS77_FROZEN_FINITE_OWNER_V1"
ENCODING = "Decimal.from_float(binary64), exact"
LOADER_REL = "research/hh_phys76_time_transport_20261021/source/continue_saved.py"
LOADER_SHA256 = "959952f9d347bcc515410ef90b3b8dc4b36388ad4bfd2acc2bac356fafd6d97b"
LOCK_REL = "research/hh_phys75_sector_memory_20261021/source/OWNER_LOCK.json"
LOCK_SHA256 = "85991ae90de5041bb1ff967b3abaf426a4787874ba71a3b1290a111317acdd1c"
ARCHIVE_SHA256 = "2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d"
MANIFEST_SHA256 = "3907bc7a228642443178af706e925aedf0e0b0c5e71843569befec552a6586d6"
INDEX_SHA256 = "62f5d96fd323b1ed60c61f4b51e35ab80eb3498d2800c6c04addc1e5e2483115"
OWNER_FILES = {
    "pilot.py": "4cf3db0a6d2bc4803e87dcffe422faa3ebe9478bf23a16e02a9f16fe5c2e4400",
    "SOURCE_ATTRIBUTION.json": "7df77051169ed00baa3f2ad73b3bb5c4f44bb9c89d83d58051b0a4db22981824",
    "matter_radiation_20261021/component_pilot.py": "e2ce8b440765be3a728d8127a4f1085dbc304cabcaa7a5d4e892f92ccabd801e",
    "vendor/REI_BACKGROUND_FAMILY_LOCK.json": "46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0",
    "vendor/canonical_fv.py": "91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5",
    "vendor/lrs_boltzmann.py": "06ef834e4cd7adacf01f0ad6e3becc5aea9a493b5b99fd398be82610543984cc",
    "vendor/species_hierarchy.py": "ced7906b35c26d8d0374ee8ce7f67ceb957b51a63d44e5a2661997b7e46983c5",
}
SHAPES = {"q": [72], "mu2": [36], "numbers": [72, 36], "M": [5, 5]}
PROFILE = {"L": 8, "state_order": ["tau", "b", "q=s/h_ref", "E0", "E2", "E4", "E6", "E8"],
           "radial_cells": 24, "angular_cells": 12, "gauss_order": 3,
           "packet_shape": [72, 36], "packet_count": 2592,
           "momentum_q_role": "canonical radial momentum; distinct from the shear-state q"}
CONSTANT_NAMES = {"h0", "omega_m", "omega_r", "omega_lambda", "a_ref", "h_ref", "f_m",
                  "mpref", "mass", "reference_energy_norm", "amplitude", "rhocrit_j_m3"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _checked_file(path, expected):
    path = Path(path).absolute()
    if any(item.is_symlink() for item in (path, *path.parents)):
        raise ValueError("SYMLINK_SOURCE_REJECTED")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("SOURCE_SHA256_MISMATCH:" + str(path))
    return data


def exact_decimal(value):
    if isinstance(value, (bool, complex, np.complexfloating)):
        raise ValueError("FINITE_REAL_BINARY64_REQUIRED")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("FINITE_REAL_BINARY64_REQUIRED")
    return str(Decimal.from_float(number))


def _binary64_decimal(text):
    if not isinstance(text, str):
        raise ValueError("EXACT_DECIMAL_STRING_REQUIRED")
    try:
        value = Decimal(text)
        number = float(value)
    except (InvalidOperation, ValueError, OverflowError) as exc:
        raise ValueError("INVALID_EXACT_DECIMAL") from exc
    if not value.is_finite() or not math.isfinite(number) or exact_decimal(number) != text:
        raise ValueError("NONCANONICAL_OR_INEXACT_BINARY64_DECIMAL")
    return value


def _decimal_array(values, shape):
    if not isinstance(values, list) or len(values) != shape[0]:
        raise ValueError("COEFFICIENT_ARRAY_SHAPE_MISMATCH")
    if len(shape) == 1:
        return [_binary64_decimal(value) for value in values]
    return [_decimal_array(value, shape[1:]) for value in values]


def _array_record(value, shape):
    array = np.asarray(value)
    if (array.dtype != np.dtype("float64") or list(array.shape) != shape
            or np.iscomplexobj(array) or not np.isfinite(array).all()):
        raise ValueError("FINITE_FLOAT64_COEFFICIENT_ARRAY_REQUIRED")
    copied = array.copy()
    values = np.vectorize(exact_decimal, otypes=[object])(copied).tolist()
    metadata = {"shape": list(shape),
                "exact_decimal_json_sha256": hashlib.sha256(canonical(values)).hexdigest(),
                "binary64_le_sha256": hashlib.sha256(np.asarray(copied, dtype="<f8").tobytes(order="C")).hexdigest()}
    return values, metadata


def capture_coefficients(model, f_m):
    """Pure capture from an already verified owner; no model evaluation."""
    momentum, source = model.momentum, model.src
    if (model.L != 8 or momentum.radial_cells != 24 or momentum.angular_cells != 12
            or momentum.gauss_order != 3):
        raise ValueError("FINITE_OWNER_PROFILE_MISMATCH")
    if (np.asarray(momentum._q).shape != (72, 1)
            or np.asarray(momentum._mu2).shape != (1, 36)):
        raise ValueError("ORIGINAL_SEPARABLE_ARRAY_SHAPE_MISMATCH")
    constants = {"h0": source.h0, "omega_m": source.omega_m, "omega_r": source.omega_r,
                 "omega_lambda": source.omega_lambda, "a_ref": source.aref, "h_ref": source.href,
                 "f_m": f_m, "mpref": model.mpref, "mass": momentum.mass,
                 "reference_energy_norm": momentum.reference_energy_norm,
                 "amplitude": momentum.amplitude, "rhocrit_j_m3": source.rhocrit_j_m3}
    originals = {"q": momentum._q[:, 0], "mu2": momentum._mu2[0],
                 "numbers": momentum._numbers, "M": model.mat}
    arrays, metadata = {}, {}
    for name, original in originals.items():
        arrays[name], metadata[name] = _array_record(original, SHAPES[name])
    captured = {"profile": copy.deepcopy(PROFILE), "constants": {key: exact_decimal(value) for key, value in constants.items()},
                "arrays": arrays, "array_metadata": metadata}
    validate_coefficients(captured)
    return captured


def validate_coefficients(table):
    if table.get("profile") != PROFILE:
        raise ValueError("FINITE_OWNER_PROFILE_MISMATCH")
    if set(table.get("constants", {})) != CONSTANT_NAMES or set(table.get("arrays", {})) != set(SHAPES):
        raise ValueError("COEFFICIENT_FIELD_SET_MISMATCH")
    constants = {key: _binary64_decimal(value) for key, value in table["constants"].items()}
    for key in ("h0", "a_ref", "h_ref", "mpref", "mass", "reference_energy_norm", "rhocrit_j_m3"):
        if constants[key] <= 0:
            raise ValueError("POSITIVE_OWNER_CONSTANT_REQUIRED:" + key)
    if (constants["mass"] != 30 or constants["f_m"] != Decimal.from_float(0.1)
            or not -1 <= constants["amplitude"] <= 2
            or any(constants[key] < 0 for key in ("omega_m", "omega_r", "omega_lambda"))):
        raise ValueError("OWNER_PHYSICAL_CONSTANT_CONTRACT")
    if set(table.get("array_metadata", {})) != set(SHAPES):
        raise ValueError("ARRAY_METADATA_FIELD_SET_MISMATCH")
    parsed = {}
    for name, shape in SHAPES.items():
        values = table["arrays"][name]
        parsed[name] = np.asarray(_decimal_array(values, shape), dtype=object)
        metadata = table["array_metadata"][name]
        if metadata.get("shape") != shape:
            raise ValueError("ARRAY_METADATA_SHAPE_MISMATCH")
        if metadata.get("exact_decimal_json_sha256") != hashlib.sha256(canonical(values)).hexdigest():
            raise ValueError("EXACT_DECIMAL_ARRAY_HASH_MISMATCH")
        raw = np.asarray(parsed[name], dtype="<f8").tobytes(order="C")
        if metadata.get("binary64_le_sha256") != hashlib.sha256(raw).hexdigest():
            raise ValueError("BINARY64_ARRAY_HASH_MISMATCH")
    if np.any(parsed["q"] < 0) or np.any(parsed["mu2"] < 0) or np.any(parsed["mu2"] > 1):
        raise ValueError("KINETIC_COORDINATE_DOMAIN_MISMATCH")
    if np.any(parsed["numbers"] < 0) or not np.any(parsed["numbers"] > 0):
        raise ValueError("NONNEGATIVE_NONEMPTY_PACKET_POPULATION_REQUIRED")
    return True


def seal(table):
    result = dict(table)
    result.pop("table_sha256", None)
    result["table_sha256"] = hashlib.sha256(canonical(result)).hexdigest()
    return result


def validate_table(table):
    if table.get("schema") != SCHEMA or table.get("encoding") != ENCODING:
        raise ValueError("FROZEN_OWNER_SCHEMA_OR_ENCODING_MISMATCH")
    if table.get("table_sha256") != seal(table)["table_sha256"]:
        raise ValueError("FROZEN_OWNER_TABLE_HASH_MISMATCH")
    validate_coefficients(table)
    provenance = table.get("provenance", {})
    expected = {"loader_sha256": LOADER_SHA256, "owner_lock_sha256": LOCK_SHA256,
                "archive_sha256": ARCHIVE_SHA256, "manifest_sha256": MANIFEST_SHA256,
                "terminal_index_sha256": INDEX_SHA256}
    if any(provenance.get(key) != value for key, value in expected.items()):
        raise ValueError("STALE_OR_FOREIGN_OWNER_PROVENANCE")
    case = provenance.get("case_identity", {})
    if (not isinstance(case.get("case_id"), str) or not re.fullmatch(r"[A-Za-z0-9_.+\-]+", case["case_id"])
            or case["case_id"] in (".", "..")):
        raise ValueError("CASE_IDENTITY_REQUIRED")
    for key in ("npz_sha256", "receipt_sha256", "terminal_state_sha256"):
        if not isinstance(case.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", case[key]):
            raise ValueError("CASE_SOURCE_HASH_REQUIRED:" + key)
    if case.get("amplitude_exact_decimal") != table["constants"]["amplitude"]:
        raise ValueError("CASE_AMPLITUDE_BINDING_MISMATCH")
    if provenance.get("owner_files") != OWNER_FILES:
        raise ValueError("STALE_OR_FOREIGN_OWNER_FILE_HASH_MAP")
    if table.get("HH_R10") != "OFF" or table.get("production_admission") != "NOT_ISSUED":
        raise ValueError("RESEARCH_ONLY_GATE_MISMATCH")
    return table


def load_export(path):
    table = json.loads(Path(path).read_text())
    validate_table(table)
    return table


def _load_pinned_loader(repo):
    path = Path(repo).absolute() / LOADER_REL
    _checked_file(path, LOADER_SHA256)
    spec = importlib.util.spec_from_file_location("_phys77_pinned_phys76_loader", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export_owner(repo, owner_root, terminal_index, case_id):
    if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z0-9_.+\-]+", case_id) or case_id in (".", ".."):
        raise ValueError("SAFE_EXPLICIT_CASE_ID_REQUIRED")
    loader = _load_pinned_loader(repo)
    owner = Path(owner_root).absolute()
    lock = json.loads(_checked_file(Path(repo) / LOCK_REL, LOCK_SHA256))
    if lock.get("upstream_archive_sha256") != ARCHIVE_SHA256:
        raise ValueError("OWNER_ARCHIVE_IDENTITY_MISMATCH")
    files = lock["files"]
    loader.check_owner(owner, files)
    raw_manifest = json.loads(_checked_file(owner / "MATTER_RADIATION_PAYLOAD_MANIFEST.json", MANIFEST_SHA256))
    manifest = {}
    for entry in raw_manifest["files"]:
        if not entry["path"].startswith(loader.PREFIX):
            raise ValueError("MANIFEST_PREFIX_MISMATCH")
        relative = entry["path"][len(loader.PREFIX):]
        loader.safe_path(owner, relative)
        if relative in manifest:
            raise ValueError("DUPLICATE_MANIFEST_SOURCE")
        manifest[relative] = entry
    for relative, expected in files.items():
        if manifest.get(relative, {}).get("sha256") != expected:
            raise ValueError("OWNER_FILE_MANIFEST_HASH_MISMATCH")
    index = json.loads(_checked_file(terminal_index, INDEX_SHA256))
    if (index.get("schema") != "REI198_SAVED_TERMINAL_INDEX_V1"
            or index.get("archive_sha256") != ARCHIVE_SHA256 or index.get("state_order") != loader.STATE_ORDER
            or len(index.get("rows", [])) != 1231
            or len({row["case_id"] for row in index["rows"]}) != 1231):
        raise ValueError("PINNED_TERMINAL_INDEX_CONTRACT_MISMATCH")
    selected = [row for row in index["rows"] if row["case_id"] == case_id]
    if len(selected) != 1:
        raise ValueError("CASE_NOT_IN_PINNED_TERMINAL_INDEX")
    row = loader.validate_case(owner, selected[0], files, manifest)
    model = loader._load_owner(owner, files)
    model.set_amplitude(row["amplitude_from_receipt"])
    captured = capture_coefficients(model, sys.modules["pilot"].FM)
    source_identity = {"case_id": case_id, "group": row["group"], "lane": row["lane"],
                       "npz_path": row["npz_path"], "npz_sha256": row["npz_sha256"],
                       "receipt_sha256": row["receipt_sha256"],
                       "terminal_state_sha256": hashlib.sha256(loader.f64_bytes(row["terminal"]["state"])).hexdigest(),
                       "amplitude_exact_decimal": captured["constants"]["amplitude"],
                       "restart_diagnostics_source": row["restart_diagnostics_source"]}
    table = seal({"schema": SCHEMA, "encoding": ENCODING,
                  "status": "FROZEN_COEFFICIENT_EXPORT_NO_ODE",
                  "semantics": "Exact-real formula over the captured binary64 coefficients; does not certify ideal quadrature, continuum physics or each machine-reduction rounding",
                  "capture": "Original pinned constructor under recorded runtime; no assertion of unrecorded past-runtime table bit identity",
                  **captured,
                  "provenance": {"loader_path": LOADER_REL, "loader_sha256": LOADER_SHA256,
                                 "owner_lock_sha256": LOCK_SHA256, "archive_sha256": ARCHIVE_SHA256,
                                 "manifest_sha256": MANIFEST_SHA256, "terminal_index_sha256": INDEX_SHA256,
                                 "owner_files": files, "case_identity": source_identity},
                  "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": loader.scipy.__version__},
                  "exporter_sha256": sha256(__file__), "new_ODE_solves": 0, "rhs_calls": 0,
                  "benchmark_runs": 0, "HH_R10": "OFF", "production_admission": "NOT_ISSUED"})
    validate_table(table)
    return table


def write_export(path, table):
    validate_table(table)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(table, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    observed = load_export(path)
    if observed != table:
        raise ValueError("EXPORT_READBACK_MISMATCH")
    return {"path": str(path), "file_sha256": sha256(path), "table_sha256": table["table_sha256"],
            "array_shapes": SHAPES, "case_id": table["provenance"]["case_identity"]["case_id"],
            "status": "EXACT_TABLE_READBACK_PASS", "new_ODE_solves": 0, "rhs_calls": 0, "benchmark_runs": 0}


def prepare_request(table, owner_root, predictor_nodes=2):
    """Build a candidate polygon from saved nodes, anchored at the exact saved IC.

    No solution assertion is made here.  The separate enclosure engine must prove
    each whole cell.  A later sampled endpoint alone is not accepted as an IC.
    """
    validate_table(table)
    if (isinstance(predictor_nodes, bool) or not isinstance(predictor_nodes, int)
            or not 2 <= predictor_nodes <= 65):
        raise ValueError("PREDICTOR_NODE_COUNT_MUST_BE_2_THROUGH_65")
    case = table["provenance"]["case_identity"]
    relative = PurePosixPath(case["npz_path"])
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("UNSAFE_RAW_HISTORY_PATH")
    owner = Path(owner_root).absolute()
    path = owner.joinpath(*relative.parts)
    if not path.resolve().is_relative_to(owner.resolve()):
        raise ValueError("RAW_HISTORY_OUTSIDE_OWNER")
    raw = _checked_file(path, case["npz_sha256"])
    with np.load(io.BytesIO(raw), allow_pickle=False) as history:
        x, state = history["x"], history["state"]
        if (x.shape != (65,) or state.shape != (8, 65)
                or x.dtype != np.dtype("float64") or state.dtype != np.dtype("float64")
                or not np.isfinite(x).all() or not np.isfinite(state).all()
                or x[0] != 0. or np.any(np.diff(x) <= 0)):
            raise ValueError("EXACT_ORIGINAL_INITIAL_STATE_AND_FORWARD_SAVED_GRID_REQUIRED")
        xs = [exact_decimal(value) for value in x[:predictor_nodes]]
        states = [[exact_decimal(value) for value in column]
                  for column in state[:, :predictor_nodes].T]
    return {"schema": "PHYS77_ENCLOSURE_REQUEST_V1", "table": copy.deepcopy(table),
            "predictor": {"x": xs, "state": states},
            "initial": {"kind": "exact_stored_initial_state", "x": xs[0], "state": list(states[0])},
            "config": {"precision": 50, "max_inflations": 8, "radius_floor": "1e-20",
                       "inflation_factor": "2", "max_cells": 1}}


def write_request(path, request):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(request, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    if json.loads(path.read_text()) != request:
        raise ValueError("REQUEST_READBACK_MISMATCH")
    return {"path": str(path), "file_sha256": sha256(path),
            "content_sha256": hashlib.sha256(canonical(request)).hexdigest(),
            "predictor_nodes": len(request["predictor"]["x"]),
            "initial_kind": request["initial"]["kind"],
            "status": "EXACT_SAVED_PREDICTOR_REQUEST_PREPARED_NO_ENCLOSURE_CLAIM",
            "new_ODE_solves": 0, "rhs_calls": 0, "benchmark_runs": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--owner-root", type=Path, required=True)
    parser.add_argument("--terminal-index", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--request-out", type=Path)
    parser.add_argument("--predictor-nodes", type=int, default=2)
    args = parser.parse_args()
    table = export_owner(args.repo, args.owner_root, args.terminal_index, args.case_id)
    receipt = {"table": write_export(args.out, table)}
    if args.request_out is not None:
        receipt["request"] = write_request(args.request_out,
            prepare_request(table, args.owner_root, args.predictor_nodes))
    print(json.dumps(receipt, indent=2))
