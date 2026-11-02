#!/usr/bin/env python3
"""Independent standard-library audit of true [161,162] original-source Rust EOS.

No import of producer, original worker, source generator, NumPy or Rust crate.
Reads all actual 46,080 original-source physical rows and Rust result rows,
verifies every H/He electron, ionization-potential and kinetic-energy formula.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path

N=46080; EV=1.602176634e-12;KB=1.380649e-16
CHI=(13.598434599702,24.587389011,54.417760)
SOURCE_PARENT_SHA="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
SOURCE_NEXT_SHA="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
SOURCE_INPUT_SHA="119a7c846b941ace7c2a452b234f4faacf76031136a5312d8264dc833c2b5bb0"
SOURCE_RUST_SHA="e41f612239aa83000cd1713df308b2c7277e20b71040678ed69c15f5ee43a81f"
RUST_JSON_SHA="8a10a20221588eaef386b17c7cb4038cfb99666ebdadd3976c1f04fa2510f8a2"
SRC_BOUND="63fedc5926e4c2c8f56ce2805aeb4086838ead1c1accde1c526f66315625fb32"
EPS=2.220446049250313e-16
IDXS=set((0,1,5,9,23,79,255,511,1023,2047,4095,8191,12287,16383,20000,24575,
          28671,32767,36900,40000,42000,44000,45000,46079))

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def check(v,msg):
 if not v:raise AssertionError("REI_F05_RUST_BLIND_AUDIT_"+msg)
def near(a,b,scale=0.0):
 return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=64*EPS*max(abs(a),abs(b),scale,1e-300)

def main(args):
 expect=[(args.source,SOURCE_INPUT_SHA),(args.rust,SOURCE_RUST_SHA),
        (args.rust_json,RUST_JSON_SHA),(args.primary,SOURCE_NEXT_SHA),
        (args.recomb,SOURCE_NEXT_SHA),(args.shield,SOURCE_NEXT_SHA),
        (args.original_receipt,SRC_BOUND),(args.parent,SOURCE_PARENT_SHA)]
 for path,ref in expect:check(sha(path)==ref,"EXACT_SOURCE_BYTES_"+path.name)
 r=json.loads(args.original_receipt.read_text())
 z=json.loads(args.rust_json.read_text())
 inp=json.loads(args.input_lock.read_text())
 check(r["status"]=="SOURCE_NATIVE_TICK161_ACTUALLY_CONSUMED_IN_NEXT_MAP","ORIGINAL_MAP_EXECUTED")
 check(r["original_14_ledgers_include_zero"] is True,"ORIGINAL_14_LEDGER")
 check(r["original_table_event_count"]==0 and len(r["actual_original_26event_full_half_maps"])==3,"THREE_MAPS")
 check(r["source_parent_tick161_sha256"]==SOURCE_PARENT_SHA,"ACTUAL_PARENT_SOURCE")
 check(r["source_candidate_state_tick162_sha256"]==SOURCE_NEXT_SHA,"ACTUAL_NEXT_SOURCE")
 check(max(r["original_V2_common_parent_local_defect_four_coordinates"].values())<2e-4,"FROZEN_LOCAL_GATE")
 check(max(r["original_width_four_coordinates"].values())<2e-3,"FROZEN_WIDTH_GATE")
 check(r["canonical_delta"]==0 and r["production"]=="HOLD","OFFICIAL_NOT_CHANGED")
 check(inp["input_rows"]==N and inp["input_file_sha256"]==SOURCE_INPUT_SHA,"GENERATOR_LOCK")
 check(z["source_rows"]==N and z["production"]=="HOLD","RUST_SCOPE")
 check(z["electron_interval_misses"]==0 and z["thermal_interval_misses"]==0,"RUST_SOURCE_OUT_OF_CONE")
 sums={k:[] for k in ("ne161","ne162","b161","b162","u161","u162")}
 signs={"definite_decrease":0,"definite_increase":0,"ambiguous":0}
 max_rel=0.;max_delta_parent_scaled=0.;witness=[]
 with args.source.open(newline="") as f,args.rust.open(newline="") as g:
  rs=csv.DictReader(f);rout=csv.DictReader(g)
  count=0
  for idx,(s,t) in enumerate(zip(rs,rout,strict=True)):
   check(idx<N and int(s["node"])==idx and int(t["node"])==idx,"ROW_ALIGNMENT")
   H=float(s["N_H"]);He=float(s["N_He"])
   HII=float(s["N_HII161_mid"]);HeII=float(s["N_HeII161_mid"]);HeIII=float(s["N_HeIII161_mid"])
   T=float(s["T161_mid_K"])
   hlo,hhi=(float(s["N_HII162_"+q]) for q in ("lo","hi"))
   hel,heh=(float(s["N_HeII162_"+q]) for q in ("lo","hi"))
   he3l,he3h=(float(s["N_HeIII162_"+q]) for q in ("lo","hi"))
   tl,th=(float(s["T162_"+q+"_K"]) for q in ("lo","hi"))
   check(H>0 and He>0 and T>0 and 0<=HII<=H and 0<=hlo<=hhi<=H,"H_CONE")
   check(0<=HeII and 0<=HeIII and HeII+HeIII<=He*(1+2e-12),"HE161_CONE")
   check(0<=hel<=heh and 0<=he3l<=he3h and heh+he3h<=He*(1+2e-12),"HE162_CONE")
   check(0<tl<=th,"T_CONE")
   H2=(hlo+hhi)/2;He2=(hel+heh)/2;He32=(he3l+he3h)/2;T2=(tl+th)/2
   ne0=HII+HeII+2*HeIII;ne1=H2+He2+2*He32
   b0=EV*(CHI[0]*HII+CHI[1]*(HeII+HeIII)+CHI[2]*HeIII)
   b1=EV*(CHI[0]*H2+CHI[1]*(He2+He32)+CHI[2]*He32)
   u0=1.5*KB*(H+He+ne0)*T
   u1=1.5*KB*(H+He+ne1)*T2
   calc={"ne161":ne0,"ne162":ne1,"b161":b0,"b162":b1,"u161":u0,"u162":u1}
   keymap={"ne161":"Ne161_mid","ne162":"Ne162_mid",
           "b161":"B161_mid_erg","b162":"B162_mid_erg",
           "u161":"U161_mid_erg","u162":"U162_mid_erg"}
   for k,a in calc.items():
    got=float(t[keymap[k]])
    check(near(got,a),"RUST_EOS_"+k+"_"+str(idx))
    max_rel=max(max_rel,abs(got-a)/max(abs(got),abs(a),1e-300))
    sums[k].append(a)
   for name,a,b,old,new in (("ne",ne0,ne1,"DeltaNe_mid","ne"),
                              ("B",b0,b1,"DeltaB_mid_erg","b"),
                              ("U",u0,u1,"DeltaU_mid_erg","u")):
    observed=float(t[old])
    check(near(observed,b-a,abs(a)+abs(b)),"RUST_DELTA_"+name)
    max_delta_parent_scaled=max(max_delta_parent_scaled,
               abs(observed-(b-a))/max(abs(a)+abs(b),1e-300))
   ne_lo=hlo+hel+2*he3l
   ne_hi=hhi+heh+2*he3h
   u_lo=1.5*KB*(H+He+ne_lo)*tl
   u_hi=1.5*KB*(H+He+ne_hi)*th
   check(ne_lo<=ne1<=ne_hi or (near(ne1,ne_lo) or near(ne1,ne_hi)),"NE_INTERVAL")
   check(u_lo<=u1<=u_hi or (near(u1,u_lo) or near(u1,u_hi)),"U_INTERVAL")
   if ne_hi<ne0:signs["definite_decrease"]+=1
   elif ne_lo>ne0:signs["definite_increase"]+=1
   else:signs["ambiguous"]+=1
   if idx in IDXS:
    witness.append([idx,ne0,ne1,ne1-ne0,b0,b1,b1-b0,u0,u1,u1-u0,ne_lo,ne_hi,u_lo,u_hi])
   count+=1
 check(count==N and len(witness)==24,"COMPLETE_SOURCE")
 check(signs["definite_decrease"]==z["definitely_decreasing_electron_cells"] and
       signs["definite_increase"]==z["definitely_increasing_electron_cells"] and
       signs["ambiguous"]==z["sign_ambiguous_cells"],"RUST_CELL_SIGNS")
 extensive={k:float(math.fsum(vals)) for k,vals in sums.items()}
 deltas={n:extensive[n+"162"]-extensive[n+"161"] for n in ("ne","b","u")}
 for key,rust_key in (("ne161","source_ne161_mid"),("ne162","source_ne162_mid"),
                       ("b161","source_B161_mid_erg"),("b162","source_B162_mid_erg"),
                       ("u161","source_U161_mid_erg"),("u162","source_U162_mid_erg")):
  expected=float(z[rust_key]);got=extensive[key]
  check(near(expected,got),"RUST_GLOBAL_"+key)
 for key,k in (("ne","delta_ne_mid"),("b","delta_B_mid_erg"),("u","delta_U_mid_erg")):
  q=deltas[key];p=float(z[k]);base=abs(extensive[key+"161"])+abs(extensive[key+"162"])
  check(near(q,p,base),"RUST_GLOBAL_DELTA_"+key)
 # The producer's outer intervals must enclose all representative midpoints.
 for key,fromkey in (("ne","Ne"),("b","B"),("u","U")):
  low,high=r["source_conditional_delta_outer_intervals"][fromkey]
  check(low<=deltas[key]<=high,"PARENT_SOURCE_OUTER_INTERVAL_"+key)
 sample=args.out_dir/"REAL_24CELL_T161_T162_RUST_WITNESS.csv"
 args.out_dir.mkdir(parents=True,exist_ok=True)
 with sample.open("w",newline="") as f:
  wr=csv.writer(f,lineterminator="\n")
  wr.writerow(("cell","Ne161","Ne162","DeltaNe","B161_erg","B162_erg","DeltaB_erg",
              "U161_erg","U162_erg","DeltaU_erg","Ne162_lo","Ne162_hi",
              "U162_lo_erg","U162_hi_erg"))
  wr.writerows(witness)
 result={
  "schema":"REI_F05_ACTUAL_TICK161_PARENT_TO_TICK162_SOURCE_RUST_INDEPENDENT_AUDIT_V1",
  "source_rows":N,"original_realizations":1,
  "old_source_tick161_sha256":SOURCE_PARENT_SHA,
  "source_next_tick162_SHA256":SOURCE_NEXT_SHA,
  "original_source_three_lanes_next_state_exact_SHA256":True,
  "rust_input_original_source_sha256":SOURCE_INPUT_SHA,
  "rust_output_full_46080_sha256":SOURCE_RUST_SHA,
  "rust_summary_sha256":RUST_JSON_SHA,
  "original_map_receipt_sha256":SRC_BOUND,
  "original_14_ledger_zero_inclusion":"PASS",
  "original_fixed_error_limit":2e-4,"original_fixed_width_limit":2e-3,
  "rust_eos_source_full_46080_max_rel":max_rel,
  "rust_eos_source_full_46080_max_delta_normalized_to_parent":max_delta_parent_scaled,
  "rust_cell_electron_sign_classes":signs,
  "independent_source_aggregate":extensive,
  "independent_source_midpoint_delta":deltas,
  "original_HHe_eV_photo_thermal_constants":{"KB_erg_K":KB,"EV_erg":EV,
        "HI_eV":CHI[0],"HeI_eV":CHI[1],"HeII_eV":CHI[2]},
  "witness_rows":len(witness),"witness_csv_sha256":sha(sample),
  "independent_BLIND_referee":"SAME_AUTHOR_DISJOINT_STDLIB_FULL_ROW_AUDITOR",
  "no_inferred_continuum_error":True,
  "no_original_production_history_changed":True,
  "official_F05_accepted_tick":"160/131072","tick161_official":False,
  "tick162_official":False,"central_DAG":"28/88","production":"HOLD"}
 out=args.out_dir/"RUST_INDEPENDENT_AUDIT.json"
 out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"audit":"PASS","full_source_cells":N,"source_14_ledgers":"PASS",
     "max_original_RustEos_relative":max_rel,
     "max_delta_parent_scaled":max_delta_parent_scaled,
     "signs":signs,"material_midpoint_delta":deltas,
     "audit_sha256":sha(out)},indent=2),flush=True)

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 for n in ("source","rust","rust_json","primary","recomb","shield","original_receipt",
           "parent","input_lock","out_dir"):
  ap.add_argument("--"+n,required=True,type=Path)
 main(ap.parse_args())
