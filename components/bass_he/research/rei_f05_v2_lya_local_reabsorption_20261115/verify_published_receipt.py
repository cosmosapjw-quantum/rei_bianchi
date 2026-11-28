#!/usr/bin/env python3
"""Source-free immutable public receipt for original REI F05 V2 local OTS.
GitHub CI cannot replay private V2 states; local source replay separate.
"""
from pathlib import Path
import hashlib,json,importlib.util,tempfile

D=Path(__file__).resolve().parent
PR153=D.parent/"rei_f05_v2_lya_causal_parent_source_20261102"/"results"/"SCIENCE_RESULT.json"
FIXED={
 "LOCAL_OTS_FEEDBACK_SCIENCE.json":"de1451d19d9f678394e9f22415c740105e2ffa3ed7b482dde2b583442c65a8f7",
 "REI_ORIGINAL_V2_LYA_LOCAL_H_HEI_FEEDBACK_92160.csv.gz":"6acd17f0612738fa2954f3285b92b53d1444d8a4cc020375731d0557c0ba80ae",
 "INDEPENDENT_AUDIT.json":"8c096f17aa89cd6003837424262a170182b88ac29d9f8339fac79c420d3d7395"}
PARENT_SHA="bd2ee6b067f75ebd5032627abe476cfab1c628153d809cffd8016b19f682cb1b"
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def check(cond,msg):
 if not cond:raise ValueError("BASS_HE_F05_V2_LOCAL_OTS_RECEIPT_"+msg)
def verify(folder=D/"results"):
 folder=Path(folder)
 for file,ref in FIXED.items():check(sha(folder/file)==ref,"SHA_DRIFT_"+file)
 check(sha(PR153)==PARENT_SHA,"IMMUTABLE_PR153_SOURCE_DRIFT")
 result=json.loads((folder/"LOCAL_OTS_FEEDBACK_SCIENCE.json").read_text())
 audit=json.loads((folder/"INDEPENDENT_AUDIT.json").read_text())
 check(result["source_authority_head"]=="645437697d915da45147071e266bc47937e76f6c","ORIGINAL_REI_OWNER")
 check(result["original_26event_kernel_sha256"]=="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644","ORIGINAL_KERNEL")
 check(result["parent_escaped_source_science"]==PARENT_SHA,"ORIGINAL_PARENT_PHYSICS")
 check(result["source_f_interval"]==[.1,1.] and result["physical_source_rows"]==92160,"CORRECT_SOURCE_BRANCH_AND_SIZE")
 check(result["original_tick161_162_official"] is False and result["canonical_delta"]==0
   and result["production"]=="HOLD","FALSE_PRODUCTION_ADMISSION")
 check(result["actual_original_event_heat_preserved"] and result["re_absorbed_OTS_photons_already_in_source_population_RHS"],"DOUBLE_COUNT_CLAIM")
 check(result["source_no_spatial_cells_or_null_rays"],"INVENTED_SPATIAL_CAUSAL_TRANSPORT")
 check(len(result["per_microtick_original_site_branches"])==2,"SOURCE_TIME_INTERVALS")
 for p in result["per_microtick_original_site_branches"]:
  check(p["source_14_ledgers_include_zero"] and p["source_heat_intersection"] and p["source_escape_intersection"],"ORIGINAL_ENERGY_NONINTERSECTION")
  check(p["emitted"][1]>0 and p["heat_original"][1]>0 and p["absorbed_H"][1]>0
      and p["absorbed_HeI"][1]>0,"SOURCE_NATIVE_CHANNELS")
 check(audit["rows_checked"]==92160 and audit["number_and_energy_interval_overlap_cells"]==92160
       and audit["status"].startswith("PASS_SOURCE_FREE"),"INDEPENDENT_AUDIT_SCOPE")
 check(audit["source_input_csv_sha256"]==FIXED["REI_ORIGINAL_V2_LYA_LOCAL_H_HEI_FEEDBACK_92160.csv.gz"]
       and audit["source_input_json_sha256"]==FIXED["LOCAL_OTS_FEEDBACK_SCIENCE.json"],"INDEPENDENT_INPUTS")
 check(audit["max_scaled_integral_reconstruction_error"]<1e-12
       and audit["max_scaled_chemical_photoheat_upper_error"]<1e-12,"SOURCE_LOCAL_PHYSICS_RESIDUAL")
 spec=importlib.util.spec_from_file_location("hei154_sourcefree_independent",D/"audit_local_ots_sourcefree.py")
 check(spec is not None and spec.loader is not None,"AUDITOR_MISSING")
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 with tempfile.TemporaryDirectory() as tmp:
  output=Path(tmp)/"INDEPENDENT_AUDIT.json"
  mod.verify(folder/"REI_ORIGINAL_V2_LYA_LOCAL_H_HEI_FEEDBACK_92160.csv.gz",
            folder/"LOCAL_OTS_FEEDBACK_SCIENCE.json",PR153,output)
  check(sha(output)==FIXED["INDEPENDENT_AUDIT.json"],"INDEPENDENT_BYTE_REPLAY")
 print("PASS_ORIGINAL_V2_LOCAL_OTS_HHE_SOURCE_FREE_RECEIPT_ONLY")
if __name__=="__main__":verify()
