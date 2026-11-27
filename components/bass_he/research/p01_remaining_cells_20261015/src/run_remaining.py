#!/usr/bin/env python3
"""Durable, sequential, bounded 8-16 original warm P01 cell continuation.

Only midpoint/whole are independent and run as two 1-thread scientific processes.
No standalone Codex, no full original ODE replay, no hidden retries or clipping.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time, traceback
from pathlib import Path
from stage_cell import stage,WORDS
from admit_cell import propagate_and_verify
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(250000)
SRC=Path(__file__).resolve().parent
SCOPE="SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES"

def write_atomic(path,payload):
    tmp=path.with_suffix(".partial.json")
    if tmp.exists():raise ValueError("REFUSE_STALE_PARTIAL_CHECKPOINT")
    tmp.write_text(json.dumps(payload,indent=2)+"\n")
    tmp.replace(path)

def measured(cmd,folder,label,timeout=180):
    root=folder/"evidence"
    out=root/f"{label}.stdout"
    err=root/f"{label}.stderr"
    if out.exists() or err.exists():
        raise ValueError("REFUSE_OVERWRITE_EVIDENCE_LOG:"+label)
    env={**os.environ,"PYTHONPATH":str(folder/"src")+":"+str(SRC),
         "OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1",
         "MKL_NUM_THREADS":"1","NUMEXPR_NUM_THREADS":"1",
         "PYTHONDONTWRITEBYTECODE":"1"}
    start=time.monotonic()
    with out.open("xb") as o,err.open("xb") as e:
        try:
            result=subprocess.run(cmd,cwd=folder,env=env,stdout=o,stderr=e,timeout=timeout)
            code=result.returncode
        except subprocess.TimeoutExpired:
            code=124
    elapsed=time.monotonic()-start
    if code!=0:
        tail=err.read_text(errors="replace")[-3400:]
        raise RuntimeError(f"{label}_FAILED_EXIT_{code}:{tail}")
    return elapsed

def execute(n,old,root):
    if not 8<=n<=16:raise ValueError("CELL_RANGE")
    dest=root/f"HE18_MULTICELL_{n:02d}_20261015"
    start=time.monotonic()
    stage_meta=stage(old,dest,n)
    print(f"CELL {n} STAGED ({stage_meta['cell_s']})",flush=True)
    timings={}
    timings["parallel"]=measured([sys.executable,str(dest/"src/run_parallel.py"),
                                    "--runtime",str(dest)],
                                   dest,"parallel",timeout=100)
    print(f"CELL {n} PARALLEL {timings['parallel']:.3f}s",flush=True)
    timings["assembly"]=measured([sys.executable,str(dest/"src/assemble_certificate.py")],
                                   dest,"assembly",timeout=150)
    print(f"CELL {n} ASSEMBLY {timings['assembly']:.3f}s",flush=True)
    # Caller is the only exact-rational science owner: no output until all
    # physical, source, positivity and per-component checks pass.
    admitted=propagate_and_verify(dest,n)
    result=dict(schema="he18.p01_continuation.cell_result.v1",cell=n,
        status=SCOPE,stage_sha256=stage_meta["frozen_hermite_sha256"],
        timings_s=timings,elapsed_s=time.monotonic()-start,
        science=admitted)
    write_atomic(dest/"results/CONTINUATION_SUMMARY.json",result)
    print(f"CELL {n} ADMITTED cum_tau={admitted['cumulative_tau_outward']} "
          f"gain={str(admitted['gain_display'])[:24]} gas_use={str(admitted['gas_tube_usage_display'])[:24]}",
          flush=True)
    return result

def run(start,through,root,first):
    root.mkdir(parents=True,exist_ok=True)
    progress=root/"CONTINUATION_PROGRESS.json"
    if progress.exists():raise ValueError("REFUSE_OVERWRITE_RESEARCH_CAMPAIGN")
    state=dict(schema="he18.p01_remaining.cells.v1",start=start,through=through,
        selected_original_P01_source="a5c958c414dea41216b445c05f58df837f05cacb",
        status="RUNNING",results=[],blocker=None,native_subagents="NOT_RUN",
        local_codex="NOT_INVOKED",no_existing_owner_worktree_modified=True)
    write_atomic(progress,state)
    previous=first
    for n in range(start,through+1):
        try:
            result=execute(n,previous,root)
        except Exception as e:
            state["status"]="STOPPED_AT_CELL_"+str(n)
            state["blocker"]=str(e)[:5500]
            state["traceback"]=traceback.format_exc()[-7000:]
            write_atomic(progress,state)
            print("SCOPED_STOP",n,state["blocker"],flush=True)
            return 2
        state["results"].append(result)
        state["status"]="RUNNING" if n<through else "COMPLETED_SELECTED_CELLS"
        write_atomic(progress,state)
        previous=root/f"HE18_MULTICELL_{n:02d}_20261015"
    return 0

if __name__=="__main__":
    pa=argparse.ArgumentParser()
    pa.add_argument("--from-cell",type=int,required=True)
    pa.add_argument("--through",type=int,default=16)
    pa.add_argument("--parent-runtime",type=Path,required=True)
    pa.add_argument("--root",type=Path,required=True)
    args=pa.parse_args()
    if args.from_cell>args.through:raise SystemExit("EMPTY_OR_REVERSED_WINDOW")
    raise SystemExit(run(args.from_cell,args.through,
                         args.root,args.parent_runtime.resolve()))
