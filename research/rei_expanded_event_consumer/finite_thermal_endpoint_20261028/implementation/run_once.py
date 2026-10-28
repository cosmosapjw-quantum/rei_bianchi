"""One explicitly authorized C6 attempt. Authored in C5, NOT EXECUTED.

POSIX-only. This wrapper is an operational replay/budget guard, not a security
boundary. A truthful operator authorization is required; no budget is granted
by this file. Run the entire command under external OS accounting as documented.
"""
from __future__ import annotations
import time
_START_WALL = time.monotonic()
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import sys

UNIT = "finite_thermal_endpoint_20261028"
ROOT = Path(__file__).resolve().parent
FILES = ("finite_thermal.py", "test_finite_thermal.py", "run_once.py")
PRIOR_KNOWN_MINIMUM = Decimal("15.929490885")
SOURCE_JOB = (
    "import json,sys; from pathlib import Path; import finite_thermal as f; "
    "r=f.consume_saved_source(Path(sys.argv[1]).read_bytes(),Path(sys.argv[2]).read_bytes()); "
    "print(json.dumps(f.to_wire(r),ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False))"
)


class BudgetStop(RuntimeError):
    pass


def _positive_number(value, name):
    if type(value) not in (str, int, float):
        raise ValueError(name + " must be an explicit finite positive number")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(name + " is not a number") from exc
    if not number.is_finite() or number <= 0 or not math.isfinite(float(number)) or float(number) <= 0:
        raise ValueError(name + " must be finite and positive")
    return number


def validate_authorization(auth, *, mode, source_hashes, worker_command):
    """Pure validation only. Does not execute a command or manufacture approval."""
    if type(auth) is not dict or auth.get("schema") != "REI_FINITE_THERMAL_RUN_AUTH_V1":
        raise ValueError("separate explicit execution authorization required")
    if auth.get("approved") is not True or auth.get("unit") != UNIT:
        raise ValueError("this unit has no explicit execution approval")
    if auth.get("mode") != mode or mode not in ("tests", "source"):
        raise ValueError("authorization mode mismatch")
    if type(auth.get("attempts")) is not int or auth["attempts"] != 1:
        raise ValueError("exactly one attempt, no automatic retry")
    for name in ("authority_ref", "attempt_id", "accounting_boundary"):
        if type(auth.get(name)) is not str or not auth[name].strip():
            raise ValueError("missing explicit " + name)
    if auth.get("unknown_costs") != "UNKNOWN_NOT_ZERO":
        raise ValueError("historical unknown costs must be preserved")
    if auth.get("source_sha256") != source_hashes or set(source_hashes) != set(FILES):
        raise ValueError("authorized implementation/test/runner hashes differ")
    if auth.get("worker_command") != worker_command:
        raise ValueError("exact worker command not authorized")
    limits = auth.get("limits", {})
    attempt = _positive_number(limits.get("attempt_cpu_s"), "attempt CPU")
    worker = _positive_number(limits.get("worker_cpu_s"), "worker CPU")
    tail = _positive_number(limits.get("final_record_reserve_cpu_s"), "final recording reserve")
    wall = _positive_number(limits.get("wall_s"), "wall limit")
    prior = _positive_number(auth.get("prior_known_planning_cpu_s"), "prior planning lower record")
    cap = _positive_number(auth.get("approved_absolute_planning_cap_cpu_s"), "explicit cumulative cap")
    memory = limits.get("memory_bytes")
    if type(memory) is not int or memory <= 0:
        raise ValueError("explicit positive integer memory limit required")
    if prior < PRIOR_KNOWN_MINIMUM or prior + attempt > cap:
        raise ValueError("historical debit reset or reserved attempt exceeds cap")
    if worker + tail >= attempt:
        raise ValueError("positive supervisor allowance is required")
    return dict(attempt=float(attempt), worker=float(worker), tail=float(tail),
                parent=float(attempt-worker-tail), wall=float(wall), memory=memory)


