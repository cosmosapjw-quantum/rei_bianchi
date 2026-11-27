#!/usr/bin/env python3
"""Native REI-F05 H/He electron increment bridge. No new IVP or UVB owner."""
import argparse,csv,gzip,hashlib,io,json,math
from fractions import Fraction as Q
from pathlib import Path
Y=Q(79,1000)
SRC_SHA="f20ae64ff11765c6d3d09b2a728ad648630353bd8fefaa1595b1867051932b85"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","SCRIPT_SELF_SHIELDING_AUDITOR","RECOMBINATION_WEIGHTED_AUDITOR")
KINDS=("original_full_increment","original_twohalf_increment","joint_input_cancelled_defect")
def digest(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def endpoint(row,s,k,side):
 x=float(row[f"{s}_{k}_{side}"])
 if not math.isfinite(x):raise ValueError("nonfinite source")
 return Q.from_float(x)
def calc(row,k):
 intervals={}
 for s in ("x_HII","x_HeII","x_HeIII"):
  a,b=(endpoint(row,s,k,side) for side in ("lower","upper"))
  if a>b:raise ValueError("inverted source interval")
  intervals[s]=(a,b)
 h=intervals["x_HII"]
 he=tuple(Y*(intervals["x_HeII"][i]+2*intervals["x_HeIII"][i]) for i in (0,1))
 e=tuple(h[i]+he[i] for i in (0,1))
 return h,he,e
def out(x,upper):
 return format(math.nextafter(float(x),math.inf if upper else -math.inf),".17g")
def main(src,dst):
 files=[src/("rei-f05-common-parent-original26-"+n)/"REI_ORIGINAL26_COMMON_PARENT_INCREMENT_46080.csv.gz" for n in LANES]
 if any(not p.is_file() or digest(p)!=SRC_SHA for p in files):
  raise ValueError("required REI PR348 original source identity missing")
 for lane,source in zip(LANES,files):
  evidence=json.loads((source.parent/"RESULT.json").read_text())
  if (evidence["original_shape_lane"]!=lane or
      evidence["csv_sha256"]!=SRC_SHA or
      evidence["original_state_array_sha256"]!=STATE_SHA or
      evidence["original_accepted_tick"]!="160/131072" or
      evidence["original_nodes"]!=46080 or
      evidence["original_set_ledgers"]["evaluated_ledgers"]!=14 or
      not evidence["original_set_ledger_pass"] or
      evidence["canonical_delta"]!=0):
   raise ValueError("original REI PR348 certificate metadata mismatch")
 dst.mkdir(parents=True,exist_ok=True)
 output=dst/"REI_F05_H_HE_ELECTRON_46080.csv.gz"
 labels=("H_full","He_full","e_full","He_twohalf","e_twohalf","He_defect","e_defect")
 counts=dict.fromkeys(("H_negative","He_positive","e_negative","He_H_opposed","e_defect_contains_zero"),0)
 extrema={n:[None,None] for n in labels}
 maxima={n:Q(0) for n in labels}
 n=0
 with gzip.open(files[0],"rt",newline="") as original,open(output,"wb") as raw:
  rd=csv.DictReader(original)
  if len(rd.fieldnames or [])!=30:raise ValueError("unexpected 30-column source")
  with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0,compresslevel=6) as compressed:
   with io.TextIOWrapper(compressed,encoding="utf8",newline="") as text:
    columns=["node"]+[a+"_"+b for a in labels for b in ("lower","upper")]
    wr=csv.DictWriter(text,fieldnames=columns,lineterminator="\n")
    wr.writeheader()
    for row in rd:
     if int(row["node"])!=n:raise ValueError("nonsequential original node")
     if not math.isfinite(float(row["source_tick160_parent_lnT_center"])):
      raise ValueError("nonfinite temperature source")
     h,he,e=calc(row,KINDS[0])
     _,heh,eh=calc(row,KINDS[1])
     _,hed,ed=calc(row,KINDS[2])
     values=dict(zip(labels,(h,he,e,heh,eh,hed,ed)))
     line={"node":n}
     for name,(lo,hi) in values.items():
      if lo>hi:raise AssertionError("derived interval order")
      line[name+"_lower"]=out(lo,False)
      line[name+"_upper"]=out(hi,True)
      bounds=extrema[name]
      bounds[0]=lo if bounds[0] is None else min(lo,bounds[0])
      bounds[1]=hi if bounds[1] is None else max(hi,bounds[1])
      maxima[name]=max(maxima[name],abs(lo),abs(hi))
     wr.writerow(line)
     counts["H_negative"]+=int(h[1]<0)
     counts["He_positive"]+=int(he[0]>0)
     counts["e_negative"]+=int(e[1]<0)
     counts["He_H_opposed"]+=int(h[1]<0 and he[0]>0)
     counts["e_defect_contains_zero"]+=int(ed[0]<=0<=ed[1])
     n+=1
 if n!=46080:raise ValueError("original 46,080 nodes absent")
 summary={"schema":"BASS_HE_REI_F05_NATIVE_ELECTRON_BRIDGE_20261101",
 "original_rei_pr":348,"original_rei_ci_run":41292070383,
 "original_rei_source_csv_sha256":SRC_SHA,"original_state_array_sha256":STATE_SHA,
 "original_lanes_identical_sha256":True,"unique_physical_nodes":n,
 "physics":"delta_ne/N_H = delta_xHII + (79/1000)*(delta_xHeII+2*delta_xHeIII)",
 "interval_basis":"Exact Fraction from original IEEE754 endpoints; one outward ULP for derived serialized binary64 endpoints; original enclosure validity inherited from REI #348",
 "counts":counts,
 "ranges_per_H":{k:{"lower":float(v[0]),"upper":float(v[1]),"max_abs":float(maxima[k])} for k,v in extrema.items()},
 "output_sha256":digest(output),"new_ivps":0,"new_observations":0,
 "central_rei":"28/88_REPORTED","rei_physical_fast":"4/7_REPORTED",
 "bass_he_physical":"14/18_REPORTED","canonical_delta":0,
 "RUX03":"SPECTRAL_OWNER_UNBOUND","RUX04":"NOT_ADMITTED","production":"HOLD",
 "consumer_scope":"same-original-F05-clock electron increment source; not an F08 matched-history or observed Thomson optical depth"}
 (dst/"RESULT.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
 print(json.dumps(summary,sort_keys=True))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--source-root",type=Path,required=True)
 p.add_argument("--output-dir",type=Path,required=True)
 a=p.parse_args()
 main(a.source_root,a.output_dir)
