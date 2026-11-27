#!/usr/bin/env python3
"""Real original REI photon-source budget stress test for R53 deuterium photo process.

No fictitious photon allocation or claims that original 26-event group-resolved
RT included the added D sink. Source original 17 forcing photon emission and
absorption rates are compared with actual R53 46k-cell DI ionization counts.
"""
import csv,gzip,hashlib,io,json,math
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
ROOT=Path(__file__).resolve().parent
SRC=ROOT/"sources"
RESULTS=ROOT/"results"
N=46080
ETA=2.5e-5
COLS=[
"node","original_H_nuclei","source_HI_fraction_160","source_HI_fraction_preview161",
"original_gamma_HI_integrated_first_tick",
"cloned_original_HI_photo_ionizations_per_cell",
"caseB_DI_photo_ionizations_per_cell_initial_Dneutral",
"caseB_DI_photo_ionizations_per_cell_initial_Dionized",
"caseB_DI_recombinations_per_cell_initial_Dneutral",
"caseB_DI_recombinations_per_cell_initial_Dionized",
"DI_photon_demand_over_HI_photo_cloned_initial_Dneutral",
"DI_photon_demand_over_HI_photo_cloned_initial_Dionized",
"DI_photo_ratio_local_G1_relative_not_defined"
]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def percentiles(x):
 arr=np.asarray(x)
 return {k:float(np.percentile(arr,q)) for k,q in [("min",0),("p05",5),("median",50),("p95",95),("max",100)]}

