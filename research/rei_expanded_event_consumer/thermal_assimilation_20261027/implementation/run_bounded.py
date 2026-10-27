"""Single authorized new checker with CPU, wall and address-space bounds.

Execution permission is the controller's separate GO. This wrapper records
the actual invocation and outcome; it does not grant scientific admission.
"""
from __future__ import annotations

import time
WALL_START = time.perf_counter()

import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
UNIT = HERE.parent
MANIFEST = HERE / "PREEXEC_MANIFEST.json"
OUTPUT = HERE / "attempt01"
CHILD_CPU_LIMIT_S = 1.25
WRAPPER_CPU_TIMER_S = .18  # Below the frozen <=.20s wrapper allowance.
WALL_TIMER_S = 7.8        # Leaves initialization margin below the8s cap.
TOTAL_CPU_CAP_S = 1.5
TAIL_RESERVE_S = .02
MEMORY_BYTES = 512 * 1024 * 1024
PRIOR_PLANNING_CPU_S = 12.196274495
VENDOR_COPY_CPU_S = .005487141
child = None
stop_reason = None


class BoundedLimit(RuntimeError):
    pass


def stopped(signum, frame):
    global stop_reason
    stop_reason = "WRAPPER_CPU_LIMIT" if signum == signal.SIGPROF else "WALL_LIMIT"
    if child is not None and child.poll() is None:
        child.kill()
    raise BoundedLimit(stop_reason)


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))


