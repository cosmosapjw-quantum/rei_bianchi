#!/usr/bin/env python3
"""Original 26-event 3-point vs 5-point sampled residual sensitivity, 3-moment bounds.

This only checks time quadrature on a specified sample path, not rigorous LTE.
"""
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path
N=46080
D="4b5d69ef35f9a5c954417d9e2b1460d435523d328ea7c4bac89587dac5ab8352"
S="d5474b5c2b8dbb96bad28da2aaca5fcffd78e7c7d91901ec7c4e04d776e5adc5"
C=("x_HI","x_HeI","r_HeIII","logT")
W3=(1/6,0,4/6,0,1/6)
W5=(1/12,4/12,2/12,4/12,1/12)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for x in iter(lambda:f.read(4<<20),b""):h.update(x)
 return h.hexdigest()
def need(q,s):
 if not q:raise ValueError("QUADRATURE_SOURCE_"+s)
def main(a):
 need(sha(a.raw)==D and sha(a.science)==S,"PINNED_SHA")
 source=json.load(open(a.science))
 dt=source["original_proper_tick_seconds"]
 out={"schema":"REI_F05_160_162_ACTUAL_SOURCE_QUADRATURE_SENSITIVITY_V1",
     "original_source_raw_sha256":D,"source_public_json_sha256":S,
     "four_source_coordinates":list(C),"sample_quadrature_is_certified_continuum_error":False,
     "actual_source_photon_moment_rank":3,"segments":[]}
 with gzip.open(a.raw,"rt",newline="") as f:
  rows=csv.DictReader(f)
  for seg,(ta,tb) in enumerate(((160,161),(161,162))):
   q3=[[0.]*N for _ in range(4)]
   q5=[[0.]*N for _ in range(4)]
   for k,site in enumerate((0,.25,.5,.75,1)):
    for node in range(N):
     row=next(rows)
     need(int(row["interval_a"])==ta and int(row["interval_b"])==tb and int(row["cell"])==node,"SOURCE_ORDER")
     for j,key in enumerate(C):
      rate=float(row["res_"+key])
      q3[j][node]+=dt*W3[k]*rate
      q5[j][node]+=dt*W5[k]*rate
   metrics=[]
   for j,key in enumerate(C):
    difference=[x-y for x,y in zip(q3[j],q5[j])]
    difmax=max(abs(v) for v in difference)
    finer=max(abs(x) for x in q5[j])
    metrics.append({"coordinate":key,
        "three_point_max_abs":max(abs(x) for x in q3[j]),
        "five_point_max_abs":finer,
        "three_minus_five_max_abs":difmax,
        "relative_max_difference_to_five_max":difmax/finer if finer else None,
        "different_under_quadrature":difmax>0})
    need(abs(finer-source["epochs"][seg]["sampled_simpson_max_abs_residual_by_coord"][j])<3e-15,"EXPECTED_SIMPSON")
   sites=source["epochs"][seg]["source_samples"]
   first=sites[0];last=sites[-1]
   moments=("global_S_HI","global_S_HeI","global_S_HeII")
   logchanges={k:math.log(last[k]/first[k]) for k in moments}
   out["segments"].append({"source_original_ticks":[ta,tb],
      "original_proper_seconds":dt,
      "discrete_sampled_residual_quadrature":metrics,
      "original_global_photon_absorber_log_moment_change":logchanges,
      "fixed_external_forcing_exact_Dg_log_change_upper_conditional":max(abs(z) for z in logchanges.values()),
      "original_external_forcing_is_time_dependent":True,
      "source_26event_binding_derivative_start_end_erg_s":[first["global_original_Bdot_erg_s"],last["global_original_Bdot_erg_s"]],
      "source_26event_gas_derivative_start_end_erg_s":[first["global_original_Udot_erg_s"],last["global_original_Udot_erg_s"]]})
 with gzip.open(a.raw,"rt",newline="") as count_input:
  need(sum(1 for _ in count_input)-1==10*N,"EXACT_RAW_ROW_COUNT")
 out["scientific_limit"]="3vs5_point_stability_is_not_quadrature_error_bound_not_continuum_LTE"
 p=Path(a.output);need(not p.exists(),"NO_OVERWRITE");p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"quadrature_sensitivity":"NUMERICALLY_CHECKED",
   "source_rows":10*N,
   "delta3v5_per_interval":[max(x["three_minus_five_max_abs"] for x in z["discrete_sampled_residual_quadrature"]) for z in out["segments"]],
   "moment_log_change_max":[z["fixed_external_forcing_exact_Dg_log_change_upper_conditional"] for z in out["segments"]],
   "sha256":sha(p)}))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for n in ("raw","science","output"):p.add_argument("--"+n,required=True)
 main(p.parse_args())
