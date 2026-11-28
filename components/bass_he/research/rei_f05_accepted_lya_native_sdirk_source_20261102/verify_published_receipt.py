#!/usr/bin/env python3
"""Public source-free immutable acceptance and full-row HeII Ly-alpha receipt.
Does not replay original 26-event source, source-authority tick or photon RT.
"""
from __future__ import annotations
import hashlib,importlib.util,json,tempfile
from pathlib import Path
D=Path(__file__).resolve().parent
FILES={
 "ORIGINAL_REI_F05_ACCEPTED_0_64_128_160_LYA_ESCAPE_138240.csv.gz":
   "13e05ff26adfb8eec5c2e0d0d028a1106f190771c642c2bb4306db79d9a80daf",
 "SCIENCE_RESULT.json":
   "545f363740a8533f643d1f26b9dd6fd0c30d42078800fc6dce0d3c604156a993",
 "INDEPENDENT_AUDIT.json":
   "197a4a603f27af881da6c615187523c60c162aa88fd943669a1d8e292068a9f3"
}
def sha(path):
 d=hashlib.sha256()
 with Path(path).open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):d.update(chunk)
 return d.hexdigest()
def check(c,msg):
 if not c:raise ValueError("BASS_HE_PR151_FROZEN_RECEIPT_"+msg)
def verify(root=D/"results"):
 root=Path(root)
 for name,dig in FILES.items():
  check(sha(root/name)==dig,"SOURCE_FREE_SHA_"+name)
 data=json.loads((root/"SCIENCE_RESULT.json").read_text())
 audit=json.loads((root/"INDEPENDENT_AUDIT.json").read_text())
 check(data["source_genuine_physics_rows"]==3*46080,"SOURCE_ROWS")
 check(data["original_accepted_source_ticks"]==[0,64,128,160],"SOURCE_ACCEPTED_CLOCK")
 check(data["original_tick161"]=="NOT_ACCEPTED" and data["production"]=="HOLD" and data["canonical_delta"]==0,"FALSE_ADMISSION")
 check(data["source_branch_f_range"]==[0.1,1.0],"FALSE_ESCAPE_F_BRACKET")
 check(data["original_spectrum_and_causal_transport"]=="NOT_ADMITTED","FALSE_CAUSAL_SOURCE")
 check(len(data["original_source_accepted_intervals"])==3,"ORIGINAL_INTERVAL_COUNT")
 for item in data["original_source_accepted_intervals"]:
  check(item["source_three_maps_certified"] and item["14_original_ledgers_include_zero"] and item["original_zero_table_events"],"ORIGINAL_GATES_NOT_SOURCED")
  check(max(item["source_local_defect_by_field"].values())<2e-4 and max(item["source_width_by_field"].values())<2e-3,"ORIGINAL_ACCEPTANCE_GATE_TAMPER")
 check(data["integrated_three_interval_escaped_energy_erg"][0]==0.0 and
       data["integrated_three_interval_escaped_photons"][0]==0.0,"SOURCE_ESCAPE_LOWER_NOT_ZERO")
 check(audit["source_CSV_sha256"]==FILES["ORIGINAL_REI_F05_ACCEPTED_0_64_128_160_LYA_ESCAPE_138240.csv.gz"] and
       audit["science_JSON_sha256"]==FILES["SCIENCE_RESULT.json"],"AUDIT_INPUT_BINDING")
 check(audit["independent_rows_checked"]==3*46080 and audit["result"]=="PASS_ALL_138240_SOURCE_LYA_PHOTON_ENERGY_ROWS","AUDIT_COUNT")
 check(audit["max_source_photon_energy_relative_residual"]<6e-15,"PHOTON_ENERGY_DIFFERENCE")
 source=D/"audit_source_free.py"
 spec=importlib.util.spec_from_file_location("bass_he_f05_original_lya_sourcefree_audit",source)
 check(spec is not None and spec.loader is not None,"AUDIT_MODULE_MISSING")
 mod=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(mod)
 with tempfile.TemporaryDirectory() as t:
  p=Path(t)/"INDEPENDENT_AUDIT.json"
  mod.audit(root/"ORIGINAL_REI_F05_ACCEPTED_0_64_128_160_LYA_ESCAPE_138240.csv.gz",
            root/"SCIENCE_RESULT.json",p)
  check(sha(p)==FILES["INDEPENDENT_AUDIT.json"],"SOURCEFREE_REPLAY_NONIDENTICAL")
 print("PASS_ALL_SOURCE_FREE_RECEIPTS_ONLY_NOT_ORIGINAL_IVP_OR_CAUSAL_RADIATION")
if __name__=="__main__":verify()
