#!/usr/bin/env python3
"""Fixed PHYS71 D3 runner. Default is read-only input/hash preflight.

Use --run for a bounded worker; --max-new-panels 1 produces one new pilot
panel. Resume reuses all valid saved panels. Completed --resume validates
and returns before any child process, directory, lock, or receipt is created.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import signal
import socket
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/"src"))

from wu088_hh.phys71_campaign import (create_json, inspect_saved, prepare_campaign,
                                     read, run_campaign)
from wu088_hh.phys71_d3 import D3Request
from wu088_hh.phys71_inherit import BAND_ARCHIVE, LOW_ARCHIVE


THREAD_ENV = {key: "1" for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
              "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
              "NUMEXPR_NUM_THREADS", "RAYON_NUM_THREADS")}


def validate_limits(timeout, memory_gib, cpu_seconds, nice):
    for value, lo, hi, name in ((timeout, 1, 86400, "timeout"),
                               (memory_gib, 1, 128, "memory_gib"),
                               (cpu_seconds, 1, 86400, "cpu_seconds"),
                               (nice, 0, 19, "nice")):
        if type(value) is not int or not lo <= value <= hi:
            raise ValueError(f"{name} must be an exact integer in {lo}..{hi}")
    if os.name != "posix":
        raise ValueError("the bounded --run worker requires POSIX process groups and resource limits")


def run_child(command, logs, *, timeout=900, memory_gib=4, cpu_seconds=900, nice=10):
    """Capture one owned process group with wall/CPU/address-space limits."""
    validate_limits(timeout, memory_gib, cpu_seconds, nice)
    import resource
    directory = Path(logs)
    directory.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env.update(THREAD_ENV)
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    requested_memory = memory_gib*1024**3
    inherited_memory_hard = resource.getrlimit(resource.RLIMIT_AS)[1]
    memory_bound = (requested_memory if inherited_memory_hard == resource.RLIM_INFINITY
                    else min(requested_memory, inherited_memory_hard))
    inherited_cpu_hard = resource.getrlimit(resource.RLIMIT_CPU)[1]
    cpu_bound = (cpu_seconds if inherited_cpu_hard == resource.RLIM_INFINITY
                 else min(cpu_seconds, inherited_cpu_hard))
    def constrain():
        resource.setrlimit(resource.RLIMIT_AS, (memory_bound, memory_bound))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_bound, cpu_bound))
        current = os.getpriority(os.PRIO_PROCESS, 0)
        if current < nice:
            os.nice(nice-current)

    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    timed_out = False
    with (directory/"STDOUT.jsonl").open("xb") as stdout, (directory/"STDERR.txt").open("xb") as stderr:
        child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env,
                                 start_new_session=True, preexec_fn=constrain)
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                code = child.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
            # The direct child can exit on TERM while an owned descendant ignores
            # it. Always kill the remaining group, even after a successful wait.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            code = child.wait()
    receipt = {"schema": "PHYS71_BOUNDED_CHILD_RECEIPT_V1", "command": list(command),
               "hostname": socket.gethostname(), "platform": platform.platform(),
               "started_utc": started_utc, "finished_utc": datetime.now(timezone.utc).isoformat(),
               "elapsed_seconds": time.monotonic()-started, "child_pid": child.pid,
               "exit_code": code, "timed_out": timed_out, "wall_seconds_limit": timeout,
               "address_space_bytes_limit": memory_bound, "cpu_seconds_limit": cpu_bound,
               "minimum_nice": nice, "thread_environment": THREAD_ENV,
               "python_bytecode_writes_disabled": True,
               "process_group_owned": True, "HH_R10": "OFF"}
    create_json(directory/"CHILD_RECEIPT.json", receipt)
    return receipt


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--out", type=Path, default=ROOT/"runs/phys71_d3")
    result.add_argument("--low-archive", type=Path, default=ROOT/LOW_ARCHIVE)
    result.add_argument("--band-archive", type=Path, default=ROOT/BAND_ARCHIVE)
    result.add_argument("--request", type=Path)
    result.add_argument("--run", action="store_true")
    result.add_argument("--resume", action="store_true")
    result.add_argument("--max-new-panels", type=int)
    result.add_argument("--timeout", type=int, default=900)
    result.add_argument("--memory-gib", type=int, default=4)
    result.add_argument("--cpu-seconds", type=int)
    result.add_argument("--nice", type=int, default=10)
    result.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    return result


def main(argv=None):
    import json
    args = parser().parse_args(argv)
    cpu = args.cpu_seconds if args.cpu_seconds is not None else args.timeout
    validate_limits(args.timeout, args.memory_gib, cpu, args.nice)
    if args.worker and not args.run:
        raise ValueError("internal worker requires --run")
    if args.max_new_panels is not None and not 0 <= args.max_new_panels <= 76:
        raise ValueError("max-new-panels must be in 0..76")
    request = D3Request(**read(args.request)).validate() if args.request else D3Request()
    prepared = prepare_campaign(ROOT, low_archive=args.low_archive,
                                band_archive=args.band_archive, request=request)
    saved = inspect_saved(prepared, args.out)
    if saved["exists"] and not args.resume:
        raise FileExistsError("existing bound campaign: use --resume")
    if saved["certificate"] is not None:
        result = run_campaign(prepared, args.out, resume=True)
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0 if result["record"]["absolute_goal_met"] else 2
    if not args.run or args.max_new_panels == 0:
        print(json.dumps({"schema": "PHYS71_READONLY_PREFLIGHT_V1", "status": "PREFLIGHT_ONLY_PASS",
              "fingerprint": prepared.fingerprint, "saved_new_D3_panels": len(saved["panels"]),
              "inherited_payloads_verified": 152, "new_D3_panels": 0,
              "Coulomb_evaluations": 0, "new_files": 0, "subprocesses": 0,
              "mathematical_zero_free_probe_performed": False, "HH_R10": "OFF"}, sort_keys=True), flush=True)
        return 0
    if args.worker:
        result = run_campaign(prepared, args.out, resume=args.resume,
                              max_new_panels=args.max_new_panels,
                              progress=lambda event: print(json.dumps(event, sort_keys=True), flush=True))
        print(json.dumps(result, sort_keys=True), flush=True)
        return 2 if result["record"].get("absolute_goal_met") is False else 0
    command = [sys.executable, str(Path(__file__).resolve()), "--worker", "--run",
               "--out", str(args.out.resolve()), "--low-archive", str(args.low_archive.resolve()),
               "--band-archive", str(args.band_archive.resolve()), "--timeout", str(args.timeout),
               "--memory-gib", str(args.memory_gib), "--cpu-seconds", str(cpu), "--nice", str(args.nice)]
    if args.request:
        command += ["--request", str(args.request.resolve())]
    if args.resume:
        command.append("--resume")
    if args.max_new_panels is not None:
        command += ["--max-new-panels", str(args.max_new_panels)]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+"_"+uuid.uuid4().hex[:8]
    logs = args.out.parent/(args.out.name+"_invocations")/stamp
    receipt = run_child(command, logs, timeout=args.timeout, memory_gib=args.memory_gib,
                        cpu_seconds=cpu, nice=args.nice)
    observed = inspect_saved(prepared, args.out)
    print(json.dumps({"child_receipt": receipt, "logs": str(logs),
                      "observed_saved_panels": len(observed["panels"]),
                      "observed_certificate_status": (observed["certificate"] or {}).get("status"),
                      "HH_R10": "OFF"}, sort_keys=True), flush=True)
    return receipt["exit_code"] if receipt["exit_code"] >= 0 else 128-receipt["exit_code"]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"PHYS71_ERROR {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1)
