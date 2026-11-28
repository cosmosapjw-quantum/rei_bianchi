#!/usr/bin/env python3
"""Public immutable source-free derived V2 source receipt.
The true original V2 26-event private source is replayed only locally.
"""
from __future__ import annotations
import hashlib,importlib.util,json,tempfile
from pathlib import Path
D=Path(__file__).resolve().parent
EXPECTED={
 "ORIGINAL_REI_F05_V2_T160_T162_LYA_92160.csv.gz":"56b597b57cb08ac1ab25dfe4f9b2b091ca5e36fc3465a89fc3d6f98769fe5521",
 "SCIENCE_RESULT.json":"bd2ee6b067f75ebd5032627abe476cfab1c628153d809cffd8016b19f682cb1b",
 "INDEPENDENT_AUDIT.json":"c47e8a4799d8b406e621a38149a6b4e5d753ef50f07caba202b3135d85eafbc3"}
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for x in iter(lambda:f.read(1048576),b""):h.update(x)
 return h.hexdigest()
def ensure(c,msg):
 if not c:raise ValueError("HE153_IMMUTABLE_RECEIPT_"+msg)
def verify(folder=D/"results"):
 folder=Path(folder)
 for f,hashval in EXPECTED.items():ensure(sha(folder/f)==hashval,"HASH_"+f)
 source=json.loads((folder/"SCIENCE_RESULT.json").read_text())
 audit=json.loads((folder/"INDEPENDENT_AUDIT.json").read_text())
 ensure(source["source_original_predecessor_all_3_lane_physical_realizations"]==1,"FALSE_3_SOURCES")
 ensure(source["science_rows"]==92160 and len(source["two_research_source_intervals"])==2,"SOURCE_GRAIN")
 ensure(source["source_escape_branch_f_interval"]==[0.1,1.0],"SOURCE_F_CHANGED")
 ensure(source["source_ticks161_162_official"] is False
        and source["original_tick161_162_production"]=="NOT_ACCEPTED","FALSE_OFFICIAL_STATE")
 ensure(source["canonical_delta"]==0 and source["production"]=="HOLD"
        and source["source_spatial_photon_transport_owned"] is False,"FALSE_SOURCE_OWNERSHIP")
 ensure(source["original_original_26event_kernel_sha256"]=="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644",
        "KERNEL_CHANGED")
 ensure(source["source_interval_local_Lya_lower_erg"]==0.0
        and source["source_interval_local_Lya_energy_upper_erg"]>0,"SOURCE_LOWER_LYA_BOUND")
 for period in source["two_research_source_intervals"]:
  ensure(period["original_native_14_ledger_zero_included"] and period["exact_research_V2_endpoint_array_identity"],
         "NATIVE_ORIGINAL_SOURCE_GATES")
  ensure(max(period["source_V2_common_parent_defects"].values())<2e-4
         and max(period["source_original_public_widths"].values())<2e-3,"FROZEN_SOURCE_GATE")
  ensure(period["esc_local_Lya_energy_erg"][0]==0.0,"PHOTON_ESCAPE_ZERO_LOWER")
 ensure(audit["source_csv_SHA256"]==EXPECTED["ORIGINAL_REI_F05_V2_T160_T162_LYA_92160.csv.gz"]
   and audit["source_json_SHA256"]==EXPECTED["SCIENCE_RESULT.json"]
   and audit["original_source_rows_verified"]==92160,"SOURCE_AUDIT_MISMATCH")
 ensure(audit["maximum_scaled_original_source_quadrature_reconstruction_discrepancy"]<1e-12
   and audit["maximum_scaled_photon_energy_consistency_discrepancy"]<1e-13,
   "SOURCE_NUMERICAL_IDENTITY")
 spec=importlib.util.spec_from_file_location("hei153_independent",D/"audit_v2_lya_sourcefree.py")
 ensure(spec is not None and spec.loader is not None,"INDEPENDENT_AUDITOR_MISSING")
 auditor=importlib.util.module_from_spec(spec);spec.loader.exec_module(auditor)
 with tempfile.TemporaryDirectory() as temp:
  p=Path(temp)/"AUDIT.json"
  auditor.run(folder/"ORIGINAL_REI_F05_V2_T160_T162_LYA_92160.csv.gz",
              folder/"SCIENCE_RESULT.json",p)
  ensure(sha(p)==EXPECTED["INDEPENDENT_AUDIT.json"],"AUDIT_BYTES_NOT_REPRODUCIBLE")
 print("PASS_PUBLIC_FROZEN_ORIGINAL_V2_LYA_SOURCE_DERIVED_RECEIPT_ONLY")
if __name__=="__main__":verify()
