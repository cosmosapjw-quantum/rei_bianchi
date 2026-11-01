#!/usr/bin/env python3
"""Independent stdlib/NumPy audit of all three source-owned F05 V2 shadow lanes.
Crosschecks real prior PR352 H/He population/T fields, no official state output.
"""
from __future__ import annotations
import argparse,hashlib,json,math,zipfile
from pathlib import Path
import numpy as np

LANES=("primary","recomb","shield")
NAMES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR",
       "SCRIPT_SELF_SHIELDING_AUDITOR")
FIELDS=("x_HII","x_HeII","x_HeIII","log_T")
SHA_SRC="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SHA_ARRAY="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
SHA_KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def audit(root,previous):
    root=Path(root).resolve()
    previous=Path(previous).resolve()
    summaries=[]
    for folder,lane in zip(LANES,NAMES):
        p=root/folder
        j=json.loads((p/"V2_RECEIPT.json").read_text())
        if j["lane"]!=lane or j["candidate_original_science"]!="SCOPED_V2_NATIVE_HHE_TICK161_PASS":
            raise ValueError("V2_SOURCE_LANE_OR_STATUS_MISMATCH")
        if not (j["source_sha256"]==SHA_SRC and j["state_array_sha256"]==SHA_ARRAY and j["kernel_sha256"]==SHA_KERNEL):
            raise ValueError("V2_SOURCE_IDENTITY_MISMATCH")
        if j["central_DAG"]!="28/88_REPORTED" or j["canonical_delta"]!=0 or j["production"]!="HOLD":
            raise ValueError("V2_FALSE_CANONICAL_ADMISSION")
        if j["official_tick161_accepted"] is not False or j["original_worker_modified"] is not False:
            raise ValueError("V2_FALSE_SOURCE_OWNER_ADMISSION")
        if j["original_policy_v2_post_map_validation"]!="PASS_SHADOW_ONLY":
            raise ValueError("MISSING_ORIGINAL_POLICY_SHADOW_TEST")
        if j["original_legacy_worker_gate"]!="FAIL_HISTORICAL_UNCHANGED":
            raise ValueError("ORIGINAL_FAIL_ERASURE")
        old,new,widths=j["old_independent_endpoint_local_upper"],j["new_original_common_parent_local_upper"],j["original_public_widths"]
        assert set(old)==set(new)==set(widths)==set(FIELDS)
        if not (old["log_T"]>2e-4 and all(x<2e-4 for x in new.values()) and all(x<2e-3 for x in widths.values())):
            raise ValueError("LOCAL_SOURCE_GATE_MISMATCH")
        if not j["original_14_ledger_pass"] or j["original_table_event"]["any_event"]:
            raise ValueError("SOURCE_LEDGER_OR_TABLE_EVENT")
        ledgers=j["original_native_raw_14_ledgers"]
        if len(ledgers)!=14 or not all(len(v)==2 and v[0]<=0<=v[1] for v in ledgers.values()):
            raise ValueError("RAW_SOURCE_LEDGER_OR_CARDINALITY")
        if set(j["native_step_receipts"])!={"full","half1","half2"}:
            raise ValueError("NATIVE_STEP_COUNT")
        for s in j["native_step_receipts"].values():
            if s["status"]!="PASS" or not s["native_certified"] or s["original_table_event_count"]!=0:
                raise ValueError("ORIGINAL_NATIVE_STEP_FAILED")
            if s["original_population_solves"]!=3 or s["original_root_calls"]<3:
                raise ValueError("WRONG_ORIGINAL_26EVENT_STEP_SEQUENCE")
        f=p/j["candidate_state_file"]
        if sha(f)!=j["candidate_state_sha256"]:raise ValueError("CANDIDATE_SHA_MISMATCH")
        if f.read_bytes()[:8]==b"REIADP1\x00":raise ValueError("ORIGINAL_ACCEPTED_STATE_FORMAT_FORBIDDEN")
        with zipfile.ZipFile(f) as z:
            if z.testzip() is not None:raise ValueError("STATE_NPZ_CRC_FAILURE")
        ref=previous/folder/"PREVIEW_NONAUTHORITATIVE_TICK161.npz"
        if not ref.is_file():raise FileNotFoundError(ref)
        d=np.load(f,allow_pickle=False)
        prior=np.load(ref,allow_pickle=False)
        mapping={
            "population_lower":"population_lower",
            "population_upper":"population_upper",
            "log_temperature_lower":"log_temperature_lower",
            "log_temperature_upper":"log_temperature_upper"}
        max_rel=0.0
        for a,b in mapping.items():
            x,y=d[a],prior[b]
            if x.shape!=y.shape or not np.isfinite(x).all() or not np.isfinite(y).all():
                raise ValueError("V2_PHYSICAL_STATE_NONFINITE_OR_SHAPE")
            rel=float(np.max(np.abs(x-y)/np.maximum(np.maximum(np.abs(x),np.abs(y)),1e-300)))
            max_rel=max(max_rel,rel)
            if rel>2e-12:raise ValueError("V2_PHYSICAL_STATE_NOT_EQUIVALENT_TO_PR352")
        if d["population_lower"].shape!=(46080,5) or d["log_temperature_lower"].shape!=(46080,):
            raise ValueError("V2_PHYSICAL_NODE_COUNT")
        if np.any(d["population_lower"]<=0):
            raise ValueError("V2_PHYSICAL_NEGATIVE_POPULATION")
        summaries.append({
          "shape_lane":lane,"physical_nodes":46080,"state_sha256":sha(f),
          "max_rel_to_original_pr352":max_rel,"new_logT_upper":new["log_T"],
          "old_logT_upper":old["log_T"],"original_14_ledger":"PASS",
          "native_steps":"FULL_HALF1_HALF2_PASS","v2_scoped_only":True})
    # Shape lanes represent one source physics dataset, even if independent
    # auditor computations carry separately serialized ledger sidecars.
    if len(set(s["state_sha256"] for s in summaries))!=1:
        raise ValueError("LOCAL_SOURCE_SHAPE_STATE_BYTE_DIVERGENCE")
    return {"status":"PASS_SOURCE_NATIVE_V2_SHADOW_ONLY",
        "source_datasets":1,"physical_nodes":46080,"shape_lanes":summaries,
        "central_DAG":"28/88_REPORTED","canonical_delta":0,
        "official_accepted_tick":"160/131072","v2_candidate_tick":"161/131072",
        "original_authoritative_owner_admission":"NOT_RUN","production":"HOLD",
        "cross_runtime_full_formal_rounding":"NOT_PROVEN"}

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--root",type=Path,required=True)
    a.add_argument("--pr352",type=Path,required=True)
    v=a.parse_args()
    result=audit(v.root,v.pr352)
    (v.root/"V2_INDEPENDENT_AUDIT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True),flush=True)