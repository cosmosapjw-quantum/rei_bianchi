"""One separately budgeted presentation job from saved JSON only."""
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

UNIT = Path(__file__).resolve().parents[1]
HERE = UNIT / "delivery"
ATTEMPT = HERE / "presentation_attempt01"
SCRIPT = HERE / "make_figure.py"
SOURCE = UNIT / "implementation/attempt01/stdout.json"
# Exact source digest is the executed attempt01 stdout, not an operator import.
SOURCE_SHA256 = "3f6e942336cb18cf1422ce4736984fb5d7f7d85ca1af39aa0f126748a0c66d99"
PRIOR_PARTS = {"inherited": 30.360058297, "R1_pack": .007053707,
               "preexecution_pack": .040968386, "C5_pack": .049747055}
TAIL_RESERVE = .03
child = None
stop_reason = None


def stop(signum, frame):
    global stop_reason
    stop_reason = "PRESENTATION_WRAPPER_CPU" if signum == signal.SIGPROF else "PRESENTATION_WALL"
    if child is not None and child.poll() is None:
        child.kill()
    raise RuntimeError(stop_reason)


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (4, 4))


def main():
    global child, stop_reason
    if ATTEMPT.exists() or (HERE / "PRESENTATION_RECEIPT.json").exists():
        raise FileExistsError("presentation attempt already exists; no automatic rerender")
    ATTEMPT.mkdir()
    command = [sys.executable, "-B", str(SCRIPT)]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    failure, exit_code, output = None, None, None
    identities = []
    signal.signal(signal.SIGPROF, stop)
    signal.signal(signal.SIGALRM, stop)
    try:
        if time.process_time() >= .18:
            raise RuntimeError("presentation wrapper startup CPU exhausted")
        signal.setitimer(signal.ITIMER_PROF, .18 - time.process_time())
        signal.setitimer(signal.ITIMER_REAL, max(.001, 14.8 - (time.perf_counter() - WALL_START)))
        if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
            raise ValueError("saved source identity mismatch")
        environment = os.environ.copy()
        environment.update({"OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1",
            "BLIS_NUM_THREADS": "1", "GOTO_NUM_THREADS": "1", "PYTHONHASHSEED": "0",
            "PYTHONDONTWRITEBYTECODE": "1", "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": "/tmp/rei_thermal_assimilation_20261027_matplotlib"})
        with (ATTEMPT / "stdout.json").open("wb") as out, (ATTEMPT / "stderr.log").open("wb") as err:
            child = subprocess.Popen(command, cwd=UNIT, env=environment, stdout=out, stderr=err,
                                     preexec_fn=child_limits)
            exit_code = child.wait()
        if exit_code == -signal.SIGPROF:
            stop_reason = "PRESENTATION_CHILD_CPU"
        output = json.loads((ATTEMPT / "stdout.json").read_text())
        for relative in output["outputs"]:
            data = (UNIT / relative).read_bytes()
            identities.append({"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    except Exception as error:
        failure = {"type": type(error).__name__, "message": str(error)}
        if child is not None:
            if child.poll() is None:
                child.kill()
            exit_code = child.wait()
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.setitimer(signal.ITIMER_REAL, 0)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    wrapper_cpu = time.process_time()
    charged = child_cpu + wrapper_cpu + TAIL_RESERVE
    wall = time.perf_counter() - WALL_START
    good = (exit_code == 0 and failure is None and stop_reason is None and charged <= 4.0
            and child_cpu <= 3.5 and wrapper_cpu <= .20 and wall <= 15)
    receipt = {"status": "PRESENTATION_COMPLETE_PENDING_VISUAL_REVIEW" if good else "FAILED_STOP_NO_AUTOMATIC_RERENDER",
        "command": command, "cwd": str(UNIT), "exit_code": exit_code, "failure": failure,
        "stop_reason": stop_reason, "source_path": str(SOURCE.relative_to(UNIT)),
        "source_sha256": SOURCE_SHA256, "script_sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
        "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "child_CPU_s": child_cpu, "wrapper_CPU_before_receipt_tail_s": wrapper_cpu,
        "measured_combined_CPU_s": child_cpu + wrapper_cpu, "conservative_receipt_tail_reserve_s": TAIL_RESERVE,
        "charged_new_presentation_CPU_s": charged, "wall_s": wall, "child_max_RSS_KiB": after.ru_maxrss,
        "limits": {"combined_CPU_s": 4.0, "child_profiling_CPU_s": 3.5,
            "wrapper_profiling_CPU_s": .18, "wall_s": 15, "address_space_MiB": 1024, "workers": 1},
        "prior_presentation_CPU_parts": PRIOR_PARTS, "prior_known_presentation_CPU_s": sum(PRIOR_PARTS.values()),
        "known_presentation_plus_current_charge_CPU_s": sum(PRIOR_PARTS.values()) + charged,
        "temporary_presentation_cap_s": 44.5, "restore_original_cap_s": 30.0,
        "unknown_startup_external_and_historical_work": "UNKNOWN_NOT_ZERO",
        "outputs": identities, "child_report": output, "scientific_operator_imports": 0,
        "new_source_evaluations": 0, "new_IVPs": 0, "model_change": False}
    (HERE / "PRESENTATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2), flush=True)
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
