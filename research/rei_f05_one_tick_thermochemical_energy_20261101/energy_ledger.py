#!/usr/bin/env python3
"""Source-authentic original-26-event SDIRK2 integrated physical energy budget.

Reads ORIGINAL accepted tick160 *full uncertain* 46080-cell parent and runs
unmodified native MPRK22(1)+Alexander SDIRK2 full/half/half at fixed original
clock. Quantifies native photoheat and OTS, sink and thermal residual, not a
joint-source rigorous D_h remainder or first-canonical-interval acceptance.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import math
import sys
from pathlib import Path
import numpy as np

N = 46080
SRC_SHA = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
ARR_SHA = "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_SHA = "579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
LANES = ("LOCAL_NEUTRAL_HAZARD_PRIMARY", "RECOMBINATION_WEIGHTED_AUDITOR",
         "SCRIPT_SELF_SHIELDING_AUDITOR")
LOCAL_GATE = 2e-4
PUBLIC_WIDTH_GATE = 2e-3
HISTORIC_LOGT_FAIL = 2.1245050576368385e-4
CHANNELS = ("photo_total", "photo_primary", "ots_resolved", "thermal_native_rhs",
            "nonphoto_sink", "chemical", "escaped", "unresolved", "thermal_energy_gain")


def load(name, path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:
        raise ImportError(path)
    mod=importlib.util.module_from_spec(s)
    sys.modules[name]=mod
    s.loader.exec_module(mod)
    return mod


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(2**20),b""):
            h.update(b)
    return h.hexdigest()


def midpoint(q):
    return 0.5*np.asarray(q.lo)+0.5*np.asarray(q.hi)


def interval_abs_upper(q):
    return np.maximum(abs(np.asarray(q.lo)),abs(np.asarray(q.hi)))


def weighted(g, x, y, duration):
    """Original SDIRK final weights, in seconds."""
    if not (0 < g < 1 and duration > 0):
        raise ValueError("INVALID_ORIGINAL_SDIRK_TIME")
    return duration*((1-g)*x+g*y)


def half_difference(full, first, second):
    return full-(first+second)


def zero_in(q):
    return (np.asarray(q.lo)<=0)&(np.asarray(q.hi)>=0)


def normalized_data(full, first, second, nuclei):
    """Per-H-integrated source and independent output-box difference.

    Exact shared-source correlation is NOT represented by separate interval
    subtraction. No 2e-4 gate is ever applied to erg/H energy diagnostics.
    """
    if np.any(nuclei <= 0):
        raise ValueError("NONPOSITIVE_SOURCE_H")
    dh=half_difference(full,first,second)/nuclei
    ff=full/nuclei
    hh=(first+second)/nuclei
    return {
        "full_center":midpoint(ff),
        "twohalf_center":midpoint(hh),
        "difference_center":midpoint(dh),
        "difference_independent_upper":interval_abs_upper(dh),
        "difference_lower":np.asarray(dh.lo),
        "difference_upper":np.asarray(dh.hi),
    }


def verify_ots_ledger(event):
    """Original OTS energy operator closure, separate from external photon heat."""
    residual=(event.chemical_energy+event.resolved_heat+
              event.escaped_energy+event.unresolved_energy)
    if not np.all(zero_in(residual)):
        raise ValueError("ORIGINAL_OTS_ENERGY_OWNER_IDENTITY_EXCLUDES_ZERO")
    return float(np.max(interval_abs_upper(residual)))


def collect_map(model, base, m, label, parent_pop, parent_lnT, t0, t1, nh, nhe):
    """Passively capture original 4 sites and native thermal-root rhs."""
    saved_event=m.event_box
    saved_root=m.thermal_root
    sites={}
    roots=[]
    call_count=[0]
    def traced_event(original_model, pop, temp, t):
        event=saved_event(original_model,pop,temp,t)
        k=call_count[0]
        call_count[0]+=1
        site="parent" if k==0 else ("predictor" if k==1 else
             ("gamma" if k%2==0 else "final"))
        sites[site]=(pop,temp,float(t),event)
        return event
    def traced_root(*args, **kwargs):
        result=saved_root(*args,**kwargs)
        roots.append(result)
        return result
    try:
        m.event_box=traced_event
        m.thermal_root=traced_root
        step=m.run_step(model,base,parent_pop=parent_pop,
                        parent_logt=parent_lnT,t0=t0,t1=t1,
                        total_h=nh,total_he=nhe)
    finally:
        m.event_box=saved_event
        m.thermal_root=saved_root
    meta={"label":label,"classification":step.classification,
          "certified":bool(step.certified),"event_calls":call_count[0],
          "thermal_root_calls":len(roots),"sites":list(sites),
          "native_diagnostics":step.diagnostics}
    if not step.certified:
        return step,None,meta
    if not all(site in sites for site in ("parent","predictor","gamma","final")):
        raise ValueError("ORIGINAL_FOUR_SOURCE_SITES_NOT_CAPTURED")
    if len(roots)<3 or not (roots[-2].certified and roots[-1].certified):
        raise ValueError("ORIGINAL_NATIVE_GAMMA_FINAL_ROOT_NOT_FOUND")
    if abs((t1-t0))<=0:
        raise ValueError("ZERO_ORIGINAL_DURATION")
    gamma=float(m.sdirk.GAMMA)
    if not (0 < gamma < 1):
        raise ValueError("INVALID_NATIVE_GAMMA")
    eg=sites["gamma"][3]
    ef=sites["final"][3]
    for ev in (eg,ef):
        verify_ots_ledger(ev)
    t1d=float(t1-t0)
    # Source owner primary rates are reevaluated through the ORIGINAL
    # _explicit_photo_fields on the same gamma/final event-box input tubes.
    def primary(site):
        pop,temp,clock,event=sites[site]
        forcing=model.forcing_bounds(clock,clock)
        populations=tuple(m._I(pop.lo[:,j],pop.hi[:,j]) for j in range(5))
        p4=model._explicit_photo_fields(populations,forcing)
        return p4[3]
    pg,pf=primary("gamma"),primary("final")
    vals={
      "photo_total":weighted(gamma,eg.photo_heat,ef.photo_heat,t1d),
      "photo_primary":weighted(gamma,pg,pf,t1d),
      "ots_resolved":weighted(gamma,eg.resolved_heat,ef.resolved_heat,t1d),
      "thermal_native_rhs":weighted(gamma,roots[-2].rhs,roots[-1].rhs,t1d),
      "chemical":weighted(gamma,eg.chemical_energy,ef.chemical_energy,t1d),
      "escaped":weighted(gamma,eg.escaped_energy,ef.escaped_energy,t1d),
      "unresolved":weighted(gamma,eg.unresolved_energy,ef.unresolved_energy,t1d)
    }
    vals["nonphoto_sink"]=vals["photo_total"]-vals["thermal_native_rhs"]
    U0=m.energy_box(parent_pop,m.iv.exp(parent_lnT))
    Uf=m.energy_box(step.population,m.iv.exp(step.log_temperature))
    vals["thermal_energy_gain"]=Uf-U0
    native_residual=vals["thermal_energy_gain"]-vals["thermal_native_rhs"]
    native_cover=zero_in(native_residual)
    meta["root_residual_zero_included_nodes"]=int(np.count_nonzero(native_cover))
    meta["root_residual_total_nodes"]=N
    meta["root_residual_max_absolute_interval_upper_erg_cell"]=float(
        np.max(interval_abs_upper(native_residual)))
    meta["root_residual_max_center_abs_erg_cell"]=float(
        np.max(abs(midpoint(native_residual))))
    meta["last_gamma_root_min_derivative"]=float(roots[-2].minimum_derivative)
    meta["last_final_root_min_derivative"]=float(roots[-1].minimum_derivative)
    meta["duration_seconds"]=t1d
    meta["sdirk_gamma"]=gamma
    if not np.all(native_cover):
        raise ValueError("NATIVE_THERMAL_ROOT_RESIDUAL_EXCLUDES_ZERO")
    # Both ORIGINAL direct primary+OTS and original photo_heat must have a
    # common feasible enclosure. A nonzero midpoint mismatch is not a
    # numerical violation when independent source intervals are wide.
    photo_cover=(pg+eg.resolved_heat)-eg.photo_heat
    second_cover=(pf+ef.resolved_heat)-ef.photo_heat
    if not np.all(zero_in(photo_cover)&zero_in(second_cover)):
        raise ValueError("PRIMARY_OTS_ORIGINAL_SOURCE_OWNER_MISMATCH")
    meta["integrated_global_photoheat_center_erg"] = float(np.sum(
        midpoint(vals["photo_total"]),dtype=np.longdouble))
    meta["integrated_global_primary_center_erg"] = float(np.sum(
        midpoint(vals["photo_primary"]),dtype=np.longdouble))
    meta["integrated_global_ots_center_erg"] = float(np.sum(
        midpoint(vals["ots_resolved"]),dtype=np.longdouble))
    meta["integrated_global_netRHS_center_erg"]=float(np.sum(
        midpoint(vals["thermal_native_rhs"]),dtype=np.longdouble))
    meta["note"]="original native SDIRK2 discrete root input/output, independent interval source boxes"
    return step,vals,meta


def write_csv(path, columns):
    if any(np.asarray(a).shape!=(N,) or not np.isfinite(a).all()
           for a in columns.values()):
        raise ValueError("NONFINITE_OR_NON46080_SCIENCE_OUTPUT")
    with path.open("wb") as fout:
        with gzip.GzipFile(filename="",mode="wb",fileobj=fout,mtime=0,compresslevel=6) as gz:
            with io.TextIOWrapper(gz,encoding="utf-8",newline="") as stream:
                w=csv.writer(stream)
                w.writerow(["node",*columns])
                for i in range(N):
                    w.writerow([i,*[format(float(a[i]),".17g") for a in columns.values()]])
    return sha256(path)


def run(repo:Path,lane:str,out:Path):
    if lane not in LANES:
        raise ValueError("INVALID_ORIGINAL_SHAPE_LANE")
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    report={
        "schema":"REI_F05_ORIGINAL26_ACTUAL_DISCRETE_THERMOCHEMICAL_ENERGY_V1",
        "lane":lane,"input":{"parent_pr":343,
        "parent_head":"84dde55018273a63fad0f49183a4ace09e7a63bb",
        "source_tar_sha256":SRC_SHA,"source_array_sha256":ARR_SHA,
        "kernel_sha256":KERNEL_SHA,"original_tick":"160/131072",
        "original_nodes":N},
        "original_local_logT_limit":LOCAL_GATE,
        "original_public_width_limit":PUBLIC_WIDTH_GATE,
        "original_frozen_logT_crossbox":HISTORIC_LOGT_FAIL,
        "full_source_correlated_dh_remainder_certified":False,
        "canonical_delta":0,"central_dag":"28/88_REPORTED",
        "working_dag":"33/88_REPORTED","physical_fast_dag":"4/7_REPORTED",
        "production":"HOLD","auto_next_node":False,"steps":{}
    }
    def save():
        (out/"RESULT.json").write_text(
            json.dumps(report,sort_keys=True,indent=2,default=str)+"\n")
    save()
    edge=load("rei_energy_frozen_parent",repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    stage=repo/edge.REL_STAGE
    worker=load("rei_energy_native_kernel_worker",stage/"analysis/attempt_worker.py")
    worker.jax_guard.install_if_missing()
    m=worker._kernel()
    if sha256(worker.KERNEL_PATH)!=KERNEL_SHA:
        raise ValueError("ORIGINAL_PHYSICS_KERNEL_MISMATCH")
    decoded,source=edge.source_state(stage,lane,worker.state_io)
    if source["archive_sha256"]!=SRC_SHA or source["accepted_array_sha256"]!=ARR_SHA:
        raise ValueError("IMMUTABLE_ORIGINAL_INPUT_MISMATCH")
    base,y,lnT,nh,nhe=worker._context(m,lane)
    if len(nh)!=N or np.any(nh<=0) or np.any(nhe<=0):
        raise ValueError("INVALID_ORIGINAL_46080_CELL_NUCLEI")
    model=m.rim.ReducedIntervalModel.from_repo(repo)
    duration=float(base.forcing.duration_seconds(0))
    t0=duration*160/131072;t1=duration*161/131072;tm=(t0+t1)/2
    X=m._I(decoded.population_lower,decoded.population_upper)
    LT=m._I(decoded.log_temperature_lower,decoded.log_temperature_upper)
    results={};budget={};step=None
    for name,parentpop,parentln,a,b in (
            ("full",X,LT,t0,t1),("half1",X,LT,t0,tm),("half2",None,None,tm,t1)):
        if name=="half2":
            if step is None:
                break
            parentpop,parentln=step.population,step.log_temperature
        try:
            step,b,receipt=collect_map(model,base,m,name,parentpop,parentln,a,b,nh,nhe)
        except Exception as exc:
            report["steps"][name]={"status":"ORIGINAL_NATIVE_TRACE_ERROR",
                                  "exception_type":type(exc).__name__,
                                  "message":str(exc)}
            report["status"]="SOURCE_AUTHENTIC_SCIENCE_ERROR_NOT_ACCEPTED"
            save()
            raise
        report["steps"][name]=receipt
        save()
        if not step.certified:
            report["status"]="ORIGINAL_NATIVE_STEP_FAILED_NO_ENERGY_ACCEPTANCE"
            save()
            break
        results[name]=step
        budget[name]=b
    if len(budget)!=3:
        print(json.dumps({"status":report.get("status"),"steps":report["steps"],
                          "canonical_delta":0},default=str),flush=True)
        return report
    full,one,two=(budget[z] for z in ("full","half1","half2"))
    columns={"parent_T_center_K":np.exp(midpoint(LT)),
             "parent_xHII_center":midpoint(X)[:,1]/nh,
             "parent_xHeII_center":midpoint(X)[:,3]/nhe}
    aggregate={}
    for name in CHANNELS:
        arr=normalized_data(full[name],one[name],two[name],nh)
        for attr in ("full_center","twohalf_center","difference_center","difference_independent_upper"):
            columns[name+"_"+attr+"_erg_per_H"]=arr[attr]
        d=arr["difference_center"]
        U=arr["difference_independent_upper"]
        aggregate[name]={
             "max_abs_center_difference_erg_per_H":float(np.max(abs(d))),
             "p95_abs_center_difference_erg_per_H":float(np.percentile(abs(d),95)),
             "max_independent_output_interval_upper_erg_per_H":float(np.max(U)),
             "center_total_full_erg":float(np.sum(midpoint(full[name]),dtype=np.longdouble)),
             "center_total_twohalf_erg":float(np.sum(
                  midpoint(one[name])+midpoint(two[name]),dtype=np.longdouble)),
             "center_difference_total_erg":float(np.sum(
                  midpoint(full[name])-midpoint(one[name])-midpoint(two[name]),
                  dtype=np.longdouble))
        }
    direct_U=results["full"].population
    direct_T=results["full"].log_temperature
    half_U=results["half2"].population
    half_T=results["half2"].log_temperature
    indep_logT=np.maximum(abs(direct_T.lo-half_T.hi),abs(direct_T.hi-half_T.lo))
    report["max_original_logT_independent_crossbox"]=float(np.max(indep_logT))
    report["global_h_nuclei"]=float(np.sum(nh,dtype=np.longdouble))
    report["actual_unique_source_nodes"]=N
    report["actual_original_native_source_sites"]=12
    report["actual_original_gamma_final_roots"]=6
    report["scientific_result"]=aggregate
    csv_path=out/"REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz"
    report["csv_sha256"]=write_csv(csv_path,columns)
    report["csv_file"]=csv_path.name
    report["csv_columns"]=len(columns)+1
    report["csv_rows"]=N
    report["status"]="ORIGINAL_26EVENT_FULL_PARENT_DISCRETE_ENERGY_CHECKED_NOT_JOINT_DH_CERTIFIED"
    save()
    print(json.dumps({"status":report["status"],
          "lane":lane,"unique_nodes":N,
          "original_sites":report["actual_original_native_source_sites"],
          "max_photoheat_center_defect_erg_per_H":aggregate["photo_total"]["max_abs_center_difference_erg_per_H"],
          "max_thermal_energy_center_defect_erg_per_H":aggregate["thermal_energy_gain"]["max_abs_center_difference_erg_per_H"],
          "logT_independent_crossbox":report["max_original_logT_independent_crossbox"],
          "csv_sha256":report["csv_sha256"],"canonical_delta":0},
           sort_keys=True),flush=True)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--lane",required=True,choices=LANES)
    a=p.parse_args()
    r=run(a.repo.resolve(),a.lane,a.out)
    if r.get("status")!="ORIGINAL_26EVENT_FULL_PARENT_DISCRETE_ENERGY_CHECKED_NOT_JOINT_DH_CERTIFIED":
        raise SystemExit(3)


if __name__=="__main__":
    main()
