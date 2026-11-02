#!/usr/bin/env python3
"""REI original F05 one bounded post-tick161 physics consumer, NONPRODUCTION.

Reads the original 46,080-cell [160,161] V2 source candidate as actual parent
and computes [161,162] from unchanged original 26-event source under original
MPRK22(1) / Alexander-SDIRK2 and opt-in source-native common-parent defect.
Source/worker/history/main and V1 failure are never modified or rewritten.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,os,sys,time
from pathlib import Path
import numpy as np

LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR",
       "SCRIPT_SELF_SHIELDING_AUDITOR")
N=46080
SRC="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
STATE160="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
CANDIDATE161="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
GATE=2e-4
WIDTH=2e-3
TICKS=131072
KB=1.380649e-16
EV=1.602176634e-12
CHI=(13.598434599702,24.587389011,54.417760)
FIELDS=("x_HII","x_HeII","x_HeIII","log_T")
SOURCE_CLOCK_LEFT=161
SOURCE_CLOCK_RIGHT=162

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def require(cond,key):
    if not cond:raise ValueError("REI_VERSIONED_TICK161_CONSUMER_"+key)

def module(name,path):
    s=importlib.util.spec_from_file_location(name,str(path))
    if s is None or s.loader is None:raise ImportError(path)
    x=importlib.util.module_from_spec(s);sys.modules[name]=x;s.loader.exec_module(x)
    return x

def interval_material(pl,ph,zl,zh,nh,nhe):
    require(pl.shape==(N,5) and ph.shape==(N,5) and zl.shape==(N,) and zh.shape==(N,),"SHAPE")
    require(np.isfinite(pl).all() and np.isfinite(ph).all() and np.isfinite(zl).all() and np.isfinite(zh).all(),"FINITE")
    require(np.all(pl>0) and np.all(pl<=ph) and np.all(zl<=zh),"POSITIVITY")
    h_lo=pl[:,0]+pl[:,1];h_hi=ph[:,0]+ph[:,1]
    he_lo=np.sum(pl[:,2:5],axis=1);he_hi=np.sum(ph[:,2:5],axis=1)
    require(np.all(h_lo<=nh*(1+4e-12)) and np.all(h_hi>=nh*(1-4e-12)),"H_NUCLEI_ENCLOSURE")
    require(np.all(he_lo<=nhe*(1+4e-12)) and np.all(he_hi>=nhe*(1-4e-12)),"HE_NUCLEI_ENCLOSURE")
    def physical(x,T):
        ne=x[:,1]+x[:,3]+2*x[:,4]
        b=EV*(CHI[0]*x[:,1]+CHI[1]*(x[:,3]+x[:,4])+CHI[2]*x[:,4])
        u=1.5*KB*(nh+nhe+ne)*np.exp(T)
        return ne,b,u
    lo=physical(pl,zl);hi=physical(ph,zh)
    for a,b in zip(lo,hi):
        require(np.isfinite(a).all() and np.isfinite(b).all() and np.all(a>0) and np.all(b>=a),"PHYSICAL_INTERVAL")
    return lo,hi

def sum_interval(lo,hi):
    return [float(math.fsum(float(x) for x in lo)),float(math.fsum(float(x) for x in hi))]

def material_delta(x,y):
    return [float(y[0]-x[1]),float(y[1]-x[0])]

def execute(repo,parent_file,parent_receipt,out_dir,lane):
    repo=repo.resolve()
    require(lane in LANES,"LANE")
    require(not out_dir.exists(),"OUTPUT_EXISTS")
    require(sha(parent_file)==CANDIDATE161,"PARENT161_SHA")
    r=json.loads(parent_receipt.read_text())
    require(sha(parent_file)==r["candidate_state_sha256"],"PARENT_RECEIPT_SHA")
    require(r["source_sha256"]==SRC and r["kernel_sha256"]==KERNEL and
            r["state_array_sha256"]==STATE160,"ORIGINAL_SOURCE_IDENTITIES")
    require(r["shadow_v2_candidate_tick"]=="161/131072_NOT_OFFICIAL" and
            r["original_accepted_tick"]=="160/131072" and
            r["official_tick161_accepted"] is False,"NO_FALSE_OFFICIAL_ACCEPTANCE")
    require(r["original_14_ledger_pass"] is True and
            not r["original_table_event"]["any_event"] and
            set(r["original_native_raw_14_ledgers"])==set(
                ("H_nuclei","He_nuclei","stage_photon_identity","stage_total_energy",
                 "final_photon_identity","final_total_energy",
                 *[f"stage_group_{g}_photon" for g in range(4)],
                 *[f"final_group_{g}_photon" for g in range(4)])),"PARENT_ORIGINAL_LEDGER")
    require(max(r["new_original_common_parent_local_upper"].values())<GATE and
            max(r["original_public_widths"].values())<WIDTH and
            r["old_independent_endpoint_local_upper"]["log_T"]>GATE,"ORIGINAL_V2_GATE_OR_V1_FAIL")
    st=sorted(repo.glob("stages/*UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY"))
    require(len(st)==1,"STAGE_UNIQUE")
    stage=st[0]
    loader=module("rei_tick161_v2_owner",repo/"research/rei_f05_owner_v2_shadow_20261101/owner_v2_shadow.py")
    mm=module("rei_tick161_original_mmatrix",repo/"research/rei_f05_mmatrix_residual_20261101/residual_certificate.py")
    inc=mm.load_original()
    worker=loader.load("rei_tick161_original_attempt_worker",stage/"analysis/attempt_worker.py")
    require(loader.sha(stage/"local_results/first_interval_r2_blocked_minimum_step.tar.gz")==SRC,"SOURCE_ARCHIVE")
    require(loader.sha(worker.KERNEL_PATH)==KERNEL,"SOURCE_KERNEL")
    worker.jax_guard.install_if_missing()
    m=worker._kernel()
    base,_,_,nh,nhe=worker._context(m,lane)
    model=m.rim.ReducedIntervalModel.from_repo(repo)
    duration=float(base.forcing.duration_seconds(0))
    t0=float(duration*(SOURCE_CLOCK_LEFT/TICKS))
    t1=float(duration*(SOURCE_CLOCK_RIGHT/TICKS))
    tm=t0+0.5*(t1-t0)
    require(t0.hex()==r["clock_hex"]["t1"],"EXACT_V2_PARENT_CLOCK_T161")
    with np.load(parent_file,allow_pickle=False) as z:
        names=set(z.files)
        require(names==set(("population_lower","population_upper","log_temperature_lower",
            "log_temperature_upper","source_parent_population_lower","source_parent_population_upper",
            "source_parent_logT_lower","source_parent_logT_upper")),"V2_PARENT_SCHEMA")
        plo=z["population_lower"].copy();phi=z["population_upper"].copy()
        zlo=z["log_temperature_lower"].copy();zhi=z["log_temperature_upper"].copy()
        origp=z["source_parent_population_lower"].copy();origh=z["source_parent_population_upper"].copy()
    require(plo.shape==(N,5),"PARENT_NODECOUNT")
    require(np.isfinite(origp).all() and np.isfinite(origh).all(),"SOURCE_ORIGINAL_PARENT_FINITE")
    parent_mat_lo,parent_mat_hi=interval_material(plo,phi,zlo,zhi,nh,nhe)
    p=m._I(plo,phi);lt=m._I(zlo,zhi)
    # One source-native one-tick experiment, no destructive runtime worker mutation.
    out_dir.mkdir(parents=True)
    result={
      "schema":"REI_F05_ORIGINAL_V2_VERSIONED_CAUSAL_TICK161_CONSUMER_V1",
      "original_source_tar_sha256":SRC,"original_source_kernel_sha256":KERNEL,
      "original_tick160_array_sha256":STATE160,
      "original_accepted_tick":"160/131072",
      "research_parent_tick":161,"research_result_tick":162,
      "source_parent_tick161_sha256":sha(parent_file),
      "source_parent_receipt_sha256":sha(parent_receipt),
      "source_parent_original_V1_failure_logT":r["old_independent_endpoint_local_upper"]["log_T"],
      "source_parent_original_V2_gate_logT":r["new_original_common_parent_local_upper"]["log_T"],
      "source_lane":lane,
      "original_source_clock_hex":{"t0":t0.hex(),"mid":tm.hex(),"t1":t1.hex(),"duration":duration.hex()},
      "worker_version":"REI_F05_RESEARCH_V2_PARENT_CONSUMER_1",
      "canonical_original_state_format_overwritten":False,
      "original_source_map_changed":False,
      "official_tick161_accepted":False,"official_tick162_accepted":False,
      "production":"HOLD","canonical_DAG":"28/88","working_DAG":"33/88",
      "physical_fast_DAG":"4/7","canonical_delta":0,
      "actual_original_26event_full_half_maps":[],
      "original_14_ledgers_include_zero":False,
      "original_one_tick_physics_generated":False}
    def snapshot():
        (out_dir/"SCIENTIFIC_CONSUMER_RECEIPT.json").write_text(json.dumps(result,indent=2,sort_keys=True,default=str)+"\n")
    snapshot()
    oldinc=inc.krawczyk_increment
    def v2_increment(module_,parent,flux,den,dt,th,the):
        return mm.structural_residual_increment(module_,parent,flux,den,dt,th,the,inc)
    inc.krawczyk_increment=v2_increment
    steps={};deltas={};recs={}
    try:
        for label,pp,zz,left,right in (
            ("full",p,lt,t0,t1),("half1",p,lt,t0,tm),("half2",None,None,tm,t1)):
            if label=="half2":
                pp=steps["half1"].population;zz=steps["half1"].log_temperature
            stp,delta,rec=inc.original_map(m,model,base,label,pp,zz,left,right,nh,nhe)
            recs[label]=rec
            require(stp.certified and delta is not None,"NATIVE_MAP_"+label)
            require(rec["original_table_event_count"]==0,"NATIVE_EVENTS_"+label)
            steps[label]=stp;deltas[label]=delta
            result["actual_original_26event_full_half_maps"].append(
                {"name":label,"native_certified":True,"event_count":rec["original_table_event_count"],
                 "original_population_solves":rec["original_population_solves"],
                 "original_thermal_roots":rec["original_root_calls"],
                 "original_increment_HHe_blocks":rec.get("increment_krawczyk_blocks")})
            snapshot()
    except Exception as e:
        result.update(status="SCOPED_SOURCE_MAP_FAILED",error_type=type(e).__name__,error=str(e))
        snapshot()
        raise
    finally:
        inc.krawczyk_increment=oldinc
    whole=steps["full"];last=steps["half2"]
    hp=last.population;fp=whole.population
    half={"x_HII":m._I(hp.lo[:,1]/nh,hp.hi[:,1]/nh),
          "x_HeII":m._I(hp.lo[:,3]/nhe,hp.hi[:,3]/nhe),
          "x_HeIII":m._I(hp.lo[:,4]/nhe,hp.hi[:,4]/nhe),
          "log_T":last.log_temperature}
    full={"x_HII":m._I(fp.lo[:,1]/nh,fp.hi[:,1]/nh),
          "x_HeII":m._I(fp.lo[:,3]/nhe,fp.hi[:,3]/nhe),
          "x_HeIII":m._I(fp.lo[:,4]/nhe,fp.hi[:,4]/nhe),
          "log_T":whole.log_temperature}
    old_defect={
        key:float(np.max(np.maximum(abs(half[key].lo-full[key].hi),
                  abs(half[key].hi-full[key].lo)))) for key in FIELDS}
    new_defect={}
    for key in FIELDS:
        d=deltas["full"][key]-(deltas["half1"][key]+deltas["half2"][key])
        q=inc.interval_upper(d)
        require(q.shape==(N,) and np.isfinite(q).all(),"V2_DEFECT_"+key)
        new_defect[key]=float(np.max(q))
    width={
       "x_HII":float(np.max((hp.hi[:,1]-hp.lo[:,1])/nh)),
       "x_HeII":float(np.max((hp.hi[:,3]-hp.lo[:,3])/nhe)),
       "x_HeIII":float(np.max((hp.hi[:,4]-hp.lo[:,4])/nhe)),
       "log_T":float(np.max(last.log_temperature.hi-last.log_temperature.lo))}
    raw=loader.source_ledgers(m,model,last,t0,tm,t1,nh,nhe)
    require(set(raw)==set(worker.policy.EXPECTED_LEDGER_KEYS) and len(raw)==14,"ORIGINAL_14_LEDGER_KEYS")
    require(all(np.isfinite(a) and np.isfinite(b) and a<=0<=b for a,b in raw.values()),"ORIGINAL_14_LEDGER_ZERO")
    ev=worker.summarize_events(whole.table_events+steps["half1"].table_events+last.table_events)
    require(not ev["any_event"] and ev["node_count"]==0,"ORIGINAL_TABLE_EVENTS")
    audit=m.primitive.audit_set_ledgers({k:tuple(v) for k,v in raw.items()})
    require(audit.all_include_zero,"ORIGINAL_NATIVE_LEDGER_AUDIT")
    row={"public_widths":width,"set_ledgers":raw,
         "diagnostics":{"map_enclosed":True,"validated_local_error_bounds":new_defect,
                        "maximum_validated_local_error":max(new_defect.values())}}
    # The exact original owner post-map predicate, but V2-local correlated defect
    # and a DISJOINT versioned research receipt; no V1 accepted-history mutation.
    worker.policy._validate_post_map_metrics(row,"PASS","V2_TICK161_RESEARCH")
    require(max(width.values())<WIDTH and max(new_defect.values())<GATE,"FROZEN_PUBLIC_GATES")
    nextlo,nexthi=interval_material(hp.lo,hp.hi,last.log_temperature.lo,last.log_temperature.hi,nh,nhe)
    names=("Ne","B","U")
    pglobal={k:sum_interval(lo,hi) for k,lo,hi in zip(names,parent_mat_lo,parent_mat_hi)}
    nglobal={k:sum_interval(lo,hi) for k,lo,hi in zip(names,nextlo,nexthi)}
    delta={k:material_delta(pglobal[k],nglobal[k]) for k in names}
    midpoint={k:float(math.fsum(float(x) for x in (0.5*lo+0.5*hi)-(0.5*plo+0.5*phi)))
              for k,lo,hi,plo,phi in zip(names,nextlo,nexthi,parent_mat_lo,parent_mat_hi)}
    source_result=out_dir/"REI_TICK162_V2_RESEARCH_NONPRODUCTION.npz"
    with source_result.open("xb") as f:
        np.savez_compressed(f,population_lower=hp.lo,population_upper=hp.hi,
            log_temperature_lower=last.log_temperature.lo,log_temperature_upper=last.log_temperature.hi)
    require(source_result.read_bytes()[:8]!=b"REIADP1\0","NO_V1_STATE_FORMAT_SPOOFING")
    result.update(
        status="SOURCE_NATIVE_TICK161_ACTUALLY_CONSUMED_IN_NEXT_MAP",
        original_one_tick_physics_generated=True,
        original_14_ledgers_include_zero=True,
        original_14_ledgers=raw,
        source_candidate_state_tick162_sha256=sha(source_result),
        source_candidate_state_tick162_bytes=source_result.stat().st_size,
        original_local_defect_four_coordinates=old_defect,
        original_V2_common_parent_local_defect_four_coordinates=new_defect,
        original_width_four_coordinates=width,
        original_table_event_count=ev["node_count"],
        parent_tick161_chemothermal_global_interval=pglobal,
        next_tick162_chemothermal_global_interval=nglobal,
        source_conditional_delta_outer_intervals=delta,
        source_conditional_delta_midpoint=midpoint,
        source_mathematical_claim="CONDITIONAL_ORIGINAL_F05_DISCRETE_MAP_NOT_CONTINUUM_GLOBAL_ERROR",
        source_owner_decision="PROMOTE_FOR_RESEARCH_NEXT_PARENT_CONSUMPTION_ONLY",
        source_state_format="NPZ_RESEARCH_V2_NONPRODUCTION_NOT_V1_REIADP1")
    snapshot()
    print(json.dumps({"status":result["status"],"lane":lane,
        "parent_sha":sha(parent_file),"tick162_sha":sha(source_result),
        "v2_error":new_defect,"source_original_width":width,
        "source_14_ledger":"14/14_ZERO",
        "material_deltas":delta,"material_midpoint_deltas":midpoint,
        "canonical_delta":0},sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--repo",required=True,type=Path)
    a.add_argument("--source-tick161",required=True,type=Path)
    a.add_argument("--source-receipt",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    a.add_argument("--lane",required=True,choices=LANES)
    args=a.parse_args()
    execute(args.repo,args.source_tick161,args.source_receipt,args.output,args.lane)
