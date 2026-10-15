"""BASS_HE / AXBI signed-q mean-a vs proper-time diagnostic using provenance-bound caches.

Read-only upstream source. The source ODE and physical closure remain unverified.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from signed_prefix_tau import load, taucum, at_a, EXPECTED_Q, DEFAULT_GRID, PREC, digest

CASE_ORDER=("SHEAR_MINUS","SHEAR_HALF_MINUS","ZERO","SHEAR_HALF_PLUS","SHEAR_PLUS")
EXPECTED_SOURCE_SHA="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
K=PREC(6.6524587321e-29)*PREC(299792458)*PREC(1000000)


def path_for(root,case):
    kind="flrw" if case=="ZERO" else "paired"
    return root/kind/"32d11e733155"/case


def as_float_d(v):
    return format(PREC(v),".20g")


def tau_at_t(t,ne,tau,ts):
    """Integrate linearly interpolated electron density through a time cell."""
    ts=PREC(ts)
    if ts<PREC(t[0]) or ts>PREC(t[-1]):
        raise ValueError("Requested common time outside history domain")
    j=int(np.searchsorted(t,ts,side="right")-1)
    if j==len(t)-1:
        return PREC(tau[-1])
    left=PREC(t[j]);dt=PREC(t[j+1])-left
    f=(ts-left)/dt
    ne_s=PREC(ne[j])+(PREC(ne[j+1])-PREC(ne[j]))*f
    return PREC(tau[j])+K*(ts-left)*(PREC(ne[j])+ne_s)/2


def make_caches(root,cache_dir,source_reports):
    cache_dir.mkdir(parents=True,exist_ok=True)
    receipts={};runtime={}
    for case in CASE_ORDER:
        path=path_for(root,case)
        hist=path/"history.csv"
        key=EXPECTED_Q[case]
        start=time.perf_counter()
        found,d,sha,census=load(hist)
        runtime[case]=time.perf_counter()-start
        if found!=case or sha!=source_reports[case]["history_sha256"]:
            raise ValueError(f"Original history provenance mismatch for {case}")
        sfile=path/"source_identity.txt"
        if digest(sfile)!=EXPECTED_SOURCE_SHA:
            raise ValueError(f"Unreviewed source epoch for {case}")
        if d["time_s"].size != 200001 or abs(d["a"][-1]-DEFAULT_GRID[-1])>5e-15:
            raise ValueError("Unexpected shared prefix length/endpoint")
        tau,_=taucum(d["time_s"],d["ne_proper_cm3"])
        fn=cache_dir/(case+".npz")
        np.savez_compressed(fn, t_s=d["time_s"],a=d["a"],ne_cm3=d["ne_proper_cm3"],
                            tau=np.asarray(tau,dtype=PREC),history_sha256=np.array(sha),
                            source_identity_sha256=np.array(EXPECTED_SOURCE_SHA))
        receipts[case]={
           "history_sha256":sha,"source_identity_sha256":EXPECTED_SOURCE_SHA,
           "cache_filename":fn.name,"cache_sha256":digest(fn),
           "rows":len(d["time_s"]),"census_max":census
        }
    manifest={"schema":"he18.axbi.provenance_cache.v1","cases":receipts,
              "raw_read_digest_parse_seconds":runtime,
              "input_root":"research/axbi_goal_20261014/runs/{flrw,paired}/32d11e733155",
              "note":"Cache contains derived t_s,a,ne and tau; original CSV authority preserved"}
    (cache_dir/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest


def read_caches(cache_dir):
    manifest=json.loads((cache_dir/"MANIFEST.json").read_text())
    by_case={}
    start=time.perf_counter()
    for case in CASE_ORDER:
        receipt=manifest["cases"][case]
        path=cache_dir/receipt["cache_filename"]
        if digest(path)!=receipt["cache_sha256"]:
            raise ValueError(f"Cache SHA mismatch for {case}")
        with np.load(path,allow_pickle=False) as x:
            if x["history_sha256"].item()!=receipt["history_sha256"]:
                raise ValueError(f"Cache source binding mismatch for {case}")
            if x["source_identity_sha256"].item()!=EXPECTED_SOURCE_SHA:
                raise ValueError(f"Cache physics binding mismatch for {case}")
            d={k:np.asarray(x[k]).copy() for k in ("t_s","a","ne_cm3","tau")}
        if d["t_s"].size!=receipt["rows"]:
            raise ValueError(f"Wrong cache grain for {case}")
        by_case[case]=d
    return by_case, manifest, time.perf_counter()-start


def response(by_case,source_reports):
    grid=DEFAULT_GRID
    result={
        "schema":"he18.axbi.signed_q_clock_decomposition.v1",
        "status":"EXPLORATORY_NUMERICAL_NOT_CERTIFIED",
        "mean_a_grid":list(grid),"common_time_strategy":"min_q[t_q(a)]",
        "cases":CASE_ORDER,"q_by_case":{k:EXPECTED_Q[k] for k in CASE_ORDER},
        "sources":{k:source_reports[k]["history_sha256"] for k in CASE_ORDER},
        "source_identity_sha256":EXPECTED_SOURCE_SHA,
        "normal_frame":"non_tilted Bianchi I",
        "units":{"proper_time":"s","optical_depth":"dimensionless"}
    }
    tau_a={}
    t_a={}
    for case in CASE_ORDER:
        d=by_case[case]
        src={"a":d["a"],"time_s":d["t_s"],"ne_proper_cm3":d["ne_cm3"]}
        at=[at_a(src,d["tau"],a) for a in grid]
        t_a[EXPECTED_Q[case]]=np.asarray([v[0] for v in at],dtype=PREC)
        tau_a[EXPECTED_Q[case]]=np.asarray([v[1] for v in at],dtype=PREC)
        previous=np.asarray([PREC(s) for s in source_reports[case]["tau_at_a"]],dtype=PREC)
        if np.max(np.abs(previous-tau_a[EXPECTED_Q[case]]))>PREC("1e-15"):
            raise ValueError(f"Cache mean-a tau parity failure {case}")
    tstar=np.min(np.stack(list(t_a.values())),axis=0)
    tau_t={}
    for case in CASE_ORDER:
        q=EXPECTED_Q[case];d=by_case[case]
        tau_t[q]=np.asarray([tau_at_t(d["t_s"],d["ne_cm3"],d["tau"],ts) for ts in tstar],dtype=PREC)
    result["t_common_s"]=[as_float_d(v) for v in tstar]
    result["t_at_mean_a_s"]={case:[as_float_d(v) for v in t_a[EXPECTED_Q[case]]] for case in CASE_ORDER}
    result["decompositions"]={}
    for h in (0.005,0.01):
        plus,minus=float(h),float(-h)
        E_a=(tau_a[plus]+tau_a[minus])/2-tau_a[0.]
        E_t=(tau_t[plus]+tau_t[minus])/2-tau_t[0.]
        O_a=(tau_a[plus]-tau_a[minus])/2
        O_t=(tau_t[plus]-tau_t[minus])/2
        E_clock=E_a-E_t
        O_clock=O_a-O_t
        threshold=PREC(64)*PREC(np.finfo(np.float64).eps)*np.abs(tau_a[0.])
        ratio=[None if abs(val)<=threshold[i] else as_float_d(E_clock[i]/val)
               for i,val in enumerate(E_a)]
        result["decompositions"][str(h)]={
            "even_mean_a":[as_float_d(v) for v in E_a],
            "even_common_time":[as_float_d(v) for v in E_t],
            "even_clock_residual":[as_float_d(v) for v in E_clock],
            "even_clock_fraction":ratio,
            "odd_mean_a":[as_float_d(v) for v in O_a],
            "odd_common_time":[as_float_d(v) for v in O_t],
            "odd_clock_residual":[as_float_d(v) for v in O_clock],
            "identity_residual_max":float(max(np.max(abs(E_a-E_t-E_clock)),np.max(abs(O_a-O_t-O_clock))))
        }
    result["interpretation"]="algebraic end-clock split; NOT an independent causal shear decomposition; entire result not a certified native ODE error bound"
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path)
    p.add_argument("--source-report-dir",type=Path,required=True)
    p.add_argument("--cache-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--rebuild",action="store_true")
    args=p.parse_args()
    reports={key:json.loads((args.source_report_dir/(key+".json")).read_text()) for key in CASE_ORDER}
    if args.rebuild:
        if args.source_root is None:p.error("--source-root required with --rebuild")
        manifest=make_caches(args.source_root,args.cache_dir,reports)
    vals,manifest,cache_read_s=read_caches(args.cache_dir)
    out=response(vals,reports)
    out["cache_sha256"]={k:v["cache_sha256"] for k,v in manifest["cases"].items()}
    out["cache_total_read_seconds"]=cache_read_s
    if args.rebuild:out["source_read_seconds"]=manifest["raw_read_digest_parse_seconds"]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
