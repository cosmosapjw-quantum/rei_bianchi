#!/usr/bin/env python3
"""R52: actual original REI F05 first-tick proper-density/clock H-D CX-only dynamics.

Original REI full native tick160 accepted and 46,080-cell tick161 NONAUTHORITATIVE
preview supply H/He/T endpoints. Source-forcing z_mid and W_node fix actual
proper volumes; published Savin 2002 original 47-point table fixes k_f, k_r.
Between endpoints the donor H+ and log T are EXPLICIT conditional interpolants,
not original 26-event continuous histories; D photoionization/HD excluded.
"""
from __future__ import annotations
import csv,gzip,hashlib,io,json,math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"source_inputs"
SHA={
"initial_material_state_z6.npz":"7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d",
"canonical_time_resolved_forcing_nodes.csv":"9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268",
"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz":"713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d",
"REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz":"024e1d1bbef95d3e254b8c54b3d1134de54eebce7b82d082401c522f813637c5",
"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv":"ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8",
"SAVIN2002_ORIGINAL_TABLE2_FITS.json":"b178d89b858ae58ed1fe873fe831e02b737532a2f1fc20a82c920e76d2c3b1bc"
}
N=46080
ETA=2.5e-5
E_REACTION_ERG=.0037*1.602176634e-12
MPC_CM=3.085677581491367e24
DENOM_TICKS=131072
COLS=[
"node","original_NH_nuclei","original_comoving_weight_W","source_proper_volume_cm3","original_nH_proper_cm3",
"original_tick160_T_K","preview_tick161_T_K","original_tick160_xHII","preview_tick161_xHII",
"source_original_F05_deltaU_erg_per_H","original_source_delta_t_s",
"theta_CX_original_source_interp","CX_timescale_over_tick_inverse","source_original_HI_photo_exposure_diagnostic",
"CX_y0_neutral","CX_y_final_neutral","CX_Dplus_N_final_neutral",
"CX_Dneutral_over_Hneutral_final_neutral","CX_Hplus_compensation_neutral",
"CX_net_energy_erg_per_H_neutral","CX_energy_over_native_thermal_abs_neutral",
"CX_y0_ionized","CX_y_final_ionized","CX_Dneutral_over_Hneutral_final_ionized",
"CX_Hplus_compensation_ionized","CX_net_energy_erg_per_H_ionized",
"CX_energy_over_native_thermal_abs_ionized",
"CX_y0_eq160","CX_y_final_eq160","CX_Dneutral_over_Hneutral_final_eq160",
"CX_Hplus_compensation_eq160","CX_net_energy_erg_per_H_eq160",
"CX_energy_over_native_thermal_abs_eq160",
"CX_stationary_equilibrium_tick161","CX_neq_distance_from_eq161_neutral",
"CX_neq_distance_from_eq161_ionized","CX_neq_distance_from_eq161_eq160",
"CX_frozen_start_vs_interp_diff_neutral","CX_frozen_end_vs_interp_diff_neutral",
"CX_RK32_vs_RK64_abs_error_neutral","CX_RK32_vs_RK64_abs_error_ionized",
"CX_RK32_vs_RK64_abs_error_eq160",
"CX_electron_total_CX_excess_per_H_neutral",
"CX_electron_total_CX_excess_per_H_ionized"
]

def sha(p:Path):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()

def quant(a):
 a=np.asarray(a)
 return {"min":float(np.min(a)),"p05":float(np.percentile(a,5)),
         "median":float(np.median(a)),"p95":float(np.percentile(a,95)),
         "max":float(np.max(a))}

def savin_rate(T, knots, ln_forward, ln_reverse):
 t=np.asarray(T,dtype=np.float64)
 if np.any(~np.isfinite(t)) or np.any(t<2.7) or np.any(t>200000):
  raise ValueError("SAVIN_FIT_VALID_DOMAIN_2p7_TO_2E5_K")
 logt=np.log(t)
 return np.exp(np.interp(logt,knots,ln_forward)),np.exp(np.interp(logt,knots,ln_reverse))

