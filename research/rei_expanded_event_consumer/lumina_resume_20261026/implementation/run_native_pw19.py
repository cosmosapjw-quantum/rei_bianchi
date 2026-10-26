"""One frozen, authorized, resource-bounded scientific child; no retry."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

UNIT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "run01"
PRIOR_PLANNING_CPU_S = 10.133409987
CAMPAIGN_CAP_CPU_S = 12.0
RESERVATION_CPU_S = 1.4
TAIL_CPU_S = .03
LIMITS = {"CPU_soft_s": 1.0, "CPU_hard_s": 2, "wall_s": 5.0,
          "memory_bytes": 268435456, "workers": 1}
REQUIRED = {
    "intake/provider/spectral_photo_source.py",
    "intake/provider/CONTRACT.json",
    "intake/provider/data/z_02.479000.csv",
    "intake/provider/data/verner_photo.dat",
    "intake/SOURCE_PROVENANCE.json",
    "theory/PW19_NATIVE_MOMENT_CONTRACT.md",
    "implementation/native_pw19_moments.py",
    "implementation/check_native_pw19.py",
    "implementation/run_native_pw19.py",
    "../lumina_20261027/implementation/lumina_adapter.py",
    "../lumina_20261027/source/radiation_moments.json",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    auth_path = HERE / "RUN_AUTHORIZATION.json"
    auth = json.loads(auth_path.read_text())
    if (auth.get("unit") != "REI-LUMINA-PW19-NATIVE-20261026" or
        auth.get("attempt") != 1 or
        auth.get("root_RUN_GO") is not True or
        not auth.get("user_approval_reference")):
        raise SystemExit("ROOT_GO_AND_USER_CAP_APPROVAL_REQUIRED")
    if (auth.get("prior_cumulative_planning_CPU_s") != PRIOR_PLANNING_CPU_S or
        auth.get("temporary_campaign_cap_CPU_s") != CAMPAIGN_CAP_CPU_S or
        auth.get("reservation_CPU_s") != RESERVATION_CPU_S or
        auth.get("receipt_tail_reserved_CPU_s") != TAIL_CPU_S or
        auth.get("limits") != LIMITS or
        PRIOR_PLANNING_CPU_S + RESERVATION_CPU_S > CAMPAIGN_CAP_CPU_S):
        raise SystemExit("FROZEN_CPU_LEDGER_OR_CAP_MISMATCH")
    bindings = auth.get("sha256_bindings", {})
    if set(bindings) != REQUIRED or any(digest(UNIT / p) != bindings[p] for p in REQUIRED):
        raise SystemExit("FROZEN_INPUT_OR_IMPLEMENTATION_BYTE_MISMATCH")
    if OUTPUT.exists():
        raise SystemExit("RUN01_ALREADY_EXISTS_NO_AUTOMATIC_RETRY")
    OUTPUT.mkdir()
    (OUTPUT / "RUN_AUTHORIZATION.json").write_bytes(auth_path.read_bytes())
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1", PW19_OUTPUT_DIR=str(OUTPUT),
               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")

    def caps():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (LIMITS["CPU_hard_s"], LIMITS["CPU_hard_s"]))
        resource.setrlimit(resource.RLIMIT_AS, (LIMITS["memory_bytes"], LIMITS["memory_bytes"]))
        signal.signal(signal.SIGPROF, signal.SIG_DFL)
        signal.setitimer(signal.ITIMER_PROF, LIMITS["CPU_soft_s"])

    command = [sys.executable, str(HERE / "check_native_pw19.py")]
    started = time.monotonic()
    timed_out = False
    with (OUTPUT / "stdout.log").open("wb") as stdout, (OUTPUT / "stderr.log").open("wb") as stderr:
        child = subprocess.Popen(command, cwd=HERE, env=env, stdout=stdout,
                                 stderr=stderr, preexec_fn=caps)
        while True:
            pid, status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic()-started >= LIMITS["wall_s"]:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                pid, status, usage = os.wait4(child.pid, 0)
                break
            time.sleep(.002)
    child_cpu = usage.ru_utime + usage.ru_stime
    wrapper_cpu = time.process_time()
    debit = child_cpu + wrapper_cpu + TAIL_CPU_S
    check_path, moment_path = OUTPUT / "CHECKS.json", OUTPUT / "MOMENTS.json"
    checks = json.loads(check_path.read_text()) if check_path.is_file() else None
    receipt = {
        "unit": auth["unit"], "attempt": 1, "command": command,
        "exit_code": os.waitstatus_to_exitcode(status), "timed_out": timed_out,
        "expected_outputs_present": bool(checks and checks.get("passed") is True and moment_path.is_file()),
        "checks_run": checks.get("check_count") if checks else None,
        "child_CPU_s": child_cpu, "child_wall_s": time.monotonic()-started,
        "wrapper_CPU_s_including_startup": wrapper_cpu, "receipt_tail_reserved_CPU_s": TAIL_CPU_S,
        "new_planning_CPU_debit_s": debit, "within_1p4_CPU_reservation": debit <= RESERVATION_CPU_S,
        "prior_cumulative_planning_CPU_s": PRIOR_PLANNING_CPU_S,
        "cumulative_planning_CPU_s": PRIOR_PLANNING_CPU_S + debit,
        "temporary_campaign_cap_CPU_s": CAMPAIGN_CAP_CPU_S,
        "CPU_soft_s": LIMITS["CPU_soft_s"], "CPU_hard_s": LIMITS["CPU_hard_s"],
        "wall_cap_s": LIMITS["wall_s"], "memory_bytes": LIMITS["memory_bytes"],
        "workers": 1, "new_IVPs": 0, "historical_suite_replays": 0,
        "automatic_retry": False, "source_sha256": bindings,
        "post_run_sha256": {p: digest(UNIT / p) for p in sorted(REQUIRED)},
        "authorization_sha256": digest(auth_path),
        "output_sha256": {p.name: digest(p) for p in OUTPUT.iterdir()
                          if p.is_file() and p.name != "RUN_AUTHORIZATION.json"},
        "requested_executor": auth.get("requested_executor", "gpt-6-sol/high"),
        "observed_runtime_model": "UNEXPOSED",
    }
    (OUTPUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps(receipt, indent=2))
    return 0 if (receipt["exit_code"] == 0 and not timed_out and
                 receipt["expected_outputs_present"] and debit <= RESERVATION_CPU_S) else 1


if __name__ == "__main__":
    raise SystemExit(main())
