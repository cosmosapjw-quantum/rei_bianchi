#!/usr/bin/env python3
"""Independent standard-library readback of published 0-160 accepted
native HeII Ly-alpha source-time quadrature. Not original REI source replay.
"""
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path

N=46080
INTERVALS=((0,64),(64,128),(128,160))
CHI=54.417760
EV=1.602176634e-12

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()

def check(cond,msg):
 if not cond:raise ValueError("SOURCE_FREE_HEII_LYA_"+msg)

def finite(x):return math.isfinite(x)

def audit(csvpath,sciencepath,out):
 c=Path(csvpath);s=Path(sciencepath);out=Path(out)
 q=json.loads(s.read_text())
 check(sha(c)==q["derived_CSV_SHA256"],"SOURCE_CSV_SHA_DRIFT")
 check(q["original_REI_source_head"]=="70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00","ORIGINAL_HEAD_DRIFT")
 check(q["input_REC195_source_zip_sha256"]=="ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657","SOURCE_ZIP_DRIFT")
 check(q["original_accepted_source_ticks"]==[0,64,128,160],"ORIGINAL_TIME_DRIFT")
 check(q["original_source_accepted_intervals"] and len(q["original_source_accepted_intervals"])==3,"SOURCE_TIME_COUNT")
 check(q["original_tick161"]=="NOT_ACCEPTED" and q["canonical_delta"]==0 and q["production"]=="HOLD","FALSE_OWNER_ADMISSION")
 check(q["source_branch_f_range"]==[0.1,1.0],"SOURCE_ESCAPE_BRANCH_INVARIANT")
 e=0.75*CHI*EV
 check(abs(q["line_energy_erg"]-e)<1e-12*e,"HEII_LYA_ENERGY_MISMATCH")
 sums=[];rows=0;max_energy_rel=0.0;negative=0
 with gzip.open(c,"rt",newline="") as handle:
  reader=csv.DictReader(handle)
  fields=set(reader.fieldnames or [])
  required={"tick_left","tick_right","cell","escaped_photon_lo","escaped_photon_hi",
      "escaped_energy_lo_erg","escaped_energy_hi_erg","fullstep_energy_hi_erg",
      "twohalf_vs_full_center_energy_erg"}
  check(required.issubset(fields),"MISSING_SOURCE_COLUMNS")
  for a,b in INTERVALS:
   ener_lo=[];ener_hi=[];nlo=[];nhi=[];full=[];difference=[]
   for j in range(N):
    try:row=next(reader)
    except StopIteration:raise ValueError("SOURCE_TRUNCATED_ROWS")
    check((int(row["tick_left"]),int(row["tick_right"]),int(row["cell"]))==(a,b,j),"ORIGINAL_CELL_TIME_ORDER")
    z={k:float(row[k]) for k in required if k not in ("tick_left","tick_right","cell")}
    check(all(finite(v) for v in z.values()),"NONFINITE_SOURCE_PHYSICS")
    e0,e1=z["escaped_energy_lo_erg"],z["escaped_energy_hi_erg"]
    n0,n1=z["escaped_photon_lo"],z["escaped_photon_hi"]
    check(0<=e0<=e1 and 0<=n0<=n1,"NEGATIVE_PHYSICAL_ESCAPE")
    check(z["fullstep_energy_hi_erg"]>=0,"NEGATIVE_FULL_SOURCE_ENERGY")
    for ph,erg in ((n0,e0),(n1,e1)):
     rel=abs(ph*e-erg)/max(abs(erg),abs(ph*e),1e-290)
     check(rel<6e-15,"SOURCE_LINE_PHOTON_ENERGY_NONCONSERVED")
     max_energy_rel=max(max_energy_rel,rel)
    if n0==0:negative+=1
    ener_lo.append(e0);ener_hi.append(e1);nlo.append(n0);nhi.append(n1)
    full.append(z["fullstep_energy_hi_erg"])
    difference.append(z["twohalf_vs_full_center_energy_erg"])
    rows+=1
   expected=next(t for t in q["original_source_accepted_intervals"] if t["ticks"]==[a,b])
   for values,key in (
      (ener_lo,"integrated_escaped_line_energy_twohalf_erg"),
      (ener_hi,"integrated_escaped_line_energy_twohalf_erg"),
      (nlo,"integrated_escaped_line_photons_twohalf"),
      (nhi,"integrated_escaped_line_photons_twohalf"),
      (full,"integrated_escaped_line_energy_full_erg")):
    idx=0 if values is ener_lo or values is nlo else 1
    if values is full:idx=1
    want=expected[key][idx]
    got=math.fsum(values)
    check(abs(got-want)<=4e-12*max(abs(got),abs(want),1e-250),
          "SOURCE_TIME_INTEGRAL_MISMATCH_"+str(a)+"_"+str(b)+"_"+key)
   sums.append({"ticks":[a,b],"energy_upper_erg":math.fsum(ener_hi),
                "photon_upper":math.fsum(nhi),"zero_lower_rows":sum(v==0 for v in nlo),
                "one_step_full_upper_erg":math.fsum(full),
                "full_twohalf_midpoint_signed_difference_erg":math.fsum(difference)})
  check(next(reader,None) is None,"UNEXPECTED_EXTRA_ROWS")
 check(rows==138240 and q["source_genuine_physics_rows"]==rows,"ORIGINAL_ROW_COUNT_DRIFT")
 total_erg=math.fsum(x["energy_upper_erg"] for x in sums)
 total_n=math.fsum(x["photon_upper"] for x in sums)
 for value,key in ((total_erg,"integrated_three_interval_escaped_energy_erg"),
                   (total_n,"integrated_three_interval_escaped_photons")):
  want=q[key][1]
  check(abs(value-want)<=4e-12*max(value,want,1e-250),"FULL_0_160_SOURCE_SUM_DRIFT")
 res={"schema":"BASS_HE_F05_ACCEPTED_LYA_INDEPENDENT_SOURCEFREE_AUDIT_V1",
      "source_CSV_sha256":sha(c),"science_JSON_sha256":sha(s),
      "original_event_source_cells_per_interval":N,"intervals":sums,
      "independent_rows_checked":rows,"line_energy_erg":e,
      "max_source_photon_energy_relative_residual":max_energy_rel,
      "total_escaped_line_photons_upper":total_n,
      "zero_lower_rows":negative,
      "source_f_interval":[0.1,1.0],
      "independent_author":"NO_SAME_AUTHOR_ALGORITHM",
      "original_IVP_replay":"NOT_PERFORMED_BY_AUDIT",
      "canonical_delta":0,"result":"PASS_ALL_138240_SOURCE_LYA_PHOTON_ENERGY_ROWS"}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"result":res["result"],"rows":rows,
     "source_energy_upper_erg":total_erg,"source_photons_upper":total_n,
     "max_energy_relative":max_energy_rel,"audit_sha256":sha(out)},sort_keys=True),flush=True)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--csv",required=True,type=Path)
 p.add_argument("--science",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 audit(a.csv,a.science,a.out)
