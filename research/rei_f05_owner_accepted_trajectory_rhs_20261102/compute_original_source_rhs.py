#!/usr/bin/env python3
"""Original REI F05 26-event native photo/chem/OTS/gas RHS on four accepted epochs.
No mutated history, independent IVP, candidate tick161, or production action.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, importlib.util, io, json, math, subprocess, sys
from pathlib import Path
import numpy as np

N=46080
TICKS=131072
EVE=1.602176634e-12
KB=1.380649e-16
CHI=np.array([13.598434599702,24.587389011,54.41776])
SHA_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SHA_KERN="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
SHA_POLICY="c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
SHA_REI_BASE="fab9429140038974a98f3ad3212036b0227e600e"
SHA_REC_HEAD="0f1f6dbd33a654a3dd49bc2d9dbe8854b572d235"
SHA_HE_HEAD="f2d26ef196b50e69c1793cc4c29e96a248fe6c0b"
SHA_REC_JSON="f015ff77dfdc2afc022360880030aa29f06c234cac146105edbbf291fce39429"
SHA_REC_CSV="6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c"
SHA_HE_JSON="202c422e7c23da3ea93b82e35429efe387b66225107e94248e28c6263facc5e2"
SHA_STATE={
  64:"aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425",
  128:"bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6",
  160:"74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6",
}
RATE_NAMES=("HI_ION","HEI_ION","HEII_ION","HII_CASE_B","HEII_GROUND","HEII_CASE_B","HEIII_GROUND","HEIII_N2","HEIII_CASCADE")
FIELDS=("node","accepted_tick","proper_time_s","N_H","N_He","N_e","T_K",
        "Bdot_net_erg_s","photo_binding_erg_s","collisional_binding_erg_s",
        "OTS_chemical_erg_s","OTS_resolved_heat_erg_s",
        "OTS_unresolved_erg_s","OTS_escaped_erg_s","primary_photoheat_erg_s",
        "Udot_thermochemical_erg_s","native_thermal_rhs_erg_s","dN_e_dt_per_s",
        "Bdot_stoich_scaled_residual","OTS_energy_scaled_residual")

def require(condition,message):
    if not condition:raise ValueError("REI_F05_4EPOCH_ORIGINAL_RHS_"+message)

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    require(spec is not None and spec.loader is not None,"MODULE_LOAD")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def value(a):
    return float(math.fsum(float(v) for v in np.ravel(np.asarray(a,dtype=np.float64))))

def sourced_identity(repo,rec,he,stage,worker,states):
    require(subprocess.run(["git","-C",str(repo),"merge-base","--is-ancestor",SHA_REI_BASE,"HEAD"],check=False).returncode==0,"REI_PARENT_ANCESTRY")
    for path,expected in ((stage/"local_results/first_interval_r2_blocked_minimum_step.tar.gz",SHA_TAR),
                          (stage/"analysis/adaptive_policy.py",SHA_POLICY),
                          (worker.KERNEL_PATH,SHA_KERN)):
        require(sha(path)==expected,"REI_KERNEL_SOURCE_SHA_"+path.name)
    require(subprocess.run(["git","-C",str(rec),"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()==SHA_REC_HEAD,"REC_DONOR_HEAD")
    require(subprocess.run(["git","-C",str(he),"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()==SHA_HE_HEAD,"HE_DONOR_HEAD")
    recpath=rec/"research/rec_f05_accepted_trajectory_20261102/results/SCIENCE_RESULT.json"
    recsv=rec/"research/rec_f05_accepted_trajectory_20261102/results/ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz"
    hepath=he/"research/rei_f05_native_ots_stoichiometric_energy_20261102/results/SCIENCE_RESULT.json"
    require(sha(recpath)==SHA_REC_JSON and sha(recsv)==SHA_REC_CSV,"REC_ORIGINAL_PHYSICAL_SOURCE_BYTE")
    require(sha(hepath)==SHA_HE_JSON,"BASS_HE_ORIGINAL_OTS_SOURCE_BYTE")
    ref=json.loads(recpath.read_text())
    hedata=json.loads(hepath.read_text())
    require(ref["cells_per_epoch"]==N and ref["f05_tick161"]=="NOT_ACCEPTED","REC_ORIGINAL_STATE_SCOPE")
    require(hedata["source_original_tar_sha256"]==SHA_TAR and hedata["kernel_sha256"]==SHA_KERN and hedata["source_original_event_sha256"]=="b9cb365989149a4368b6a257e15cabf8e07c522419bd2328401c90d2fe49ce5d","OTS_SOURCE_ORIGINAL_LOCK")
    require(hedata["source_original_rhs_sha256"]=="b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36","OTS_RHS_SOURCE_SHA")
    for tick,p in states.items():
        require(sha(p)==SHA_STATE[tick],"ORIGINAL_STATE_SHA_"+str(tick))
    return ref,hedata

def physics_at(tick,pops,logt,m,model,base,nH,nHe,csvwriter):
    # Original source-correlated, positive interior of an authentic population interval.
    if tick==0:
        point_pop=np.asarray(pops,dtype=np.float64)
        point_log=np.asarray(logt,dtype=np.float64)
    else:
        interval=pops;logs=logt
        point_pop=model._original_point_from_intervals(interval, nH, nHe) if hasattr(model,"_original_point_from_intervals") else None
        if point_pop is None: raise ValueError("INTERNAL_POINT_TRANSFORM_NOT_BOUND")
        point_log=(logs[0]+logs[1])*0.5
    coords=np.vstack([point_pop[:,0]/model.n_h,
                     point_pop[:,2]/model.n_he,
                     point_pop[:,4]/(point_pop[:,3]+point_pop[:,4]),
                     point_log])
    state=model.coordinates_to_state(coords)
    pop=np.asarray(state.values[:5].T)
    temp=np.asarray(state.temperature_K)
    require(pop.shape==(N,5) and temp.shape==(N,) and np.isfinite(temp).all() and (temp>0).all(),"PHYSICAL_STATE")
    require(np.allclose(pop,point_pop,rtol=5e-14,atol=1e-14),"ORIGINAL_POINT_MATERIAL")
    require(np.allclose(pop[:,0]+pop[:,1],nH,rtol=5e-14,atol=1e-12) and
            np.allclose(pop[:,2]+pop[:,3]+pop[:,4],nHe,rtol=5e-14,atol=1e-12),"NUCLEI_INPUTS")
    duration=float(base.forcing.duration_seconds(0))
    t=duration*tick/TICKS
    point_forcing=model.solver.forcing.point(interval=0,time_s=t)
    vol=np.asarray(model.inputs.comoving_volume_cm3)/(1.0+point_forcing.z)**3
    require((vol>0).all() and np.isfinite(vol).all(),"PROPER_CELL_VOLUME")
    electron=pop[:,1]+pop[:,3]+2*pop[:,4]
    ne=electron/vol
    v=model.source_v_point(point_log)
    owner=model.solver._owner(state,point_forcing)
    photo=model.solver.backend.photo_fields(owner)
    ev=model.event.evaluate_event_flux(populations=pop,temperature_K=temp,
        proper_volume_cm3=vol,photo_hi=photo.HI,photo_hei=photo.HeI,
        photo_heii=photo.HeII,v=v,f=np.full(N,0.1))
    point_photo=np.column_stack((photo.HI,photo.HeI,photo.HeII))
    native_ion=np.column_stack([ev.event_rates[n] for n in RATE_NAMES[:3]])
    coll=native_ion-point_photo
    bind=EVE*(CHI[0]*ev.population_rhs[:,1]+
               CHI[1]*(ev.population_rhs[:,3]+ev.population_rhs[:,4])+
               CHI[2]*ev.population_rhs[:,4])
    p_photo=EVE*(point_photo@CHI)
    p_coll=EVE*(coll@CHI)
    ots=np.asarray(ev.chemical_ots_energy_rate_erg_s)
    ots_h=np.asarray(ev.resolved_ots_heating_erg_s)
    unres=np.asarray(ev.unresolved_ots_energy_erg_s)
    escaped=np.asarray(ev.escaped_ots_energy_erg_s)
    prim=np.asarray(photo.heating)
    rbind=bind-(p_photo+p_coll+ots)
    rots=ots+ots_h+unres+escaped
    scale=np.maximum.reduce((np.abs(bind),np.abs(p_photo),np.abs(p_coll),np.abs(ots),np.full(N,1e-140)))
    scale2=np.maximum.reduce((np.abs(ots),np.abs(ots_h),np.abs(unres),np.abs(escaped),np.full(N,1e-140)))
    rr=np.abs(rbind)/scale;rr2=np.abs(rots)/scale2
    require(np.isfinite(rr).all() and np.isfinite(rr2).all() and np.max(rr)<2e-12 and np.max(rr2)<2e-12,"ENERGY_LEDGER")
    require(np.max(np.abs(ev.population_rhs[:,0]+ev.population_rhs[:,1]))<1e-11*np.max(np.abs(ev.population_rhs[:,1])),"H_NUCLEAR")
    hel=ev.population_rhs[:,2]+ev.population_rhs[:,3]+ev.population_rhs[:,4]
    he_scale=np.maximum(np.max(np.abs(ev.population_rhs[:,2:5]),axis=1),1e-280)
    require(np.max(np.abs(hel)/he_scale)<3e-13,"HE_NUCLEAR")
    particle=nH+nHe+electron
    U=1.5*KB*particle*temp
    d_ne=ev.population_rhs[:,1]+ev.population_rhs[:,3]+2*ev.population_rhs[:,4]
    dlog=model.floating_reference_rhs(coordinates=coords,time_s=t,v=v,f=0.1)[3]
    udot=U*(dlog+d_ne/particle)
    thermal=model.thermal._thermal_rhs_numpy(np.log(temp),pop,vol,prim+ots_h,np.full(N,point_forcing.hubble_s_inv))
    u_scale=np.maximum.reduce((np.abs(thermal),np.abs(prim),np.abs(ots_h),np.abs(udot),np.full(N,1e-130)))
    thermal_error=np.max(np.abs(udot-thermal)/u_scale)
    require(np.isfinite(udot).all() and np.isfinite(thermal).all() and thermal_error<2e-11,"THERMAL_RHS_SOURCE_PARITY")
    powers={"Bdot_net_erg_s":value(bind),"photo_binding_erg_s":value(p_photo),
        "collisional_binding_erg_s":value(p_coll),"OTS_chemical_erg_s":value(ots),
        "OTS_resolved_heat_erg_s":value(ots_h),
        "OTS_unresolved_erg_s":value(unres),"OTS_escaped_erg_s":value(escaped),
        "primary_photoheat_erg_s":value(prim),"Udot_thermochemical_erg_s":value(udot),
        "native_thermal_rhs_erg_s":value(thermal),
        "dNe_dt_per_s":value(d_ne),"resolved_heat_erg_s":value(prim+ots_h),
        "cooling_plus_expansion_erg_s":value(prim+ots_h-thermal),
        "nine_original_event_rates_per_s":{n:value(ev.event_rates[n]) for n in RATE_NAMES}}
    for i in range(N):
        csvwriter.writerow((i,tick,format(t,".17e"),
            *[format(float(x[i]),".17e") for x in (nH,nHe,electron,temp,bind,
                p_photo,p_coll,ots,ots_h,unres,escaped,prim,udot,thermal,d_ne,rr,rr2)]))
    return {"tick":tick,"proper_time_s":t,"source_rows":N,
        "point_method":"ORIGINAL_REI_ACCEPTED_ELEMENT_CONSERVING_INTERVAL_INTERIOR" if tick else "ORIGINAL_SOURCE_INITIAL",
        "source_powers":powers,"maximum_source_stoich_scaled_residual":float(np.max(rr)),
        "maximum_OTS_scaled_residual":float(np.max(rr2)),
        "maximum_Udot_thermal_scaled_residual":float(thermal_error),
        "T_K_minmax":[float(np.min(temp)),float(np.max(temp))]}

def run(args):
    repo=Path(args.rei).resolve()
    stage=next(repo.glob("stages/*UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY"))
    worker=load("rei_f05_readonly_native_worker",stage/"analysis/attempt_worker.py")
    states={64:Path(args.tick64),128:Path(args.tick128),160:Path(args.tick160)}
    ref,hedata=sourced_identity(repo,Path(args.rec),Path(args.he),stage,worker,states)
    edge=load("rei_f05_readonly_edge",repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    worker.jax_guard.install_if_missing()
    kernel=worker._kernel()
    base,y,logt,nH,nHe=worker._context(kernel,"LOCAL_NEUTRAL_HAZARD_PRIMARY")
    model=kernel.rim.ReducedIntervalModel.from_repo(repo)
    require(y.shape==(N,5),"ORIGINAL_STATE_NODES")
    # Bind source-original scientific construction, do not hand-author a surrogate.
    model._original_point_from_intervals=lambda ab,hn,hen: edge.element_conserving_parent_candidate(ab[0],ab[1],hn,hen)
    private=Path(args.private);public=Path(args.public)
    private.mkdir(parents=True,exist_ok=True);public.mkdir(parents=True,exist_ok=True)
    privatecsv=private/"ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz"
    summary={}
    with privatecsv.open("wb") as sink:
        with gzip.GzipFile(fileobj=sink,mode="wb",filename="",mtime=0,compresslevel=6) as gz:
            with io.TextIOWrapper(gz,encoding="ascii",newline="") as stream:
                writer=csv.writer(stream,lineterminator="\n")
                writer.writerow(FIELDS)
                for tick in (0,64,128,160):
                    if tick==0:pops=y;logx=logt
                    else:
                        dec=worker.state_io.read_state(states[tick],expected_sha256=SHA_STATE[tick])
                        require(dec.metadata.get("endpoint_tick")==tick,"STATE_TIME_METADATA")
                        pops=(dec.population_lower,dec.population_upper)
                        logx=(dec.log_temperature_lower,dec.log_temperature_upper)
                    summary[tick]=physics_at(tick,pops,logx,kernel,model,base,nH,nHe,writer)
                    print(json.dumps({"tick":tick,"Bdot":summary[tick]["source_powers"]["Bdot_net_erg_s"],
                        "Udot":summary[tick]["source_powers"]["Udot_thermochemical_erg_s"],
                        "max_residual":summary[tick]["maximum_source_stoich_scaled_residual"]}),
                        flush=True)
    hepower=hedata["result"]["physical_energy_powers"]
    t160=summary[160]["source_powers"]
    for key,remote in hepower.items():
        if key in t160:
            rel=abs(t160[key]-remote)/max(abs(remote),abs(t160[key]),1e-120)
            require(rel<6e-11,"BASS_HE150_SOURCE_POINT_RATE_"+key)
    intervals=[]
    for row in ref["interval_physics"]:
        a,b=map(int,row["interval_ticks"])
        require((a,b) in ((0,64),(64,128),(128,160)),"ORIGINAL_SEGMENT")
        source_dt=float(row["source_dt_seconds"])
        require(abs((summary[b]["proper_time_s"]-summary[a]["proper_time_s"])/source_dt-1.0)<3e-14,"EXACT_ORIGINAL_TIME")
        entry={"original_interval_ticks":[a,b],"source_dt_seconds":source_dt}
        for field,key in (("B","Bdot_net_erg_s"),("U","Udot_thermochemical_erg_s")):
            lo,hi=row[f"source_delta_{field}_secant_erg_s"]
            pa=summary[a]["source_powers"][key];pb=summary[b]["source_powers"][key]
            trap=(pa+pb)/2.0
            entry[field]={"accepted_material_source_secant_erg_s":[lo,hi],
                "instantaneous_source_rate_left_erg_s":pa,
                "instantaneous_source_rate_right_erg_s":pb,
                "trapezoid_endpoint_derivative_erg_s":trap,
                "point_trapezoid_minus_interval_secant_erg_s":[trap-hi,trap-lo],
                "left_inside_secant":lo<=pa<=hi,
                "right_inside_secant":lo<=pb<=hi,
                "trapezoid_inside_secant":lo<=trap<=hi}
        intervals.append(entry)
    result={"schema":"REI_F05_4_ORIGINAL_ACCEPTED_EPOCH_FULL26_SOURCE_CHEM_THERMAL_RHS_V1",
      "original_state_source_sha256":SHA_TAR,
      "original_kernel_sha256":SHA_KERN,"original_policy_sha256":SHA_POLICY,
      "accepted_primary_state_sha256":{str(k):v for k,v in SHA_STATE.items()},
      "other_owner_inputs":{"REC_PR195_SCIENCE_JSON_SHA256":SHA_REC_JSON,
         "REC_PR195_PHYSICAL_CSV_SHA256":SHA_REC_CSV,
         "BASS_HE150_SOURCE26_JSON_SHA256":SHA_HE_JSON},
      "original_epoch_results":[summary[k] for k in (0,64,128,160)],
      "original_accepted_interval_comparisons":intervals,
      "source_46080_cell_rows":4*N,
      "private_original_26event_4epoch_gzip_sha256":sha(privatecsv),
      "private_original_26event_4epoch_gzip_bytes":privatecsv.stat().st_size,
      "science_claim_scope":"ORIGINAL_FROZEN_ACCEPTED_MATERIAL_F05_SOURCE_RHS_NOT_NEW_INTEGRATED_IVP",
      "old_original_first_tick161_gate":"FAIL_V1_UNCHANGED",
      "new_official_tick161":False,
      "original_worker_modified":False,
      "original_dag":{"central":"28/88","working":"33/88_NONADDITIVE","physical_fast":"4/7","delta":0},
      "production":"HOLD"}
    out=public/"ORIGINAL_F05_4EPOCH_RHS_SCIENCE.json"
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"science_result_sha256":sha(out),"private_data_sha256":sha(privatecsv),
        "rate_rows":4*N,"central_DAG":"28/88","old_tick161":"V1_FAIL"}),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for name in ("rei","rec","he","tick64","tick128","tick160","private","public"):ap.add_argument("--"+name,required=True)
    run(ap.parse_args())
