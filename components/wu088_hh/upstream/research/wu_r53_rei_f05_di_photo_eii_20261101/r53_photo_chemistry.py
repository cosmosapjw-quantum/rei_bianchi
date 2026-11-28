#!/usr/bin/env python3
"""WU R53: source-conditional photoionization+recombination+D/H charge exchange.

Real 46,080 REI F05 original source nodes, actual first tick proper time,
actual proper nH and H+He electron densities, original 17-node HI photon
forcing PCHIP, native H case A/B recombination coefficients, Savin original
47 paired atomic D/H charge-exchange rates. Unapproved REI tick161 endpoint
is ONLY a donor interpolation, not an accepted original IVP.
"""
from __future__ import annotations
import csv,gzip,hashlib,io,json,math
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
ROOT=Path(__file__).resolve().parent
SRC=ROOT/"sources"
N=46080
ETA=2.5e-5
DX_ERG=.0037*1.602176634e-12
MPC_CM=3.085677581491367e24
SOURCE_HEAD_REI="ea8d6bf94197392c69f939f03c1673ed3afe349c"
PARENT_WU="0f45a3a13c8bbf277804eacc3a80e822a39a0b18"
FNAME="R53_ORIGINAL_REI_F05_D_PHOTO_CX_46080.csv.gz"
KEYS=[
"node","W_node","proper_volume_cm3","nH_cm3","n_e_HHe_source160_cm3","n_e_HHe_preview161_cm3",
"source_T160_K","preview_T161_K","source_xHII160","preview_xHII161","first_F05_tick_dt_s",
"Gamma_HI_original_at160_s_inv","Gamma_HI_original_at161_s_inv",
"caseB_alphaHII_at160_cm3_s","caseA_alphaHII_at160_cm3_s",
"cx_only_R52_y_final_neutral","cx_only_R52_y_final_ionized",
"caseB_photo_y_final_neutral","caseB_photo_y_final_ionized","caseB_photo_y_final_CXeq160",
"caseA_photo_y_final_neutral","caseA_photo_y_final_ionized","caseA_photo_y_final_CXeq160",
"caseB_minus_CXonly_Dplus_neutral","caseB_minus_CXonly_Dplus_ionized",
"caseB_minus_caseA_Dplus_neutral","caseB_minus_caseA_Dplus_ionized",
"caseB_CX_integrated_per_D_neutral","caseB_D_photoionizations_per_D_neutral",
"caseB_D_recombinations_per_D_neutral","caseB_D_radio_net_ion_per_D_neutral",
"caseB_D_photoionizations_count_neutral","caseB_D_recombinations_count_neutral",
"caseB_D_photo_new_electron_per_H_neutral",
"caseB_D_electron_total_over_H_final_neutral",
"caseB_CX_Hion_change_per_H_neutral",
"caseB_CX_heat_erg_per_H_neutral",
"caseB_photo_latent_ion_count_per_H_neutral",
"caseB_D_photoionizations_per_D_ionized","caseB_D_recombinations_per_D_ionized",
"caseB_D_photo_new_electron_per_H_ionized","caseB_CX_heat_erg_per_H_ionized",
"caseB_RK32_vs64_abs_y_neutral",
"caseB_RK32_vs64_abs_y_ionized",
"caseA_RK32_vs64_abs_y_neutral",
"caseB_currentD_relative_H_photo_xHI_tick160"
]

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def require():
 c=json.loads((ROOT/"SOURCE_CONTRACT.json").read_text())
 for name,expected in c["original_REI_CX_relevant_source_shas"].items():
  if sha(SRC/name)!=expected:raise ValueError("ORIGINAL_BYTE_SOURCE_DRIFT_"+name)
 if c["origin_WU_parent_HEAD"]!=PARENT_WU or c["origin_REI_HEAD"]!=SOURCE_HEAD_REI:
  raise ValueError("ORIGINAL_GIT_AUTHORITY_CHANGED")
 return c

def savin(T,knots,forward,reverse):
 t=np.asarray(T)
 if np.any(~np.isfinite(t)) or np.any(t<2.7) or np.any(t>200000):
  raise ValueError("AUTHOR_SAVIN_RATE_T_DOMAIN")
 logt=np.log(t)
 return np.exp(np.interp(logt,knots,forward)),np.exp(np.interp(logt,knots,reverse))

