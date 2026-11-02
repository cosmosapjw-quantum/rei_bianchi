#!/usr/bin/env python3
"""Actual new standalone source-scoped V2 research worker for 3 original F05 lanes.

Invokes genuine immutable PR354 full/half/half native MPRK22 + Alexander-SDIRK2
with existing PR350 M-matrix common-parent increments, then independently binds
new REI_V2SC1 physical state to original 0->64->128->160 historical REIADP1 and
the running scientific environment. NOT an official V1/131072-tick history.
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, json, os, pathlib, platform
import struct, subprocess, sys
from pathlib import Path
import numpy as np
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR","SCRIPT_SELF_SHIELDING_AUDITOR")
SLUGS=("primary","recomb","shield")
STATE_SHA={
 "LOCAL_NEUTRAL_HAZARD_PRIMARY":{
 64:"aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425",
 128:"bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6",
 160:"74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6"},
 "RECOMBINATION_WEIGHTED_AUDITOR":{
 64:"b9b1c383a3b697770528481f9cfa35989c61e17609c0100ef27b8c8cda337d9d",
 128:"030ab8e767b2d81bd20ec548e1ce1be23fdeaa79ceaaade091f9da4105e5febe",
 160:"a93c9a5f3cf95521322dc033d14a24a0ed8d4ed44a823ccb39720b0434c73b0a"},
 "SCRIPT_SELF_SHIELDING_AUDITOR":{
 64:"31a763fdca76eb4d0b3fb03276342733dd1618bc2c7df22c3b00ba80691604fa",
 128:"da02bd8000280383a520ac8284d943b6e638b0500b4d58cf9dafd2f17caf9df5",
 160:"3aaff7b8cc4be8664c2d81d617d205f85f6ff974b62460a69e3839760c2fcf9c"}
}
SOURCE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
POLICY_SHA="c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
ACCEPTED_PARENT_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
EXPECTED={"numpy":"2.3.5","pandas":"2.2.3","scipy":"1.17.0"}
FIELDS=("x_HII","x_HeII","x_HeIII","log_T")
MAGIC=b"REIV2SC1\0"
FORMAT="REI_V2SC1_SOURCE_SCOPED_RESEARCH_NOT_REIADP1"
VERSION="REI_F05_V2_DISCRETE_COMMON_PARENT_WORKER_EXPERIMENT_V1"
EV=1.602176634e-12;KB=1.380649e-16
CHI=(13.598434599702,24.587389011,54.41776)
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(4<<20),b""):h.update(b)
 return h.hexdigest()
def require(ok,msg):
 if not ok:raise ValueError("REI_V2_WORKER_FAIL_CLOSED_"+msg)
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False,ensure_ascii=True).encode("ascii")
def state_body(file,tick,lane,stage_id,lock):
 p=Path(file); require(p.is_file() and sha(p)==STATE_SHA[lane][tick],"HISTORICAL_STATE_SHA_"+lane+"_"+str(tick))
 with p.open("rb") as f:
  magic=f.read(8)
  require(magic==b"REIADP1\0","ORIGINAL_STATE_FORMAT")
  count=struct.unpack("<Q",f.read(8))[0]
  require(100<count<2**20,"HEADER_LENGTH")
  header=json.loads(f.read(count))
  raw=f.read()
 require(header["metadata"]["endpoint_tick"]==tick,"PARENT_TICK")
 require(header["metadata"]["lane"]==lane,"PARENT_LANE")
 require(header["metadata"]["accepted_index"]=={64:1,128:2,160:3}[tick],"PARENT_ACCEPTED_INDEX")
 require(header["metadata"]["stage_id"]==stage_id,"PARENT_STAGE_ID")
 require(header["metadata"]["input_lock_sha256"]==lock,"PARENT_INPUT_LOCK")
 require(header["metadata"]["predecessor_kernel_sha256"]==KERNEL_SHA,"PARENT_KERNEL")
 require(header["population_shape"]==[46080,5] and header["log_temperature_shape"]==[46080],"SOURCE_SHAPE")
 require(len(raw)==4423680,"ORIGINAL_REAL_SOURCE_PAYLOAD_LENGTH")
 return header["metadata"],hashlib.sha256(raw).hexdigest()
def original_history(args,repo):
 stage=next(repo.glob("stages/*UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY"))
 f=stage/"local_results/first_interval_r2_blocked_minimum_step.tar.gz"
 policy=stage/"analysis/adaptive_policy.py"
 kernel=next(repo.glob("stages/*CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK/analysis/interval_discrete_map.py"))
 lock=sha(stage/"INPUT_LOCK.json")
 require(sha(f)==SOURCE_SHA and sha(policy)==POLICY_SHA and sha(kernel)==KERNEL_SHA,"IMMUTABLE_SOURCE_KERNEL_POLICY")
 # Source-free original historical runtime state metadata binds worker's original stage policy.
 import importlib.util
 s=importlib.util.spec_from_file_location("versioned_v2_old_policy",policy)
 v=importlib.util.module_from_spec(s);sys.modules[s.name]=v;s.loader.exec_module(v)
 file_map={
  LANES[0]:{64:Path(args.p64),128:Path(args.p128),160:Path(args.p160)},
  LANES[1]:{64:Path(args.r64),128:Path(args.r128),160:Path(args.r160)},
  LANES[2]:{64:Path(args.s64),128:Path(args.s128),160:Path(args.s160)}}
 lineage={}
 for lane in LANES:
  lineage[lane]={}
  previous="INITIAL"
  for tick in (64,128,160):
   meta,body_sha=state_body(file_map[lane][tick],tick,lane,v.STAGE_ID,lock)
   require(meta["parent_state_sha256"]==previous,"ORIGINAL_CHAIN_"+lane+"_"+str(tick))
   previous=STATE_SHA[lane][tick]
   lineage[lane][str(tick)]={"full_state_sha256":previous,"physical_payload_sha256":body_sha,"job_key":meta["job_key"],"runtime_contract_sha256":meta["runtime_contract_sha256"]}
 for tick in ("64","128","160"):
  hashes={lineage[l][tick]["physical_payload_sha256"] for l in LANES}
  require(len(hashes)==1,"LANES_PHYSICAL_BODY_DIFFER")
 return stage,lock,lineage
def fresh_runtime(repo,stage,locked,code_commit):
 require(subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip()==code_commit,"CODE_COMMIT_HEAD")
 require(not subprocess.check_output(["git","-C",str(repo),"status","--porcelain","--untracked-files=no"],text=True).strip(),"TRACKED_SOURCE_DIRTY")
 actual={key:importlib.metadata.version(key) for key in EXPECTED}
 require(actual==EXPECTED,"NUMERIC_DEPENDENCIES_NOT_PINNED")
 sys_path={k:__import__(k).__file__ for k in EXPECTED}
 import numpy as np
 worker=Path(__file__).resolve()
 return {"schema":"REI_F05_VERSIONED_V2_SOURCE_RUNTIME_V1","worker_version":VERSION,"code_git_head":code_commit,
         "code_file_sha256":sha(worker),
         "original_worker_file_sha256":sha(stage/"analysis/attempt_worker.py"),
         "original_runtime_contract_file_sha256":sha(stage/"analysis/runtime_contract.py"),
         "original_policy_sha256":POLICY_SHA,"original_kernel_sha256":KERNEL_SHA,
         "original_source_sha256":SOURCE_SHA,"original_input_lock_sha256":locked,
         "python_implementation":platform.python_implementation(),
         "python_version":platform.python_version(),
         "os_system":platform.system(),"machine":platform.machine(),
         "dependencies":actual,"dependency_file_locations":sys_path,
         "threads":{k:os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS")},
         "numpy_dtype":"float64_little_endian",
         "original_V1_acceptance_policy":"UNCHANGED_FAILURE_2.1245050576368385e-4",
         "official_acceptance":False}
def write_versioned(path,metadata,npz):
 keys=("population_lower","population_upper","log_temperature_lower","log_temperature_upper")
 arrs=[]
 for key in keys:
  a=np.asarray(npz[key],dtype="<f8")
  require(a.shape==((46080,5) if "population" in key else (46080,)) and np.isfinite(a).all(),"V2_STATE_SHAPE_FINITE")
  arrs.append(np.ascontiguousarray(a).tobytes(order="C"))
 header={"format":FORMAT,"worker_version":VERSION,"fields":list(keys),"metadata":metadata,
         "cells":46080,"dtype":"<f8","array_bytes":[len(x) for x in arrs],
         "source_not_official":True}
 raw=canonical(header);body=b"".join(arrs)
 with path.open("xb") as f:
  f.write(MAGIC+struct.pack("<Q",len(raw))+raw+body)
 return hashlib.sha256(body).hexdigest(),sha(path)
def physical_npz(z):
 for k in z.files:require(np.isfinite(z[k]).all(),"NONFINITE_V2_"+k)
 p0l,p0h=z["source_parent_population_lower"],z["source_parent_population_upper"]
 plo,phi=z["population_lower"],z["population_upper"]
 l0,u0=z["source_parent_logT_lower"],z["source_parent_logT_upper"]
 l1,u1=z["log_temperature_lower"],z["log_temperature_upper"]
 def bound(p):
  ne_lo=p[0][:,1]+p[0][:,3]+2*p[0][:,4]
  ne_hi=p[1][:,1]+p[1][:,3]+2*p[1][:,4]
  N_H=p0l[:,0]+p0l[:,1]
  N_He=p0l[:,2]+p0l[:,3]+p0l[:,4]
  b_lo=EV*(CHI[0]*p[0][:,1]+CHI[1]*(p[0][:,3]+p[0][:,4])+CHI[2]*p[0][:,4])
  b_hi=EV*(CHI[0]*p[1][:,1]+CHI[1]*(p[1][:,3]+p[1][:,4])+CHI[2]*p[1][:,4])
  return (ne_lo,ne_hi,b_lo,b_hi,N_H,N_He)
 old=bound((p0l,p0h));new=bound((plo,phi))
 nH=old[4];nHe=old[5]
 U0l=1.5*KB*(nH+nHe+old[0])*np.exp(l0)
 U0h=1.5*KB*(nH+nHe+old[1])*np.exp(u0)
 U1l=1.5*KB*(nH+nHe+new[0])*np.exp(l1)
 U1h=1.5*KB*(nH+nHe+new[1])*np.exp(u1)
 return {"delta_Ne":[float(np.sum(new[0]-old[1])),float(np.sum(new[1]-old[0]))],
         "delta_B_erg":[float(np.sum(new[2]-old[3])),float(np.sum(new[3]-old[2]))],
         "delta_U_gas_erg":[float(np.sum(U1l-U0h)),float(np.sum(U1h-U0l))],
         "midpoint_delta_Ne":float(np.sum((new[0]+new[1]-old[0]-old[1])*0.5)),
         "midpoint_delta_B_erg":float(np.sum((new[2]+new[3]-old[2]-old[3])*0.5)),
         "midpoint_delta_U_gas_erg":float(np.sum((U1l+U1h-U0l-U0h)*0.5)),
         "physical_computation":"ORIGINAL_INTERVAL_CONDITIONAL_F64_NOT_PROOF_OF_DIRECTED_ROUNDING"}
def run(args):
 repo=Path(args.repo).resolve()
 private=Path(args.private).resolve()
 public=Path(args.public).resolve()
 require(not private.exists() and not public.exists(),"DO_NOT_REPLACE_EXISTING_STATE")
 stage,lock,lineage=original_history(args,repo)
 runtime=fresh_runtime(repo,stage,lock,args.code_head)
 runtime_sha=hashlib.sha256(canonical(runtime)).hexdigest()
 private.mkdir(parents=True);public.mkdir(parents=True)
 source_code=repo/"research/rei_f05_owner_v2_shadow_20261101/owner_v2_shadow.py"
 require(source_code.is_file(),"ORIGINAL_V2_ADAPTER_SOURCE_MISSING")
 receipts={}
 bodies=[]
 actual_sources=[]
 for lane,slug in zip(LANES,SLUGS):
  out=private/slug
  env=os.environ.copy()
  for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
   env[k]="1"
  env.pop("PYTHONNOUSERSITE",None)
  cmd=[sys.executable,str(source_code),"--repo",str(repo),"--lane",lane,"--out",str(out)]
  proc=subprocess.run(cmd,env=env,capture_output=True,text=True,check=False)
  (private/(slug+"_native.stdout.log")).write_text(proc.stdout)
  (private/(slug+"_native.stderr.log")).write_text(proc.stderr)
  require(proc.returncode==0,"NATIVE_ORIGINAL_V2_MAP_"+slug+"_EXIT_"+str(proc.returncode))
  receipt=json.loads((out/"V2_RECEIPT.json").read_text())
  require(receipt["lane"]==lane and receipt["source_sha256"]==SOURCE_SHA,"NATIVE_RECEIPT_SOURCE_"+slug)
  require(receipt["state_array_sha256"]==ACCEPTED_PARENT_SHA,"NATIVE_ACCEPTED_PARENT_"+slug)
  require(receipt["original_legacy_worker_gate"]=="FAIL_HISTORICAL_UNCHANGED" and receipt["old_independent_endpoint_local_upper"]["log_T"]>2e-4,"V1_FAILURE_MUST_SURVIVE_"+slug)
  require(receipt["original_policy_v2_post_map_validation"]=="PASS_SHADOW_ONLY" and receipt["official_tick161_accepted"] is False,"V2_SCOPE_"+slug)
  require(len(receipt["original_native_raw_14_ledgers"])==14 and receipt["original_14_ledger_pass"] and not receipt["original_table_event"]["any_event"],"ORIGINAL_LEDGERS_"+slug)
  require(all(v<2e-4 for v in receipt["new_original_common_parent_local_upper"].values()),"SOURCE_FIXED_V2_ERROR_GATE_"+slug)
  require(all(v<0.002 for v in receipt["original_public_widths"].values()),"SOURCE_FIXED_V2_WIDTH_GATE_"+slug)
  require(len(receipt["native_step_receipts"])==3 and set(receipt["native_step_receipts"])=={"full","half1","half2"},"SOURCE_NATIVE_THREE_MAPS_"+slug)
  require(receipt["original_lock_sha256"]==lock and receipt["original_policy_sha256"]==POLICY_SHA,"SOURCE_NATIVE_LOCK_"+slug)
  expected_meta=lineage[lane]["160"]
  require(receipt["actual_parent_state_member_sha256"]==expected_meta["full_state_sha256"],"ORIGINAL_LANE_T160_RECEIPT_"+slug)
  for k,v in receipt["original_native_raw_14_ledgers"].items():
   require(len(v)==2 and v[0]<=0<=v[1],"ORIGINAL_SOURCE_LEDGER_ZERO_"+slug+"_"+k)
  previous={t:lineage[lane][str(t)]["full_state_sha256"] for t in (64,128,160)}
  job={"schema":"REI_F05_RESEARCH_V2_JOB_V1","version":VERSION,
       "lane":lane,"accepted_index":4,"interval":[160,161],"depth":6,
       "original_history_state_sha256":previous,
       "accepted_parent_state_sha256":previous[160],
       "original_V1_runtime_contract_sha256":expected_meta["runtime_contract_sha256"],
       "new_v2_runtime_sha256":runtime_sha,
       "source_tar_sha256":SOURCE_SHA,"source_kernel_sha256":KERNEL_SHA,
       "original_input_lock_sha256":lock,
       "source_V1_error_failure":"V1_LOGT_2.1245050576368385e-4_GT_GATE_2e-4",
       "official_tick161":False}
  job_sha=hashlib.sha256(canonical(job)).hexdigest()
  with np.load(out/"SHADOW_V2_NONAUTHORITATIVE_TICK161.npz",allow_pickle=False) as z:
   physics=physical_npz(z)
   body_sha,versioned_sha=write_versioned(out/"VERSIONED_RESEARCH_V2_SOURCE_TICK161.state",
       {"job_key":job_sha,"job":job,"V2_discrete_bounds":receipt["new_original_common_parent_local_upper"],
        "source_V1_old_endpoint_bounds":receipt["old_independent_endpoint_local_upper"],
        "14_original_ledgers":receipt["original_native_raw_14_ledgers"],
        "clock_hex":receipt["clock_hex"],
        "source_only_admission":True,"official":False},z)
  bodies.append(body_sha)
  actual_sources.append(receipt["candidate_state_sha256"])
  receipts[lane]={"job_key":job_sha,"job":job,"source_shadows_sha256":receipt["candidate_state_sha256"],
      "versioned_state_sha256":versioned_sha,"state_body_sha256":body_sha,
      "V1_old_logT_upper":receipt["old_independent_endpoint_local_upper"]["log_T"],
      "V2_source_logT_upper":receipt["new_original_common_parent_local_upper"]["log_T"],
      "V2_public_max_width":max(receipt["original_public_widths"].values()),
      "native_full_half_map_count":len(receipt["native_step_receipts"]),
      "source_native_14_ledgers":14,"source_table_events":receipt["original_table_event"]["node_count"],
      "physical_response":physics}
  print(json.dumps({"lane":lane,"V2_worker":"SOURCE_SCOPED_PASS",
      "old_V1_logT":receipts[lane]["V1_old_logT_upper"],
      "V2_logT":receipts[lane]["V2_source_logT_upper"],
      "midpoint_delta_B":physics["midpoint_delta_B_erg"],
      "BODYSHA":body_sha}),flush=True)
 require(len(set(bodies))==1,"V2_LANES_NUMERICAL_BODY_DIFFER")
 require(len(set(actual_sources))==1,"V2_SOURCE_NPZ_DIFFER")
 require(len({receipts[l]["job_key"] for l in LANES})==3,"JOB_KEYS_NOT_DISTINCT")
 result={"schema":"REI_F05_NEW_SOURCE_ONLY_VERSIONED_V2_RESEARCH_WORKER_V1",
   "original_parent_pr":366,"original_parent_head":"a09ea7b999c90a692de07c74352f835707e65838",
   "worker_version":VERSION,"worker_source_git_head":args.code_head,
   "new_runtime_contract_sha256":runtime_sha,"runtime":runtime,
   "original_source_history":lineage,
   "original_accepted_tick":"160/131072","original_research_candidate_tick":"161/131072_NOT_OFFICIAL",
   "physical_lanes":receipts,"number_of_original_physical_realizations":1,
   "three_lane_new_v2_numerical_body_sha256":bodies[0],
   "original_native_map_evaluations":9,
   "old_V1_error_gate":"FAIL_UNCHANGED","new_V2_fixed_threshold":"PASS_SOURCE_DISCRETE_ONLY",
   "owner_decision":"PROMOTE_FOR_SPECIFIED_USE_NEW_VERSIONED_V2_EXPERIMENTAL_WORKER_NOT_ACCEPTED_ORIGINAL_PRODUCTION",
   "official_accepted_161":False,"automatic_next_162":False,"production":"HOLD",
   "scientific_limit":"NO_CONTINUUM_LOCAL_OR_GLOBAL_ERROR_CERTIFICATE",
   "original_state_format_preserved":"REIADP1_OLD_UNCHANGED",
   "new_state_format":FORMAT,"original_worker_modified":False,
   "DAG":{"central":"28/88","working":"33/88_NONADDITIVE","physical_fast":"4/7","canonical_delta":0}}
 (public/"VERSIONED_V2_SOURCE_WORKER_RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"owner":"REI_F05","new_original_source_v2_worker":"PASS_SCOPED",
    "three_lanes":3,"runtime_SHA256":runtime_sha,"source_data_body_SHA256":bodies[0],
    "actual_full_half_runs":9,"official_tick161":"HOLD","DAG":"28/88"}),flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for key in ("repo","code_head","p64","p128","p160","r64","r128","r160","s64","s128","s160","private","public"):
  p.add_argument("--"+key.replace("_","-"),dest=key,required=True)
 run(p.parse_args())
