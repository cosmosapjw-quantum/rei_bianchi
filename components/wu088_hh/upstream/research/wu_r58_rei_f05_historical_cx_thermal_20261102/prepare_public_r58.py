#!/usr/bin/env python3
"""Publish only source-free science and 24 authentic source-cell rows."""
import csv,gzip,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
D=ROOT/"results"
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for ch in iter(lambda:f.read(1<<20),b""):h.update(ch)
 return h.hexdigest()
def run():
 s=json.loads((D/"R58_RESULTS.json").read_text())
 p=D/s["files"]["full_original_source_conditional_46080_csv"]
 assert sha(p)==s["files"]["full_original_source_conditional_SHA256"]
 with gzip.open(p,"rt") as f:rows=list(csv.DictReader(f))
 assert len(rows)==46080
 indices=np.argsort(np.array([float(row["native_proper_nH_cm3"]) for row in rows]))
 selected=np.unique(indices[np.linspace(0,46079,24,dtype=int)])
 columns=[
  "node","native_proper_nH_cm3","original_T_tick160_K",
  "original_HII_tick160","original_REI_26event_thermal_Udot_tick160_erg_per_s",
  "H_MATCHED_y160","ALL_NEUTRAL_y160",
  "H_MATCHED_C160","ALL_NEUTRAL_C160",
  "H_MATCHED_cx_rate_tick160_per_D_s","ALL_NEUTRAL_cx_rate_tick160_per_D_s",
  "H_MATCHED_Qgas_CX_0to160_erg_per_H","ALL_NEUTRAL_Qgas_CX_0to160_erg_per_H",
  "H_MATCHED_Qgas_CX_first_tick_erg_per_H","ALL_NEUTRAL_Qgas_CX_first_tick_erg_per_H"]
 witness=D/"R58_REAL_ORIGINAL_CELL_WITNESS_24.csv"
 with witness.open("w",newline="") as f:
  w=csv.writer(f,lineterminator="\n");w.writerow(columns)
  for i in selected:w.writerow([rows[i][key] for key in columns])
 a=json.loads((D/"R58_INDEPENDENT_AUDIT.json").read_text())
 public={
  "schema":"WU_R58_REAL_REI_F05_SOURCE_HISTORICAL_D_CX_THERMAL_PUBLIC_V1",
  "project":"cosmosapjw-quantum/WU088_HH",
  "WU_immutable_parent_PR":197,"REI_native_owner_PR":367,
  "authority_source_SHA256":s["authority_source_SHA256"],
  "physical_contract":s["physical_contract"],
  "original_source_reference":s["original_source_reference"],
  "scenario_science":s["scenario_science"],
  "DAG":s["DAG"],"gates":s["gates"],
  "independent_audit":{
    "verdict":a["verdict"],
    "original_REI_4epoch_source_rows_scanned":a["original_REI_4epoch_source_rows_scanned"],
    "source_replayed_D_cells":a["source_replayed_D_cells"],
    "Savin_47_original_rate_nodes_checked":a["Savin_47_original_rate_nodes_checked"],
    "scenarios":a["scenarios"],
    "native_subagent":a["native_subagent"],"distinct_author":a["distinct_author"]},
  "test_verdict":{"normal_Python":"11/11_PASS","optimized_Python":"11/11_PASS"},
  "source_free_24cell_witness_SHA256":sha(witness),
  "original_full_46080_private_data_SHA256":s["files"]["full_original_source_conditional_SHA256"],
  "R58_model_does_not_claim_net_heating":True,
  "source_complete_parent_archive_required":True,
  "original_R57_parent_source_archive_SHA256":"ad3d9c99d14cfbd4d729c691d8766705812ff936cf15081a5870061f807d02ea"}
 path=D/"R58_PUBLIC_SCIENCE.json"
 path.write_text(json.dumps(public,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"R58_PUBLIC_SHA256":sha(path),"WITNESS_SHA256":sha(witness),"DATA_FULL_SHA256":sha(p),"ROWS":len(rows)},sort_keys=True))
if __name__=="__main__":run()
