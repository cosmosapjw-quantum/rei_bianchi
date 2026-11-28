#!/usr/bin/env python3
"""R51 one-pass same-author blind-style adversarial audit, independently formulated.

Reads all source state and science data, checks physical source joins, rate-equilibrium
identities, H/D charge conservation and 36 high-precision Decimal rate witnesses.
Not a second scientist/model or rigorous continuum solver.
"""
import csv,gzip,hashlib,json,math,statistics
from decimal import Decimal,localcontext
from pathlib import Path
BASE=Path(__file__).resolve().parent
S=BASE/"sources"
R=BASE/"results"
SHA={
 "ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz":"713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d",
 "REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz":"024e1d1bbef95d3e254b8c54b3d1134de54eebce7b82d082401c522f813637c5",
 "SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv":"ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8",
}
ETA=2.5e-5
E=0.0037*1.602176634e-12

def hash(path):
 with open(path,"rb") as f:
  return hashlib.sha256(f.read()).hexdigest()

def num(x):
 return float(x)

def check():
 for k,v in SHA.items():
  if hash(S/k)!=v:raise AssertionError("ANALYTIC_WITNESS_SOURCE_HASH_MISMATCH "+k)
 rates=[]
 with (S/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv").open() as f:
  for r in csv.DictReader(f):
   rates.append((Decimal(r["T_K"]),Decimal(r["k_forward_cm3_s"]),Decimal(r["k_reverse_cm3_s"])))
 assert len(rates)==47
 energy=E*ETA
 rows=0
 bad_balance=0; fit_errors=0
 max_charge=0.0;max_stationarity=0.0;max_cx_energy=0.
 high_precision=0;max_decimal_relative=0.
 unique=[]
 sampled=set([0,1,10,100,999,46079] + list(range(137,46080,1417)))
 with gzip.open(S/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz","rt") as inp, \
      gzip.open(S/"REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz","rt") as en, \
      gzip.open(R/"R51_REI_F05_SAVIN_H_D_CX_46080.csv.gz","rt") as d:
  ia=csv.DictReader(inp);ib=csv.DictReader(en);ic=csv.DictReader(d)
  for A,B,X in zip(ia,ib,ic):
   n=int(A["node"])
   if n!=rows or n!=int(B["node"]) or n!=int(X["node"]):
    raise AssertionError("ORIGINAL_SOURCE_ORDER_OR_INDEX_MISMATCH")
   rows+=1
   x=num(X["original_xHII160"])
   y=num(X["CX_equilibrium_Dplus160"])
   k1=num(X["k_forward160_cm3_s"])
   k2=num(X["k_reverse160_cm3_s"])
   npH=num(X["original_H_nuclei_N"])
   if not 0<x<1 or not 0<y<1 or not npH>0 or not k1>0 or not k2>0:
    raise AssertionError("ORIGINAL_SOURCE_PHYSICAL_CONE")
   if not(num(A["tick160_xHII_lower"])<=x<=num(A["tick160_xHII_upper"])):
    raise AssertionError("SOURCE_PARENT_H_PROVENANCE")
   if not(num(A["tick160_Tgas_K_lower"])<=num(X["original_T160_K"])<=num(A["tick160_Tgas_K_upper"])):
    raise AssertionError("SOURCE_PARENT_T_PROVENANCE")
   if abs(num(X["preview_T161_K"])-(num(A["tick161_preview_Tgas_K_lower"])+num(A["tick161_preview_Tgas_K_upper"]))/2)>1e-11:
    raise AssertionError("PREVIEW_PHYSICAL_T_PROVENANCE")
   if abs(npH-num(A["source_H_nuclei_N_lower"]))>1e-14*npH:
    raise AssertionError("N_H_SOURCE_WRONG")
   den=k1*x+k2*(1-x)
   rcalc=1/(1-x+(k1/k2)*x)
   if abs(rcalc-num(X["CX_Dneutral_over_Hneutral160"]))>4e-14:
    raise AssertionError("INDEPENDENT_NEUTRAL_D_OVER_H_CORRECTION")
   residual=(k1*(1-y)*x-k2*y*(1-x))/den
   max_stationarity=max(max_stationarity,abs(residual))
   if abs(residual)>3e-14:
    raise AssertionError("SAVIN_SOURCE_CX_BALANCE_FAILED")
   if abs(den-num(X["CX_stationary_relaxation_per_nH160_cm3_s"]))>1e-22:
    raise AssertionError("SOURCE_RELAXATION_PER_NH_RATE_NOT_EQUAL_SUM")
   for suffix,y0 in [("initial_Dneutral",0),("initial_Dplus",1)]:
    yd=num(X["CX_conserving_Dplus_eq160_"+suffix])
    xh=num(X["CX_conserving_Hplus_eq160_"+suffix])
    charge=xh+ETA*yd-x-ETA*y0
    max_charge=max(max_charge,abs(charge))
    if abs(charge)>4e-16:
     bad_balance+=1
    eq=k1*(1-yd)*xh-k2*yd*(1-xh)
    if abs(eq)/den>5e-14:raise AssertionError("EXACT_COUPLED_H_D_STATIONARY_FAILURE")
    q=-ETA*E*(yd-y0)  # exact gas energy sign for D0+H+ -> D++H endothermic
    if abs(q-num(X["CX_heat_"+suffix+"_160_erg_per_H"]))>5e-31:
     raise AssertionError("SOURCE_CX_REACTION_ENERGY_WRONG")
    max_cx_energy=max(max_cx_energy,abs(q))
   if num(X["CX_absolute_energy_ceiling_erg_per_H"])!=energy:
    raise AssertionError("SOURCE_CX_ENERGY_CAP_WRONG")
   if abs(num(X["CX_energy_ceiling_over_F05_abs_thermal_gain"])*abs(num(B["thermal_energy_gain_twohalf_center_erg_per_H"]))-energy)>1e-30:
    raise AssertionError("SOURCE_OWNER_GAS_ENERGY_NORMALIZATION_WRONG")
   if n in sampled:
    with localcontext() as ctx:
     ctx.prec=70
     t=Decimal(X["original_T160_K"])
     k=[]
     for a in (1,2):
      j=next(i for i in range(len(rates)-1) if rates[i][0]<=t<=rates[i+1][0])
      t0,z0=rates[j][0],rates[j][a]
      t1,z1=rates[j+1][0],rates[j+1][a]
      weight=(t.ln()-t0.ln())/(t1.ln()-t0.ln())
      k.append((z0.ln()+(z1.ln()-z0.ln())*weight).exp())
     for expected,real in zip(k,[k1,k2]):
      rel=abs(float(expected)-real)/float(expected)
      max_decimal_relative=max(max_decimal_relative,rel)
      if rel>3e-14:raise AssertionError("DECIMAL_ORIGINAL_SOURCE_RATE_DISAGREEMENT")
    high_precision+=1
 if rows!=46080:raise AssertionError("REAL_ORIGINAL_SOURCE_ROW_COUNT_WRONG")
 if bad_balance:raise AssertionError("CONSERVATION_RESIDUAL_EXCEEDED_CONTRACT")
 result=json.loads((R/"R51_RESULTS.json").read_text())
 if result["number_original_source_cells"]!=rows:
  raise AssertionError("DAG_SOURCE_COUNT_MISMATCH")
 if result["source_identity"]["ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz"]!=SHA["ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz"]:
  raise AssertionError("ORIGINAL_OWNER_SOURCE_REF_DRIFT")
 out={
  "schema":"WU_R51_SAME_AUTHOR_ADVERSARIAL_C7_C9_V1",
  "same_author_only":True,"distinct_author":False,
  "full_source_original_rows_independently_scanned":rows,
  "source_table_Savin_rows":47,
  "Decimal_rate_witnesses":high_precision,
  "Decimal_max_relative_error":max_decimal_relative,
  "max_stationary_rate_residual_dimensionless":max_stationarity,
  "max_H_D_charge_conservation_abs_residual":max_charge,
  "max_CX_transferred_energy_abs_erg_per_H":max_cx_energy,
  "max_exact_CX_energy_capacity_erg_per_H":energy,
  "source_conditional_model_validity":"SAVIN_TABLE_INTERPOLATED_CX_ONLY_QUASISTATIC_H_D_CHARGE_CONSERVED",
  "reactions_cannot_change_total_free_electrons_if_only_CX":True,
  "ACTUAL_SOURCE_EOR_IONIZATION_AND_PHOTON_CHEMISTRY_NOT_SOLVED":True,
  "source_H_nuclei_number_not_proper_density":True,
  "canonical_WU":"34/49","canonical_REI":"28/88",
  "claim_status":"PRIMARY_SOURCE_CROSS_JOIN_AND_MATH_PASS_SAME_AUTHOR"
 }
 (R/"R51_ADVERSARIAL_AUDIT.json").write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
 print(json.dumps(out,sort_keys=True))
 return out

if __name__=="__main__":check()
