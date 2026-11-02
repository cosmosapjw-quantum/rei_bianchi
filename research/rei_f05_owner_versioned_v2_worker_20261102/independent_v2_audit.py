#!/usr/bin/env python3
"""Source-disjoint stdlib V2 audit: independently decode actual REIV2SC1 & REIADP1,
check original 3 historical shape lanes, full/half ledger and source-real 46k physics.
Not an independent author's referee; does not call original solver or new worker.
"""
from __future__ import annotations
import argparse,array,hashlib,json,math,struct,sys
from pathlib import Path
EXPECTED_SOURCE="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
EXPECTED_KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
EXPECTED_POLICY="c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
EXPECTED_PARENT="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
N=46080
KB=1.380649e-16
EV=1.602176634e-12
CHI=(13.598434599702,24.587389011,54.41776)
SLUG={"LOCAL_NEUTRAL_HAZARD_PRIMARY":"primary",
      "RECOMBINATION_WEIGHTED_AUDITOR":"recomb",
      "SCRIPT_SELF_SHIELDING_AUDITOR":"shield"}
def need(ok,where):
 if not ok:raise RuntimeError("REI_V2_INDEPENDENT_FAIL_CLOSED_"+where)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(4<<20),b""):h.update(b)
 return h.hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False,ensure_ascii=True).encode("ascii")
def read_packed(path,magic):
 p=Path(path)
 with p.open("rb") as f:
  expected=f.read(len(magic));need(expected==magic,"INVALID_STATE_MAGIC")
  hsize=struct.unpack("<Q",f.read(8))[0]
  need(16<hsize<1<<20,"INVALID_HEADER_SIZE")
  header=json.loads(f.read(hsize))
  body=f.read()
 need(len(body)==4423680,"ORIGINAL_STATE_ARRAY_LAYOUT")
 return header,body
def decode_body(body):
 need(sys.byteorder=="little","ENDIAN_NOT_ORIGINAL")
 off=0;out=[]
 for n in (N*5,N*5,N,N):
  raw=body[off:off+8*n];off+=8*n
  a=array.array("d");a.frombytes(raw);need(len(a)==n,"FLOAT_COUNT")
  out.append(a)
 need(off==len(body),"V2_RAW_TRAILING_BYTES")
 return out
def close(a,b,rtol=4e-11):
 return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=rtol*max(abs(a),abs(b),1e-300)
def independent_thermophysical(parent,child):
 p0,p1,lt0,lt1=decode_body(parent)
 c0,c1,cl0,cl1=decode_body(child)
 sums=[[],[],[],[],[],[],[],[],[]]
 for j in range(N):
  k=j*5
  NH=p0[k]+p0[k+1];NHe=p0[k+2]+p0[k+3]+p0[k+4]
  neo_lo=p0[k+1]+p0[k+3]+2*p0[k+4];neo_hi=p1[k+1]+p1[k+3]+2*p1[k+4]
  nen_lo=c0[k+1]+c0[k+3]+2*c0[k+4];nen_hi=c1[k+1]+c1[k+3]+2*c1[k+4]
  Bo_lo=EV*(CHI[0]*p0[k+1]+CHI[1]*(p0[k+3]+p0[k+4])+CHI[2]*p0[k+4])
  Bo_hi=EV*(CHI[0]*p1[k+1]+CHI[1]*(p1[k+3]+p1[k+4])+CHI[2]*p1[k+4])
  Bn_lo=EV*(CHI[0]*c0[k+1]+CHI[1]*(c0[k+3]+c0[k+4])+CHI[2]*c0[k+4])
  Bn_hi=EV*(CHI[0]*c1[k+1]+CHI[1]*(c1[k+3]+c1[k+4])+CHI[2]*c1[k+4])
  Uo_lo=1.5*KB*(NH+NHe+neo_lo)*math.exp(lt0[j])
  Uo_hi=1.5*KB*(NH+NHe+neo_hi)*math.exp(lt1[j])
  Un_lo=1.5*KB*(NH+NHe+nen_lo)*math.exp(cl0[j])
  Un_hi=1.5*KB*(NH+NHe+nen_hi)*math.exp(cl1[j])
  values=(nen_lo-neo_hi,nen_hi-neo_lo,Bn_lo-Bo_hi,Bn_hi-Bo_lo,
          Un_lo-Uo_hi,Un_hi-Uo_lo,
          (nen_lo+nen_hi-neo_lo-neo_hi)*.5,
          (Bn_lo+Bn_hi-Bo_lo-Bo_hi)*.5,
          (Un_lo+Un_hi-Uo_lo-Uo_hi)*.5)
  for arr,val in zip(sums,values):arr.append(val)
 tot=[math.fsum(a) for a in sums]
 return {"delta_Ne":tot[:2],"delta_B_erg":tot[2:4],"delta_U_gas_erg":tot[4:6],
         "midpoint_delta_Ne":tot[6],"midpoint_delta_B_erg":tot[7],
         "midpoint_delta_U_gas_erg":tot[8]}
