#!/usr/bin/env python3
"""Single-node, create-only, wall/memory-bounded manufactured execution launcher."""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import secrets
import signal
import subprocess
import sys
import time
import traceback

from runtime_support import (GIB, ContractError, atomic_create, code_identity, execution_environment,
    file_identity, host_preflight, load_manifest, sha256_file, validate_request)


def reserve_output(path):
    output = Path(path).resolve()
    if output.exists():
        raise FileExistsError(f"create-only output already exists: {output}")
    companion = output.with_name(output.name + ".runtime")
    companion.mkdir(mode=0o700)
    return output, companion


OWNER_ENV = "BASS_C2F_RUNTIME_OWNER_TOKEN"


def process_snapshot():
    """Map procfs PIDs to syscall namespace PIDs before accounting/signaling.

    Adapted from the pinned C2d process_guard identity scheme. This sandbox can
    expose an outer procfs mount; numeric /proc names are not syscall PIDs.
    """
    namespace = Path("/proc/self/ns/pid").stat().st_ino
    result = {}
    for path in Path("/proc").iterdir():
        if not path.name.isdecimal():
            continue
        try:
            if (path/"ns/pid").stat().st_ino != namespace:
                continue
            fields = (path/"stat").read_text().rsplit(")", 1)[1].split()
            status = dict(line.split(":", 1) for line in (path/"status").read_text().splitlines() if ":" in line)
            pid, pgid, sid = (int(status[k].split()[-1]) for k in ("NSpid", "NSpgid", "NSsid"))
            result[int(path.name)] = {"pid": pid, "procfs_pid": int(path.name),
                    "procfs_ppid": int(fields[1]), "pgid": pgid, "sid": sid,
                    "start_time_ticks": int(fields[19]), "namespace_inode": namespace,
                    "state": fields[0], "rss_bytes": max(0, int(fields[21]))*os.sysconf("SC_PAGE_SIZE")}
        except (OSError, ValueError, KeyError, IndexError):
            continue
    return result


def process_key(ident):
    return (ident["namespace_inode"], ident["pid"], ident["procfs_pid"], ident["start_time_ticks"])


