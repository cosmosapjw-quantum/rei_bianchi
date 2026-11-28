#!/usr/bin/env python3
"""R57 source-free public science summaries and original native 24-cell witnesses."""
from pathlib import Path
import csv,gzip,math,hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parent
FULL=ROOT/"results/R57_ORIGINAL_NATIVE_RHS_HERMITE_DI_46080.csv.gz"
RHS=ROOT/"source_private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz"
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def run():
 data=json.loads((ROOT/"results/R57_RESULTS.json").read_text())
 assert sha(FULL)==data["files"]["sha256"]
 with gzip.open(FULL,"rt") as f:rows=list(csv.DictReader(f))
 assert len(rows)==46080
 ix=np.argsort([float(r["source_nH_proper_cm3"]) for r in rows])[np.linspace(0,46079,24,dtype=int)]
 names=("node","source_nH_proper_cm3","native_HII_tick160","native_dHII_dTick_tick160",
 "H_MATCHED_native_rhs_hermite_DII_tick160",
 "H_MATCHED_owner_point_linear_DII_tick160",
 "ALL_NEUTRAL_native_rhs_hermite_DII_tick160",
 "H_MATCHED_native_rhs_hermite_DI_gross_photo_per_D_160to161",
 "ALL_NEUTRAL_native_rhs_hermite_DI_gross_photo_per_D_160to161")
 w=ROOT/"results/R57_ORIGINAL_SOURCE_WITNESS_24.csv"
 with w.open("w",newline="") as f:
  a=csv.writer(f,lineterminator="\n");a.writerow(names)
  for i in ix:a.writerow([rows[i][k] for k in names])
 # Re-read source old-state endpoint derivatives for direct-coordinate cubic negative control.
 lists={}
 with gzip.open(RHS,"rt") as f:
  for row in csv.DictReader(f):
   t=int(row["accepted_tick"])
   if t in (0,64):lists.setdefault(t,[]).append((float(row["N_HII_point"])/float(row["N_H"]),
      float(row["dN_HII_dt_per_s"])/float(row["N_H"])))
 assert len(lists[0])==len(lists[64])==46080
 D=4871848749.16828;interval=64*D;u=.5
 y=np.array([p[0] for p in lists[0]]);dy=np.array([p[1] for p in lists[0]])
 y1=np.array([p[0] for p in lists[64]]);dy1=np.array([p[1] for p in lists[64]])
 H00=2*u**3-3*u*u+1;H10=u**3-2*u*u+u;H01=-2*u**3+3*u*u;H11=u**3-u*u
 direct=H00*y+H10*interval*dy+H01*y1+H11*interval*dy1
 bad=int(np.count_nonzero(direct>1));upper=float(np.max(direct));lower=float(np.min(direct))
 control=y+interval*dy/3
 obs={"schema":"WU_R57_UNCONSTRAINED_DIRECT_HII_CUBIC_NEGATIVE_TEST","original_REI367_source_rows_checked":2*46080,
   "test_interval":[0,64],"u":0.5,"unconstrained_cubic_x_greater_than_one_cells":bad,
   "unconstrained_cubic_max_x":upper,"unconstrained_cubic_min_x":lower,
   "source_first_Bezier_control_above_one_cells":int(np.count_nonzero(control>1)),
   "mechanism":"Direct interpolation in fraction x can leave [0,1] even with legitimate source endpoint derivatives",
   "repair":"Source-tangent logistic H and softmax He + exact electron nucleus ledger",
   "statement":"A tested interpolation failure, NOT a general mathematical no-go on continuous physical source paths"}
 assert bad==150 and abs(upper-1.0000566889968443)<1e-12
 (ROOT/"results/R57_DIRECT_CUBIC_NEGATIVE_CONTROL.json").write_text(json.dumps(obs,sort_keys=True,indent=2)+"\n")
 public=dict(schema="WU_R57_ORIGINAL_REI_26EVENT_ENDPOINT_RHS_HHE_TO_DI_SOURCE_PUBLIC",
  authority=dict(WU_parent_PR196="2d52baa98bd97b513a2cdad2f2c1fe1b5e9917b0",
   original_REI367="b9cd64afee16dc4c0e74aa39b00c831df626c777",
   original_20col_SHA256=data["source_original_REI367_20field_private_sha256"],
   new_27col_SHA256=data["new_source_original_derivative_27field_sha256"],
   full_46080_DI_SHA256=data["files"]["sha256"]),
  source_evidence=data["native_four_epoch_exact_20field_parity"],
  source_chemistry_consistency=data["accepted_source_derivative_consistency"],
  source_science_results=data["results"],source_y160_differences=data["y160_differences"],
  science_claim_scope=data["scientific_scope"],physical_cells=46080,
  accepted_HHe_ticks=[0,64,128,160],
  original_26event_continuum="NOT_RUN",
  D_initial_conditions="UNRESOLVED_SOURCE_CONDITIONAL",
  source_161="PREVIEW_NOT_ACCEPTED",
  original_D_net_heat="NOT_COMPUTED",
  tests="9/9_NORMAL_AND_9/9_OPTIMIZED",
  same_author_audit=json.loads((ROOT/"results/R57_INDEPENDENT_AUDIT.json").read_text()),
  negative_source_cone_test=obs,
  witness_SHA256=sha(w),
  DAG=dict(WU="34/49",REI_CENTRAL="28/88",REI_WORKING="33/88",FAST="4/7",canonical_delta=0),
  NO_MAIN_MERGE=True,PRODUCTION="HOLD")
 p=ROOT/"results/R57_PUBLIC_SCIENCE.json"
 p.write_text(json.dumps(public,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"WITNESS_SHA256":sha(w),"NEGATIVE_CONTROL":obs,"PUBLIC_SCIENCE_SHA256":sha(p)},sort_keys=True))
if __name__=="__main__":run()
