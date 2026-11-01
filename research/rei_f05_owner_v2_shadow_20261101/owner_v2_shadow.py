#!/usr/bin/env python3
"""One original REI H/He/OTS/thermal tick [160,161] with a proposed V2 owner gate.
NOT the original source owner, NOT official accepted history, NO tick162.
Only changed numeric representation: reuse PR350 positive M-matrix increment.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,sys,os
from pathlib import Path
import numpy as np

SOURCE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
P350_HEAD="38e32c7b23683930e788696bb65e923819678aac"
N=46080
LOCAL_GATE=2e-4
WIDTH_GATE=2e-3
FIELDS=("x_HII","x_HeII","x_HeIII","log_T")
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR",
       "SCRIPT_SELF_SHIELDING_AUDITOR")

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(str(path))
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def check_old_new_gate(old,new,widths,raw_ledgers,events,policy):
    """Reuse actual old owner strict post-map validator on NEW separate receipt."""
    if set(new)!=set(FIELDS) or set(widths)!=set(FIELDS):
        raise ValueError("V2_BAD_COORDINATE_KEYS")
    if old["log_T"]<=LOCAL_GATE:
        raise ValueError("ORIGINAL_HISTORICAL_F05_FAILURE_NOT_REPRODUCED")
    if max(new.values())>=LOCAL_GATE or max(widths.values())>=WIDTH_GATE:
        raise ArithmeticError("V2_FROZEN_GATE_REJECT")
    if events["any_event"]:
        raise ArithmeticError("V2_TABLE_EVENT_REJECT")
    if set(raw_ledgers)!=set(policy.EXPECTED_LEDGER_KEYS):
        raise ArithmeticError("V2_ORIGINAL_14_LEDGER_MISMATCH")
    for name,interval in raw_ledgers.items():
        if len(interval)!=2 or not interval[0]<=0<=interval[1]:
            raise ArithmeticError("V2_LEDGER_ZERO_EXCLUSION:"+name)
    row={"public_widths":widths,"set_ledgers":raw_ledgers,
         "diagnostics":{"map_enclosed":True,
             "validated_local_error_bounds":new,
             "maximum_validated_local_error":max(new.values())}}
    # Contract: this is the real original owner validator implementation.
    policy._validate_post_map_metrics(row,"PASS","V2_SHADOW")
    return row

def source_ledgers(m,model,step2,t0,tm,t1,nh,nhe):
    p=step2.population
    ledgers={
      "H_nuclei":[float(np.min(p.lo[:,0]+p.lo[:,1]-nh)),
                   float(np.max(p.hi[:,0]+p.hi[:,1]-nh))],
      "He_nuclei":[float(np.min(np.sum(p.lo[:,2:5],axis=1)-nhe)),
                    float(np.max(np.sum(p.hi[:,2:5],axis=1)-nhe))]
    }
    for label,event,pbox,time in (
      ("stage",step2.stage_event,p,tm+m.sdirk.GAMMA*(t1-tm)),
      ("final",step2.final_event,p,t1)
    ):
        k=event.photon_identity
        ledgers[label+"_photon_identity"]=[float(np.min(k.lo)),float(np.max(k.hi))]
        energy=event.resolved_heat+event.unresolved_energy+event.escaped_energy+event.chemical_energy
        ledgers[label+"_total_energy"]=[float(np.min(energy.lo)),float(np.max(energy.hi))]
        for gi,res in enumerate(m.group_photon_residuals(model,pbox,time)):
            ledgers[label+"_group_"+str(gi)+"_photon"]=[
                float(np.min(res.lo)),float(np.max(res.hi))]
    return ledgers

def run(repo:Path,lane:str,out:Path):
    repo=Path(repo).resolve()
    out=Path(out).resolve()
    if lane not in LANES:raise ValueError("INVALID_FROZEN_SHAPE_LANE")
    if out.exists():raise FileExistsError("NO_OVERWRITE_EXISTING_NATIVE_DATA")
    out.mkdir(parents=True)
    r={"schema":"REI_F05_V2_OWNER_SHADOW_PHYSICS_CANDIDATE_V1",
       "lane":lane,"original_accepted_tick":"160/131072",
       "shadow_v2_candidate_tick":"161/131072_NOT_OFFICIAL",
       "source_sha256":SOURCE_SHA,"state_array_sha256":STATE_SHA,
       "kernel_sha256":KERNEL_SHA,"original_parent_HEAD":P350_HEAD,
       "central_DAG":"28/88_REPORTED","working_DAG":"33/88_REPORTED",
       "physical_fast_DAG":"4/7_REPORTED","canonical_delta":0,
       "production":"HOLD","original_worker_modified":False,
       "official_tick161_accepted":False,"runtime_contract":"NONAUTHORITATIVE_SHADOW_V2"}
    def checkpoint():
        (out/"V2_RECEIPT.json").write_text(json.dumps(r,indent=2,sort_keys=True,default=str)+"\n")
    checkpoint()
    mm=load("original_rei_f05_mmatrix_for_v2",
            repo/"research/rei_f05_mmatrix_residual_20261101/residual_certificate.py")
    inc=mm.load_original()
    edge=load("original_rei_f05_source_state_for_v2",
              repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    stage=repo/edge.REL_STAGE
    worker=load("original_rei_f05_attempt_worker_for_v2",stage/"analysis/attempt_worker.py")
    # Original immutable inputs are checked from their REAL BYTES.
    source_archive=stage/"local_results"/edge.ARCHIVE_NAME
    if sha(source_archive)!=SOURCE_SHA or sha(worker.KERNEL_PATH)!=KERNEL_SHA:
        raise ValueError("ORIGINAL_SOURCE_OR_KERNEL_BYTE_DRIFT")
    worker.jax_guard.install_if_missing()
    decoded,src=edge.source_state(stage,lane,worker.state_io)
    if src["archive_sha256"]!=SOURCE_SHA or src["accepted_array_sha256"]!=STATE_SHA:
        raise ValueError("ORIGINAL_SOURCE_STATE_LOCK_FAILURE")
    if decoded.metadata["accepted_index"]!=3 or decoded.metadata["endpoint_tick"]!=160:
        raise ValueError("ORIGINAL_ACCEPTED_PARENT_OWNER_MISMATCH")
    base,_,_,nh,nhe=worker._context(worker._kernel(),lane)
    if not np.all(np.asarray(nh)>0) or not np.all(np.asarray(nhe)>0) or len(nh)!=N:
        raise ValueError("ORIGINAL_NUCLEI_SOURCE_BAD")
    m=worker._kernel()
    model=m.rim.ReducedIntervalModel.from_repo(repo)
    p=m._I(decoded.population_lower,decoded.population_upper)
    z=m._I(decoded.log_temperature_lower,decoded.log_temperature_upper)
    duration=float(base.forcing.duration_seconds(0))
    t0=duration*(160/131072)
    t1=duration*(161/131072)
    tm=t0+0.5*(t1-t0)
    r["clock_hex"]={"t0":t0.hex(),"tm":tm.hex(),"t1":t1.hex(),"duration":duration.hex()}
    r["actual_parent_state_member_sha256"]=src["source_state_sha256"]
    r["parent_source_metadata"]=decoded.metadata
    r["original_lock_sha256"]=sha(stage/"INPUT_LOCK.json")
    r["original_worker_sha256"]=sha(stage/"analysis/attempt_worker.py")
    r["original_policy_sha256"]=sha(stage/"analysis/adaptive_policy.py")
    r["numpy_version"]=np.__version__
    checkpoint()
    original_krawczyk=inc.krawczyk_increment
    def independent_v2_increment(module,parent,flux,den,dt,totalh,totalhe):
        return mm.structural_residual_increment(module,parent,flux,den,dt,
                                                totalh,totalhe,inc)
    inc.krawczyk_increment=independent_v2_increment
    maps={}
    increments={}
    receipts={}
    try:
        for label,pp,zz,begin,end in (
           ("full",p,z,t0,t1),
           ("half1",p,z,t0,tm),
           ("half2",None,None,tm,t1)
        ):
            if label=="half2":
                pp=maps["half1"].population
                zz=maps["half1"].log_temperature
            step,delta,details=inc.original_map(m,model,base,label,pp,zz,
                                                  begin,end,nh,nhe)
            receipts[label]=details
            if not step.certified or delta is None:
                raise ArithmeticError("NATIVE_ORIGINAL_"+label+"_MAP_FAILED")
            if details["original_table_event_count"]!=0:
                raise ArithmeticError("ORIGINAL_NATIVE_TABLE_EVENT_"+label)
            maps[label]=step
            increments[label]=delta
        r["native_step_receipts"]=receipts
        checkpoint()
    finally:
        inc.krawczyk_increment=original_krawczyk

    step=maps["half2"]
    whole=maps["full"]
    raw=source_ledgers(m,model,step,t0,tm,t1,nh,nhe)
    event=worker.summarize_events(whole.table_events+
                    maps["half1"].table_events+step.table_events)
    hp=step.population
    fp=whole.population
    widths={
      "x_HII":float(np.max((hp.hi[:,1]-hp.lo[:,1])/nh)),
      "x_HeII":float(np.max((hp.hi[:,3]-hp.lo[:,3])/nhe)),
      "x_HeIII":float(np.max((hp.hi[:,4]-hp.lo[:,4])/nhe)),
      "log_T":float(np.max(step.log_temperature.hi-step.log_temperature.lo))
    }
    half={
      "x_HII":m._I(hp.lo[:,1]/nh,hp.hi[:,1]/nh),
      "x_HeII":m._I(hp.lo[:,3]/nhe,hp.hi[:,3]/nhe),
      "x_HeIII":m._I(hp.lo[:,4]/nhe,hp.hi[:,4]/nhe),
      "log_T":step.log_temperature
    }
    full={
      "x_HII":m._I(fp.lo[:,1]/nh,fp.hi[:,1]/nh),
      "x_HeII":m._I(fp.lo[:,3]/nhe,fp.hi[:,3]/nhe),
      "x_HeIII":m._I(fp.lo[:,4]/nhe,fp.hi[:,4]/nhe),
      "log_T":whole.log_temperature
    }
    old={name:float(np.max(np.maximum(abs(half[name].lo-full[name].hi),
             abs(half[name].hi-full[name].lo)))) for name in FIELDS}
    new={}
    for name in FIELDS:
        D=increments["full"][name]-(increments["half1"][name]+increments["half2"][name])
        bound=inc.interval_upper(D)
        if bound.shape!=(N,) or not np.isfinite(bound).all():
            raise ArithmeticError("ORIGINAL_V2_LOCAL_DEFECT_NONFINITE")
        new[name]=float(np.max(bound))
    # The source original worker policy receives actual source-native raw 14 intervals.
    checked=check_old_new_gate(old,new,widths,raw,event,worker.policy)
    audit=m.primitive.audit_set_ledgers({name:tuple(v) for name,v in raw.items()})
    if not audit.all_include_zero or len(raw)!=14:
        raise ArithmeticError("ORIGINAL_NATIVE_14_LEDGER_FAILED")
    r["old_independent_endpoint_local_upper"]=old
    r["new_original_common_parent_local_upper"]=new
    r["original_public_widths"]=widths
    r["original_native_raw_14_ledgers"]=raw
    r["original_table_event"]=event
    r["original_14_ledger_pass"]=True
    r["original_policy_v2_post_map_validation"]="PASS_SHADOW_ONLY"
    r["original_legacy_worker_gate"]="FAIL_HISTORICAL_UNCHANGED"
    r["candidate_original_science"]="SCOPED_V2_NATIVE_HHE_TICK161_PASS"
    # Persist all 5 H/He physical population intervals plus T for continuation
    # ONLY under an explicitly different, non-authoritative NPZ evidence identity.
    dest=out/"SHADOW_V2_NONAUTHORITATIVE_TICK161.npz"
    with dest.open("xb") as f:
        np.savez_compressed(f,population_lower=hp.lo,population_upper=hp.hi,
            log_temperature_lower=step.log_temperature.lo,
            log_temperature_upper=step.log_temperature.hi,
            source_parent_population_lower=p.lo,
            source_parent_population_upper=p.hi,
            source_parent_logT_lower=z.lo,source_parent_logT_upper=z.hi)
    if dest.read_bytes()[:8]==b"REIADP1\x00":
        raise ArithmeticError("OFFICIAL_OWNER_STATE_FORMAT_FORBIDDEN")
    r["candidate_state_file"]=dest.name
    r["candidate_state_sha256"]=sha(dest)
    r["candidate_state_node_count"]=N
    checkpoint()
    print(json.dumps({"lane":lane,"v2_status":r["candidate_original_science"],
          "old_logT":old["log_T"],"new_logT":new["log_T"],
          "14_ledger":r["original_14_ledger_pass"],
          "v2_state_sha256":r["candidate_state_sha256"],"canonical_delta":0},
          sort_keys=True),flush=True)
    return r

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--repo",type=Path,required=True)
    a.add_argument("--lane",choices=LANES,required=True)
    a.add_argument("--out",type=Path,required=True)
    v=a.parse_args()
    run(v.repo,v.lane,v.out)