def validate_source():
 for name,d in SHA.items():
  if sha(SOURCE/name)!=d:raise ValueError("IMMUTABLE_ORIGINAL_SOURCE_SHA_MISMATCH:"+name)
 with (SOURCE/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv").open() as f:
  table=list(csv.DictReader(f))
 assert len(table)==47
 T=np.array([float(q["T_K"]) for q in table])
 kf=np.array([float(q["k_forward_cm3_s"]) for q in table])
 kb=np.array([float(q["k_reverse_cm3_s"]) for q in table])
 if np.any(np.diff(T)<=0) or np.any(kf<=0) or np.any(kb<=0):
  raise ValueError("PUBLISHED_SAVIN_TABLE_INVALID")
 z=np.load(SOURCE/"initial_material_state_z6.npz",allow_pickle=False)
 W=np.asarray(z["W_node"],float)
 initial_H=np.asarray(z["N_HI"],float)+np.asarray(z["N_HII"],float)
 if W.shape!=(N,) or np.any(W<=0) or abs(float(np.sum(W))-1)>1e-14:
  raise ValueError("ORIGINAL_CELL_WEIGHTS_NONPHYSICAL")
 with (SOURCE/"canonical_time_resolved_forcing_nodes.csv").open() as f:
  all_forcing=list(csv.DictReader(f))
 first=[q for q in all_forcing if int(q["interval_index"])==0]
 if len(first)!=17 or any(float(q["z_mid"])!=5.95 for q in first):
  raise ValueError("ORIGINAL_FIRST_FORCING_Z_NOT_CONSTANT")
 times=np.array([float(q["time_s"]) for q in first])
 if not np.all(np.diff(times)>0) or times[0]!=0:
  raise ValueError("ORIGINAL_FORCING_CLOCK_NOT_MONOTONE")
 duration=float(times[-1]-times[0])
 dt=duration/DENOM_TICKS
 t0=160*dt;t1=161*dt
 if abs(dt-4871848749.16828)>1e-2:raise ValueError("ORIGINAL_26_EVENT_CLOCK_DRIFT")
 # Linear interpolation of original HI photo-rate is diagnostic ONLY, never
 # a true deuterium radiative rate in this isolated CX-only system.
 gamma=np.interp(t0,times,np.array([float(q["Gamma_HI_s-1"]) for q in first]))
 return dict(W=W,NH0=initial_H,knots=np.log(T),lnkf=np.log(kf),lnkb=np.log(kb),
             dt=dt,t0=t0,t1=t1,source_gamma_HI=float(gamma),
             source_first_z=5.95,original_forcing_node_count=len(first))

def rk4_coupled(y0,x0,x1,T0,T1,nH,dt,model,steps,eta=ETA):
 """Finite abundance ion transfer to O(eta), with exact CX charge compensation.

 x_base(s) is the native H/He endpoint linear interpolation, log T also linear.
 Corrected H-ion fraction is x_base - eta*(y(s)-y(0)); this tracks the H/D
 charge transfer without rerunning the original H/He photon source.
 For the optional endpoint frozen controls, x,T are held at their endpoint.
 """
 y=y0.copy()
 logfrac=np.log(T1/T0)
 step=1.0/steps
 def rhs(ys,s):
  if model=="linear":
   x=x0+(x1-x0)*s;temp=T0*np.exp(logfrac*s)
  elif model=="left":x=x0;temp=T0
  elif model=="right":x=x1;temp=T1
  else:raise ValueError("unknown donor model")
  h_ion=x-eta*(ys-y0)
  if np.any(h_ion<-1e-12) or np.any(h_ion>1+1e-12) or np.any(ys<-1e-12) or np.any(ys>1+1e-12):
   raise ArithmeticError("H_D_CHARGE_CX_PHYSICAL_DOMAIN_EXIT")
  kf,kb=savin_rate(temp,model_table[0],model_table[1],model_table[2])
  return dt*nH*(kf*h_ion*(1-ys)-kb*(1-h_ion)*ys)
 for i in range(steps):
  s=i*step
  d1=rhs(y,s)
  d2=rhs(y+0.5*step*d1,s+0.5*step)
  d3=rhs(y+0.5*step*d2,s+0.5*step)
  d4=rhs(y+step*d3,s+step)
  y=y+(step/6.0)*(d1+2*d2+2*d3+d4)
 if np.any(y<0) or np.any(y>1) or np.any(~np.isfinite(y)):
  raise ArithmeticError("UNPHYSICAL_CX_ODE_SOLUTION")
 return y

# Kept unmodified during all computations within a run, assigned from
# source immutable rate nodes before any RHS invocation.
model_table=None

def write_gz(path,columns):
 with path.open("wb") as raw:
  with gzip.GzipFile(fileobj=raw,mode="wb",filename="",compresslevel=6,mtime=0) as zipped:
   with io.TextIOWrapper(zipped,encoding="utf-8",newline="") as f:
    w=csv.writer(f,lineterminator="\n")
    w.writerow(columns.keys())
    arrays=[np.asarray(v) for v in columns.values()]
    for i in range(N):
     w.writerow([format(float(a[i]),".17g") if a.dtype.kind=="f" else int(a[i]) for a in arrays])

def load_original():
 z=validate_source()
 npz=np.load(SOURCE/"initial_material_state_z6.npz",allow_pickle=False)
 vol=z["W"]*(MPC_CM**3)/(1+z["source_first_z"])**3
 nh=[]
 t0=[];t1=[];x0=[];x1=[];old_energy=[]
 with gzip.open(SOURCE/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz","rt") as f1, \
      gzip.open(SOURCE/"REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz","rt") as f2:
  a=csv.DictReader(f1);b=csv.DictReader(f2)
  for j,(p,q) in enumerate(zip(a,b)):
   if int(p["node"])!=j or int(q["node"])!=j:
    raise ValueError("ORIGINAL_REI_PHYSICAL_NODE_ORDER_DRIFT")
   nh.append(float(p["source_H_nuclei_N_lower"]))
   t0.append(float(q["parent_T_center_K"]))
   x0.append(float(q["parent_xHII_center"]))
   t1.append(0.5*(float(p["tick161_preview_Tgas_K_lower"])+float(p["tick161_preview_Tgas_K_upper"])))
   x1.append(0.5*(float(p["tick161_preview_xHII_lower"])+float(p["tick161_preview_xHII_upper"])))
   old_energy.append(float(q["thermal_energy_gain_twohalf_center_erg_per_H"]))
   if not (float(p["tick160_Tgas_K_lower"])<=t0[-1]<=float(p["tick160_Tgas_K_upper"])
          and float(p["tick160_xHII_lower"])<=x0[-1]<=float(p["tick160_xHII_upper"])):
    raise ArithmeticError("SOURCE_PARENT_T_X_ENCLOSURE_MISMATCH")
 nh=np.asarray(nh)
 if len(nh)!=N or not np.all(nh>0) or np.any(~np.isfinite(nh)):
  raise ValueError("SOURCE_CELL_H_NUCLEI_NOT_46080_POSITIVE")
 if not np.array_equal(nh,z["NH0"]):
  raise ValueError("SOURCE_TICK160_H_NUCLEI_VS_INITIAL_MATERIAL_BYTE_NUMERIC_MISMATCH")
 density=nh/vol
 T0,T1,x0,x1,old_energy=map(np.asarray,(t0,t1,x0,x1,old_energy))
 if np.any(~np.isfinite(density)) or np.any(density<=0):
  raise ValueError("SOURCE_PROPER_H_DENSITY_NOT_VALID")
 if np.any(T0<2.7) or np.any(T1>200000) or np.any(T1<2.7) or np.any(T0>200000):
  raise ValueError("SOURCE_SAVIN_T_K_EXTRAPOLATION")
 if not (np.all((x0>0)&(x0<1)) and np.all((x1>0)&(x1<1))):
  raise ValueError("SOURCE_PHYSICAL_H_IONIZATION_OUT_OF_CONE")
 if np.any(old_energy==0):raise ValueError("SOURCE_F05_THERMAL_GAIN_ZERO")
 return z,vol,nh,density,T0,T1,x0,x1,old_energy

def run(out):
 global model_table
 z,vol,nh,density,T0,T1,x0,x1,dU=load_original()
 model_table=(z["knots"],z["lnkf"],z["lnkb"])
 dt=z["dt"]
 kf0,kb0=savin_rate(T0,*model_table)
 a0=kf0*x0;b0=kb0*(1-x0)
 y_eq0=a0/(a0+b0)
 kf1,kb1=savin_rate(T1,*model_table)
 a1=kf1*x1;b1=kb1*(1-x1)
 y_eq1=a1/(a1+b1)
 init={"neutral":np.zeros(N),"ionized":np.ones(N),"eq160":y_eq0}
 # Strict stage-long kinetic source rate integral under explicit interpolated native donor.
 c=np.zeros(N)
 for j in range(64):
  s=(j+.5)/64
  T=T0*np.exp(np.log(T1/T0)*s)
  x=x0+(x1-x0)*s
  kf,kb=savin_rate(T,*model_table)
  c+=kf*x+kb*(1-x)
 theta=density*dt*c/64
 if np.any(theta<0):raise ArithmeticError("NEGATIVE_CX_KINETIC_EXPOSURE")
 final={}
 errors={}
 for key,v in init.items():
  y16=rk4_coupled(v,x0,x1,T0,T1,density,dt,"linear",16)
  y32=rk4_coupled(v,x0,x1,T0,T1,density,dt,"linear",32)
  y64=rk4_coupled(v,x0,x1,T0,T1,density,dt,"linear",64)
  final[key]=y64
  errors[key]=np.abs(y32-y64)
 # Independent sensitivity to source endpoint interpolation closure.
 left=rk4_coupled(init["neutral"],x0,x1,T0,T1,density,dt,"left",64)
 right=rk4_coupled(init["neutral"],x0,x1,T0,T1,density,dt,"right",64)
 # Under this owner-prescribed H-only source the D transfer compensating H charge
 # is delta_xH = -eta*(y_end-y_initial), at fixed original H donor trajectory.
 dxi={k:-ETA*(final[k]-init[k]) for k in init}
 echange={k:-ETA*E_REACTION_ERG*(final[k]-init[k]) for k in init}
 ratio={k:echange[k]/np.abs(dU) for k in init}
 h_eff={k:x1+dxi[k] for k in init}
 for key in init:
  if np.any((h_eff[key]<0)|(h_eff[key]>1)):raise ArithmeticError("CX_EXCHANGE_H_VIOLATES_PHYSICAL_CONE")
  if np.any(np.abs(h_eff[key]+ETA*final[key]-(x1+ETA*init[key]))>4e-16):
   raise ArithmeticError("SOURCE_H_D_ELECTRON_CHARGE_LEDGER_FAILED")
 columns={
 "node":np.arange(N,dtype=np.int64),
 "original_NH_nuclei":nh,
 "original_comoving_weight_W":z["W"],
 "source_proper_volume_cm3":vol,
 "original_nH_proper_cm3":density,
 "original_tick160_T_K":T0,
 "preview_tick161_T_K":T1,
 "original_tick160_xHII":x0,
 "preview_tick161_xHII":x1,
 "source_original_F05_deltaU_erg_per_H":dU,
 "original_source_delta_t_s":np.full(N,dt),
 "theta_CX_original_source_interp":theta,
 "CX_timescale_over_tick_inverse":theta,
 "source_original_HI_photo_exposure_diagnostic":np.full(N,z["source_gamma_HI"]*dt),
 "CX_y0_neutral":init["neutral"],
 "CX_y_final_neutral":final["neutral"],
 "CX_Dplus_N_final_neutral":ETA*nh*final["neutral"],
 "CX_Dneutral_over_Hneutral_final_neutral":(1-final["neutral"])/(1-h_eff["neutral"]),
 "CX_Hplus_compensation_neutral":dxi["neutral"],
 "CX_net_energy_erg_per_H_neutral":echange["neutral"],
 "CX_energy_over_native_thermal_abs_neutral":ratio["neutral"],
 "CX_y0_ionized":init["ionized"],
 "CX_y_final_ionized":final["ionized"],
 "CX_Dneutral_over_Hneutral_final_ionized":(1-final["ionized"])/(1-h_eff["ionized"]),
 "CX_Hplus_compensation_ionized":dxi["ionized"],
 "CX_net_energy_erg_per_H_ionized":echange["ionized"],
 "CX_energy_over_native_thermal_abs_ionized":ratio["ionized"],
 "CX_y0_eq160":init["eq160"],
 "CX_y_final_eq160":final["eq160"],
 "CX_Dneutral_over_Hneutral_final_eq160":(1-final["eq160"])/(1-h_eff["eq160"]),
 "CX_Hplus_compensation_eq160":dxi["eq160"],
 "CX_net_energy_erg_per_H_eq160":echange["eq160"],
 "CX_energy_over_native_thermal_abs_eq160":ratio["eq160"],
 "CX_stationary_equilibrium_tick161":y_eq1,
 "CX_neq_distance_from_eq161_neutral":np.abs(final["neutral"]-y_eq1),
 "CX_neq_distance_from_eq161_ionized":np.abs(final["ionized"]-y_eq1),
 "CX_neq_distance_from_eq161_eq160":np.abs(final["eq160"]-y_eq1),
 "CX_frozen_start_vs_interp_diff_neutral":left-final["neutral"],
 "CX_frozen_end_vs_interp_diff_neutral":right-final["neutral"],
 "CX_RK32_vs_RK64_abs_error_neutral":errors["neutral"],
 "CX_RK32_vs_RK64_abs_error_ionized":errors["ionized"],
 "CX_RK32_vs_RK64_abs_error_eq160":errors["eq160"],
 "CX_electron_total_CX_excess_per_H_neutral":h_eff["neutral"]+ETA*final["neutral"]-x1-ETA*init["neutral"],
 "CX_electron_total_CX_excess_per_H_ionized":h_eff["ionized"]+ETA*final["ionized"]-x1-ETA*init["ionized"]
 }
 if list(columns)!=COLS:raise RuntimeError("SCIENCE_COLUMN_CONTRACT_MISMATCH")
 out.mkdir(parents=True,exist_ok=True)
 full=out/"R52_ORIGINAL_REI_F05_REAL_PROPER_D_CX_46080.csv.gz"
 write_gz(full,columns)
 stat={
 "nH_cm3":quant(density),"dt_s":dt,"original_z_mid_first_tick":z["source_first_z"],
 "theta_CX":quant(theta),
 "median_theta_CX":float(np.median(theta)),
 "N_theta_below_001":int(np.count_nonzero(theta<.01)),
 "N_theta_above_01":int(np.count_nonzero(theta>.1)),
 "N_theta_above_1":int(np.count_nonzero(theta>1.)),
 "source_HI_photo_exposure_approx_gamma_dt":z["source_gamma_HI"]*dt,
 "N_CX_exposure_below_source_HI_photo_diagnostic":int(np.count_nonzero(theta<z["source_gamma_HI"]*dt)),
 "source_initial_D_ratio_assumed":ETA,
 "source_H_N_total":float(np.sum(nh)),
 "assumed_total_D_N":float(ETA*np.sum(nh)),
 "initial_scenario":{},
 "RK32vsRK64_max_abs":{k:float(np.max(v)) for k,v in errors.items()},
 "source_interpolation_sensitivity_maxabs_y0_neutral":float(max(np.max(np.abs(left-final["neutral"])),np.max(np.abs(right-final["neutral"])))),
 "source_interpolation_sensitivity_median_y0_neutral":float(np.median(np.maximum(np.abs(left-final["neutral"]),np.abs(right-final["neutral"])))),
 "origin_tick160_vs_npz_H_count_all_exact":True
 }
 for key in init:
  stat["initial_scenario"][key]={
   "final_Dplus":quant(final[key]),
   "delta_Dplus":quant(final[key]-init[key]),
   "final_Dneutral_over_Hneutral":quant(columns["CX_Dneutral_over_Hneutral_final_"+key]),
   "net_CX_gas_heat_erg_per_H":quant(echange[key]),
   "heat_over_native_F05_abs_gain":quant(ratio[key]),
   "N_positive_gas_heat":int(np.count_nonzero(echange[key]>0)),
   "N_negative_gas_heat":int(np.count_nonzero(echange[key]<0)),
   "N_abs_heat_gt_1pct_original_F05":int(np.count_nonzero(np.abs(ratio[key])>.01)),
   "global_Dplus_N_start":float(np.dot(ETA*nh,init[key])),
   "global_Dplus_N_end":float(np.dot(ETA*nh,final[key])),
   "global_CX_heat_erg":float(np.dot(nh,echange[key]))
  }
 result={
 "schema":"WU_R52_REI_F05_ORIGINAL_PROPER_CLOCK_NH_D_CX_FINITE_TIME_V1",
 "science_status":"SOURCE_CONDITIONAL_REAL_DENSITY_ONE_TICK_NON_EQUILIBRIUM_CX_ONLY",
 "origin_REI_PR":352,"origin_REI_head":"ea8d6bf94197392c69f939f03c1673ed3afe349c",
 "origin_WU_PR":190,"origin_WU_head":"a42fa9113573a588ef2033ef6bbad2d9b3f87f94",
 "input_sha256":SHA,"original_source_tar_sha256":"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b",
 "original_accepted_array_sha256":"cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01",
 "MPC_CM":MPC_CM,"first_interval_source_forcing_z":z["source_first_z"],
 "first_interval_original_forcing_nodes":17,"original_total_ticks":DENOM_TICKS,
 "actual_original_nodes":N,"new_physics_column_count":len(columns),
 "model_contract":{
 "D_H_nuclei_ratio_eta":ETA,
 "underlying_original_rei_HHe_f05_tick160":"ACCEPTED",
 "tick161_HHe_material":"NONAUTHORITATIVE_PREVIEW_ONLY",
 "HII_and_logT_between_native_endpoints":"DECLARED_INTERPOLATION_NOT_SOURCE_STAGE_TRAJECTORY",
 "source_z_mid":"ORIGINAL_17_NODES_EQUAL_5p95",
 "D_CX_ionization_only":"SAVIN2002_PUBLISHED_47_RATE_PAIRS",
 "H_to_D_exchange_ion_charge":"TOTAL_HPLUS_DPLUS_CONSERVED_RELATIVE_TO_BASELINE",
 "donor_photon_feedback":"NOT_SOLVED",
 "D_photoionization_recombination":"OMITTED",
 "D_H2_HD_reactions":"OMITTED",
 "time_interval":"ONE_ORIGINAL_160_TO_161_NATIVE_F05_TICK_UNAPPROVED",
 "no_Einstein_Boltzmann_coupling":True,"no_real_cosmic_observation":True
 },
 "source_physics":stat,
 "output":{full.name:sha(full)},
 "DAG":{"WU":"34/49","REI_central":"28/88","REI_working":"33/88","fast":"4/7",
        "delta":0,"accepted_tick":"160/131072_HOLD"},
 "R6_C9_distinct_author":"NOT_RUN","native_subagent":"NOT_RUN","production":"HOLD",
 "no_main_merge":True,"auto_next":False
 }
 (out/"R52_RESULT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
 print(json.dumps({"nodes":N,"source_nH_cm3":stat["nH_cm3"],
      "theta":stat["theta_CX"],"below_001":stat["N_theta_below_001"],
      "above01":stat["N_theta_above_01"],
      "Gamma_HI_diagnostic":stat["source_HI_photo_exposure_approx_gamma_dt"],
      "neutral_y_final":stat["initial_scenario"]["neutral"]["final_Dplus"],
      "ionized_y_final":stat["initial_scenario"]["ionized"]["final_Dplus"],
      "RK64_vs32":stat["RK32vsRK64_max_abs"],
      "output":result["output"]},sort_keys=True))
 return result

if __name__=="__main__":
 import argparse
 parser=argparse.ArgumentParser()
 parser.add_argument("--out",type=Path,default=ROOT/"results")
 opt=parser.parse_args()
 run(opt.out)
