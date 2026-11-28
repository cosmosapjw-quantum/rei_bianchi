#!/usr/bin/env python3
"""One independent-formulation source-native R53 blind-style same-author audit.

Read all ORIGINAL sources and physical outputs independently. Compare source-owned
46,080 H/He states and photon budgets, solve 96 scalar four-state D/H equations
with SciPy DOP853 rather than the producer's vectorized RK4.
"""
import csv,gzip,hashlib,json,math,bisect
from pathlib import Path
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
import numpy as np
ROOT=Path(__file__).resolve().parent
S=ROOT/"sources"
R=ROOT/"results"
ETA=2.5e-5
ENG=.0037*1.602176634e-12
MPC_CM=3.085677581491367e24
def SHA(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def main():
 contract=json.loads((ROOT/"SOURCE_CONTRACT.json").read_text())
 for n,exp in contract["original_REI_CX_relevant_source_shas"].items():
  if SHA(S/n)!=exp:raise AssertionError("SOURCE_DRIFT "+n)
 tab=[]
 with open(S/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv") as f:
  for row in csv.DictReader(f):
   tab.append(tuple(float(row[k]) for k in ("T_K","k_forward_cm3_s","k_reverse_cm3_s")))
 assert len(tab)==47
 Ttab=np.array([q[0] for q in tab])
 def rate(T,index):
  j=max(0,min(len(tab)-2,bisect.bisect_right(Ttab,T)-1))
  a,b=tab[j],tab[j+1]
  w=math.log(T/a[0])/math.log(b[0]/a[0])
  return math.exp((1-w)*math.log(a[index])+w*math.log(b[index]))
 def rec(T,kind):
  ll=315614./T
  if kind=="B":return 2.753e-14*ll**1.5/(1+(ll/2.740)**.407)**2.242
  return 1.269e-13*ll**1.503/(1+(ll/.522)**.470)**1.923
 rows=[]
 with open(S/"canonical_time_resolved_forcing_nodes.csv") as f:
  rows=[x for x in csv.DictReader(f) if int(x["interval_index"])==0]
 assert len(rows)==17 and all(float(q["z_mid"])==5.95 for q in rows)
 times=np.array([float(x["time_s"]) for x in rows])
 vals=np.array([float(x["Gamma_HI_s-1"]) for x in rows])
 gamma=PchipInterpolator(times,vals,extrapolate=False)
 dt=(times[-1]-times[0])/131072.
 s0=160*dt
 parent=json.loads((R/"R53_RESULTS.json").read_text())
 if parent["numerical"]["native_real_cells"]!=46080 or parent["original_admission"]!="NOT_GRANTED":
  raise AssertionError("ORIGINAL_REI_CANONICAL_GATE")
 budget=json.loads((R/"R53_PHOTON_BUDGET.json").read_text())
 full=R/"R53_ORIGINAL_REI_F05_D_PHOTO_CX_46080.csv.gz"
 bfile=R/"R53_OWNER_PHOTON_BUDGET_46080.csv.gz"
 assert SHA(full)==parent["output_SHA256"][full.name]
 assert SHA(bfile)==budget["source_photon_stress_csv_SHA256"]
 N=0
 max_charge=0.;max_book=0.;max_source=0.;tot_photo=0.;tot_recomb=0.
 selected={}
 # Select genuinely spread physical nH and geometry manually + by deterministic node schedule.
 selected_idx=set([0,1,32,128,999,1234,46079]+list(range(251,46080,1801))) # around 33 original sources
 with gzip.open(S/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz","rt") as native, \
      gzip.open(full,"rt") as generated, gzip.open(bfile,"rt") as budgetrows:
  fi=csv.DictReader(native);fg=csv.DictReader(generated);fb=csv.DictReader(budgetrows)
  for raw,r,b in zip(fi,fg,fb):
   j=int(r["node"])
   if not(j==N==int(raw["node"])==int(b["node"])):
    raise AssertionError("SOURCE_NODE_ID_OR_ORDER")
   N+=1
   NH=float(raw["source_H_nuclei_N_lower"])
   nh=float(r["nH_cm3"]);V=float(r["proper_volume_cm3"])
   err=abs(NH-nh*V)/NH
   max_source=max(max_source,err)
   if err>2e-14:raise AssertionError("DENSITY_SOURCE_NH_MISMATCH")
   x=float(r["source_xHII160"]);x1=float(r["preview_xHII161"])
   T=float(r["source_T160_K"]);T1=float(r["preview_T161_K"])
   if not(float(raw["tick160_xHII_lower"])<=x<=float(raw["tick160_xHII_upper"]) and
      float(raw["tick160_Tgas_K_lower"])<=T<=float(raw["tick160_Tgas_K_upper"])):
    raise AssertionError("ORIGINAL_NATIVE_SOURCE_T_OR_X_DISAGREEMENT")
   ne0=float(r["n_e_HHe_source160_cm3"])
   ne1=float(r["n_e_HHe_preview161_cm3"])
   true_ne0=(float(raw["tick160_electron_count_N_lower"])+float(raw["tick160_electron_count_N_upper"]))/(2*V)
   true_ne1=(float(raw["tick161_preview_electron_count_N_lower"])+float(raw["tick161_preview_electron_count_N_upper"]))/(2*V)
   if abs(true_ne0-ne0)>2e-14*true_ne0 or abs(true_ne1-ne1)>2e-14*true_ne1:
    raise AssertionError("ORIGINAL_NATIVE_HHE_ELECTRON_SOURCE")
   y=float(r["caseB_photo_y_final_neutral"])
   cx=float(r["caseB_CX_integrated_per_D_neutral"])
   p=float(r["caseB_D_photoionizations_per_D_neutral"])
   rr=float(r["caseB_D_recombinations_per_D_neutral"])
   max_book=max(max_book,abs(y-cx-p+rr))
   if max_book>4e-13:raise AssertionError("ORIGINAL_SOURCE_ISOTOPE_POPULATION_LEDGER")
   ion_e=float(r["caseB_D_photo_new_electron_per_H_neutral"])
   max_charge=max(max_charge,abs(ion_e-ETA*(p-rr)))
   if max_charge>4e-16:raise AssertionError("SOURCE_ELECTRON_CREATED_BY_CX")
   if abs(float(r["caseB_CX_heat_erg_per_H_neutral"])+ETA*ENG*cx)>4e-28:
    raise AssertionError("SOURCE_CX_ENERGY_BAD")
   phabs=float(b["caseB_DI_photo_ionizations_per_cell_initial_Dneutral"])
   if abs(phabs-ETA*NH*p)>2e-13*max(1e-200,abs(phabs)):
    raise AssertionError("LOCAL_PHOTON_PER_CELL_COUNT_ERROR")
   tot_photo+=phabs
   tot_recomb+=float(b["caseB_DI_recombinations_per_cell_initial_Dneutral"])
   if j in selected_idx:selected[j]=r
 if N!=46080 or len(selected)<22:raise AssertionError("SOURCE_NODE_AUDIT_INCOMPLETE")
 if abs(tot_photo-budget["derived_source_cell_HI_and_DI_photo_counts"]["D_photo_neutral"])/tot_photo>4e-14:
  raise AssertionError("D_PHOTO_NUMBER_BUDGET_MISMATCH")
 if abs(tot_recomb-budget["derived_source_cell_HI_and_DI_photo_counts"]["D_recomb_neutral"])/tot_recomb>4e-14:
  raise AssertionError("D_RECOMB_NUMBER_BUDGET_MISMATCH")
 errors=[]
 for j,r in sorted(selected.items()):
  nh=float(r["nH_cm3"]);x0=float(r["source_xHII160"]);x1=float(r["preview_xHII161"])
  T0=float(r["source_T160_K"]);T1=float(r["preview_T161_K"])
  e0=float(r["n_e_HHe_source160_cm3"]);e1=float(r["n_e_HHe_preview161_cm3"])
  for kind,case in [("neutral","B"),("ionized","B"),("neutral","A"),("ionized","A")]:
   y0=float(kind=="ionized")
   def vector_ODE(s,z):
    y,c,p,rr=z
    xi=x0+s*(x1-x0)-ETA*c
    T=T0*math.exp(s*math.log(T1/T0))
    ne=e0+s*(e1-e0)+ETA*nh*(y-c)
    kf,kr=rate(T,1),rate(T,2)
    C=nh*(kf*xi*(1-y)-kr*(1-xi)*y)
    P=float(gamma(s0+s*dt))*(1-y)
    RR=rec(T,case)*ne*y
    return dt*np.array([C+P-RR,C,P,RR])
   sol=solve_ivp(vector_ODE,(0.,1.),[y0,0.,0.,0.],method="DOP853",rtol=2e-12,atol=2e-13)
   if not sol.success:raise ArithmeticError("INDEPENDENT_SCALAR_DOP853_SOURCE_FAILURE")
   end=sol.y[:,-1]
   known=float(r[f"case{case}_photo_y_final_{kind}"])
   errors.append(abs(end[0]-known))
   if abs(end[0]-known)>8e-8:raise AssertionError("INDEPENDENT_ODE_SOURCE_DISAGREES")
   if case=="B" and kind=="neutral":
    for vname,q in [('caseB_CX_integrated_per_D_neutral',1),('caseB_D_photoionizations_per_D_neutral',2),('caseB_D_recombinations_per_D_neutral',3)]:
     if abs(float(r[vname])-end[q])>5e-8:raise AssertionError("FOUR_STATE_REACTION_FLOW_DISAGREES")
 evidence={
  "schema":"WU_R53_ORIGINAL_REI_46K_PHOTON_AND_ISOTOPE_C9_SELF_ADVERSARIAL_V1",
  "original_frozen_source_nodes_all_checked":N,
  "original_HHe_electron_state_and_volume_max_rel_error":max_source,
  "isotope_4state_charge_max_abs":max_charge,
  "isotope_4state_chemical_ledger_max_abs":max_book,
  "source_reconstructed_D_photon_total":tot_photo,
  "source_reconstructed_D_recombination_total":tot_recomb,
  "independent_scipy_scalar_DOP853_cases":len(errors),
  "independent_original_source_nodes_used":len(selected),
  "independent_max_abs_Dplus_difference":max(errors),
  "same_author":True,
  "distinct_author":"NOT_RUN",
  "original_owner_status":"F05_TICK161_PREVIEW_HOLD",
  "photon_allocation_consistency":"UNPROVED_SOURCE_GAMMA_CLONE_NOT_NATIVE_DI_GROUP_RESOLVED",
  "source_D_photo_may_alter_native_photon_rates":True,
  "hard_failures":0,"assessment":"NUMERICALLY_CHECKED_SCOPED",
  "canonical_WU":"34/49","canonical_REI":"28/88","delta":0
 }
 (R/"R53_ADVERSARIAL_AUDIT.json").write_text(json.dumps(evidence,indent=2,sort_keys=True)+"\n")
 print(json.dumps(evidence,sort_keys=True))
if __name__=="__main__":main()
