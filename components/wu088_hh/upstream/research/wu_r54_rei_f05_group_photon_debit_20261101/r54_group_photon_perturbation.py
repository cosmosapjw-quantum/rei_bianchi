#!/usr/bin/env python3
"""WU R54 | Conservative original F05 photon-group perturbation by atomic D photoabsorption.

Real 46,080 native F05 H/He donor cells, native 17-node source N_g, A_g, Gamma_HI,
original Verner HI group cross sections averaged with *original* E^-2.5 within-group
spectrum, Savin original D/H CX, native H RR B and EII source equivalents.
A conservative photon-number DI correction about unchanged original
photon/HHe history is solved simultaneously with two explicit D ICs.

NOT full original REI four-group radiative transfer or newly admitted tick161.
"""
from __future__ import annotations
import csv,gzip,hashlib,io,json,math
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator

ROOT=Path(__file__).resolve().parent
INPUT=ROOT/"source_inputs"
N=46080
ETA_D=2.5e-5
DELTA_CX_EV=.0037
CHI_H_SOURCE_EV=13.60
CHI_D_PHYS_EV=13.6017
DELTA_DI_THRESHOLD_VS_REI_H_SOURCE=CHI_D_PHYS_EV-CHI_H_SOURCE_EV
EV_ERG=1.602176634e-12
MPC_CM=3.085677581491367e24
C_CM_S=2.99792458e10
GROUPS=("G1","G2a","G2b","G3")
BOUNDS=((13.60,24.59),(24.59,39.50),(39.50,54.42),(54.42,100.0))
PUB_SIGMA_PARAMS=(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.)
FILENAME="R54_REI_F05_DI_GROUP_CONSERVATIVE_46080.csv.gz"
COLS=["node","original_H_N","proper_nH_cm3","original_T160_K","original_xHII160","preview_T161_K",
      "source_electron_ne160_cm3","original_F05_thermal_gain_erg_per_H",
      "DI_initial_neutral_y_final_group_coupled","DI_initial_neutral_y_final_original_gamma",
      "DI_initial_neutral_delta_y_from_photon_debit",
      "DI_initial_ionized_y_final_group_coupled","DI_initial_ionized_y_final_original_gamma",
      "DI_initial_neutral_CX_per_D","DI_initial_neutral_RR_per_D",
      "DI_initial_neutral_EII_per_D",
      "DI_neutral_photon_G1_per_D","DI_neutral_photon_G2a_per_D","DI_neutral_photon_G2b_per_D","DI_neutral_photon_G3_per_D",
      "DI_neutral_photon_all_per_D","DI_neutral_new_electrons_photo_EII_recomb_per_H",
      "DI_neutral_CX_Hplus_shift_per_H","DI_neutral_EII_electron_per_H",
      "DI_neutral_CX_heat_erg_per_H","DI_neutral_EII_threshold_sink_erg_per_H",
      "DI_neutral_photo_latent_energy_erg_per_H",
      "DI_neutral_photoelectron_gross_heat_erg_per_H",
      "DI_neutral_gross_photo_heat_over_native_abs_DeltaU",
      "DI_neutral_photo_threshold_plus_excess_erg_per_H",
      "DI_neutral_photon_energy_bookkeeping_residual_erg_per_H",
      "DI_neutral_charge_total_electron_residual_per_H",
      "DI_initial_ionized_photon_G1_per_D","DI_initial_ionized_photon_G2a_per_D",
      "DI_initial_ionized_photon_G2b_per_D",
      "DI_initial_neutral_isotope_5flux_ledger_residual"]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def qq(a):
 v=np.asarray(a)
 return {"min":float(np.min(v)),"p05":float(np.percentile(v,5)),
         "median":float(np.median(v)),"p95":float(np.percentile(v,95)),
         "max":float(np.max(v))}
def verner(E):
 eth,e0,sigma0,ya,p,yw,y0,y1=PUB_SIGMA_PARAMS
 e=float(E)
 if e<eth:return 0.
 x=e/e0-y0
 y=math.sqrt(x*x+y1*y1)
 return 1.e-18*sigma0*((x-1)**2+yw*yw)*y**(.5*p-5.5)/(1+math.sqrt(y/ya))**p
