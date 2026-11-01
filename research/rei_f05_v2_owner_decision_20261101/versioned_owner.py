#!/usr/bin/env python3
"""Versioned source-owner decision for ONE authentic original REI F05 interval.

V1 worker/policy and accepted REIADP1 history are immutable.
This is a source-scoped V2 decision, never a canonical-history promotion.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

SOURCE="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
LOCK="90137341a1a37344be762e82e6603cd5c6bf4db00164ab0ba98809f0e9d9f381"
POLICY="c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
PARENT_HEAD="6574db945a1b96fa5e0b55923e36781b5db0b03b"
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR",
       "SCRIPT_SELF_SHIELDING_AUDITOR")
FIELDS=("x_HII","x_HeII","x_HeIII","log_T")
GATE=2e-4
WIDTH=2e-3
N=46080
REQUIRED_PKGS={"numpy":"2.3.5","pandas":"2.2.3","scipy":"1.17.0"}

def digest(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def load(name:str,path:Path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:
        raise ImportError(str(path))
    m=importlib.util.module_from_spec(s)
    sys.modules[name]=m
    s.loader.exec_module(m)
    return m

def must(c:bool,msg:str):
    if not c:
        raise ValueError("V2_FAIL_CLOSED:"+msg)

def version_gate(rec:dict,expected_lane:str,ledger_keys:set[str])->None:
    must(rec.get("lane")==expected_lane,"lane")
    must(rec.get("source_sha256")==SOURCE and rec.get("state_array_sha256")==STATE,"source")
    must(rec.get("kernel_sha256")==KERNEL,"kernel")
    must(rec.get("original_lock_sha256")==LOCK,"lock")
    must(rec.get("original_policy_sha256")==POLICY,"policy")
    must(rec.get("original_accepted_tick")=="160/131072","accepted_parent")
    must(rec.get("shadow_v2_candidate_tick")=="161/131072_NOT_OFFICIAL","candidate_tick")
    must(rec.get("original_worker_modified") is False,"worker_mutation")
    must(rec.get("official_tick161_accepted") is False,"illicit_admission")
    must(rec.get("original_legacy_worker_gate")=="FAIL_HISTORICAL_UNCHANGED","historic_v1")
    must(rec.get("original_policy_v2_post_map_validation")=="PASS_SHADOW_ONLY","native_policy")
    must(rec.get("original_14_ledger_pass") is True,"native_14_ledger")
    must(rec.get("original_table_event",{}).get("any_event") is False,"table_event")
    must(set(rec.get("native_step_receipts",{}))=={"full","half1","half2"},"three_native_steps")
    old=rec.get("old_independent_endpoint_local_upper",{})
    new=rec.get("new_original_common_parent_local_upper",{})
    widths=rec.get("original_public_widths",{})
    must(set(old)==set(FIELDS) and set(new)==set(FIELDS) and set(widths)==set(FIELDS),"coordinates")
    must(all(np.isfinite(float(old[k])) and float(old[k])>=0 for k in FIELDS),"historical_v1_finite")
    must(float(old["log_T"])>GATE,"historical_v1_not_failed")
    for name in FIELDS:
        must(np.isfinite(float(new[name])) and 0<=float(new[name])<GATE,"direct_defect_"+name)
        must(np.isfinite(float(widths[name])) and 0<=float(widths[name])<WIDTH,"public_width_"+name)
    ledgers=rec.get("original_native_raw_14_ledgers",{})
    must(set(ledgers)==ledger_keys,"exact_native_14_ledger_keys")
    for name,v in ledgers.items():
        must(isinstance(v,(list,tuple)) and len(v)==2,"ledger_shape_"+name)
        must(all(isinstance(q,(int,float)) and np.isfinite(q) for q in v),"ledger_finite_"+name)
        must(v[0]<=0<=v[1],"ledger_inclusion_"+name)
    clock=rec.get("clock_hex",{})
    must(set(clock)=={"t0","tm","t1","duration"},"original_clock_sites")
    duration=float.fromhex(clock["duration"])
    must(duration>0 and np.isfinite(duration),"duration")
    t0=duration*(160/131072);t1=duration*(161/131072);tm=t0+0.5*(t1-t0)
    must(clock["t0"]==t0.hex() and clock["tm"]==tm.hex()
         and clock["t1"]==t1.hex(),"source_clock_parity")

def read_candidate(path:Path,rec:dict,decoded):
    must(digest(path)==rec.get("candidate_state_sha256"),"candidate_sha")
    with np.load(path,allow_pickle=False) as z:
        keys={"population_lower","population_upper","log_temperature_lower",
              "log_temperature_upper","source_parent_population_lower",
              "source_parent_population_upper","source_parent_logT_lower",
              "source_parent_logT_upper"}
        must(set(z.files)==keys,"npz_schema")
        data={name:z[name] for name in keys}
    for name in keys:
        a=data[name]
        must(np.issubdtype(a.dtype,np.floating) and np.isfinite(a).all(),"dtype_finite_"+name)
        must(a.shape==(N,5) if "population" in name else a.shape==(N,),"shape_"+name)
    for name,p in (("source_parent_population_lower",decoded.population_lower),
                   ("source_parent_population_upper",decoded.population_upper),
                   ("source_parent_logT_lower",decoded.log_temperature_lower),
                   ("source_parent_logT_upper",decoded.log_temperature_upper)):
        must(np.array_equal(data[name],p),"accepted_tick160_parent_array_parity_"+name)
    must(np.all(data["population_lower"]<=data["population_upper"]),"physical_population_order")
    must(np.all(data["log_temperature_lower"]<=data["log_temperature_upper"]),"temperature_order")
    must(np.all(data["population_upper"]>0),"positive_population_upper")
    return data

def electron_science(data:dict)->dict:
    """Real source state-number response, not optical depth or continuum trajectory."""
    a=data["source_parent_population_lower"];b=data["source_parent_population_upper"]
    x=data["population_lower"];y=data["population_upper"]
    ne0lo=a[:,1]+a[:,3]+2*a[:,4]
    ne0hi=b[:,1]+b[:,3]+2*b[:,4]
    ne1lo=x[:,1]+x[:,3]+2*x[:,4]
    ne1hi=y[:,1]+y[:,3]+2*y[:,4]
    dlo=np.nextafter(ne1lo-ne0hi,-np.inf)
    dhi=np.nextafter(ne1hi-ne0lo,np.inf)
    must(np.isfinite(dlo).all() and np.isfinite(dhi).all(),"electron_response_finite")
    must(np.all(dlo<=dhi),"electron_response_order")
    return {"physics":"source_native_HHe_electron_inventory_not_tau",
            "cells":N,
            "delta_Ne_global_float64_interval":[float(np.sum(dlo)),float(np.sum(dhi))],
            "Ne_tick161_global_float64_interval":[float(np.sum(ne1lo)),float(np.sum(ne1hi))],
            "delta_Ne_positive_cells":int(np.count_nonzero(dlo>0)),
            "delta_Ne_negative_cells":int(np.count_nonzero(dhi<0)),
            "delta_Ne_uncertain_cells":int(np.count_nonzero((dlo<=0)&(dhi>=0))),
            "uncertainty":"inherited_native_float64_interval_not_formal_MPFR"}

INCREMENT_SHA="11df439390209bd48742ca9f4303c8743c9e14900289805e13d1ed489450a5dd"

def correlated_electron_science(increment_csv:Path,total_h,total_he)->dict:
    """True native original two-half H/He fraction increments on SAME parent.
    No independent end-state subtraction. Rounding remains float64-conditional.
    """
    must(digest(increment_csv)==INCREMENT_SHA,"native_increment_source_identity")
    nh=np.asarray(total_h,dtype=np.float64)
    he=np.asarray(total_he,dtype=np.float64)
    must(nh.shape==(N,) and he.shape==(N,) and np.all(nh>0)
         and np.all(he>0) and np.isfinite(nh).all()
         and np.isfinite(he).all(),"nuclei_inventory")
    lows=np.empty(N,dtype=np.float64)
    highs=np.empty(N,dtype=np.float64)
    fields=tuple(f"x_{s}_original_twohalf_increment_{side}"
                 for s in ("HII","HeII","HeIII") for side in ("lower","upper"))
    with gzip.open(increment_csv,"rt",newline="") as f:
        reader=csv.DictReader(f)
        must(reader.fieldnames is not None and len(reader.fieldnames)==30
             and set(fields).issubset(reader.fieldnames),"original_increment_30_columns")
        count=0
        for row in reader:
            must(count<N and int(row["node"])==count,"native_node_order")
            x=[float(row[k]) for k in fields]
            must(all(np.isfinite(z) for z in x),"native_increment_finite")
            must(x[0]<=x[1] and x[2]<=x[3] and x[4]<=x[5],"native_increment_order")
            lows[count]=nh[count]*x[0]+he[count]*(x[2]+2*x[4])
            highs[count]=nh[count]*x[1]+he[count]*(x[3]+2*x[5])
            count+=1
    must(count==N and np.all(lows<=highs),"original_rows")
    # Local float64 outward nudge. This is NOT an MPFR or rigorous global sum.
    lows=np.nextafter(lows,-np.inf)
    highs=np.nextafter(highs,np.inf)
    result={
      "physics":"original_correlated_native_twohalf_delta_electron_number_not_tau",
      "source_increment_sha256":INCREMENT_SHA,
      "nodes":N,
      "global_delta_Ne_conditional_float64_interval":[float(np.sum(lows)),float(np.sum(highs))],
      "positive_cells":int(np.count_nonzero(lows>0)),
      "negative_cells":int(np.count_nonzero(highs<0)),
      "uncertain_cells":int(np.count_nonzero((lows<=0)&(highs>=0))),
      "source_approximation":"original_shared_parent_26event_4photon_group_OTS_MPRK22_SDIRK2",
      "arithmetic_scope":"inherited_float64_not_end_to_end_formal_outward"
    }
    return result

def versioned_owner(repo:Path,shadow:Path,out:Path,*,increment:Path|None=None,allow_unpinned:bool=False)->dict:
    repo=repo.resolve();shadow=shadow.resolve();out=out.resolve()
    must(not out.exists(),"immutable_output_exists")
    versions={n:importlib.metadata.version(n) for n in REQUIRED_PKGS}
    pinned=all(versions[n]==v for n,v in REQUIRED_PKGS.items())
    must(pinned or allow_unpinned,"pinned_science_runtime_required")
    code_root=repo/"research/rei_f05_owner_v2_shadow_20261101"
    original=load("rei_v2_original_edge_for_owner",repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    stage=repo/original.REL_STAGE
    worker=load("rei_v2_original_attempt_for_owner",stage/"analysis/attempt_worker.py")
    must(digest(stage/"local_results"/original.ARCHIVE_NAME)==SOURCE,"actual_original_archive")
    must(digest(worker.KERNEL_PATH)==KERNEL,"original_kernel_bytes")
    must(digest(stage/"INPUT_LOCK.json")==LOCK,"original_input_lock_bytes")
    must(digest(stage/"analysis/adaptive_policy.py")==POLICY,"original_worker_policy_bytes")
    policy=worker.policy
    allrows={}
    first=None
    first_clock=None
    candidate_sha=None
    archive_lanes={LANES[0]:"primary",LANES[1]:"recomb",LANES[2]:"shield"}
    for lane in LANES:
        lp=shadow/archive_lanes[lane]
        rec=json.loads((lp/"V2_RECEIPT.json").read_text())
        version_gate(rec,lane,set(policy.EXPECTED_LEDGER_KEYS))
        decoded,src=original.source_state(stage,lane,worker.state_io)
        must(src["archive_sha256"]==SOURCE and src["accepted_array_sha256"]==STATE,"loaded_original_state")
        must(decoded.metadata["endpoint_tick"]==160 and decoded.metadata["accepted_index"]==3,"parent_metadata")
        state=read_candidate(lp/"SHADOW_V2_NONAUTHORITATIVE_TICK161.npz",rec,decoded)
        if first is None:
            first={k:v.copy() for k,v in state.items()}
            first_clock=rec["clock_hex"]
            candidate_sha=rec["candidate_state_sha256"]
        else:
            must(first_clock==rec["clock_hex"],"shared_physical_clock")
            must(candidate_sha==rec["candidate_state_sha256"],"same_source_lane_binary")
            must(all(np.array_equal(state[k],first[k]) for k in first),"shape_lanes_same_dataset")
        allrows[lane]={"source_candidate_sha256":rec["candidate_state_sha256"],
                       "old_v1_logT_upper":rec["old_independent_endpoint_local_upper"]["log_T"],
                       "v2_logT_upper":rec["new_original_common_parent_local_upper"]["log_T"],
                       "original_14_ledger":"14/14_ZERO_INCLUDED",
                       "original_table_events":0,
                       "source_original_parent_parity":"EXACT_ARRAYS"}
    ele=electron_science(first)
    correlated={"status":"NOT_RUN_NO_ORIGINAL_INCREMENT_SOURCE"}
    if increment is not None:
        worker.jax_guard.install_if_missing()
        base,y,logt,nh,nhe=worker._context(worker._kernel(),LANES[0])
        correlated=correlated_electron_science(Path(increment),nh,nhe)
        direct=correlated["global_delta_Ne_conditional_float64_interval"]
        broad=ele["delta_Ne_global_float64_interval"]
        must(broad[0]<=direct[0] and direct[1]<=broad[1],
             "original_discrete_increment_must_lie_in_endpoint_difference_enclosure")
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=repo,capture_output=True,
                        text=True,check=True).stdout.strip()
    must(len(head)==40,"git_head")
    receipt={"schema":"REI_IGM_F05_VERSIONED_V2_SOURCE_OWNER_DECISION_20261101",
             "status":"V2_SOURCE_SCOPED_CHECK_PASS_NO_OFFICIAL_ADMISSION" if pinned else
                      "UNPINNED_EXPLORATORY_ONLY",
             "repository_head":head,"source_parent_pr354_head":PARENT_HEAD,
             "original_accepted_tick":"160/131072",
             "v2_source_candidate_tick":"161/131072",
             "canonical_tick161_admitted":False,
             "original_worker_modified":False,"original_V1_failure_preserved":True,
             "source_sha256":SOURCE,"original_state_sha256":STATE,
             "original_kernel_sha256":KERNEL,"original_policy_sha256":POLICY,
             "runtime_versions":versions,"pinned_runtime":pinned,
             "physical_datasets":1,"shape_lanes":allrows,
             "first_0_to_64_exact_replay":"NOT_RUN",
             "continuous_IVP_LTE":"NOT_PROVEN",
             "full_outward_rounding":"NOT_PROVEN",
             "same_author_referee_only":True,
             "central_DAG":"28/88_REPORTED","working_DAG":"33/88_REPORTED",
             "physical_fast_DAG":"4/7_REPORTED","canonical_delta":0,
             "production":"HOLD","auto_tick162":False,
             "electron_physics":ele,
             "original_correlated_increment_physics":correlated}
    out.mkdir(parents=True)
    (out/"VERSIONED_SOURCE_OWNER_DECISION.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":receipt["status"],"canonical_delta":0,
                      "electron_science":ele},sort_keys=True),flush=True)
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True,type=Path)
    ap.add_argument("--shadow",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--increment",type=Path)
    ap.add_argument("--allow-unpinned",action="store_true")
    a=ap.parse_args()
    versioned_owner(a.repo,a.shadow,a.out,increment=a.increment,allow_unpinned=a.allow_unpinned)
