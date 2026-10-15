"""Read-only signed-q optical-depth response on the shared AXBI prefix.

All data from original COLD histories. Geometric coordinates are mean scale factor
a and elapsed normal-frame proper time (s). No certified source-ODE error bound.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

from cold_history_tau import HE_TO_H, OPACITY_FACTOR

DEFAULT_GRID=(0.055,0.06,0.07,0.08,0.08873654701704167)
EXPECTED_Q={"SHEAR_MINUS":-0.01,"SHEAR_HALF_MINUS":-0.005,"ZERO":0.0,
            "SHEAR_HALF_PLUS":0.005,"SHEAR_PLUS":0.01}
COLUMNS=("time_s","a","nH_proper_cm3","ne_proper_cm3",
         "x_HII","x_HeII","x_HeIII")
PREC=np.longdouble

def digest(path):
    sha=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(2**20),b""):
            sha.update(chunk)
    return sha.hexdigest()

def load(path):
    path=Path(path)
    before=path.stat()
    h=digest(path)
    arrays={key:[] for key in COLUMNS}
    case=None
    with path.open(newline="") as f:
        reader=csv.reader(f)
        header=next(reader)
        ind={key:header.index(key) for key in COLUMNS}
        ci=header.index("case_id");qi=header.index("q_ref")
        for row in reader:
            if not row:continue
            if case is None:
                case=row[ci]
                if case not in EXPECTED_Q:raise ValueError("Unknown signed case")
            if row[ci]!=case or float(row[qi])!=EXPECTED_Q[case]:
                raise ValueError("Case/q_ref changes across one history")
            for key in COLUMNS:arrays[key].append(float(row[ind[key]]))
    after=path.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
        raise ValueError("Source history mutated during read")
    d={key:np.asarray(value,dtype=np.float64) for key,value in arrays.items()}
    n=d["time_s"].size
    if n<2 or any(v.size!=n or not np.all(np.isfinite(v)) for v in d.values()):
        raise ValueError("Incomplete/nonfinite history")
    if not np.all(np.diff(d["time_s"])>0) or not np.all(np.diff(d["a"])>0):
        raise ValueError("Elapsed proper times / scale factors not strictly increasing")
    x=d["x_HII"];y=d["x_HeII"];z=d["x_HeIII"]
    if np.any((x<0)|(x>1)|(y<0)|(z<0)|(y+z>1)):
        raise ValueError("Species simplex violated")
    ne_census=d["nH_proper_cm3"]*(x+HE_TO_H*(y+2*z))
    if np.any(d["nH_proper_cm3"]<=0) or np.any(d["ne_proper_cm3"]<0):
        raise ValueError("Invalid proper density")
    census=float(np.max(abs(ne_census-d["ne_proper_cm3"])/d["nH_proper_cm3"]))
    if census>1e-10:raise ValueError(f"Electron census mismatch {census}")
    return case,d,h,census

def taucum(t,ne):
    if len(t)!=len(ne) or len(t)<2:raise ValueError("Bad grid")
    t=np.asarray(t,dtype=PREC)
    ne=np.asarray(ne,dtype=PREC)
    increments=np.diff(t)*(PREC(OPACITY_FACTOR)/2)*(ne[:-1]+ne[1:])
    return np.concatenate(([PREC(0)],np.cumsum(increments,dtype=PREC))),increments

def at_a(d,tau,a_target):
    a=d["a"];t=d["time_s"];ne=d["ne_proper_cm3"]
    if not (a[0]<=a_target<=a[-1]):raise ValueError("Target outside mean scale interval")
    j=int(np.searchsorted(a,a_target,side="right")-1)
    if j==len(a)-1:return (PREC(t[-1]),tau[-1])
    ratio=PREC(a_target-a[j])/PREC(a[j+1]-a[j])
    ts=PREC(t[j])+ratio*PREC(t[j+1]-t[j])
    ne_s=PREC(ne[j])+ratio*PREC(ne[j+1]-ne[j])
    extra=(ts-PREC(t[j]))*(PREC(OPACITY_FACTOR)/2)*(PREC(ne[j])+ne_s)
    return ts,tau[j]+extra

def point(d,grid):
    tau,inc=taucum(d["time_s"],d["ne_proper_cm3"])
    at=[at_a(d,tau,a_target) for a_target in grid]
    endpoint_fsum=math.fsum(map(float,inc))
    dectau={}
    for stride in (2,4,8):
        idx=np.arange(0,len(d["time_s"]),stride,dtype=int)
        if idx[-1]!=len(d["time_s"])-1:idx=np.r_[idx,len(d["time_s"])-1]
        tsmall=d["time_s"][idx];nesmall=d["ne_proper_cm3"][idx]
        ts,incs=taucum(tsmall,nesmall)
        dectau[str(stride)]=float(ts[-1])
    return {
      "grid":list(grid),
      "tau_at_a":[format(v[1],".20g") for v in at],
      "proper_seconds_at_a":[format(v[0],".20g") for v in at],
      "full_tau_fsum":format(endpoint_fsum,".17g"),
      "full_tau_longdouble":format(tau[-1],".20g"),
      "decimated_end_tau":dectau,
      "max_decimation_difference":max(abs(float(tau[-1])-v) for v in dectau.values())
    }

def calculate(path,grid=DEFAULT_GRID):
    case,d,h,census=load(path)
    if d["time_s"].size!=200001:
        raise ValueError(f"Expected 200001 accepted prefix rows, got {d['time_s'].size}")
    final_a=float(d["a"][-1])
    if abs(final_a-grid[-1])>5e-15:
        raise ValueError("Final shared scale factor changed")
    out={
      "schema":"he18.axbi.signed_prefix_tau.v1",
      "status":"SOURCE_SCOPED_NUMERICAL_DIAGNOSTIC_NOT_OD E_CERTIFIED".replace(" ",""),
      "case":case,"q_ref":EXPECTED_Q[case],
      "history_sha256":h,"rows":d["time_s"].size,
      "terminal_a":final_a,"terminal_zbar":float(1/final_a-1),
      "electron_census_max_abs_over_nH":census,
      "units":{"t":"proper_seconds_since_zbar20","nH_and_ne":"proper_cm-3","tau":"dimensionless"},
      "method":"piecewise linear n_e and a(t); longdouble composite trapezoid; sampled-node error not source ODE bound"
    }
    out.update(point(d,grid))
    return out

def combine(reports):
    items={r["q_ref"]:r for r in reports}
    if set(items)!={-0.01,-0.005,0.,0.005,0.01}:raise ValueError("Five q values required")
    grid=items[0.]["grid"]
    if not all(r["grid"]==grid for r in reports):raise ValueError("Different scale grid")
    tau={q:np.asarray([PREC(v) for v in row["tau_at_a"]],dtype=PREC)
         for q,row in items.items()}
    t={q:np.asarray([PREC(v) for v in row["proper_seconds_at_a"]],dtype=PREC)
       for q,row in items.items()}
    base=tau[0.]
    o05=(tau[0.005]-tau[-0.005])/2
    o10=(tau[0.01]-tau[-0.01])/2
    e05=(tau[0.005]+tau[-0.005])/2-base
    e10=(tau[0.01]+tau[-0.01])/2-base
    # Correct leading q^2 and q^3 coefficients for q magnitudes h and 2h.
    h=PREC(0.005)
    c4=(e10-4*e05)/(12*h**4)
    c2=(16*e05-e10)/(12*h**2)
    c3=(o10-2*o05)/(6*h**3)
    c1=(8*o05-o10)/(6*h)
    threshold=PREC(64)*PREC(np.finfo(np.float64).eps)*np.abs(base)
    ratio=[None if abs(v)<=threshold[i] else format(e10[i]/v,".12g") for i,v in enumerate(e05)]
    return {
      "schema":"he18.axbi.signed_q_tau_response.v1",
      "status":"EXPLORATORY_SOURCE_SCOPED_UNCERTIFIED",
      "q_values":sorted(items),
      "comparison":"matched mean a=1/(1+zbar), NOT common proper time, NOT direction-dependent redshift",
      "a_grid":grid,
      "base_tau_ZERO":[format(v,".18g") for v in base],
      "even_half_q005":[format(v,".18g") for v in e05],
      "even_half_q010":[format(v,".18g") for v in e10],
      "odd_half_q005":[format(v,".18g") for v in o05],
      "odd_half_q010":[format(v,".18g") for v in o10],
      "even_ratio_q010_to_q005":ratio,
      "quadratic_coefficient_q2":[format(v,".15g") for v in c2],
      "quartic_coefficient_q4":[format(v,".15g") for v in c4],
      "linear_coefficient_q1":[format(v,".15g") for v in c1],
      "cubic_coefficient_q3":[format(v,".15g") for v in c3],
      "even_drift_at_fixed_a":[format(v,".15g") for v in (t[0.005]+t[-0.005])/2-t[0.]],
      "odd_clock_half_difference_s":[format(v,".15g") for v in (t[0.005]-t[-0.005])/2],
      "input_sha256":{r["case"]:r["history_sha256"] for r in reports},
      "max_electron_census_mismatch":max(r["electron_census_max_abs_over_nH"] for r in reports),
      "limitation":"finite differences of independently evolved histories; not certified physical shear detection or source-ODE error bound; q1/q3 and q2/q4 decomposition is polynomial stencil diagnostic"
    }

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="operation",required=True)
    single=sub.add_parser("single")
    single.add_argument("--history",type=Path,required=True)
    single.add_argument("--out",type=Path,required=True)
    joined=sub.add_parser("combine")
    joined.add_argument("--inputs",nargs=5,type=Path,required=True)
    joined.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.operation=="single":
        result=calculate(args.history)
    else:
        result=combine([json.loads(pth.read_text()) for pth in args.inputs])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