def audit(a):
 result_path=Path(a.result);result=json.loads(result_path.read_text())
 need(result["schema"]=="REI_F05_NEW_SOURCE_ONLY_VERSIONED_V2_RESEARCH_WORKER_V1","RESULT_SCHEMA")
 runtime=result["runtime"]
 need(hashlib.sha256(canonical(runtime)).hexdigest()==result["new_runtime_contract_sha256"],"RUNTIME_HASH")
 need(runtime["original_source_sha256"]==EXPECTED_SOURCE and runtime["original_kernel_sha256"]==EXPECTED_KERNEL and runtime["original_policy_sha256"]==EXPECTED_POLICY,"ORIGINAL_THREE_SOURCE_KEYS")
 need(runtime["dependencies"]=={"numpy":"2.3.5","pandas":"2.2.3","scipy":"1.17.0"},"PINNED_RUNTIME_VERSION")
 need(result["original_accepted_tick"]=="160/131072" and result["original_research_candidate_tick"]=="161/131072_NOT_OFFICIAL","TIME_DOMAIN")
 need(result["original_native_map_evaluations"]==9 and len(result["physical_lanes"])==3,"ACTUAL_NATIVE_MAP_COUNT")
 need(result["old_V1_error_gate"]=="FAIL_UNCHANGED" and not result["official_accepted_161"] and result["production"]=="HOLD","NO_UNAUTHORIZED_ACCEPTANCE")
 need(result["DAG"]["central"]=="28/88" and result["DAG"]["canonical_delta"]==0,"DAG_FALSE_PROMOTION")
 reference_phys=None;body_ids=[];different_jobs=set()
 by={}
 for lane,slug in SLUG.items():
  row=result["physical_lanes"][lane]
  source_dir=Path(a.private)/slug
  state_file=Path(a.override_primary) if slug=="primary" and a.override_primary else source_dir/"VERSIONED_RESEARCH_V2_SOURCE_TICK161.state"
  need(sha(state_file)==row["versioned_state_sha256"],"TAMPERED_CANDIDATE_BYTES_"+slug)
  header,body=read_packed(state_file,b"REIV2SC1\0")
  need(header["format"]=="REI_V2SC1_SOURCE_SCOPED_RESEARCH_NOT_REIADP1" and header["source_not_official"],"UNAUTHORIZED_STATE_FORMAT")
  job=header["metadata"]["job"]
  need(job["lane"]==lane and job["accepted_index"]==4 and job["interval"]==[160,161] and job["depth"]==6,"JOB_SHAPE_"+slug)
  need(not job["official_tick161"] and job["source_tar_sha256"]==EXPECTED_SOURCE and job["source_kernel_sha256"]==EXPECTED_KERNEL,"JOB_SOURCE_"+slug)
  need(job["accepted_parent_state_sha256"]==result["original_source_history"][lane]["160"]["full_state_sha256"],"JOB_PARENT_SHA_"+slug)
  key=hashlib.sha256(canonical(job)).hexdigest()
  need(key==row["job_key"]==header["metadata"]["job_key"],"JOB_INTEGRITY_"+slug)
  different_jobs.add(key)
  need(job["new_v2_runtime_sha256"]==result["new_runtime_contract_sha256"],"RUNTIME_JOB_BIND_"+slug)
  need(header["metadata"]["source_V1_old_endpoint_bounds"]["log_T"]>2e-4,"OLD_V1_GATE_MUST_FAIL")
  need(all(v<2e-4 for v in header["metadata"]["V2_discrete_bounds"].values()),"NEW_V2_GATE_NOT_PASSED")
  require_ledgers=header["metadata"]["14_original_ledgers"]
  need(len(require_ledgers)==14 and all(aa<=0<=bb for aa,bb in require_ledgers.values()),"ORIGINAL_LEDGERS")
  source_v2=source_dir/"V2_RECEIPT.json";n=json.loads(source_v2.read_text())
  need(sha(source_dir/"SHADOW_V2_NONAUTHORITATIVE_TICK161.npz")==row["source_shadows_sha256"],"ORIGINAL_V2_NATIVE_SOURCE_BYTES_"+slug)
  need(n["original_policy_v2_post_map_validation"]=="PASS_SHADOW_ONLY" and n["official_tick161_accepted"] is False and n["original_legacy_worker_gate"]=="FAIL_HISTORICAL_UNCHANGED","ORIGINAL_NATIVE_SCOPE_"+slug)
  clock=header["metadata"]["clock_hex"]
  duration=float.fromhex(clock["duration"]);t0=duration*160/131072;t1=duration*161/131072;tm=t0+.5*(t1-t0)
  need(clock["t0"]==t0.hex() and clock["t1"]==t1.hex() and clock["tm"]==tm.hex(),"ORIGINAL_CLOCK_"+slug)
  need(hashlib.sha256(body).hexdigest()==result["three_lane_new_v2_numerical_body_sha256"]==row["state_body_sha256"],"V2_THREE_LANE_PHYSICAL_IDENTITY")
  body_ids.append(hashlib.sha256(body).hexdigest())
  parent=Path({"primary":a.p160,"recomb":a.r160,"shield":a.s160}[slug])
  need(sha(parent)==result["original_source_history"][lane]["160"]["full_state_sha256"],"ORIGINAL_160_SHA_"+slug)
  oldheader,oldbody=read_packed(parent,b"REIADP1\0")
  need(oldheader["metadata"]["lane"]==lane and oldheader["metadata"]["endpoint_tick"]==160,"ORIGINAL_PARENT_LANE")
  independent=independent_thermophysical(oldbody,body)
  recorded=row["physical_response"]
  for k,v in independent.items():
   other=recorded[k]
   if isinstance(v,list):need(all(close(x,y) for x,y in zip(v,other)),"REAL_PHYSICS_CROSSCHECK_"+slug+"_"+k)
   else:need(close(v,other),"REAL_PHYSICS_CROSSCHECK_"+slug+"_"+k)
  if reference_phys is None:reference_phys=independent
  else:need(all(close(x,y) for k,v in independent.items() for x,y in zip(v,reference_phys[k])) if False else independent==reference_phys,"PHYSICAL_REALIZATION_DIFFER")
  need(recorded["delta_Ne"][1]<0 and recorded["delta_B_erg"][1]<0,"SIGNED_ELECTRON_CHEMISTRY")
  need(recorded["delta_U_gas_erg"][0]<0<recorded["delta_U_gas_erg"][1],"THERMAL_SIGN_UNCERTAIN_NOT_ADMITTED")
  by[lane]={"job_key":key,"new_source_state_sha256":sha(state_file),
            "state_body_sha256":body_ids[-1],
            "original_parent_state_sha256":sha(parent),
            "old_v1_logT_upper":header["metadata"]["source_V1_old_endpoint_bounds"]["log_T"],
            "V2_bound_logT":header["metadata"]["V2_discrete_bounds"]["log_T"],
            "independent_46080_source_physics":independent}
 need(len(set(body_ids))==1 and len(different_jobs)==3,"CROSS_LANE_VERSIONED_JOB_IDENTITY")
 report={"schema":"REI_F05_V2_WORKER_SOURCE_DISJOINT_STDLIB_AUDIT_V1",
         "result":"PASS_SOURCE_SCOPED_NOT_OFFICIAL",
         "cells_per_lane":N,"new_v2_native_map_executions":9,
         "three_lanes_one_physical_body":True,"three_versioned_distinct_job_keys":True,
         "three_original_14_ledger_checks":"14/14_EACH_PASS",
         "actual_original_v1_failure_preserved":True,
         "new_v2_source_discrete_comparison_pass":True,
         "official_tick161":False,"DAG":"28/88",
         "thermal_delta_U_sign":"UNRESOLVED_INTERVAL_CONTAINS_ZERO",
         "original_source_separate_author":"NOT_RUN_SAME_AUTHOR_DIFFERENT_READER",
         "verified_lanes":by}
 Path(a.out).parent.mkdir(parents=True,exist_ok=True)
 Path(a.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"AUDIT":"PASS","new_physics_cells":3*N,"unique_physical_realizations":1,
                   "versioned_job_keys":3,"tamper_rejection_contract":"SHA_FAIL_CLOSED",
                   "Ne_delta_sign":"NEGATIVE","B_delta_sign":"NEGATIVE","gas_U_delta_sign":"UNRESOLVED",
                   "official_tick161":"HOLD","DAG":"28/88"}))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for q in ("result","private","p160","r160","s160","out"):p.add_argument("--"+q,required=True)
 p.add_argument("--override-primary",default="")
 audit(p.parse_args())