def classify_outcome(*, exit_code, terminal_usage_observed, supervisor_error_kind,
                     limit_overrun):
    """Classify observed process evidence, not the truth of the science.

    A missing observation is not a measured budget overrun. Timer-related
    worker signals are recorded as signals, without inventing their sender.
    SIGKILL alone cannot identify CPU exhaustion, OOM, or an external kill.
    """
    if supervisor_error_kind not in (None, "resource", "execution", "interrupted"):
        raise ValueError("unknown supervisor error kind")
    if limit_overrun or supervisor_error_kind == "resource":
        return "RESOURCE_STOP_OR_OVERRUN", "runtime_environment/resource_budget"
    if supervisor_error_kind == "interrupted":
        return "INTERRUPTED", "execution/operator_interruption"
    if supervisor_error_kind == "execution":
        return "EXECUTION_FAILED", "runtime_environment/execution_error"
    if exit_code is None or not terminal_usage_observed:
        return "INCOMPLETE_OBSERVATION", "runtime_environment/incomplete_observation"
    if exit_code < 0:
        if -exit_code in (signal.SIGALRM, signal.SIGPROF, signal.SIGXCPU):
            return "WORKER_RESOURCE_SIGNAL", "runtime_environment/resource_signal_cause_unconfirmed"
        return "EXECUTION_FAILED", "runtime_environment/signal_cause_unconfirmed"
    if exit_code != 0:
        return "EXECUTION_FAILED", "execution/nonzero_exit_unadjudicated"
    return "EXECUTION_EXIT_ZERO_NOT_SCIENTIFIC_ADMISSION", None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("tests", "source"))
    parser.add_argument("--source", type=Path)
    parser.add_argument("--literals", type=Path)
    args = parser.parse_args(argv)
    if os.name != "posix" or not hasattr(os, "fork") or not hasattr(os, "wait4"):
        raise RuntimeError("POSIX fork/wait4 required; no unmetered fallback")
    import resource

    def self_cpu():
        r = resource.getrusage(resource.RUSAGE_SELF)
        return r.ru_utime + r.ru_stime

    if args.mode == "tests":
        if args.source is not None or args.literals is not None:
            raise ValueError("fixture tests cannot also run the actual source")
        command = [sys.executable, "-B", "-S", "-m", "unittest", "discover",
                   "-s", str(ROOT), "-p", "test_finite_thermal.py", "-v"]
    else:
        if args.source is None or args.literals is None:
            raise ValueError("source mode needs the ORIGINAL source and literal packet")
        source, literals = args.source.resolve(), args.literals.resolve()
        if not source.is_file() or not literals.is_file():
            raise ValueError("missing original input; automatic restoration is not supported")
        command = [sys.executable, "-B", "-S", "-c", SOURCE_JOB, str(source), str(literals)]
    auth_path = args.authorization.resolve()
    auth_bytes = auth_path.read_bytes()
    auth = json.loads(auth_bytes)
    hashes = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FILES}
    limits = validate_authorization(auth, mode=args.mode, source_hashes=hashes, worker_command=command)
    if self_cpu() >= limits["parent"] or time.monotonic()-_START_WALL >= limits["wall"]:
        raise BudgetStop("startup/authorization processing already exhausted its allowance")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    # One use of this authorization file, even if a later launch fails.
    with auth_path.with_name(auth_path.name + ".used").open("x", encoding="utf-8") as f:
        json.dump(dict(attempt_id=auth["attempt_id"], output_dir=str(output),
                       authorization_sha256=hashlib.sha256(auth_bytes).hexdigest()), f)
    record = dict(unit=UNIT, mode=args.mode, attempt_id=auth["attempt_id"],
                  status="STARTED", scientific_admission="NOT_ISSUED",
                  authorization=auth, worker_command=command, source_sha256=hashes,
                  python=sys.version, child_started=False, automatic_retries=0,
                  physical_outputs=dict(actual_native25=None, actual_temperature_update=None,
                                        physical_radii=None, L4_ready=False, global_physical_completion=None))
    (output/"STARTED.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    pid, usage, wait_status = None, None, None
    stop_reason = None
    supervisor_error_kind = None
    supervisor_exception_type = None

    def stopped(signum, frame):
        raise BudgetStop("supervisor resource stop signal=" + str(signum))

    handlers = {s: signal.getsignal(s) for s in (signal.SIGALRM, signal.SIGPROF, signal.SIGXCPU)}
    for sig in handlers:
        signal.signal(sig, stopped)
    try:
        parent_remaining = limits["parent"] - self_cpu()
        wall_remaining = limits["wall"] - (time.monotonic()-_START_WALL)
        if parent_remaining <= 0 or wall_remaining <= 0:
            raise BudgetStop("prelaunch metadata exhausted the supervisor allowance")
        signal.setitimer(signal.ITIMER_PROF, parent_remaining)
        signal.setitimer(signal.ITIMER_REAL, wall_remaining)
        pid = os.fork()
        if pid == 0:
            try:
                for sig in handlers:
                    signal.signal(sig, signal.SIG_DFL)
                os.setsid()
                out = os.open(output/"stdout.txt", os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
                err = os.open(output/"stderr.txt", os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
                os.dup2(out, 1)
                os.dup2(err, 2)
                os.close(out)
                os.close(err)
                resource.setrlimit(resource.RLIMIT_AS, (limits["memory"], limits["memory"]))
                cpu_hard = max(1, math.ceil(limits["worker"]))
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_hard, cpu_hard))
                remaining = limits["worker"] - self_cpu()
                if remaining <= 0:
                    raise BudgetStop("child setup exhausted worker budget")
                signal.setitimer(signal.ITIMER_PROF, remaining)
                signal.setitimer(signal.ITIMER_REAL, max(0.001, wall_remaining))
                os.chdir(ROOT)
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1",
                           OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
                os.execve(sys.executable, command, env)
            except BaseException as exc:
                os.write(2, ("WORKER_LAUNCH_FAILED: " + repr(exc) + "\n").encode())
                os._exit(125)
        record["child_started"] = True
        while True:
            got, status, observed = os.wait4(pid, os.WNOHANG)
            if got == pid:
                wait_status, usage = status, observed
                break
            if self_cpu() >= limits["parent"] or time.monotonic()-_START_WALL >= limits["wall"]:
                raise BudgetStop("supervisor CPU/wall limit")
            time.sleep(0.01)
    except BaseException as exc:
        supervisor_exception_type = type(exc).__name__
        stop_reason = supervisor_exception_type + ": " + str(exc)
        supervisor_error_kind = ("resource" if isinstance(exc, BudgetStop)
                                 else "interrupted" if isinstance(exc, KeyboardInterrupt)
                                 else "execution")
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.setitimer(signal.ITIMER_REAL, 0)
        if pid is not None and pid > 0 and usage is None:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _, wait_status, usage = os.wait4(pid, 0)
        for sig, handler in handlers.items():
            signal.signal(sig, handler)

    child_cpu = None if usage is None else usage.ru_utime + usage.ru_stime
    parent_prefix = self_cpu()
    measured_prefix = None if child_cpu is None else parent_prefix + child_cpu
    exit_code = None if wait_status is None else os.waitstatus_to_exitcode(wait_status)
    elapsed_prefix = time.monotonic() - _START_WALL
    overrun_observations = dict(
        worker_cpu=None if usage is None else child_cpu > limits["worker"],
        supervisor_cpu_prefix=parent_prefix > limits["parent"],
        attempt_cpu_prefix_plus_record_reserve=(None if usage is None else
                                               measured_prefix + limits["tail"] > limits["attempt"]),
        wall_prefix=elapsed_prefix > limits["wall"],
    )
    status, failure_class = classify_outcome(
        exit_code=exit_code, terminal_usage_observed=usage is not None,
        supervisor_error_kind=supervisor_error_kind,
        limit_overrun=any(value is True for value in overrun_observations.values()),
    )
    record.update(status=status, failure_class=failure_class,
                  exit_code=exit_code, raw_wait_status=wait_status,
                  worker_termination_signal=(-exit_code if exit_code is not None and exit_code < 0 else None),
                  supervisor_error_kind=supervisor_error_kind,
                  supervisor_exception_type=supervisor_exception_type,
                  terminal_usage_observed=usage is not None,
                  limit_overrun_observations=overrun_observations,
                  stop_reason=stop_reason,
                  worker_terminal_user_s=None if usage is None else usage.ru_utime,
                  worker_terminal_system_s=None if usage is None else usage.ru_stime,
                  worker_terminal_cpu_s=None if usage is None else child_cpu,
                  worker_maxrss_host_units=None if usage is None else usage.ru_maxrss,
                  supervisor_pre_serialization_cpu_s=parent_prefix,
                  inclusive_pre_serialization_cpu_s=measured_prefix,
                  unmeasured_final_record_reserve_cpu_s=limits["tail"],
                  elapsed_since_wrapper_early_clock_s=elapsed_prefix,
                  exact_whole_command_cpu_s=None,
                  external_full_command_accounting="REQUIRED; inclusive external total must not be added to worker CPU again",
                  historical_unknown_costs="UNKNOWN_NOT_ZERO",
                  whole_turn_budget_compliance="NOT_CLAIMED",
                  source_scope="Fixture checks only" if args.mode == "tests" else "Conditional frozen-source diagnostic only")
    with (output/"RESULT.json").open("x", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
    return 0 if status == "EXECUTION_EXIT_ZERO_NOT_SCIENTIFIC_ADMISSION" else 2


if __name__ == "__main__":
    try:
        code = main()
    except Exception as exc:
        print(type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        code = 2
    raise SystemExit(code)
