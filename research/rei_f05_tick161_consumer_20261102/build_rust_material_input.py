#!/usr/bin/env python3
"""Prepare actual original [161,162] 46k interval physics for historical Rust EOS.

The prior original REI V2 source parent and the next-step state must be
cryptographically source matched. Rust is a *consumer*, NOT a replacement
for original 26-event thermal/radiative integration.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path
import numpy as np

N=46080
SRC161="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
NEXT162="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
SRC366="a27d8b0c4c98b112a42720570a8be77887d1170fb794383d525c7e2f10fa2176"
EV=1.602176634e-12; KB=1.380649e-16
CHI=(13.598434599702,24.587389011,54.417760)
HEADER="node,N_H,N_He,N_HII161_mid,N_HeII161_mid,N_HeIII161_mid,T161_mid_K,N_HII162_lo,N_HII162_hi,N_HeII162_lo,N_HeII162_hi,N_HeIII162_lo,N_HeIII162_hi,T162_lo_K,T162_hi_K"

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def must(c,msg):
 if not c:raise ValueError("REI_TICK161_RUST_INPUT_"+msg)
def sumv(x):return float(math.fsum(float(y) for y in x))
def main(args):
 must(sha(args.source161)==SRC161,"SOURCE_PARENT_SHA")
 must(sha(args.next162)==NEXT162,"NEXT_STATE_SHA")
 must(sha(args.original366)==SRC366,"EARLIER_46K_OWNER_LOCK")
 for name,path in (("primary",args.primary),("recomb",args.recomb),("shield",args.shield)):
  must(sha(path)==NEXT162,"NEXT_OTHER_LANE_"+name)
 with np.load(args.source161,allow_pickle=False) as a,np.load(args.next162,allow_pickle=False) as b:
  pl=a["population_lower"].copy();ph=a["population_upper"].copy()
  zl=a["log_temperature_lower"].copy();zh=a["log_temperature_upper"].copy()
  ql=b["population_lower"].copy();qh=b["population_upper"].copy()
  qzl=b["log_temperature_lower"].copy();qzh=b["log_temperature_upper"].copy()
 must(pl.shape==(N,5) and ql.shape==(N,5),"SHAPES")
 must(np.all(pl>0) and np.all(ql>0) and np.all(pl<=ph) and np.all(ql<=qh),"POSITIVE_SOURCE")
 P=0.5*pl+0.5*ph
 Z=0.5*zl+0.5*zh
 t161=np.exp(Z);t162lo=np.exp(qzl);t162hi=np.exp(qzh)
 total_h=np.empty(N);total_he=np.empty(N)
 original_ne=np.empty(N);original_b=np.empty(N)
 with gzip.open(args.original366,"rt",newline="") as src:
  reader=csv.DictReader(src)
  count=0
  for r in reader:
   i=count
   must(int(r["cell"])==i and i<N,"ORDER")
   total_h[i]=float(r["NH"]);total_he[i]=float(r["NHe"])
   original_ne[i]=float(r["Ne161V2_mid"])
   original_b[i]=float(r["B161V2_mid_erg"])
   count+=1
  must(count==N,"SOURCE_NODES")
 must(np.all(total_h>0) and np.all(total_he>0),"NUCLEI")
 Hlo=ql[:,0]+ql[:,1];Hhi=qh[:,0]+qh[:,1]
 Helo=ql[:,2]+ql[:,3]+ql[:,4];Hehi=qh[:,2]+qh[:,3]+qh[:,4]
 must(np.all(Hlo<=total_h*(1+4e-12)) and np.all(Hhi>=total_h*(1-4e-12)),"H_T162_CONE")
 must(np.all(Helo<=total_he*(1+4e-12)) and np.all(Hehi>=total_he*(1-4e-12)),"HE_T162_CONE")
 ne161=P[:,1]+P[:,3]+2*P[:,4]
 b161=EV*(CHI[0]*P[:,1]+CHI[1]*(P[:,3]+P[:,4])+CHI[2]*P[:,4])
 # The source stored a midpoint of endpoint B rather than B(midpoint P);
 # compare only representation equivalence, not physical solver tolerance.
 must(np.max(np.abs(ne161-original_ne)/np.maximum(abs(original_ne),1e-300))<4e-13,"OWNER_161_NE")
 must(np.max(np.abs(b161-original_b)/np.maximum(abs(original_b),1e-300))<4e-13,"OWNER_161_BINDING")
 must(np.all(t161>0) and np.all(t162lo>0) and np.all(t162lo<=t162hi),"THERMAL_CONE")
 args.private.mkdir(parents=True,exist_ok=True)
 f=args.private/"REI_ORIGINAL_T161_T162_RUST_EOS_INPUT_46080.csv"
 with f.open("w",newline="") as file:
  wr=csv.writer(file,lineterminator="\n")
  wr.writerow(HEADER.split(","))
  for i in range(N):
   wr.writerow([i,total_h[i],total_he[i],P[i,1],P[i,3],P[i,4],t161[i],
       ql[i,1],qh[i,1],ql[i,3],qh[i,3],ql[i,4],qh[i,4],t162lo[i],t162hi[i]])
 receipt={
  "schema":"REI_F05_ORIGINAL_V2_T161_T162_RUST_EOS_SOURCE_INPUT_V1",
  "source_parent_tick161_npz_sha256":SRC161,
  "source_next_tick162_npz_sha256":NEXT162,
  "source_REI_PR366_full_46080_csv_sha256":SRC366,
  "source_3_lanes_tick162_same_complete_npz_SHA":True,
  "input_file_sha256":sha(f),"input_bytes":f.stat().st_size,
  "input_rows":N,"input_columns":len(HEADER.split(",")),
  "original_num_of_realizations":1,
  "original_26event_time_integrator_rust_port":False,
  "source_cone_H_He_T":"PASS_ORIGINAL_INTERVALS",
  "source_owner_midpoint_NE_equivalence_maxrel":float(np.max(np.abs(ne161-original_ne)/original_ne)),
  "source_owner_midpoint_B_equivalence_maxrel":float(np.max(np.abs(b161-original_b)/original_b)),
  "original_official_accept_tick":"160/131072","tick161":"SOURCE_SCOPED_V2_ONLY",
  "tick162":"RESEARCH_NEXT_MAP_ONLY","central_DAG":"28/88","production":"HOLD"
 }
 args.public.mkdir(parents=True,exist_ok=True)
 out=args.public/"RUST_INPUT_LOCK.json"
 out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":"SOURCE_NATIVE_RUST_INPUT_PREPARED","rows":N,
  "input_sha":sha(f),"NE_maxrel":receipt["source_owner_midpoint_NE_equivalence_maxrel"],
  "B_maxrel":receipt["source_owner_midpoint_B_equivalence_maxrel"]},sort_keys=True),flush=True)
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 for name in ("source161","next162","original366","primary","recomb","shield","private","public"):
  ap.add_argument("--"+name,required=True,type=Path)
 main(ap.parse_args())
