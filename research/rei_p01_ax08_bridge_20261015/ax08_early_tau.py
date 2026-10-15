#!/usr/bin/env python3
"""Time-window matched (not model-matched) AX08 cold vs warm P01 optical ledgers.

Independent actual frozen AX08 original five-case histories are read ONLY
through 1e11 proper seconds, while an AX08 signed continuation runs separately.
No warm source/gas/clock parameters are imported into the cold solver.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from hashlib import sha256
import json
from pathlib import Path
import statistics
import time
import numpy as np

from certified16 import CSV_PATH, CSV_SHA, SOURCE_COMMIT, source_rows

CASE_REL={
 "ZERO":"runs/flrw/32d11e733155/ZERO",
 "SHEAR_MINUS":"runs/paired/32d11e733155/SHEAR_MINUS",
 "SHEAR_HALF_MINUS":"runs/paired/32d11e733155/SHEAR_HALF_MINUS",
 "SHEAR_HALF_PLUS":"runs/paired/32d11e733155/SHEAR_HALF_PLUS",
 "SHEAR_PLUS":"runs/paired/32d11e733155/SHEAR_PLUS"
}
QREF={"ZERO":0.0,"SHEAR_MINUS":-0.01,"SHEAR_HALF_MINUS":-0.005,
      "SHEAR_HALF_PLUS":0.005,"SHEAR_PLUS":0.01}
OWNER_SOURCE_ID="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
DURATION=1e11
BOUNDARIES=np.arange(1,17,dtype=np.float64)*6250000000
# Current owner igm_thermal.rs constant, NOT assumed identical to frozen P01.
SIGMA_T=6.6524587051e-25  # cm^2
C_CGS=2.99792458e10 # cm/s
FACTOR=C_CGS*SIGMA_T
HERE=Path(__file__).resolve().parent
RESULTS=HERE/"results"

def file_sha(path):
    h=sha256()
    with path.open("rb") as f:
        for piece in iter(lambda:f.read(65536),b""):
            h.update(piece)
    return h.hexdigest()

def load_case(owner,case,stop=DURATION):
    if case not in CASE_REL:
        raise ValueError("HOLD_UNRECOGNIZED_AX08_CASE")
    folder=owner/"research/axbi_goal_20261014"/CASE_REL[case]
    if file_sha(folder/"source_identity.txt")!=OWNER_SOURCE_ID:
        raise ValueError("HOLD_PHYSICAL_SOURCE_IDENTITY_CHANGED")
    config={}
    for line in (folder/"config.cfg").read_text().splitlines():
        if "=" in line:
            k,v=line.split("=",1)
            config[k.strip()]=v.strip()
    if float(config["q_ref"])!=QREF[case]:
        raise ValueError("HOLD_QREF_CHANGED")
    ret={}
    for line in (folder/"RETURN.txt").read_text().splitlines():
        if "=" in line:
            k,v=line.split("=",1)
            ret[k]=v
    if (ret.get("status")!="STOPPED_CHECKPOINTED"
            or "AXBI_RUNTIME_CAP" not in ret.get("result","")
            or int(ret.get("accepted",-1))!=200000):
        raise ValueError("HOLD_ORIGINAL_PREFIX_NOT_TYPED")
    filepath=folder/"history.csv"
    header=None
    clipped=sha256()
    tx=[];ex=[];ax=[];xe=[];temp=[]
    max_charge_relative=0.0
    with filepath.open("r",newline="") as f:
        raw=f.readline()
        clipped.update(raw.encode())
        header=raw.strip().split(",")
        required={"case_id","time_s","a","ne_proper_cm3","nH_proper_cm3",
                  "x_HII","x_HeII","x_HeIII","temperature_K"}
        if not required.issubset(header):
            raise ValueError("HOLD_HISTORY_HEADER_REGISTRY_CHANGED")
        idx={name:header.index(name) for name in required}
        found_beyond=False
        for line in f:
            item=line.strip().split(",")
            if len(item)!=len(header) or item[idx["case_id"]]!=case:
                raise ValueError("HOLD_HISTORY_MALFORMED_OR_CASE_ID")
            t=float(item[idx["time_s"]])
            a=float(item[idx["a"]])
            ne=float(item[idx["ne_proper_cm3"]])
            nh=float(item[idx["nH_proper_cm3"]])
            xh=float(item[idx["x_HII"]])
            h2=float(item[idx["x_HeII"]]);h3=float(item[idx["x_HeIII"]])
            tg=float(item[idx["temperature_K"]])
            if not all(np.isfinite(v) for v in (t,a,ne,nh,xh,h2,h3,tg)):
                raise ValueError("HOLD_NONFINITE_COLD_SOURCE")
            if ne<0 or nh<=0 or tg<=0 or not(0<=xh<=1 and 0<=h2<=1 and 0<=h3<=1):
                raise ValueError("HOLD_COLD_GAS_DOMAIN")
            # The actual source tracks ne=nH*x_HII+ nHe*(x_HeII+2*x_HeIII).
            # This tight local check is independent of any exact global source freeze.
            yhe=0.2454/(4*(1-0.2454))
            charged=nh*(xh+yhe*(h2+2*h3))
            charge_relative=abs(charged-ne)/max(ne,1e-18)
            max_charge_relative=max(max_charge_relative,charge_relative)
            if charge_relative>1e-10:
                raise ValueError("HOLD_ION_CHARGE_OR_HELIUM_NORMALIZATION")
            if tx and (t<=tx[-1] or a<=ax[-1]):
                raise ValueError("HOLD_NONMONOTONE_COLD_PROPER_CLOCK")
            tx.append(t);ex.append(ne);ax.append(a);xe.append(xh);temp.append(tg)
            clipped.update(line.encode())
            if t>stop:
                found_beyond=True
                break
    if not found_beyond or tx[0]!=0 or abs(ax[0]-1/21)>1e-16:
        raise ValueError("HOLD_AX08_EARLY_TIME_WINDOW_OUTSIDE_ORIGIN")
    return {"case":case,"q_ref":QREF[case],
           "prefix_sha256":clipped.hexdigest(),"source_identity_sha256":OWNER_SOURCE_ID,
           "prefix_rows":len(tx),"interval_max_s":tx[-1],
           "max_charge_relative_residual":max_charge_relative,
           "arrays":{"t":np.asarray(tx),"ne":np.asarray(ex),
                     "a":np.asarray(ax),"x_HII":np.asarray(xe),
                     "Tgas_K":np.asarray(temp)}}

def optical_history(times,ne,targets):
    """O(N+M) NumPy trapezoid prefix and linearly interpolated target endpoint."""
    if len(times)!=len(ne) or np.any(np.diff(times)<=0) or np.any(ne<0):
        raise ValueError("INVALID_MONOTONE_HISTORY")
    if len(times)<3 or targets[0]<times[0] or targets[-1]>times[-1]:
        raise ValueError("TARGET_OUTSIDE_SUPPORTED_PREFIX")
    accum=np.empty(len(times),dtype=np.float64)
    accum[0]=0.0
    np.cumsum((ne[1:]+ne[:-1])*0.5*np.diff(times),out=accum[1:])
    j=np.searchsorted(times,targets,side="right")-1
    j=np.minimum(j,len(times)-2)
    frac=(targets-times[j])/(times[j+1]-times[j])
    interp=ne[j]+frac*(ne[j+1]-ne[j])
    local=0.5*(ne[j]+interp)*(targets-times[j])
    return FACTOR*(accum[j]+local)

def kahan_tau(times,ne,tmax):
    # Independent scalar accumulation using Kahan instead of NumPy cumsum.
    total=0.
    compensation=0.
    for i in range(1,len(times)):
        lo=times[i-1]
        hi=times[i]
        if lo>=tmax:break
        top=min(hi,tmax)
        f=(top-lo)/(hi-lo)
        right=ne[i-1]+f*(ne[i]-ne[i-1])
        add=(top-lo)*(ne[i-1]+right)*0.5
        y=add-compensation
        t=total+y
        compensation=(t-total)-y
        total=t
        if hi>=tmax:break
    return FACTOR*total

def subsampled_history(times,ne,step,targets):
    idx=np.arange(0,len(times),step)
    if idx[-1]!=len(times)-1:
        idx=np.r_[idx,len(times)-1]
    return optical_history(times[idx],ne[idx],targets)

def evaluate(owner,bench_repetitions=5):
    warm_rows,_=source_rows()
    cases={k:load_case(owner,k) for k in CASE_REL}
    report={}
    durations={}
    for name,data in cases.items():
        t=data["arrays"]["t"];ne=data["arrays"]["ne"]
        direct=optical_history(t,ne,BOUNDARIES)
        scalar=kahan_tau(t,ne,DURATION)
        if abs(scalar-direct[-1])>max(1e-25,1e-11*direct[-1]):
            raise RuntimeError("HOLD_INDEPENDENT_KAHAN_NUMPY_MISMATCH:"+name)
        e2=subsampled_history(t,ne,2,BOUNDARIES)
        e4=subsampled_history(t,ne,4,BOUNDARIES)
        e8=subsampled_history(t,ne,8,BOUNDARIES)
        report[name]={
            "q_ref":QREF[name],
            "prefix_rows":data["prefix_rows"],
            "prefix_sha256":data["prefix_sha256"],
            "max_charge_relative_residual":data["max_charge_relative_residual"],
            "start_ne_cm3":float(ne[0]),
            "end_ne_cm3":float(np.interp(DURATION,t,ne)),
            "start_x_HII":float(data["arrays"]["x_HII"][0]),
            "start_Tgas_K":float(data["arrays"]["Tgas_K"][0]),
            "end_Tgas_K":float(np.interp(DURATION,t,data["arrays"]["Tgas_K"])),
            "tau_cumulative_16":[float(x) for x in direct],
            "tau_final":float(direct[-1]),
            "tau_kahan_scalar":float(scalar),
            "tau_subsample2_max_abs":float(np.max(abs(direct-e2))),
            "tau_subsample4_max_abs":float(np.max(abs(direct-e4))),
            "tau_subsample8_max_abs":float(np.max(abs(direct-e8))),
            "scope":"actual original frozen AX08 cold-IGM history, equal elapsed proper time, not same warm physical scenario"}
        t0=time.perf_counter()
        for _ in range(bench_repetitions):kahan_tau(t,ne,DURATION)
        scalar_s=(time.perf_counter()-t0)/bench_repetitions
        t0=time.perf_counter()
        for _ in range(bench_repetitions):optical_history(t,ne,BOUNDARIES)
        numpy_s=(time.perf_counter()-t0)/bench_repetitions
        durations[name]={"python_kahan_s":scalar_s,"numpy_vectorized_s":numpy_s,
                          "kernel_speedup":scalar_s/numpy_s}
    old=np.array(report["ZERO"]["tau_cumulative_16"])
    if np.any(np.diff(old)<=0):raise ValueError("ZERO_COLD_TAU_NOT_POSITIVE")
    comparison=[]
    for i,w in enumerate(warm_rows):
        comparison.append({
         "cell":i+1,"proper_elapsed_s":int(BOUNDARIES[i]),
         "warm_P01_source_tau_lower":w["source_tau_lower"],
         "warm_P01_source_tau_upper":w["source_tau_upper"],
         "cold_AX08_tau_ZERO":report["ZERO"]["tau_cumulative_16"][i],
         "cold_AX08_tau_MINUS":report["SHEAR_MINUS"]["tau_cumulative_16"][i],
         "cold_AX08_tau_HALF_MINUS":report["SHEAR_HALF_MINUS"]["tau_cumulative_16"][i],
         "cold_AX08_tau_HALF_PLUS":report["SHEAR_HALF_PLUS"]["tau_cumulative_16"][i],
         "cold_AX08_tau_PLUS":report["SHEAR_PLUS"]["tau_cumulative_16"][i]
        })
    from decimal import Decimal
    ratio=str(Decimal(warm_rows[-1]["source_tau_upper"])/Decimal(str(old[-1])))
    return {
        "schema":"rei.axbi.p01_16_cell_same_duration_distinct_source.v1",
        "status":"SCOPED_DIFFERENT_PHYSICS_SAME_DURATION_REPRODUCED",
        "provenance":{
          "warm_BASS_HE_commit":"b0af50b052862320896085fac70250f51c077944",
          "warm_original_source_commit":SOURCE_COMMIT,
          "warm_csv_sha256":CSV_SHA,
          "cold_original_source_identity_sha256":OWNER_SOURCE_ID,
          "thomson_constant_source":"rei_bianchi rust/rei_microphysics/src/igm_thermal.rs SIGMA_T_CM2=6.6524587051e-25",
          "C_cm_s":C_CGS,"sigma_t_cm2":SIGMA_T
        },
        "clock":"elapsed proper seconds 0..1e11 independently from each source initial epoch, NOT physically coeval",
        "cold_integral":"tau(t)=c*sigma_T*integral_0^t ne_proper_cm3 dt; piecewise-linear interpolation of stored ne",
        "warm_integral":"16 cell SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES",
        "time_subsampling":"2/4/8 saved-row stride is an internal sampling sensitivity only; does not certify ODE time convergence",
        "warm_to_cold_zero_final_ratio":ratio,
        "cases":report,
        "rows":comparison,
        "kernel_benchmark":durations,
        "claim_boundary":"Not a model-matched comparison; different source, gas, microphysics, initial epoch, background. Source-specific tau cannot be inserted as AX08 foreground or observer CMB tau.",
        "scientific_admission":"NOT_ISSUED"
    }

def save(report):
    RESULTS.mkdir(exist_ok=True,parents=True)
    (RESULTS/"ax08_cold_vs_p01_warm.json").write_text(json.dumps(report,indent=2)+"\n")
    fields=list(report["rows"][0])
    with (RESULTS/"ax08_cold_vs_p01_warm.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        writer.writeheader();writer.writerows(report["rows"])

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner-root",type=Path,required=True)
    args=p.parse_args()
    r=evaluate(args.owner_root)
    save(r)
    print(json.dumps({"status":r["status"],
       "cold_end_taus":{k:z["tau_final"] for k,z in r["cases"].items()},
       "warm_to_cold_zero_final_ratio":r["warm_to_cold_zero_final_ratio"],
       "cold_zero_sampling_error_8":r["cases"]["ZERO"]["tau_subsample8_max_abs"],
       "kernel_benchmark_speedup":{k:v["kernel_speedup"] for k,v in r["kernel_benchmark"].items()}},indent=2))
