#!/usr/bin/env python3
"""Publish one traceable REI source-only 7-pin V2 owner science admission.

Does not read/write or change original V1 production accepted history.
Checks prior REI #368 research worker identity and #369 actual t162 physics.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

SOURCE="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
PREVIOUS_PR369_SCIENCE_SHA="44458ac677ace87d33a807422e8a4c692ea29563e57e81f88bc05aaad33d4b23"
T161="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
T162="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
BODY="fa71a11bf14326e3b2bf2303005917786af1e0e47c39003c07b28708b4e664e5"
PINNED={"numpy":"2.3.5","scipy":"1.17.0","pandas":"2.2.3",
 "python-dateutil":"2.9.0.post0","pytz":"2026.3.post1","tzdata":"2026.3","six":"1.17.0"}
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR",
       "SCRIPT_SELF_SHIELDING_AUDITOR")
def check(ok,msg):
 if not ok: raise AssertionError("REI_OWNER_FULL_V2_RUNTIME_"+msg)
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for v in iter(lambda:f.read(1<<20),b""):h.update(v)
 return h.hexdigest()
def canonical(v):
 return json.dumps(v,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(",",":")).encode("ascii")

def main(result,audit,continuation,old_science,private,out):
 check(sha(old_science)==PREVIOUS_PR369_SCIENCE_SHA,"PR369_SCIENCE_SOURCE_IDENTITY")
 a=json.loads(result.read_text());b=json.loads(audit.read_text())
 c=json.loads(continuation.read_text());old=json.loads(old_science.read_text())
 check(a["schema"]=="REI_F05_NEW_SOURCE_ONLY_VERSIONED_V2_RESEARCH_WORKER_V1","PR368_SCHEMA")
 check(a["original_accepted_tick"]=="160/131072" and not a["official_accepted_161"],"OLD_ACCEPTED_HISTORY_HOLD")
 full=a["runtime"]["complete_original_seven_pin_runtime"]
 check(full["all_seven_original_dependencies_byte_version_matched"] and
       full["new_full_runtime_contract"]["dependencies"]==PINNED,"EXACT_SEVEN_PIN")
 check(full["original_v1_sha256"]=="10ab5823e109f32d693c82d246b3369045ddecf5217fa30fc4013ab6d55c3810",
       "HISTORICAL_FULL_RUNTIME_CONTRACT")
 check(full["original_runtime_changed_fields"]==
       ["git_head","numeric_fingerprint.numpy_runtime_sha256"],"NEW_NUMERIC_RUNTIME_DIFFERENCE_CLASS")
 check(not full["numa_cpu_simd_runtime_equivalence"]=="VERIFIED","UNPROVEN_RUNTIME_NUMERICS")
 check(full["new_full_runtime_contract_sha256"]==full["new_full_runtime_contract"]["sha256"],"NEW_FULL_RUNTIME_SHA")
 check(hashlib.sha256(canonical(a["runtime"])).hexdigest()==a["new_runtime_contract_sha256"],
       "WORKER_V2_RUNTIME_SHA")
 check(a["three_lane_new_v2_numerical_body_sha256"]==BODY,"REAL_V2SC1_SOURCE_BODY")
 check(a["original_native_map_evaluations"]==9 and len(a["physical_lanes"])==3,"NATIVE_MAPS")
 check(b["result"]=="PASS_SOURCE_SCOPED_NOT_OFFICIAL" and b["cells_per_lane"]==46080,
       "BLIND_INDEPENDENT_SOURCE_AUDIT")
 check(set(a["physical_lanes"])==set(LANES),"ORIGINAL_THREE_LANES")
 jobs=set();body=set();state_digests={};source={}
 for key in LANES:
  x=a["physical_lanes"][key]
  check(x["V1_old_logT_upper"]>2e-4 and x["V2_source_logT_upper"]<2e-4 and
        x["V2_public_max_width"]<.002,"UNCHANGED_V1_FAIL_AND_V2_GATE_"+key)
  check(x["source_native_14_ledgers"]==14 and x["source_table_events"]==0,"ORIGINAL_14_LEDGER_"+key)
  check(x["native_full_half_map_count"]==3 and x["source_shadows_sha256"]==T161,
        "ACTUAL_ORIGINAL_SOURCE_MAP_"+key)
  jobs.add(x["job_key"]);body.add(x["state_body_sha256"])
  state_digests[key]=x["versioned_state_sha256"]
  source[key]=x["source_shadows_sha256"]
 check(len(jobs)==3 and body=={BODY},"THREE_LANE_STATE_JOB_IDENTITY")
 check(c["status"]=="SOURCE_NATIVE_TICK161_ACTUALLY_CONSUMED_IN_NEXT_MAP" and
       c["source_parent_tick161_sha256"]==T161 and
       c["source_candidate_state_tick162_sha256"]==T162,"ACTUAL_NEXT_SOURCE")
 check(c["original_14_ledgers_include_zero"] and c["original_table_event_count"]==0,
       "CONSUMED_ORIGINAL_14_LEDGER")
 check(max(c["original_V2_common_parent_local_defect_four_coordinates"].values())<2e-4 and
       max(c["original_width_four_coordinates"].values())<.002,"NEXT_SOURCE_GATES")
 check(c["official_tick161_accepted"] is False and c["official_tick162_accepted"] is False,
       "NEXT_STEP_NOT_OLD_PRODUCTION")
 check(old["source_v2_tick161_parent_SHA256"]==T161 and
       old["source_v2_tick162_research_SHA256"]==T162,"PREVIOUS_ORIGINAL_T161_T162")
 out.mkdir(parents=True,exist_ok=True)
 private=Path(private)
 for slug in ("primary","recomb","shield"):
  p=private/slug/"SHADOW_V2_NONAUTHORITATIVE_TICK161.npz"
  check(sha(p)==T161,"PRIVATE_SOURCE_NPZ_"+slug)
 status={
   "schema":"REI_F05_OWNER_FULL_SEVEN_PIN_VERSIONED_V2_RUNTIME_ADMISSION_V1",
   "source_original_F05_TAR_SHA256":SOURCE,
   "source_original_F05_kernel_SHA256":KERNEL,
   "source_accepted_previous_history":"0_64_128_160_ALL_3_LANES_BYTE_IDENTITY",
   "old_V1_official_accepted_tick":"160/131072",
   "v2_new_runtime_full_sha256":full["new_full_runtime_contract_sha256"],
   "v2_new_runtime_bound_job_sha256":a["new_runtime_contract_sha256"],
   "old_historical_v1_runtime_sha256":full["original_v1_sha256"],
   "historical_runtime_difference":full["original_runtime_changed_fields"],
   "all_seven_original_dependency_pins_matched":True,
   "v2_source_imported_from_original_PR368_worker_git_blob_sha1":
      full["source_upstream_worker_git_blob_sha1"],
   "three_lane_original_V2SC1_body_byte_identical":True,
   "three_lane_original_V2SC1_body_SHA256":BODY,
   "three_lane_distinct_job_keys":True,
   "source_original_native_full_half_maps_t160_t161":9,
   "original_native_full_half_maps_t161_t162":3,
   "source_original_realizations":1,
   "source_46080_cells_per_lane":46080,
   "source_V2SC1_full_state_SHA256_by_lane":state_digests,
   "source_V2_tick161_real_NPZ_SHA256":T161,
   "source_V2_tick162_next_NPZ_SHA256":T162,
   "source_original_14_ledger_each_lane":"3/3_PASS",
   "source_original_next_14_ledger":"PASS",
   "source_original_table_events":0,
   "source_V1_160_161_logT_failed_upper":a["physical_lanes"][LANES[0]]["V1_old_logT_upper"],
   "source_V2_160_161_logT_upper":a["physical_lanes"][LANES[0]]["V2_source_logT_upper"],
   "source_V2_161_162_logT_upper":c["original_V2_common_parent_local_defect_four_coordinates"]["log_T"],
   "source_original_local_gate":2e-4,
   "source_original_width_gate":2e-3,
   "next_source_material_delta_outer":c["source_conditional_delta_outer_intervals"],
   "next_source_material_delta_midpoint":c["source_conditional_delta_midpoint"],
   "new_v2_worker_source_bound_state_decision":"ACCEPT_SOURCE_DISCRETE_V2SC1_FOR_EXPLICIT_RESEARCH_HISTORY",
   "original_V1_production_admission":"HOLD_NOT_SAME_RUNTIME_CONTRACT",
   "unresolved_original_opaque_numpy_runtime_fingerprint_diff":True,
   "not_a_global_continuum_ODE_error_certificate":True,
   "not_a_full_26event_Rust_solver":True,
   "canonical_REI_DAG":"28/88",
   "working_REI_DAG":"33/88",
   "physical_fast_REI_DAG":"4/7",
   "canonical_delta":0,
   "official_tick161":False,
   "official_tick162":False,
   "production":"HOLD",
   "native_subagent":"NOT_RUN",
   "scientific_progress":"FULL_RUNTIME_SEVEN_PIN_VERSIONED_ADMISSION_AND_OLD_NEXT_MAP_BYTE_PARITY"
 }
 path=out/"SEVEN_PIN_V2_OWNER_SCIENCE.json"
 path.write_text(json.dumps(status,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":status["new_v2_worker_source_bound_state_decision"],
   "old_runtime_sha":status["old_historical_v1_runtime_sha256"],
   "new_full_runtime_sha":status["v2_new_runtime_full_sha256"],
   "full_7_pins":True,"historical_difference":status["historical_runtime_difference"],
   "old_161_source_byte":T161,"next_162_source_byte":T162,
   "original_maps_executed":12,"DAG":"28/88",
   "public_sha256":sha(path)},sort_keys=True))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for s in ("result","audit","continuation","old_science","private","out"):
  p.add_argument("--"+s,required=True,type=Path)
 a=p.parse_args()
 main(a.result,a.audit,a.continuation,a.old_science,a.private,a.out)
