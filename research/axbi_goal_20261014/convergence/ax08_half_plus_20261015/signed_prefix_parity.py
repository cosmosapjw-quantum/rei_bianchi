#!/usr/bin/env python3
"""Actual AX08 five-case shared-prefix even/odd q decomposition.

Only original 200001-row histories to common accepted a≈0.0887365.
No full signed family, continuum-error estimate, or sign detection.
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE=ROOT/"research/axbi_goal_20261014/runs"
REL={
    "ZERO":"flrw/32d11e733155/ZERO",
    "SHEAR_PLUS":"paired/32d11e733155/SHEAR_PLUS",
    "SHEAR_MINUS":"paired/32d11e733155/SHEAR_MINUS",
    "SHEAR_HALF_PLUS":"paired/32d11e733155/SHEAR_HALF_PLUS",
    "SHEAR_HALF_MINUS":"paired/32d11e733155/SHEAR_HALF_MINUS"
}
Q={"ZERO":0., "SHEAR_PLUS":.01,"SHEAR_MINUS":-.01,
   "SHEAR_HALF_PLUS":.005,"SHEAR_HALF_MINUS":-.005}
N=200001
COLUMNS=("a","x_HII","temperature_K","J2_photon_u_eV_per_H")

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def load_case(k,rel):
    base=BASE/rel
    ret=dict(line.split("=",1) for line in (base/"RETURN.txt").read_text().splitlines() if "=" in line)
    cfg=dict(line.split("=",1) for line in (base/"config.cfg").read_text().splitlines() if "=" in line)
    if ret.get("status")!="STOPPED_CHECKPOINTED" or ret.get("result")!='Err(InvalidInput(\\"AXBI_RUNTIME_CAP\\"))':
        # The first 200k rows are valid even when the original solver stops at a resource cap.
        if ret.get("status")!="STOPPED_CHECKPOINTED" or "AXBI_RUNTIME_CAP" not in ret.get("result",""):
            raise AssertionError("NOT_TYPED_ACCEPTED_STEP_RESOURCE_STOP")
    if int(ret["accepted"])!=200000 or float(cfg["q_ref"])!=Q[k]:
        raise AssertionError("MISMATCHED_ORIGINAL_CASE")
    with (base/"history.csv").open() as saved:
        columns=saved.readline().strip().split(",")
    indices=(4,9,14,22)
    if tuple(columns[j] for j in indices)!=COLUMNS:
        raise AssertionError("HOLD_EXACT_HISTORY_HEADER_BINDING")
    arr=np.loadtxt(base/"history.csv",delimiter=",",skiprows=1,
                   usecols=indices,dtype=np.float64,ndmin=2)
    if arr.shape!=(N,4) or not np.all(np.isfinite(arr)):
        raise AssertionError("BAD_SAVED_ROWS")
    a=arr[:,0]
    if a[0]!=1/21 or abs(a[-1]-0.08873654701704167)>5e-16 or np.any(np.diff(a)<=0):
        raise AssertionError("BAD_PARTIAL_INTERVAL")
    return {"arr":arr,"files":{"history_sha256":digest(base/"history.csv"),
                   "return_sha256":digest(base/"RETURN.txt"),
                   "source_identity_sha256":digest(base/"source_identity.txt")},
            "last_a":float(a[-1])}

def stats(values,a):
    i=int(np.argmax(np.abs(values)))
    return {"sampled_max_abs":float(abs(values[i])),
            "signed_at_max":float(values[i]),
            "a_at_max":float(a[i]),
            "zbar_at_max":float(1/a[i]-1),
            "endpoint":float(values[-1])}

if __name__=="__main__":
    allcases={k:load_case(k,v) for k,v in REL.items()}
    if len({v["files"]["source_identity_sha256"] for v in allcases.values()})!=1:
        raise AssertionError("MISMATCHED_MODEL_COMPILATION")
    a0=1/21
    a1=min(d["last_a"] for d in allcases.values())
    grid=np.exp(np.linspace(math.log(a0),math.log(a1),501))
    grid[0]=a0;grid[-1]=a1
    data={}
    for case,spec in allcases.items():
        a=spec["arr"][:,0]
        if a[0]>a0 or a[-1]<a1:
            raise AssertionError("EXTRAPOLATION_REQUIRED")
        data[case]=[np.interp(grid,a,spec["arr"][:,j]) for j in (1,2,3)]
    summary={}
    for j,name in enumerate(COLUMNS[1:]):
        zero=data["ZERO"][j]
        p=data["SHEAR_PLUS"][j];m=data["SHEAR_MINUS"][j]
        hp=data["SHEAR_HALF_PLUS"][j];hm=data["SHEAR_HALF_MINUS"][j]
        e=(p+m)/2-zero
        o=(p-m)/2
        eh=(hp+hm)/2-zero
        oh=(hp-hm)/2
        summary[name]={"even_at_q_0p01":stats(e,grid),"odd_at_q_0p01":stats(o,grid),
                       "even_at_q_0p005":stats(eh,grid),"odd_at_q_0p005":stats(oh,grid)}
    r={
       "schema":"rei.axbi.signed_prefix_parity.v1",
       "status":"EXECUTED_PARTIAL_SIGNED_FAMILY_SAMPLED_DIAGNOSTIC",
       "scope":"actual original q=0, +/-0.005,+/-0.01 prefix through a=.0887365, not a full history",
       "coordinate":"common 501 ln(a) samples, distinct proper clock not equated",
       "formula":"even=(O(+q)+O(-q))/2-O0; odd=(O(+q)-O(-q))/2",
       "num_uncertainty":"UNKNOWN; zero detected sign/ratio claims issued",
       "a_min":a0,"a_max":a1,"zbar_min":1/a1-1,
       "cases":{k:dict(v["files"],last_a=v["last_a"]) for k,v in allcases.items()},
       "metrics":summary,"scientific_admission":"NOT_ISSUED"
    }
    (HERE/"signed_prefix_parity.json").write_text(json.dumps(r,indent=2)+"\n")
    for name,part in summary.items():
        print(name,"E(q)",part["even_at_q_0p01"]["sampled_max_abs"],
              "O(q)",part["odd_at_q_0p01"]["sampled_max_abs"],
              "E(q/2)",part["even_at_q_0p005"]["sampled_max_abs"],
              "O(q/2)",part["odd_at_q_0p005"]["sampled_max_abs"])
