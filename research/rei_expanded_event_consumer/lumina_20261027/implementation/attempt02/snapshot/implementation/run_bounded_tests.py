"""Single authorized deterministic child with raw logs and measured debit.

Preparation/import alone does not execute tests. Root writes RUN_AUTHORIZATION.json
after static review and requests the one bounded invocation explicitly.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent
LIMITS = {"CPU_soft_s": .05, "wall_s": 2.0, "memory_bytes": 134217728, "workers": 1}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    auth_path = HERE / "RUN_AUTHORIZATION.json"
    auth = json.loads(auth_path.read_text())
    if auth.get("authorized") is not True or auth.get("unit") != "REI-LUMINA-20261027":
        raise SystemExit("ROOT_RUN_GO_REQUIRED")
    if auth.get("limits") != LIMITS or auth.get("campaign_prior_planning_CPU_s") != 9.874926553:
        raise SystemExit("FROZEN_BUDGET_OR_LIMIT_MISMATCH")
    if 10 - auth["campaign_prior_planning_CPU_s"] < .1:
        raise SystemExit("INSUFFICIENT_RESERVATION")
    bindings = auth["sha256_bindings"]
    required = {"implementation/lumina_adapter.py", "implementation/test_lumina_adapter.py",
                "implementation/run_bounded_tests.py", "source/radiation_moments.json",
                "data/HI_reion_lumina.txt", "data/HeIII_reion_lumina.txt",
                "data/sfrd_lumina.txt", "data/tau_cmb_vs_z_lumina.txt",
                "data/fetch_attempts.json", "data/DATA_CONTRACT.md",
                "theory/FROZEN_CONTRACT.md"}
    if set(bindings) != required or any(digest(UNIT / p) != bindings[p] for p in required):
        raise SystemExit("INPUT_BYTE_IDENTITY_MISMATCH")
    attempt = HERE / "attempt01"
    attempt.mkdir(exist_ok=False)
    for p in sorted(required):
        target = attempt / "snapshot" / p
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((UNIT / p).read_bytes())
    (attempt / "RUN_AUTHORIZATION.json").write_bytes(auth_path.read_bytes())
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["LUMINA_OUTPUT_DIR"] = str(attempt)
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[key] = "1"

    def caps():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
        resource.setrlimit(resource.RLIMIT_AS, (LIMITS["memory_bytes"], LIMITS["memory_bytes"]))
        signal.signal(signal.SIGPROF, signal.SIG_DFL)
        signal.setitimer(signal.ITIMER_PROF, LIMITS["CPU_soft_s"])

    command = [sys.executable, str(HERE / "test_lumina_adapter.py")]
    start = time.monotonic()
    timeout = False
    with (attempt / "stdout.log").open("wb") as stdout, (attempt / "stderr.log").open("wb") as stderr:
        child = subprocess.Popen(command, cwd=HERE, env=env, stdout=stdout, stderr=stderr, preexec_fn=caps)
        while True:
            pid, status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - start >= LIMITS["wall_s"]:
                timeout = True
                os.killpg(child.pid, signal.SIGKILL)
                pid, status, usage = os.wait4(child.pid, 0)
                break
            time.sleep(.002)
    exit_code = os.waitstatus_to_exitcode(status)
    wall = time.monotonic() - start
    wrapper_cpu = time.process_time()  # Includes process startup/imports, measured after child.
    debit = usage.ru_utime + usage.ru_stime + wrapper_cpu + .01
    receipt = {
        "unit": "REI-LUMINA-20261027", "attempt": 1, "command": command,
        "exit_code": exit_code, "timed_out": timeout,
        "child_CPU_s": usage.ru_utime + usage.ru_stime, "child_wall_s": wall,
        "wrapper_CPU_s_including_startup": wrapper_cpu,
        "receipt_tail_reserved_CPU_s": .01, "new_planning_CPU_debit_s": debit,
        "new_debit_within_reserved_0p1_CPU_s": debit <= .1,
        "prior_planning_CPU_s": auth["campaign_prior_planning_CPU_s"],
        "cumulative_planning_CPU_s": auth["campaign_prior_planning_CPU_s"] + debit,
        "CPU_soft_s": .05, "hard_RLIMIT_CPU_s": 1,
        "wall_cap_s": LIMITS["wall_s"], "memory_bytes": LIMITS["memory_bytes"],
        "workers": 1, "new_IVPs": 0, "prior_IVP_replays": 0,
        "automatic_retry": False, "source_sha256": bindings,
        "post_run_input_sha256": {p: digest(UNIT / p) for p in sorted(required)},
        "authorization_sha256": digest(auth_path),
        "output_sha256": {str(p.relative_to(attempt)): digest(p) for p in attempt.iterdir() if p.is_file() and p.name != "RUN_AUTHORIZATION.json"},
        "requested_executor": auth.get("requested_executor", "unexposed"),
        "observed_runtime_model": "UNEXPOSED",
    }
    (attempt / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    return 0 if exit_code == 0 and debit <= .1 and not timeout else 1


if __name__ == "__main__":
    raise SystemExit(main())
