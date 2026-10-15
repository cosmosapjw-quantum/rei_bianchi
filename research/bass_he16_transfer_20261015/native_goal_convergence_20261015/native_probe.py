"""Isolated exploratory native AXBI micro-convergence experiment.

Never writes original rei_bianchi owner worktree, frozen configs or source data.
The driver is unchanged and pinned by binary SHA. This run is explicitly
EXPLORATORY and cannot independently establish a true solution error bound.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

CASE_Q={"ZERO":0.,"SHEAR_HALF_MINUS":-.005,"SHEAR_HALF_PLUS":.005}
TARGETS={"baseline":1e-5,"refined":3e-6}
BINARY_SHA="32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca"
SOURCE_SHA="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
END_ZBAR=19.99
MAX_PER_JOB_SECONDS=120

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(2**20),b""):h.update(chunk)
    return h.hexdigest()

def conf(q,local_target):
    return "\n".join([
        f"q_ref={q}",
        "end_zbar=19.99","same_h=false","escape_fraction=0.2",
        "initial_temperature_k=8.098143045064857",
        "energy_subdivisions=16","n_mu=8","background_panels=4096",
        f"local_target={local_target}","initial_dln_a=0.0001",
        "spectra_every_accepted=10000",
        "max_steps=12000","max_attempts=40000","max_rhs=400000",
        "max_wall_s=110","output_budget_mib=256",""
    ])

def scientific_report(out):
    receipt=out/"RETURN.txt"
    if not receipt.exists():
        return {"native_return":"MISSING"}
    rows=dict(x.split("=",1) for x in receipt.read_text().splitlines() if "=" in x)
    p=out/"history.csv"
    if not p.exists():return {"native_return":rows}
    count=sum(1 for _ in p.open())-1
    return {"native_return":rows,"rows":count,"history_sha256":digest(p),
            "source_identity_sha256":digest(out/"source_identity.txt"),
            "config_sha256":digest(out/"config.cfg")}

def preflight(binary,base,allow_prepared=False):
    if digest(binary)!=BINARY_SHA:
        raise ValueError("Original executable SHA does not match preserved source run")
    if not binary.is_file() or not os.access(binary,os.X_OK):
        raise ValueError("Pinned binary not executable")
    if base.exists() and not allow_prepared:
        raise FileExistsError("Do not overwrite existing exploratory run")
    import shutil
    free=shutil.disk_usage(base.parent).free
    if free<2*(1024**3):
        raise ValueError("Insufficient free scratch disk")
    mem={}
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            mem["available_kib"]=int(line.split()[1])
    if mem.get("available_kib",0)<4*1024**2:
        raise ValueError("Insufficient free RAM")
    return {"binary_sha256":BINARY_SHA,"free_bytes":free,"ram_available_kib":mem["available_kib"]}

def one_run(binary,base,name,level):
    out=base/"runs"/name/level
    if out.exists():
        raise FileExistsError(out)
    cfg=base/"configs"/f"{name}_{level}.cfg"
    requested_command=[str(binary),"--config",str(cfg),"--output",str(out),"--case",name]
    begin=time.perf_counter()
    env={**os.environ,"OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1","RAYON_NUM_THREADS":"1"}
    status="NOT_STARTED"
    code=None
    try:
        executed=subprocess.run(requested_command,text=True,capture_output=True,
                               env=env,timeout=MAX_PER_JOB_SECONDS)
        code=executed.returncode
        status="EXIT_ZERO" if code==0 else "ERROR"
        stdout,stderr=executed.stdout,executed.stderr
    except subprocess.TimeoutExpired as e:
        status="TIMED_OUT_KILLED"
        stdout=e.stdout.decode(errors="replace") if isinstance(e.stdout,bytes) else (e.stdout or "")
        stderr=e.stderr.decode(errors="replace") if isinstance(e.stderr,bytes) else (e.stderr or "")
    record={"case":name,"q_ref":CASE_Q[name],"level":level,
            "target_local_error":TARGETS[level],"status":status,"exit_code":code,
            "elapsed_s":time.perf_counter()-begin,"binary_sha256":BINARY_SHA,
            "config_sha256":digest(cfg),
            "output_relative":str(out.relative_to(base)),"stdout_tail":stdout[-2400:],
            "stderr_tail":stderr[-2400:],"result":scientific_report(out)}
    receipt=base/"receipts"/f"{name}_{level}.json"
    receipt.write_text(json.dumps(record,indent=2)+"\n")
    return record

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--jobs",type=int,default=2)
    p.add_argument("--execute",action="store_true")
    args=p.parse_args()
    if args.jobs not in (1,2):p.error("--jobs must be 1 or 2 to bound resources")
    pre=preflight(args.binary,args.out,allow_prepared=args.execute)
    config_hashes={}
    if args.execute:
        old=json.loads((args.out/"PLAN.json").read_text())
        if old["source_frozen_binary_sha256"] != BINARY_SHA or old["cases"] != CASE_Q or old["targets"] != TARGETS or old["resource"]["parallel_jobs"] != args.jobs:
            raise ValueError("Frozen plan/physics/resource contract changed")
        if (args.out/"runs").exists() or any((args.out/"receipts").iterdir()):
            raise FileExistsError("Already attempted plan; cannot launch twice")
        for name,q in CASE_Q.items():
            for level,target in TARGETS.items():
                path=args.out/"configs"/f"{name}_{level}.cfg"
                if path.read_text() != conf(q,target):
                    raise ValueError("Frozen config content no longer matches")
                config_hashes[path.name]=digest(path)
        if config_hashes != old["config_sha256"]:
            raise ValueError("Frozen config SHA mismatch")
    else:
        (args.out/"configs").mkdir(parents=True)
        (args.out/"receipts").mkdir()
        for name,q in CASE_Q.items():
            for level,target in TARGETS.items():
                path=args.out/"configs"/f"{name}_{level}.cfg"
                path.write_text(conf(q,target))
                config_hashes[path.name]=digest(path)
    manifest={
        "schema":"he18.axbi.exploratory_native_goal_convergence.v1",
        "scientific_admission":"EXPLORATORY_NONAUTHORITATIVE",
        "source_frozen_binary_sha256":BINARY_SHA,
        "original_source_identity_sha256":SOURCE_SHA,
        "physics":"AXBI cold Plancklike_MD14_BB50K, normal comoving, fixed original rates",
        "end_zbar":END_ZBAR,
        "targets":TARGETS,
        "cases":CASE_Q,
        "max_per_job_seconds":MAX_PER_JOB_SECONDS,
        "resource":{"parallel_jobs":args.jobs,"steps_max":12000,"disk_max_mib_per_case":256,
                    "preflight":pre},
        "config_sha256":config_hashes,
        "owner_worktree_modified":False,
        "native_subagents":"NOT_RUN",
        "source_ODE_error_certified":False
    }
    if not args.execute:
        (args.out/"PLAN.json").write_text(json.dumps(manifest,indent=2)+"\n")
    if not args.execute:
        print(json.dumps({"status":"PLAN_ONLY","path":str(args.out),"configs":config_hashes},indent=2))
        return
    jobs=[(case,level) for case in CASE_Q for level in TARGETS]
    start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures=[pool.submit(one_run,args.binary,args.out,case,level) for case,level in jobs]
        records=[f.result() for f in futures]
    result={"schema":"he18.axbi.native_run_receipts.v1",
            "wall_s":time.perf_counter()-start,"records":records,
            "successful":sum(x["status"]=="EXIT_ZERO" for x in records),
            "scientific_admission":"NOT_ISSUED"}
    (args.out/"RUN_SUMMARY.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":"RUNS_ATTEMPTED",
                      "wall_s":result["wall_s"],
                      "success":result["successful"],
                      "cases":[[x["case"],x["level"],x["status"],x["elapsed_s"]] for x in records]},indent=2))
if __name__=="__main__":
    main()
