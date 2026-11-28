#!/usr/bin/env python3
"""Independent SOURCE-FREE standard-library audit of actual accepted source
HeII Ly-alpha first-flight capacity conditional on frozen local homogeneous gas.
Uses an independent algorithm and recomputes all 138,240 event rows.
This does NOT establish actual null transport or source-cell spatial geometry.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path
C=2.99792458e10;EV=1.602176634e-12
E=40.81332;CHI_H=13.598434599702;CHI_HE=24.587389011
N=46080;INTERVALS=((0,64),(64,128),(128,160))
FIELDS=("left_tick","right_tick","node","source_escape_upper_photons",
"kappa_HI_end_cm_inv","kappa_HeI_end_cm_inv","kappa_HI_end_upper_cm_inv",
"kappa_HeI_end_upper_cm_inv","tau_light_horizon_end",
"same_window_absorbed_upper_reference_photons","same_window_absorbed_HI_upper_reference",
"same_window_absorbed_HeI_upper_reference","photo_binding_upper_reference_erg",
"primary_heat_upper_reference_erg","box_upper_total_absorbed_photons",
"uniform_emission_upper_reference_photons")
def require(ok,msg):
 if not ok:raise ValueError("PR152_INDEPENDENT_SOURCEFREE_"+msg)
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def equal(a,b,tag,rel=3e-12):
 require(math.isfinite(a) and math.isfinite(b),tag+"_NONFINITE")
 scale=max(abs(a),abs(b),1e-285)
 if abs(a-b)>rel*scale:raise ArithmeticError("SOURCE_REFERENCE_MISMATCH_"+tag+f" {a} vs {b}")
 return abs(a-b)/scale
def uniform(t):
 if t<1e-4:return t*(.5-t/6+t*t/24-t**3/120+t**4/720)
 return 1.+math.expm1(-t)/t
def check(producer_csv,science_json,out):
 p=Path(producer_csv);j=Path(science_json);x=json.loads(j.read_text())
 require(sha(p)==x["derived_CSV_SHA256"],"DATASET_SHA_DRIFT")
 require(x["original_source_quadrature_nodes_not_spatial_ray_cells"] is True,"FALSE_SPATIAL_GRID")
 require(x["original_causal_geometry_not_identified"] is True,"INVENTED_SPATIAL_GEOMETRY")
 require(x["source_f_interval"]==[0.1,1.0] and x["original_tick161"]=="NOT_ACCEPTED","SOURCE_PHYSICS_MISADMITTED")
 require(x["canonical_delta"]==0 and x["production"]=="HOLD","FALSE_CANONICAL")
 require(x["source_original_data_rows"]==3*N,"ROW_COUNT_SCHEMA")
 require(len(x["intervals"])==3 and x["source_original_accepted_ticks"]==[0,64,128,160],"SOURCE_ACCEPTED_TIMES")
 maxres=0.;max_ident=0.;aggregates=[];count=0
 with gzip.open(p,"rt",newline="") as stream:
  rdr=csv.DictReader(stream)
  require(tuple(rdr.fieldnames or ())==FIELDS,"SOURCE_FIELDS")
  for a,b in INTERVALS:
   h=float(next(t for t in x["intervals"] if t["accepted_ticks"]==[a,b])["source_duration_s"])
   totals={k:[] for k in ("source","absorbed","HI","HeI","binding","electron_heat","capacity_box","uniform")}
   for node in range(N):
    try:r=next(rdr)
    except StopIteration:raise ValueError("TRUNCATED_ORIGINAL_SOURCE_ROWS")
    require((int(r["left_tick"]),int(r["right_tick"]),int(r["node"]))==(a,b,node),"SOURCE_TIME_NODE_ORDER")
    s=float(r["source_escape_upper_photons"])
    kh=float(r["kappa_HI_end_cm_inv"]);khe=float(r["kappa_HeI_end_cm_inv"])
    kh_hi=float(r["kappa_HI_end_upper_cm_inv"]);khe_hi=float(r["kappa_HeI_end_upper_cm_inv"])
    require(all(math.isfinite(z) and z>=0 for z in (s,kh,khe,kh_hi,khe_hi)),"SOURCE_POSITIVITY")
    require(kh<=kh_hi*(1+1e-14) and khe<=khe_hi*(1+1e-14),"SOURCE_POINT_OUTSIDE_ACCEPTED_BOX")
    opacity=kh+khe
    tau=C*h*opacity
    expabs=-math.expm1(-tau)
    ref=s*expabs
    fH=kh/opacity if opacity>0 else 0.
    fHe=khe/opacity if opacity>0 else 0.
    hi=ref*fH;he=ref*fHe
    binding=EV*(CHI_H*hi+CHI_HE*he)
    heat=EV*((E-CHI_H)*hi+(E-CHI_HE)*he)
    cap=s*(-math.expm1(-C*h*(kh_hi+khe_hi)))
    unif=s*uniform(tau)
    actual=[float(r[k]) for k in FIELDS[8:]]
    expect=[tau,ref,hi,he,binding,heat,cap,unif]
    for label,observed,want in zip(FIELDS[8:],actual,expect):
     maxres=max(maxres,equal(observed,want,label))
    max_ident=max(max_ident,equal(binding+heat,E*EV*(hi+he),"PHOTOENERGY_IDENTITY",rel=8e-15))
    require(0<=expabs<=1 and 0<=unif+1e-280<=ref+1e-280 and cap+1e-280>=ref-1e-280,
            "PHOTON_CAPACITY_ORDER")
    for key,v in zip(totals, (s,ref,hi,he,binding,heat,cap,unif)):totals[key].append(v)
    count+=1
   sums={k:math.fsum(v) for k,v in totals.items()}
   src=next(t for t in x["intervals"] if t["accepted_ticks"]==[a,b])
   correspondence={
      "source":"input_source_escape_upper_photons",
      "absorbed":"right_endpoint_frozen_conditional_absorbed_photons",
      "HI":"right_endpoint_frozen_conditional_absorbed_HI_photons",
      "HeI":"right_endpoint_frozen_conditional_absorbed_HeI_photons",
      "binding":"right_endpoint_frozen_conditional_binding_gain_erg",
      "electron_heat":"right_endpoint_frozen_conditional_primary_electron_heat_erg",
      "capacity_box":"source_box_hi_cap_absorbed_photons",
      "uniform":"uniform_emission_time_reference_absorbed_photons"}
   for key,dst in correspondence.items():
    maxres=max(maxres,equal(sums[key],float(src[dst]),"INTERVAL_"+str(a)+"_"+dst))
   max_ident=max(max_ident,equal(sums["binding"]+sums["electron_heat"],
                                E*EV*sums["absorbed"],"INTERVAL_ENERGY",rel=8e-15))
   aggregates.append({"interval":[a,b],**sums})
  require(next(rdr,None) is None,"EXTRA_SOURCE_ROWS")
 require(count==3*N,"NOT_138240_NODES")
 result={"schema":"BASS_HE_PR152_INDEPENDENT_SOURCEFREE_138240_CAPACITY_AUDIT_V1",
  "original_science_json_sha256":sha(j),"source_dataset_sha256":sha(p),
  "rows_verified":count,"intervals":aggregates,
  "max_abs_relative_reconstruction_error":maxres,
  "max_relative_line_energy_identity_error":max_ident,
  "actual_causal_transfer_claimed":False,
  "source_endpoint_frozen_medium_conditional":True,
  "source_missing_ray_geometry":True,
  "independent_author":"NOT_RUN",
  "same_author_second_implementation":"PASS_SCOPED",
  "canonical_delta":0,"production":"HOLD",
  "status":"INDEPENDENT_RECONSTRUCTION_138240_PASS"}
 p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":result["status"],"rows":count,
  "max_relative_reconstruction":maxres,
  "max_energy_identity":max_ident,
  "audit_sha256":sha(p)},sort_keys=True))
 return result

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--csv",type=Path,required=True)
 p.add_argument("--science",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();check(a.csv,a.science,a.out)
