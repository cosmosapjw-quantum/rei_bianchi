"""One presentation attempt; run only after controller releases the command."""
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

UNIT = Path(__file__).resolve().parents[1]
OUT = UNIT / "outputs"


def main():
    own_start = resource.getrusage(resource.RUSAGE_SELF)
    OUT.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, str(Path(__file__).with_name("plot_single_axis.py"))]
    contract = {"command": command, "ledger": "presentation", "inherited_cpu_s": 62.468055494,
        "cumulative_ceiling_cpu_s": 65, "reserve_cpu_s": 2.5,
        "cumulative_reserved_cpu_s": 64.968055494, "child_cpu_limit_s": 2,
        "wrapper_and_tail_reserve_cpu_s": .5, "wall_limit_s": 30,
        "workers": 1, "memory_bytes": 3 * 1024**3, "automatic_retries": 0,
        "attempts": 1, "input_case": "ON_refined", "IVP_execution": "NONE"}
    with (OUT / "SINGLE_AXIS_ATTEMPT_STARTED.json").open("x") as stream:
        json.dump(contract, stream, indent=2)
        stream.write("\n")

    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
        resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))

    env = os.environ.copy()
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[key] = "1"
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    code = None
    status = "COMPLETED"
    try:
        result = subprocess.run(command, cwd=UNIT, env=env, text=True, capture_output=True,
                                timeout=30, preexec_fn=limits)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
        if code:
            status = "FAILED"
    except subprocess.TimeoutExpired as exc:
        status, stdout, stderr = "WALL_LIMIT", exc.stdout or "", exc.stderr or ""
        if isinstance(stdout, bytes): stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes): stderr = stderr.decode(errors="replace")
    except Exception as exc:
        status, stdout, stderr = "LAUNCH_ERROR", "", repr(exc)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    own = resource.getrusage(resource.RUSAGE_SELF)
    child_cpu = child.ru_utime + child.ru_stime - before.ru_utime - before.ru_stime
    wrapper_cpu = own.ru_utime + own.ru_stime - own_start.ru_utime - own_start.ru_stime
    receipt = {**contract, "status": status, "returncode": code,
        "child_cpu_s": child_cpu, "wrapper_cpu_s_observed": wrapper_cpu,
        "wall_s": time.monotonic() - start,
        "observed_increment_cpu_s": child_cpu + wrapper_cpu,
        "observed_cumulative_cpu_s_lower_bound": 62.468055494 + child_cpu + wrapper_cpu,
        "requested_executor_identity": "lower-tier coding/figure agent",
        "observed_runtime_model_identity": "UNKNOWN",
        "unknown_overhead": "UNKNOWN_NOT_ZERO: authoring/tool/host/wrapper-before-timer and receipt serialization",
        "stop_rule": "one attempt only; failure returns to controller; no automatic retry"}
    (OUT / "SINGLE_AXIS_stdout.txt").write_text(stdout)
    (OUT / "SINGLE_AXIS_stderr.txt").write_text(stderr)
    (OUT / "SINGLE_AXIS_ATTEMPT_RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    if status != "COMPLETED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
