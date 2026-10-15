#!/usr/bin/env python3
"""One actual user-authorized AX08 MINUS release with fresh NCP readback.

Controller is not a science solver and cannot itself claim independent-model
review. Must be invoked once with a currently reachable remote-host argument.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime,timezone

ROOT=Path(os.environ.get("AX08_CANONICAL_ROOT",str(Path(__file__).resolve().parents[6])))
OWN=Path(__file__).resolve().parent
LAUNCHER=OWN/"launcher.py"
REVIEW=OWN/"MECHANICAL_REVIEW.json"
CONTRACT=OWN/"LAUNCH_CONTRACT.json"
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def atomic_x(path,data):
    with path.open("x") as f:
        json.dump(data,f,sort_keys=True,indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
def now():
    return datetime.now(timezone.utc).isoformat()
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--remote-host",required=True)
    p.add_argument("--start",action="store_true")
    args=p.parse_args()
    if not args.start:
        raise ValueError("NO_ACTION_WITHOUT_EXPLICIT_START")
    release=OWN/"RELEASE.json"
    if release.exists() or (OWN/"RESERVATION.json").exists() or (OWN/"PROCESS_ACK.json").exists():
        raise RuntimeError("ALREADY_RELEASED_OR_SPENT")
    review=json.loads(REVIEW.read_text())
    contract=json.loads(CONTRACT.read_text())
    if review.get("status")!="PASS_SCOPED_INDEPENDENT_IMPLEMENTATION_CONTROL":
        raise RuntimeError("MECHANICAL_REVIEW_NOT_PASS")
    if review.get("source_sha256")!=sha(LAUNCHER) or review.get("contract_sha256")!=sha(CONTRACT):
        raise RuntimeError("CHANGED_REVIEWED_SOURCE")
    checks=subprocess.run([sys.executable,str(LAUNCHER),"--preflight"],
           cwd=ROOT,capture_output=True,text=True,timeout=30)
    if checks.returncode!=0:
        raise RuntimeError("CURRENT_PREFLIGHT_FAILED:"+checks.stderr[-1000:])
    pre=json.loads(checks.stdout)
    if pre.get("status")!="PRELAUNCH_SCOPED_LOCAL_PASS" or pre.get("active_science_count")!=0 or pre.get("active_owner_count")!=0:
        raise RuntimeError("SHARED_LOCAL_SLOT_NOT_FREE")
    ssh=subprocess.run(["ssh","-i",str(Path.home()/".ssh/ncp_key"),
       "-o","BatchMode=yes","-o","ConnectTimeout=8",args.remote_host,
       "ps -eo comm= | grep -E '^axbi_' || true"],capture_output=True,text=True,timeout=15)
    if ssh.returncode!=0 or ssh.stdout.strip():
        raise RuntimeError("NCP_SCIENCE_STATE_UNKNOWN_OR_BUSY:"+ssh.stdout[-300:])
    # Check the explicitly reviewed single-start frozen allocation still binds.
    if contract["existing_authority"]["science_allocation_increase"]!=0:
        raise RuntimeError("UNAUTHORIZED_ALLOCATION_CHANGE")
    if contract["execution"]["caps"]["new_observed_starts_max"]!=1 or contract["execution"]["caps"]["automatic_retries"]!=0:
        raise RuntimeError("MULTIPLE_SCIENCE_STARTS_NOT_ALLOWED")
    # A previous local science reservation counts as pending unless it has its own
    # typed terminal receipt. This avoids silently reusing a scheduler slot.
    old_reservations=list((ROOT/"research/axbi_goal_20261014/driver/full").rglob("RESERVATION.json"))
    pending=[]
    for reservation in old_reservations:
        if reservation.parent==OWN:
            continue
        terminal=reservation.parent/"TERMINAL_RECEIPT.json"
        if not terminal.is_file():
            pending.append(str(reservation.relative_to(ROOT)))
    if pending:
        raise RuntimeError("UNRESOLVED_PREEXISTING_SCIENCE_RESERVATION:"+str(pending))
    unix=time.time()
    record={
       "schema":"rei.axbi.shear_half_minus_controller_release.v1",
       "case":"SHEAR_HALF_MINUS","status":"FRESH_CONTROLLER_RELEASE_ONE_START",
       "utc":now(),"observed_unix_s":unix,
       "launcher_sha256":sha(LAUNCHER),
       "contract_sha256":sha(CONTRACT),
       "independent_launcher_review":"PASS_SCOPED",
       "review_independence_detail":"Independent implementation checker/real preflight; distinct model NOT_RUN",
       "mechanical_review_sha256":sha(REVIEW),
       "existing_independent_science_binding_review_sha256":contract["existing_authority"]["independent_review_sha256"],
       "remote_checked":True,"pending_checked":True,"exclusive_owner":True,
       "remote_observation":{"ssh_exit_code":ssh.returncode,
          "binary_comm_matches":[],"utc":now(),"unresolved_other_wrapped_jobs":"not_observed"},
       "local_observation":pre,
       "no_active_axbi_on_local_or_ncp":True,
       "science_count_after_reservation":1,
        "half_plus_terminal_sha256":pre["half_plus_classification"]["terminal_sha256"],
       "minus_terminal_sha256":pre["minus_classification"]["terminal_sha256"],
       "no_scientific_claim_authorized":True,
       "automatic_retries":0
    }
    atomic_x(release,record)
    # The launcher is the only owner that can create science RESERVATION/Popen.
    with (OWN/"controller.stdout").open("xb") as stdout, (OWN/"controller.stderr").open("xb") as stderr:
        child=subprocess.Popen([sys.executable,str(LAUNCHER),"--launch","--release",str(release)],
            cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,
            start_new_session=True,close_fds=True)
    atomic_x(OWN/"CONTROLLER_DETACHED_ACK.json",
        {"utc":now(),"launcher_pid":child.pid,"controller_pid":os.getpid(),
        "release_sha256":sha(release),"science_started":False,
        "science_launch_delegated":True,"no_retries":True})
    print(json.dumps({"status":"RELEASED_AND_LAUNCHER_DETACHED",
         "launcher_pid":child.pid,"release_sha256":sha(release),
         "scientific_admission":"NOT_ISSUED"}))
if __name__=="__main__":
    main()
