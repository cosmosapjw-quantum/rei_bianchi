#!/usr/bin/env python3
"""Original first64 F05 predecessor across all shape lanes. Original 26-event map,
zero edits to worker/history. No official production admission."""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math, sys, tarfile, gzip
from pathlib import Path
import numpy as np

REPO=Path(__file__).resolve().parents[2]
STAGES=list(REPO.glob("stages/*UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY"))
assert len(STAGES)==1
STAGE=STAGES[0]
ARCHIVE=STAGE/"local_results/first_interval_r2_blocked_minimum_step.tar.gz"
A=STAGE/"analysis"
TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
POLICY_SHA="c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR","SCRIPT_SELF_SHIELDING_AUDITOR")
KB=1.380649e-16
EV=1.602176634e-12
CHI=(13.598434599702,24.587389011,54.417760)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def import_at(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    assert spec and spec.loader
    x=importlib.util.module_from_spec(spec)
    sys.modules[name]=x
    spec.loader.exec_module(x)
    return x

def require(ok,msg):
    if not ok: raise ValueError("ORIGINAL_FIRST64_ALL_LANE_"+msg)

def bounds(v): return [float(np.asarray(v.lo)),float(np.asarray(v.hi))]

def main(private,public,primary_previous):
    require(sha(ARCHIVE)==TAR_SHA,"SOURCE_ARCHIVE_DRIFT")
    require(sha(A/"adaptive_policy.py")==POLICY_SHA,"ADAPTIVE_POLICY_DRIFT")
    worker=import_at("all_lane_readonly_original_worker",A/"attempt_worker.py")
    require(sha(worker.KERNEL_PATH)==KERNEL_SHA,"ORIGINAL_KERNEL_DRIFT")
    with tarfile.open(ARCHIVE,"r:gz") as tar:
        receipt=json.load(tar.extractfile("receipts/attempt_00000001_000000_000064.json"))
    require(receipt["action"]=="ACCEPT" and receipt["classification"]=="CANDIDATE_UNSEALED_LOCAL_EXECUTION","ORIGINAL_RECEIPT")
    rec={x["lane"]:x["envelope"] for x in receipt["processes"]}
    require(set(rec)==set(LANES),"ORIGINAL_THREE_LANE_RECEIPTS")
    worker.jax_guard.install_if_missing()
    m=worker._kernel()
    model=m.rim.ReducedIntervalModel.from_repo(REPO)
    private.mkdir(parents=True,exist_ok=True)
    public.mkdir(parents=True,exist_ok=True)
    first_sha=sha(primary_previous)
    require(first_sha==rec[LANES[0]]["candidate_state"]["sha256"],"PRIMARY_PARENT_BYTE_REF")
    outputs=[]
    all_states=[]
    for lane in LANES:
        original=rec[lane]
        if lane==LANES[0]:
            outputs.append({
                "lane":lane,"classification":"REUSED_VERIFIED_ORIGINAL64_RUST_OWNER_PR363",
                "original_state_sha256":original["candidate_state"]["sha256"],
                "replayed_state_sha256":first_sha,
                "byte_identical":True,
                "original_widths":original["public_widths"],
                "original_validated_local_bounds":original["diagnostics"]["validated_local_error_bounds"],
                "reported_new_46080_source_maps":False
            })
            continue
        base,y,logt,total_h,total_he=worker._context(m,lane)
        require(y.shape==(46080,5),"SOURCE_STATE_SHAPE")
        parent_pop=m._I(y,y);parent_log=m._I(logt,logt)
        duration=float(base.forcing.duration_seconds(0))
        t0=0.0;t1=duration*64/131072;tm=(t0+t1)*0.5
        kw=dict(model=model,base=base,parent_pop=parent_pop,parent_logt=parent_log,
                t0=t0,t1=t1,total_h=total_h,total_he=total_he)
        full=m.run_step(**kw); require(full.certified,"FULL_"+lane)
        kw["t1"]=tm
        half1=m.run_step(**kw); require(half1.certified,"HALF1_"+lane)
        kw.update(parent_pop=half1.population,parent_logt=half1.log_temperature,t0=tm,t1=t1)
        half2=m.run_step(**kw); require(half2.certified,"HALF2_"+lane)
        pop=half2.population;lf=half2.log_temperature
        fh={
          "x_HII":m._I(pop.lo[:,1]/total_h,pop.hi[:,1]/total_h),
          "x_HeII":m._I(pop.lo[:,3]/total_he,pop.hi[:,3]/total_he),
          "x_HeIII":m._I(pop.lo[:,4]/total_he,pop.hi[:,4]/total_he),
          "log_T":lf}
        pf=full.population
        ffull={
          "x_HII":m._I(pf.lo[:,1]/total_h,pf.hi[:,1]/total_h),
          "x_HeII":m._I(pf.lo[:,3]/total_he,pf.hi[:,3]/total_he),
          "x_HeIII":m._I(pf.lo[:,4]/total_he,pf.hi[:,4]/total_he),
          "log_T":full.log_temperature}
        widths={k:float(np.max(v.hi-v.lo)) for k,v in fh.items()}
        local={k:float(np.max(np.maximum(abs(fh[k].lo-ffull[k].hi),
                        abs(fh[k].hi-ffull[k].lo)))) for k in fh}
        ledgers={
          "H_nuclei":(float(np.min(pop.lo[:,0]+pop.lo[:,1]-total_h)),float(np.max(pop.hi[:,0]+pop.hi[:,1]-total_h))),
          "He_nuclei":(float(np.min(np.sum(pop.lo[:,2:5],axis=1)-total_he)),float(np.max(np.sum(pop.hi[:,2:5],axis=1)-total_he)))}
        for prefix,event,pbox,t in (
                ("stage",half2.stage_event,half2.population,tm+m.sdirk.GAMMA*(t1-tm)),
                ("final",half2.final_event,half2.population,t1)):
            ledgers[prefix+"_photon_identity"]=(float(np.min(event.photon_identity.lo)),float(np.max(event.photon_identity.hi)))
            resid=event.resolved_heat+event.unresolved_energy+event.escaped_energy+event.chemical_energy
            ledgers[prefix+"_total_energy"]=(float(np.min(resid.lo)),float(np.max(resid.hi)))
            for gi,r in enumerate(m.group_photon_residuals(model,pbox,t)):
                ledgers[f"{prefix}_group_{gi}_photon"]=bounds(r)
        audited=m.primitive.audit_set_ledgers(ledgers)
        events=full.table_events+half1.table_events+half2.table_events
        event_count=sum(len(np.asarray(x.node_indices)) for x in events)
        require(len(ledgers)==14 and audited.all_include_zero,"LEDGER_"+lane)
        require(not any(x.any_event for x in events) and event_count==0,"TABLE_"+lane)
        require(max(widths.values())<.002 and max(local.values())<.0002,"FROZEN_GATES_"+lane)
        # Bind the exact original historical job metadata; no synthetic accepted index.
        meta={k:original[k] for k in ("accepted_index","input_lock_sha256","job_key","lane",
            "parent_state_sha256","predecessor_kernel_sha256","runtime_contract_sha256","stage_id")}
        meta["endpoint_tick"]=64
        state=private/(lane+".state")
        current_sha=worker.state_io.write_state(state,meta,pop.lo,pop.hi,lf.lo,lf.hi)
        require(current_sha==sha(state),"REPLAY_STATE_SHA_READBACK_"+lane)
        original_sha=original["candidate_state"]["sha256"]
        # Physical source-native counts and potential/thermal reservoirs, preserving intervals.
        ne0=y[:,1]+y[:,3]+2*y[:,4]
        ne_l=pop.lo[:,1]+pop.lo[:,3]+2*pop.lo[:,4]
        ne_u=pop.hi[:,1]+pop.hi[:,3]+2*pop.hi[:,4]
        b0=EV*(CHI[0]*y[:,1]+CHI[1]*y[:,3]+(CHI[1]+CHI[2])*y[:,4])
        b_l=EV*(CHI[0]*pop.lo[:,1]+CHI[1]*pop.lo[:,3]+(CHI[1]+CHI[2])*pop.lo[:,4])
        b_u=EV*(CHI[0]*pop.hi[:,1]+CHI[1]*pop.hi[:,3]+(CHI[1]+CHI[2])*pop.hi[:,4])
        u0=1.5*KB*(total_h+total_he+ne0)*np.exp(logt)
        u_l=1.5*KB*(total_h+total_he+ne_l)*np.exp(lf.lo)
        u_u=1.5*KB*(total_h+total_he+ne_u)*np.exp(lf.hi)
        sumv=lambda a:float(math.fsum(float(x) for x in a))
        d_ne=[sumv(ne_l)-sumv(ne0),sumv(ne_u)-sumv(ne0)]
        d_b=[sumv(b_l)-sumv(b0),sumv(b_u)-sumv(b0)]
        d_u=[sumv(u_l)-sumv(u0),sumv(u_u)-sumv(u0)]
        # Real 46k source variation: save only privately, never commit to Git.
        csvpath=private/(lane+"_PHYSICAL_46080.csv.gz")
        with gzip.open(csvpath,"wt",newline="") as z:
            writer=csv.writer(z)
            writer.writerow(("node","Ne0","Ne64_lo","Ne64_hi","B0_erg","B64_lo_erg","B64_hi_erg","U0_erg","U64_lo_erg","U64_hi_erg"))
            for i in range(46080):
                writer.writerow((i,ne0[i],ne_l[i],ne_u[i],b0[i],b_l[i],b_u[i],u0[i],u_l[i],u_u[i]))
        original_local=original["diagnostics"]["validated_local_error_bounds"]
        orig_width=original["public_widths"]
        data={"lane":lane,"classification":"SOURCE_MAP_REPLAY_UNPINNED_NOT_PRODUCTION",
            "original_state_sha256":original_sha,"replayed_state_sha256":current_sha,
            "byte_identical":original_sha==current_sha,
            "source_rows":len(y),"source_map_certification":[bool(full.certified),bool(half1.certified),bool(half2.certified)],
            "ledger_keys":sorted(ledgers),"ledgers_all_include_zero":bool(audited.all_include_zero),
            "table_events":event_count,"original_widths":orig_width,"replay_widths":widths,
            "original_validated_local_bounds":original_local,"replay_validated_local_bounds":local,
            "max_abs_local_difference":max(abs(local[k]-original_local[k]) for k in local),
            "max_abs_width_difference":max(abs(widths[k]-orig_width[k]) for k in widths),
            "proper_dt_s":t1,"physical_interval_delta_Ne":d_ne,
            "physical_interval_delta_B_erg":d_b,"physical_interval_delta_U_erg":d_u,
            "definite_ne_decrease":int(np.sum(ne_u<ne0)),
            "definite_ne_increase":int(np.sum(ne_l>ne0)),
            "uncertain_ne_sign":int(np.sum((ne_l<=ne0)&(ne_u>=ne0))),
            "private_state_sha256":sha(state),
            "private_physical_csv_gz_sha256":sha(csvpath),
            "private_physical_csv_gz_bytes":csvpath.stat().st_size}
        outputs.append(data)
        print(json.dumps({"lane":lane,"byte_identical":data["byte_identical"],
                          "original_sha":original_sha,"replayed_sha":current_sha,
                          "dNe":d_ne,"dB":d_b,"dU":d_u,"max_local":max(local.values()),
                          "max_width":max(widths.values())},sort_keys=True),flush=True)
    report={"schema":"REI_F05_HISTORICAL_ORIGINAL64_ALLLANE_SOURCE_REPLAY_V1",
      "parent_REI_PR":363,"parent_HEAD":"abf83d4d883d5f311426b7f02cb001e70138ceb4",
      "original_source_tar_sha256":TAR_SHA,"original_kernel_sha256":KERNEL_SHA,
      "reused_original_primary_from_PR363_sha256":first_sha,"source_map_rows_per_lane":46080,
      "original_lanes":list(LANES),"historical_all_lane_byte_identity":all(x["byte_identical"] for x in outputs),
      "actually_new_native_lanes_recomputed":2,"new_source_map_stage_calls":6,
      "lanes":outputs,"runtime_deps":{"numpy":np.__version__,
        "historical_numpy":"2.3.5","historical_scipy":"1.17.0","historical_pandas":"2.2.3"},
      "original_accepted_tick":"160/131072","candidate_tick161":"NOT_ACCEPTED",
      "production":"HOLD","canonical_DAG":"28/88","working_DAG":"33/88",
      "physical_fast":"4/7","canonical_delta":0,
      "scope":"ALL_LANE_HISTORICAL_STATE_IDENTITY_NOT_V2_WORKER_RUNTIME_ADMISSION"}
    public_file=public/"ALL_LANE_ORIGINAL64_SCIENCE.json"
    public_file.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"all_lanes_byte_identical":report["historical_all_lane_byte_identity"],
        "science_sha256":sha(public_file),"canonical_DAG":"28/88"}),flush=True)
    require(report["historical_all_lane_byte_identity"],"STATE_SHA_NOT_EQUAL_HISTORIC")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--private",type=Path,required=True)
    ap.add_argument("--public",type=Path,required=True)
    ap.add_argument("--primary-previous",type=Path,required=True)
    a=ap.parse_args()
    main(a.private,a.public,a.primary_previous)
