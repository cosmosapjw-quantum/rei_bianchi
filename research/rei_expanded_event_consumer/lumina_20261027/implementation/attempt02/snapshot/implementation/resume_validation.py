"""One unexecuted recovery attempt after explicit owner cap approval and root RUN_GO.

Runs the same thirteen deterministic test groups and emits the existing public
benchmark panel export. This runner never executes the earlier attempt again.
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
ATTEMPT = HERE / "attempt02"
PRIOR_PLANNING_CPU_S = 9.978508078
PRIOR_CHILD_LEDGER_CPU_S = 8.912366
PROPOSED_CAMPAIGN_CAP_CPU_S = 11.0
RESERVATION_CPU_S = .7
LIMITS = {"CPU_soft_s": .5, "wall_s": 2.0, "memory_bytes": 134217728, "workers": 1}
TAIL_RESERVATION_CPU_S = .02
REQUIRED = {
    "implementation/lumina_adapter.py", "implementation/test_lumina_adapter.py",
    "implementation/run_bounded_tests.py", "implementation/resume_validation.py",
    "theory/FROZEN_CONTRACT.md", "source/radiation_moments.json",
    "data/DATA_CONTRACT.md", "data/HI_reion_lumina.txt",
    "data/HeIII_reion_lumina.txt", "data/sfrd_lumina.txt",
    "data/tau_cmb_vs_z_lumina.txt", "data/fetch_attempts.json",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    auth_path = HERE / "RESUME_AUTHORIZATION.json"
    auth = json.loads(auth_path.read_text())
    if (auth.get("unit") != "REI-LUMINA-20261027" or
        auth.get("attempt") != 2 or
        auth.get("user_approved_cap_increase") is not True or
        not auth.get("user_approval_reference") or
        auth.get("root_RUN_GO") is not True):
        raise SystemExit("EXPLICIT_USER_CAP_APPROVAL_AND_ROOT_RUN_GO_REQUIRED")
    if (auth.get("proposed_campaign_cap_CPU_s") != PROPOSED_CAMPAIGN_CAP_CPU_S or
        auth.get("campaign_prior_planning_CPU_s") != PRIOR_PLANNING_CPU_S or
        auth.get("prior_child_ledger_CPU_s") != PRIOR_CHILD_LEDGER_CPU_S or
        auth.get("new_reservation_CPU_s") != RESERVATION_CPU_S or
        auth.get("limits") != LIMITS or
        auth.get("receipt_tail_reserved_CPU_s") != TAIL_RESERVATION_CPU_S or
        PROPOSED_CAMPAIGN_CAP_CPU_S - PRIOR_PLANNING_CPU_S < RESERVATION_CPU_S):
        raise SystemExit("FROZEN_RECOVERY_LIMITS_OR_LEDGER_MISMATCH")
    bindings = auth.get("sha256_bindings", {})
    if set(bindings) != REQUIRED or any(digest(UNIT / p) != bindings[p] for p in REQUIRED):
        raise SystemExit("FROZEN_SOURCE_BYTE_IDENTITY_MISMATCH")
    if ATTEMPT.exists():
        raise SystemExit("ATTEMPT02_ALREADY_EXISTS_NO_AUTOMATIC_RETRY")
    if not (HERE / "attempt01" / "RECEIPT.json").is_file():
        raise SystemExit("PREVIOUS_FAILURE_RECEIPT_MISSING")
    ATTEMPT.mkdir()
    for p in sorted(REQUIRED):
        target = ATTEMPT / "snapshot" / p
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((UNIT / p).read_bytes())
    (ATTEMPT / "RESUME_AUTHORIZATION.json").write_bytes(auth_path.read_bytes())
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["LUMINA_OUTPUT_DIR"] = str(ATTEMPT)
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
    timed_out = False
    with (ATTEMPT / "stdout.log").open("wb") as stdout, (ATTEMPT / "stderr.log").open("wb") as stderr:
        child = subprocess.Popen(command, cwd=HERE, env=env, stdout=stdout, stderr=stderr, preexec_fn=caps)
        while True:
            pid, status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - start >= LIMITS["wall_s"]:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                pid, status, usage = os.wait4(child.pid, 0)
                break
            time.sleep(.002)
    exit_code = os.waitstatus_to_exitcode(status)
    child_cpu = usage.ru_utime + usage.ru_stime
    wrapper_cpu = time.process_time()  # Cumulative wrapper CPU, including interpreter startup.
    debit = child_cpu + wrapper_cpu + TAIL_RESERVATION_CPU_S
    results_path = ATTEMPT / "TEST_RESULTS.json"
    panel_path = ATTEMPT / "BENCHMARK_PANELS.json"
    results = json.loads(results_path.read_text()) if results_path.is_file() else None
    expected_outputs = bool(results and results.get("run") == 13 and
                            results.get("successful") is True and
                            results.get("failures") == 0 and
                            results.get("errors") == 0 and panel_path.is_file())
    receipt = {
        "unit": "REI-LUMINA-20261027", "attempt": 2,
        "command": command, "exit_code": exit_code, "timed_out": timed_out,
        "expected_outputs_present": expected_outputs,
        "child_CPU_s": child_cpu, "child_wall_s": time.monotonic() - start,
        "wrapper_CPU_s_including_startup": wrapper_cpu,
        "receipt_tail_reserved_CPU_s": TAIL_RESERVATION_CPU_S,
        "new_planning_CPU_debit_s": debit,
        "new_debit_within_reserved_0p7_CPU_s": debit <= RESERVATION_CPU_S,
        "prior_planning_CPU_s": PRIOR_PLANNING_CPU_S,
        "cumulative_planning_CPU_s": PRIOR_PLANNING_CPU_S + debit,
        "prior_child_ledger_CPU_s": PRIOR_CHILD_LEDGER_CPU_S,
        "cumulative_child_ledger_CPU_s": PRIOR_CHILD_LEDGER_CPU_S + child_cpu,
        "approved_campaign_cap_CPU_s": PROPOSED_CAMPAIGN_CAP_CPU_S,
        "CPU_soft_s": LIMITS["CPU_soft_s"], "hard_RLIMIT_CPU_s": 1,
        "wall_cap_s": LIMITS["wall_s"], "memory_bytes": LIMITS["memory_bytes"],
        "workers": 1, "new_IVPs": 0, "old_IVP_or_quadrature_replays": 0,
        "automatic_retry": False, "source_sha256": bindings,
        "post_run_input_sha256": {p: digest(UNIT / p) for p in sorted(REQUIRED)},
        "authorization_sha256": digest(auth_path),
        "output_sha256": {str(p.relative_to(ATTEMPT)): digest(p) for p in ATTEMPT.iterdir()
                          if p.is_file() and p.name != "RESUME_AUTHORIZATION.json"},
        "requested_executor": auth.get("requested_executor", "gpt-6-sol/high"),
        "observed_runtime_model": "UNEXPOSED",
    }
    (ATTEMPT / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    return 0 if exit_code == 0 and not timed_out and expected_outputs and debit <= RESERVATION_CPU_S else 1


if __name__ == "__main__":
    raise SystemExit(main())
