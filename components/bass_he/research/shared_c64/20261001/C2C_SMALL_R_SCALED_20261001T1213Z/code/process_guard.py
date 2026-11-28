"""Linux-only ownership-checked cleanup for independent task sessions.

No global process scan is ever acted on without an exact batch/task token,
session identity, start time and pidfd identity check. The executable wrapper
sets a parent-death SIGKILL before waiting for the parent's registry gate.
"""
from __future__ import annotations
import argparse
import ctypes
import json
import os
from pathlib import Path
import signal
import sys
import time

TASK_TOKEN_ENV = "BASS_TASK_OWNER_TOKEN"
BATCH_TOKEN_ENV = "BASS_BATCH_OWNER_TOKEN"
REGISTRY_NAME = "OWNED_PROCESS.json"


def _identity_from_proc(path):
    """Resolve a procfs entry into our PID namespace, never assume mounts agree.

    This sandbox exposes outer-namespace /proc with inner-namespace syscalls.
    NSpid/NSpgid/NSsid are ordered from procfs mount namespace inward.
    Reject entries in another PID namespace before using the innermost IDs.
    """
    try:
        namespace_inode = (path/"ns/pid").stat().st_ino
        if namespace_inode != Path("/proc/self/ns/pid").stat().st_ino:
            return None
        raw = (path/"stat").read_text()
        status = dict(line.split(":", 1) for line in (path/"status").read_text().splitlines() if ":" in line)
        pid, pgid, session = (int(status[key].split()[-1]) for key in ("NSpid", "NSpgid", "NSsid"))
    except (FileNotFoundError, ProcessLookupError, PermissionError, KeyError):
        return None
    end = raw.rfind(")")
    if end < 0:
        raise RuntimeError("invalid Linux process stat")
    fields = raw[end+2:].split()
    return {"pid": pid, "state": fields[0], "procfs_ppid": int(fields[1]),
            "pgid": pgid, "session": session, "procfs_pid": int(path.name),
            "pid_namespace_inode": namespace_inode,
            "start_time_ticks": int(fields[19])}


def _processes():
    for path in Path("/proc").iterdir():
        if path.name.isdecimal():
            ident = _identity_from_proc(path)
            if ident is not None:
                yield ident


def process_identity(pid):
    return next((ident for ident in _processes() if ident["pid"] == int(pid)), None)


def boot_id():
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()


def registry_record(pid, task_id, task_token, batch_token):
    leader = process_identity(pid)
    if leader is None or leader["pgid"] != pid or leader["session"] != pid:
        raise RuntimeError("task must be a live independent session leader")
    return {"schema": 1, "task_id": task_id, "task_owner_token": task_token,
            "batch_owner_token": batch_token, "boot_id": boot_id(), "leader": leader}


def _has_tokens(ident, task_token, batch_token):
    try:
        data = Path(f"/proc/{ident['procfs_pid']}/environ").read_bytes().split(b"\0")
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return False
    return ((TASK_TOKEN_ENV+"="+task_token).encode() in data and
            (BATCH_TOKEN_ENV+"="+batch_token).encode() in data)


def _matching_processes(record):
    leader = record["leader"]
    matches = []
    for ident in _processes():
        if (ident is not None and ident["state"] != "Z" and
                ident["pgid"] == leader["pgid"] and ident["session"] == leader["session"] and
                ident["start_time_ticks"] >= leader["start_time_ticks"] and
                ident["pid_namespace_inode"] == leader["pid_namespace_inode"] and
                _has_tokens(ident, record["task_owner_token"], record["batch_owner_token"])):
            matches.append(ident)
    return matches


