#!/usr/bin/env python3
"""Original 26-event MPRK22/SDIRK2 nonlinear full/twohalf map at tick [160,161].

Diagnostic ONLY. Parameter intervals at four sites are unchanged; a point
parent does not establish the correlated source-and-parent D_h(X) enclosure.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,json,sys,time
from pathlib import Path
import numpy as np

N=46080
L=160
R=161
NT=131072
LOCAL_ERROR_GATE=2e-4
PUBLIC_WIDTH_GATE=2e-3
ORIGINAL_ERROR=2.1245050576368385e-4
ORIGINAL_ARCHIVE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SOURCE="research/rei_igm_original_26event_tick160_20261101/source_26events.py"
PRED=("Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
      "R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK")
OLD=("Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
     "R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY")
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR","SCRIPT_SELF_SHIELDING_AUDITOR")
KEYS=("x_HII","x_HeII","x_HeIII","log_T")

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(path)
    o=importlib.util.module_from_spec(spec);sys.modules[name]=o;spec.loader.exec_module(o);return o

def cross(a,b):
    al,ah,bl,bh=np.asarray(a.lo),np.asarray(a.hi),np.asarray(b.lo),np.asarray(b.hi)
    if not (al.shape==ah.shape==bl.shape==bh.shape) or not all(np.isfinite(x).all() for x in (al,ah,bl,bh)):
        raise ValueError("invalid pair of interval images")
    if np.any(al>ah) or np.any(bl>bh):raise ValueError("inverted interval image")
    return np.maximum(np.abs(al-bh),np.abs(ah-bl))

def boxes(m,step,nh,nhe):
    if not step.certified:raise ValueError("noncertified map")
    p=step.population
    return {"x_HII":m._I(p.lo[:,1]/nh,p.hi[:,1]/nh),
            "x_HeII":m._I(p.lo[:,3]/nhe,p.hi[:,3]/nhe),
            "x_HeIII":m._I(p.lo[:,4]/nhe,p.hi[:,4]/nhe),
            "log_T":step.log_temperature}

def qtiles(v):
    if not np.isfinite(v).all():raise ValueError("nonfinite physical diagnostic")
    return {p:float(np.percentile(v,q)) for p,q in (("min",0),("p05",5),("median",50),("p95",95),("max",100))}

def evaluate(m,model,base,old_state,source,mode):
    orig=base.inputs.state0.mutable_copy()
    ys=np.asarray(orig.values[:5].T,dtype=np.float64)
    nh=ys[:,0]+ys[:,1];nhe=np.sum(ys[:,2:5],axis=1)
    if nh.shape!=(N,) or np.any(nh<=0) or np.any(nhe<=0):raise ValueError("bad original nuclei")
    if mode=="uncertain_parent":
        p=m._I(old_state["lo"],old_state["hi"])
        t=m._I(old_state["tl"],old_state["th"])
    elif mode=="nuclei_conserving_point_parent":
        yp=source.representative(old_state["lo"],old_state["hi"],nh,nhe)
        tp=0.5*(old_state["tl"]+old_state["th"])
        p=m._I(yp,yp);t=m._I(tp,tp)
    else:raise ValueError("unknown parent mode")
    duration=float(base.forcing.duration_seconds(0))
    t0=duration*(L/NT);t1=duration*(R/NT);tm=t0+0.5*(t1-t0)
    common=dict(model=model,base=base,parent_pop=p,parent_logt=t,total_h=nh,total_he=nhe)
    full=m.run_step(**common,t0=t0,t1=t1)
    first=m.run_step(**common,t0=t0,t1=tm)
    if not first.certified:
        return {"status":"EARLY_FAIL_CLOSED","stage_classes":[full.classification,first.classification,None]},None
    second=m.run_step(**dict(common,parent_pop=first.population,parent_logt=first.log_temperature),t0=tm,t1=t1)
    if not all(s.certified for s in (full,first,second)):
        return {"status":"EARLY_FAIL_CLOSED","stage_classes":[s.classification for s in (full,first,second)]},None
    a=boxes(m,full,nh,nhe);b=boxes(m,second,nh,nhe)
    fields={"parent_logT_width":np.asarray(t.hi-t.lo),
            "parent_temperature_K":np.exp(0.5*(np.asarray(t.lo)+np.asarray(t.hi)))}
    for k in KEYS:
        fields[k+"_F_lo"]=np.asarray(a[k].lo)
        fields[k+"_F_hi"]=np.asarray(a[k].hi)
        fields[k+"_H_lo"]=np.asarray(b[k].lo)
        fields[k+"_H_hi"]=np.asarray(b[k].hi)
        fields[k+"_crossbox"]=cross(a[k],b[k])
        fields[k+"_twohalf_width"]=np.asarray(b[k].hi-b[k].lo)
    frac=0.5*(np.asarray(b["x_HII"].lo)+np.asarray(b["x_HII"].hi))
    hei=0.5*(np.asarray(b["x_HeII"].lo)+np.asarray(b["x_HeII"].hi))
    heiii=0.5*(np.asarray(b["x_HeIII"].lo)+np.asarray(b["x_HeIII"].hi))
    # The helium number per H is from the exact owner state, not a substituted cosmology.
    fields["x_e_HHe_mid"]=frac+(nhe/nh)*(hei+2*heiii)
    fields["T_K_twohalf_mid"]=np.exp(0.5*(np.asarray(b["log_T"].lo)+np.asarray(b["log_T"].hi)))
    fields["T_K_twohalf_lo"]=np.exp(np.asarray(b["log_T"].lo))
    fields["T_K_twohalf_hi"]=np.exp(np.asarray(b["log_T"].hi))
    # Nodes and source uncertainty remain the same, but no source-site correlation was imposed.
    if any(np.any(b[k].lo>b[k].hi) for k in KEYS):raise ValueError("invalid endpoint enclosure")
    report={"status":"ENCLOSED_NONLINEAR_MAPS_DIAGNOSTIC_ONLY",
       "original_26event_kernel":True,"all_table_events_clear":all(not e.any_event for v in (full,first,second) for e in v.table_events),
       "duration_s":duration,"physical_timestep_s":t1-t0,
       "crossbox_max":{k:float(np.max(fields[k+"_crossbox"])) for k in KEYS},
       "crossbox_median":{k:float(np.median(fields[k+"_crossbox"])) for k in KEYS},
       "output_width_max":{k:float(np.max(fields[k+"_twohalf_width"])) for k in KEYS},
       "parent_T_K":qtiles(fields["parent_temperature_K"]),
       "candidate_twohalf_T_K":qtiles(fields["T_K_twohalf_mid"]),
       "candidate_twohalf_xe_per_H":qtiles(fields["x_e_HHe_mid"]),
       "original_strict_error_gate":LOCAL_ERROR_GATE,
       "original_strict_public_width_gate":PUBLIC_WIDTH_GATE,
       "not_validated_joint_same_parent_defect":True}
    return report,fields

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for data in iter(lambda:f.read(1048576),b""):h.update(data)
    return h.hexdigest()

def run(root,out,lanes=LANES):
    root,out=Path(root).resolve(),Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    source=load("hei_source_tick160",root/SOURCE)
    archive=root/"stages"/OLD/"local_results"/"first_interval_r2_blocked_minimum_step.tar.gz"
    if sha(archive)!=ORIGINAL_ARCHIVE_SHA:raise ValueError("ORIGINAL_ARCHIVE_SHA_MISMATCH")
    accepted=source.archived_tick160(archive)
    if set(accepted)!=set(LANES):raise ValueError("missing source original lanes")
    m=load("orig_26event_map_tick160",root/"stages"/PRED/"analysis"/"interval_discrete_map.py")
    model=m.rim.ReducedIntervalModel.from_repo(root)
    result={"schema":"REI_F05_NONLINEAR_MAP_POINT_PARENT_CONTRAST_V1",
        "original_archive_sha256":ORIGINAL_ARCHIVE_SHA,
        "original_state_body_sha256":accepted[LANES[0]]["array_sha"],
        "original_accepted_tick":L,"failing_tick":R,"total_ticks":NT,
        "original_historical_failure_error":ORIGINAL_ERROR,"original_strict_gate":LOCAL_ERROR_GATE,
        "physical_nodes_unique":N,"observed_experiments":0,
        "point_is_noncanonical_representative":True,
        "original_site_parameters_independent":True,
        "whole_canonical_interval_accepted":False,"canonical_DAG_reported":"28/88","canonical_delta":0,
        "production":"HOLD","merge":"HOLD","rows":[],"contrasts":[]}
    for lane in lanes:
        b=m.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=root,lane=lane)
        for mode in ("uncertain_parent","nuclei_conserving_point_parent"):
            start=time.monotonic()
            info,fields=evaluate(m,model,b,accepted[lane],source,mode)
            info.update(lane=lane,mode=mode,elapsed_s=float(time.monotonic()-start),
                        source_accepted_array_sha=accepted[lane]["array_sha"])
            if fields is not None:
                p=out/(lane+"_"+mode+"_46080.csv.gz")
                keys=list(fields)
                with gzip.open(p,"wt",encoding="utf8",newline="") as fp:
                    writer=csv.writer(fp)
                    writer.writerow(["node",*keys])
                    for i in range(N):writer.writerow([i,*[format(float(fields[k][i]),".17g") for k in keys]])
                info["csv"]=p.name;info["sha256"]=sha(p)
            result["rows"].append(info)
            print("REAL_26EVENT_NONLINEAR",json.dumps(info,sort_keys=True),flush=True)
        o,pt=result["rows"][-2:]
        contrast={"lane":lane,"original_parent":o["status"],"point_parent":pt["status"],
                  "not_joint_defect_proof":True}
        if "crossbox_max" in o and "crossbox_max" in pt:
            contrast["crossbox_ratio_box_to_point"]={k:o["crossbox_max"][k]/max(pt["crossbox_max"][k],1e-300) for k in KEYS}
        result["contrasts"].append(contrast)
    result["model_diagnostic_rows"]=N*sum("csv" in r for r in result["rows"])
    target=out/"NONLINEAR_MAP_TICK160_RESULT.json"
    target.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("REAL_26EVENT_FINAL",target,"diagnostic_rows",result["model_diagnostic_rows"],flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    x=p.parse_args();run(x.repo,x.output)
