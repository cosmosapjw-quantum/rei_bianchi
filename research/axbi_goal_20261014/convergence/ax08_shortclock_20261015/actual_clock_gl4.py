#!/usr/bin/env python3
"""Independent AX08 actual saved trajectory proper-time and b(t) increments.

Uses exact byte-copied AX03 C8 source derivative Gauss4/8, not the original
AX08 accumulated timestamps or integration operator. Scientific model locked.
Checks 3 full frozen ZERO/+half/-q histories and original ±half prefix,
does NOT read a concurrently active continuation or launch any solver.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/"vendor/rei_axbi_shortstep_20261015"))
from shortstep import Background, Family, gauss_batch, stable_dx
SOURCE_SHA="46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0"
LABELS={
    "ZERO":(0., "runs/flrw/32d11e733155/ZERO_composed_001", True),
    "SHEAR_HALF_PLUS":(.005, "runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002",True),
    "SHEAR_MINUS":(-.01, "runs/paired/32d11e733155/SHEAR_MINUS_composed_001",True),
    "SHEAR_HALF_PLUS_PREFIX":(.005,"runs/paired/32d11e733155/SHEAR_HALF_PLUS",False),
    "SHEAR_HALF_MINUS_PREFIX":(-.005,"runs/paired/32d11e733155/SHEAR_HALF_MINUS",False),
}
COLS=(3,4,6)
A_REF=1/21
def hash_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()

def load_one(owner:Path,name:str):
    q,rel,isfull=LABELS[name]
    folder=owner/"research/axbi_goal_20261014"/rel
    path=folder/"history.csv"
    with path.open(newline="") as f:
        head=next(csv.reader(f))
    if len(head)!=25 or tuple(head[j] for j in COLS)!=("time_s","a","b"):
        raise RuntimeError("HOLD_SOURCE_SAVED_HEADER")
    if isfull:
        receipt=json.loads((folder/"COMPOSITION_RECEIPT.json").read_text())
        if receipt.get("status")!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION" or receipt["row_counts"]["history.csv"]["composed_rows"]!=312238:
            raise RuntimeError("HOLD_COMPLETED_SOURCE_UNVERIFIED")
        if hash_file(path)!=receipt["output_sha256"]["history.csv"]:
            raise RuntimeError("HOLD_HISTORY_DATA_IDENTITY_CHANGED")
        row_target=312238
    else:
        terminal=dict(x.split("=",1) for x in (folder/"RETURN.txt").read_text().splitlines() if "=" in x)
        if terminal.get("status")!="STOPPED_CHECKPOINTED" or int(terminal.get("accepted",-1))!=200000 or terminal.get("result")!='Err(InvalidInput("AXBI_RUNTIME_CAP"))':
            raise RuntimeError("HOLD_PREFIX_UNTYPED")
        source=hash_file(folder/"source_identity.txt")
        if source!="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185":
            raise RuntimeError("HOLD_ORIGINAL_SOURCE_CHANGED")
        row_target=200001
    arr=np.loadtxt(path,delimiter=",",skiprows=1,usecols=COLS,dtype=float)
    if arr.shape!=(row_target,3) or not np.isfinite(arr).all():
        raise RuntimeError("HOLD_SAVED_ARRAY_SHAPE_NONFINITE")
    if not(np.all(np.diff(arr[:,0])>0) and np.all(np.diff(arr[:,1])>0)):
        raise RuntimeError("HOLD_CLOCK_MONOTONICITY")
    if arr[0,0]!=0 or abs(arr[0,1]-A_REF)>1e-16:
        raise RuntimeError("HOLD_COMMON_ORIGIN")
    if isfull and arr[-1,1]!=.2:
        raise RuntimeError("HOLD_SAVED_TERMINAL_SCALE")
    if q and np.sign(arr[-1,2])!=np.sign(q):
        raise RuntimeError("HOLD_SIGNED_GEOMETRIC_SOURCE")
    return arr,{"source_sha256":hash_file(path),"rows":row_target,"case":name,"q_ref":q}

def increments(bg,a0,a1,order):
    # Uses AX03 C8 source-frozen background, no accumulated-time subtraction.
    return gauss_batch(bg,a0,a1,order=order,max_step_x=.0028)

def case_audit(data,meta,stride=39):
    sample=np.unique(np.r_[np.arange(0,len(data),stride),len(data)-1])
    source=data[sample]
    ti,ai,bi=source.T
    bg=Background(Family(meta["q_ref"]))
    if abs(bg.aref-A_REF)>1e-16 or bg.aend!=.2:
        raise RuntimeError("HOLD_AX03_REI_PHYSICS_LOCK_DIFFERENT")
    local_start=time.perf_counter()
    dt4,db4=increments(bg,ai[:-1],ai[1:],4)
    elapsed4=time.perf_counter()-local_start
    dt8,db8=increments(bg,ai[:-1],ai[1:],8)
    dts=np.diff(ti);dbs=np.diff(bi)
    if not np.all(np.isfinite(dt4)) or np.any(dt4<=0):
        raise RuntimeError("HOLD_SOURCE_PHYSICAL_GL4_CLOCK")
    if abs(meta["q_ref"])==0 and (np.any(db4!=0) or np.any(dbs!=0)):
        raise RuntimeError("HOLD_SIGNED_ZERO_B")
    dtrel=np.abs(dts-dt4)/dt4
    bscale=np.maximum(np.abs(db4),1e-30)
    dbrel=np.abs(dbs-db4)/bscale
    batch_ordererr=np.abs(dt8-dt4)/dt8
    # Compare all saved proper clocks / b against independent DOP853 source
    x=np.log(ai/A_REF)
    x[0]=0.
    x[-1]=min(x[-1],bg.xmax)
    Y=bg.ivp.sol(x)
    t_independent=Y[0]/bg.href
    b_independent=Y[1]
    diff_t=np.abs(ti-t_independent)
    diff_b=np.abs(bi-b_independent)
    max_dtrel=float(np.max(dtrel))
    return {
        **meta,"sampled_states":len(source),"sampled_intervals":len(source)-1,
        "stride":stride,
        "first_a":float(ai[0]),"last_a":float(ai[-1]),
        "last_elapsed_proper_s":float(ti[-1]),
        "integrator":"original AX03 C8 GL4/GL8 on log1p exact endpoint scales",
        "max_abs_saved_dt_minus_GL4_s":float(np.max(np.abs(dts-dt4))),
        "max_rel_saved_dt_minus_GL4":max_dtrel,
        "p99_rel_saved_dt_minus_GL4":float(np.quantile(dtrel,.99)),
        "median_rel_saved_dt_minus_GL4":float(np.median(dtrel)),
        "max_abs_saved_db_minus_GL4":float(np.max(np.abs(dbs-db4))),
        "max_rel_saved_db_minus_GL4":float(np.max(dbrel)),
        "max_rel_GL4_GL8_time_increment":float(np.max(batch_ordererr)),
        "max_abs_full_t_minus_independent_DOP853_s":float(np.max(diff_t)),
        "max_abs_full_b_minus_independent_DOP853":float(np.max(diff_b)),
        "dt_saved_min_s":float(np.min(dts)),
        "dt_saved_median_s":float(np.median(dts)),
        "max_rel_vs_GL4_index":int(np.argmax(dtrel)),
        "source_GL4_batch_s":elapsed4,
        "gl4_physical_data":(dt4,db4),"sampled_data":source
    }

def signed_prefix(pairplus,pairminus):
    xp,xm=pairplus["sampled_data"],pairminus["sampled_data"]
    if xp.shape!=xm.shape or not np.array_equal(xp[:,1],xm[:,1]):
        raise RuntimeError("UNMATCHED_ORIGINAL_PREFIX_MEAN_SCALE")
    # Exact q -> -q symmetry of density-fixed H and b, distinct from scalar chemistry.
    dt_plus=np.diff(xp[:,0]);dt_minus=np.diff(xm[:,0])
    bp=xp[:,2];bm=xm[:,2]
    plus_dt4,plus_db4=pairplus["gl4_physical_data"]
    minus_dt4,minus_db4=pairminus["gl4_physical_data"]
    return {
      "pair":"original STATIC 200001-row +/-.005 legacy accepted prefix",
      "same_mean_scale_exact":True,
      "max_abs_saved_proper_clock_symmetry_s":float(np.max(abs(xp[:,0]-xm[:,0]))),
      "max_abs_saved_b_antisymmetry":float(np.max(abs(bp+bm))),
      "max_abs_GL4_dt_even_antisymmetric_error_s":float(np.max(abs(plus_dt4-minus_dt4))),
      "max_abs_GL4_db_odd_symmetry_error":float(np.max(abs(plus_db4+minus_db4))),
      "clock_array_identical_bytes_as_float":bool(np.array_equal(xp[:,0],xm[:,0])),
      "a_sample_rows":len(xp),
      "source_chemistry_even_or_odd_claim":"NO, only background clock and geometry symmetry."
    }

def main(owner,output,stride):
    cases={};data={}
    for case in LABELS:
        inp,meta=load_one(owner,case)
        r=case_audit(inp,meta,stride=stride)
        cases[case]={k:v for k,v in r.items() if k not in ("gl4_physical_data","sampled_data")}
        data[case]=r
    signed=signed_prefix(data["SHEAR_HALF_PLUS_PREFIX"],data["SHEAR_HALF_MINUS_PREFIX"])
    # Detect whether a positive and negative full-history q=-.005 case is admitted.
    halfminus_comp=owner/"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_MINUS_composed_001/COMPOSITION_RECEIPT.json"
    metadata={
      "schema":"rei.axbi.actual_accepted_step_clock_increment_gl4.v1",
      "status":"REAL_SAVED_AX08_5_INPUT_CLOCK_ANALYSIS_PASS",
      "scientific_source":"density-fixed Bianchi I frozen AX03 clock; original signed 200k prefix; 3 completed 312238 histories",
      "foreign_supplier":"rei_bianchi AX03 C8 PR123 at immutable 602f9726858b8a183c259ac7eae9fc11d1d7fb99, exact-vendored shortstep and provider",
      "ax03_source_lock_sha256":SOURCE_SHA,
      "actual_full_plusminus_005_complete":False,
      "halfminus_composed_exists":halfminus_comp.exists(),
      "modes":cases,
      "signed_static_prefix":signed,
      "scientific_error_boundary":"dt/dln a and db/dln a background local GL4/8, NOT real coupled ionization ODE AX11 dt/dE/dmu or global source/chemistry accuracy",
      "scientific_admission":"NOT_ISSUED",
      "native_subagent":"NOT_RUN","local_codex":"NOT_USED",
    }
    if not all(x["max_rel_GL4_GL8_time_increment"]<2e-11 for x in cases.values()):
        raise RuntimeError("GL4_GL8_NUMERIC_LOCAL_CLOCK_UNSTABLE")
    output.parent.mkdir(exist_ok=True,parents=True)
    output.write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps({
      "status":metadata["status"],
      "max_abs_signed_pair_clock_s":signed["max_abs_saved_proper_clock_symmetry_s"],
      "max_abs_signed_pair_b_even":signed["max_abs_saved_b_antisymmetry"],
      "source_clock_errors":{k:{
        "max_rel_saved_dt_minus_GL4":v["max_rel_saved_dt_minus_GL4"],
        "max_rel_GL4_GL8_time_increment":v["max_rel_GL4_GL8_time_increment"],
        "max_abs_saved_b_minus_GL4":v["max_abs_saved_db_minus_GL4"]
      } for k,v in cases.items()}},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--stride",type=int,default=39)
    x=p.parse_args()
    main(x.owner_root,x.output,x.stride)
