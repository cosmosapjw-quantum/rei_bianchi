#!/usr/bin/env python3
"""Read-only original 26-event F05 [0,64] physics direct map; NOT official worker."""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,sys,tarfile
from pathlib import Path
import numpy as np

REPO=Path(__file__).resolve().parents[2]
STAGES=sorted(REPO.glob("stages/*UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY"))
if len(STAGES)!=1:raise RuntimeError("exact original stage not unique")
STAGE=STAGES[0]
A=STAGE/"analysis"
ARCHIVE=STAGE/"local_results/first_interval_r2_blocked_minimum_step.tar.gz"
ARCHIVE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
POLICY_SHA="c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"
KB=1.380649e-16; EV=1.602176634e-12
CHI=(13.598434599702,24.587389011,54.41776)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    assert s is not None and s.loader is not None
    m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def ensure(ok,msg):
    if not ok:raise ValueError("ORIGINAL64_SOURCE_REPLAY_"+msg)
def endpoint(v):
    return [float(np.asarray(v.lo)),float(np.asarray(v.hi))]
def main(priv,pub):
    ensure(sha(ARCHIVE)==ARCHIVE_SHA,"TAR_MISMATCH")
    ensure(sha(A/"adaptive_policy.py")==POLICY_SHA,"POLICY_MISMATCH")
    worker=module("original64_readonly_attempt_worker",A/"attempt_worker.py")
    ensure(sha(worker.KERNEL_PATH)==KERNEL_SHA,"KERNEL_MISMATCH")
    with tarfile.open(ARCHIVE,"r:gz") as z:
        orig=json.load(z.extractfile("receipts/attempt_00000001_000000_000064.json"))
    receipt=next(p["envelope"] for p in orig["processes"] if p["lane"]==LANE)
    ensure(orig["action"]=="ACCEPT" and orig["classification"]=="CANDIDATE_UNSEALED_LOCAL_EXECUTION","HISTORY_STATUS")
    ensure(receipt["candidate_state"]["sha256"]=="aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425","OLD_STATE_SHA")
    guard=worker.jax_guard.install_if_missing()
    m=worker._kernel()
    base,y,logt,total_h,total_he=worker._context(m,LANE)
    ensure(y.shape==(46080,5),"INITIAL_SHAPE")
    initial_pop=m._I(y,y); initial_logt=m._I(logt,logt)
    model=m.rim.ReducedIntervalModel.from_repo(REPO)
    duration=float(base.forcing.duration_seconds(0))
    t0=0.0;t1=duration*(64/131072);mid=t0+.5*(t1-t0)
    kw=dict(model=model,base=base,parent_pop=initial_pop,parent_logt=initial_logt,
            t0=t0,t1=t1,total_h=total_h,total_he=total_he)
    full=m.run_step(**kw);ensure(bool(full.certified),"FULL_MAP")
    kw["t1"]=mid
    first=m.run_step(**kw);ensure(bool(first.certified),"HALF1_MAP")
    kw.update(parent_pop=first.population,parent_logt=first.log_temperature,t0=mid,t1=t1)
    second=m.run_step(**kw);ensure(bool(second.certified),"HALF2_MAP")
    pop=second.population; xf=second.log_temperature
    half={"x_HII":m._I(pop.lo[:,1]/total_h,pop.hi[:,1]/total_h),
          "x_HeII":m._I(pop.lo[:,3]/total_he,pop.hi[:,3]/total_he),
          "x_HeIII":m._I(pop.lo[:,4]/total_he,pop.hi[:,4]/total_he),
          "log_T":xf}
    fp=full.population
    fullc={"x_HII":m._I(fp.lo[:,1]/total_h,fp.hi[:,1]/total_h),
           "x_HeII":m._I(fp.lo[:,3]/total_he,fp.hi[:,3]/total_he),
           "x_HeIII":m._I(fp.lo[:,4]/total_he,fp.hi[:,4]/total_he),
           "log_T":full.log_temperature}
    local={k:float(np.max(np.maximum(np.abs(half[k].lo-fullc[k].hi),
                          np.abs(half[k].hi-fullc[k].lo)))) for k in half}
    widths={k:float(np.max(v.hi-v.lo)) for k,v in half.items()}
    ledgers={"H_nuclei":(float(np.min(pop.lo[:,0]+pop.lo[:,1]-total_h)),
                           float(np.max(pop.hi[:,0]+pop.hi[:,1]-total_h))),
             "He_nuclei":(float(np.min(np.sum(pop.lo[:,2:5],axis=1)-total_he)),
                            float(np.max(np.sum(pop.hi[:,2:5],axis=1)-total_he)))}
    for prefix,event,pbox,ts in (("stage",second.stage_event,second.population,mid+m.sdirk.GAMMA*(t1-mid)),
                                  ("final",second.final_event,second.population,t1)):
        ledgers[prefix+"_photon_identity"]=(float(np.min(event.photon_identity.lo)),float(np.max(event.photon_identity.hi)))
        term=event.resolved_heat+event.unresolved_energy+event.escaped_energy+event.chemical_energy
        ledgers[prefix+"_total_energy"]=(float(np.min(term.lo)),float(np.max(term.hi)))
        for gi,res in enumerate(m.group_photon_residuals(model,pbox,ts)):
            ledgers[f"{prefix}_group_{gi}_photon"]=endpoint(res)
    gate=m.primitive.audit_set_ledgers(ledgers)
    events=full.table_events+first.table_events+second.table_events
    event_count=sum(len(np.asarray(x.node_indices)) for x in events)
    ensure(not any(x.any_event for x in events),"TABLE_EVENT")
    ensure(gate.all_include_zero,"LEDGER_EXCLUSION")
    ensure(max(widths.values())<2e-3 and max(local.values())<2e-4,"ORIGINAL_FIXED_GATE")
    # Original deterministic REIADP1 serialization, with exact historical metadata.
    meta={k:receipt[k] for k in ("accepted_index","input_lock_sha256","job_key","lane",
                "parent_state_sha256","predecessor_kernel_sha256","runtime_contract_sha256","stage_id")}
    meta["endpoint_tick"]=64
    priv.mkdir(parents=True,exist_ok=True)
    st=priv/"FIRST64_CURRENT_RUNTIME_NONAUTHORITATIVE.state"
    state_sha=worker.state_io.write_state(st,meta,pop.lo,pop.hi,xf.lo,xf.hi)
    # Private 46080 source-native material data for Rust consumer, never committed to Git.
    rows=priv/"ORIGINAL64_HHE_MATERIAL_46080.csv"
    fields=["node","N_H","N_He","N_HII_0","N_HeII_0","N_HeIII_0","T0_K",
            "N_HII64_lo","N_HII64_hi","N_HeII64_lo","N_HeII64_hi",
            "N_HeIII64_lo","N_HeIII64_hi","T64_lo_K","T64_hi_K"]
    with rows.open("w",newline="") as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(fields)
        for i in range(46080):
            w.writerow([i,total_h[i],total_he[i],y[i,1],y[i,3],y[i,4],float(np.exp(logt[i])),
                 pop.lo[i,1],pop.hi[i,1],pop.lo[i,3],pop.hi[i,3],
                 pop.lo[i,4],pop.hi[i,4],float(np.exp(xf.lo[i])),float(np.exp(xf.hi[i]))])
    frac_ne0=y[:,1]+y[:,3]+2*y[:,4]
    ne_lo=pop.lo[:,1]+pop.lo[:,3]+2*pop.lo[:,4]
    ne_hi=pop.hi[:,1]+pop.hi[:,3]+2*pop.hi[:,4]
    b0=EV*(CHI[0]*y[:,1]+CHI[1]*y[:,3]+(CHI[1]+CHI[2])*y[:,4])
    b_lo=EV*(CHI[0]*pop.lo[:,1]+CHI[1]*pop.lo[:,3]+(CHI[1]+CHI[2])*pop.lo[:,4])
    b_hi=EV*(CHI[0]*pop.hi[:,1]+CHI[1]*pop.hi[:,3]+(CHI[1]+CHI[2])*pop.hi[:,4])
    u0=1.5*KB*(total_h+total_he+frac_ne0)*np.exp(logt)
    u_lo=1.5*KB*(total_h+total_he+ne_lo)*np.exp(xf.lo)
    u_hi=1.5*KB*(total_h+total_he+ne_hi)*np.exp(xf.hi)
    sum_=lambda v:float(math.fsum(float(x) for x in v))
    stats={"initial_electrons":sum_(frac_ne0),"endpoint_electrons":[sum_(ne_lo),sum_(ne_hi)],
           "electron_change_outer":[sum_(ne_lo)-sum_(frac_ne0),sum_(ne_hi)-sum_(frac_ne0)],
           "initial_ionization_storage_erg":sum_(b0),"endpoint_ionization_storage_erg":[sum_(b_lo),sum_(b_hi)],
           "ionization_storage_change_outer_erg":[sum_(b_lo)-sum_(b0),sum_(b_hi)-sum_(b0)],
           "initial_gas_thermal_erg":sum_(u0),"endpoint_gas_thermal_erg":[sum_(u_lo),sum_(u_hi)],
           "gas_thermal_change_outer_erg":[sum_(u_lo)-sum_(u0),sum_(u_hi)-sum_(u0)],
           "electron_cell_sign_classes":{
            "definitely_decreasing":int(np.sum(ne_hi<frac_ne0)),
            "definitely_increasing":int(np.sum(ne_lo>frac_ne0)),
            "ambiguous":int(np.sum((ne_lo<=frac_ne0)&(ne_hi>=frac_ne0)))}}
    result={"schema":"REI_F05_ORIGINAL64_UNPINNED_SOURCE_NATIVE_26EVENT_AND_RUST_GATE_V1",
            "original_source_tar_sha256":ARCHIVE_SHA,"original_kernel_sha256":KERNEL_SHA,
            "original_accepted_0_64_sha256":receipt["candidate_state"]["sha256"],
            "new_unpinned_0_64_sha256":state_sha,"byte_equal_to_historical":state_sha==receipt["candidate_state"]["sha256"],
            "original_worker_runtime_sha256":receipt["runtime_contract_sha256"],
            "runtime":{"numpy":np.__version__,"pandas":"3.0.0","scipy":"1.17.0",
                       "original_pinned":{"numpy":"2.3.5","pandas":"2.2.3","scipy":"1.17.0"}},
            "physical_rows":len(y),"original_0_64_seconds":t1,
            "source_map_full_half_half_certified":[bool(full.certified),bool(first.certified),bool(second.certified)],
            "original_fixed_local_gate":2e-4,"original_fixed_width_gate":2e-3,
            "recomputed_local_bounds":local,"historical_local_bounds":receipt["diagnostics"]["validated_local_error_bounds"],
            "recomputed_widths":widths,"historical_widths":receipt["public_widths"],
            "recomputed_14_ledgers_include_zero":bool(gate.all_include_zero),
            "recomputed_14_ledger_keys":sorted(ledgers),"table_event_count":event_count,
            "source_job_key_matches_original_receipt":meta["job_key"]==receipt["job_key"],
            "source_material_private_csv_sha256":sha(rows),"source_private_state_sha256":sha(st),
            "physics":stats,"scientific_scope":"EXPLORATORY_UNPINNED_MAP_NOT_WORKER_ACCEPTANCE",
            "canonical_DAG":"28/88","working_DAG":"33/88","fast_DAG":"4/7",
            "canonical_delta":0,"production":"HOLD","original_accepted_tick":"160/131072"}
    pub.mkdir(parents=True,exist_ok=True)
    (pub/"ORIGINAL64_PYTHON_PHYSICAL_RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"ORIGINAL64_PHYSICAL_REPLAY_COMPLETED","source_rows":len(y),
       "byte_equal_to_historical":result["byte_equal_to_historical"],
       "local_max":max(local.values()),"width_max":max(widths.values()),
       "electrons_change":stats["electron_change_outer"],
       "dB_erg":stats["ionization_storage_change_outer_erg"],
       "thermal_change":stats["gas_thermal_change_outer_erg"],
       "PRIVATE_CSV":str(rows),"PUBLIC_JSON":str(pub/"ORIGINAL64_PYTHON_PHYSICAL_RESULT.json")},indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--private-dir",type=Path,required=True)
    p.add_argument("--public-dir",type=Path,required=True)
    a=p.parse_args();main(a.private_dir,a.public_dir)
