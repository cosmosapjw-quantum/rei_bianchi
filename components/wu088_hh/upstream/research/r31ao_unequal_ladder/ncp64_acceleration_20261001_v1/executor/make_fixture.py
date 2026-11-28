#!/usr/bin/env python3
"""Create-only synthetic manifests; creates no backend build or execution."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from core import SCHEMA, ContractError, absolute, file_identity, identity_spec, load_manifest, read_json

HERE = Path(__file__).resolve().parent


def write_manifest(path, root, tasks):
    path, root = Path(path).absolute(), Path(root).absolute()
    if path.exists() or root.exists() or not path.parent.is_dir() or not root.parent.is_dir():
        raise ContractError("CREATE_ONLY_MANIFEST_AND_RUN_WITH_EXISTING_PARENTS_REQUIRED")
    doc = {"schema": SCHEMA, "scope": "SYNTHETIC_ONLY", "output_root": str(root),
           "tasks": tasks, "dispatch_order": sorted(range(len(tasks)),
              key=lambda i: (-tasks[i]["cost_hint"], tasks[i]["task_id"]))}
    with path.open("x") as f:
        json.dump(doc, f, indent=2); f.write("\n")
    load_manifest(path)
    return doc


def default_limits():
    return {"wall_seconds": 30, "address_space_bytes": 256 << 20,
            "rss_bytes": 128 << 20, "poll_ms": 50, "max_output_bytes": 8 << 20}


def create_fixture(output_manifest, output_root, task_count=16, cpu_units=1000000):
    if type(task_count) is not int or not 1 <= task_count <= 4096:
        raise ContractError("TASK_COUNT")
    if type(cpu_units) is not int or not 1 <= cpu_units <= 5000000:
        raise ContractError("CPU_UNITS_1_TO_5000000")
    exe = file_identity(Path(sys.executable).resolve())
    script = file_identity(HERE / "synthetic_backend.py")
    tasks = []
    for i in range(task_count):
        n, d = (-1 if i % 2 else 1) * (2*i + 17), 2*i + 9
        value = Fraction(n, d)
        # Uneven deterministic CPU cost, bounded by the requested base maximum.
        units = max(1, cpu_units * (1 + ((i*7) % 8)) // 8)
        exact_sum = units * (units + 1) * (2*units + 1) // 6
        payload = (f"EXACT_RATIONAL_V1\n{value.numerator}/{value.denominator}\nimag=0/1\nliteral=\n"
                   f"exact_sum_of_squares={exact_sum}\n").encode("ascii")
        tasks.append({"task_id": f"cpu_{i:05d}", "executable": exe, "inputs": [script],
            "argv": [exe["path"], "-B", script["path"], "--output", "OUTPUT_PATH",
                     "--numerator", str(n), "--denominator", str(d), "--work-units", str(units)],
            "env": {}, "cost_hint": units, "limits": default_limits(),
            "semantic_identity": {"fixture": "SIGNED_RATIONAL_AND_EXACT_SUM_SQUARES_V1",
                 "precision": "EXACT_INTEGER_FRACTION", "work_units": units,
                 "full_parameter_box": {"real": [str(value), str(value)], "imag": ["0", "0"]}},
            "expected_output_sha256": hashlib.sha256(payload).hexdigest()})
    return write_manifest(output_manifest, output_root, tasks)


def native_receipt(build_ready, backend_library_path, backend=None):
    """Pin supplied build-receipt bytes; this is not a witnessed-build verifier."""
    if build_ready is None or backend_library_path is None:
        raise ContractError("NATIVE_BUILD_READY_AND_LIBRARY_DIRECTORY_REQUIRED")
    receipt_path = absolute(str(build_ready))
    library_dir = absolute(str(backend_library_path))
    if library_dir.resolve() != library_dir or not library_dir.is_dir() or ":" in str(library_dir):
        raise ContractError("ONE_CANONICAL_BACKEND_LIBRARY_DIRECTORY_REQUIRED")
    doc, raw = read_json(receipt_path)
    receipt_pin = file_identity(receipt_path)
    if receipt_pin["sha256"] != hashlib.sha256(raw).hexdigest():
        raise ContractError("BUILD_READY_CHANGED_DURING_READ")
    if (type(doc) is not dict or doc.get("scope") != "SYNTHETIC_ONLY" or
        type(doc.get("actual_HH_runs")) is not int or doc["actual_HH_runs"] != 0 or
        doc.get("scientific_promotion") is not False or doc.get("native_executed") is not False or
        doc.get("native_equality_verified") is not False):
        raise ContractError("SYNTHETIC_BUILD_ONLY_RECEIPT_REQUIRED")
    def checked(item):
        if type(item) is not dict or not {"path", "size", "sha256"} <= set(item):
            raise ContractError("BUILD_READY_FILE_IDENTITY_REQUIRED")
        wanted = {"path": item["path"], "bytes": item["size"], "sha256": item["sha256"]}
        identity_spec(wanted)
        if file_identity(wanted["path"]) != wanted:
            raise ContractError("BUILD_READY_FILE_BYTES_MISMATCH")
        return wanted
    binary = checked(doc.get("binary"))
    if backend is not None and str(absolute(str(backend)).resolve()) != binary["path"]:
        raise ContractError("BUILD_READY_BACKEND_ARGUMENT_MISMATCH")
    linkage, chain = doc.get("linkage"), doc.get("backend_byte_chain")
    names = {"flint", "gmp", "mpfr"}
    if (type(linkage) is not dict or linkage.get("status") != "LINKED_BACKEND_PATHS_VERIFIED" or
        type(linkage.get("libraries")) is not dict or set(linkage["libraries"]) != names or
        type(chain) is not dict or chain.get("status") != "BYTE_CHAIN_VERIFIED" or
        type(chain.get("libraries")) is not dict or set(chain["libraries"]) != names):
        raise ContractError("BUILD_READY_THREE_LINKED_LIBRARIES_REQUIRED")
    libraries = {}
    for name in sorted(names):
        pin = checked(linkage["libraries"][name])
        if Path(pin["path"]).parent != library_dir:
            raise ContractError("BACKEND_LIBRARY_DIRECTORY_MISMATCH")
        if pin["path"] in libraries:
            raise ContractError("DUPLICATE_BACKEND_LIBRARY_PATH")
        item = chain["libraries"][name]
        if type(item) is not dict or checked(item.get("binary")) != pin:
            raise ContractError("BUILD_READY_CHAIN_LINKAGE_MISMATCH")
        libraries[pin["path"]] = pin
    system = linkage.get("system_libraries")
    if type(system) is not list or len(system) > 64:
        raise ContractError("BUILD_READY_SYSTEM_LIBRARY_LIST_REQUIRED")
    for item in system:
        pin = checked(item)
        if pin["path"] in libraries:
            raise ContractError("DUPLICATE_LINKED_LIBRARY_PATH")
        libraries[pin["path"]] = pin
    if type(doc.get("sources")) is not list or not 1 <= len(doc["sources"]) <= 128:
        raise ContractError("BUILD_READY_SOURCES_REQUIRED")
    inputs = {receipt_pin["path"]: receipt_pin}
    for item in doc["sources"] + [doc.get(k) for k in
            ("backend_record", "link_report", "native_compiler", "native_compiler_version_output")]:
        pin = checked(item)
        inputs[pin["path"]] = pin
    # Retain archive and executed-stage/log identities from the supplied byte chain.
    # Checks all referenced bytes, but never infers that logs independently prove execution.
    visited = 0
    def visit(value, depth=0):
        nonlocal visited
        visited += 1
        if visited > 4096 or depth > 16:
            raise ContractError("BUILD_READY_CHAIN_TOO_LARGE")
        if type(value) is dict:
            if {"path", "size", "sha256"} <= set(value):
                pin = checked(value)
                inputs[pin["path"]] = pin
            for child in value.values():
                visit(child, depth + 1)
        elif type(value) is list:
            for child in value:
                visit(child, depth + 1)
    visit(chain)
    for path in libraries:
        inputs.pop(path, None)
    inputs.pop(binary["path"], None)
    if len(inputs) > 128 or len(libraries) < 3:
        raise ContractError("BUILD_READY_INPUT_COUNT")
    return binary, list(inputs.values()), list(libraries.values()), str(library_dir), receipt_pin


def create_native_fixture(output_manifest, output_root, backend, cases,
                          precision=128, repeat=1, *, build_ready=None, backend_library_path=None):
    allowed = {"point107", "complex_point107", "complex_box107", "errors"}
    if (type(cases) is not list or not 1 <= len(cases) <= 4096 or
        any(type(c) is not str or c not in allowed for c in cases) or
        type(precision) is not int or not 32 <= precision <= 4096 or
        type(repeat) is not int or not 1 <= repeat <= 100):
        raise ContractError("NATIVE_SYNTHETIC_CASE_PRECISION_REPEAT")
    if "errors" in cases and repeat != 1:
        raise ContractError("ERROR_FIXTURE_REQUIRES_REPEAT_ONE")
    binary, inputs, library_pins, library_dir, receipt_pin = native_receipt(
        build_ready, backend_library_path, backend)
    tasks = []
    for i, case in enumerate(cases):
        limits = default_limits()
        limits.update(wall_seconds=120, address_space_bytes=1 << 30, rss_bytes=768 << 20)
        tasks.append({"task_id": f"native_{i:05d}_{case}", "executable": binary,
            "inputs": inputs, "library_pins": library_pins,
            "argv": [binary["path"], "--output", "OUTPUT_PATH", "--case", case,
                     "--repeat", str(repeat), "--precision", str(precision)],
            "env": {"LD_LIBRARY_PATH": library_dir}, "cost_hint": repeat * (3 if case == "complex_box107" else 1),
            "limits": limits, "semantic_identity": {"fixture": "NATIVE_CACHE_SYNTHETIC_V1",
                "case": case, "precision_bits": precision, "repeat": repeat,
                "build_ready_sha256": receipt_pin["sha256"],
                "full_parameter_box": "complete fixed synthetic recipe embedded in the declared binary identity",
                "baseline_cached_exact_ball_equality_required_by_backend": True}})
    return write_manifest(output_manifest, output_root, tasks)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-manifest", required=True)
    p.add_argument("--output-root", required=True)
    p.add_argument("--task-count", type=int, default=16)
    p.add_argument("--cpu-units", type=int, default=1000000)
    p.add_argument("--backend")
    p.add_argument("--case", action="append")
    p.add_argument("--precision", type=int, default=128)
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--build-ready")
    p.add_argument("--backend-library-path")
    a = p.parse_args()
    try:
        if a.backend or a.build_ready or a.backend_library_path or a.case:
            doc = create_native_fixture(a.output_manifest, a.output_root, a.backend,
                                        a.case or ["point107", "complex_point107", "complex_box107"],
                                        a.precision, a.repeat, build_ready=a.build_ready,
                                        backend_library_path=a.backend_library_path)
        else:
            doc = create_fixture(a.output_manifest, a.output_root, a.task_count, a.cpu_units)
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({"status": "INCONCLUSIVE", "reason": str(exc)}))
        return 2
    print(json.dumps({"status": "MANIFEST_CREATED", "tasks": len(doc["tasks"]),
                      "manifest": str(Path(a.output_manifest).absolute())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
