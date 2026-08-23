#!/usr/bin/env python3
"""Bounded TEST_ONLY command capture with canonical external-audit evidence."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import time
from typing import Any, Sequence


CLASSIFICATION = "TEST_ONLY_NOT_SCIENCE"
_SECRET_ARGUMENT = re.compile(
    r"(?i)(?:^|[-_])(?:api[-_]?key|authorization|bearer|password|passwd|secret|token)(?:$|[=: ])"
)
_THREAD_NAMES = (
    "BLIS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


class AuditPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class CaptureResult:
    manifest: dict[str, Any]
    manifest_path: Path
    manifest_sha256: str


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _exclusive_write(path: Path, payload: bytes) -> None:
    with Path(path).open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _validate_command(command: Sequence[str]) -> tuple[str, ...]:
    if isinstance(command, (str, bytes)) or not command:
        raise AuditPolicyError("command must be a nonempty argv sequence")
    argv = tuple(command)
    if not all(isinstance(item, str) and item and "\x00" not in item for item in argv):
        raise AuditPolicyError("argv entries must be nonempty NUL-free strings")
    for item in argv:
        if _SECRET_ARGUMENT.search(item):
            raise AuditPolicyError("secret-like argv is forbidden")
    requested = Path(argv[0])
    if not requested.is_absolute():
        raise AuditPolicyError("executable must be an absolute path")
    try:
        resolved = requested.resolve(strict=True)
    except OSError as error:
        raise AuditPolicyError("executable cannot be resolved") from error
    if requested != resolved:
        raise AuditPolicyError("executable path must already be fully resolved")
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise AuditPolicyError("executable must be an executable regular file")
    return (str(resolved),) + argv[1:]


def _validate_cwd(cwd: Path) -> Path:
    requested = Path(cwd)
    if not requested.is_absolute():
        raise AuditPolicyError("cwd must be absolute")
    try:
        resolved = requested.resolve(strict=True)
    except OSError as error:
        raise AuditPolicyError("cwd cannot be resolved") from error
    if requested != resolved or not resolved.is_dir():
        raise AuditPolicyError("cwd must already be a resolved directory")
    return resolved


def _validate_import_roots(values: Sequence[Path]) -> tuple[Path, ...]:
    if isinstance(values, (str, bytes)):
        raise AuditPolicyError("pythonpath_roots must be a path sequence")
    if len(values) > 4:
        raise AuditPolicyError("at most four explicit import roots are allowed")
    roots = []
    for value in values:
        requested = Path(value)
        if not requested.is_absolute() or os.pathsep in str(requested):
            raise AuditPolicyError("import roots must be absolute and pathsep-free")
        try:
            resolved = requested.resolve(strict=True)
        except OSError as error:
            raise AuditPolicyError("import root cannot be resolved") from error
        if requested != resolved or not resolved.is_dir():
            raise AuditPolicyError("import root must already be a resolved directory")
        roots.append(resolved)
    if len(set(roots)) != len(roots):
        raise AuditPolicyError("duplicate import roots are forbidden")
    return tuple(roots)


def _import_root_identity(root: Path) -> dict[str, Any]:
    root_stat = root.stat()
    entries = []
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        child_stat = child.lstat()
        entries.append(
            {
                "mode": stat.S_IMODE(child_stat.st_mode),
                "name": child.name,
                "size_bytes": child_stat.st_size,
                "type": (
                    "directory"
                    if child.is_dir()
                    else "file"
                    if child.is_file()
                    else "other"
                ),
            }
        )
    return {
        "device": root_stat.st_dev,
        "direct_entry_count": len(entries),
        "direct_listing_sha256": hashlib.sha256(
            canonical_json_bytes(entries)
        ).hexdigest(),
        "inode": root_stat.st_ino,
        "mode": stat.S_IMODE(root_stat.st_mode),
        "path": str(root),
        "scope": "PATH_AND_DIRECT_LISTING_IDENTITY_NOT_CONTENT_SEAL",
    }


def _fresh_environment(tmpdir: Path, import_roots: tuple[Path, ...]) -> dict[str, str]:
    values = {
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": "/usr/bin",
        "TZ": "UTC",
        "PYTHONHASHSEED": "0",
        "PYTHONNOUSERSITE": "1",
        "XLA_FLAGS": "--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1",
        "TMPDIR": str(tmpdir),
    }
    values.update({name: "1" for name in _THREAD_NAMES})
    if import_roots:
        values["PYTHONPATH"] = os.pathsep.join(str(root) for root in import_roots)
    return values


def _run_git(git: Path, cwd: Path, *arguments: str) -> bytes:
    result = subprocess.run(
        [str(git), "-C", str(cwd), *arguments],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        close_fds=True,
    )
    if result.returncode:
        raise AuditPolicyError("git identity query failed")
    return result.stdout


def _git_identity(cwd: Path) -> dict[str, Any]:
    located = shutil.which("git")
    if located is None:
        raise AuditPolicyError("git executable is unavailable")
    git = Path(located).resolve(strict=True)
    root = Path(_run_git(git, cwd, "rev-parse", "--show-toplevel").decode().strip())
    head = _run_git(git, cwd, "rev-parse", "HEAD").decode("ascii").strip()
    tree = _run_git(git, cwd, "rev-parse", "HEAD^{tree}").decode("ascii").strip()
    status_bytes = _run_git(
        git, cwd, "status", "--porcelain=v1", "--untracked-files=all"
    )
    if not re.fullmatch(r"[0-9a-f]{40}", head) or not re.fullmatch(
        r"[0-9a-f]{40}", tree
    ):
        raise AuditPolicyError("git returned a malformed object identity")
    return {
        "head": head,
        "root": str(root.resolve()),
        "status_clean": status_bytes == b"",
        "status_entry_count": len(status_bytes.splitlines()),
        "status_sha256": hashlib.sha256(status_bytes).hexdigest(),
        "tree": tree,
    }


def _kill_process_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def capture_audit_run(
    *,
    command: Sequence[str],
    cwd: Path,
    output_dir: Path,
    timeout_seconds: float,
    max_stdout_bytes: int,
    max_stderr_bytes: int,
    pythonpath_roots: Sequence[Path] = (),
) -> CaptureResult:
    """Run one secret-free test command with bounded incremental capture."""

    argv = _validate_command(command)
    run_cwd = _validate_cwd(Path(cwd))
    import_roots = _validate_import_roots(pythonpath_roots)
    if (
        not isinstance(timeout_seconds, (int, float))
        or isinstance(timeout_seconds, bool)
        or not math.isfinite(float(timeout_seconds))
        or timeout_seconds <= 0
    ):
        raise AuditPolicyError("timeout_seconds must be finite and positive")
    for name, value in (
        ("max_stdout_bytes", max_stdout_bytes),
        ("max_stderr_bytes", max_stderr_bytes),
    ):
        if type(value) is not int or value <= 0:
            raise AuditPolicyError(f"{name} must be a positive integer")

    destination = Path(output_dir)
    if destination.exists():
        raise AuditPolicyError("output_dir already exists")
    destination.mkdir(parents=True, exist_ok=False)
    tmpdir = destination / "tmp"
    tmpdir.mkdir()
    environment = _fresh_environment(tmpdir.resolve(), import_roots)
    stdout_path = destination / "stdout.bin"
    stderr_path = destination / "stderr.bin"

    executable = Path(argv[0])
    executable_stat = executable.stat()
    git = _git_identity(run_cwd)
    started_utc = _utc_now()
    started_ns = time.monotonic_ns()
    termination = "EXITED"
    timed_out = False

    with stdout_path.open("xb") as stdout_file, stderr_path.open("xb") as stderr_file:
        process = subprocess.Popen(
            argv,
            cwd=run_cwd,
            env=environment,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
            start_new_session=True,
        )
        if process.stdout is None or process.stderr is None:
            _kill_process_group(process)
            raise RuntimeError("subprocess pipes were not created")

        stdout_fd = process.stdout.fileno()
        stderr_fd = process.stderr.fileno()
        stream_state = {
            stdout_fd: {
                "pipe": process.stdout,
                "file": stdout_file,
                "hasher": hashlib.sha256(),
                "limit": max_stdout_bytes,
                "size": 0,
                "capped": False,
            },
            stderr_fd: {
                "pipe": process.stderr,
                "file": stderr_file,
                "hasher": hashlib.sha256(),
                "limit": max_stderr_bytes,
                "size": 0,
                "capped": False,
            },
        }
        selector = selectors.DefaultSelector()
        for file_descriptor, state in stream_state.items():
            selector.register(file_descriptor, selectors.EVENT_READ, state)

        killed = False
        while selector.get_map():
            elapsed_seconds = (time.monotonic_ns() - started_ns) / 1_000_000_000
            if not killed and elapsed_seconds >= timeout_seconds:
                timed_out = True
                termination = "TIMEOUT"
                killed = True
                _kill_process_group(process)
            wait = 0.05
            if not killed:
                wait = max(0.0, min(wait, timeout_seconds - elapsed_seconds))
            for key, _mask in selector.select(wait):
                state = key.data
                chunk = os.read(key.fd, 64 * 1024)
                if not chunk:
                    selector.unregister(key.fd)
                    state["pipe"].close()
                    continue
                remaining = state["limit"] - state["size"]
                captured = chunk[: max(0, remaining)]
                if captured:
                    state["file"].write(captured)
                    state["hasher"].update(captured)
                    state["size"] += len(captured)
                if len(chunk) > len(captured):
                    state["capped"] = True
                    if not killed:
                        termination = "OUTPUT_LIMIT"
                        killed = True
                        _kill_process_group(process)

        selector.close()
        returncode = process.wait()
        for state in stream_state.values():
            state["file"].flush()
            os.fsync(state["file"].fileno())

    ended_ns = time.monotonic_ns()
    ended_utc = _utc_now()
    stdout_state = stream_state[stdout_fd]
    stderr_state = stream_state[stderr_fd]
    process_signal = -returncode if returncode < 0 else None
    environment_bytes = canonical_json_bytes(environment)
    runtime_executable = Path(sys.executable).resolve(strict=True)
    runtime = {
        "implementation": platform.python_implementation(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "python_executable": str(runtime_executable),
        "python_executable_sha256": _sha256_file(runtime_executable),
        "python_version": platform.python_version(),
        "system": platform.system(),
    }
    manifest = {
        "classification": CLASSIFICATION,
        "command": {
            "argv": list(argv),
            "argv_sha256": hashlib.sha256(canonical_json_bytes(list(argv))).hexdigest(),
            "cwd": str(run_cwd),
            "executable": {
                "device": executable_stat.st_dev,
                "inode": executable_stat.st_ino,
                "mode": stat.S_IMODE(executable_stat.st_mode),
                "requested": command[0],
                "resolved": str(executable),
                "sha256": _sha256_file(executable),
                "size_bytes": executable_stat.st_size,
            },
            "shell": False,
        },
        "environment": {
            "canonical_sha256": hashlib.sha256(environment_bytes).hexdigest(),
            "explicit_import_roots": [
                _import_root_identity(root) for root in import_roots
            ],
            "inherited_variable_count": 0,
            "policy": "FRESH_EXACT_ALLOWLIST",
            "values": environment,
        },
        "git": git,
        "limits": {
            "max_stderr_bytes": max_stderr_bytes,
            "max_stdout_bytes": max_stdout_bytes,
            "timeout_seconds_hex": float(timeout_seconds).hex(),
        },
        "process": {
            "returncode": returncode,
            "signal": process_signal,
            "termination": termination,
            "timed_out": timed_out,
        },
        "runtime": runtime,
        "schema": "REI_AUDIT_RUN_V1",
        "stderr": {
            "capped": bool(stderr_state["capped"]),
            "complete_until_termination": not stderr_state["capped"],
            "path": "stderr.bin",
            "sha256": stderr_state["hasher"].hexdigest(),
            "size_bytes": stderr_state["size"],
        },
        "stdout": {
            "capped": bool(stdout_state["capped"]),
            "complete_until_termination": not stdout_state["capped"],
            "path": "stdout.bin",
            "sha256": stdout_state["hasher"].hexdigest(),
            "size_bytes": stdout_state["size"],
        },
        "time": {
            "duration_clock": "CLOCK_MONOTONIC",
            "duration_monotonic_ns": ended_ns - started_ns,
            "ended_utc": ended_utc,
            "started_utc": started_utc,
        },
    }
    manifest_payload = canonical_json_bytes(manifest) + b"\n"
    manifest_path = destination / "manifest.json"
    _exclusive_write(manifest_path, manifest_payload)
    manifest_sha256 = hashlib.sha256(manifest_payload).hexdigest()
    _exclusive_write(
        destination / "manifest.json.sha256",
        f"{manifest_sha256}  manifest.json\n".encode("ascii"),
    )
    return CaptureResult(manifest, manifest_path, manifest_sha256)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--timeout-seconds", type=float, required=True)
    parser.add_argument("--max-stdout-bytes", type=int, required=True)
    parser.add_argument("--max-stderr-bytes", type=int, required=True)
    parser.add_argument("--pythonpath-root", action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    arguments = parser.parse_args(argv)
    command = arguments.command
    if command[:1] == ["--"]:
        command = command[1:]
    try:
        result = capture_audit_run(
            command=command,
            cwd=Path(arguments.cwd),
            output_dir=Path(arguments.output_dir),
            timeout_seconds=arguments.timeout_seconds,
            max_stdout_bytes=arguments.max_stdout_bytes,
            max_stderr_bytes=arguments.max_stderr_bytes,
            pythonpath_roots=tuple(Path(item) for item in arguments.pythonpath_root),
        )
    except AuditPolicyError as error:
        print(f"AUDIT_POLICY_ERROR: {error}", file=sys.stderr)
        return 64
    summary = {
        "classification": CLASSIFICATION,
        "manifest": str(result.manifest_path),
        "manifest_sha256": result.manifest_sha256,
        "returncode": result.manifest["process"]["returncode"],
        "termination": result.manifest["process"]["termination"],
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if (
        summary["termination"] == "EXITED" and summary["returncode"] == 0
    ) else 2


if __name__ == "__main__":
    raise SystemExit(main())
