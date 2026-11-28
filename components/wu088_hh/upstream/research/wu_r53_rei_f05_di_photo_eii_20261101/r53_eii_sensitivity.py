#!/usr/bin/env python3
"""R53 risk-justified original-source electron-impact ionization (EII) sensitivity.

Source: original REI H beta_HI(T) and Savin 2002 Eq12 DI≈HI electron-impact rate.
Adds EII to already computed CX+HI-cloned-photo+caseB RR as separate real 46k
physical model, with exact CX versus photon+EII charge and energy ledgers.
"""
import csv,gzip,hashlib,io,json,math
from pathlib import Path
import numpy as np
import r53_photo_chemistry as base
ROOT=Path(__file__).resolve().parent
SRC=ROOT/"sources"
OUT=ROOT/"results"
ETA=base.ETA
EII_CHI_E_V=13.598+.0037
EV_ERG=1.602176634e-12
N=base.N
def source_check():
 z=json.loads((ROOT/"EII_SOURCE_CONTRACT.json").read_text())
 if base.sha(SRC/"REI_joint_sink_reservoir_history.py")!=z["original_REI_module_SHA256"]:
  raise ValueError("ORIGINAL_REI_EII_FORMULA_SHA_CHANGED")
 return z

def beta_HI(T):
 t=np.asarray(T)
 if np.any(~np.isfinite(t)) or np.any(t<=0):raise ValueError("EII_T_INVALID")
 return 5.835e-11*np.sqrt(t)*np.exp(-157804./t)

def integrate(v,y0,eii=1.,steps=64):
 y=y0.copy();cx=np.zeros_like(y);photo=np.zeros_like(y);rr=np.zeros_like(y);Ei=np.zeros_like(y)
 dt=v["dt"];logratio=np.log(v["T1"]/v["T0"]);nh=v["nH"]
 def rhs(s,Y,CX):
  x=v["x0"]+(v["x1"]-v["x0"])*s
  temp=v["T0"]*np.exp(logratio*s)
  ne=v["ne0"]+(v["ne1"]-v["ne0"])*s
  xeff=x-ETA*CX
  neeff=ne+ETA*nh*(Y-CX)
  if np.any(xeff<-1e-9) or np.any(xeff>1+1e-9) or np.any(Y<-1e-9) or np.any(Y>1+1e-9) or np.any(neeff<=0):
   raise ValueError("NATIVE_D_H_EII_PHYSICAL_CONE_FAIL")
  kf,kr=base.savin(temp,v["knots"],v["forward"],v["reverse"])
  C=nh*(kf*xeff*(1-Y)-kr*(1-xeff)*Y)
  P=float(v["gamma"](v["tleft"]+dt*s))*(1-Y)
  R=base.case_alpha(temp,"B")*neeff*Y
  EI=eii*beta_HI(temp)*neeff*(1-Y)
  return dt*(C+P+EI-R),dt*C,dt*P,dt*R,dt*EI
 h=1./steps
 for j in range(steps):
  s=j*h
  a1,b1,c1,d1,e1=rhs(s,y,cx)
  a2,b2,c2,d2,e2=rhs(s+h/2,y+h*a1/2,cx+h*b1/2)
  a3,b3,c3,d3,e3=rhs(s+h/2,y+h*a2/2,cx+h*b2/2)
  a4,b4,c4,d4,e4=rhs(s+h,y+h*a3,cx+h*b3)
  y+=h*(a1+2*a2+2*a3+a4)/6
  cx+=h*(b1+2*b2+2*b3+b4)/6
  photo+=h*(c1+2*c2+2*c3+c4)/6
  rr+=h*(d1+2*d2+2*d3+d4)/6
  Ei+=h*(e1+2*e2+2*e3+e4)/6
 if np.any(~np.isfinite(y)) or np.any(y<0) or np.any(y>1):
  raise ArithmeticError("ISOTOPE_EII_PHYSICAL_POPULATION_FAIL")
 ledger=y-y0-cx-photo-Ei+rr
 if np.max(np.abs(ledger))>3e-13:raise ArithmeticError("ISOTOPE_5_REACTION_LEDGER_FAILURE")
 return dict(y=y,cx=cx,photo=photo,rr=rr,eii=Ei,ledger=ledger)

def stats(v):
 a=np.asarray(v)
 return dict(min=float(a.min()),median=float(np.median(a)),p95=float(np.percentile(a,95)),max=float(a.max()))

