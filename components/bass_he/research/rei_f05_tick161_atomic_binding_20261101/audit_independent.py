#!/usr/bin/env python3
"""Separate source-conditional F05 latent-energy numerical referee.
No import of latent_energy.py, only original compressed source/preview and output.
"""
import csv,gzip,hashlib,json,math
from pathlib import Path
BASE=Path(__file__).resolve().parent
S=BASE/"source_inputs"
O=BASE/"results"
EV=1.602176634e-12
EH=13.598434599702
EHE1=24.587389011
EHE2=54.41776
def rows(path):
 with gzip.open(path,"rt",newline="") as f:
  yield from csv.DictReader(f)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def audit():
 vals={k:[[],[]] for k in ("dB_H","dB_He","dB_total","dNe","B161","U161")}
 source=rows(S/"REI_ORIGINAL26_COMMON_PARENT_INCREMENT_46080.csv.gz")
 physical=rows(S/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz")
 output=rows(O/"ORIGINAL_REI_F05_TICK161_H_HE_LATENT_ENERGY_46080.csv.gz")
 max_rel=0.;count=0
 for inc,prev,out in zip(source,physical,output):
  if int(inc["node"])!=count or int(prev["node"])!=count or int(out["node"])!=count:
   raise ValueError("source rows not aligned")
  nh=float(prev["source_H_nuclei_N_lower"])
  he=float(prev["source_He_nuclei_N_lower"])
  if not (.0789999999998<he/nh<.0790000000002):raise ValueError("F05 helium abundance changed")
  def delta(s,j):return float(inc[f"{s}_original_twohalf_increment_"+j])
  for side in ("lower","upper"):
   dH=delta("x_HII",side);dA=delta("x_HeII",side);dB=delta("x_HeIII",side)
   h=nh*EH*dH*EV
   h1=he*EHE1*(dA+dB)*EV
   h2=he*EHE2*dB*EV
   helu=math.fsum((h1,h2))
   total=math.fsum((h,helu))
   dne=math.fsum((nh*dH,he*(dA+2*dB)))
   trial={"dB_H":h,"dB_He":helu,"dB_total":total,"dNe":dne}
   for k,v in trial.items():
    q=float(out[k+"_"+side])
    diff=abs(q-v)
    rel=diff/max(abs(q),abs(v),1e-300)
    max_rel=max(max_rel,rel)
    if not rel<=3e-12:raise AssertionError("independent source-value inconsistency "+k+" row "+str(count))
    vals[k][0 if side=="lower" else 1].append(v)
   for key in ("B161","U161"):
    vals[key][0 if side=="lower" else 1].append(float(out[key+"_"+side]))
   # H+He and helium first+second closure on actual artifact.
   he_sum=float(out["dB_He_first_"+side])+float(out["dB_He_second_"+side])
   total_sum=float(out["dB_H_"+side])+float(out["dB_He_"+side])
   if abs(he_sum-float(out["dB_He_"+side]))>max(1e-280,(abs(float(out["dB_He_first_"+side]))+abs(float(out["dB_He_second_"+side])))*3e-15):
    raise AssertionError("helium ionization-stage double-count error")
   if abs(total_sum-float(out["dB_total_"+side]))>max(1e-280,(abs(float(out["dB_H_"+side]))+abs(float(out["dB_He_"+side])))*3e-15):
    raise AssertionError("total binding decomposition error")
  count+=1
 if count!=46080:raise ValueError("original source row count mismatch")
 result=json.loads((O/"RESULT.json").read_text())
 if result["official_tick161"]!="NOT_ACCEPTED" or result["canonical_delta"]!=0:
  raise ValueError("scientific admission illegally changed")
 global_rels={}
 for k,components in vals.items():
  for i,side in enumerate(("lower","upper")):
   got=math.fsum(components[i])
   target=result["global_intervals"][k][side]
   err=abs(got-target)/max(abs(target),1e-280)
   global_rels[k+"_"+side]=err
   if err>1e-11:raise AssertionError("global source total mismatch "+k)
 proof={"schema":"BASS_HE_REI_F05_INDEPENDENT_ORIGINAL_SOURCE_HE_LATENT_REFEREE_V1",
    "same_author_separate_numerical_code":True,
    "source_46080_rows_and_all_energy_outputs":"PASS",
    "original_preview_and_increment_source_owner":"REI352_PLUS_REI350",
    "maximum_independent_source_relative_error":max_rel,
    "maximum_global_independent_relative_error":max(global_rels.values()),
    "output_sha256":digest(O/"ORIGINAL_REI_F05_TICK161_H_HE_LATENT_ENERGY_46080.csv.gz"),
    "source_sample_count":count,"original_state_161":"NOT_ACCEPTED",
    "claim":"ionization-potential storage only, not net radiative escape or gas heat"}
 (O/"INDEPENDENT_AUDIT.json").write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n")
 print(json.dumps(proof,sort_keys=True))
if __name__=="__main__":audit()
