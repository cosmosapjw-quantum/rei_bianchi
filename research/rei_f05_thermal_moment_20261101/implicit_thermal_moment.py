#!/usr/bin/env python3
"""Original 26-event stage thermal-root response to shared H/He photoheating.

Read-only hooks around ACTUAL original MPRK22(1)/Alexander SDIRK2 full/two-half
at original first canonical interval [160,161]. Native local thermal-root
derivative is used; the denominator-only source derivatives are evaluated with
original 26-event photon owner and the three shared population sums.

Conditional: fixed event-box and all OTHER thermal RHS factors. This is NOT
the full coupled source/state Jacobian or all-parent D_h certificate.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
PRIOR="research/rei_igm_original26_stage_photon_20261101/stage_photon_audit.py"
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"
N=46080
SRC_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
TARGET=[160,161];TOTAL=131072;GATE=2e-4;WIDTH_GATE=2e-3
MOMENTS=("HI","HeI","HeII")

def import_file(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    if spec is None or spec.loader is None:raise ImportError(str(path))
    x=importlib.util.module_from_spec(spec);sys.modules[name]=x;spec.loader.exec_module(x);return x

def native_conditional_response(native_dlo,native_dhi,photo_dlogS,weighted_time):
    """Outward order bounds for q/A, A>0 (q may have either sign)."""
    low=np.asarray(native_dlo,float);high=np.asarray(native_dhi,float)
    delta=np.asarray(photo_dlogS,float)
    h=float(weighted_time)
    if low.shape!=high.shape or delta.shape[:1]!=low.shape or delta.shape[-1]!=3:
        raise ValueError("native thermal-root dimensions")
    if not np.isfinite(delta).all() or np.any(low<=0) or np.any(high<low) or h<0:
        raise ValueError("uncertified native thermal-root derivative")
    q=h*delta
    a=q/high[:,None];b=q/low[:,None]
    lower=np.minimum(a,b);upper=np.maximum(a,b)
    # Exact structural zero stays zero; for nonzero outputs expand by one binary64 ulp.
    lower=np.where(q==0.0,0.0,np.nextafter(lower,-np.inf))
    upper=np.where(q==0.0,0.0,np.nextafter(upper,np.inf))
    return lower,upper

def stage_frozen_source_thermal_response(mod,ctx,root,step,weight,original_photon):
    if root.log_temperature is None or not root.certified:
        raise ValueError("original thermal root not certified")
    derivative=mod.thermal_root_derivative(ctx,root.log_temperature,float(step)*float(weight))
    dl=np.asarray(derivative.lo,float);dh=np.asarray(derivative.hi,float)
    if dl.shape!=(N,) or dh.shape!=(N,) or np.any(dl<=0) or np.any(dh<dl):
        raise ValueError("native implicit thermal derivative does not certify positivity")
    primary=np.asarray(original_photon["primary_photoheat_erg_per_H_s"],float)*original_photon["nh"]
    dphoto=np.column_stack([np.asarray(original_photon[f"d_primary_photoheat_d_lnS_{s}_den_erg_H_s"],float)
                  for s in MOMENTS])*original_photon["nh"][:,None]
    lower,upper=native_conditional_response(dl,dh,dphoto,float(step)*float(weight))
    if np.any(dphoto>1e-21*np.maximum(1.,np.abs(primary[:,None]))):
        raise ValueError("denominator-only heating response should not have positive sign")
    mid=0.5*(dl+dh)
    q=np.asarray(primary,float)
    arr={
        "thermal_logT_native_lo":np.asarray(root.log_temperature.lo,float),
        "thermal_logT_native_hi":np.asarray(root.log_temperature.hi,float),
        "thermal_T_native_K":np.exp(.5*(np.asarray(root.log_temperature.lo,float)+np.asarray(root.log_temperature.hi,float))),
        "native_Fz_derivative_erg_lo":dl,"native_Fz_derivative_erg_hi":dh,
        "primary_photoheat_erg_per_s":q,
        "primary_heat_elasticity_logT":float(step)*float(weight)*q/mid}
    for j,s in enumerate(MOMENTS):
        arr[f"primary_heat_d_lnS_{s}_erg_per_s"]=dphoto[:,j]
        arr[f"conditional_dlogT_dlnS_{s}_lo"]=lower[:,j]
        arr[f"conditional_dlogT_dlnS_{s}_hi"]=upper[:,j]
    if any(v.shape!=(N,) or not np.isfinite(v).all() for v in arr.values()):
        raise ValueError("original 46k thermal response invalid")
    return arr

def quantiles(v):
    v=np.asarray(v,float)
    return {str(k):float(np.percentile(v,k)) for k in (0,5,50,95,100)}

def compress_rows(target,records):
    with target.open("wb") as stream:
        with gzip.GzipFile(fileobj=stream,mode="wb",filename="",mtime=0,compresslevel=6) as gz:
            with io.TextIOWrapper(gz,encoding="utf8",newline="") as f:
                keys=list(records[0][2])
                w=csv.writer(f);w.writerow(["map_step","root_order","source_site","node","proper_time_s","root_weight","root_dt_s",*keys])
                for step,order,arr,info in records:
                    for i in range(N):
                        w.writerow([step,order,info["site"],i,
                          format(info["source_time_s"],".17g"),
                          format(info["weight"],".17g"),
                          format(info["dt_s"],".17g"),
                          *[format(float(arr[k][i]),".17g") for k in keys]])
    h=hashlib.sha256(target.read_bytes()).hexdigest()
    return h,keys

def run(repo,out):
    repo=Path(repo).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    prior=import_file("rei_original_stage_photon_thermal_owner",repo/PRIOR)
    fb=prior.load_feedback()
    src,mod,model,_,_,frozen,_=fb.context(repo)
    if frozen["array_sha"]!=STATE_SHA or fb.sha(repo/"stages"/fb.OLD/"local_results/first_interval_r2_blocked_minimum_step.tar.gz")!=SRC_SHA:
        raise ValueError("ORIGINAL_REI_FROZEN_SOURCE_IDENTITY_MISMATCH")
    base=mod.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=LANE)
    original=np.asarray(base.inputs.state0.mutable_copy().values[:5].T,float)
    nh=original[:,0]+original[:,1];nhe=np.sum(original[:,2:5],axis=1)
    point=src.representative(frozen["lo"],frozen["hi"],nh,nhe)
    P=mod._I(point);T=mod._I(.5*(frozen["tl"]+frozen["th"]))
    duration=float(base.forcing.duration_seconds(0))
    left=duration*160/131072;right=duration*161/131072;middle=(left+right)*.5
    result={"schema":"REI_ORIGINAL26_THERMAL_ROOT_SHARED_PHOTON_PARTIAL_JACOBIAN_V1",
      "original_archive_sha256":SRC_SHA,"original_state_array_sha256":STATE_SHA,
      "parent_PR":337,"parent_accepted_tick":160,"total_ticks":131072,
      "native_physics":"original unmodified 26event MPRK22 + Alexander SDIRK2",
      "reused_parent":"one nuclei-conserving representative point of original accepted parent box",
      "conditional_response_only":True,"photoheat_derivative":"denominator-only nonlocal shared-neutral-moment part at FIXED local numerator, source event branch and other RHS factors",
      "not_original_full_Dh_certificate":True,"original_historical_logT_gate":GATE,
      "original_historical_failed_one_tick":2.1245050576368385e-4,
      "canonical_DAG":"28/88_REPORTED","working_DAG":"33/88_REPORTED","fast_DAG":"4/7_REPORTED","canonical_delta":0,
      "new_full_cosmological_ivps":0,"new_observational_rows":0,
      "first_canonical_interval":"BLOCKED_MINIMUM_STEP","production":"HOLD","map_steps":[],"root_stats":[],"status":"STARTED"}
    def checkpoint():
        (out/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    checkpoint()
    records=[]
    oldev=mod.event_box;oldroot=mod.thermal_root
    try:
        for label,p,t0,t1 in [("full",P,left,right),("half_first",P,left,middle),("half_second",None,middle,right)]:
            if label=="half_second":
                if first is None or not first.certified:break
                p=first.population;tt=first.log_temperature
            else:tt=T
            event_by_id={};root_records=[];source_count=[0];root_count=[0]
            def traced_event(mm,pp,temp,ts):
                event=oldev(mm,pp,temp,ts)
                arr,stats,group=prior.physics_snapshot(fb,src,mod,model,pp,temp,ts,nh,nhe)
                arr["nh"]=nh
                event_by_id[id(event.photo_heat)]={"array":arr,"time_s":float(ts),
                    "site":("parent" if source_count[0]==0 else
                            "predictor" if source_count[0]==1 else
                            "gamma" if source_count[0]%2==0 else "final"),
                    "keep_alive":event.photo_heat}
                source_count[0]+=1
                return event
            def traced_root(ctx,U0,step,constant,weight,seed_lo,seed_hi,*args,**kwargs):
                root=oldroot(ctx,U0,step,constant,weight,seed_lo,seed_hi,*args,**kwargs)
                if root.certified:
                    matching=event_by_id.get(id(ctx.photoheat))
                    if matching is None:raise ValueError("native thermal root without exact source-event owner")
                    arr=stage_frozen_source_thermal_response(mod,ctx,root,step,weight,matching["array"])
                    root_records.append((label,root_count[0],arr,{"site":matching["site"],
                         "source_time_s":matching["time_s"],"dt_s":float(step),"weight":float(weight)}))
                root_count[0]+=1
                return root
            mod.event_box=traced_event
            mod.thermal_root=traced_root
            try:
                native=mod.run_step(model,base,parent_pop=p,parent_logt=tt,t0=t0,t1=t1,
                  total_h=nh,total_he=nhe)
            finally:
                mod.event_box=oldev;mod.thermal_root=oldroot
            result["map_steps"].append({"label":label,"certified":bool(native.certified),
                "classification":native.classification,
                "source_events":source_count[0],"original_thermal_root_calls":root_count[0],
                "captured_certified_thermal_roots":len(root_records),
                "native_diagnostics":native.diagnostics})
            records+=root_records
            if label=="half_first":first=native
            if not native.certified:
                result["status"]="NATIVE_ORIGINAL_26EVENT_MAP_UNCERTIFIED_"+label
                checkpoint();break
            checkpoint()
        if len(result["map_steps"])==3 and all(x["certified"] for x in result["map_steps"]):
            if not records:raise ValueError("no native original thermal roots")
            target=out/"REI_ORIGINAL26_IMPLICIT_THERMAL_MOMENT_46080.csv.gz"
            digest,keys=compress_rows(target,records)
            result["root_site_count"]=len(records)
            result["new_physical_root_node_rows"]=N*len(records)
            result["output_csv"]=target.name;result["output_sha256"]=digest
            result["root_numerical_columns"]=keys
            for name,index,arr,meta in records:
                temp=np.asarray(arr["thermal_T_native_K"])
                Fzlo=np.asarray(arr["native_Fz_derivative_erg_lo"])
                Fzhi=np.asarray(arr["native_Fz_derivative_erg_hi"])
                x=arr["conditional_dlogT_dlnS_HeI_lo"];y=arr["conditional_dlogT_dlnS_HeI_hi"]
                result["root_stats"].append({"map_step":name,"root_order":index,**meta,
                    "minimum_Fz_erg":float(np.min(Fzlo)),
                    "maximum_Fz_erg":float(np.max(Fzhi)),
                    "all_native_thermal_roots_certified":True,
                    "temperature_median_K":float(np.median(temp)),
                    "photoheat_elasticity_median":float(np.median(arr["primary_heat_elasticity_logT"])),
                    "dlogT_dlnS_HeI_median_lower":float(np.median(x)),
                    "dlogT_dlnS_HeI_median_upper":float(np.median(y)),
                    "dlogT_dlnS_HeI_max_abs_bound":float(np.max(np.maximum(abs(x),abs(y))))})
            result["status"]="NATIVE_ROOT_PARTIAL_PHOTON_THERMAL_JACOBIAN_COMPUTED_NOT_FULL_Dh"
            result["all_source_site_derivatives_partial_frozen_context"]=True
            print("ORIGINAL_26EVENT_IMPLICIT_THERMAL_PHYSICS",json.dumps({
              "rows":result["new_physical_root_node_rows"],
              "roots":result["root_site_count"],
              "first":result["root_stats"][0],
              "last":result["root_stats"][-1],
              "sha256":digest,"central":"28/88","canonical_delta":0},sort_keys=True),flush=True)
        else:
            result["status"]="ORIGINAL_MAP_PARTIAL_FAILURE_NOT_PROMOTED"
    finally:
        mod.event_box=oldev;mod.thermal_root=oldroot
        checkpoint()
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    z=p.parse_args();run(z.repo,z.out)
