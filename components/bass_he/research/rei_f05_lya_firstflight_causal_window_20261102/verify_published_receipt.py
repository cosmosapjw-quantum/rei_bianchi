#!/usr/bin/env python3
"""Source-free public immutable receipt validation.
REI original source / private REC195 raw state NOT replayed by GitHub Actions.
"""
import hashlib,importlib.util,json,tempfile
from pathlib import Path

D=Path(__file__).resolve().parent
EXPECTED={
 "REI_F05_LYA_FROZEN_CAUSAL_WINDOW_CAPACITY_138240.csv.gz":"7eca7c5f3e8188177496033cd3443b26eee12e0b87c04f53bb13f6c3294510f6",
 "SCIENCE_RESULT.json":"9ee4a8039c937394ef89e2d2d0ac04f12baa80c35a941fc03c8037dfd9f62dbd",
 "INDEPENDENT_AUDIT.json":"692c36366e5db0ed141643973b3a2d710229746a091dad22a4b0b72c36bbc5d2"
}
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def check(x,msg):
 if not x:raise ValueError("BASS_HE_PR152_FROZEN_PUBLIC_RECEIPT_"+msg)
def verify(folder=D/"results"):
 folder=Path(folder)
 for filename,s in EXPECTED.items():
  check(sha(folder/filename)==s,"HASH_CHANGED_"+filename)
 data=json.loads((folder/"SCIENCE_RESULT.json").read_text())
 audit=json.loads((folder/"INDEPENDENT_AUDIT.json").read_text())
 check(data["original_source_quadrature_nodes_not_spatial_ray_cells"] is True
   and data["original_causal_geometry_not_identified"] is True,"FALSE_RAY_GEOMETRY")
 check(data["original_line_transported"]=="NO_SOURCE_RAY_PATHS","FALSE_PHOTON_TRANSPORT")
 check(data["original_tick161"]=="NOT_ACCEPTED" and data["production"]=="HOLD" and data["canonical_delta"]==0,
   "FALSE_CANONICAL_ADMISSION")
 check(data["source_original_data_rows"]==138240 and len(data["intervals"])==3,
   "NO_ORIGINAL_SOURCE_SCIENCE_ROWS")
 check(data["source_f_interval"]==[0.1,1.0],"SOURCE_F_INTERVAL_FALSE")
 check(data["source_original_opacity_constants_cm2"]["HI_41"]>0 and
   data["source_original_opacity_constants_cm2"]["HeI_41"]>0,"ORIGINAL_OPACITY_MISSING")
 check(data["totals"]["input_source_escape_upper_photons"]>data["totals"]["right_endpoint_frozen_conditional_absorbed_photons"]>0,
  "SOURCE_PHOTON_REFERENCE_NOT_CONSERVING")
 check(data["totals"]["source_box_hi_cap_absorbed_photons"]>=
       data["totals"]["right_endpoint_frozen_conditional_absorbed_photons"],"BOX_UPPER_MISLABELED")
 check(audit["original_science_json_sha256"]==EXPECTED["SCIENCE_RESULT.json"] and
   audit["source_dataset_sha256"]==EXPECTED["REI_F05_LYA_FROZEN_CAUSAL_WINDOW_CAPACITY_138240.csv.gz"],"INDEPENDENT_AUDIT_SOURCE_DRIFT")
 check(audit["rows_verified"]==138240 and audit["max_relative_line_energy_identity_error"]<1e-14,
       "ORIGINAL_PHOTON_ENERGY_IDENTITY")
 spec=importlib.util.spec_from_file_location("he152_frozen_independent",D/"audit_conditional_sourcefree.py")
 check(spec is not None and spec.loader is not None,"NO_SECOND_ALGORITHM")
 m=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(m)
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)/"INDEPENDENT_AUDIT.json"
  m.check(folder/"REI_F05_LYA_FROZEN_CAUSAL_WINDOW_CAPACITY_138240.csv.gz",
          folder/"SCIENCE_RESULT.json",out)
  check(sha(out)==EXPECTED["INDEPENDENT_AUDIT.json"],"INDEPENDENT_REPLAY_NOT_DETERMINISTIC")
 print("PASS_SOURCEFREE_SOURCE_ORIGINAL_FROZEN_WINDOW_CAPACITY_ONLY_NO_GEODESIC_CLAIM")
if __name__=="__main__":verify()