def main():
    global child, stop_reason
    if OUTPUT.exists():
        raise FileExistsError("attempt01 exists; preserve its raw bytes and return to root")
    OUTPUT.mkdir()
    command = [sys.executable, "-B", str(HERE / "check_thermal_join.py")]
    start = {"status": "STARTED_NOT_ADMITTED", "command": command,
        "cwd": str(ROOT), "prior_planning_CPU_s": PRIOR_PLANNING_CPU_S,
        "preserved_vendor_copy_CPU_s": VENDOR_COPY_CPU_S,
        "limits": {"child_profiling_CPU_s": CHILD_CPU_LIMIT_S,
            "wrapper_profiling_CPU_s": WRAPPER_CPU_TIMER_S,
            "combined_CPU_cap_s": TOTAL_CPU_CAP_S, "wall_cap_s": 8.0,
            "wall_timer_s": WALL_TIMER_S, "address_space_MiB": 512,
            "workers": 1, "receipt_tail_reserve_s": TAIL_RESERVE_S},
        "science": "new conditional thermal join only; no old suite, IVP or quadrature"}
    (OUTPUT / "START_RECEIPT.json").write_text(json.dumps(start, indent=2) + "\n")
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    exit_code = None
    failure = None
    stdout_status = None
    check_count = None
    authoring_metadata_cpu = None
    signal.signal(signal.SIGPROF, stopped)
    signal.signal(signal.SIGALRM, stopped)
    try:
        left = WRAPPER_CPU_TIMER_S - time.process_time()
        if left <= 0:
            raise BoundedLimit("WRAPPER_STARTUP_CPU_LIMIT")
        signal.setitimer(signal.ITIMER_PROF, left)
        wall_left = WALL_TIMER_S - (time.perf_counter() - WALL_START)
        if wall_left <= 0:
            raise BoundedLimit("WRAPPER_STARTUP_WALL_LIMIT")
        signal.setitimer(signal.ITIMER_REAL, wall_left)
        manifest = json.loads(MANIFEST.read_text())
        authoring_metadata_cpu = float(manifest["preparation_metadata_process_CPU_s"])
        for entry in manifest["inputs"]:
            source = ROOT / entry["path"]
            if hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError("frozen source/input changed: " + entry["path"])
        environment = os.environ.copy()
        environment.update({
            "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1",
            "BLIS_NUM_THREADS": "1", "GOTO_NUM_THREADS": "1",
            "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1",
        })
        with (OUTPUT / "stdout.json").open("wb") as stdout, (OUTPUT / "stderr.log").open("wb") as stderr:
            child = subprocess.Popen(command, cwd=ROOT, env=environment,
                stdout=stdout, stderr=stderr, preexec_fn=child_limits)
            exit_code = child.wait()
        if exit_code == -signal.SIGPROF:
            stop_reason = "CHILD_PROFILING_CPU_LIMIT"
        elif exit_code in (-signal.SIGXCPU, -signal.SIGKILL):
            stop_reason = "CHILD_OS_LIMIT_OR_KILL"
        try:
            saved_stdout = json.loads((OUTPUT / "stdout.json").read_text())
            stdout_status = saved_stdout.get("status")
            check_count = saved_stdout.get("check_count")
        except (json.JSONDecodeError, OSError) as error:
            failure = {"type": type(error).__name__, "message": str(error),
                       "scope": "raw stdout is preserved; incomplete child output"}
    except Exception as error:
        failure = {"type": type(error).__name__, "message": str(error)}
        if child is not None:
            if child.poll() is None:
                child.kill()
            exit_code = child.wait()
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0.0)
        signal.setitimer(signal.ITIMER_REAL, 0.0)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    wrapper_cpu = time.process_time()  # Includes interpreter/stdlib startup.
    measured_cpu = child_cpu + wrapper_cpu
    charged_cpu = measured_cpu + TAIL_RESERVE_S
    wall = time.perf_counter() - WALL_START
    within_budget = (charged_cpu <= TOTAL_CPU_CAP_S and wall <= 8.0
                     and child_cpu <= CHILD_CPU_LIMIT_S
                     and wrapper_cpu <= .20)
    completed = (exit_code == 0 and stop_reason is None and failure is None
                 and stdout_status == "PASS_PENDING_INDEPENDENT_REVIEW" and within_budget)
    receipt = {**start,
        "status": "COMPLETED_PENDING_INDEPENDENT_REVIEW" if completed else "FAILED_STOP_NO_AUTOMATIC_RETRY",
        "exit_code": exit_code, "stop_reason": stop_reason, "failure": failure,
        "stdout_status": stdout_status, "check_count": check_count,
        "child_CPU_s": child_cpu, "wrapper_CPU_before_receipt_tail_s": wrapper_cpu,
        "measured_combined_CPU_before_receipt_tail_s": measured_cpu,
        "conservative_receipt_tail_reserve_s": TAIL_RESERVE_S,
        "charged_new_CPU_s": charged_cpu,
        "separately_measured_authoring_metadata_CPU_s": authoring_metadata_cpu,
        "planning_known_plus_conservative_tail_CPU_s": (
            PRIOR_PLANNING_CPU_S + VENDOR_COPY_CPU_S + authoring_metadata_cpu + charged_cpu
            if authoring_metadata_cpu is not None else None),
        "temporary_planning_cap_s": 14.9, "restore_original_policy_cap_s": 10.0,
        "unknown_historical_and_unmeasured_work": "UNKNOWN_NOT_ZERO",
        "wall_s_from_wrapper_initialization": wall,
        "child_max_RSS_KiB": after.ru_maxrss, "within_combined_budget": within_budget,
        "measurement": "RUSAGE_CHILDREN delta + wrapper process_time; no /proc parsing",
        "input_manifest": str(MANIFEST.relative_to(ROOT)),
        "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
        "stdout": "stdout.json", "stderr": "stderr.log", "partial_checks": "CHECKS.jsonl",
        "requested_executor_role": "lower-tier mechanical executor",
        "observed_executor": "inherited GPT-6 Astra Pro /root/rei_baseline_intake under capacity recovery",
        "scientific_admission": "PENDING_INDEPENDENT_REVIEW",
        "old_main_campaign": "595.225063/600 CPU s; NO_MORE_IVPs; unchanged",
    }
    (OUTPUT / "RESOURCE_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2), flush=True)
    return 0 if completed else 1


if __name__ == "__main__":
    raise SystemExit(main())
