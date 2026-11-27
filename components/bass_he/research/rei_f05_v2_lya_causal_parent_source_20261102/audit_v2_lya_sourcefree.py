#!/usr/bin/env python3
"""Independent SOURCE-FREE stdlib reconstruction of 92,160 real original
REI V2 HeII Ly-alpha emission quadrature records. Not original IVP replay.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path
N=46080
INTERVALS=((160,161),(161,162))
COLUMNS=("left_tick","right_tick","node","escaped_llya_energy_lo_erg",
 "escaped_llya_energy_hi_erg","escaped_llya_photons_lo",
 "escaped_llya_photons_hi","stage1_escaped_rate_lo_erg_s",
 "stage1_escaped_rate_hi_erg_s","final1_escaped_rate_lo_erg_s",
 "final1_escaped_rate_hi_erg_s","stage2_escaped_rate_lo_erg_s",
 "stage2_escaped_rate_hi_erg_s","final2_escaped_rate_lo_erg_s",
 "final2_escaped_rate_hi_erg_s","full_escaped_energy_upper_erg",
 "source_delta_B_cell_mid_erg","source_delta_U_cell_mid_erg")
E=40.813320*1.602176634e-12
GAMMA=1.-1./math.sqrt(2.)
def digest(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def require(x,name):
 if not x:raise ValueError("BASS_HE_V2_LYA_INDEPENDENT_"+name)
def diff(a,b,label,tol=8e-13):
 require(math.isfinite(a) and math.isfinite(b),label+"_NONFINITE")
 den=max(abs(a),abs(b),1e-290)
 delta=abs(a-b)/den
 if delta>tol:raise ArithmeticError("INDEPENDENT_"+label+"_DIFFERENCE_"+str(delta))
 return delta
def run(csv_path,science_path,out):
 csv_path=Path(csv_path);science_path=Path(science_path);out=Path(out)
 source=json.loads(science_path.read_text())
 require(digest(csv_path)==source["output_csv_sha256"],"CSV_INPUT_SHA_MISMATCH")
 require(source["source_ticks161_162_official"] is False and source["canonical_delta"]==0
  and source["production"]=="HOLD","FALSE_RESEARCH_SOURCE_ADMISSION")
 require(source["original_source_method"] if False else source["source_original_method"].endswith("CORRELATED_INCREMENT"),
         "SOURCE_PROVENANCE_MISSING")
 require(len(source["two_research_source_intervals"])==2 and source["science_rows"]==2*N,"ORIGINAL_V2_GRAIN")
 require(source["source_escape_branch_f_interval"]==[0.1,1.0],"NATIVE_OTS_F_INTERVAL_CHANGED")
 require(source["source_original_predecessor_all_3_lane_physical_realizations"]==1,"FALSE_3_INDEPENDENT_UNIVERSES")
 require(math.isclose(source["source_HeII_Lya_E_erg"],E,rel_tol=1e-14),"LYA_LINE_ENERGY_MISMATCH")
 rows=0;max_res=0.;max_photon=0.;summaries=[]
 with gzip.open(csv_path,"rt",newline="") as f:
  reader=csv.DictReader(f)
  require(tuple(reader.fieldnames or ())==COLUMNS,"COLUMNS_CHANGED")
  for a,b in INTERVALS:
   vals={k:[] for k in ("esc_lo","esc_hi","photon_hi","B_mid","U_mid")}
   orig=next(x for x in source["two_research_source_intervals"] if x["ticks"]==[a,b])
   h=orig["duration_s"]/2.
   for idx in range(N):
    try:row=next(reader)
    except StopIteration:raise ValueError("TRUNCATED_ORIGINAL_V2_ROWS")
    require((int(row["left_tick"]),int(row["right_tick"]),int(row["node"]))==(a,b,idx),
            "RESEARCH_TIME_NODE_ORDER")
    def v(name):return float(row[name])
    rates=[v("stage1_escaped_rate_lo_erg_s"),
           v("stage1_escaped_rate_hi_erg_s"),
           v("final1_escaped_rate_lo_erg_s"),
           v("final1_escaped_rate_hi_erg_s"),
           v("stage2_escaped_rate_lo_erg_s"),
           v("stage2_escaped_rate_hi_erg_s"),
           v("final2_escaped_rate_lo_erg_s"),
           v("final2_escaped_rate_hi_erg_s")]
    require(all(math.isfinite(x) for x in rates),"NONFINITE_V2_RATE")
    reference_hi=max(0.,h*math.fsum(((1.-GAMMA)*rates[1],GAMMA*rates[3],
                                   (1.-GAMMA)*rates[5],GAMMA*rates[7])))
    reference_lo=max(0.,h*math.fsum(((1.-GAMMA)*rates[0],GAMMA*rates[2],
                                   (1.-GAMMA)*rates[4],GAMMA*rates[6])))
    value_hi=v("escaped_llya_energy_hi_erg")
    value_lo=v("escaped_llya_energy_lo_erg")
    max_res=max(max_res,diff(reference_hi,value_hi,"PER_CELL_ORIGINAL_QUADRATURE"))
    max_res=max(max_res,diff(reference_lo,value_lo,"PER_CELL_LOWER"))
    photon_hi=v("escaped_llya_photons_hi")
    photon_lo=v("escaped_llya_photons_lo")
    require(0<=value_lo<=value_hi and 0<=photon_lo<=photon_hi,"INVALID_HEII_ESC_SOURCE_INTERVAL")
    require(v("full_escaped_energy_upper_erg")>=0,"INVALID_FULL_REFERENCE")
    max_photon=max(max_photon,diff(photon_hi*E,value_hi,"PHOTON_ENERGY_IDENTITY",2e-14))
    max_photon=max(max_photon,diff(photon_lo*E,value_lo,"PHOTON_ENERGY_IDENTITY_LOWER",2e-14))
    for key,x in (("esc_lo",value_lo),("esc_hi",value_hi),("photon_hi",photon_hi),
                  ("B_mid",v("source_delta_B_cell_mid_erg")),
                  ("U_mid",v("source_delta_U_cell_mid_erg"))):vals[key].append(x)
    rows+=1
   total={key:math.fsum(values) for key,values in vals.items()}
   for key,name,index in (("esc_lo","esc_local_Lya_energy_erg",0),
                          ("esc_hi","esc_local_Lya_energy_erg",1),
                          ("photon_hi","esc_local_Lya_photons",1),
                          ("B_mid","original_V2_source_Bmid_erg",None),
                          ("U_mid","original_V2_source_Umid_erg",None)):
    val=orig[name] if index is None else orig[name][index]
    max_res=max(max_res,diff(total[key],float(val),"GLOBAL_"+str(a)+"_"+key,tol=6e-12))
   require(orig["original_native_14_ledger_zero_included"] and orig["exact_research_V2_endpoint_array_identity"],
           "NATIVE_ACCEPTANCE_NOT_SOURCED")
   require(max(orig["source_V2_common_parent_defects"].values())<2e-4
           and max(orig["source_original_public_widths"].values())<2e-3,
           "NATIVE_SOURCE_GATE_TAMPER")
   summaries.append({"tick":[a,b],"source_escaped_upper_erg":total["esc_hi"],
                     "source_photon_upper":total["photon_hi"],
                     "source_mid_delta_B":total["B_mid"],
                     "source_mid_delta_U":total["U_mid"]})
  require(next(reader,None) is None,"EXTRA_SOURCE_ROWS")
 require(rows==2*N,"NO_92160_SOURCE_ROWS")
 total_energy=math.fsum(v["source_escaped_upper_erg"] for v in summaries)
 total_num=math.fsum(v["source_photon_upper"] for v in summaries)
 max_res=max(max_res,diff(total_energy,source["source_interval_local_Lya_energy_upper_erg"],"TOTAL_LYA"))
 max_res=max(max_res,diff(total_num,source["source_interval_photon_upper_total"],"TOTAL_N"))
 result={"schema":"BASS_HE_REI_ORIGINAL_F05_V2_LYA_STDLIB_INDEPENDENT_AUDIT_V1",
  "source_csv_SHA256":digest(csv_path),
  "source_json_SHA256":digest(science_path),
  "original_source_rows_verified":rows,
  "native_source_SDIRK2_events_per_row":4,
  "source_interval_records":summaries,
  "maximum_scaled_original_source_quadrature_reconstruction_discrepancy":max_res,
  "maximum_scaled_photon_energy_consistency_discrepancy":max_photon,
  "source_f_interval":[0.1,1.0],
  "original_tick161_162_official":False,
  "source_geometry_or_bianchi_null_transport":"NOT_IMPLEMENTED",
  "distinct_author_blind_referee":"NOT_RUN",
  "same_author_independent_stdlib":"PASS_SCOPED",
  "production":"HOLD","canonical_delta":0,
  "status":"PASS_INDEPENDENT_ORIGINAL_F05_V2_HEII_LYA_92160"}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":result["status"],
       "source_rows":rows,"max_quadrature_error":max_res,
       "max_photon_energy_error":max_photon,
       "source_emission_upper_erg":total_energy,
       "audit_SHA256":digest(out)},sort_keys=True),flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--csv",type=Path,required=True)
 p.add_argument("--science",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 run(a.csv,a.science,a.out)
