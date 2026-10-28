"""One measured attempt for manufactured tests and saved-source calibration.

POSIX only. The authorization JSON is a controller-issued execution decision;
this code does not grant a budget. External whole-command accounting is still
required because interpreter startup precedes this script's first clock.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import sys
import time

START = time.monotonic()
ROOT = Path(__file__).resolve().parent
FILES = ("caloric_branch.py", "test_caloric_branch.py",
         "run_saved_caloric_branch.py", "suite_once.py", "run_once.py")
UNIT = "rei_supplied_caloric_branch_20261028"
PRIOR_PLANNING_LOWER = Decimal("16.350357885")


def cpu_self() -> float:
    u = resource.getrusage(resource.RUSAGE_SELF)
    return u.ru_utime + u.ru_stime


def positive(raw, label: str) -> float:
    if type(raw) is not str:
        raise ValueError(label + " must be explicit decimal string")
    value = Decimal(raw)
    if not value.is_finite() or value <= 0 or not math.isfinite(float(value)):
        raise ValueError(label + " must be finite positive")
    return float(value)


def validate(auth: dict, token: dict, command: list[str], hashes: dict) -> dict:
    if type(auth) is not dict or auth.get("schema") != "REI_CALORIC_BRANCH_RUN_AUTH_V1":
        raise ValueError("separate quantified authorization missing")
    if auth.get("approved") is not True or auth.get("unit") != UNIT or auth.get("mode") != "combined":
        raise ValueError("authorization/unit/mode mismatch")
    if (type(token) is not dict or token.get("schema") != "REI_CALORIC_BRANCH_EXECUTION_APPROVAL_V1"
            or token.get("approved") is not True or token.get("unit") != UNIT
            or token.get("attempt_id") != auth.get("attempt_id")
            or token.get("authority_ref") != auth.get("authority_ref")
            or token.get("approved_absolute_planning_cap_cpu_s") != auth.get("approved_absolute_planning_cap_cpu_s")):
        raise ValueError("explicit approval token absent or inconsistent")
    if auth.get("attempts") != 1 or type(auth.get("attempts")) is not int:
        raise ValueError("exactly one authorized attempt required")
    for field in ("attempt_id", "authority_ref", "accounting_boundary"):
        if type(auth.get(field)) is not str or not auth[field].strip():
            raise ValueError("missing " + field)
    if auth.get("unknown_costs") != "UNKNOWN_NOT_ZERO":
        raise ValueError("unknown historical costs must be preserved")
    if auth.get("worker_command") != command or auth.get("source_sha256") != hashes:
        raise ValueError("worker command or authored file hashes mismatch")
    prior = Decimal(str(auth.get("prior_known_planning_cpu_s", "")))
    cap = Decimal(str(auth.get("approved_absolute_planning_cap_cpu_s", "")))
    limits = auth.get("limits")
    if type(limits) is not dict:
        raise ValueError("limits required")
    attempt = positive(limits.get("attempt_cpu_s"), "attempt CPU")
    worker = positive(limits.get("worker_cpu_s"), "worker CPU")
    reserve = positive(limits.get("final_record_reserve_cpu_s"), "final-record reserve")
    wall = positive(limits.get("wall_s"), "wall")
    memory = limits.get("memory_bytes")
    if type(memory) is not int or memory <= 0:
        raise ValueError("positive memory bytes required")
    if prior < PRIOR_PLANNING_LOWER or prior + Decimal(limits["attempt_cpu_s"]) > cap:
        raise ValueError("prior debit/reset or attempt exceeds newly approved cap")
    if attempt > 1.5 or worker > 1 or worker + reserve >= attempt:
        raise ValueError("combined unit permits at most 1.5 CPU-second, worker at most 1")
    if Decimal(str(token.get("max_attempt_cpu_s", ""))) < Decimal(limits["attempt_cpu_s"]):
        raise ValueError("approval token attempt reservation too small")
    return {"attempt": attempt, "worker": worker, "reserve": reserve,
            "parent": attempt-worker-reserve, "wall": wall, "memory": memory}


def main() -> int:
    if os.name != "posix" or not hasattr(os, "wait4"):
        raise RuntimeError("POSIX wait4 and resource limits required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--approval-token", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    command = [sys.executable, "-B", str(ROOT/"suite_once.py"),
               "--input", str(args.source.resolve()),
               "--output", str(args.output_dir.resolve()/"saved_source_result.json")]
    hashes = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FILES}
    auth_bytes = args.authorization.read_bytes()
    auth = json.loads(auth_bytes)
    token_bytes = args.approval_token.read_bytes()
    token = json.loads(token_bytes)
    limits = validate(auth, token, command, hashes)
    if cpu_self() >= limits["parent"] or time.monotonic()-START >= limits["wall"]:
        raise RuntimeError("prelaunch budget exhausted")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    with args.authorization.with_name(args.authorization.name+".used").open("x", encoding="utf-8") as marker:
        json.dump({"attempt_id": auth["attempt_id"], "authorization_sha256": hashlib.sha256(auth_bytes).hexdigest(),
                   "approval_token_sha256": hashlib.sha256(token_bytes).hexdigest(),
                   "output": str(out)}, marker)
    record = {"unit": UNIT, "mode": "combined", "authorization": auth,
              "approval_token": token,
              "file_sha256": hashes, "worker_command": command,
              "scientific_admission": "NOT_ISSUED", "automatic_retries": 0,
              "child_started": False, "historical_unknown_costs": "UNKNOWN_NOT_ZERO"}
    (out/"STARTED.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    pid = None
    usage = None
    wait_status = None
    stop = None
    stop_kind = None
    try:
        pid = os.fork()
        if pid == 0:
            try:
                os.setsid()
                stdout = os.open(out/"stdout.txt", os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
                stderr = os.open(out/"stderr.txt", os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
                os.dup2(stdout, 1)
                os.dup2(stderr, 2)
                os.close(stdout)
                os.close(stderr)
                resource.setrlimit(resource.RLIMIT_AS, (limits["memory"], limits["memory"]))
                hard = max(1, math.ceil(limits["worker"]))
                resource.setrlimit(resource.RLIMIT_CPU, (hard, hard))
                signal.setitimer(signal.ITIMER_PROF, max(0.001, limits["worker"]-cpu_self()))
                signal.setitimer(signal.ITIMER_REAL, max(0.001, limits["wall"]-(time.monotonic()-START)))
                os.chdir(ROOT)
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1",
                           OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
                os.execve(sys.executable, command, env)
            except BaseException as exc:
                os.write(2, ("WORKER_LAUNCH_FAILED: "+repr(exc)+"\n").encode())
                os._exit(125)
        record["child_started"] = True
        while True:
            got, status, observed = os.wait4(pid, os.WNOHANG)
            if got == pid:
                wait_status, usage = status, observed
                break
            if cpu_self() >= limits["parent"]:
                stop = "SUPERVISOR_CPU_STOP"
                stop_kind = "resource"
                break
            if time.monotonic()-START >= limits["wall"]:
                stop = "WALL_STOP"
                stop_kind = "resource"
                break
            time.sleep(0.01)
    except BaseException as exc:
        stop = type(exc).__name__+": "+str(exc)
        stop_kind = "execution"
    finally:
        if pid is not None and pid > 0 and usage is None:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _, wait_status, usage = os.wait4(pid, 0)
    self_usage = resource.getrusage(resource.RUSAGE_SELF)
    child_cpu = None if usage is None else usage.ru_utime+usage.ru_stime
    parent_cpu = self_usage.ru_utime+self_usage.ru_stime
    exit_code = None if wait_status is None else os.waitstatus_to_exitcode(wait_status)
    observed_overrun = (child_cpu is not None and child_cpu > limits["worker"]
                        or (child_cpu is not None and parent_cpu+child_cpu+limits["reserve"] > limits["attempt"])
                        or time.monotonic()-START > limits["wall"])
    timer_signals = (signal.SIGPROF, signal.SIGXCPU, signal.SIGALRM)
    status = ("RESOURCE_STOP_OR_OVERRUN" if stop_kind == "resource" or observed_overrun else
              "EXECUTION_FAILED" if stop_kind == "execution" else
              "INCOMPLETE_OBSERVATION" if usage is None or exit_code is None else
              "WORKER_RESOURCE_SIGNAL" if exit_code < 0 and -exit_code in timer_signals else
              "EXECUTION_FAILED" if exit_code != 0 else
              "EXECUTION_EXIT_ZERO_NOT_SCIENTIFIC_ADMISSION")
    record.update({"status": status, "stop_reason": stop, "exit_code": exit_code,
                   "stop_kind": stop_kind,
                   "worker_termination_signal": -exit_code if exit_code is not None and exit_code < 0 else None,
                   "raw_wait_status": wait_status, "terminal_usage_observed": usage is not None,
                   "worker_user_s": None if usage is None else usage.ru_utime,
                   "worker_system_s": None if usage is None else usage.ru_stime,
                   "worker_cpu_s": child_cpu, "worker_maxrss_host_units": None if usage is None else usage.ru_maxrss,
                   "worker_minor_faults": None if usage is None else usage.ru_minflt,
                   "worker_major_faults": None if usage is None else usage.ru_majflt,
                   "worker_inblock": None if usage is None else usage.ru_inblock,
                   "worker_oublock": None if usage is None else usage.ru_oublock,
                   "worker_voluntary_switches": None if usage is None else usage.ru_nvcsw,
                   "worker_involuntary_switches": None if usage is None else usage.ru_nivcsw,
                   "supervisor_user_s_pre_record": self_usage.ru_utime,
                   "supervisor_system_s_pre_record": self_usage.ru_stime,
                   "inclusive_cpu_pre_record_s": None if child_cpu is None else parent_cpu+child_cpu,
                   "final_record_reserve_cpu_s": limits["reserve"],
                   "wall_elapsed_pre_record_s": time.monotonic()-START,
                   "exact_whole_command_cpu_s": None,
                   "external_whole_command_accounting": "REQUIRED; do not double-count child CPU",
                   "physical_temperature_interval": None, "actual_native25": None, "physical_radii": None})
    with (out/"RESULT.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return 0 if status == "EXECUTION_EXIT_ZERO_NOT_SCIENTIFIC_ADMISSION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
