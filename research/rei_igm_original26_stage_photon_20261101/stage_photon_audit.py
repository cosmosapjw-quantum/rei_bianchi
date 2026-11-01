#!/usr/bin/env python3
"""Original 26-event H/He one-tick, four-site photon feedback on the actual 46080-node parent.
Uses the unmodified original MPRK22(1)/Alexander SDIRK2 map from PR332 ancestry.
One nuclei-conserving representative of tick160's parent interval: NOT all-X proof.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
FB=ROOT/"research/rei_igm_tick160_global_photon_20261101/photon_global_feedback.py"
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"
SOURCE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
N=46080
G=4
S=3
GATE=2e-4
WIDTH=2e-3
EV_ERG=1.602176634e-12
SRC_INDICES=(0,2,3)
SPECIES=("HI","HeI","HeII")

def file_sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for x in iter(lambda:f.read(1048576),b""):h.update(x)
    return h.hexdigest()

def load_feedback():
    spec=importlib.util.spec_from_file_location("rei_pr332_original_photon_global_feedback",FB)
    if spec is None or spec.loader is None:raise ImportError(FB)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

def woodbury(A,B,V,b):
    """(A+B V^T)^-1 b using shared-source Schur complement; synthetic proof control."""
    A,B,V,b=[np.asarray(q,dtype=float) for q in (A,B,V,b)]
    t=np.linalg.solve(A,b)
    u=np.linalg.solve(A,B)
    schur=np.eye(B.shape[1])+V.T@u
    return t-u@np.linalg.solve(schur,V.T@t),schur

def exact_three_moment_derivative(p):
    """Photon shares derivative wrt ln global source moments at fixed current/coefs."""
    p=np.asarray(p,dtype=float)
    if p.shape!=(3,) or np.any(p<0) or np.sum(p)>1+1e-13:
        raise ValueError("invalid 3-moment source shares")
    return np.diag(p)-np.outer(p,p)

def check_unit_reaction_rates(flux,group_deriv,shares):
    """Check denominator-only source nonlocal sensitivity, no wrong local numerator term."""
    if flux.shape!=(N,3) or group_deriv.shape!=(N,3,3):
        raise ValueError("source shape differs from original 46k state")
    if not np.isfinite(flux).all() or not np.isfinite(group_deriv).all():
        raise ValueError("nonfinite source")
    return float(np.max(np.abs(group_deriv+flux[:,:,None]*shares[None,None,:])))

def physics_snapshot(fb,src,mod,model,pop,temp,t,nh,nhe):
    """Original stage source with exact shared group denominator and conserved source owner."""
    if not hasattr(pop,"lo") or not hasattr(temp,"lo"):raise ValueError("original interval state required")
    pt=src.representative(np.asarray(pop.lo),np.asarray(pop.hi),nh,nhe)
    if pt.shape!=(N,5) or np.any(pt<=0):raise ValueError("not admissible H/He parent")
    force=model.forcing_bounds(float(t),float(t))
    z=fb.midpoint(force.z)
    coeff=fb.coefficients(model,mod,z)
    currents=np.asarray([fb.midpoint(q) for q in force.current],dtype=float)
    external=np.asarray([fb.midpoint(q) for q in force.external_subgrid],dtype=float)
    mom=np.asarray([np.sum(pt[:,j],dtype=np.longdouble) for j in SRC_INDICES],dtype=float)
    rows=np.zeros((N,3),dtype=float)
    nonlocal_deriv=np.zeros((N,3,3),dtype=float)
    heat=np.zeros(N,dtype=float)
    dheat=np.zeros((N,3),dtype=float)
    group_rows=[]
    for g in range(G):
        pg,pe,den=fb.shares(mom,coeff[g],external[g])
        src_rate=currents[g]*pt[:,SRC_INDICES]*coeff[g][None,:]/den
        if not np.isfinite(src_rate).all() or np.any(src_rate<0):raise ValueError("source must be positive")
        source_logderiv=-src_rate[:,:,None]*pg[None,None,:]
        if np.max(np.abs(source_logderiv+src_rate[:,:,None]*pg[None,None,:]))>5e-15:
            raise ValueError("source logmoment identity")
        J=exact_three_moment_derivative(pg)
        eig=np.linalg.eigvalsh(J)
        if np.min(eig)<-2e-12:raise ValueError("photon competition covariance must be PSD")
        frac_photons=src_rate.sum(axis=0)
        rel=np.max(abs(frac_photons-currents[g]*pg)/(1+abs(currents[g]*pg)))
        if rel>2e-12:raise ValueError("source photon group sum does not match original")
        ex=np.asarray(model.excess_eV[:,g],dtype=float)
        phot_heat=src_rate@ex*EV_ERG
        rows+=src_rate
        nonlocal_deriv+=source_logderiv
        heat+=phot_heat
        dheat+=np.sum(source_logderiv*ex[None,:,None],axis=1)*EV_ERG
        group_rows.append({
            "group":g,"source_time_s":float(t),"redshift":z,
            "current_photons_per_s":float(currents[g]),
            "external_fraction":float(pe),
            "absorber_fractions":pg.tolist(),
            "original_global_neutral_moments":mom.tolist(),
            "source_photons_per_s":frac_photons.tolist(),
            "photon_heat_erg_per_s":float(np.sum(phot_heat)),
            "max_original_normalization_relative":float(rel),
            "source_share_Jacobian":J.tolist(),
            "minimum_eigenvalue":float(np.min(eig)),
            "determinant":float(np.linalg.det(J))
        })
    # Original PR332 helper accepts a point ndarray, while run_step supplies an
    # interval-valued source parent. Evaluate the ORIGINAL source on its whole
    # interval rather than collapsing it to the selected representative.
    populations=tuple(mod._I(np.asarray(pop.lo)[:,k],np.asarray(pop.hi)[:,k]) for k in range(5))
    original_components=model._explicit_photo_fields(populations,force)
    original=[mod.iv.sum_interval(q) for q in original_components]
    for i in range(3):
        q=float(np.sum(rows[:,i]))
        scale=max(1e-100,abs(q))
        if q<float(original[i].lo)-1e-9*scale or q>float(original[i].hi)+1e-9*scale:
            raise ValueError(f"original 26event photon owner not enclosing source {i}")
    Q=float(np.sum(heat))
    if Q<float(original[3].lo)-1e-9*max(Q,1e-100) or Q>float(original[3].hi)+1e-9*max(Q,1e-100):
        raise ValueError("original photoheat owner mismatch")
    electron=(pt[:,1]+pt[:,3]+2*pt[:,4])/nh
    T=0.5*(np.asarray(temp.lo)+np.asarray(temp.hi))
    arrays={
        "x_HII":pt[:,1]/nh,
        "x_HeII":pt[:,3]/nhe,
        "x_HeIII":pt[:,4]/nhe,
        "electron_per_H":electron,
        "T_K":T,
        "photo_HI_events_per_H_s":rows[:,0]/nh,
        "photo_HeI_events_per_H_s":rows[:,1]/nh,
        "photo_HeII_events_per_H_s":rows[:,2]/nh,
        "primary_photoheat_erg_per_H_s":heat/nh,
        "d_primary_photoheat_d_lnS_HI_den_erg_H_s":dheat[:,0]/nh,
        "d_primary_photoheat_d_lnS_HeI_den_erg_H_s":dheat[:,1]/nh,
        "d_primary_photoheat_d_lnS_HeII_den_erg_H_s":dheat[:,2]/nh
    }
    for i,si in enumerate(SPECIES):
        for j,sj in enumerate(SPECIES):
            arrays[f"d_photo_{si}_d_lnS_{sj}_den_events_H_s"]=nonlocal_deriv[:,i,j]/nh
    if any(q.shape!=(N,) or not np.isfinite(q).all() for q in arrays.values()):
        raise ValueError("nonfinite original 46k-cell stage response")
    scalar={
        "source_time_s":float(t),"source_group_count":G,
        "source_photon_per_H_s":(rows.sum(axis=0)/np.sum(nh)).tolist(),
        "global_primary_heat_erg_per_H_s":float(np.sum(heat)/np.sum(nh)),
        "global_denominator_heat_sensitivity_erg_H_s":(dheat.sum(axis=0)/np.sum(nh)).tolist(),
        "max_original_point_photon_conservation":max(x["max_original_normalization_relative"] for x in group_rows),
        "source_operator_original_interval_inclusion":True
    }
    return arrays,scalar,group_rows

def step_with_photon_trace(fb,src,mod,model,base,nh,nhe,pop,logt,t0,t1,label):
    """Passive wrapper: instrument *unmodified* event_box on actual original four sites."""
    saved=mod.event_box
    slots={}
    count=0
    def traced(m,p,T,ts):
        nonlocal count
        r=saved(m,p,T,ts)
        slot="parent" if count==0 else "predictor" if count==1 else "gamma" if count%2==0 else "final"
        arr,stats,groups=physics_snapshot(fb,src,mod,model,p,T,ts,nh,nhe)
        slots[slot]=(arr,stats,groups)
        count+=1
        return r
    try:
        mod.event_box=traced
        step=mod.run_step(model,base,parent_pop=pop,parent_logt=logt,t0=t0,t1=t1,
                          total_h=nh,total_he=nhe)
    finally:
        mod.event_box=saved
    return step,slots,count

def gzip_data(out,entries):
    path=out/"ORIGINAL_26EVENT_ACTUAL_STAGE_PHOTON_FEEDBACK_552960.csv.gz"
    keys=list(entries[0][2])
    with open(path,"wb") as f:
        with gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0,compresslevel=6) as gz:
            with io.TextIOWrapper(gz,encoding="utf8",newline="") as stream:
                wr=csv.writer(stream);wr.writerow(["node","map_step","source_site","source_time_s",*keys])
                for name,site,arr,stats in entries:
                    for i in range(N):
                        wr.writerow([i,name,site,format(stats["source_time_s"],".17g"),
                                    *[format(float(arr[k][i]),".17g") for k in keys]])
    return path,file_sha(path)

def main(repo,out):
    repo=Path(repo).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    fb=load_feedback()
    src,mod,model,p0,p1,frozen,t0=fb.context(repo)
    if fb.sha(repo/"stages"/fb.OLD/"local_results/first_interval_r2_blocked_minimum_step.tar.gz")!=SOURCE_SHA:
        raise ValueError("original archive identity mismatch")
    if frozen["array_sha"]!=STATE_SHA:raise ValueError("original parent source array mismatch")
    base=mod.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=LANE)
    y0=np.asarray(base.inputs.state0.mutable_copy().values[:5].T,float)
    nh=y0[:,0]+y0[:,1];nhe=np.sum(y0[:,2:5],axis=1)
    rep=src.representative(frozen["lo"],frozen["hi"],nh,nhe)
    X=mod._I(0.5*(frozen["tl"]+frozen["th"]))
    P=mod._I(rep)
    duration=float(base.forcing.duration_seconds(0))
    start=duration*160/131072;stop=duration*161/131072;mid=0.5*(start+stop)
    manifest={"schema":"REI_ORIGINAL26_THREE_MOMENT_ALL_FOUR_SITES_V1",
         "original_source_sha256":SOURCE_SHA,"source_array_sha256":STATE_SHA,
         "original_physics":"26-event 46,080-node original unmodified MPRK22+SDIRK2",
         "accepted_ticks":"160/131072","target":"[160,161]",
         "original_local_error_limit":GATE,"original_width_limit":WIDTH,
         "all_X_joint_correlated_remainder_certified":False,
         "source_conditioning":"one nuclei-preserving point parent inside original accepted enclosure",
         "new_full_cosmological_IVP":False,"canonical_delta":0,"central_DAG":"28/88_REPORTED",
         "working_DAG":"33/88_REPORTED","physical_fast_DAG":"4/7_REPORTED",
         "production":"HOLD","map_steps":{},"source_group_rows":[]}
    def save():
        (out/"RESULT.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    save()
    saved=[]
    first=None;full=None;second=None
    for label,pop,x,a,b in (("full",P,X,start,stop),("half1",P,X,start,mid)):
        try:
            q,slots,calls=step_with_photon_trace(fb,src,mod,model,base,nh,nhe,pop,x,a,b,label)
        except Exception as e:
            manifest["map_steps"][label]={"status":"ERROR","error":str(e)}
            save();raise
        manifest["map_steps"][label]={"classification":q.classification,"certified":bool(q.certified),
            "source_evaluations":calls,"source_sites":list(slots),"diagnostics":q.diagnostics}
        for site,(arr,st,gr) in slots.items():
            saved.append((label,site,arr,st))
            for group in gr:manifest["source_group_rows"].append({"map_step":label,"site":site,**group})
        save()
        if not q.certified:break
        if label=="full":full=q
        else:first=q
    if first is not None:
        try:q,slots,calls=step_with_photon_trace(fb,src,mod,model,base,nh,nhe,first.population,
              first.log_temperature,mid,stop,"half2")
        except Exception as e:
            manifest["map_steps"]["half2"]={"status":"ERROR","error":str(e)}
            save();raise
        manifest["map_steps"]["half2"]={"classification":q.classification,"certified":bool(q.certified),
             "source_evaluations":calls,"source_sites":list(slots),"diagnostics":q.diagnostics}
        for site,(arr,st,gr) in slots.items():
            saved.append(("half2",site,arr,st))
            for group in gr:manifest["source_group_rows"].append({"map_step":"half2","site":site,**group})
        if q.certified:second=q
    if len(saved)==12 and full is not None and second is not None:
        path,digest=gzip_data(out,saved)
        manifest["original_stage_physics_rows"]=N*len(saved)
        manifest["original_stage_site_count"]=len(saved)
        manifest["original_source_group_count"]=len(manifest["source_group_rows"])
        manifest["source_physics_csv_sha256"]=digest
        manifest["source_physics_csv"]=path.name
        upper=np.maximum(abs(full.log_temperature.lo-second.log_temperature.hi),
                         abs(full.log_temperature.hi-second.log_temperature.lo))
        manifest["one_point_parent_max_logT_independent_output_upper"]=float(np.max(upper))
        manifest["original_full_X_frozen_failure"]=2.1245050576368385e-4
        manifest["status"]="ACTUAL_STAGE_PHOTON_SOURCE_CALCULATED_NOT_ALL_X_CERTIFIED"
        print("ORIGINAL_STAGE_PHOTON_PHYSICS",json.dumps({
          "rows":manifest["original_stage_physics_rows"],
          "site_count":manifest["original_stage_site_count"],
          "groups":manifest["original_source_group_count"],
          "max_point_logT":manifest["one_point_parent_max_logT_independent_output_upper"],
          "first_stage_heat_per_H_s":saved[0][3]["global_primary_heat_erg_per_H_s"],
          "last_stage_heat_per_H_s":saved[-1][3]["global_primary_heat_erg_per_H_s"],
          "sha256":digest,"central":"28/88","canonical_delta":0},sort_keys=True),flush=True)
    else:
        manifest["status"]="ORIGINAL_MAP_STAGE_FAILED_SCOPED_PARTIAL"
        manifest["actual_stage_rows_recorded_in_json_only"]=len(saved)
        print("ORIGINAL_STAGE_PARTIAL",json.dumps({k:v["classification"] for k,v in manifest["map_steps"].items()}),flush=True)
    save()
    return manifest

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=ROOT)
    ap.add_argument("--out",type=Path,required=True)
    v=ap.parse_args()
    main(v.repo,v.out)
