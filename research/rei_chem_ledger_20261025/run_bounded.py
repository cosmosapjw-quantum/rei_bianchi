"""Single-attempt isolated child runner. No scientific module is imported here."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time


def save_new(path, value):
    with path.open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu-seconds", type=int, required=True)
    parser.add_argument("--wall-seconds", type=int, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.cpu_seconds != 30 or args.wall_seconds != 120:
        parser.error("Frozen unit requires maximum CPU30s/wall120s; no budget transfer or reset")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    attempt_file = output / "attempt.json"
    if attempt_file.exists():
        print("ALREADY_ATTEMPTED")
        return 2
    source = Path(__file__).resolve().parent
    files = sorted(p for p in source.rglob("*") if p.is_file() and p.suffix in (".py", ".json", ".md") and "raw" not in p.relative_to(source).parts)
    manifest = [{"path": str(p.relative_to(source)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size} for p in files]
    command = [sys.executable, str(source / "run_checks.py"), "--output", str(output)]
    save_new(attempt_file, {"schema": "REI_CHEM_LEDGER_ATTEMPT_V1", "attempt": 1,
                           "command": command, "source_manifest": manifest,
                           "cpu_cap_seconds": 30, "wall_cap_seconds": 120, "memory_cap_bytes": 512 * 1024 * 1024,
                           "workers": 1, "threads": 1, "requested_executor": "lower-tier coding agent", "observed_model_identity": "UNOBSERVED",
                           "historical_L0_known_partial_cpu_seconds": "11.449628",
                           "historical_L0_whole_debit": "UNKNOWN_NOT_ZERO",
                           "historical_L0_overrun_seconds": "10.110448/10",
                           "historical_and_unrelated_budgets_transferred": False})
    environment = dict(os.environ)
    environment.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"})

    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))

    wall_start = time.monotonic()
    process = None
    usage = None
    exit_code = None
    timed_out = False
    launch_error = None
    try:
        with (output / "child_stdout.txt").open("xb") as stdout, (output / "child_stderr.txt").open("xb") as stderr:
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=environment, preexec_fn=limits)
            while True:
                pid, status, child_usage = os.wait4(process.pid, os.WNOHANG)
                if pid:
                    usage = child_usage
                    exit_code = os.waitstatus_to_exitcode(status)
                    process.returncode = exit_code
                    break
                if time.monotonic() - wall_start >= args.wall_seconds:
                    timed_out = True
                    os.kill(process.pid, signal.SIGKILL)
                    _, status, usage = os.wait4(process.pid, 0)
                    exit_code = os.waitstatus_to_exitcode(status)
                    process.returncode = exit_code
                    break
                time.sleep(0.01)
    except Exception as error:
        launch_error = {"type": type(error).__name__, "message": str(error)}
        if process is not None and process.returncode is None:
            try:
                os.kill(process.pid, signal.SIGKILL)
                _, status, usage = os.wait4(process.pid, 0)
                exit_code = os.waitstatus_to_exitcode(status)
                process.returncode = exit_code
            except ProcessLookupError:
                pass
    elapsed = time.monotonic() - wall_start
    results_path = output / "results.json"
    results = json.loads(results_path.read_text()) if results_path.exists() else None
    receipt = {"schema": "REI_CHEM_LEDGER_RESOURCE_RECEIPT_V1", "attempt": 1,
               "child_user_seconds": usage.ru_utime if usage else None,
               "child_system_seconds": usage.ru_stime if usage else None,
               "child_cpu_seconds": usage.ru_utime + usage.ru_stime if usage else None,
               "wall_seconds": elapsed, "exit_code": exit_code, "peak_rss_kib": usage.ru_maxrss if usage else None,
               "timed_out": timed_out, "launch_error": launch_error,
               "checks_by_category": results.get("checks_by_category") if results else None,
               "child_status": results.get("status") if results else "NO_RESULTS",
               "postprocessing_cpu_seconds": None, "postprocessing_wall_seconds": None,
               "cumulative_unit_cpu_seconds": usage.ru_utime + usage.ru_stime if usage else None,
               "cumulative_unit_wall_seconds": elapsed,
               "remaining_cap_is_not_reexecution_permission": True,
               "historical_budget_reset": False}
    save_new(output / "resource_receipt.json", receipt)
    print(json.dumps(receipt))
    return 0 if exit_code == 0 and results and results["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
