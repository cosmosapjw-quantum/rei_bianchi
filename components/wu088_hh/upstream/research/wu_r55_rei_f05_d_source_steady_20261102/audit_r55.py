#!/usr/bin/env python3
"""Independent algebra/CSV audit of archived WU R55 46,080 original-source cells.
No import of R54 or R55 simulation code. Same author, not independent reviewer.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math
from pathlib import Path

EV_ERG=1.602176634e-12
ETA_D=2.5e-5
CHI_D_EV=13.6017
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for part in iter(lambda:f.read(1<<20),b""):h.update(part)
 return h.hexdigest()
def audit(out,r54=None):
 out=Path(out)
 data=json.loads((out/"R55_RESULTS.json").read_text())
 fmeta=data["files"]
 for name,h in [(fmeta["physical_full_csv_name"],fmeta["physical_full_csv_sha256"]),
                (fmeta["group_csv_name"],fmeta["group_csv_sha256"]),
                (fmeta["24_cell_witness_name"],fmeta["24_cell_witness_sha256"])]:
  assert sha(out/name)==h,("FILE_SOURCE_CHANGED",name)
 with open(out/fmeta["group_csv_name"],newline="") as f:
  groups=list(csv.DictReader(f))
 assert [x["group"] for x in groups]==["G1","G2a","G2b","G3"]
 E=[float(x["mean_absorbed_photon_energy_eV"]) for x in groups[:3]]
 photo_groups=[[],[],[]]
 count=0;max_population=0.;max_energy=0.;max_electron=0.;max_heat_ratio=0.
 N_heat_gt_pct=0
 with gzip.open(out/fmeta["physical_full_csv_name"],"rt",newline="") as f:
  source=csv.DictReader(f)
  for row in source:
   assert int(row["node"])==count
   count+=1
   value=lambda key:float(row[key])
   nh=value("original_H_N")
   x=value("source_original_xHII160")
   cy=value("CX_equilibrium_initial_y_DII")
   y0=value("full_instantaneous_stationary_initial_y_DII")
   yf=value("FULL_final_y_DII")
   assert nh>0 and .99<x<1. and .99<cy<=1 and .99<y0<=1 and 0<=yf<=1
   p=[value("FULL_photo_"+g+"_per_D") for g in ("G1","G2a","G2b")]
   assert min(p)>=0.
   for i in range(3):
    photo_groups[i].append(ETA_D*nh*p[i])
   cx=value("FULL_CX_per_D")
   rr=value("FULL_RR_per_D")
   eii=value("FULL_EII_per_D")
   pop_res=(yf-y0)-(cx+sum(p)+eii-rr)
   max_population=max(max_population,abs(pop_res))
   electrons_new=ETA_D*(sum(p)+eii-rr)
   electrons_from_balance=value("FULL_Dplus_electrons_per_H_including_initial")-value("FULL_initial_Dplus_electrons_per_H")
   max_electron=max(max_electron,abs(electrons_new-value("FULL_new_electrons_per_H_since_initial")),abs(electrons_new-electrons_from_balance))
   q_ph=ETA_D*EV_ERG*math.fsum(E[i]*p[i] for i in range(3))
   q_binding=ETA_D*CHI_D_EV*EV_ERG*sum(p)
   q_heat=q_ph-q_binding
   max_energy=max(max_energy,abs(q_heat-value("FULL_photo_excess_heat_gross_erg_per_H")),
       abs(q_binding-value("FULL_photo_latent_binding_gross_erg_per_H")),
       abs(q_ph-value("FULL_photo_photon_energy_gross_erg_per_H")))
   ratio=q_heat/abs(value("original_native_F05_deltaU_erg_per_H"))
   assert ratio>=0
   max_heat_ratio=max(max_heat_ratio,abs(ratio-value("FULL_gross_photoheat_over_abs_native_F05_deltaU")))
   N_heat_gt_pct+=int(ratio>.01)
 assert count==46080,("ROW_COUNT",count)
 sums=[math.fsum(x) for x in photo_groups]
 rel=[]
 for i,g in enumerate(groups):
  actual=float(g["FULL_DI_gross_photoevents_per_cMpc3"])
  calc=sums[i] if i<3 else 0.
  rel.append(abs(actual-calc)/max(actual,1.))
  val=float(g["FULL_DI_group_deficit_per_cMpc3"])+float(g["FULL_native_absorption_displaced_per_cMpc3"])
  rel.append(abs(actual-val)/max(actual,1.))
 assert max(rel)<2e-12,("GROUP_PHOTON_LEDGER",rel)
 assert max_population<6e-12,("ISOTOPE_5FLUX_LEDGER",max_population)
 assert max_electron<2e-17,("ELECTRON_LEDGER",max_electron)
 assert max_energy<2e-29,("PHOTON_ENERGY_LEDGER",max_energy)
 assert max_heat_ratio<2e-12,("HEAT_RATIO",max_heat_ratio)
 assert N_heat_gt_pct==data["numeric"]["FULL_photoheat_exceeds_1pct_native_abs_deltaU_cells"]
 assert abs(math.fsum(sums)-data["numeric"]["FULL_gross_DI_photons_per_cMpc3"])/data["numeric"]["FULL_gross_DI_photons_per_cMpc3"]<2e-12
 assert data["REI_original_accepted_tick"]=="160/131072" and data["REI_tick161"]=="PREVIEW_HOLD"
 assert data["DAG"]["WU"]=="34/49" and data["DAG"]["REI_central"]=="28/88"
 assert data["gates"]["historical_D_evolution"]=="NOT_RUN"
 # Verify full modeled D+ is nested between preexisting archived extreme
 # physical trajectories on the SAME original cell and source. This is a
 # numerical comparison only, not an all-parameter monotonicity theorem.
 bracket_misses=0
 if r54 is not None:
  old=Path(r54)/"results/R54_REI_F05_DI_GROUP_CONSERVATIVE_46080.csv.gz"
  with gzip.open(out/fmeta["physical_full_csv_name"],"rt") as f1,gzip.open(old,"rt") as f2:
   for i,(new,ref) in enumerate(zip(csv.DictReader(f1),csv.DictReader(f2))):
    yf=float(new["FULL_final_y_DII"])
    lo=float(ref["DI_initial_neutral_y_final_group_coupled"])
    hi=float(ref["DI_initial_ionized_y_final_group_coupled"])
    if not lo-2e-13<=yf<=hi+2e-13: bracket_misses+=1
  assert bracket_misses==0,("INITIAL_EXTREME_BRACKET_MISSES",bracket_misses)
 summary={"schema":"WU_R55_CROSS_FORMULA_STD_LIB_BLIND_SAME_AUTHOR_AUDIT",
   "rows":count,"source_original_cells":46080,
   "max_group_gross_vs_independent_row_sum_relative":max(rel),
   "max_isotope_population_5flux_residual":max_population,
   "max_initial_electron_correction_ledger_abs":max_electron,
   "max_photo_energy_ledger_erg_per_H":max_energy,
   "max_heat_ratio_independent_deviation":max_heat_ratio,
   "gross_photoheat_materiality_gt_1pct_cells":N_heat_gt_pct,
   "original_extreme_ion_fraction_bracket_misses":bracket_misses,
   "same_author":True,"native_subagent":"NOT_RUN",
   "full_native_26event_solver":"NOT_RUN",
   "result":"PASS_SCOPED_SOURCE_CONDITIONAL"}
 (out/"R55_INDEPENDENT_ALGEBRA_AUDIT.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
 print(json.dumps(summary,sort_keys=True))
 return summary

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,required=True)
 p.add_argument("--r54-root",type=Path)
 a=p.parse_args()
 audit(a.out,a.r54_root)
