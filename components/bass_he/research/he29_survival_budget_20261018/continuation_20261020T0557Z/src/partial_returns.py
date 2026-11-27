"""Read and classify the four frozen HE29 reference returns without executing them.

Physical admission reuses reference_contract.check_result/admit_pair unchanged.
Return-file consistency is an additional evidence contract, reported separately.
Missing methods, process failures and differing runtime/binary cohorts remain
visible; this module never constructs a substitute reference or resumes a job.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

HE29 = Path(__file__).resolve().parents[2]
BASELINE_CODE = "1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f"
# Unchanged original science bytes retained in the a5d publication/readback.
SCIENCE_SOURCES = {
    "src/analyze_references.py": "31ca4a81e0da032338f2a560710df45058bfafcdfe02a31a22f4554c29affaa6",
    "src/analyze_return.py": "f8b2e3ad3388d499b23e06ca68c21ddd12a0584dcd000ecc728448196d29fb66",
    "src/kernel_study.py": "02cbbb365e70b9b533611b196c89288da1febe869e805769cd03721bfcef928f",
    "src/reference_contract.py": "d5d595ea71134b24e0d17ee8a0c89b7f1176d40c98c06086d296846921ca9cdb",
    "src/reference_runner.py": "dabb4968e5247815b8d19c31d792187bad497b23bf2028ce2539613ed527ff7e",
    "src/survival_bounds.py": "bedfc5050ac0ed9a434a8711e28e6d7e50218253873a5d62c58f9a9f7f5ad4f3",
}
PARENT_MANIFEST_SHA = "7c3262d58a28d4d272a9bb90e0a018be9d35306312f45787a5569698654e9f82"
INPUT_MANIFEST_SHA = "28917c4c292988a72dd4154443555437ed1de06158ff91a2104c0b189aacaca7"
SERVER_SOURCE = "research/he25_proper_birth_20261016/src/owner_server.rs"
METHODS = ("Radau", "DOP853")
CASE_JSON = ("IDENTITY.json", "TABLE.json", "SAVED_POINT_PARITY.json",
             "Radau.json", "DOP853.json", "RESULT.json", "FAILURE.json")
COHORT_FIELDS = ("binary_sha256", "source_files", "parent_sources", "input_sources",
                 "numerical_thread_environment")
sys.path.insert(0, str(HE29 / "src"))
from reference_contract import OWNER, JOBS, THREADS, check_result, admit_pair


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("HE29_RETURN_DUPLICATE_JSON_KEY: " + key)
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("HE29_RETURN_NONFINITE_JSON: " + value)


def _finite_json(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("HE29_RETURN_NONFINITE_JSON_NUMBER")
    if isinstance(value, dict):
        for item in value.values():
            _finite_json(item)
    elif isinstance(value, list):
        for item in value:
            _finite_json(item)


def read_json(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
    _finite_json(data)  # Also rejects finite-looking numeric literals such as 1e999.
    if not isinstance(data, dict):
        raise ValueError("HE29_RETURN_JSON_OBJECT_REQUIRED")
    return data


def _pinned_json(path, expected):
    if digest(path) != expected:
        raise ValueError("HE29_TRUSTED_INPUT_HASH: " + str(path))
    return read_json(path)


def load_trusted_identity(data_root=None):
    """Read pinned metadata/needed saved DATA, not old science or test outputs.

    No Git subprocess or solver is used. The original six source SHA values are
    frozen above; the two manifests are pinned by their published file hashes.
    Other parent code is not executed or revalidated by this read-only consumer.
    """
    # Code/manifests stay in this Git checkout; only DATA may live elsewhere.
    data_root = HE29 if data_root is None else Path(data_root)
    contract = HE29 / "src/reference_contract.py"
    if digest(contract) != SCIENCE_SOURCES["src/reference_contract.py"]:
        raise ValueError("HE29_IMPORTED_ADMISSION_SOURCE_CHANGED")
    parents = _pinned_json(HE29 / "provenance/PARENT_SHA256.json", PARENT_MANIFEST_SHA)
    inputs = _pinned_json(HE29 / "provenance/INPUT_SHA256.json", INPUT_MANIFEST_SHA)
    points = _pinned_json(data_root / "inputs/SAVED_NATIVE_POINTS.json",
                          inputs["inputs/SAVED_NATIVE_POINTS.json"])
    if points.get("owner_source") != OWNER or len(points.get("points", ())) != 6:
        raise ValueError("HE29_TRUSTED_SAVED_POINT_IDENTITY")
    tables = {}
    for r in (2, 4, 8):
        name = f"inputs/study/m8_r{r}_n64/RESULT.json"
        saved = _pinned_json(data_root / name, inputs[name])
        tables[f"m8_r{r}_table512"] = saved["source_table_sha256"]
    return {"source_files": dict(SCIENCE_SOURCES), "parent_sources": parents,
            "input_sources": inputs, "original_binary_sha256": points["original_binary_sha256"],
            "table_sha256": tables, "baseline_code_revision": BASELINE_CODE,
            "parent_manifest_sha256": PARENT_MANIFEST_SHA,
            "input_manifest_sha256": INPUT_MANIFEST_SHA}


def _sha(value):
    return (isinstance(value, str) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def _nonnegative(value, label, *, integer=False):
    if (type(value) not in ((int,) if integer else (int, float))
            or not math.isfinite(value) or value < 0):
        raise ValueError("HE29_RETURN_METRIC: " + label)


def _error(layer, exc, *, file=None, affects_admission=True):
    return {"layer": layer, "type": type(exc).__name__, "message": str(exc),
            "file": file, "affects_admission": affects_admission}


def _check_identity(identity, r, nodes, trust, binary_sha):
    if trust is None:
        raise ValueError("HE29_TRUST_UNAVAILABLE")
    expected = {"m": 8, "r": r, "angles": 4, "q": 0., "table_nodes": nodes}
    if any(identity.get(k) != v for k, v in expected.items()):
        raise ValueError("HE29_REFERENCE_CASE_IDENTITY")
    if identity.get("owner_source") != OWNER:
        raise ValueError("HE29_REFERENCE_OWNER_IDENTITY")
    for key in ("source_files", "parent_sources", "input_sources"):
        if canonical(identity.get(key)) != canonical(trust[key]):
            raise ValueError("HE29_REFERENCE_SOURCE_IDENTITY: " + key)
    if identity.get("numerical_thread_environment") != THREADS:
        raise ValueError("HE29_REFERENCE_THREAD_IDENTITY")
    sha = identity.get("binary_sha256")
    build = identity.get("build_receipt")
    if not _sha(sha) or not isinstance(build, dict):
        raise ValueError("HE29_REFERENCE_BINARY_RECEIPT_REQUIRED")
    if (build.get("owner_source") != OWNER or build.get("binary_sha256") != sha
            or build.get("server_source_sha256") != trust["parent_sources"][SERVER_SOURCE]):
        raise ValueError("HE29_REFERENCE_BUILD_IDENTITY")
    if binary_sha is not None and binary_sha != sha:
        raise ValueError("HE29_REFERENCE_RETURNED_BINARY_BYTES_MISMATCH")
    runtime = identity.get("runtime")
    if (not isinstance(runtime, dict)
            or any(not isinstance(runtime.get(k), str) or not runtime[k]
                   for k in ("python", "numpy", "scipy"))):
        raise ValueError("HE29_REFERENCE_RUNTIME_IDENTITY")
    cohort = {k: identity[k] for k in COHORT_FIELDS}
    cohort["runtime"] = {k: runtime[k] for k in ("python", "numpy", "scipy")}
    return hashlib.sha256(canonical(cohort).encode()).hexdigest(), cohort


def _check_qualification(value, identity, trust):
    if (value.get("scope") != "six_saved_native_points_only"
            or type(value.get("points")) is not int or value["points"] != 6
            or value.get("original_binary_sha256") != trust["original_binary_sha256"]):
        raise ValueError("HE29_REFERENCE_SAVED_POINT_IDENTITY")
    error = value.get("max_relative_nonzero_error")
    _nonnegative(error, "max_relative_nonzero_error")
    if error > 5e-13:
        raise ValueError("HE29_SAVED_POINT_PARITY")
    identical = identity["binary_sha256"] == trust["original_binary_sha256"]
    if (type(value.get("binary_byte_identity")) is not bool
            or value["binary_byte_identity"] != identical):
        raise ValueError("HE29_REFERENCE_SAVED_BINARY_LABEL")


def _method_metadata(value, method):
    metadata = value.get("metadata")
    if (not isinstance(metadata, dict) or metadata.get("method") != method
            or metadata.get("rtol") != 1e-10 or metadata.get("atol_scaled") != 1e-12):
        raise ValueError("HE29_REFERENCE_METHOD_OR_TOLERANCE_IDENTITY: " + method)


def _phase(data):
    if "RESULT.json" in data:
        return "COMPLETE_RECORD_PRESENT"
    methods = sum(name + ".json" in data for name in METHODS)
    if methods == 2:
        return "BOTH_METHODS_NO_RESULT"
    if methods == 1:
        return "METHOD_ONLY"
    if "IDENTITY.json" in data and "TABLE.json" in data:
        return "PREPARED"
    if "TABLE.json" in data:
        return "TABLE_ONLY"
    if "IDENTITY.json" in data:
        return "IDENTITY_ONLY"
    return "ABSENT"


def _classify_case(root, r, nodes, trust, binary_sha, global_errors):
    key = f"m8_r{r}_table{nodes}"
    folder, process_dir = root / key, root / (key + "_process")
    files, data, errors = {}, {}, []

    def read(path, label, *, process=False):
        if not path.exists() and not path.is_symlink():
            return None
        try:
            if path.is_symlink() or not path.is_file():
                raise ValueError("HE29_RETURN_REGULAR_FILE_REQUIRED")
            files[label] = {"bytes": path.stat().st_size, "sha256": digest(path)}
            result = read_json(path)
            return result
        except Exception as exc:
            errors.append(_error("process" if process else "return_consistency", exc,
                                 file=label, affects_admission=not process))
            return None

    for name in CASE_JSON:
        value = read(folder / name, key + "/" + name)
        if value is not None:
            data[name] = value
    process_data = {}
    for name in ("COMMAND.json", "RECEIPT.json"):
        value = read(process_dir / name, key + "_process/" + name, process=True)
        if value is not None:
            process_data[name] = value
    for path in (folder / "native.jsonl.gz", folder / "native.jsonl.gz.partial",
                 process_dir / "stdout.log", process_dir / "stderr.log"):
        if path.exists() or path.is_symlink():
            label = str(path.relative_to(root))
            try:
                if path.is_symlink() or not path.is_file():
                    raise ValueError("HE29_RETURN_REGULAR_FILE_REQUIRED")
                files[label] = {"bytes": path.stat().st_size, "sha256": digest(path)}
            except Exception as exc:
                errors.append(_error("process", exc, file=label, affects_admission=False))

    identity = data.get("IDENTITY.json")
    cohort_id = cohort_identity = None
    if identity is not None:
        try:
            if global_errors:
                raise ValueError("HE29_TRUST_OR_BINARY_READBACK_UNAVAILABLE")
            cohort_id, cohort_identity = _check_identity(identity, r, nodes, trust, binary_sha)
        except Exception as exc:
            errors.append(_error("identity", exc, file=key + "/IDENTITY.json"))
    table = data.get("TABLE.json")
    if table is not None:
        try:
            if not _sha(table.get("source_table_sha256")):
                raise ValueError("HE29_REFERENCE_TABLE_HASH_REQUIRED")
            expected = trust.get("table_sha256", {}).get(key) if trust else None
            if expected is not None and table["source_table_sha256"] != expected:
                raise ValueError("HE29_REBUILT_TABLE_DIFFERS_FROM_PARENT")
        except Exception as exc:
            errors.append(_error("identity", exc, file=key + "/TABLE.json"))
    qualification = data.get("SAVED_POINT_PARITY.json")
    if qualification is not None and identity is not None:
        try:
            if trust is None:
                raise ValueError("HE29_TRUST_UNAVAILABLE")
            _check_qualification(qualification, identity, trust)
        except Exception as exc:
            errors.append(_error("identity", exc, file=key + "/SAVED_POINT_PARITY.json"))

    results, method_records, method_gates = {}, {}, {}
    performance = {"methods": {}, "case_wall_s": None, "table_build_wall_s": None,
                   "case_native_calls": None, "process_wall_s": None,
                   "packed_or_native_speedup": "NOT_COMPUTED_DIFFERENT_MEASUREMENT_SCOPES",
                   "whole_process_peak_rss": "NOT_MEASURED"}
    for method in METHODS:
        record = data.get(method + ".json")
        if record is None:
            continue
        method_records[method] = record
        value = record.get("result")
        if isinstance(value, dict):
            results[method] = value
        try:
            check_result(value)
            method_gates[method] = {"status": "PASS", "original_contract_reused": True}
        except Exception as exc:
            method_gates[method] = {"status": "FAIL", "error": str(exc),
                                    "original_contract_reused": True}
            errors.append(_error("physical_admission", exc, file=key + "/" + method + ".json"))
        try:
            _method_metadata(value, method)
            _nonnegative(record.get("wall_s"), method + ".wall_s")
            _nonnegative(record.get("native_calls"), method + ".native_calls", integer=True)
            performance["methods"][method] = {
                "wall_s": record["wall_s"], "native_calls": record["native_calls"],
                "scope": "single method integration, including its native I/O and evidence writes",
                "solver_counters": {k: value["metadata"].get(k) for k in ("nfev", "njev", "nlu", "segment_count")}}
        except Exception as exc:
            errors.append(_error("return_consistency", exc, file=key + "/" + method + ".json"))
    pair_gate = {"status": "NOT_AVAILABLE", "original_contract_reused": True}
    if all(method in results for method in METHODS):
        try:
            pair_gate = {"status": "PASS", "original_contract_reused": True,
                         "comparison": admit_pair(results["Radau"], results["DOP853"])}
        except Exception as exc:
            pair_gate = {"status": "FAIL", "original_contract_reused": True, "error": str(exc)}
            errors.append(_error("physical_admission", exc))

    result = data.get("RESULT.json")
    required = ("IDENTITY.json", "TABLE.json", "SAVED_POINT_PARITY.json",
                "Radau.json", "DOP853.json", "RESULT.json")
    missing = [name for name in required if name not in data]
    if result is not None:
        try:
            if missing:
                raise ValueError("HE29_INCOMPLETE_RETURN_FILES: " + ",".join(missing))
            if result.get("status") != "REFERENCE_COMPLETED_SCOPED":
                raise ValueError("HE29_REFERENCE_COMPLETION_STATUS")
            if result.get("table_sha256") != table["source_table_sha256"]:
                raise ValueError("HE29_REFERENCE_TABLE_RECORD_MISMATCH")
            if canonical(result.get("point_qualification")) != canonical(qualification):
                raise ValueError("HE29_REFERENCE_QUALIFICATION_RECORD_MISMATCH")
            if canonical(result.get("results")) != canonical(results):
                raise ValueError("HE29_REFERENCE_METHOD_RESULT_MISMATCH")
            if canonical(result.get("method_calls")) != canonical(
                    {m: method_records[m]["native_calls"] for m in METHODS}):
                raise ValueError("HE29_REFERENCE_METHOD_CALLS_MISMATCH")
            if (pair_gate["status"] == "PASS"
                    and canonical(result.get("comparison")) != canonical(pair_gate["comparison"])):
                raise ValueError("HE29_REFERENCE_COMPARISON_RECORD_MISMATCH")
            _nonnegative(result.get("wall_s"), "case.wall_s")
            _nonnegative(result.get("native_calls"), "case.native_calls", integer=True)
            performance["case_wall_s"] = result["wall_s"]
            performance["case_native_calls"] = result["native_calls"]
            performance["case_scope"] = "source checks, qualification, table, both methods and case output"
        except Exception as exc:
            errors.append(_error("return_consistency", exc, file=key + "/RESULT.json"))
    if table is not None:
        diagnostics = table.get("diagnostics")
        if isinstance(diagnostics, dict) and "build_wall_s" in diagnostics:
            try:
                _nonnegative(diagnostics["build_wall_s"], "table.build_wall_s")
                performance["table_build_wall_s"] = diagnostics["build_wall_s"]
            except Exception as exc:
                errors.append(_error("return_consistency", exc, file=key + "/TABLE.json"))

    process = {"receipt": process_data.get("RECEIPT.json"),
               "command": process_data.get("COMMAND.json"),
               "case_failure": data.get("FAILURE.json"),
               "timed_out": None, "failed": None,
               "scope": "process observation is separate from completed scientific-file admission"}
    receipt = process["receipt"]
    if receipt is not None:
        try:
            if type(receipt.get("returncode")) is not int or type(receipt.get("timed_out")) is not bool:
                raise ValueError("HE29_PROCESS_RECEIPT_SCHEMA")
            _nonnegative(receipt.get("wall_s"), "process.wall_s")
            process["timed_out"] = receipt["timed_out"]
            process["failed"] = receipt["returncode"] != 0
            performance["process_wall_s"] = receipt["wall_s"]
            for stream in ("stdout", "stderr"):
                label = key + "_process/" + stream + ".log"
                if label in files and receipt.get(stream + "_sha256") != files[label]["sha256"]:
                    raise ValueError("HE29_PROCESS_STREAM_HASH_MISMATCH: " + stream)
        except Exception as exc:
            errors.append(_error("process", exc, file=key + "_process/RECEIPT.json",
                                 affects_admission=False))

    blockers = [error for error in errors if error["affects_admission"]]
    consistency_errors = [error for error in blockers if error["layer"] == "return_consistency"]
    identity_errors = [error for error in blockers if error["layer"] == "identity"]
    admitted = bool(not missing and not blockers and cohort_id and pair_gate["status"] == "PASS")
    phase = _phase(data)
    if admitted:
        status = "COMPLETE_VALID"
    elif blockers:
        status = "INVALID"
    elif process["timed_out"]:
        status = "TIMED_OUT"
    elif process["failed"] or process["case_failure"] is not None:
        status = "FAILED"
    else:
        status = phase
    return {"key": key, "r": r, "table_nodes": nodes, "status": status, "phase": phase,
            "admitted": admitted, "identity": identity, "cohort_id": cohort_id,
            "cohort_identity": cohort_identity, "table": table, "results": results,
            "method_records": method_records, "completion_record": result,
            "physical_admission": {"methods": method_gates, "pair": pair_gate},
            "identity_validation": {"status": "FAIL" if identity_errors else
                ("PASS" if cohort_id and table and qualification else "PARTIAL"),
                "recorded_execution_identity_only": binary_sha is None},
            "return_consistency": {"status": "FAIL" if consistency_errors else ("PARTIAL" if missing else "PASS"),
                                   "missing_files": missing,
                                   "original_physical_gates_unchanged": True},
            "binary_bytes_readback": ("FAILED" if any(e["layer"] == "binary_readback" for e in global_errors) else
                                      "NOT_PROVIDED" if binary_sha is None else
                                       ("MATCH" if identity and identity.get("binary_sha256") == binary_sha else "MISMATCH")),
            "errors": errors, "files": files, "performance": performance, "process": process}


def classify_campaign(root, *, binary=None, data_root=None):
    """Return four case records plus exact cohorts; never mutate input files.

    ``results[method]`` is the physical result dict, even for a partial method.
    Only ``admitted`` cases may be used as paired references. ``cohort_id`` must
    match before taking a cross-case contrast. An optional actual binary file
    enables byte readback; otherwise only recorded execution identity is checked.
    """
    root = Path(root)
    trust, binary_sha, global_errors = None, None, []
    if any((root / f"m8_r{r}_table{n}" / "IDENTITY.json").exists() for r, n in JOBS):
        try:
            trust = load_trusted_identity(data_root=data_root)
        except Exception as exc:
            global_errors.append(_error("trust_dependency", exc))
    if binary is not None:
        try:
            binary_sha = digest(binary)
        except Exception as exc:
            global_errors.append(_error("binary_readback", exc))
    cases = []
    for r, nodes in JOBS:
        try:
            cases.append(_classify_case(root, r, nodes, trust, binary_sha, global_errors))
        except Exception as exc:
            # A malformed case must not discard already classified independent cases.
            cases.append({"key": f"m8_r{r}_table{nodes}", "r": r, "table_nodes": nodes,
                          "status": "INVALID", "phase": "UNCLASSIFIED_ERROR", "admitted": False,
                          "identity": None, "results": {}, "method_records": {}, "files": {},
                          "performance": {}, "cohort_id": None,
                          "errors": [_error("case_read", exc)]})
    grouped = {}
    for case in cases:
        if case.get("cohort_id") is not None:
            item = grouped.setdefault(case["cohort_id"], {
                "id": case["cohort_id"], "identity": case["cohort_identity"] ,
                "case_keys": [], "admitted_keys": []})
            item["case_keys"].append(case["key"])
            if case["admitted"]:
                item["admitted_keys"].append(case["key"])
    cohorts = [grouped[key] for key in sorted(grouped)]
    admitted = sum(case["admitted"] for case in cases)
    active_cohorts = sum(bool(cohort["admitted_keys"]) for cohort in cohorts)
    return {"schema": "he29.reference.partial_returns.v1", "cases": cases, "cohorts": cohorts,
            "admitted_pairs": admitted, "requested_pairs": len(JOBS),
            "complete": admitted == len(JOBS) and active_cohorts == 1,
            "admitted_cohort_count": active_cohorts,
            "cross_cohort_contrasts": "HOLD" if active_cohorts > 1 else "SAME_COHORT_ONLY",
            "global_errors": global_errors, "baseline_code_revision": BASELINE_CODE,
            "trusted_metadata": {k: trust[k] for k in
                ("baseline_code_revision", "parent_manifest_sha256", "input_manifest_sha256")} if trust else None,
            "binary_bytes_readback": "NOT_PROVIDED" if binary is None else ("READ" if binary_sha else "FAILED"),
            "returned_binary_sha256": binary_sha, "solver_calls": 0, "native_calls": 0,
            "old_audit_recomputations": 0, "source_or_input_mutations": 0,
            "continuous_spectrum": "HOLD", "global_temperature_error_bound": "HOLD"}


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with temporary.open("x") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink()
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="original four-case campaign directory")
    parser.add_argument("--binary", help="optional returned owner binary for actual byte readback")
    parser.add_argument("--data-root", help="existing baseline HE29 DATA root; code/manifests remain in Git")
    parser.add_argument("--out", required=True, help="fresh immutable classification JSON")
    args = parser.parse_args(argv)
    result = classify_campaign(args.root, binary=args.binary, data_root=args.data_root)
    _write_json(args.out, result)
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