def run():
 source_check()
 v=base.load()
 kf,kr=base.savin(v["T0"],v["knots"],v["forward"],v["reverse"])
 init=dict(neutral=np.zeros(N),ionized=np.ones(N),
   eq160=kf*v["x0"]/(kf*v["x0"]+kr*(1-v["x0"])))
 old={}
 with gzip.open(OUT/base.FNAME,"rt") as f:
  for r in csv.DictReader(f):
   for name in ("caseB_photo_y_final_neutral","caseB_photo_y_final_ionized","caseB_photo_y_final_CXeq160",
                "caseB_D_photoionizations_per_D_neutral","caseB_D_photoionizations_per_D_ionized"):
    old.setdefault(name,[]).append(float(r[name]))
 old={k:np.asarray(x) for k,x in old.items()}
 if any(len(x)!=N for x in old.values()):raise ValueError("ORIGINAL_R53_RESULT_MISSING_46080")
 out={};max_num=0
 for name,y0 in init.items():
  z=integrate(v,y0)
  w=integrate(v,y0,steps=32)
  out[name]=z
  max_num=max(max_num,float(np.max(np.abs(z["y"]-w["y"]))))
 # Important negative regression: EII set to 0 recovers ALL original R53 primary y
 # within binary64 integration rounding, not only a 24-row witness.
 oldzero=integrate(v,init["neutral"],eii=0.)
 restore=float(np.max(abs(oldzero["y"]-old["caseB_photo_y_final_neutral"])))
 if restore>2e-12:raise ArithmeticError("R53_ORIGINAL_PHOTO_RECOMB_BASE_NOT_RECOVERED")
 # Original discrete thermal increment per H from actual source native F05 PR347
 originalDU=[]
 with gzip.open(SRC/"REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz","rt") as f:
  for i,r in enumerate(csv.DictReader(f)):
   if int(r["node"])!=i:raise ValueError("F05_ENERGY_SOURCE_NODE_CHANGED")
   originalDU.append(float(r["thermal_energy_gain_twohalf_center_erg_per_H"]))
 if len(originalDU)!=N:raise ValueError("F05_ENERGY_ROWS_MISSING")
 du=np.array(originalDU)
 if np.any(du==0):raise ValueError("F05_ENERGY_ZERO")
 f=out["neutral"];fi=out["ionized"];fEq=out["eq160"]
 energ=-ETA*(EII_CHI_E_V*EV_ERG)*f["eii"]
 ratio=energ/np.abs(du)
 target=OUT/"R53_REI_F05_EII_SOURCE_SENSITIVITY_46080.csv.gz"
 keys=[
 "node","original_T160_K","original_n_e_HHe160_cm3","original_proper_nH_cm3",
 "native_beta_HI_cm3_s","source_eii_exposure_160_one_tick",
 "caseB_noEII_neutral_y","caseB_withEII_neutral_y","caseB_withEII_ionized_y",
 "caseB_withEII_eq160_y",
 "EII_on_minus_off_neutral_y","EII_on_minus_off_ionized_y",
 "EII_photons_per_D_neutral","EII_collisional_ionizations_per_D_neutral",
 "EII_recomb_per_D_neutral","EII_CX_integral_per_D_neutral",
 "EII_photo_count_per_cell_neutral","EII_photo_count_change_vs_noEII_per_cell",
 "EII_CX_heat_erg_per_H_neutral","EII_thermal_threshold_sink_erg_per_H_neutral",
 "EII_sink_over_original_native_F05_thermal_abs_neutral",
 "EII_free_electron_new_vs_initial_per_H_neutral",
 "EII_all_electron_over_H_at161_neutral",
 "EII_charge_balance_H_CX_only_per_H",
 "EII_vs_gamma_HI_at160_ratio",
 "EII_5flux_stoich_residual"
 ]
 cols=[
 np.arange(N),v["T0"],v["ne0"],v["nH"],beta_HI(v["T0"]),
 beta_HI(v["T0"])*v["ne0"]*v["dt"],
 old["caseB_photo_y_final_neutral"],f["y"],fi["y"],fEq["y"],
 f["y"]-old["caseB_photo_y_final_neutral"],
 fi["y"]-old["caseB_photo_y_final_ionized"],
 f["photo"],f["eii"],f["rr"],f["cx"],
 ETA*v["nH"]*v["vol"]*f["photo"],
 ETA*v["nH"]*v["vol"]*(f["photo"]-old["caseB_D_photoionizations_per_D_neutral"]),
 -ETA*base.DX_ERG*f["cx"],
 energ,ratio,ETA*(f["photo"]+f["eii"]-f["rr"]),
 ETA*(f["y"]-f["cx"]),-ETA*f["cx"],
 beta_HI(v["T0"])*v["ne0"]/float(v["gamma"](v["tleft"])),
 f["ledger"]
 ]
 with target.open("wb") as raw:
  with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0,compresslevel=6) as gz:
   with io.TextIOWrapper(gz,encoding="utf8",newline="") as text:
    w=csv.writer(text,lineterminator="\n");w.writerow(keys)
    for i in range(N):
     w.writerow([i if j==0 else format(float(c[i]),".17g") for j,c in enumerate(cols)])
 dabs=float(np.sum(ETA*v["nH"]*v["vol"]*f["photo"]))
 photon=json.loads((OUT/"R53_PHOTON_BUDGET.json").read_text())
 native_emit=photon["native_source_integrated_counts_per_cMpc3"]["emission_rate_s-1_cMpc-3"]
 report={
  "schema":"WU_R53_ORIGINAL_REI_46K_SOURCE_RECOMB_PHOTO_CX_PLUS_EII_SENSITIVITY_V1",
  "source_native_H_EII_beta_Module_SHA":source_check()["original_REI_module_SHA256"],
  "source_R53_photon_contract":"ORIGINAL_HI_GAMMA_CLONED_DI_SAVIN_EQ11_12_13",
  "original_native_DI_photo_groups":"NOT_ALLOCATED",
  "real_source_cells":N,
  "native_first_tick_dt_s":v["dt"],
  "native_EII_exposure_start":stats(beta_HI(v["T0"])*v["ne0"]*v["dt"]),
  "N_EII_exposure_gt_original_HI_photo_exposure":int(np.count_nonzero(beta_HI(v["T0"])*v["ne0"]*v["dt"]>
                  float(v["gamma"](v["tleft"]))*v["dt"])),
  "N_EII_exposure_gt_0p01":int(np.count_nonzero(beta_HI(v["T0"])*v["ne0"]*v["dt"]>.01)),
  "initial_neutral_Dplus_final_withEII":stats(f["y"]),
  "initial_neutral_Dplus_final_withoutEII":stats(old["caseB_photo_y_final_neutral"]),
  "initial_ionized_Dplus_final_withEII":stats(fi["y"]),
  "initial_eq160_Dplus_final_withEII":stats(fEq["y"]),
  "EII_on_minus_off_initial_neutral_y":stats(f["y"]-old["caseB_photo_y_final_neutral"]),
  "EII_on_minus_off_initial_ionized_y":stats(fi["y"]-old["caseB_photo_y_final_ionized"]),
  "total_DI_photo_reactions_with_EII_initial_neutral":dabs,
  "total_DI_photo_reactions_noEII_initial_neutral":photon["derived_source_cell_HI_and_DI_photo_counts"]["D_photo_neutral"],
  "DI_photo_over_native_photon_emission_withEII":dabs/native_emit,
  "DI_photo_over_native_photon_emission_noEII":photon["photon_demand_ratios"]["DI_neutral_over_source_emission"],
  "EII_thermal_threshold_D_ionization_potential_eV":EII_CHI_E_V,
  "EII_thermal_threshold_sink_erg_per_H":stats(energ),
  "EII_sink_over_original_F05_native_thermal_abs":stats(ratio),
  "N_EII_sink_gt1pct_native_F05_thermal":int(np.count_nonzero(np.abs(ratio)>.01)),
  "max_RK32_vs64_abs_y_all_scenarios":max_num,
  "noEII_R53_noRadiativeCorrection_regression_maxabs":restore,
  "five_reaction_charge_ledger_maxabs":float(np.max(abs(f["ledger"]))),
  "full_source_five_flux_sha256":base.sha(target),
  "strong_no_go_claim":False,
  "canonical_DAG":{"WU":"34/49","REI_central":"28/88","delta":0},
  "status":"SOURCE_CONDITIONAL_EII_UPPER_PHYSICAL_RISK_CHECK_NOT_ORIGINAL_OWNER_ADMISSION"
 }
 (OUT/"R53_EII_RESULTS.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
 print(json.dumps({k:report[k] for k in (
  "real_source_cells","native_EII_exposure_start",
  "N_EII_exposure_gt_original_HI_photo_exposure",
  "initial_neutral_Dplus_final_withEII","EII_on_minus_off_initial_neutral_y",
  "DI_photo_over_native_photon_emission_withEII",
  "EII_sink_over_original_F05_native_thermal_abs",
  "N_EII_sink_gt1pct_native_F05_thermal",
  "noEII_R53_noRadiativeCorrection_regression_maxabs",
  "full_source_five_flux_sha256"
 )},sort_keys=True))
 return report
if __name__=="__main__":run()
