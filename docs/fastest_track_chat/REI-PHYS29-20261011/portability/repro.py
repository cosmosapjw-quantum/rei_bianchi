#!/usr/bin/env python3
"""Restore the frozen PHYS29 runtime and optionally perform one operational replay.

Only the new PHYS29 entrypoint is invoked. No old research module is imported.
This checks operational reproducibility, with independent physics credit zero.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import subprocess
import sys
import time
import zipfile


TASK = "REI-PHYS29-20261011"
ENTRYPOINT = "contributions/numerics/second_order_width.py"
FREEZE = "contributions/numerics/PREEXECUTION_FROZEN.json"
PROTOCOL = "contributions/numerics/PROTOCOL.json"
MANIFEST = "PORTABLE_MANIFEST.json"
TIMEOUT_SECONDS = 30
FORBIDDEN_COUNTS = (
    "new_physical_root_searches", "physical_root_iterations", "old_module_imports",
    "old_main_invocations", "closed_suite_replays", "old_physical_root_searches",
    "quadrature_evaluations", "finite_difference_evaluations", "width_root_sweep",
    "new_derivative_sign_campaigns", "native_runs", "gas_IVP_runs",
    "dense_LP_or_multiple_parameter_campaigns", "display_new_kernel_derivative_evaluations",
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": digest(raw)}


def fresh_write(path, raw):
    with path.open("xb") as handle:
        handle.write(raw)


def write_json(path, value):
    fresh_write(path, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode())


def safe_relative(name):
    path = PurePosixPath(name)
    if (not name or name.endswith("/") or "\\" in name or path.is_absolute()
            or ".." in path.parts or "." in path.parts or str(path) != name):
        raise ValueError(f"unsafe or noncanonical archive path: {name!r}")


def validate_archive(archive, expected_sha256):
    archive_id = identity(archive)
    if archive_id["sha256"] != expected_sha256:
        raise ValueError("archive SHA256 differs from explicitly supplied identity")
    with zipfile.ZipFile(archive) as handle:
        names = handle.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP member")
        for item in handle.infolist():
            safe_relative(item.filename)
            if (item.external_attr >> 16) != 0o100644:
                raise ValueError(f"nonregular or wrong-mode ZIP member: {item.filename}")
        manifest_raw = handle.read(MANIFEST)
        manifest = json.loads(manifest_raw)
        if manifest["task"] != TASK or manifest["entrypoint"] != ENTRYPOINT:
            raise ValueError("wrong task or entrypoint")
        rows = manifest["files"]
        expected_names = [row["path"] for row in rows] + [MANIFEST]
        if (len(expected_names) != len(set(expected_names))
                or set(names) != set(expected_names) or len(rows) != 26):
            raise ValueError("archive member set does not match the 26-file runtime closure")
        payloads = {}
        for row in rows:
            name = row["path"]
            safe_relative(name)
            data = handle.read(name)
            if (len(data) != row["bytes"] or digest(data) != row["sha256"]
                    or row["mode"] != "100644"):
                raise ValueError(f"payload identity or mode mismatch: {name}")
            payloads[name] = data
        payloads[MANIFEST] = manifest_raw
    return manifest, payloads, archive_id


def verify_dependency_chain(manifest, payloads):
    frozen = json.loads(payloads[FREEZE])
    protocol = json.loads(payloads[PROTOCOL])
    archive_rows = {row["path"]: row for row in manifest["files"]}
    frozen_rows = {row["path"]: row for row in frozen["files"]}
    input_rows = {row["path"]: row for row in protocol["inputs"]}
    extras = {
        ENTRYPOINT, PROTOCOL,
        "contributions/numerics/INPUT_PROVENANCE.json",
        "contributions/numerics/STATIC_CHECKS.json",
        "contributions/numerics/PREEXECUTION_CHANGES.json",
    }
    checks = []
    for name, row in frozen_rows.items():
        stored = archive_rows.get(name, {})
        checks.append({"kind": "freeze_to_archive", "path": name,
                       "pass": all(stored.get(key) == row[key] for key in ("bytes", "sha256"))})
    for name, row in input_rows.items():
        stored = frozen_rows.get(name, {})
        checks.append({"kind": "protocol_to_freeze", "path": name,
                       "pass": all(stored.get(key) == row[key] for key in ("bytes", "sha256"))})
    runtime = set(frozen_rows) | {FREEZE}
    all_pass = (len(frozen_rows) == len(frozen["files"]) == 25
                and len(input_rows) == len(protocol["inputs"]) == 20
                and set(frozen_rows) == set(input_rows) | extras
                and set(archive_rows) == runtime
                and set(manifest["runtime_files"]) == runtime
                and protocol["entrypoint"] == ENTRYPOINT
                and all(row["pass"] for row in checks))
    return {"all_pass": all_pass, "protocol_input_count": len(input_rows),
            "frozen_identity_count": len(frozen_rows), "runtime_file_count": len(runtime),
            "scope": "Declared frozen dependency closure; static source I/O inspected; no OS-wide open tracing",
            "checks": checks}


def verify_restored(destination, manifest, payloads):
    checks = []
    for row in manifest["files"]:
        path = destination / row["path"]
        raw = path.read_bytes()
        checks.append({
            "path": row["path"], "bytes": len(raw), "sha256": digest(raw),
            "size_equal": len(raw) == row["bytes"], "sha256_equal": digest(raw) == row["sha256"],
            "archive_byte_equal": raw == payloads[row["path"]],
            "regular_file": path.is_file() and not path.is_symlink(),
            "mode_100644": stat.S_IMODE(path.stat().st_mode) == 0o644,
        })
    actual_names = sorted(path.relative_to(destination).as_posix()
                          for path in destination.rglob("*") if path.is_file() or path.is_symlink())
    manifest_path = destination / MANIFEST
    manifest_equal = manifest_path.read_bytes() == payloads[MANIFEST]
    manifest_mode = (not manifest_path.is_symlink()
                     and stat.S_IMODE(manifest_path.stat().st_mode) == 0o644)
    exact_member_set = actual_names == sorted(payloads)
    all_pass = (exact_member_set and manifest_equal and manifest_mode
                and all(all(row[key] for key in (
                    "size_equal", "sha256_equal", "archive_byte_equal", "regular_file", "mode_100644"
                )) for row in checks))
    return {"all_pass": all_pass, "runtime_payload_count": len(checks),
            "total_files_including_manifest": len(actual_names), "exact_member_set": exact_member_set,
            "manifest_byte_equal": manifest_equal, "manifest_mode_100644": manifest_mode,
            "files": checks}


def counts_match_protocol(counts):
    expected = {
        "program_main_invocations_this_process": 1,
        "actual_unique_energy_nodes": 4,
        "primary_jet_joint_evaluations": 4,
        "independent_scalar_joint_evaluations": 4,
        "combined_kernel_derivative_joint_evaluations": 8,
        "k_component_outputs": 8, "k_prime_component_outputs": 8,
        "k_second_component_outputs": 8,
        "combined_k_kprime_ksecond_component_outputs": 24,
        "sigma_auxiliary_outputs": 8,
    }
    expected.update({key: 0 for key in FORBIDDEN_COUNTS})
    checks = {key: counts.get(key) == value for key, value in expected.items()}
    return {"all_pass": all(checks.values()), "expected": expected, "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--record-prefix", type=Path, required=True)
    parser.add_argument("--reference-result", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify-only", action="store_true")
    mode.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    archive, destination, prefix = args.archive.resolve(), args.destination.resolve(), args.record_prefix.resolve()
    records = {name: Path(str(prefix) + suffix) for name, suffix in {
        "receipt": "_RECEIPT.json", "stdout": "_STDOUT.txt", "stderr": "_STDERR.txt",
        "result": "_RESULT.json", "invocation": "_INVOCATION.json",
    }.items()}
    if prefix.is_relative_to(destination):
        raise ValueError("records must remain outside the immutable restored runtime")
    if destination.exists():
        raise FileExistsError(f"refusing existing destination: {destination}")
    for path in records.values():
        if path.exists():
            raise FileExistsError(f"refusing existing record: {path}")
    if args.replay and args.reference_result is None:
        raise ValueError("--reference-result is required for a replay comparison")
    manifest, payloads, archive_id = validate_archive(archive, args.archive_sha256)
    dependency = verify_dependency_chain(manifest, payloads)
    if not dependency["all_pass"]:
        raise ValueError("declared dependency closure mismatch before any science invocation")
    first_raw = None
    if args.replay:
        reference = args.reference_result.resolve()
        if reference.is_relative_to(destination):
            raise ValueError("original result must remain external to restored runtime")
        first_raw = reference.read_bytes()
        expected_first = manifest["comparison_reference"]
        if len(first_raw) != expected_first["bytes"] or digest(first_raw) != expected_first["sha256"]:
            raise ValueError("original result identity differs from frozen comparison reference")
        first_result = json.loads(first_raw)
        if first_result["task"] != TASK or first_result["summary"]["all_pass"] is not True:
            raise ValueError("original first result is not the accepted PHYS29 comparison reference")
    destination.mkdir(parents=True, exist_ok=False)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    for name, data in payloads.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        fresh_write(target, data)
        target.chmod(0o644)
    before = verify_restored(destination, manifest, payloads)
    if not before["all_pass"]:
        raise ValueError("restored payload identity failed before any science invocation")
    receipt = {
        "schema": 1, "task": TASK, "agent": "/root/phys29_portability",
        "evidence_status": "implementation-verified", "independent_physics_credit": 0,
        "mode": "replay" if args.replay else "verify-only", "created_utc": utc_now(),
        "archive": archive_id, "destination": str(destination), "runner": identity(Path(__file__).resolve()),
        "preexecution_restore": before, "preexecution_dependency_chain": dependency,
        "source_or_science_code_edits": 0, "new_program_replay_invocations": 0,
        "old_PHYS19_through_PHYS28_program_invocations": 0, "new_physical_root_searches": 0,
        "environment": {"python_version": sys.version, "python_executable": sys.executable,
                        "platform": platform.platform(), "bytecode_writes": False,
                        "scope": "Same cloud host and Python; different absolute runtime path, not a new OS or independent implementation"},
    }
    if args.verify_only:
        receipt.update(status="VERIFY_ONLY_PASS", postexecution_restore=before)
        write_json(records["receipt"], receipt)
        print(json.dumps({"status": receipt["status"], "runtime_files": 26, "science_runs": 0}))
        return 0
    command = [sys.executable, "-B", str(destination / ENTRYPOINT), "--output", str(records["result"])]
    receipt.update(command=command, cwd=str(destination), timeout_seconds=TIMEOUT_SECONDS,
                   started_utc=utc_now(), replay_attempts_debited=1, first_result=identity(reference))
    write_json(records["invocation"], {
        "task": TASK, "started_utc": receipt["started_utc"], "command": command,
        "cwd": str(destination), "timeout_seconds": TIMEOUT_SECONDS,
        "replay_attempts_debited": 1, "automatic_retry": False, "independent_physics_credit": 0,
        "archive_sha256": archive_id["sha256"], "first_result_sha256": digest(first_raw),
    })
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started_wall = time.perf_counter()
    timed_out, launch_error, returncode = False, None, None
    with records["stdout"].open("xb") as stdout, records["stderr"].open("xb") as stderr:
        try:
            completed = subprocess.run(command, cwd=destination, env=environment,
                                       stdout=stdout, stderr=stderr, timeout=TIMEOUT_SECONDS, check=False)
            returncode = completed.returncode
            receipt["new_program_replay_invocations"] = 1
        except subprocess.TimeoutExpired:
            timed_out = True
            receipt["new_program_replay_invocations"] = 1
        except OSError as error:
            launch_error = {"type": type(error).__name__, "message": str(error)}
    receipt.update(wall_seconds=time.perf_counter() - started_wall, ended_utc=utc_now(),
                   actual_exit_code=returncode, timed_out=timed_out, launch_error=launch_error,
                   stdout=identity(records["stdout"]), stderr=identity(records["stderr"]))
    receipt["postexecution_restore"] = verify_restored(destination, manifest, payloads)
    receipt.update(result_exists=records["result"].is_file(), result_byte_equal=False,
                   result_parsed_json_equal=False, result_all_pass=False, actual_count_check={"all_pass": False})
    if receipt["result_exists"]:
        result_raw = records["result"].read_bytes()
        receipt.update(result=identity(records["result"]), result_byte_equal=result_raw == first_raw)
        try:
            result = json.loads(result_raw)
            receipt.update(result_parsed_json_equal=result == first_result,
                           result_all_pass=result["summary"]["all_pass"] is True,
                           result_summary=result["summary"], actual_counts=result["summary"]["actual_counts"],
                           actual_count_check=counts_match_protocol(result["summary"]["actual_counts"]))
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            receipt["result_structure_error"] = {"type": type(error).__name__, "message": str(error)}
    all_pass = (returncode == 0 and not timed_out and launch_error is None
                and receipt["result_byte_equal"] and receipt["result_parsed_json_equal"]
                and receipt["result_all_pass"] and receipt["actual_count_check"]["all_pass"]
                and receipt["postexecution_restore"]["all_pass"])
    receipt["status"] = "REPLAY_PASS" if all_pass else "REPLAY_FAIL_PRESERVED"
    receipt["failure_class"] = None if all_pass else (
        "RUNTIME_ENVIRONMENT" if timed_out or launch_error else "IMPLEMENTATION_OR_NUMERICAL_UNRESOLVED")
    write_json(records["receipt"], receipt)
    print(json.dumps({"status": receipt["status"], "actual_exit_code": returncode,
                      "wall_seconds": receipt["wall_seconds"], "runtime_files": 26,
                      "byte_equal": receipt["result_byte_equal"],
                      "parsed_json_equal": receipt["result_parsed_json_equal"],
                      "actual_counts": receipt.get("actual_counts"), "independent_physics_credit": 0}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
