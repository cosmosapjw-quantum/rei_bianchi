"""Measure the complete bounded runner process and its waited descendants.

This outer launcher imports no science. Its final metadata write is outside the
measured subprocess boundary and is not recursively included in that boundary.
"""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def save_create_only(path,value):
    temporary=path.with_name(path.name+".tmp")
    with temporary.open("x",encoding="utf-8") as handle:
        json.dump(value,handle,indent=2,sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.link(temporary,path)
    temporary.unlink()
    descriptor=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(descriptor)
    finally:os.close(descriptor)


if __name__=="__main__":
    outer_cpu0=time.process_time()
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=["validate","plot"],required=True)
    parser.add_argument("--source-commit",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--receipt",required=True)
    parser.add_argument("--saved-json")
    args=parser.parse_args()
    receipt_path=Path(args.receipt).resolve()
    receipt_path.parent.mkdir(parents=True,exist_ok=True)
    if receipt_path.exists() or receipt_path.with_name(receipt_path.name+".tmp").exists():
        raise SystemExit("external resource receipt already exists")
    cpu_cap,wall_cap=(12,40) if args.mode=="validate" else (8,20)
    command=[sys.executable,"-B",str(ROOT/"scripts/run_bounded.py"),"--mode",args.mode,"--source-commit",args.source_commit,"--output",str(Path(args.output).resolve())]
    if args.saved_json:command.extend(["--saved-json",str(Path(args.saved_json).resolve())])
    env=os.environ.copy()
    env.update({name:"1" for name in ["OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"]})
    env["PYTHONDONTWRITEBYTECODE"]="1"
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(cpu_cap,cpu_cap))
        resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    started=datetime.now(timezone.utc).isoformat()
    wall0=time.perf_counter()
    process=subprocess.Popen(command,cwd=ROOT,env=env,preexec_fn=limits,start_new_session=True)
    timed_out=False
    try:
        # Inner runner enforces the unchanged wall cap and saves its receipt;
        # this margin permits only termination and final receipt cleanup.
        exit_code=process.wait(timeout=wall_cap+2)
    except subprocess.TimeoutExpired:
        timed_out=True
        os.killpg(process.pid,signal.SIGKILL)
        exit_code=process.wait()
    wall=time.perf_counter()-wall0
    finished=datetime.now(timezone.utc).isoformat()
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    whole_cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)
    outer_cpu=time.process_time()-outer_cpu0
    result={"mode":args.mode,"source_commit":args.source_commit,"command":command,
            "measurement_scope":"Complete run_bounded.py subprocess lifetime, including Python startup, all waited descendants, validation or plot, inner final receipts and interpreter shutdown",
            "outer_orchestration_scope":"Outer Python main body through subprocess measurement; final external metadata serialization/fsync and interpreter startup/shutdown are excluded and not recursively measured",
            "start":started,"finish":finished,"exit_code":exit_code,"timed_out":timed_out,
            "whole_process_cpu_s":whole_cpu,"whole_process_wall_s":wall,
            "outer_orchestration_cpu_s":outer_cpu,"peak_subprocess_rss_kib":after.ru_maxrss,
            "limits":{"whole_process_cpu_s":cpu_cap,"whole_process_wall_s":wall_cap,"timeout_cleanup_margin_s":2,"address_space_bytes":512*1024**2,"single_thread":True},
            "cpu_cap_met":whole_cpu<=cpu_cap,"wall_cap_met":wall<=wall_cap,
            "scientific_suite_runs_authorized":1 if args.mode=="validate" else 0,
            "budget_reset":False}
    result["status"]="PASS" if exit_code==0 and not timed_out and result["cpu_cap_met"] and result["wall_cap_met"] else "FAIL"
    save_create_only(receipt_path,result)
    print(json.dumps({key:result[key] for key in ["mode","status","exit_code","whole_process_cpu_s","whole_process_wall_s","outer_orchestration_cpu_s","peak_subprocess_rss_kib"]}))
    sys.exit(0 if result["status"]=="PASS" else 1)
