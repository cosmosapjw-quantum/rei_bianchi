#!/usr/bin/env python3
"""Single authorized AX08 SHEAR_MINUS continuation, no solver at --preflight.

The previously reviewed scientific binary/config/binding are immutable. A separate
fresh controller RELEASE is required before precisely one observed solver start.
Never infer ownership by searching arbitrary command-line arguments.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[6]
OWN = Path(__file__).resolve().parent
BASE = OWN.parent
AX = ROOT / "research/axbi_goal_20261014"
HALF_LAUNCH = AX / "driver/full/half_plus_continuation_001/launch_001"
PLUS_INCIDENT = AX / "driver/full/epoch_recovery_001/plus/recovery_001/INCIDENT_CLASSIFICATION.json"
HALF_COMPOSED = AX / "runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002"
CONTRACT = OWN / "LAUNCH_CONTRACT.json"

def hash_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load(path: Path) -> dict:
    return json.loads(path.read_text())

def utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe_json(path: Path, data: dict) -> None:
    with path.open("x") as f:
        json.dump(data,f,indent=2,sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())

def process_record(pid: int):
    p=Path("/proc")/str(pid)
    try:
        stat=(p/"stat").read_text().rsplit(")",1)[1].split()
        argv=[v.decode(errors="replace") for v in (p/"cmdline").read_bytes().split(b"\0") if v]
        rss=0
        for line in (p/"status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                rss=int(line.split()[1])*1024
                break
        return {"pid":pid,"pgid":int(stat[2]),"start_ticks":int(stat[19]),"argv":argv,
                "rss_bytes":rss,"cwd":os.readlink(p/"cwd")}
    except (OSError,ValueError,IndexError):
        return None

def inventory():
    return [v for s in os.listdir("/proc") if s.isdigit()
            if (v:=process_record(int(s))) is not None]

SCHEDULER_SCRIPTS={"run_campaign.py","recover_queue.py","post_cap_dispatch.py",
                   "post_plus_dispatch.py","post_plus_epoch_dispatch.py","recover_plus.py",
                   "repaired_adapter.py","launcher.py"}

def is_owner(p: dict) -> bool:
    argv=p["argv"]
    if not argv:
        return False
    first=Path(argv[0]).name
    if first.endswith(".py"):
        script=Path(argv[0])
    elif first.startswith("python"):
        i=1
        while i<len(argv) and argv[i] in ("-u","-B","-E","-I","-s","-S"):
            i+=1
        if i>=len(argv) or not argv[i].endswith(".py"):
            return False
        script=Path(argv[i])
    else:
        return False
    if script.name not in SCHEDULER_SCRIPTS:
        return False
    # A similarly named Python script in another project is not AX08's owner.
    if not script.is_absolute():
        if not p.get("cwd"):
            return False
        script=Path(p["cwd"])/script
    try:
        script.resolve().relative_to(AX/"driver/full")
        return True
    except ValueError:
        return False

def is_science(p: dict) -> bool:
    argv=p["argv"]
    # Executable slot ONLY, never data operands, shell command text or rg paths.
    return bool(argv) and Path(argv[0]).name.startswith("axbi_")

def usage_bytes(path: Path) -> int:
    if not path.exists(): return 0
    if path.is_file(): return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())

def classify_half_plus() -> dict:
    terminal=load(HALF_LAUNCH/"TERMINAL_RECEIPT.json")
    prior_return=(AX/"runs/paired/32d11e733155/SHEAR_HALF_PLUS_continuation_001/RETURN.txt")
    ret=dict(line.split("=",1) for line in prior_return.read_text().splitlines() if "=" in line)
    comp=load(HALF_COMPOSED/"COMPOSITION_RECEIPT.json")
    incident=load(PLUS_INCIDENT)
    if incident.get("status")!="RUNTIME_CLASSIFIER_FALSE_POSITIVE_SOLVER_ABORTED":
        raise RuntimeError("PLUS_INCIDENT_NOT_CLASSIFIED")
    if terminal.get("exit_code")!=0 or terminal.get("stop_reason") is not None:
        raise RuntimeError("HALF_PLUS_LAUNCH_NOT_NATURAL")
    if not (ret.get("status")=="COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT"
            and ret.get("result")=="Ok(())" and float(ret.get("a","nan"))==.2
            and int(ret.get("accepted",-1))==312237):
        raise RuntimeError("HALF_PLUS_RETURN_NOT_COMPLETE")
    if (comp.get("status")!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION"
            or comp.get("row_counts",{}).get("history.csv",{}).get("composed_rows")!=312238):
        raise RuntimeError("HALF_PLUS_COMPOSITION_NOT_COMPLETED")
    if comp.get("input_sha256",{}).get(str(prior_return.relative_to(ROOT))) != hash_file(prior_return):
        raise RuntimeError("HALF_PLUS_TERMINAL_IDENTITY_CHANGED")
    return {"terminal_exit":0,"last_accepted":312237,"a":.2,
            "composed_rows":312238,"source_compatibility":"REVIEWED_RESOURCE_ONLY",
            "incident_status":incident["status"],
            "terminal_sha256":hash_file(prior_return),
            "composition_receipt_sha256":hash_file(HALF_COMPOSED/"COMPOSITION_RECEIPT.json")}

def preflight() -> dict:
    c=load(CONTRACT)
    if c["case"]!="SHEAR_MINUS" or c["segment"]!="SHEAR_MINUS_RESOURCE_CONTINUATION_001":
        raise RuntimeError("CASE_CONTRACT_CHANGED")
    if c["existing_authority"]["review_decision"]!="PASS_SCOPED_EXACT_BINDINGS_CONDITIONAL_LAUNCH":
        raise RuntimeError("PREVIOUS_BINDING_REVIEW_NOT_PASS")
    checked={}
    for key,descriptor in {
       "authority":(c["existing_authority"]["path"],c["existing_authority"]["sha256"]),
       "previous_review":(c["existing_authority"]["independent_binding_review"],c["existing_authority"]["independent_review_sha256"]),
       "binding":(c["binding"]["path"],c["binding"]["sha256"]),
       "private_authority":(str(BASE.relative_to(ROOT)/"EXECUTION_AUTHORITY.binding"),c["binding"]["private_authority_binding_sha256"]),
       "binary":(c["binding"]["binary"],c["binding"]["binary_sha256"]),
    }.items():
        path=ROOT/descriptor[0]
        if hash_file(path)!=descriptor[1]:
            raise RuntimeError("FROZEN_IDENTITY_MISMATCH:"+key)
        checked[key]=descriptor[1]
    half=classify_half_plus()
    out=ROOT/c["execution"]["output"]
    raw=ROOT/c["execution"]["raw_output"]
    if out.exists() or raw.exists():
        raise RuntimeError("DUPLICATE_OUTPUT_OR_RAW")
    if any((OWN/name).exists() for name in ("RESERVATION.json","PROCESS_ACK.json",
                                            "stdout.log","stderr.log","TERMINAL_RECEIPT.json")):
        raise RuntimeError("PREVIOUS_LAUNCH_RESERVED")
    records=inventory()
    active=[v for v in records if is_science(v)]
    owners=[v for v in records if is_owner(v) and v["pid"]!=os.getpid()]
    if active or owners:
        raise RuntimeError("ACTIVE_SCIENCE_OR_SCHEDULER_OWNER")
    cpu0=0 in os.sched_getaffinity(0)
    free=shutil.disk_usage(out.parent).free
    mem=next(int(s.split()[1])*1024 for s in Path("/proc/meminfo").read_text().splitlines() if s.startswith("MemAvailable:"))
    if not cpu0 or free<4*1024**3 + 128*1024**2 or mem<2*1024**3:
        raise RuntimeError("LOCAL_RESOURCES_INSUFFICIENT")
    if c["execution"]["outer_argv"][-1]!=c["binding"]["sha256"]:
        raise RuntimeError("FROZEN_ARGV_BINDING_MISMATCH")
    return {"status":"PRELAUNCH_SCOPED_LOCAL_PASS","utc":utc(),"checked":checked,
            "half_plus_classification":half,"active_science_count":len(active),
            "active_owner_count":len(owners),"disk_free_bytes":free,
            "mem_available_bytes":mem,"cpu0":cpu0,
            "contract_sha256":hash_file(CONTRACT),"scientific_admission":"NOT_ISSUED"}

def launch(release_path: Path) -> int:
    rel=load(release_path)
    if rel.get("status")!="FRESH_CONTROLLER_RELEASE_ONE_START" or rel.get("case")!="SHEAR_MINUS":
        raise RuntimeError("MISSING_RELEASE")
    if rel.get("launcher_sha256")!=hash_file(Path(__file__)) or rel.get("contract_sha256")!=hash_file(CONTRACT):
        raise RuntimeError("RELEASE_SOURCE_CHANGED")
    if rel.get("independent_launcher_review")!="PASS_SCOPED":
        raise RuntimeError("LAUNCH_REVIEW_MISSING")
    if not rel.get("remote_checked") or not rel.get("pending_checked") or not rel.get("exclusive_owner"):
        raise RuntimeError("SHARED_SCHEDULER_NOT_RELEASED")
    t=rel.get("observed_unix_s")
    if not isinstance(t,(int,float)) or not 0<=time.time()-t<=300:
        raise RuntimeError("STALE_SHARED_SCHEDULER_OBSERVATION")
    check=preflight()
    if rel.get("half_plus_terminal_sha256")!=check["half_plus_classification"]["terminal_sha256"]:
        raise RuntimeError("HALF_PLUS_REVIEW_DRIFT")
    if rel.get("science_count_after_reservation",3)>2:
        raise RuntimeError("EXCESS_SHARED_SCIENCE_COUNT")
    c=load(CONTRACT)
    argv=c["execution"]["outer_argv"]
    after={"original_starts":5,"zero_continuation":1,"plus_attempted":2,
           "plus_observed":1,"half_plus_observed":1,"minus_observed":1,
           "full_observed_starts":9,"history_observed_starts":12}
    safe_json(OWN/"RESERVATION.json",{"status":"ONE_ATTEMPT_RESERVED","utc":utc(),
              "release_sha256":hash_file(release_path),"args":argv,
              "before":check,"projected_if_process_starts":after})
    env=os.environ.copy()
    env.update(c["execution"]["environment"])
    t0=time.monotonic()
    with (OWN/"stdout.log").open("xb") as stdout, (OWN/"stderr.log").open("xb") as stderr:
        proc=subprocess.Popen(argv,cwd=ROOT,env=env,stdin=subprocess.DEVNULL,
                              stdout=stdout,stderr=stderr,start_new_session=True,close_fds=True)
        rec=process_record(proc.pid)
        safe_json(OWN/"PROCESS_ACK.json",{"utc":utc(),"pid":proc.pid,"pgid":proc.pid,
                  "start_ticks":rec["start_ticks"] if rec else None,
                  "argv":argv,"accounting":after,"scientific_admission":"NOT_ISSUED"})
        reason=None
        out=ROOT/c["execution"]["output"]
        raw=ROOT/c["execution"]["raw_output"]
        while proc.poll() is None:
            group=[v for v in inventory() if v["pgid"]==proc.pid]
            rss=sum(v["rss_bytes"] for v in group)
            data=usage_bytes(out)
            evid=usage_bytes(raw)+usage_bytes(OWN)
            sec=time.monotonic()-t0
            if rss>2*1024**3: reason="RSS_CAP"
            elif data>3968*1024**2: reason="SCIENCE_OUTPUT_CAP"
            elif evid>128*1024**2: reason="LAUNCHER_OUTPUT_CAP"
            elif data+evid>4096*1024**2: reason="COMBINED_OUTPUT_CAP"
            elif sec>10800: reason="WALL_CAP"
            if reason:
                os.killpg(proc.pid,signal.SIGKILL)
                break
            time.sleep(1)
        code=proc.wait()
    safe_json(OWN/"TERMINAL_RECEIPT.json",{"utc":utc(),"exit_code":code,
              "stop_reason":reason,"elapsed_s":time.monotonic()-t0,
              "checkpoint_present":(out/"checkpoint.txt").exists(),
              "return_present":(out/"RETURN.txt").exists(),
              "status":"TERMINAL_NEEDS_SCIENTIFIC_CLASSIFICATION",
              "automatic_retry":False,"scientific_admission":"NOT_ISSUED",
              "accounting":after})
    return code

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--preflight",action="store_true")
    g.add_argument("--launch",action="store_true")
    ap.add_argument("--release",type=Path)
    args=ap.parse_args()
    if args.preflight:
        print(json.dumps(preflight(),indent=2))
        return 0
    if args.release is None: ap.error("--launch requires --release")
    return launch(args.release)

if __name__=="__main__":
    raise SystemExit(main())
