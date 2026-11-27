#!/usr/bin/env python3
"""Frozen SOURCE-FREE public receipt verification; not a full 26-event replay."""
from __future__ import annotations
import csv,gzip,hashlib,json,math
from pathlib import Path

D=Path(__file__).resolve().parent
FIXED={
 "REI_ORIGINAL_T160_46080_HHE_26EVENT_ENERGY_SOURCE.csv.gz":"f0aba50cf048499ecaed4642b050d2e4c76de9fbe6a77be5d3cc9a3f39ee641c",
 "SCIENCE_RESULT.json":"202c422e7c23da3ea93b82e35429efe387b66225107e94248e28c6263facc5e2",
 "INDEPENDENT_AUDIT.json":"dce153d7c433d41e476de86b5c63e308a975f48bce98144459ba5df0f94b6220"}
def check(x,label):
 if not x:raise ValueError("PUBLISHED_SOURCE_RECEIPT_"+label)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()

def verify(folder=D/"results"):
 folder=Path(folder)
 for name,want in FIXED.items():
  check(sha(folder/name)==want,"SHA_DRIFT_"+name)
 data=json.loads((folder/"SCIENCE_RESULT.json").read_text())
 audit=json.loads((folder/"INDEPENDENT_AUDIT.json").read_text())
 check(data["source_original_array_sha256"]=="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01","SOURCE_ARRAY_DRIFT")
 check(data["source_original_rhs_sha256"]=="b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36","RHS_DRIFT")
 check(data["result"]["original_nodes"]==46080 and data["canonical_delta"]==0,"NODE_OR_DAG_DRIFT")
 check(not data["official_tick161"] and not data["photon_spectral_emissivity_admitted"] and data["production"]=="HOLD","FALSE_OWNER_ADMISSION")
 check(audit["source_csv_sha256"]==FIXED["REI_ORIGINAL_T160_46080_HHE_26EVENT_ENERGY_SOURCE.csv.gz"],"AUDIT_INPUT_CSV_DRIFT")
 check(audit["source_json_sha256"]==FIXED["SCIENCE_RESULT.json"],"AUDIT_INPUT_JSON_DRIFT")
 check(audit["verified_source_cells"]==46080 and audit["independent_stoichiometric_energy_channels"]==5,"INDEPENDENT_RECONSTRUCTION_NOT_ALL_CELLS")
 check(audit["max_scaled_per_cell_reconstruction_error"]<2e-12,"INDEPENDENT_RECONSTRUCTION_EXCEEDS_LIMIT")
 powers=data["result"]["physical_energy_powers"]
 check(powers["Bdot_net_erg_s"]<0 and powers["photo_binding_positive_erg_s"]>0 and powers["collisional_binding_positive_erg_s"]>0,"SCIENTIFIC_SIGNS")
 check(powers["OTS_unresolved_residual_erg_s"]>0 and powers["OTS_escaped_erg_s"]>0,"PHOTON_RESIDUAL_SIGNS")
 # Exact source-group chemistry+OTS energy-rearrangement versus source power.
 rhs=(powers["photo_binding_positive_erg_s"]+powers["collisional_binding_positive_erg_s"])
 lhs=(powers["Bdot_net_erg_s"]+powers["OTS_resolved_heat_erg_s"]+
      powers["OTS_unresolved_residual_erg_s"]+powers["OTS_escaped_erg_s"])
 check(abs(lhs-rhs)/max(abs(lhs),abs(rhs))<1e-12,"GLOBAL_SOURCE_ENERGY_IDENTITY")
 with gzip.open(folder/"REI_ORIGINAL_T160_46080_HHE_26EVENT_ENERGY_SOURCE.csv.gz","rt") as f:
  reader=csv.DictReader(f)
  check(all(z in reader.fieldnames for z in ("cell","rate_HI_ION","rate_HEI_ION","rate_HEII_ION","branch_A_H","branch_A_HeI","OTS_unresolved_erg_s")),"SOURCE_EVENT_COLUMNS")
  count=0
  for row in reader:
   check(int(row["cell"])==count,"CELL_ORDER")
   count+=1
  check(count==46080,"ROW_COUNT")
 print("PASS_46080_DERIVED_SOURCE_RECEIPT_ONLY_NOT_ORIGINAL_OWNER_REPLAY")

if __name__=="__main__":verify()
