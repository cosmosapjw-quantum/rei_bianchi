#!/usr/bin/env python3
"""Run exactly one frozen, root-bounded independent R15 reference campaign.

The root wrapper enforces CPU180s/wall240s/memory1GiB from process launch.
This CLI never imports production code, invokes CAS, or overwrites an output.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys


sys.set_int_max_str_digits(6000)

import reference_oracle as oracle


ALLOWED_MANIFEST_READS = (
    "verification/run_reference.py",
    "verification/reference_oracle.py",
    "verification/CASES.json",
    "verification/ARITHMETIC_SOURCE.json",
)


def fingerprint(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def read_json(path):
    raw = path.read_bytes()

    def reject_constant(value):
        raise oracle.ReferenceFailure("JSON_FORMAT", "Nonfinite JSON constant", value=value)

    try:
        document = json.loads(raw.decode("utf-8"), parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise oracle.ReferenceFailure("JSON_FORMAT", "Cannot decode frozen UTF-8 JSON", path=str(path), exception_type=type(exc).__name__) from exc
    return document, fingerprint(raw)


def relative_path(root, value):
    oracle.need(type(value) is str and value, "Invalid manifest path", "FROZEN_MANIFEST")
    path = Path(value)
    resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
    oracle.need(resolved.is_relative_to(root), "Manifest path escapes root leaf", "FROZEN_MANIFEST", path=value)
    return resolved.relative_to(root).as_posix()


def inspect_manifest(root, manifest):
    oracle.need(type(manifest) is dict and type(manifest.get("schema")) is str
                and type(manifest.get("files")) is list, "Invalid root freeze manifest", "FROZEN_MANIFEST")
    indexed = {}
    for row in manifest["files"]:
        key = relative_path(root, row["path"])
        oracle.need(key not in indexed, "Duplicate root freeze path", "FROZEN_MANIFEST", path=key)
        oracle.exact_int(row["bytes"], "manifest/bytes", 0)
        oracle.need(type(row["sha256"]) is str and oracle.SHA_RE.fullmatch(row["sha256"]) is not None,
                    "Invalid root freeze SHA256", "FROZEN_MANIFEST", path=key)
        indexed[key] = {"bytes": row["bytes"], "sha256": row["sha256"]}
    own_snapshots = {}
    for key in ALLOWED_MANIFEST_READS:
        oracle.need(key in indexed, "Required independent input/code absent from freeze manifest", "FROZEN_MANIFEST", path=key)
        actual = oracle.file_fingerprint(root / key)
        oracle.need(actual == indexed[key], "Independent code/input differs from freeze manifest", "FROZEN_MANIFEST", path=key)
        own_snapshots[key] = actual
    # CONTRACT is safe shared policy, and is checked if included in the root manifest.
    if "CONTRACT.json" in indexed:
        actual = oracle.file_fingerprint(root / "CONTRACT.json")
        oracle.need(actual == indexed["CONTRACT.json"], "Contract differs from freeze manifest", "FROZEN_MANIFEST")
        own_snapshots["CONTRACT.json"] = actual
    return indexed, own_snapshots


def check_contract(contract):
    finite = contract["finite_domain"]
    verification = contract["verification_contract"]
    internal = verification["reference_internal_arithmetic"]
    budget = contract["execution_budget"]["reference"]
    targets = {
        "input_scalar_bits_max": 256, "derived_scalar_bits_max": 16384,
        "runtime_integer_decimal_digit_limit": 6000,
        "saved_derived_rational_text_max_characters": 10000,
        "subdivision_depth": 96, "dyadic_bits": 128, "Taylor_degree": 96,
    }
    oracle.need(contract["unit"] == "WU_CUBIC_BERNSTEIN_FORCING_R15", "Wrong frozen reference unit", "CONTRACT")
    for key, value in targets.items():
        oracle.need(finite[key] == value, "Frozen finite arithmetic contract changed", "CONTRACT", field=key)
    oracle.need(internal["rational_numerator_denominator_bits_max"] == 1048576
                and internal["polynomial_degree_max"] == 4
                and internal["Euclidean_reductions_per_polynomial_chain_max"] == 5,
                "Reference-only arithmetic clarification missing or changed", "CONTRACT")
    oracle.need(verification["reference_precision"] == 160
                and verification["reference_guard"] == "1e-80*max(1,abs(reference),abs(lower),abs(upper)), fixed before execution; retain strict no-guard misses/count/examples",
                "Frozen Decimal precision/guard changed", "CONTRACT")
    oracle.need(budget["CPU_s_per_attempt"] == 180 and budget["wall_s_per_attempt"] == 240
                and budget["memory_bytes"] == 1073741824 and budget["base_runs"] == 1,
                "Frozen reference budget changed", "CONTRACT")


def check_primary_freeze_metadata(root, primary, indexed, manifest_snapshot):
    rows = primary["frozen_files"]
    oracle.need(type(rows) is list and rows, "Primary frozen-file record absent", "FROZEN_MANIFEST")
    seen = set()
    for row in rows:
        key = relative_path(root, row["path"])
        oracle.need(key not in seen, "Duplicate primary frozen-file record", "FROZEN_MANIFEST", path=key)
        seen.add(key)
        expected = manifest_snapshot if key == "verification/FROZEN_FILES.json" else indexed.get(key)
        oracle.need(expected is not None, "Primary frozen-file record is outside declared manifest", "FROZEN_MANIFEST", path=key)
        oracle.need({"bytes": row["bytes"], "sha256": row["sha256"]} == expected,
                    "Primary frozen-file metadata differs from root freeze", "FROZEN_MANIFEST", path=key)
    return len(rows)


def failed_payload(error):
    if isinstance(error, oracle.ReferenceFailure):
        record = error.record()
    else:
        record = {"category": "REFERENCE_IMPLEMENTATION_EXCEPTION", "message": str(error), "exception_type": type(error).__name__}
    return {
        "schema": "WU_R15_REFERENCE_RESULTS_V1", "unit": "WU_CUBIC_BERNSTEIN_FORCING_R15",
        "status": "FAIL", "classification": "REFERENCE_PREREQUISITE_OR_RUNTIME_FAILURE",
        "summary": {"valid_cases": len(oracle.CASE_IDS), "cases_passed": 0, "cases_failed": len(oracle.CASE_IDS),
                    "semantic_check_records": 0, "checks_passed": 0, "checks_failed": 0,
                    "guarded_comparisons": 0, "guarded_failures": 0, "strict_Decimal_misses": 0},
        "valid_cases": [{"id": case_id, "status": "FAIL", "blocked_after_failure": True,
                         "error": {"category": "BLOCKED_BY_PREREQUISITE_FAILURE", "message": "Declared case retained; see campaign_errors"}}
                        for case_id in oracle.CASE_IDS],
        "checks": [], "campaign_errors": [record], "strict_Decimal_miss_examples": [],
        "independence": {"production_imports": 0, "production_implementation_read": False},
    }


def add_failure(payload, error, check_id):
    payload["status"] = "FAIL"
    record = error.record() if isinstance(error, oracle.ReferenceFailure) else {
        "category": "REFERENCE_IMPLEMENTATION_EXCEPTION", "message": str(error), "exception_type": type(error).__name__}
    payload.setdefault("campaign_errors", []).append(record)
    payload.setdefault("checks", []).append({"id": check_id, "case_id": "__campaign__", "kind": "EXACT_METADATA", "status": "FAIL", "error": record})
    summary = payload.setdefault("summary", {})
    summary["semantic_check_records"] = len(payload["checks"])
    summary["checks_failed"] = sum(row["status"] != "PASS" for row in payload["checks"])
    summary["checks_passed"] = len(payload["checks"]) - summary["checks_failed"]


def progress(record):
    print(json.dumps({"reference_progress": record}, ensure_ascii=False, sort_keys=True), flush=True)


def serialize_output(payload):
    ready = oracle.json_ready(payload)
    ready["serialization"] = {"encoding": "UTF-8", "rational_format": "canonical reduced strings", "bytes": 0}
    for _ in range(5):
        raw = (json.dumps(ready, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
        if ready["serialization"]["bytes"] == len(raw):
            return raw
        ready["serialization"]["bytes"] = len(raw)
    raise oracle.ReferenceFailure("REFERENCE_SERIALIZATION", "Serialized byte-count fixed point did not close")


def emergency_ready(value):
    """Preserve every case/check if a derived value cannot be serialized normally."""
    if isinstance(value, oracle.Fraction):
        try:
            return oracle.rational_text(value)
        except Exception:
            numerator, denominator = value.numerator, value.denominator
            nb, db = abs(numerator).bit_length(), denominator.bit_length()
            return {"value_status": "EXACT_VALUE_EXCEEDS_PERSISTED_CAP",
                    "numerator_sign": -1 if numerator < 0 else 0 if numerator == 0 else 1,
                    "numerator_bits": nb, "denominator_bits": db,
                    "value_sha256": hashlib.sha256(
                        abs(numerator).to_bytes((nb + 7) // 8 or 1, "big") + b"/"
                        + denominator.to_bytes((db + 7) // 8 or 1, "big")).hexdigest()}
    if isinstance(value, oracle.Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(k): emergency_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [emergency_ready(v) for v in value]
    if value is None or type(value) in (str, int, bool):
        return value
    return {"value_status": "UNEXPECTED_SERIALIZATION_TYPE", "type": type(value).__name__, "representation": repr(value)[:2000]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    root, output = Path(args.root), Path(args.output)
    if not root.is_absolute() or not output.is_absolute():
        print("Both --root and --output must be absolute paths", file=sys.stderr)
        return 2
    root, output = root.resolve(), output.resolve()
    if output.exists():
        print("Refusing to overwrite an existing reference result: " + str(output), file=sys.stderr)
        return 2
    snapshots = {}
    payload = None
    try:
        oracle.need(Path(__file__).resolve() == root / "verification/run_reference.py"
                    and Path(oracle.__file__).resolve() == root / "verification/reference_oracle.py",
                    "Reference executed outside the frozen canonical code paths", "FROZEN_MANIFEST")
        oracle.need("cubic_convolution" not in sys.modules, "Production module present in independent reference process", "INDEPENDENCE")
        manifest, snapshots["verification/FROZEN_FILES.json"] = read_json(root / "verification/FROZEN_FILES.json")
        indexed, own_snapshots = inspect_manifest(root, manifest)
        snapshots.update(own_snapshots)
        fixtures, fixture_snapshot = read_json(root / "verification/CASES.json")
        source, source_snapshot = read_json(root / "verification/ARITHMETIC_SOURCE.json")
        oracle.need(fixture_snapshot == snapshots["verification/CASES.json"]
                    and source_snapshot == snapshots["verification/ARITHMETIC_SOURCE.json"],
                    "Frozen JSON changed between verification and read", "FROZEN_MANIFEST")
        contract, contract_snapshot = read_json(root / "CONTRACT.json")
        if "CONTRACT.json" in snapshots:
            oracle.need(contract_snapshot == snapshots["CONTRACT.json"], "Contract changed between freeze check and read", "FROZEN_MANIFEST")
        snapshots["CONTRACT.json"] = contract_snapshot
        check_contract(contract)
        primary, snapshots["raw/PRIMARY_RESULTS.json"] = read_json(root / "raw/PRIMARY_RESULTS.json")
        primary_freeze_count = check_primary_freeze_metadata(root, primary, indexed, snapshots["verification/FROZEN_FILES.json"])
        payload = oracle.run_reference_campaign(fixtures, primary, source, source_snapshot["sha256"], progress=progress)
        payload["frozen_manifest_scope"] = {
            "root_wrapper": "All manifest entries verified before launch by root-owned wrapper; no production code interpreted here",
            "reference": "Own code, fixed fixtures, shared contract, manifest stability and primary result stability",
            "manifest_entries": len(indexed), "primary_freeze_records_compared": primary_freeze_count,
            "production_file_bytes_read_by_reference": False,
        }
    except Exception as exc:
        payload = failed_payload(exc)
    try:
        for key, before in snapshots.items():
            oracle.need(oracle.file_fingerprint(root / key) == before, "Frozen input or primary changed during reference campaign", "FROZEN_POSTCHECK", path=key)
        payload["input_stability_postcheck"] = {"status": "PASS" if snapshots else "NOT_PERFORMED_NO_SNAPSHOTS", "files_checked": len(snapshots)}
    except Exception as exc:
        add_failure(payload, exc, "REF01_FREEZE_POSTCHECK")
        payload["input_stability_postcheck"] = {"status": "FAIL", "files_checked": len(snapshots)}
    payload["frozen_files"] = [{"path": key, **value} for key, value in sorted(snapshots.items())]
    payload["execution_contract"] = {
        "CPU_s": 180, "wall_s": 240, "memory_bytes": 1073741824,
        "measurement_owner": "ROOT_BOUNDED_WRAPPER_FROM_PROCESS_LAUNCH_THROUGH_SERIALIZATION",
        "ODE_runs": 0, "CAS_calls": 0, "production_imports": 0,
        "repair_policy": "No automatic retry; preserve actual failure for root diagnosis and at most one authorized repair attempt",
    }
    try:
        data = serialize_output(payload)
    except Exception as exc:
        # Preserve all case/check records; oversize exact values become explicit
        # unresolved bit-length/hash records rather than deleted failed cases.
        add_failure(payload, exc, "REF17_SERIALIZATION")
        payload["serialization_failure_preserved_report_with_explicit_value_markers"] = True
        payload = emergency_ready(payload)
        data = serialize_output(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(data)
    print(json.dumps({"reference_result": {"status": payload["status"], "path": str(output),
                                          "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}}, sort_keys=True), flush=True)
    return 0 if payload["status"] == "PASS_SCOPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
