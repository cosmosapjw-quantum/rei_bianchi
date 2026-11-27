#!/usr/bin/env python3
"""Second source-free full 92160-cell four-source-site OTS reabsorption audit.
Not original REI 26-event solver replay, no claim of interval-upper correlations.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path
E=40.813320; EV=1.602176634e-12
CHIH=13.598434599702;CHIHE=24.587389011
G=1.-1./math.sqrt(2.0)
N=46080
TIMES=((160,161),(161,162))
CHANNELS=("emitted","absorbed_H","absorbed_HeI","escaped")
EN_CHANNELS=("chemical","photoheat","heat_original","escape_original")
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def require(x,msg):
 if not x:raise ValueError("BASS_HE_PR154_SOURCE_FREE_"+msg)
def near(a,b,tag,rtol=2e-12):
 if not (math.isfinite(a) and math.isfinite(b)):
  raise ArithmeticError("NONFINITE_"+tag)
 err=abs(a-b)/max(abs(a),abs(b),1e-280)
 if err>rtol:raise ArithmeticError("MISMATCH_"+tag+"_"+str(err))
 return err
def row_num(r,key):return float(r[key])
def verify(data,science,parent,out):
 data=Path(data);science=Path(science);parent=Path(parent);out=Path(out)
 j=json.loads(science.read_text());base=json.loads(parent.read_text())
 require(j["source_csv_sha256"]==sha(data),"SOURCE_DATA_HASH")
 require(j["parent_escaped_source_science"]==sha(parent),"PARENT_SCIENCE_HASH")
 require(j["source_authority_head"]=="645437697d915da45147071e266bc47937e76f6c","SOURCE_HEAD")
 require(j["original_V2_tick161_SHA256"]=="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823","V2_T161_HASH")
 require(j["original_V2_tick162_SHA256"]=="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b","V2_T162_HASH")
 require(j["canonical_delta"]==0 and j["production"]=="HOLD"
         and j["original_tick161_162_official"] is False,"FALSE_OWNER_ADMISSION")
 require(j["actual_original_event_heat_preserved"] and j["re_absorbed_OTS_photons_already_in_source_population_RHS"],"DOUBLE_COUNT_RISK")
 require(j["source_f_interval"]==[0.1,1.] and j["physical_source_rows"]==2*N,"SOURCE_F_OR_NODES")
 require(len(j["per_microtick_original_site_branches"])==2,"SOURCE_INTERVAL_COUNT")
 require(base["source_escape_branch_f_interval"]==[0.1,1.] and base["science_rows"]==2*N,"PARENT_F_OR_NODES")
 cols=["left_tick","right_tick","source_node"]
 for name in (*CHANNELS,*EN_CHANNELS):cols.extend((name+"_lo",name+"_hi"))
 for step in ("half1","half2"):
  for event in ("stage_event","final_event"):
   for name in CHANNELS:cols.extend((step+"_"+event+"_"+name+"_lo",step+"_"+event+"_"+name+"_hi"))
 rows=0; maxrate=0.;maxenergy=0.;overlaps=0;outcomes=[]
 with gzip.open(data,"rt",newline="") as f:
  reader=csv.DictReader(f)
  require(reader.fieldnames==cols,"COLUMNS_CHANGED")
  for left,right in TIMES:
   raw=next(x for x in base["two_research_source_intervals"] if x["ticks"]==[left,right])
   target=next(x for x in j["per_microtick_original_site_branches"] if x["ticks"]==[left,right])
   h=float(raw["duration_s"])/2.
   acc={c+"_"+side:[] for c in (*CHANNELS,*EN_CHANNELS) for side in ("lo","hi")}
   for i in range(N):
    try:r=next(reader)
    except StopIteration:raise ValueError("TRUNCATED_ORIGINAL_SOURCE")
    require((int(r["left_tick"]),int(r["right_tick"]),int(r["source_node"]))==(left,right,i),"SOURCE_ORDER")
    for name in CHANNELS:
     for s in ("lo","hi"):
      rates=[row_num(r,f"{step}_{event}_{name}_{s}")
        for step in ("half1","half2") for event in ("stage_event","final_event")]
      expected=h*math.fsum(((1.-G)*rates[0],G*rates[1],(1.-G)*rates[2],G*rates[3]))
      expected=max(expected,0.)
      actual=row_num(r,f"{name}_{s}")
      maxrate=max(maxrate,near(expected,actual,f"QUADRATURE_{name}_{s}"))
    for name in (*CHANNELS,*EN_CHANNELS):
     lo=row_num(r,name+"_lo");hi=row_num(r,name+"_hi")
     require(lo>=0 and hi>=lo and math.isfinite(lo) and math.isfinite(hi),"INTERVAL_NONPHYSICAL_"+name)
     acc[name+"_lo"].append(lo);acc[name+"_hi"].append(hi)
    e_lo,e_hi=(row_num(r,"emitted_"+x) for x in ("lo","hi"))
    sum_lo=sum(row_num(r,c+"_lo") for c in ("absorbed_H","absorbed_HeI","escaped"))
    sum_hi=sum(row_num(r,c+"_hi") for c in ("absorbed_H","absorbed_HeI","escaped"))
    require(e_lo<=sum_hi*(1+3e-14) and e_hi*(1+3e-14)>=sum_lo,"NUMBER_INTERVAL_NOT_OVERLAP")
    h_lo,h_hi=[row_num(r,"absorbed_H_"+s) for s in ("lo","hi")]
    he_lo,he_hi=[row_num(r,"absorbed_HeI_"+s) for s in ("lo","hi")]
    qlo,qhi=[row_num(r,"photoheat_"+s) for s in ("lo","hi")]
    hlo,hhi=[row_num(r,"heat_original_"+s) for s in ("lo","hi")]
    elo,ehi=[row_num(r,"escaped_"+s) for s in ("lo","hi")]
    selo,sehi=[row_num(r,"escape_original_"+s) for s in ("lo","hi")]
    blo,bhi=[row_num(r,"chemical_"+s) for s in ("lo","hi")]
    # intervals overlap, do NOT equate separately optimized upper endpoints
    q_to_heat_lo=EV*((E-CHIH)*h_lo+(E-CHIHE)*he_lo)
    q_to_heat_hi=EV*((E-CHIH)*h_hi+(E-CHIHE)*he_hi)
    b_calc_lo=EV*(CHIH*h_lo+CHIHE*he_lo)
    b_calc_hi=EV*(CHIH*h_hi+CHIHE*he_hi)
    energy_em_lo=EV*E*e_lo;energy_em_hi=EV*E*e_hi
    sum_energy_lo=blo+qlo+selo
    sum_energy_hi=bhi+qhi+sehi
    require(qlo<=hhi*(1+5e-14) and hlo<=qhi*(1+5e-14),"ORIGINAL_HEAT_INTERVAL_NONOVERLAP")
    require(elo*EV*E<=sehi*(1+5e-14) and selo<=ehi*EV*E*(1+5e-14),"ESCAPED_ENERGY_NONOVERLAP")
    require(blo<=b_calc_hi*(1+5e-14) and b_calc_lo<=bhi*(1+5e-14),"BINDING_INTERVAL_NONOVERLAP")
    require(qlo<=q_to_heat_hi*(1+5e-14) and q_to_heat_lo<=qhi*(1+5e-14),"PHOTOHEAT_INTERVAL_NONOVERLAP")
    require(sum_energy_lo<=energy_em_hi*(1+1e-13) and energy_em_lo<=sum_energy_hi*(1+1e-13),"PHOTON_ENERGY_INTERVAL_NONOVERLAP")
    maxenergy=max(maxenergy,near(hhi,q_to_heat_hi,"HEAT_UPPER",5e-12),
                  near(bhi,b_calc_hi,"BINDING_UPPER",5e-12))
    rows+=1;overlaps+=1
   aggregate={name:[math.fsum(acc[name+"_lo"]),math.fsum(acc[name+"_hi"])]
              for name in (*CHANNELS,*EN_CHANNELS)}
   for name in aggregate:
    for idx in (0,1):
     maxrate=max(maxrate,near(aggregate[name][idx],target[name][idx],"AGGREGATE_"+name+"_"+str(idx),6e-12))
   maxrate=max(maxrate,near(aggregate["escape_original"][1],raw["esc_local_Lya_energy_erg"][1],
                   "ORIGINAL_ESCAPE_OWNER_"+str(left),6e-12))
   outcomes.append({"ticks":[left,right],**aggregate})
  require(next(reader,None) is None,"EXTRA_ROWS")
 require(rows==2*N and overlaps==rows,"ALL_ORIGINAL_CELLS_EVALUATED")
 audit={
  "schema":"BASS_HE_F05_V2_HHE_LYA_LOCAL_OTS_SOURCEFREE_AUDIT_V1",
  "source_input_csv_sha256":sha(data),"source_input_json_sha256":sha(science),
  "parent_original_escape_json_sha256":sha(parent),
  "rows_checked":rows,
  "original_twohalf_microticks":[[160,161],[161,162]],
  "source_4_event_sites_per_microtick":True,
  "max_scaled_integral_reconstruction_error":maxrate,
  "max_scaled_chemical_photoheat_upper_error":maxenergy,
  "number_and_energy_interval_overlap_cells":overlaps,
  "interval_upper_not_algebraically_co_realisable":True,
  "original_local_absorption_already_in_chemistry":True,
  "producer_microtick_sums":outcomes,
  "native_subagent":"NOT_RUN","distinct_author_referee":"NOT_RUN",
  "canonical_delta":0,"production":"HOLD",
  "status":"PASS_SOURCE_FREE_92160_NATIVE_OTS_LOCAL_H_HEI_FEEDBACK"
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(audit,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":audit["status"],"rows":rows,
   "max_integral_scaled":maxrate,"max_energy_scaled":maxenergy,
   "audit_sha256":sha(out)},sort_keys=True),flush=True)
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--csv",required=True,type=Path)
 a.add_argument("--science",required=True,type=Path)
 a.add_argument("--parent",required=True,type=Path)
 a.add_argument("--out",required=True,type=Path)
 x=a.parse_args();verify(x.csv,x.science,x.parent,x.out)
