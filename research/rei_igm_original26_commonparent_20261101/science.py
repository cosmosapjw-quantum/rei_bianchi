#!/usr/bin/env python3
"""Authentic original 26-event H/He source temperature response and shared-point local step.

Single point chosen inside locked tick160 source interval is NOT a rigorous
common-parent all-X certificate. No new full interval IVP or production change.
"""
import argparse,csv,gzip,hashlib,importlib.util,io,json,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
STAGE=("Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
       "R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY")
PRED=("Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_"
      "R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK")
BASE_SRC=ROOT/"research/rei_igm_original_26event_tick160_20261101/source_26events.py"
ORIGINAL_ARCHIVE=ROOT/"stages"/STAGE/"local_results/first_interval_r2_blocked_minimum_step.tar.gz"
ARRAY_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"
STRICT_ERROR=2e-4
STRICT_WIDTH=2e-3
DELTA_LOGT=1e-4

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(str(path))
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def init_source():
    guard=load("rei26_source_guard_tick160_v1",ROOT/"stages"/STAGE/"analysis/jax_import_guard.py")
    if not guard.install_if_missing():raise RuntimeError("JAX guard cannot be verified")
    source=load("rei26_source_readonly_tick160_v1",BASE_SRC)
    mod=load("rei26_interval_original_tick160_v1",ROOT/"stages"/PRED/"analysis/interval_discrete_map.py")
    states=source.archived_tick160(ORIGINAL_ARCHIVE)
    if set(states)!=set(source.LANES) or {s["array_sha"] for s in states.values()}!={ARRAY_SHA}:
        raise ValueError("original tick160 array identity mismatch")
    base=mod.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=ROOT,lane=LANE)
    model=mod.rim.ReducedIntervalModel.from_repo(ROOT)
    state=states[LANE]
    initial=base.inputs.state0.mutable_copy()
    p0=np.asarray(initial.values[:5].T,dtype=float)
    nh=p0[:,0]+p0[:,1];nhe=np.sum(p0[:,2:5],axis=1)
    pop=source.representative(state["lo"],state["hi"],nh,nhe)
    logt=0.5*(state["tl"]+state["th"])
    if not ((pop>=state["lo"]).all() and (pop<=state["hi"]).all()):raise ValueError("source point not enclosed")
    duration=float(base.forcing.duration_seconds(0))
    t0=duration*160/131072;t1=duration*161/131072
    assert duration>0 and t0<t1
    return source,mod,model,base,pop,logt,nh,nhe,t0,t1

def distribution(x):
    x=np.asarray(x,float)
    if x.size!=46080 or not np.isfinite(x).all():raise ValueError("nonfinite 46080-node data")
    return {str(q):float(np.percentile(x,q)) for q in (0,5,50,95,100)}

def middle(a):
    return 0.5*(np.asarray(a.lo)+np.asarray(a.hi))

def source_temperature_response(ctx,out):
    source,mod,model,base,p,logt,nh,nhe,t0,t1=ctx
    responses=[]
    for delta in (-DELTA_LOGT,0,DELTA_LOGT):
        ev=mod.event_box(model,mod._I(p),mod._I(np.exp(logt+delta)),t0)
        f=middle(ev.flux)
        dot=source.stoich_flux(f)
        residual=max(float(np.max(np.abs(dot[:,0]+dot[:,1]))),
                     float(np.max(np.abs(np.sum(dot[:,2:5],axis=1)))))
        if residual>1e-11*max(float(np.max(abs(dot))),1e-300):
            raise ValueError("nuclear stoichiometry failure")
        energy=ev.resolved_heat+ev.unresolved_energy+ev.escaped_energy+ev.chemical_energy
        if not (np.all(energy.lo<=0)&np.all(energy.hi>=0)&
                np.all(ev.photon_identity.lo<=0)&np.all(ev.photon_identity.hi>=0)):
            raise ValueError("photon-energy original source closure failure")
        responses.append((dot[:,1]/nh,(dot[:,1]+dot[:,3]+2*dot[:,4])/nh,
                          middle(ev.photo_heat)/nh))
    a,b,c=responses
    columns={
       "temperature_K":np.exp(logt),
       "x_HII":p[:,1]/nh,
       "x_HeII":p[:,3]/nhe,
       "x_HeIII":p[:,4]/nhe,
       "dx_HII_dt_source_mid_s_inverse":b[0],
       "dxe_dt_source_mid_s_inverse":b[1],
       "photoheat_source_mid_erg_per_H_s":b[2],
       "partial_temperature_dxe_dt_dlogT_s_inverse":(c[1]-a[1])/(2*DELTA_LOGT),
       "partial_temperature_photoheat_dlogT_erg_per_H_s":(c[2]-a[2])/(2*DELTA_LOGT)
    }
    path=out/"ORIGINAL_26EVENT_THERMAL_RESPONSE_46080.csv.gz"
    with open(path,"wb") as f:
        with gzip.GzipFile(fileobj=f,mode="wb",filename="",mtime=0,compresslevel=6) as g:
            with io.TextIOWrapper(g,encoding="utf-8",newline="") as h:
                writer=csv.writer(h);writer.writerow(["node",*columns])
                for i in range(46080):
                    writer.writerow([i,*[format(float(columns[k][i]),".17g") for k in columns]])
    report={
      "schema":"REI_IGM_ORIGINAL26_TICK160_THERMAL_SOURCE_RESPONSE",
      "source_state_array_sha256":ARRAY_SHA,"rows":46080,
      "scope":"frozen original 26-event source on one shared nuclei-preserving representative, not accepted IVP",
      "delta_logT":DELTA_LOGT,"fixed_composition":True,
      "source_event_midpoint_not_joint_realization":True,
      "photon_energy_identity_zero_included":True,"nuclear_stoichiometry_pass":True,
      "csv_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
      "equal_node_percentiles":{k:distribution(v) for k,v in columns.items()},
      "DAG_central":"28/88_REPORTED","DAG_working":"33/88_REPORTED","DAG_fast":"4/7_REPORTED",
      "canonical_delta":0,"production":"HOLD"
    }
    (out/"ORIGINAL_26EVENT_THERMAL_RESPONSE.json").write_text(json.dumps(report,indent=2)+"\n")
    print("REAL_SOURCE_TEMPERATURE_RESPONSE",json.dumps({
        "rows":report["rows"],
        "median_dxe_dlogT":report["equal_node_percentiles"]["partial_temperature_dxe_dt_dlogT_s_inverse"]["50"],
        "median_photoheat":report["equal_node_percentiles"]["photoheat_source_mid_erg_per_H_s"]["50"],
        "sha256":report["csv_sha256"],"canonical_delta":0}),flush=True)
    return report