class OwnedProcessGuard:
    """Token + ancestry ownership, retained across setsid/reparenting; pidfd kill."""
    def __init__(self, proc, token):
        self.proc, self.token = proc, token
        self.known, self.signals = {}, []
        # Popen's unreaped child cannot have its PID reused at this point.
        self.leader_pidfd = os.pidfd_open(proc.pid, 0)
        self.leader = None
        for ident in process_snapshot().values():
            if ident["pid"] == proc.pid:
                self.leader = ident
                self.known[process_key(ident)] = ident
        if self.leader is None:
            try:
                signal.pidfd_send_signal(self.leader_pidfd, signal.SIGKILL)
            except ProcessLookupError:
                pass
            self.proc.wait(timeout=5.0)
            self.close()
            raise ContractError("launched process identity unavailable in visible procfs")

    def has_token(self, ident):
        try:
            values = Path(f"/proc/{ident['procfs_pid']}/environ").read_bytes().split(b"\0")
            return (OWNER_ENV + "=" + self.token).encode() in values
        except OSError:
            return False

    def observe(self):
        snapshot = process_snapshot()
        owned = {p: ident for p, ident in snapshot.items()
                 if process_key(ident) in self.known or self.has_token(ident)}
        # Discover children even if an exec stripped the inherited token. Known
        # identities remain owned if they subsequently detach or are reparented.
        changed = True
        while changed:
            changed = False
            for p, ident in snapshot.items():
                if p not in owned and ident["procfs_ppid"] in owned:
                    owned[p] = ident
                    changed = True
        for ident in owned.values():
            self.known[process_key(ident)] = ident
        return [ident for ident in owned.values() if ident["state"] != "Z"]

    def signal_owned(self, signum):
        for ident in self.observe():
            fd = None
            try:
                fd = os.pidfd_open(ident["pid"], 0)
                again = process_snapshot().get(ident["procfs_pid"])
                if again is not None and process_key(again) == process_key(ident):
                    signal.pidfd_send_signal(fd, signum)
                    self.signals.append({"pid": ident["pid"], "start_time_ticks": ident["start_time_ticks"], "signal": int(signum)})
            except ProcessLookupError:
                pass
            finally:
                if fd is not None:
                    os.close(fd)

    def stop(self):
        self.signal_owned(signal.SIGTERM)
        deadline = time.monotonic() + 0.5
        while self.observe() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.signal_owned(signal.SIGKILL)
        # pidfd remains bound to our Popen child even if /proc disappeared.
        try:
            signal.pidfd_send_signal(self.leader_pidfd, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self.proc.wait(timeout=5.0)
        deadline = time.monotonic() + 1.0
        while self.observe() and time.monotonic() < deadline:
            self.signal_owned(signal.SIGKILL)
            time.sleep(0.02)
        return {"signals": self.signals, "remaining": self.observe(),
                "observed_processes": list(self.known.values()),
                "ownership": "unique_inherited_token_or_observed_ancestry_retained_by_namespace_pid_start_time",
                "signaling": "pidfd_after_identity_recheck"}

    def close(self):
        if self.leader_pidfd is not None:
            os.close(self.leader_pidfd)
            self.leader_pidfd = None


def monitor_process(proc, guard, wall_seconds, memory_bytes):
    started, peak, termination, cleanup = time.monotonic(), 0, None, None
    while True:
        members = guard.observe()
        rss = sum(ident["rss_bytes"] for ident in members)
        peak = max(peak, rss)
        if time.monotonic() - started >= wall_seconds:
            termination = "WALL_TIMEOUT"
        elif rss > memory_bytes:
            termination = "MEMORY_BUDGET_EXCEEDED"
        if termination:
            cleanup = guard.stop()
            break
        if proc.poll() is not None:
            members = guard.observe()
            if members:
                termination = "OWNED_DESCENDANTS_AFTER_LEADER_EXIT"
                cleanup = guard.stop()
            break
        time.sleep(0.05)
    return {"returncode": proc.wait(), "termination": termination,
            "wall_seconds": time.monotonic()-started, "sampled_owned_rss_peak_bytes": peak,
            "observed_processes": list(guard.known.values()), "cleanup": cleanup,
            "memory_measurement": "sum_owned_process_RSS_sampled_50ms_shared_pages_may_be_overcounted",
            "memory_limit_kind": "sampled_watchdog_not_strict_allocation_or_true_peak_bound"}


def resolve_mpiexec(value, env):
    candidate = shutil.which("mpiexec", path=env.get("PATH")) if value == "auto" else value
    if not candidate:
        raise ContractError("explicit MPI requested but mpiexec is unavailable; no fallback")
    p = Path(candidate).resolve(strict=True)
    if not p.is_file() or not os.access(p, os.X_OK):
        raise ContractError("mpiexec is not an executable regular file")
    probe = subprocess.run([str(p), "--version"], env=env, capture_output=True, text=True, timeout=5, check=False)
    version = (probe.stdout + probe.stderr).strip()
    if probe.returncode != 0 or ("Open MPI" not in version and "OpenRTE" not in version):
        raise ContractError("mpiexec is not identified as Open MPI/OpenRTE")
    return str(p), {"executable": file_identity(p), "version_probe": version}


def execute(args, output, companion):
    original_manifest = file_identity(args.manifest)
    manifest = load_manifest(args.manifest)
    if file_identity(args.manifest) != original_manifest:
        raise ContractError("source manifest changed while being parsed")
    host = host_preflight()
    native = str(Path(args.native_library).resolve(strict=True)) if args.native_library else None
    validate_request(manifest, args.execution, args.backend, native, args.ranks, args.threads, args.binding, host)
    env = execution_environment(args.threads, args.binding)
    env[OWNER_ENV] = secrets.token_hex(32)
    snapshot = companion / "manifest.json"
    atomic_create(snapshot, manifest)
    worker_output = companion / "worker_result.json"
    context_path = companion / "launch_context.json"
    code_dir = Path(__file__).resolve().parent
    context = {"schema": "bass-he.c2f.launch-context.v1", "physical_launch_enabled": False,
               "manifest_original": original_manifest, "manifest": file_identity(snapshot),
               "code": code_identity(code_dir), "native_library_identity": file_identity(native) if native else None,
               "host_preflight": host, "worker_output": str(worker_output),
               "launch": {"execution": args.execution, "backend": args.backend, "native_library": native,
                          "ranks": args.ranks, "threads": args.threads, "binding": args.binding},
               "mpi": None, "serial_affinity_cpus": None}
    prefix = []
    preexec = None
    if args.execution == "mpi":
        mpiexec, context["mpi"] = resolve_mpiexec(args.mpiexec, env)
        prefix = [mpiexec, "-np", str(args.ranks), "--host", f"localhost:{math.floor(host['effective_cpu_budget'])}", "--nooversubscribe"]
        if args.binding == "core":
            prefix += ["--map-by", f"slot:PE={args.threads}", "--bind-to", "core"]
        else:
            prefix += ["--map-by", "slot", "--bind-to", "none"]
    elif args.binding == "core":
        cores = list(host["physical_cores_in_affinity"].values())[:args.threads]
        selected = sorted(cpu for core in cores for cpu in core)
        context["serial_affinity_cpus"] = selected
        def set_affinity():
            os.sched_setaffinity(0, selected)
        preexec = set_affinity
    atomic_create(context_path, context)
    command = prefix + [sys.executable, str(code_dir / "run_manufactured.py"), "--context", str(context_path),
                       "--context-sha256", sha256_file(context_path), "--execution", args.execution,
                       "--backend", args.backend, "--output", str(worker_output)]
    if native:
        command += ["--native-library", native]
    atomic_create(companion / "command.json", {"argv": command, "cwd": str(code_dir),
                 "environment_overrides": {k: env[k] for k in ("OMP_NUM_THREADS", "OMP_DYNAMIC", "OMP_PROC_BIND", "OMP_PLACES", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")}})
    with (companion / "stdout.txt").open("xb") as stdout, (companion / "stderr.txt").open("xb") as stderr:
        proc = subprocess.Popen(command, cwd=code_dir, env=env, stdout=stdout, stderr=stderr,
                                start_new_session=True, preexec_fn=preexec)
        guard = OwnedProcessGuard(proc, env[OWNER_ENV])
        try:
            process = monitor_process(proc, guard, manifest["limits"]["wall_seconds"], manifest["limits"]["memory_gib"]*GIB)
        except BaseException:
            guard.stop()
            raise
        finally:
            guard.close()
            stdout.flush(); os.fsync(stdout.fileno())
            stderr.flush(); os.fsync(stderr.fileno())
    worker = None
    if worker_output.is_file():
        worker = json.loads(worker_output.read_text())
    status = "PASS" if process["returncode"] == 0 and process["termination"] is None and worker and worker.get("status") == "PASS" else "FAIL"
    report = {"schema": "bass-he.c2f.launch-result.v1", "status": status,
              "physical_launch_enabled": False, "evidence_scope": "manufactured_implementation_only",
              "NCP64_actual_scaling": "NOT_CLAIMED", "context": file_identity(context_path),
              "process": process, "worker_result": file_identity(worker_output) if worker else None,
              "worker_status": worker.get("status") if worker else "MISSING",
              "case_count": len(manifest["cases"]), "backend": args.backend, "execution": args.execution,
              "ranks": args.ranks, "threads_per_rank": args.threads, "binding": args.binding,
              "runtime_directory": str(companion), "stdout": file_identity(companion / "stdout.txt"),
              "stderr": file_identity(companion / "stderr.txt")}
    atomic_create(output, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--execution", required=True, choices=("serial", "mpi"))
    parser.add_argument("--backend", required=True, choices=("reference", "native"))
    parser.add_argument("--native-library")
    parser.add_argument("--ranks", required=True, type=int)
    parser.add_argument("--threads", required=True, type=int)
    parser.add_argument("--binding", required=True, choices=("none", "core"))
    parser.add_argument("--mpiexec", default="auto")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        output, companion = reserve_output(args.output)
    except Exception as exc:
        print(f"CREATE_ONLY_OUTPUT_REJECTED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    try:
        report = execute(args, output, companion)
    except (Exception, KeyboardInterrupt) as exc:
        report = {"schema": "bass-he.c2f.launch-result.v1", "status": "FAIL", "stage": "LAUNCH_OR_PREFLIGHT",
                  "physical_launch_enabled": False, "runtime_directory": str(companion),
                  "error": {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}}
        atomic_create(output, report)
    print(json.dumps({"status": report["status"], "output": str(output)}, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
