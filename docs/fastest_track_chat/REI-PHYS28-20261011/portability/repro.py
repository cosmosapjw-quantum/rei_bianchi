#!/usr/bin/env python3
"""Restore the frozen PHYS28 stage and optionally debit one new-program replay.

This is an operational reproducibility check, with independent physics credit 0.
It never calls an inherited PHYS19--27 program and performs no root search.
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


ENTRYPOINT = "contributions/numerics/small_width_sensitivity.py"
FIRST_RESULT = "contributions/numerics/SMALL_WIDTH_FIRST.json"
MANIFEST = "PORTABLE_MANIFEST.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path) -> dict:
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": sha256(data)}


def fresh_write(path: Path, data: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(data)


def safe_relative(name: str) -> None:
    relative = PurePosixPath(name)
    if (not name or name.endswith("/") or "\\" in name
            or relative.is_absolute() or ".." in relative.parts
            or "." in relative.parts or str(relative) != name):
        raise ValueError(f"unsafe or noncanonical archive path: {name!r}")


def validate_archive(archive: Path, expected_sha256: str) -> tuple[dict, dict, dict]:
    raw = archive.read_bytes()
    archive_identity = {"path": str(archive), "bytes": len(raw), "sha256": sha256(raw)}
    if archive_identity["sha256"] != expected_sha256:
        raise ValueError("archive SHA256 differs from explicitly supplied identity")
    with zipfile.ZipFile(archive) as handle:
        names = handle.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP member name")
        for info in handle.infolist():
            safe_relative(info.filename)
            if ((info.external_attr >> 16) & 0o170000) not in (0, 0o100000):
                raise ValueError(f"nonregular ZIP member: {info.filename}")
        manifest = json.loads(handle.read(MANIFEST))
        if manifest["task"] != "REI-PHYS28-20261011":
            raise ValueError("wrong portable task identity")
        if manifest["entrypoint"] != ENTRYPOINT or manifest["first_result"] != FIRST_RESULT:
            raise ValueError("entrypoint or first result is outside the PHYS28 replay contract")
        rows = manifest["files"]
        expected_names = [row["path"] for row in rows] + [MANIFEST]
        if len(expected_names) != len(set(expected_names)) or set(names) != set(expected_names):
            raise ValueError("ZIP members do not exactly match portable manifest")
        payloads = {}
        for row in rows:
            name = row["path"]
            safe_relative(name)
            data = handle.read(name)
            if len(data) != row["bytes"] or sha256(data) != row["sha256"]:
                raise ValueError(f"payload identity mismatch: {name}")
            if row["mode"] != "100644":
                raise ValueError(f"unexpected file mode: {name}")
            payloads[name] = data
        payloads[MANIFEST] = handle.read(MANIFEST)
    return manifest, payloads, archive_identity


def verify_restored(destination: Path, manifest: dict, payloads: dict) -> dict:
    checks = []
    for row in manifest["files"]:
        path = destination / row["path"]
        data = path.read_bytes()
        checks.append({
            "path": row["path"],
            "sha256": sha256(data),
            "bytes": len(data),
            "size_equal": len(data) == row["bytes"],
            "sha256_equal": sha256(data) == row["sha256"],
            "archive_byte_equal": data == payloads[row["path"]],
            "regular_file": path.is_file() and not path.is_symlink(),
            "mode_100644": stat.S_IMODE(path.stat().st_mode) == 0o644,
        })
    actual_names = sorted(path.relative_to(destination).as_posix()
                          for path in destination.rglob("*") if path.is_file())
    expected_names = sorted(payloads)
    all_pass = (actual_names == expected_names and all(
        row["size_equal"] and row["sha256_equal"] and row["archive_byte_equal"]
        and row["regular_file"] and row["mode_100644"] for row in checks)
        and (destination / MANIFEST).read_bytes() == payloads[MANIFEST])
    return {"payload_count": len(checks), "exact_member_set": actual_names == expected_names,
            "manifest_byte_equal": (destination / MANIFEST).read_bytes() == payloads[MANIFEST],
            "all_pass": all_pass, "files": checks}


def verify_dependency_chain(destination: Path, manifest: dict) -> dict:
    frozen_path = "contributions/numerics/PREEXECUTION_FROZEN.json"
    protocol_path = "contributions/numerics/PROTOCOL.json"
    static_path = "contributions/numerics/PREEXECUTION_STATIC.json"
    frozen = json.loads((destination / frozen_path).read_bytes())
    protocol = json.loads((destination / protocol_path).read_bytes())
    archive_rows = {row["path"]: row for row in manifest["files"]}
    frozen_rows = {row["path"]: row for row in frozen["files"]}
    checks = []
    for row in frozen["files"]:
        stored = archive_rows.get(row["path"], {})
        checks.append({"kind": "frozen_identity", "path": row["path"],
                       "pass": all(stored.get(key) == row[key] for key in ("bytes", "sha256"))})
    for row in protocol["inputs"]:
        stored = frozen_rows.get(row["path"], {})
        checks.append({"kind": "protocol_input_identity", "path": row["path"],
                       "pass": all(stored.get(key) == row[key] for key in ("bytes", "sha256"))})
    expected_frozen = {row["path"] for row in protocol["inputs"]}
    expected_frozen.update([ENTRYPOINT, protocol_path, static_path])
    runtime = set(frozen_rows) | {frozen_path}
    all_pass = (len(frozen_rows) == len(frozen["files"])
                and set(frozen_rows) == expected_frozen
                and set(manifest["runtime_files"]) == runtime
                and runtime.issubset(archive_rows)
                and all(row["pass"] for row in checks))
    return {"protocol_input_count": len(protocol["inputs"]),
            "frozen_identity_count": len(frozen_rows), "runtime_file_count": len(runtime),
            "all_pass": all_pass, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--record-prefix", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify-only", action="store_true")
    mode.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    archive = args.archive.resolve()
    destination = args.destination.resolve()
    prefix = args.record_prefix.resolve()
    records = {name: Path(str(prefix) + suffix) for name, suffix in {
        "receipt": "_RECEIPT.json", "stdout": "_STDOUT.txt",
        "stderr": "_STDERR.txt", "result": "_RESULT.json",
        "invocation": "_INVOCATION.json",
    }.items()}
    if prefix.is_relative_to(destination):
        raise ValueError("record prefix must be outside the immutable restored tree")
    if destination.exists():
        raise FileExistsError(f"refusing an existing restore destination: {destination}")
    for path in records.values():
        if path.exists():
            raise FileExistsError(f"refusing an existing record path: {path}")
    manifest, payloads, archive_identity = validate_archive(archive, args.archive_sha256)
    destination.mkdir(parents=True, exist_ok=False)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    for name, data in payloads.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        fresh_write(target, data)
        target.chmod(0o644)
    before = verify_restored(destination, manifest, payloads)
    if not before["all_pass"]:
        raise ValueError("restore verification failed before any science invocation")
    dependency_chain = verify_dependency_chain(destination, manifest)
    if not dependency_chain["all_pass"]:
        raise ValueError("frozen/protocol dependency chain failed before any science invocation")

    receipt = {
        "schema": 1, "task": "REI-PHYS28-20261011", "agent": "/root/phys28_portability",
        "evidence_status": "implementation-verified", "independent_physics_credit": 0,
        "mode": "replay" if args.replay else "verify-only", "created_utc": utc_now(),
        "archive": archive_identity, "destination": str(destination),
        "runner": file_identity(Path(__file__).resolve()), "preexecution_restore": before,
        "preexecution_dependency_chain": dependency_chain,
        "source_or_science_code_edits": 0, "new_program_replay_invocations": 0,
        "old_PHYS19_through_PHYS27_program_invocations": 0, "new_physical_root_searches": 0,
        "environment": {"python_version": sys.version, "python_executable": sys.executable,
                        "platform": platform.platform(), "bytecode_writes": False},
    }
    if args.verify_only:
        receipt["status"] = "VERIFY_ONLY_PASS"
        receipt["postexecution_restore"] = before
        fresh_write(records["receipt"], (json.dumps(receipt, indent=2) + "\n").encode())
        print(json.dumps({"status": receipt["status"], "payload_count": before["payload_count"],
                          "new_program_replay_invocations": 0}))
        return 0

    command = [sys.executable, "-B", str(destination / ENTRYPOINT),
               "--output", str(records["result"])]
    receipt["command"] = command
    receipt["cwd"] = str(destination)
    receipt["timeout_seconds"] = 30
    receipt["started_utc"] = utc_now()
    receipt["replay_attempts_debited"] = 1
    fresh_write(records["invocation"], (json.dumps({
        "task": receipt["task"], "started_utc": receipt["started_utc"],
        "command": command, "cwd": str(destination), "timeout_seconds": 30,
        "replay_attempts_debited": 1, "independent_physics_credit": 0,
        "archive_sha256": archive_identity["sha256"], "automatic_retry": False,
    }, indent=2) + "\n").encode())
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started_wall = time.perf_counter()
    timed_out = False
    launch_error = None
    returncode = None
    with records["stdout"].open("xb") as stdout, records["stderr"].open("xb") as stderr:
        try:
            completed = subprocess.run(command, cwd=destination, env=environment,
                                       stdout=stdout, stderr=stderr, timeout=30, check=False)
            returncode = completed.returncode
            receipt["new_program_replay_invocations"] = 1
        except subprocess.TimeoutExpired:
            timed_out = True
            receipt["new_program_replay_invocations"] = 1
        except OSError as error:
            launch_error = {"type": type(error).__name__, "message": str(error)}
    receipt["wall_seconds"] = time.perf_counter() - started_wall
    receipt["ended_utc"] = utc_now()
    receipt["actual_exit_code"] = returncode
    receipt["timed_out"] = timed_out
    receipt["launch_error"] = launch_error
    receipt["stdout"] = file_identity(records["stdout"])
    receipt["stderr"] = file_identity(records["stderr"])
    receipt["postexecution_restore"] = verify_restored(destination, manifest, payloads)
    receipt["first_result"] = file_identity(destination / FIRST_RESULT)
    receipt["result_exists"] = records["result"].is_file()
    receipt["result_byte_equal"] = False
    receipt["result_parsed_json_equal"] = False
    receipt["result_all_pass"] = False
    if receipt["result_exists"]:
        result_bytes = records["result"].read_bytes()
        receipt["result"] = file_identity(records["result"])
        receipt["result_byte_equal"] = result_bytes == payloads[FIRST_RESULT]
        try:
            result = json.loads(result_bytes)
            first = json.loads(payloads[FIRST_RESULT])
            receipt["result_parsed_json_equal"] = result == first
            receipt["result_all_pass"] = result["summary"]["all_pass"] is True
            receipt["actual_counts"] = result["summary"]["actual_counts"]
            receipt["result_summary"] = result["summary"]
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            receipt["result_structure_error"] = {"type": type(error).__name__, "message": str(error)}
    all_pass = (returncode == 0 and not timed_out and receipt["result_byte_equal"]
                and receipt["result_parsed_json_equal"] and receipt["result_all_pass"]
                and receipt["postexecution_restore"]["all_pass"])
    receipt["status"] = "REPLAY_PASS" if all_pass else "REPLAY_FAIL_PRESERVED"
    receipt["failure_class"] = None if all_pass else (
        "RUNTIME_ENVIRONMENT" if timed_out or launch_error else "IMPLEMENTATION_OR_NUMERICAL_UNRESOLVED")
    fresh_write(records["receipt"], (json.dumps(receipt, indent=2) + "\n").encode())
    print(json.dumps({"status": receipt["status"], "actual_exit_code": returncode,
                      "wall_seconds": receipt["wall_seconds"],
                      "payload_count": before["payload_count"],
                      "byte_equal": receipt["result_byte_equal"],
                      "parsed_json_equal": receipt["result_parsed_json_equal"],
                      "actual_counts": receipt.get("actual_counts"),
                      "independent_physics_credit": 0}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