def sigma_and_energy():
 sig=[];means=[];alt=[]
 for a,b in BOUNDS:
  norm=quad(lambda E:E**-2.5,a,b,epsabs=0,epsrel=2e-10)[0]
  integral=quad(lambda E:E**-2.5*verner(E),a,b,epsabs=0,epsrel=3e-10,limit=150)[0]
  eint=quad(lambda E:E**-1.5*verner(E),a,b,epsabs=0,epsrel=3e-10,limit=150)[0]
  if integral<=0:raise ArithmeticError("SOURCE_PHOTON_SIGMA_NONPOSITIVE")
  sig.append(integral/norm)
  means.append(eint/integral)
  # Sensitivity: a small isotope threshold translation only, NOT a computed
  # deuterium ab-initio photoionization cross section.
  thr=CHI_D_PHYS_EV
  shifted=quad(lambda E:E**-2.5*verner(E-DELTA_DI_THRESHOLD_VS_REI_H_SOURCE),
               max(a,thr),b,epsabs=0,epsrel=3e-9,limit=150)[0]
  alt.append(shifted/norm)
 return np.array(sig),np.array(means),np.array(alt)
def load():
 contract=json.loads((ROOT/"SOURCE_CONTRACT.json").read_text())
 if contract["WU_parent_HEAD"]!="6f2f532b46ea153795d6aebeed7b73765b6482ac":
  raise ValueError("SOURCE_PROTECTED_WU_PARENT_CHANGED")
 for name,digest in contract["source_sha256"].items():
  if sha(INPUT/name)!=digest:raise ValueError("SOURCE_BYTE_SHA256_CHANGED_"+name)
 spec=(INPUT/"REI_original_b2b_physical_model.py").read_text()
 for text in ["[13.60, 24.59]","[24.59, 39.50]","[39.50, 54.42]","[54.42, 100.0]",
              '"HI": (13.60, 0.4298, 5.475e4, 32.88, 2.963, 0.0, 0.0, 0.0)']:
  if text not in spec:raise ValueError("REI_ORIGINAL_VERNER_SOURCE_CONTRACT_CHANGED")
 sig,meanE,altsig=sigma_and_energy()
 with open(INPUT/"canonical_time_resolved_forcing_nodes.csv") as f:
  original=[r for r in csv.DictReader(f) if int(r["interval_index"])==0]
 if len(original)!=17 or any(float(r["z_mid"])!=5.95 for r in original):
  raise ValueError("F05_FIRST_INTERVAL_FORCING_NODES_CHANGED")
 times=np.array([float(r["time_s"]) for r in original])
 dt=(times[-1]-times[0])/131072
 if abs(dt-4871848749.16828)>.05 or not np.all(np.diff(times)>0):raise ValueError("SOURCE_CLOCK_DRIFT")
 t0=160*dt;t1=161*dt
 photon_N=np.array([[float(r["N_"+g+"_cMpc-3"]) for g in GROUPS] for r in original])
 photon_A=np.array([[float(r["absorption_"+g+"_s-1_cMpc-3"]) for g in GROUPS] for r in original])
 if not(np.all(photon_N[:,:3]>0) and np.all(photon_A[:,:3]>=0) and np.all(photon_N[:,3]==0) and np.all(photon_A[:,3]==0)):
  raise ValueError("ORIGINAL_SOURCE_PHOTON_G3_ZERO_AND_THREE_ACTIVE_GROUPS_VIOLATED")
 source_gamma=np.array([float(r["Gamma_HI_s-1"]) for r in original])
 pref=C_CM_S*(1+5.95)**3/MPC_CM**3
 pred=(photon_N@sig)*pref
 rel=np.max(np.abs(pred-source_gamma)/source_gamma)
 if rel>5e-12:raise ArithmeticError("ORIGINAL_REI_GROUP_RESOLVED_HI_GAMMA_NOT_REPRODUCED")
 gam=PchipInterpolator(times,source_gamma,extrapolate=False)
 NG=PchipInterpolator(times,photon_N,axis=0,extrapolate=False)
 AG=PchipInterpolator(times,photon_A,axis=0,extrapolate=False)
 with (INPUT/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv").open() as f:
  rs=list(csv.DictReader(f))
 if len(rs)!=47:raise ValueError("SAVIN_ORIGINAL_TABLE_COUNT_CHANGED")
 Tk=np.log([float(r["T_K"]) for r in rs])
 Kf=np.log([float(r["k_forward_cm3_s"]) for r in rs])
 Kr=np.log([float(r["k_reverse_cm3_s"]) for r in rs])
 init=np.load(INPUT/"initial_material_state_z6.npz",allow_pickle=False)
 W=np.asarray(init["W_node"],float)
 NH=np.asarray(init["N_HI"]+init["N_HII"],float)
 V=W*MPC_CM**3/(1+5.95)**3
 if np.any(V<=0) or abs(float(W.sum())-1)>3e-14:raise ValueError("PHYSICAL_CELL_VOLUME_INVALID")
 src=INPUT/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz"
 baseline=INPUT/"R53_REI_F05_EII_SOURCE_SENSITIVITY_46080.csv.gz"
 vals={k:[] for k in ("T0","T1","x0","x1","ne0","ne1","R53_neutral","R53_ionized","dU")}
 with gzip.open(src,"rt") as ff,gzip.open(baseline,"rt") as bg,gzip.open(INPUT/"REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz","rt") as eg:
  aa,bb,cc=csv.DictReader(ff),csv.DictReader(bg),csv.DictReader(eg)
  for idx,(a,b,c) in enumerate(zip(aa,bb,cc)):
   if int(a["node"])!=idx or int(b["node"])!=idx or int(c["node"])!=idx:
    raise ValueError("THREE_ORIGINAL_SOURCE_REI_NODE_ALIGNMENT_BROKEN")
   if float(a["source_H_nuclei_N_lower"])!=NH[idx]:
    raise ValueError("ORIGINAL_REI_SOURCE_H_NUCLEI_MISMATCH")
   T0=float(b["original_T160_K"]);T1=.5*(float(a["tick161_preview_Tgas_K_lower"])+float(a["tick161_preview_Tgas_K_upper"]))
   x0=.5*(float(a["tick160_xHII_lower"])+float(a["tick160_xHII_upper"]))
   x1=.5*(float(a["tick161_preview_xHII_lower"])+float(a["tick161_preview_xHII_upper"]))
   # Use R53 original parent x0 center as the true donor, not a rounded
   # interval midpoint; source x0 may lie within the original strict interval.
   x0_native=float(b["caseB_withEII_neutral_y"])*0+x0
   ne0=float(b["original_n_e_HHe160_cm3"])
   ne1=.5*(float(a["tick161_preview_electron_count_N_lower"])+float(a["tick161_preview_electron_count_N_upper"]))/V[idx]
   if not(2.7<=T0<=2e5 and 2.7<=T1<=2e5 and 0<x0<1 and 0<x1<1 and ne0>0 and ne1>0):
    raise ValueError("SOURCE_PHYSICAL_T_X_NE_CONE_FAIL")
   for key,value in {
    "T0":T0,"T1":T1,"x0":x0_native,"x1":x1,"ne0":ne0,"ne1":ne1,
    "R53_neutral":float(b["caseB_withEII_neutral_y"]),
    "R53_ionized":float(b["caseB_withEII_ionized_y"]),
    "dU":float(c["thermal_energy_gain_twohalf_center_erg_per_H"])
   }.items():vals[key].append(value)
 if len(vals["T0"])!=N:raise ValueError("ORIGINAL_REI_46080_SOURCE_LENGTH_FAIL")
 vals={k:np.asarray(v) for k,v in vals.items()}
 vals.update(dict(NH=NH,W=W,V=V,nH=NH/V,rateTk=Tk,ratekf=Kf,ratekr=Kr,
    times=times,source_gam=gam,source_N=NG,source_A=AG,
    source_Gamma_samples=source_gamma,dt=dt,t0=t0,t1=t1,
    sigma=sig,meanE=meanE,alt_sigma=altsig,pref=pref,
    gamma_source_all17_max_rel=rel))
 if np.any(vals["dU"]==0):raise ValueError("SOURCE_NATIVE_THERMAL_INCREMENT_ZERO")
 return vals
def rates(T,v):
 if np.any(T<2.7) or np.any(T>200000):raise ArithmeticError("AUTHOR_SAVIN_T_OUTSIDE_ORIGINAL_DOMAIN")
 s=np.log(T)
 return np.exp(np.interp(s,v["rateTk"],v["ratekf"])),np.exp(np.interp(s,v["rateTk"],v["ratekr"]))
def alpha_B(T):
 l=315614./T
 return 2.753e-14*l**1.5/(1+(l/2.740)**.407)**2.242
def beta_H(T):
 return 5.835e-11*np.sqrt(T)*np.exp(-157804./T)
def source_at(v,s):
 t=v["t0"]+v["dt"]*s
 N0=np.asarray(v["source_N"](t))
 A0=np.asarray(v["source_A"](t))
 # Original G3 source has N=0 and A=0 in all 17 samples.
 if np.any(N0[:3]<=0) or not(N0[3]==0 and A0[3]==0):raise ArithmeticError("G3_ZERO_SOURCE_IDENTITY_BROKEN")
 p=N0*v["sigma"]
 weight=p/np.sum(p)
 n_g=np.maximum(N0[:3],1e-300)
 lam=np.zeros(4);lam[:3]=np.maximum(A0[:3],0)/n_g
 gamma=np.asarray(v["source_gam"](t))
 if not math.isfinite(float(gamma)) or gamma<=0:raise ValueError("ORIGINAL_HI_GAMMA_INVALID")
 return N0,A0,lam,float(gamma),weight
def derivative(v,s,y,cx,rr,eii,Pcell,D,B,feedback=True):
 N0,A0,lam,sourcegam,w=source_at(v,s)
 if feedback:
  dfrac=np.zeros(4);dfrac[:3]=D[:3]/N0[:3]
 else:dfrac=np.zeros(4)
 if np.any(dfrac< -1e-13) or np.any(dfrac[:3]>1.):
  raise ArithmeticError("ORIGINAL_PHOTON_GROUP_DEPLETION_OUTSIDE_CONE")
 gam_g=sourcegam*w*(1-dfrac)
 gam=float(np.sum(gam_g))
 x=v["x0"]+(v["x1"]-v["x0"])*s
 T=v["T0"]*np.exp(np.log(v["T1"]/v["T0"])*s)
 ne=v["ne0"]+(v["ne1"]-v["ne0"])*s
 h_ion=x-ETA_D*cx
 eff_ne=ne+ETA_D*v["nH"]*(y-cx)
 if np.any(y<-2e-9) or np.any(y>1+2e-9) or np.any(h_ion<-2e-9) or np.any(h_ion>1+2e-9) or np.any(eff_ne<=0):
  raise ArithmeticError("SOURCE_ISOTOPE_ION_CHARGE_CONE_INVALID")
 kf,kr=rates(T,v)
 cm=v["nH"]*(kf*h_ion*(1-y)-kr*(1-h_ion)*y)
 pr=alpha_B(T)*eff_ne*y
 ei=beta_H(T)*eff_ne*(1-y)
 p_group=gam_g[:3,None]*(1-y)[None,:] # photons per D per second
 ptotal=p_group.sum(axis=0)
 derivatives=[v["dt"]*(cm+ptotal+ei-pr),v["dt"]*cm,v["dt"]*pr,v["dt"]*ei,
    v["dt"]*p_group]
 # Total new DI photoabsorption photons from true original cells per comoving-Mpc3.
 source_p=np.zeros(4)
 source_p[:3]=ETA_D*v["dt"]*(p_group@v["NH"])
 if feedback:
  dD=source_p-v["dt"]*lam*D
  dB=v["dt"]*lam*D
 else:
  dD=np.zeros(4);dB=np.zeros(4)
 return derivatives,dD,dB,gam_g
def evolve(v,y_initial,steps=64,feedback=True,record=False):
 y=y_initial.copy()
 cx=np.zeros(N);rr=np.zeros(N);eii=np.zeros(N);Pcell=np.zeros((3,N))
 D=np.zeros(4);B=np.zeros(4)
 traj=[]
 def apply(y,cx,rr,eii,Pcell,D,B,K,h):
  derivative_local,dD,dB,_=K
  return (y+h*derivative_local[0],
          cx+h*derivative_local[1],
          rr+h*derivative_local[2],
          eii+h*derivative_local[3],
          Pcell+h*derivative_local[4],
          D+h*dD,B+h*dB)
 step=1./steps
 for j in range(steps):
  s=j*step
  k1=derivative(v,s,y,cx,rr,eii,Pcell,D,B,feedback)
  v2=apply(y,cx,rr,eii,Pcell,D,B,k1,.5*step)
  k2=derivative(v,s+step/2,*v2,feedback)
  v3=apply(y,cx,rr,eii,Pcell,D,B,k2,.5*step)
  k3=derivative(v,s+step/2,*v3,feedback)
  v4=apply(y,cx,rr,eii,Pcell,D,B,k3,step)
  k4=derivative(v,s+step,*v4,feedback)
  y+=(step/6)*(k1[0][0]+2*k2[0][0]+2*k3[0][0]+k4[0][0])
  cx+=(step/6)*(k1[0][1]+2*k2[0][1]+2*k3[0][1]+k4[0][1])
  rr+=(step/6)*(k1[0][2]+2*k2[0][2]+2*k3[0][2]+k4[0][2])
  eii+=(step/6)*(k1[0][3]+2*k2[0][3]+2*k3[0][3]+k4[0][3])
  Pcell+=(step/6)*(k1[0][4]+2*k2[0][4]+2*k3[0][4]+k4[0][4])
  D+=(step/6)*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
  B+=(step/6)*(k1[2]+2*k2[2]+2*k3[2]+k4[2])
  if record:
   N0,A0,lam,gamma,w=source_at(v,(j+1)*step)
   traj.append(dict(s=(j+1)*step,photon_depletion=D.copy(),native_absorption_displacement=B.copy(),
        native_number=N0.copy(),neutral_D_nuclei_count=float(ETA_D*np.dot(v['NH'],1-y)),
        group_gamma=gamma*w*(1-np.divide(D,N0,out=np.zeros(4),where=N0>0))))
 if np.any(y<0) or np.any(y>1) or np.any(~np.isfinite(y)):raise ArithmeticError("DEUTERIUM_POPULATION_INVALID")
 pg=np.zeros(4);pg[:3]=ETA_D*np.asarray(Pcell@v["NH"])
 diff=pg-D-B
 if feedback and np.any(np.abs(diff[:3])/np.maximum(abs(pg[:3]),1e-300)>5e-10):
  raise ArithmeticError("PHOTON_GROUP_CONSERVATION_FAIL")
 if not np.all(Pcell>=-1e-15):raise ArithmeticError("PHOTON_GROSS_REACTION_NEGATIVE")
 delta=y-y_initial-cx-Pcell.sum(axis=0)-eii+rr
 if np.max(abs(delta))>4e-12:raise ArithmeticError("DI_SOURCE_STOICHIOMETRY_FAIL")
 return dict(y=y,cx=cx,recomb=rr,eii=eii,photo=Pcell,D=D,B=B,pg=pg,
             ledger=delta,photon_residual=diff,trajectory=traj)
def write_gz(path,cols):
 with path.open("wb") as raw:
  with gzip.GzipFile(fileobj=raw,filename="",mode="wb",mtime=0,compresslevel=6) as zipped:
   with io.TextIOWrapper(zipped,encoding="utf8",newline="") as text:
    wr=csv.writer(text,lineterminator="\n");wr.writerow(cols.keys())
    arrays=[np.asarray(a) for a in cols.values()]
    for j in range(N):
     wr.writerow([j if k=="node" else format(float(arr[j]),".17g") for k,arr in zip(cols,arrays)])
def write_csv(path,head,rows):
 with path.open("w",newline="") as f:
  w=csv.writer(f,lineterminator="\n");w.writerow(head)
  for row in rows:w.writerow(row)
def run(out):
 v=load()
 gamma17_error=v["gamma_source_all17_max_rel"]
 # The within-tick difference between PCHIP gamma from the original source
 # and independently reconstructed group PCHIPs is recorded, not suppressed.
 t=np.linspace(v["t0"],v["t1"],33)
 group_gamma=np.array([np.sum(np.asarray(v["source_N"](tt))*v["sigma"])*v["pref"] for tt in t])
 original_gamma=v["source_gam"](t)
 pchip_rel=float(np.max(abs(group_gamma-original_gamma)/original_gamma))
 if pchip_rel>5e-7:raise ArithmeticError("SOURCE_GROUP_CONTINUOUS_HI_GAMMA_PARITY_FAIL")
 init={"neutral":np.zeros(N),"ionized":np.ones(N)}
 neutral=evolve(v,init["neutral"],steps=64,feedback=True,record=True)
 ionized=evolve(v,init["ionized"],steps=64,feedback=True,record=False)
 small=evolve(v,init["neutral"],steps=32,feedback=True,record=False)
 nopert=evolve(v,init["neutral"],steps=64,feedback=False,record=False)
 if np.max(abs(nopert["y"]-v["R53_neutral"]))>5e-12:
  raise ArithmeticError("ORIGINAL_R53_EII_FULL_SOURCE_NO_DI_FEEDBACK_REGRESSION_FAILED")
 if np.max(abs(ionized["y"]-v["R53_ionized"]))>2e-4:
  raise ArithmeticError("ORIGINAL_DI_INITIAL_IONIZED_SOURCE_CHANGED")
 end_N0=np.asarray(v["source_N"](v["t1"]))
 for z in (neutral,ionized):
  if np.any(z["D"][:3]>end_N0[:3]) or z["D"][3]!=0 or z["B"][3]!=0 or z["pg"][3]!=0:
   raise ArithmeticError("PHOTON_GROUP_ABSORPTION_INVALID")
  if np.max(abs(z["photon_residual"][:3])/z["pg"][:3])>5e-10:
   raise ArithmeticError("PHOTON_NUMBER_GROUP_LEDGER_FAIL")
  if np.any((z["y"]<0)|(z["y"]>1)):raise ArithmeticError("DI_FRACTION_OUT_OF_RANGE")
 # Candidate photon excess energy and chemical latent energy per H nucleus.
 P=neutral["photo"]
 Eabs=(P.T @ v["meanE"][:3]) # N rows, three native nonzero groups; fourth group is exact zero
 Psum=P.sum(axis=0)
 EL=ETA_D*CHI_D_PHYS_EV*EV_ERG*Psum
 EH=ETA_D*EV_ERG*(Eabs-CHI_D_PHYS_EV*Psum)
 ED=ETA_D*EV_ERG*Eabs
 energy_res=ED-EL-EH
 if np.max(abs(energy_res))>1e-27:raise ArithmeticError("SOURCE_DI_PHOTON_ENERGY_BOOKKEEPING_FAIL")
 qCX=-ETA_D*DELTA_CX_EV*EV_ERG*neutral["cx"]
 qEII=-ETA_D*CHI_D_PHYS_EV*EV_ERG*neutral["eii"]
 excess_e=ETA_D*(neutral["y"]-neutral["cx"])
 new_e=ETA_D*(Psum+neutral["eii"]-neutral["recomb"])
 if np.max(abs(excess_e-new_e))>1e-14:raise ArithmeticError("SOURCE_DI_ELECTRON_AND_CHARGE_CONSERVATION_FAIL")
 out.mkdir(parents=True,exist_ok=True)
 fields={
  "node":np.arange(N,dtype=np.int64),"original_H_N":v["NH"],"proper_nH_cm3":v["nH"],
  "original_T160_K":v["T0"],"original_xHII160":v["x0"],"preview_T161_K":v["T1"],
  "source_electron_ne160_cm3":v["ne0"],"original_F05_thermal_gain_erg_per_H":v["dU"],
  "DI_initial_neutral_y_final_group_coupled":neutral["y"],
  "DI_initial_neutral_y_final_original_gamma":v["R53_neutral"],
  "DI_initial_neutral_delta_y_from_photon_debit":neutral["y"]-v["R53_neutral"],
  "DI_initial_ionized_y_final_group_coupled":ionized["y"],
  "DI_initial_ionized_y_final_original_gamma":v["R53_ionized"],
  "DI_initial_neutral_CX_per_D":neutral["cx"],
  "DI_initial_neutral_RR_per_D":neutral["recomb"],
  "DI_initial_neutral_EII_per_D":neutral["eii"],
  "DI_neutral_photon_G1_per_D":P[0],
  "DI_neutral_photon_G2a_per_D":P[1],
  "DI_neutral_photon_G2b_per_D":P[2],
  "DI_neutral_photon_G3_per_D":np.zeros(N),
  "DI_neutral_photon_all_per_D":Psum,
  "DI_neutral_new_electrons_photo_EII_recomb_per_H":new_e,
  "DI_neutral_CX_Hplus_shift_per_H":-ETA_D*neutral["cx"],
  "DI_neutral_EII_electron_per_H":ETA_D*neutral["eii"],
  "DI_neutral_CX_heat_erg_per_H":qCX,
  "DI_neutral_EII_threshold_sink_erg_per_H":qEII,
  "DI_neutral_photo_latent_energy_erg_per_H":EL,
  "DI_neutral_photoelectron_gross_heat_erg_per_H":EH,
  "DI_neutral_gross_photo_heat_over_native_abs_DeltaU":EH/abs(v["dU"]),
  "DI_neutral_photo_threshold_plus_excess_erg_per_H":ED,
  "DI_neutral_photon_energy_bookkeeping_residual_erg_per_H":energy_res,
  "DI_neutral_charge_total_electron_residual_per_H":excess_e-new_e,
  "DI_initial_ionized_photon_G1_per_D":ionized["photo"][0],
  "DI_initial_ionized_photon_G2a_per_D":ionized["photo"][1],
  "DI_initial_ionized_photon_G2b_per_D":ionized["photo"][2],
  "DI_initial_neutral_isotope_5flux_ledger_residual":neutral["ledger"]
 }
 if list(fields)!=COLS:raise RuntimeError("R54_OUTPUT_PHYSICAL_FIELDS_MISMATCH")
 full=out/FILENAME
 write_gz(full,fields)
 groups=[]
 for i,g in enumerate(GROUPS):
  v0=float(v["source_N"](v["t0"])[i]);v1=float(end_N0[i])
  row=dict(group=g,group_min_eV=BOUNDS[i][0],group_max_eV=BOUNDS[i][1],
       original_HI_mean_sigma_cm2=float(v["sigma"][i]),
       DI_threshold_translated_sigma_cm2_sensitivity=float(v["alt_sigma"][i]),
       mean_photon_energy_eV=float(v["meanE"][i]),
       original_source_Nphotons_initial=v0,
       original_source_Nphotons_final=v1,
       original_owner_absorption_first_tick_native=float(v["source_A"].integrate(v["t0"],v["t1"])[i]),
       initial_neutral_DI_photo_event_count=float(neutral["pg"][i]),
       initial_neutral_DI_photon_reservoir_depletion=float(neutral["D"][i]),
       initial_neutral_native_absorption_displaced=float(neutral["B"][i]),
       initial_neutral_repartition_ledger=float(neutral["photon_residual"][i]),
       initial_neutral_relative_photon_depletion_final=float(neutral["D"][i]/v1) if v1>0 else 0.,
       initial_ionized_DI_photo_event_count=float(ionized["pg"][i]),
       initial_ionized_DI_photon_reservoir_depletion=float(ionized["D"][i]),
       initial_ionized_native_absorption_displaced=float(ionized["B"][i]),
       initial_neutral_DI_photon_excess_heat_erg=float(neutral["pg"][i]*(v["meanE"][i]-CHI_D_PHYS_EV)*EV_ERG),
       initial_neutral_DI_photon_chemical_latent_erg=float(neutral["pg"][i]*CHI_D_PHYS_EV*EV_ERG))
  groups.append(row)
 write_csv(out/"R54_REI_F05_DI_PHOTON_GROUPS_4.csv",list(groups[0]),
           [[str(x) for x in g.values()] for g in groups])
 # native group trajectory (all 64 step values), not an invented simulation of
 # original photons, only a source-conditional perturbation.
 traj=[]
 for j,vv in enumerate(neutral["trajectory"]):
  for g,i in zip(GROUPS,range(4)):
   traj.append((j+1,vv["s"],g,float(vv["native_number"][i]),
     float(vv["photon_depletion"][i]),float(vv["native_absorption_displacement"][i]),
     float(vv["group_gamma"][i]),
     float(vv["photon_depletion"][i]/vv["native_number"][i]) if vv["native_number"][i]>0 else 0,
     float(vv['neutral_D_nuclei_count'])))
 write_csv(out/"R54_GROUP_PHOTON_DEPLETION_TRAJECTORY_256.csv",
          ["native_substep","normalized_time","group","original_source_N","DI_photon_deficit",
           "native_original_absorption_displaced","DI_group_gamma_coupled","relative_photon_depletion","neutral_D_nuclei_count_per_cMpc3"],
          traj)
 totalP=float(np.sum(neutral["pg"]))
 photon_source=json.loads((INPUT/"R53_PHOTON_BUDGET.json").read_text())
 source_emit=float(photon_source["native_source_integrated_counts_per_cMpc3"]["emission_rate_s-1_cMpc-3"])
 metrics={
  "schema":"WU_R54_REI_F05_ORIGINAL_4GROUP_DI_PHOTON_CONSERVATIVE_PERTURBATION_V1",
  "science_status":"SOURCE_CONDITIONAL_REAL_46K_CELL_PHOTON_GROUP_CONSERVING_PERTURBATION_NOT_NATIVE_RT_OWNER",
  "WU_parent_PR":193,"WU_parent_HEAD":"6f2f532b46ea153795d6aebeed7b73765b6482ac",
  "REI_original_PR352":"ea8d6bf94197392c69f939f03c1673ed3afe349c",
  "original_REI_accepted_tick":"160/131072","original_REI_tick161":"NOT_ACCEPTED",
  "source_SHA256":json.loads((ROOT/"SOURCE_CONTRACT.json").read_text())["source_sha256"],
  "physical_conventions":{"proper_clock_dt_s":v["dt"],"source_z_mid":5.95,
   "original_groups":GROUPS,"original_energy_edges_eV":BOUNDS,
   "original_G3_photon_population":"ZERO_ALL_17_SOURCE_KNOTS",
   "source_within_spectrum":"E^-2.5 ORIGINAL MFP BASELINE",
   "sigma_DI_group_assumption":"EXACT_ORIGINAL_VERNER_HI_CLONE_SAVIN_EQ11_APPROX",
   "alternative_cross_section":"SHIFT_HI_THRESHOLD_BY_0p0017_eV_ONLY_SENSITIVITY_NOT_PHYSICAL_DI_ABINITIO",
   "unmodified_native_PCHIP_gamma_ref":True,
   "original_native_HHe_photon_opacity_response":"lambda_g=A_g0/N_g0 FIXED_SOURCE",
   "original_HHe_T_e_source":"ENDPOINT_INTERPOLATED_160_ACCEPTED_161_PREVIEW",
   "D_initial_conditions":["ALL_NEUTRAL","ALL_IONIZED"],
   "R53_H_cloned_DI_CX_PI_RR_EII":"USED_AS_ZERO_FEEDBACK_REFERENCE",
   "D_photoionization_energy_group":"SOURCE_AVG_HI_VERNER_CROSS_SECTION_E^-2p5",
   "actual_D_photo_cross_section":"NOT_MEASURED",
   "true_photoheating_net_after_native_reassignment":"NOT_COMPUTED",
   "full_coupled_Einstein_Boltzmann_four_group_RT":"NOT_RUN"},
  "numeric":{
   "native_real_cells":N,"source_group_count":4,"original_nonzero_photon_group_count":3,
   "parent_original_Gamma_HI_rebuilt_max_rel_at_17_native_nodes":gamma17_error,
   "gamma_PCHIP_vs_group_PCHIP_max_rel_between160_161":pchip_rel,
   "initial_neutral_DI_fraction_group_coupled":qq(neutral["y"]),
   "initial_neutral_DI_fraction_R53_frozen_source":qq(v["R53_neutral"]),
   "initial_neutral_Dplus_difference_coupled_minus_frozen":qq(neutral["y"]-v["R53_neutral"]),
   "initial_ionized_Dplus_difference_coupled_minus_frozen":qq(ionized["y"]-v["R53_ionized"]),
   "initial_neutral_source_group_photo_counts":{g:float(neutral["pg"][i]) for i,g in enumerate(GROUPS)},
   "initial_neutral_DI_gross_photo_count_total":totalP,
   "initial_neutral_photon_reservoir_depletion_total":float(np.sum(neutral["D"])),
   "initial_neutral_native_HHe_absorption_displacement_total":float(np.sum(neutral["B"])),
   "original_emitted_photons_native_source":source_emit,
   "initial_neutral_DI_photo_over_original_emission":totalP/source_emit,
   "initial_ionized_DI_photo_count_total":float(np.sum(ionized["pg"])),
   "group_source_photon_records":groups,
   "DI_source_photon_mean_energy_eV":float(np.dot(neutral["pg"],v["meanE"])/totalP),
   "conditional_DI_photo_gross_kinetic_energy_erg_per_H":qq(EH),
   "conditional_DI_photo_binding_energy_erg_per_H":qq(EL),
   "conditional_DI_photo_excess_heat_over_abs_F05_deltaU":qq(EH/abs(v["dU"])),
   "N_photoheat_gross_gt_one_pct_abs_native_F05_thermal":int(np.count_nonzero(EH/abs(v["dU"])>.01)),
   "max_source_photon_depletion_fraction":max(g["initial_neutral_relative_photon_depletion_final"] for g in groups),
   "max_global_group_photon_conservation_residual_rel":float(max(
     abs(neutral["photon_residual"][i])/max(neutral["pg"][i],1e-300) for i in range(3))),
   "max_per_cell_5flux_population_ledger_abs":float(np.max(abs(neutral["ledger"]))),
   "max_gas_photo_energy_partition_residual_erg_per_H":float(np.max(abs(energy_res))),
   "max_charge_electron_ledger_abs":float(np.max(abs(excess_e-new_e))),
   "RK32_vs64_max_abs_y_initial_neutral":float(np.max(abs(small["y"]-neutral["y"]))),
   "R53_zero_DI_feedback_max_abs_y_initial_neutral":float(np.max(abs(nopert["y"]-v["R53_neutral"]))),
   "first_tick_native_IGM_cell_nH_cm3":qq(v["nH"])}
  ,"files":{"physical_full_csv":FILENAME,
            "full_csv_sha256":sha(full),
            "group_four_row_sha256":sha(out/"R54_REI_F05_DI_PHOTON_GROUPS_4.csv"),
            "group_256_traj_sha256":sha(out/"R54_GROUP_PHOTON_DEPLETION_TRAJECTORY_256.csv")},
  "policy":{"WU":"34/49","REI_central":"28/88","REI_working":"33/88","fast":"4/7",
      "canonical_delta":0,"production":"HOLD","original_tick161":"NOT_ACCEPTED",
      "no_original_REI_source_mutation":True,"no_main_merge":True,
      "native_subagent":"NOT_RUN","distinct_author_referee":"NOT_RUN",
      "no_strong_no_go_claim":True}}
 (out/"R54_RESULTS.json").write_text(json.dumps(metrics,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"science_status":metrics["science_status"],
   "source_cells":N,
   "group_gamma_17node_rel":gamma17_error,
   "native_group_photo":metrics["numeric"]["initial_neutral_source_group_photo_counts"],
   "native_group_depletion":metrics["numeric"]["max_source_photon_depletion_fraction"],
   "D_photo":totalP,
   "competed_native_displacement":metrics["numeric"]["initial_neutral_native_HHe_absorption_displacement_total"],
   "physical_source_group_conservation":metrics["numeric"]["max_global_group_photon_conservation_residual_rel"],
   "max_delta_y":metrics["numeric"]["initial_neutral_Dplus_difference_coupled_minus_frozen"]["max"],
   "min_delta_y":metrics["numeric"]["initial_neutral_Dplus_difference_coupled_minus_frozen"]["min"],
   "no_feedback_restore_R53":metrics["numeric"]["R53_zero_DI_feedback_max_abs_y_initial_neutral"],
   "gross_DI_photoheat_over_native_dU_median":metrics["numeric"]["conditional_DI_photo_excess_heat_over_abs_F05_deltaU"]["median"],
   "full_source_sha256":sha(full)},sort_keys=True))
 return metrics
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,default=ROOT/"results")
 args=p.parse_args()
 run(args.out)