def run():
 contract=json.loads((ROOT/"SOURCE_CONTRACT.json").read_text())
 for name,expected in contract["original_REI_CX_relevant_source_shas"].items():
  if sha(SRC/name)!=expected:raise ValueError("ORIGINAL_SOURCE_LOCK_MISMATCH_"+name)
 a=json.loads((RESULTS/"R53_RESULTS.json").read_text())
 original_gz=RESULTS/"R53_ORIGINAL_REI_F05_D_PHOTO_CX_46080.csv.gz"
 if sha(original_gz)!=a["output_SHA256"][original_gz.name]:
  raise ValueError("R53_COMPUTED_SOURCE_ID_CHANGED")
 with (SRC/"canonical_time_resolved_forcing_nodes.csv").open(newline="") as f:
  forcing=[r for r in csv.DictReader(f) if int(r["interval_index"])==0]
 if len(forcing)!=17 or any(float(x["z_mid"])!=5.95 for x in forcing):
  raise ValueError("FIRST_ORIGINAL_PHOTON_FORCING_CHANGED")
 times=np.array([float(x["time_s"]) for x in forcing])
 t0=160*a["numerical"]["original_tick_dt_s"]
 t1=161*a["numerical"]["original_tick_dt_s"]
 sources={k:PchipInterpolator(times,[float(x[k]) for x in forcing],extrapolate=False)
   for k in ("Gamma_HI_s-1","emission_rate_s-1_cMpc-3",
   "front_absorption_rate_s-1_cMpc-3",
   "absorption_G1_s-1_cMpc-3","absorption_G2a_s-1_cMpc-3","absorption_G2b_s-1_cMpc-3",
   "N_G1_cMpc-3","N_G2a_cMpc-3","N_G2b_cMpc-3")}
 # Γ_HI(s) PCHIP is cubic on the first source knot, with x_HII(s) linear,
 # so Gauss16 integrates Γ_HI*(1-x(s)) exactly within rounding in that segment.
 q,w=np.polynomial.legendre.leggauss(16)
 sq=.5*(q+1)
 gw=.5*w
 I0=float(np.sum(gw*sources["Gamma_HI_s-1"](t0+sq*(t1-t0)))*(t1-t0))
 I1=float(np.sum(gw*sq*sources["Gamma_HI_s-1"](t0+sq*(t1-t0)))*(t1-t0))
 assert abs(I0-sources["Gamma_HI_s-1"].integrate(t0,t1))<1e-14*I0
 data={k:[] for k in COLS}
 sums={name:0. for name in ("H_cloned_absorbed","D_photo_neutral","D_photo_ionized","D_recomb_neutral","D_recomb_ionized")}
 with gzip.open(original_gz,"rt",newline="") as f:
  c=csv.DictReader(f)
  for idx,r in enumerate(c):
   if idx!=int(r["node"]):raise ValueError("PHOTON_REI_NODES_MISMATCH")
   H=float(r["nH_cm3"])*float(r["proper_volume_cm3"])
   x0=float(r["source_xHII160"])
   x1=float(r["preview_xHII161"])
   HI_abs=H*((1-x0)*I0-(x1-x0)*I1)
   d0=float(r["caseB_D_photoionizations_count_neutral"])
   d1=ETA*H*float(r["caseB_D_photoionizations_per_D_ionized"])
   R0=ETA*H*float(r["caseB_D_recombinations_per_D_neutral"])
   R1=ETA*H*float(r["caseB_D_recombinations_per_D_ionized"])
   if HI_abs<=0 or any(x<-1e-8 for x in (d0,d1,R0,R1)):
    raise ArithmeticError("SOURCED_PHOTO_COUNTS_INVALID")
   ratio0=d0/HI_abs
   ratio1=d1/HI_abs
   row={
    "node":idx,"original_H_nuclei":H,
    "source_HI_fraction_160":1-x0,
    "source_HI_fraction_preview161":1-x1,
    "original_gamma_HI_integrated_first_tick":I0,
    "cloned_original_HI_photo_ionizations_per_cell":HI_abs,
    "caseB_DI_photo_ionizations_per_cell_initial_Dneutral":d0,
    "caseB_DI_photo_ionizations_per_cell_initial_Dionized":d1,
    "caseB_DI_recombinations_per_cell_initial_Dneutral":R0,
    "caseB_DI_recombinations_per_cell_initial_Dionized":R1,
    "DI_photon_demand_over_HI_photo_cloned_initial_Dneutral":ratio0,
    "DI_photon_demand_over_HI_photo_cloned_initial_Dionized":ratio1,
    "DI_photo_ratio_local_G1_relative_not_defined":"NOT_DEFINED_NO_CELL_G1_OWNER"
   }
   for k in COLS:data[k].append(row[k])
   for k,v in dict(H_cloned_absorbed=HI_abs,D_photo_neutral=d0,D_photo_ionized=d1,
        D_recomb_neutral=R0,D_recomb_ionized=R1).items():sums[k]+=v
 if len(data["node"])!=N:raise ValueError("SOURCE_46080_PHOTON_ROWS_NOT_PRESENT")
 compare={}
 for name in ("emission_rate_s-1_cMpc-3","front_absorption_rate_s-1_cMpc-3",
       "absorption_G1_s-1_cMpc-3","absorption_G2a_s-1_cMpc-3","absorption_G2b_s-1_cMpc-3"):
  compare[name]=float(sources[name].integrate(t0,t1))
 for name in ("N_G1_cMpc-3","N_G2a_cMpc-3","N_G2b_cMpc-3"):
  compare[name]=float(sources[name](t0))
 if not(all(v>0 for v in compare.values()) and I0>0):raise ValueError("SOURCE_PHOTON_FORCING_NONPOSITIVE")
 owner_emission=compare["emission_rate_s-1_cMpc-3"]
 g1=compare["absorption_G1_s-1_cMpc-3"]
 thin_source=SUM_CX_R52_REI_HI=a["numerical"]["source_gamma_HI_one_tick_exposure"]
 output=RESULTS/"R53_OWNER_PHOTON_BUDGET_46080.csv.gz"
 with output.open("wb") as raw:
  with gzip.GzipFile(filename="",fileobj=raw,mode="wb",compresslevel=6,mtime=0) as gz:
   with io.TextIOWrapper(gz,encoding="utf8",newline="") as txt:
    wr=csv.writer(txt,lineterminator="\n");wr.writerow(COLS)
    for idx in range(N):
     wr.writerow([int(data[k][idx]) if k=="node" else (data[k][idx] if isinstance(data[k][idx],str) else format(data[k][idx],".17g")) for k in COLS])
 report={
  "schema":"WU_R53_SOURCE_NATIVE_FIRST_TICK_ADDED_DI_PHOTON_BUDGET_STRESS_TEST_V1",
  "modeled_photon_field":"EXPLICITLY_FROZEN_ORIGINAL_HI_CLONED_TO_DI_APPROXIMATION",
  "original_17_node_time_and_four_group_forcing_exact_SHA":contract["original_REI_CX_relevant_source_shas"]["canonical_time_resolved_forcing_nodes.csv"],
  "original_REI_first_tick_source_duration_seconds":t1-t0,
  "sourced_HI_gamma_time_integral":I0,
  "native_owner_forcing_one_comoving_Mpc_cube":True,
  "original_W_node_sum":1.0,
  "native_source_integrated_counts_per_cMpc3":compare,
  "derived_source_cell_HI_and_DI_photo_counts":sums,
  "photon_demand_ratios":{
   "DI_neutral_over_source_emission":sums["D_photo_neutral"]/owner_emission,
   "DI_neutral_over_original_G1_absorption":sums["D_photo_neutral"]/g1,
   "DI_neutral_over_original_HI_gamma_cloned_absorption":sums["D_photo_neutral"]/sums["H_cloned_absorbed"],
   "DI_ionized_over_source_emission":sums["D_photo_ionized"]/owner_emission,
   "DI_neutral_over_original_G1_instant_reservoir":sums["D_photo_neutral"]/compare["N_G1_cMpc-3"],
  },
  "original_real_source_cells":N,
  "original_same_source_cell_DI_neutral_over_HI_photo_ratio":percentiles(data["DI_photon_demand_over_HI_photo_cloned_initial_Dneutral"]),
  "N_cells_DI_neutral_photo_gt10pct_HI_cloned_source":int(np.count_nonzero(np.asarray(data["DI_photon_demand_over_HI_photo_cloned_initial_Dneutral"])>.1)),
  "N_cells_DI_neutral_photo_gt_HI_cloned_source":int(np.count_nonzero(np.asarray(data["DI_photon_demand_over_HI_photo_cloned_initial_Dneutral"])>1.)),
  "origin_isotope_photo_cross_section":"SAVIN_EQ11_SOURCED_HI_GAMMA_APPROX_NOT_EXACT_D_ABSORPTION",
  "photons_debited_from_native_REI_owner":"NO",
  "interpretation":"SCOPED_DI_ADDITIONAL_PHOTON_SINK_STRESS_NOT_ACTUAL_CONSERVING_REI_PHOTON_SOLVER",
  "new_source_sink_gt1percent_original_emission":bool(sums["D_photo_neutral"]/owner_emission>.01),
  "not_a_proved_violation_of_photon_budget":True,
  "next_physical_action":"REI_OWNER_NATIVE_G1_ABSORPTION_ALLOCATION_PLUS_DI_SPECIFIC_PHOTO_CROSS_SECTION",
  "source_full_physics_sha":a["output_SHA256"][original_gz.name],
  "source_photon_stress_csv_SHA256":sha(output),
  "canonical_DAG":{"WU":"34/49","REI_central":"28/88","delta":0},
  "original_F05_tick161":"NOT_ACCEPTED"
 }
 (RESULTS/"R53_PHOTON_BUDGET.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"source_46080_cells":N,"gross_DI_photons_neutral":sums["D_photo_neutral"],
   "gross_DI_photons_ionized":sums["D_photo_ionized"],
   "owner_emission":owner_emission,"owner_G1_absorption":g1,
   "H_owner_cloned_absorption":sums["H_cloned_absorbed"],
   "ratios":report["photon_demand_ratios"],
   "DI_gtHI_cell_count":report["N_cells_DI_neutral_photo_gt_HI_cloned_source"],
   "filename":str(output),"sha256":sha(output)},sort_keys=True))
 return report
if __name__=="__main__":run()