def case_alpha(T,kind):
 if np.any(~np.isfinite(T)) or np.any(T<=0):raise ValueError("INVALID_T")
 ll=315614.0/T
 if kind=="B":
  return 2.753e-14*ll**1.5/(1+(ll/2.740)**.407)**2.242
 if kind=="A":
  return 1.269e-13*ll**1.503/(1+(ll/.522)**.470)**1.923
 raise ValueError("CASE_A_B_ONLY")

def load():
 require()
 with (SRC/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv").open() as f: table=list(csv.DictReader(f))
 if len(table)!=47:raise ValueError("SAVIN_ORIGINAL_TABLE_ROW_DRIFT")
 knots=np.log([float(x["T_K"]) for x in table])
 forward=np.log([float(x["k_forward_cm3_s"]) for x in table])
 reverse=np.log([float(x["k_reverse_cm3_s"]) for x in table])
 z=np.load(SRC/"initial_material_state_z6.npz",allow_pickle=False)
 W=z["W_node"]
 NH=z["N_HI"]+z["N_HII"]
 first=[]
 with (SRC/"canonical_time_resolved_forcing_nodes.csv").open() as f:
  first=[r for r in csv.DictReader(f) if int(r["interval_index"])==0]
 if len(first)!=17 or any(float(x["z_mid"])!=5.95 for x in first):
  raise ValueError("ORIGINAL_FIRST_INTERVAL_FORCING_CHANGED")
 times=np.array([float(x["time_s"]) for x in first])
 gammas=np.array([float(x["Gamma_HI_s-1"]) for x in first])
 dt=(times[-1]-times[0])/131072
 tleft=160*dt;tright=161*dt
 if abs(dt-4871848749.16828)>1e-2:raise ValueError("TICK_DURATION_MISMATCH")
 if np.any(gammas<0) or not np.all(np.diff(times)>0):
  raise ValueError("ORIGINAL_HI_PHOTO_FORCING_INVALID")
 gamma=PchipInterpolator(times,gammas,extrapolate=False)
 vol=W*MPC_CM**3/(1+5.95)**3
 if np.any(vol<=0):raise ValueError("PHYSICAL_VOLUME_NOT_POSITIVE")
 vals={k:[] for k in ("NH","T0","T1","x0","x1","ne0","ne1","baseR52neutral","baseR52ionized","baseR52eq")}
 with gzip.open(SRC/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz","rt") as f1, \
      gzip.open(SRC/"R52_ORIGINAL_REI_F05_REAL_PROPER_D_CX_46080.csv.gz","rt") as f2:
  a=csv.DictReader(f1);b=csv.DictReader(f2)
  for idx,(s,r) in enumerate(zip(a,b)):
   if idx!=int(s["node"]) or idx!=int(r["node"]):
    raise ValueError("REI_R52_SOURCE_NODE_ALIGNMENT")
   h=float(s["source_H_nuclei_N_lower"])
   if h!=NH[idx] or h!=float(r["original_NH_nuclei"]):
    raise ValueError("REI_SOURCE_H_NUCLEI_DIFFER")
   v=vol[idx]
   T0=float(r["original_tick160_T_K"])
   T1=float(r["preview_tick161_T_K"])
   x0=float(r["original_tick160_xHII"])
   x1=float(r["preview_tick161_xHII"])
   ne0=.5*(float(s["tick160_electron_count_N_lower"])+float(s["tick160_electron_count_N_upper"]))/v
   ne1=.5*(float(s["tick161_preview_electron_count_N_lower"])+float(s["tick161_preview_electron_count_N_upper"]))/v
   if not(0<ne0 and ne1>0 and ne0>=h/v*x0*(1-1e-13) and 0<x0<1 and 0<x1<1):
    raise ArithmeticError("NATIVE_REI_HHe_ELECTRON_OR_PHYSICAL_CONE")
   for key,value in dict(NH=h,T0=T0,T1=T1,x0=x0,x1=x1,ne0=ne0,ne1=ne1,
          baseR52neutral=float(r["CX_y_final_neutral"]),
          baseR52ionized=float(r["CX_y_final_ionized"]),
          baseR52eq=float(r["CX_y_final_eq160"])).items():
    vals[key].append(value)
 if len(vals["NH"])!=N:raise ValueError("REI_SOURCE_46K_ROWS_CHANGED")
 vals={k:np.asarray(v,dtype=float) for k,v in vals.items()}
 if np.any(vals["T0"]<2.7) or np.any(vals["T1"]>200000):
  raise ValueError("OUTSIDE_ORIGINAL_SAVIN_DOMAIN")
 vals.update(dict(W=np.asarray(W),vol=vol,nH=NH/vol,gamma=gamma,
                  dt=dt,tleft=tleft,tright=tright,
                  knots=knots,forward=forward,reverse=reverse,
                  count_forcing=17))
 return vals

def integrate(v,y0,case="B",steps=64,gamma_scale=1.,rr_scale=1.,cx_scale=1.,eta=ETA):
 """Four-component state: D+ fraction, net D ionized by CX, gross photon ion, gross RR.

 The H+ source adjusts for CX exactly x_eff=x_source-eta*q_CX. D free
 electrons = η nH(y-q_CX). Photon net electron change from initially
 D ion population is η nH[(y-y0)-q_CX] = η nH(q_photo-q_rr).
 """
 y=np.array(y0,dtype=float,copy=True)
 cx=np.zeros_like(y)
 photo=np.zeros_like(y)
 recomb=np.zeros_like(y)
 logratio=np.log(v["T1"]/v["T0"])
 ns=v["nH"]
 dt=v["dt"]
 def rhs(s,y,cx):
  x=v["x0"]+(v["x1"]-v["x0"])*s
  T=v["T0"]*np.exp(logratio*s)
  ne=v["ne0"]+(v["ne1"]-v["ne0"])*s
  xeff=x-eta*cx
  neeff=ne+eta*ns*(y-cx)
  if np.any(xeff<-1e-9) or np.any(xeff>1+1e-9) or np.any(yeff:=y<-1e-9) or np.any(y>1+1e-9) or np.any(neeff<=0):
   raise ArithmeticError("CX_D_PHOTO_PHYSICAL_CONE_EXIT")
  kf,kr=savin(T,v["knots"],v["forward"],v["reverse"])
  cxrate=cx_scale*ns*(kf*xeff*(1-y)-kr*(1-xeff)*y)
  a=case_alpha(T,case)
  ph=gamma_scale*v["gamma"](v["tleft"]+s*dt)*(1-y)
  rr=rr_scale*a*neeff*y
  return dt*(cxrate+ph-rr),dt*cxrate,dt*ph,dt*rr
 ds=1./steps
 for i in range(steps):
  s=i*ds
  y1,c1,p1,r1=rhs(s,y,cx)
  y2,c2,p2,r2=rhs(s+.5*ds,y+.5*ds*y1,cx+.5*ds*c1)
  y3,c3,p3,r3=rhs(s+.5*ds,y+.5*ds*y2,cx+.5*ds*c2)
  y4,c4,p4,r4=rhs(s+ds,y+ds*y3,cx+ds*c3)
  y+=ds*(y1+2*y2+2*y3+y4)/6
  cx+=ds*(c1+2*c2+2*c3+c4)/6
  photo+=ds*(p1+2*p2+2*p3+p4)/6
  recomb+=ds*(r1+2*r2+2*r3+r4)/6
 if np.any(~np.isfinite(y)) or np.any((y<0)|(y>1)):
  raise ArithmeticError("OUTPUT_DEUTERIUM_ION_PHYSICAL_CONE")
 residual=y-y0-cx-photo+recomb
 if np.max(np.abs(residual))>1e-12:raise ArithmeticError("D_ISOTOPE_TRANSITION_LEDGER_FAILED")
 return dict(y=y,cx=cx,photo=photo,recomb=recomb,ledger=residual)

def quant(x):
 x=np.asarray(x)
 return dict(min=float(x.min()),p05=float(np.percentile(x,5)),
     median=float(np.median(x)),p95=float(np.percentile(x,95)),max=float(x.max()))

def write_gz(path,fields):
 with path.open("wb") as raw:
  with gzip.GzipFile(fileobj=raw,mode="wb",filename="",mtime=0,compresslevel=6) as comp:
   with io.TextIOWrapper(comp,encoding="utf8",newline="") as f:
    w=csv.writer(f,lineterminator="\n")
    w.writerow(fields.keys())
    arrays=[np.asarray(x) for x in fields.values()]
    for i in range(N):
     w.writerow([i if a.dtype.kind in "iu" else format(float(a[i]),".17g") for a in arrays])

def run(out):
 v=load()
 dt=v["dt"]
 kf0,kr0=savin(v["T0"],v["knots"],v["forward"],v["reverse"])
 eq0=kf0*v["x0"]/(kf0*v["x0"]+kr0*(1-v["x0"]))
 init=dict(neutral=np.zeros(N),ionized=np.ones(N),eq160=eq0)
 calculated={};errors={};exps={}
 for typ in ["B","A"]:
  for key,y0 in init.items():
   cur=integrate(v,y0,case=typ,steps=64)
   half=integrate(v,y0,case=typ,steps=32)
   calculated[(typ,key)]=cur
   errors[(typ,key)]=np.abs(cur["y"]-half["y"])
   excess=ETA*(cur["y"]-cur["cx"]) # relative to original H+He source, initial D electrons included
   new=ETA*(cur["photo"]-cur["recomb"]) # newly created by D radiative only
   if np.max(np.abs(excess-ETA*y0-new))>3e-15:
    raise ArithmeticError("FREE_ELECTRON_NET_PHOTON_CX_IDENTITY")
   if np.any(v["x1"]-ETA*cur["cx"]<0) or np.any(v["x1"]-ETA*cur["cx"]>1):
    raise ArithmeticError("ORIGINAL_H_ION_D_CX_COMPENSATION_NOT_PHYSICAL")
   exps[(typ,key)]=(excess,new)
 # no-radiation regression exact only on v's original source temperature/H+ interpolation:
 ref=integrate(v,init["neutral"],case="B",steps=64,gamma_scale=0.,rr_scale=0.)
 no_radiation_regression=float(np.max(np.abs(ref["y"]-v["baseR52neutral"])))
 if no_radiation_regression>3e-12:
  raise ArithmeticError("EXACT_R52_SOURCE_CX_ONLY_RECOVERY_FAILED")
 a=calculated[("B","neutral")];ab=calculated[("B","ionized")]
 cols={
  "node":np.arange(N,dtype=np.int64),
  "W_node":v["W"],"proper_volume_cm3":v["vol"],"nH_cm3":v["nH"],
  "n_e_HHe_source160_cm3":v["ne0"],"n_e_HHe_preview161_cm3":v["ne1"],
  "source_T160_K":v["T0"],"preview_T161_K":v["T1"],
  "source_xHII160":v["x0"],"preview_xHII161":v["x1"],
  "first_F05_tick_dt_s":np.full(N,dt),
  "Gamma_HI_original_at160_s_inv":np.full(N,float(v["gamma"](v["tleft"]))),
  "Gamma_HI_original_at161_s_inv":np.full(N,float(v["gamma"](v["tright"]))),
  "caseB_alphaHII_at160_cm3_s":case_alpha(v["T0"],"B"),
  "caseA_alphaHII_at160_cm3_s":case_alpha(v["T0"],"A"),
  "cx_only_R52_y_final_neutral":v["baseR52neutral"],
  "cx_only_R52_y_final_ionized":v["baseR52ionized"],
  "caseB_photo_y_final_neutral":a["y"],
  "caseB_photo_y_final_ionized":ab["y"],
  "caseB_photo_y_final_CXeq160":calculated[("B","eq160")]["y"],
  "caseA_photo_y_final_neutral":calculated[("A","neutral")]["y"],
  "caseA_photo_y_final_ionized":calculated[("A","ionized")]["y"],
  "caseA_photo_y_final_CXeq160":calculated[("A","eq160")]["y"],
  "caseB_minus_CXonly_Dplus_neutral":a["y"]-v["baseR52neutral"],
  "caseB_minus_CXonly_Dplus_ionized":ab["y"]-v["baseR52ionized"],
  "caseB_minus_caseA_Dplus_neutral":a["y"]-calculated[("A","neutral")]["y"],
  "caseB_minus_caseA_Dplus_ionized":ab["y"]-calculated[("A","ionized")]["y"],
  "caseB_CX_integrated_per_D_neutral":a["cx"],
  "caseB_D_photoionizations_per_D_neutral":a["photo"],
  "caseB_D_recombinations_per_D_neutral":a["recomb"],
  "caseB_D_radio_net_ion_per_D_neutral":a["photo"]-a["recomb"],
  "caseB_D_photoionizations_count_neutral":ETA*v["NH"]*a["photo"] if "NH" in v else ETA*v["nH"]*v["vol"]*a["photo"],
  "caseB_D_recombinations_count_neutral":ETA*v["nH"]*v["vol"]*a["recomb"],
  "caseB_D_photo_new_electron_per_H_neutral":exps[("B","neutral")][1],
  "caseB_D_electron_total_over_H_final_neutral":exps[("B","neutral")][0],
  "caseB_CX_Hion_change_per_H_neutral":-ETA*a["cx"],
  "caseB_CX_heat_erg_per_H_neutral":-ETA*DX_ERG*a["cx"],
  "caseB_photo_latent_ion_count_per_H_neutral":exps[("B","neutral")][1],
  "caseB_D_photoionizations_per_D_ionized":ab["photo"],
  "caseB_D_recombinations_per_D_ionized":ab["recomb"],
  "caseB_D_photo_new_electron_per_H_ionized":exps[("B","ionized")][1],
  "caseB_CX_heat_erg_per_H_ionized":-ETA*DX_ERG*ab["cx"],
  "caseB_RK32_vs64_abs_y_neutral":errors[("B","neutral")],
  "caseB_RK32_vs64_abs_y_ionized":errors[("B","ionized")],
  "caseA_RK32_vs64_abs_y_neutral":errors[("A","neutral")],
  "caseB_currentD_relative_H_photo_xHI_tick160":ETA*(1-init["neutral"])*float(v["gamma"](v["tleft"]))/(v["gamma"](v["tleft"])*np.maximum(1-v["x0"],1e-300))
 }
 # The source contract includes old source nucleus count in volume;nH.
 if len(cols)!=len(set(cols)):raise ArithmeticError("COLUMN_REPEATED")
 out.mkdir(parents=True,exist_ok=True)
 full=out/FNAME
 write_gz(full,cols)
 result={
 "schema":"WU_R53_ORIGINAL_REI_F05_46K_HI_CLONE_D_PHOTO_CASEA_B_CX_TRANSIENT_V1",
 "scientific_state":"SOURCE_CONDITIONAL_26EVENT_F05_160_TO_161_D_PHOTO_CX_4_STATE_NON_EQUILIBRIUM",
 "source_SHA256":require()["original_REI_CX_relevant_source_shas"],
 "source_WU_parent_PR":192,"source_WU_HEAD":PARENT_WU,
 "REI_original_preview_PR":352,"REI_original_HEAD":SOURCE_HEAD_REI,
 "physical_scope":"Original 46080 real cell native HHe electrons+nH+proper clock, Savin original D/H rates and cloned native HI photo/recomb (A/B) model.",
 "assumptions":{
  "eta_D_assumed":ETA,
  "HI_equals_DI_photo_Savin2002_approximation":True,
  "HII_recomb_AorB_clone_for_DI":True,
  "case_B_primary_from_original_REI_native_OTS":True,
  "case_A_alternative_total_RR":True,
  "DI_photo_gamma_not_independently_source_spectrum_computed":True,
  "gamma_HI_first17_native_forcing_PCHIP_not_local_D_ray":True,
  "source_HHe_T_between160_161":"LINEAR_HII_LOG_LINEAR_T_LINEAR_ELECTRON_DENSITY",
  "original_tick161":"PREVIEW_NOT_ACCEPTED",
  "D_gas_heating_from_photon_energy":"NOT_COMPUTED",
  "gas_heat_only_CX_3p7meV":"CANDIDATE",
  "no_HD_no_further_molecules":True,
  "no_global_photon_feedback":True,"no_Einstein_Boltzmann_backreaction":True
 },
 "numerical":{
  "native_real_cells":N,"columns":len(cols),"original_tick_dt_s":dt,
  "source_Gamma_HI_160_s_inv":float(v["gamma"](v["tleft"])),
  "source_Gamma_HI_161_s_inv":float(v["gamma"](v["tright"])),
  "source_gamma_HI_one_tick_exposure":float(v["gamma"](v["tleft"])*dt),
  "original_source_electron_cm3":quant(v["ne0"]),
  "H_caseB_recomb_cm3_s":quant(case_alpha(v["T0"],"B")),
  "H_caseA_recomb_cm3_s":quant(case_alpha(v["T0"],"A")),
  "cx_only_R52_neutral_median":float(np.median(v["baseR52neutral"])),
  "no_radiation_R52_CX_only_max_abs_y_regression":no_radiation_regression,
  "case_B_final_Dplus":{key:quant(calculated[("B",key)]["y"]) for key in init},
  "case_A_final_Dplus":{key:quant(calculated[("A",key)]["y"]) for key in init},
  "case_B_minus_CXonly":{key:quant(calculated[("B",key)]["y"]-v["baseR52"+key if key!="eq160" else "baseR52eq"]) for key in init},
  "case_B_minus_case_A":{key:quant(calculated[("B",key)]["y"]-calculated[("A",key)]["y"]) for key in init},
  "case_B_photons_per_D":{key:quant(calculated[("B",key)]["photo"]) for key in init},
  "case_B_recombinations_per_D":{key:quant(calculated[("B",key)]["recomb"]) for key in init},
  "case_B_isotope_CX_heat_erg_per_H":{key:quant(-ETA*DX_ERG*calculated[("B",key)]["cx"]) for key in init},
  "case_B_new_electrons_due_to_D_photo_per_H":{key:quant(exps[("B",key)][1]) for key in init},
  "max_D_transition_bookkeeping_abs_residual":max(float(np.max(np.abs(calculated[(kind,key)]["ledger"]))) for kind in ("A","B") for key in init),
  "max_RK32_vs_RK64_y_abs":{kind+"_"+key:float(np.max(errors[(kind,key)])) for kind in ("A","B") for key in init},
  "D_photo_count_global_neutral":float(np.sum(ETA*v["nH"]*v["vol"]*a["photo"])),
  "D_recomb_count_global_neutral":float(np.sum(ETA*v["nH"]*v["vol"]*a["recomb"])),
  "D_CX_count_global_neutral":float(np.sum(ETA*v["nH"]*v["vol"]*a["cx"])),
  "net_D_photon_electron_count_global_neutral":float(np.sum(ETA*v["nH"]*v["vol"]*(a["photo"]-a["recomb"]))),
  "all_cells_solved_without_extrapolation":N
 },
 "output_SHA256":{FNAME:sha(full)},
 "DAG":{"WU":"34/49","REI_central":"28/88","REI_working":"33/88","fast":"4/7","delta":0,"original_F05_tick":"160/131072"},
 "original_admission":"NOT_GRANTED",
 "distinct_author_review":"NOT_RUN",
 "native_subagent":"NOT_RUN",
 "no_merge":True,"production":"HOLD","auto_next_node":False
 }
 (out/"R53_RESULTS.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"cells":N,"source_gamma":result["numerical"]["source_gamma_HI_one_tick_exposure"],
   "R52_CXonly_median":result["numerical"]["cx_only_R52_neutral_median"],
   "caseB_neutral":result["numerical"]["case_B_final_Dplus"]["neutral"],
   "caseB_delta_vs_R52":result["numerical"]["case_B_minus_CXonly"]["neutral"],
   "caseB_vs_caseA":result["numerical"]["case_B_minus_case_A"]["neutral"],
   "all_row_CX_only_recovered_maxabs":no_radiation_regression,
   "sha256":result["output_SHA256"][FNAME]},sort_keys=True))
 return result

if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,default=ROOT/"results")
 args=p.parse_args()
 run(args.out)
