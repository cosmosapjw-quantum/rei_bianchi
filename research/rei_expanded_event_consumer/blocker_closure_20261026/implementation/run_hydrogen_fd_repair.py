"""One authorized targeted two-check repair; original run01 is immutable."""
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
OUTPUT = HERE / "repair01"
PRIOR_PLANNING_CPU_S = 11.368119996
TEMPORARY_CAMPAIGN_CAP_CPU_S = 13.0
RESERVATION_CPU_S = 1.4
TAIL_RESERVATION_CPU_S = .03
LIMITS = {"CPU_soft_s":1.0,"CPU_hard_s":2,"wall_s":8.0,
          "memory_bytes":536870912,"workers":1}
REQUIRED = {
    "theory/HYDROGEN_FD_REPAIR_CONTRACT.md",
    "implementation/check_hydrogen_fd_repair.py",
    "implementation/run_hydrogen_fd_repair.py",
    "implementation/run01/CALLBACK.json",
    "implementation/run01/CHECKS.json",
    "implementation/run01/RECEIPT.json",
    "implementation/pw19_rec_callback.py",
    "intake/rec119/code/atomic_network.py",
    "intake/rec119/data/atomic_model.json",
    "intake/rec119/data/atomic_coefficients.json",
    "intake/rec119/provenance/atomic_sources.json",
    "../lumina_resume_20261026/implementation/run01/MOMENTS.json",
    "../lumina_resume_20261026/intake/provider/data/z_02.479000.csv",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    auth_path = HERE / "REPAIR_AUTHORIZATION.json"
    auth = json.loads(auth_path.read_text())
    if (auth.get("unit") != "REI-PW19-REC119-HYDROGEN-FD-REPAIR-20261026" or
        auth.get("attempt") != 1 or auth.get("root_RUN_GO") is not True or
        not auth.get("authorization_reference")):
        raise SystemExit("REPAIR_ROOT_RUN_GO_REQUIRED")
    if (auth.get("prior_cumulative_planning_CPU_s") != PRIOR_PLANNING_CPU_S or
        auth.get("temporary_campaign_cap_CPU_s") != TEMPORARY_CAMPAIGN_CAP_CPU_S or
        auth.get("reservation_CPU_s") != RESERVATION_CPU_S or
        auth.get("receipt_tail_reserved_CPU_s") != TAIL_RESERVATION_CPU_S or
        auth.get("limits") != LIMITS or
        PRIOR_PLANNING_CPU_S+RESERVATION_CPU_S > TEMPORARY_CAMPAIGN_CAP_CPU_S):
        raise SystemExit("FROZEN_REPAIR_BUDGET_MISMATCH")
    bindings = auth.get("sha256_bindings",{})
    if set(bindings) != REQUIRED or any(digest(UNIT/p) != bindings[p] for p in REQUIRED):
        raise SystemExit("FROZEN_REPAIR_CODE_OR_INPUT_MISMATCH")
    if OUTPUT.exists():
        raise SystemExit("REPAIR01_EXISTS_NO_AUTOMATIC_RETRY")
    OUTPUT.mkdir()
    (OUTPUT/"REPAIR_AUTHORIZATION.json").write_bytes(auth_path.read_bytes())
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1",PW19_REC_REPAIR_OUTPUT_DIR=str(OUTPUT),
               OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1")

    def caps():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU,(LIMITS["CPU_hard_s"],LIMITS["CPU_hard_s"]))
        resource.setrlimit(resource.RLIMIT_AS,(LIMITS["memory_bytes"],LIMITS["memory_bytes"]))
        signal.signal(signal.SIGPROF,signal.SIG_DFL)
        signal.setitimer(signal.ITIMER_PROF,LIMITS["CPU_soft_s"])

    command = [sys.executable,str(HERE/"check_hydrogen_fd_repair.py")]
    start = time.monotonic()
    timed_out = False
    with (OUTPUT/"stdout.log").open("wb") as stdout,(OUTPUT/"stderr.log").open("wb") as stderr:
        child = subprocess.Popen(command,cwd=HERE,env=env,stdout=stdout,
                                 stderr=stderr,preexec_fn=caps)
        while True:
            pid,status,usage = os.wait4(child.pid,os.WNOHANG)
            if pid:
                break
            if time.monotonic()-start >= LIMITS["wall_s"]:
                timed_out = True
                os.killpg(child.pid,signal.SIGKILL)
                pid,status,usage = os.wait4(child.pid,0)
                break
            time.sleep(.002)
    child_cpu = usage.ru_utime+usage.ru_stime
    wrapper_cpu = time.process_time()
    debit = child_cpu+wrapper_cpu+TAIL_RESERVATION_CPU_S
    path = OUTPUT/"HYDROGEN_REPAIR.json"
    result = json.loads(path.read_text()) if path.is_file() else None
    receipt = {
        "unit":auth["unit"],"attempt":1,"command":command,
        "exit_code":os.waitstatus_to_exitcode(status),"timed_out":timed_out,
        "targeted_two_checks_pass":bool(result and result.get("pass") is True and
                                        result.get("combined_evidence_passing_count")==84),
        "child_CPU_s":child_cpu,"child_wall_s":time.monotonic()-start,
        "wrapper_CPU_s_including_startup":wrapper_cpu,
        "receipt_tail_reserved_CPU_s":TAIL_RESERVATION_CPU_S,
        "new_planning_CPU_debit_s":debit,"within_reserved_1p4_CPU_s":debit<=RESERVATION_CPU_S,
        "prior_cumulative_planning_CPU_s":PRIOR_PLANNING_CPU_S,
        "cumulative_planning_CPU_s":PRIOR_PLANNING_CPU_S+debit,
        "temporary_campaign_cap_CPU_s":TEMPORARY_CAMPAIGN_CAP_CPU_S,
        "limits":LIMITS,"new_IVPs":0,"old_suite_or_quadrature_replays":0,
        "automatic_retry":False,"sha256_bindings":bindings,
        "post_run_sha256":{p:digest(UNIT/p) for p in sorted(REQUIRED)},
        "authorization_sha256":digest(auth_path),
        "output_sha256":{p.name:digest(p) for p in OUTPUT.iterdir()
                         if p.is_file() and p.name != "REPAIR_AUTHORIZATION.json"},
        "requested_executor":auth.get("requested_executor","gpt-6-sol/high"),
        "observed_runtime_model":"UNEXPOSED",
    }
    (OUTPUT/"RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))
    return 0 if (receipt["exit_code"]==0 and not timed_out and
                 receipt["targeted_two_checks_pass"] and debit<=RESERVATION_CPU_S) else 1


if __name__ == "__main__":
    raise SystemExit(main())