def one_pair(ctx,out):
    source,mod,model,base,p,logt,nh,nhe,t0,t1=ctx
    report={"schema":"REI_IGM_ORIGINAL26_COMMON_POINT_TICK160_TO161",
        "parent":"one representative point IN original frozen tick160 interval",
        "state_sha256":ARRAY_SHA,"strict_error":STRICT_ERROR,"strict_width":STRICT_WIDTH,
        "tested_tick":[160,161],"original_full_interval_closed":False,
        "all_X_joint_proof":False,"new_production_IVP":False,
        "central_dag":"28/88_REPORTED","canonical_delta":0,"stages":{}}
    path=out/"ORIGINAL_26EVENT_POINT_MAP.json"
    def save():path.write_text(json.dumps(report,indent=2,default=str)+"\n")
    save()
    mid=.5*(t0+t1);P=mod._I(p);X=mod._I(logt)
    for name,pp,xx,a,b in (("full",P,X,t0,t1),("half_first",P,X,t0,mid)):
        z=mod.run_step(model,base,parent_pop=pp,parent_logt=xx,t0=a,t1=b,total_h=nh,total_he=nhe)
        report["stages"][name]={"certified":bool(z.certified),"classification":z.classification,"diagnostics":z.diagnostics}
        save()
        if not z.certified:
            report["status"]="ORIGINAL_MAP_BLOCKED_"+name;save()
            print("ORIGINAL_MAP_BLOCKED",name,z.classification,flush=True)
            return report
        if name=="full":full=z
        else:first=z
    second=mod.run_step(model,base,parent_pop=first.population,parent_logt=first.log_temperature,
                        t0=mid,t1=t1,total_h=nh,total_he=nhe)
    report["stages"]["half_second"]={"certified":bool(second.certified),
                                  "classification":second.classification,"diagnostics":second.diagnostics}
    save()
    if not second.certified:
        report["status"]="ORIGINAL_MAP_BLOCKED_half_second";save()
        print("ORIGINAL_MAP_BLOCKED","half_second",second.classification,flush=True)
        return report
    def bounds(alo,ahi,blo,bhi):
        m1=.5*(alo+ahi);m2=.5*(blo+bhi)
        return dict(max_abs_center_difference=float(np.max(np.abs(m1-m2))),
                    max_independent_interval_distance=float(np.max(np.maximum(abs(alo-bhi),abs(ahi-blo)))),
                    max_full_width=float(np.max(ahi-alo)),max_two_half_width=float(np.max(bhi-blo)))
    outres={}
    for name,col,norm in (("x_HII",1,nh),("x_HeII",3,nhe),("x_HeIII",4,nhe)):
        outres[name]=bounds(full.population.lo[:,col]/norm,full.population.hi[:,col]/norm,
                            second.population.lo[:,col]/norm,second.population.hi[:,col]/norm)
    outres["log_T"]=bounds(full.log_temperature.lo,full.log_temperature.hi,
                           second.log_temperature.lo,second.log_temperature.hi)
    report["point_only_results"]=outres
    report["status"]="SOURCE_AUTHENTIC_SINGLE_PARENT_POINT_COMPUTED_NOT_ALL_X_ACCEPTED"
    report["point_run_below_strict_local_error"]=(max(x["max_independent_interval_distance"] for x in outres.values())<STRICT_ERROR)
    save()
    print("REAL_ORIGINAL_SOURCE_POINT_MAP",json.dumps({
        "point_logT":outres["log_T"],"all_X_proof":False,"canonical_delta":0}),flush=True)
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",required=True,choices=("source","pair"))
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    context=init_source()
    if args.mode=="source":source_temperature_response(context,out)
    else:one_pair(context,out)

if __name__=="__main__":main()