def cleanup_record(record, expected_batch_token, expected_task_id, timeout=2.0, signum=signal.SIGKILL):
    """SIGKILL only verified members through pidfds; never numeric killpg.

    start-time mismatch rejects the entire record before any signal. An exited
    leader may leave descendants; those still require the exact inherited
    tokens, original session and PGID. Every signal uses a pidfd opened before
    a repeated identity/token check, eliminating PID reuse at signal delivery.
    """
    result = {"task_id": expected_task_id, "status": "REJECTED", "signals": [], "remaining": []}
    if (not isinstance(record, dict) or record.get("schema") != 1 or
            record.get("batch_owner_token") != expected_batch_token or
            record.get("task_id") != expected_task_id or not expected_batch_token or
            not isinstance(record.get("task_owner_token"), str) or not record["task_owner_token"] or
            record.get("boot_id") != boot_id()):
        result["reason"] = "REGISTRY_OWNERSHIP_MISMATCH"
        return result
    leader = record.get("leader", {})
    if (not all(type(leader.get(k)) is int and leader[k] > 0 for k in
                ("pid", "pgid", "session", "start_time_ticks", "procfs_pid", "pid_namespace_inode")) or
            leader["pid"] != leader["pgid"] or leader["pid"] != leader["session"]):
        result["reason"] = "INVALID_SESSION_IDENTITY"
        return result
    current = process_identity(leader["pid"])
    if current is not None and any(current[k] != leader[k] for k in
                                   ("pid", "pgid", "session", "start_time_ticks", "procfs_pid", "pid_namespace_inode")):
        result["reason"] = "PID_START_TIME_OR_SESSION_MISMATCH"
        return result
    deadline = time.monotonic() + timeout
    while True:
        matching = _matching_processes(record)
        if not matching:
            result["status"] = "NO_LIVE_OWNED_MEMBERS"
            return result
        for ident in matching:
            pidfd = None
            try:
                pidfd = os.pidfd_open(ident["pid"], 0)
                again = process_identity(ident["pid"])
                if (again is not None and all(again[k] == ident[k] for k in
                      ("pid", "pgid", "session", "start_time_ticks", "procfs_pid", "pid_namespace_inode")) and
                      _has_tokens(ident, record["task_owner_token"], record["batch_owner_token"])):
                    marker = {"pid": ident["pid"], "start_time_ticks": ident["start_time_ticks"], "signal": int(signum)}
                    if marker not in result["signals"]:
                        signal.pidfd_send_signal(pidfd, signum)
                        result["signals"].append(marker)
            except ProcessLookupError:
                pass
            finally:
                if pidfd is not None:
                    os.close(pidfd)
        if time.monotonic() >= deadline:
            result["remaining"] = _matching_processes(record)
            result["status"] = "CLEANUP_INCOMPLETE" if result["remaining"] else "NO_LIVE_OWNED_MEMBERS"
            return result
        time.sleep(0.01)


def cleanup_batch(output_dir, expected_batch_token, task_ids):
    """Read only expected task registry files in one caller-owned batch."""
    root = Path(output_dir)
    reports = []
    if not root.exists():
        return reports
    if root.is_symlink():
        raise RuntimeError("batch directory must not be a symlink")
    for task_id in task_ids:
        if not isinstance(task_id, str) or Path(task_id).name != task_id or task_id in (".", ".."):
            raise ValueError("invalid task ID")
        directory = root / task_id
        registry = directory / REGISTRY_NAME
        if directory.is_symlink() or registry.is_symlink():
            raise RuntimeError("task registry must not use symlinks")
        if registry.exists():
            record = json.loads(registry.read_text())
            reports.append(cleanup_record(record, expected_batch_token, task_id))
    return reports


def parent_death_guard(expected_parent):
    if os.getppid() != expected_parent:
        raise RuntimeError("supervisor exited before parent-death registration")
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
        raise OSError(ctypes.get_errno(), "PR_SET_PDEATHSIG failed")
    if os.getppid() != expected_parent:
        raise RuntimeError("supervisor exited during parent-death registration")
    signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGTERM, signal.SIGINT})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supervisor-pid", required=True, type=int)
    parser.add_argument("--gate-fd", required=True, type=int)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("missing guarded command")
    parent_death_guard(args.supervisor_pid)
    try:
        if os.read(args.gate_fd, 1) != b"1":
            raise RuntimeError("supervisor closed registry gate without registration")
    finally:
        os.close(args.gate_fd)
    if os.getppid() != args.supervisor_pid:
        raise RuntimeError("supervisor exited before task exec")
    os.execvpe(command[0], command, os.environ.copy())


if __name__ == "__main__":
    main()
