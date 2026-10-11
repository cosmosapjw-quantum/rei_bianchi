#!/usr/bin/env python3
"""PHYS30: one explicitly admitted separate-path replay, no implicit retry.

This controller does not import the candidate or evaluate physical quantities.
The owner must first complete the sole initial run and supply an admission JSON
whose identities bind that actual result, execution receipt and runtime freeze.
An admission document records the owner's explicit GO; it does not create it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "portability"
TASK = "REI-PHYS30-20261011"
LOCK = OUT / "REPLAY_ATTEMPT_LOCK.json"
RECEIPT = OUT / "REPLAY_RECEIPT.json"
ARCHIVE = OUT / "PHYS30_PORTABLE_STAGE.zip"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def new_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(name: str) -> str:
    require(isinstance(name, str) and bool(name), "missing relative file name")
    require("\\" not in name and "\x00" not in name, "unsafe file name")
    path = PurePosixPath(name)
    require(not path.is_absolute(), "absolute archive/runtime member")
    require(all(part not in ("", ".", "..") for part in path.parts),
            "traversal or empty archive/runtime member")
    require(path.as_posix() == name, "noncanonical relative file name")
    return name


def mode_value(value: str) -> int:
    require(value in ("0644", "0755"), "unexpected frozen mode")
    return int(value, 8)


def identity(path: Path) -> dict:
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode), f"not a regular file: {path}")
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha(data),
            "mode": format(stat.S_IMODE(info.st_mode), "04o")}


def bound_file(root: Path, row: dict) -> tuple[Path, dict]:
    name = relative(row["path"])
    path = root / name
    require(path.resolve(strict=True) == path.absolute(),
            f"symlink or unresolved runtime path: {name}")
    mode_value(row["mode"])
    actual = identity(path)
    require(all(actual[key] == row[key] for key in ("bytes", "sha256", "mode")),
            f"file identity mismatch: {name}")
    return path, {"path": name, **actual, "matches": True}


def field(obj: object, dotted: str) -> object:
    value = obj
    for name in dotted.split("."):
        value = value[name]
    return value


def restored_check(runtime: Path, rows: list[dict], manifest_data: bytes,
                   manifest_name: str, manifest_mode: str) -> dict:
    expected = {row["path"] for row in rows} | {manifest_name}
    actual = set()
    for path in runtime.rglob("*"):
        info = path.lstat()
        require(not stat.S_ISLNK(info.st_mode), "restored tree contains symlink")
        if stat.S_ISREG(info.st_mode):
            actual.add(path.relative_to(runtime).as_posix())
        else:
            require(stat.S_ISDIR(info.st_mode), "restored tree has nonregular member")
    require(actual == expected, "restored exact file member set differs")
    checks = []
    for row in rows:
        path, check = bound_file(runtime, row)
        source = ROOT / row["path"]
        check["matches_source_bytes"] = path.read_bytes() == source.read_bytes()
        require(check["matches_source_bytes"], "restored file differs from source")
        checks.append(check)
    manifest = runtime / manifest_name
    require(manifest.read_bytes() == manifest_data, "restored manifest bytes differ")
    require(identity(manifest)["mode"] == manifest_mode, "restored manifest mode differs")
    return {"status": "EXACT_MEMBERS_BYTES_SHA256_MODES_PASS",
            "file_count": len(actual), "runtime_payload_count": len(rows),
            "exact_member_set": True, "runtime_files": checks,
            "manifest": {"path": manifest_name, **identity(manifest)}}


def run(admission_path: Path) -> int:
    require(not LOCK.exists(), "replay was already reserved; no automatic retry")
    require(not RECEIPT.exists(), "a replay receipt already exists")
    require(not ARCHIVE.exists(), "portable stage archive already exists")
    require(not (OUT / "raw").exists(), "retained raw replay evidence already exists")
    admission_data = admission_path.read_bytes()
    admission = json.loads(admission_data)
    require(admission["task"] == TASK, "wrong task admission")
    require(admission["authorization"] == "ROOT_EXPLICIT_SINGLE_REPLAY_GO",
            "explicit root replay GO is not recorded")
    require(bool(admission["root_go_message"]), "missing root GO provenance")
    require(admission["timeout_seconds"] == 30, "timeout must be frozen at 30 s")
    require(identity(Path(__file__).resolve())["sha256"] == admission["controller_sha256"],
            "controller differs from the owner's admitted identity")
    new_json(LOCK, {"task": TASK, "status": "ONE_REPLAY_RESERVED_NO_RETRY",
                   "created_utc": utc(), "admission_path": str(admission_path),
                   "admission_sha256": sha(admission_data),
                   "note": "Reservation is not proof of subprocess execution."})
    receipt = {"schema": 1, "task": TASK, "agent": "/root/phys30_portability",
               "created_utc": utc(), "status": "INCOMPLETE",
               "evidence_status": "implementation-verified only if actual replay passes",
               "independent_physics_credit": 0,
               "same_host_python_limitation": True,
               "new_program_replay_invocations": 0,
               "subprocess_launch_attempts": 0,
               "new_physical_kernel_or_derivative_evaluations": 0,
               "new_physical_roots": 0,
               "old_PHYS19_through_PHYS29_program_import_or_main": 0,
               "automatic_retry": False,
               "admission": {"path": str(admission_path), **identity(admission_path)},
               "controller": {"path": str(Path(__file__).resolve()),
                              **identity(Path(__file__).resolve())},
               "environment": {"python_executable": sys.executable,
                               "python_version": sys.version,
                               "platform": platform.platform(),
                               "hostname": platform.node(),
                               "environment_overrides": {"PYTHONDONTWRITEBYTECODE": "1"}},
               "timeout_seconds": 30}
    phase = "preexecution_identity_and_restore"
    try:
        manifest_path, manifest_identity = bound_file(ROOT, admission["runtime_manifest"])
        manifest_data = manifest_path.read_bytes()
        freeze = json.loads(manifest_data)
        require(freeze["task"] == TASK, "wrong task runtime manifest")
        rows = freeze["files"]
        manifest_name = relative(admission["runtime_manifest"]["path"])
        require(isinstance(rows, list) and rows, "empty runtime closure")
        names = [relative(row["path"]) for row in rows]
        require(len(names) == len(set(names)), "duplicate runtime member")
        require(len(rows) == freeze["file_count"], "runtime file count mismatch")
        require(manifest_name not in names,
                "self-referential freeze is not allowed")
        entrypoint = relative(freeze["entrypoint"])
        require(entrypoint == "contributions/numerics/profile_second_order.py",
                "unexpected PHYS30 entrypoint")
        require(entrypoint in names, "entrypoint outside runtime freeze")
        require([name for name in names if name.endswith(".py")] == [entrypoint],
                "runtime closure may contain only the new candidate Python program")
        source_before = [bound_file(ROOT, row)[1] for row in rows]
        first_execution_path, execution_identity = bound_file(ROOT, admission["first_execution"])
        first_execution = json.loads(first_execution_path.read_bytes())
        assertions = admission["first_execution_assertions"]
        require(isinstance(assertions, dict) and bool(assertions),
                "actual first execution success assertions are missing")
        require(all(field(first_execution, key) == expected
                    for key, expected in assertions.items()),
                "first execution receipt does not show the supplied success conditions")
        first_output_path, first_identity = bound_file(ROOT, admission["first_output"])
        first_bytes = first_output_path.read_bytes()
        first = json.loads(first_bytes)
        require(first["summary"]["all_pass"] is True, "first science main did not pass")
        require(first["summary"] == admission["expected_summary"], "first summary mismatch")
        require(first["actual_counts"] == admission["expected_actual_counts"],
                "first actual counts differ from owner admission")
        fresh = Path(admission["fresh_root"])
        require(fresh.is_absolute() and fresh == fresh.resolve(),
                "fresh replay root must be an absolute canonical path")
        require(fresh.parent == ROOT.parent and fresh != ROOT,
                "fresh replay root must be a separate sibling of the candidate root")
        require(not fresh.exists(), "fresh replay root already exists; no replacement")
        fresh.mkdir(mode=0o755, exist_ok=False)
        runtime = fresh / "runtime"
        runtime.mkdir(mode=0o755, exist_ok=False)
        run_dir = fresh / "run"
        run_dir.mkdir(mode=0o755, exist_ok=False)
        output_name = relative(admission["output_name"])
        require("/" not in output_name and output_name.endswith(".json"),
                "replay output must be one JSON filename")
        replay_output = run_dir / output_name
        members = [(row["path"], (ROOT / row["path"]).read_bytes(), row["mode"])
                   for row in rows]
        members.append((manifest_name, manifest_data, admission["runtime_manifest"]["mode"]))
        with zipfile.ZipFile(ARCHIVE, "x", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, strict_timestamps=True) as archive:
            for name, data, mode in sorted(members):
                info = zipfile.ZipInfo(name, date_time=(2026, 10, 11, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | mode_value(mode)) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED,
                                 compresslevel=9)
        expected_members = {name: (data, mode) for name, data, mode in members}
        archive_checks = []
        with zipfile.ZipFile(ARCHIVE, "r") as archive:
            infos = archive.infolist()
            require(len(infos) == len(expected_members), "archive has duplicate or extra members")
            require({info.filename for info in infos} == set(expected_members),
                    "archive exact member set differs")
            for info in infos:
                name = relative(info.filename)
                data, mode = expected_members[name]
                archived_mode = info.external_attr >> 16
                require(stat.S_ISREG(archived_mode), "archive member is not regular")
                require(stat.S_IMODE(archived_mode) == mode_value(mode), "archive mode mismatch")
                actual_data = archive.read(info)
                require(actual_data == data, "archive byte mismatch")
                target = runtime / name
                target.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(actual_data)
                target.chmod(mode_value(mode))
                archive_checks.append({"path": name, "bytes": len(actual_data),
                                       "sha256": sha(actual_data), "mode": mode,
                                       "bytes_match": True})
        receipt.update({"runtime_manifest": manifest_identity,
                        "first_execution": execution_identity,
                        "first_execution_assertions": assertions,
                        "first_result": first_identity,
                        "first_summary": first["summary"],
                        "first_actual_counts": first["actual_counts"],
                        "source_before": source_before,
                        "archive": {"path": str(ARCHIVE), **identity(ARCHIVE),
                                    "entry_count": len(members), "members": archive_checks},
                        "destination": str(fresh), "runtime": str(runtime),
                        "run_directory": str(run_dir)})
        receipt["preexecution_restore"] = restored_check(
            runtime, rows, manifest_data, manifest_name, admission["runtime_manifest"]["mode"])
        command = [sys.executable, "-B", entrypoint, "--output", str(replay_output)]
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        receipt.update({"command": command, "cwd": str(runtime), "started_utc": utc(),
                        "replay_attempts_debited": 1, "timed_out": False,
                        "actual_exit_code": None, "launch_error": None})
        phase = "single_subprocess_replay"
        started = time.perf_counter()
        stdout = b""
        stderr = b""
        try:
            receipt["subprocess_launch_attempts"] = 1
            completed = subprocess.run(command, cwd=runtime, env=env, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       timeout=30, check=False)
            stdout, stderr = completed.stdout, completed.stderr
            receipt["new_program_replay_invocations"] = 1
            receipt["actual_exit_code"] = completed.returncode
        except subprocess.TimeoutExpired as error:
            receipt["new_program_replay_invocations"] = 1
            receipt["timed_out"] = True
            stdout, stderr = error.stdout or b"", error.stderr or b""
        except OSError as error:
            receipt["launch_error"] = repr(error)
        finally:
            receipt["ended_utc"] = utc()
            receipt["wall_seconds"] = time.perf_counter() - started
            for name, data in (("replay.stdout.txt", stdout), ("replay.stderr.txt", stderr)):
                log = run_dir / name
                with log.open("xb") as stream:
                    stream.write(data)
                receipt["stdout" if name.startswith("replay.stdout") else "stderr"] = {
                    "path": str(log), **identity(log)}
        retained = OUT / "raw"
        retained.mkdir(mode=0o755, exist_ok=False)
        retained_rows = []
        for path in sorted(run_dir.iterdir()):
            require(path.is_file() and not path.is_symlink(), "unexpected run-directory object")
            copy = retained / path.name
            with copy.open("xb") as stream:
                stream.write(path.read_bytes())
            copy.chmod(stat.S_IMODE(path.stat().st_mode))
            require(identity(copy) == identity(path), "retained replay evidence differs")
            retained_rows.append({"original_path": str(path),
                                  "retained_path": str(copy.relative_to(ROOT)), **identity(copy)})
        receipt["retained_raw_evidence"] = retained_rows
        phase = "postexecution_identity_and_comparison"
        receipt["postexecution_restore"] = restored_check(
            runtime, rows, manifest_data, manifest_name, admission["runtime_manifest"]["mode"])
        receipt["source_after"] = [bound_file(ROOT, row)[1] for row in rows]
        receipt["runtime_manifest_after"] = bound_file(ROOT, admission["runtime_manifest"])[1]
        receipt["result_exists"] = replay_output.is_file()
        if replay_output.is_file():
            replay_bytes = replay_output.read_bytes()
            receipt["result"] = {"path": str(replay_output), **identity(replay_output)}
            receipt["result_byte_equal"] = replay_bytes == first_bytes
            replay = json.loads(replay_bytes)
            receipt["result_parsed_json_equal"] = replay == first
            receipt["result_summary"] = replay.get("summary")
            receipt["actual_counts"] = replay.get("actual_counts")
            receipt["result_all_pass"] = replay.get("summary", {}).get("all_pass") is True
            receipt["actual_count_check"] = replay.get("actual_counts") == admission["expected_actual_counts"]
        else:
            receipt.update({"result_byte_equal": False, "result_parsed_json_equal": False,
                            "result_all_pass": False, "actual_count_check": False})
        passed = (receipt["actual_exit_code"] == 0 and not receipt["timed_out"]
                  and receipt["launch_error"] is None and receipt["result_byte_equal"]
                  and receipt["result_parsed_json_equal"] and receipt["result_all_pass"]
                  and receipt["actual_count_check"])
        receipt["status"] = "REPLAY_PASS" if passed else "REPLAY_FAIL"
        receipt["failure_class"] = None if passed else (
            "RUNTIME_ENVIRONMENT" if receipt["timed_out"] or receipt["launch_error"]
            else "OBSERVED_REPLAY_FAILURE_CAUSE_NOT_YET_CLASSIFIED")
        receipt["evidence_status"] = "implementation-verified" if passed else "unresolved"
    except Exception as error:
        receipt.update({"status": "REPLAY_FAIL", "failure_phase": phase,
                        "failure_class": "RUNTIME_OR_IDENTITY_FAILURE",
                        "observed_failure": repr(error),
                        "traceback": traceback.format_exc(),
                        "evidence_status": "unresolved"})
    finally:
        receipt["receipt_closed_utc"] = utc()
        new_json(RECEIPT, receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(RECEIPT),
                      "new_program_replay_invocations": receipt["new_program_replay_invocations"],
                      "result_byte_equal": receipt.get("result_byte_equal"),
                      "result_parsed_json_equal": receipt.get("result_parsed_json_equal")},
                     sort_keys=True))
    return 0 if receipt["status"] == "REPLAY_PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission", type=Path, required=True)
    arguments = parser.parse_args()
    raise SystemExit(run(arguments.admission.resolve(strict=True)))
