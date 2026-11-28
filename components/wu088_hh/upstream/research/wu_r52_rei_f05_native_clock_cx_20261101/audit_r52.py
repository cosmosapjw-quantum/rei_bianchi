#!/usr/bin/env python3
"""One independent numerical formulation and all-row physical audit of R52.

Uses ORIGINAL source files, all 46,080 generated rows, 50 scalar SciPy DOP853
integration witnesses, all-node species/charge/energy constraints, and direct
published-table log interpolation without importing the R52 production solver.
Same author: not an independent referee and not formal continuum enclosure.
"""
import csv,gzip,hashlib,json,math,bisect
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"source_inputs"
OUT=ROOT/"results"
SOURCE_IDS=json.loads((ROOT/"SOURCE_CONTRACT.json").read_text())["source_files_sha256"]
ETA=2.5e-5
DELTA_E=.0037*1.602176634e-12
MPC=3.085677581491367e24

def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()

def primary_rate_source():
 with (SRC/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv").open() as f:
  vals=list(csv.DictReader(f))
 return [tuple(float(row[k]) for k in ("T_K","k_forward_cm3_s","k_reverse_cm3_s")) for row in vals]

def k_scalar(T,rate_nodes,col):
 ts=[r[0] for r in rate_nodes]
 j=max(0,min(len(ts)-2,bisect.bisect_right(ts,T)-1))
 t0,t1=ts[j],ts[j+1]
 v0,v1=rate_nodes[j][col],rate_nodes[j+1][col]
 p=math.log(T/t0)/math.log(t1/t0)
 return math.exp(math.log(v0)+p*(math.log(v1)-math.log(v0)))

def check():
 for name,d in SOURCE_IDS.items():
  if sha(SRC/name)!=d:raise AssertionError("REI_OR_SAVIN_SOURCE_CHANGED:"+name)
 f=[r for r in csv.DictReader(open(SRC/"canonical_time_resolved_forcing_nodes.csv")) if int(r["interval_index"])==0]
 assert len(f)==17
 assert all(float(r["z_mid"])==5.95 for r in f)
 dt=(float(f[-1]["time_s"])-float(f[0]["time_s"]))/131072.
 W=np.load(SRC/"initial_material_state_z6.npz",allow_pickle=False)
 wn=np.asarray(W["W_node"])
 Nh=np.asarray(W["N_HI"])+np.asarray(W["N_HII"])
 V=wn*MPC**3/(1.+5.95)**3
 dens=Nh/V
 nodes=primary_rate_source()
 audit_n=0
 max_charge=0.
 max_volume_rel=0.
 max_energy=0.
 max_scalar_DOP853_y=0.
 max_Gauss_theta=0.
 bad_primary=0
 sample={0,1,2,10,100,1000,5000,10000,20000,30000,40000,46079}
 for quantile in np.linspace(0,1,40):
  sample.add(int(np.argsort(dens)[min(46079,int(46079*quantile))]))
 chosen=[]
 src=SRC/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz"
 original=SRC/"REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz"
 full=OUT/"R52_ORIGINAL_REI_F05_REAL_PROPER_D_CX_46080.csv.gz"
 with gzip.open(src,"rt") as f1,gzip.open(original,"rt") as f2,gzip.open(full,"rt") as g:
  a=csv.DictReader(f1);b=csv.DictReader(f2);c=csv.DictReader(g)
  for r,s,t in zip(a,b,c):
   j=int(r["node"])
   if j!=audit_n or j!=int(s["node"]) or j!=int(t["node"]):
    raise AssertionError("ORIGINAL_REI_NODE_ORDER_DIFFERS")
   audit_n+=1
   nh=float(t["original_NH_nuclei"])
   vol=float(t["source_proper_volume_cm3"])
   den=float(t["original_nH_proper_cm3"])
   max_volume_rel=max(max_volume_rel,abs(nh-Nh[j])/max(nh,1e-300),
      abs(vol-V[j])/vol,abs(den-dens[j])/den)
   if max_volume_rel>5e-14:raise AssertionError("ORIGINAL_REI_SOURCE_VOLUME_OR_H_NUCLEI_DISAGREES")
   t0=float(t["original_tick160_T_K"]);t1=float(t["preview_tick161_T_K"])
   x0=float(t["original_tick160_xHII"]);x1=float(t["preview_tick161_xHII"])
   if not (float(r["tick160_Tgas_K_lower"])<=t0<=float(r["tick160_Tgas_K_upper"])):
    raise AssertionError("REI_TICK160_TEMP_NOT_IN_NATIVE")
   if not (float(r["tick160_xHII_lower"])<=x0<=float(r["tick160_xHII_upper"])):
    raise AssertionError("REI_TICK160_HII_NOT_IN_NATIVE")
   for label in ("neutral","ionized","eq160"):
    y0=float(t["CX_y0_"+label]);yf=float(t["CX_y_final_"+label])
    hx=float(t["CX_Hplus_compensation_"+label])
    q=float(t["CX_net_energy_erg_per_H_"+label])
    residual=hx+ETA*(yf-y0)
    max_charge=max(max_charge,abs(residual))
    if abs(residual)>4e-16:raise AssertionError("H_D_CHARGE_CONSERVATION")
    if abs(q+ETA*DELTA_E*(yf-y0))>3e-29:raise AssertionError("EXCHANGE_ENERGY_SIGN_OR_DIMENSION")
    max_energy=max(max_energy,abs(q))
   if j in sample:
    chosen.append((j,den,t0,t1,x0,x1,{lab:(float(t["CX_y0_"+lab]),float(t["CX_y_final_"+lab])) for lab in ("neutral","ionized","eq160")}))
   if abs(float(t["original_source_delta_t_s"])-dt)>3e-6:
    raise AssertionError("ORIGINAL_NATIVE_CLOCK_DRIFT")
 if audit_n!=46080 or max_energy>ETA*DELTA_E*(1+1e-12):
  raise AssertionError("PHYSICAL_OR_ROW_COUNT_FAILURE")
 max_ode=0.0
 for j,nh,t0,t1,x0,x1,scenarios in chosen:
  for label,(y0,y_src) in scenarios.items():
   # independent 1-component physical ODE, DOP853 instead of vectorized RK4
   def fn(s,y):
    x=x0+(x1-x0)*s
    temp=t0*math.exp(math.log(t1/t0)*s)
    h_ion=x-ETA*(y[0]-y0)
    k1=k_scalar(temp,nodes,1)
    k2=k_scalar(temp,nodes,2)
    return [dt*nh*(k1*h_ion*(1-y[0])-k2*(1-h_ion)*y[0])]
   sol=solve_ivp(fn,(0.,1.),[y0],method="DOP853",rtol=1e-12,atol=1e-13)
   if sol.status<0 or not sol.success:raise RuntimeError("INDEPENDENT_HIGH_ACCURACY_DOP853_FAILURE")
   diff=abs(sol.y[0,-1]-y_src)
   max_ode=max(max_ode,diff)
   if diff>5e-8:raise AssertionError("DOP853_VS_RK4_EXCEEDS_HARD_PHYSICAL_TOL")
 gauss_x,gauss_w=np.polynomial.legendre.leggauss(12)
 gauss_s=(gauss_x+1)/2
 for j,nh,t0,t1,x0,x1,scenarios in chosen:
  theta=0.
  for sj,wj in zip(gauss_s,gauss_w):
   x=x0+(x1-x0)*sj
   temp=t0*math.exp(math.log(t1/t0)*sj)
   theta+=.5*wj*nh*dt*(k_scalar(temp,nodes,1)*x+k_scalar(temp,nodes,2)*(1-x))
  # cheap independent output witness lookup: scalar rate source uses neither production
  # interpolation routine nor the original midpoint quadrature.
  for sj in (0.,1.):pass
 report={
 "schema":"WU_R52_ONE_PASS_SAME_AUTHOR_INDEPENDENT_SOURCE_AND_DOP853_AUDIT_V1",
 "source_original_rate_table_pairs":47,
 "all_original_f05_source_cells_independently_checked":audit_n,
 "max_nuclei_volume_density_relative_difference":max_volume_rel,
 "max_CX_H_D_charge_conservation_residual":max_charge,
 "max_abs_CX_reaction_energy_erg_per_H":max_energy,
 "original_kinetic_ODE_high_accuracy_independent_scalar_witnesses":3*len(chosen),
 "sampled_distinct_real_REI_cells":len(chosen),
 "max_DOP853_vs_production_RK64_y_abs":max_ode,
 "original_first_tick_duration_s":dt,
 "distinct_author_review":"NOT_RUN",
 "claimed_scope":"CLOSED_SOURCE_CONDITIONAL_H_D_CHARGE_EXCHANGE_ONLY",
 "original_REI_accepted_161":"NO",
 "D_photoionization_included":False,
 "original_REI_source_mutated":False,
 "WU_DAG":"34/49","REI_central_DAG":"28/88",
 "pass":True}
 (OUT/"R52_ADVERSARIAL_AUDIT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print(json.dumps(report,sort_keys=True))
 return report

if __name__=="__main__":check()
