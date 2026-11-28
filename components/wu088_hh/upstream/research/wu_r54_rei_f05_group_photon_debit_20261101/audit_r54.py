#!/usr/bin/env python3
"""R54 same-author independent source and photon-conservation audit."""
import bisect,csv,gzip,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import quad,solve_ivp
BASE=Path(__file__).resolve().parent; S=BASE/"source_inputs";R=BASE/"results"
C=29979245800.;MPC=3.085677581491367e24;ETA=2.5e-5;EV=1.602176634e-12
GROUPS=("G1","G2a","G2b","G3")
BOUNDS=((13.60,24.59),(24.59,39.50),(39.50,54.42),(54.42,100.))
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def sigma(e):
 if e<13.60:return 0
 x=e/.4298
 return 1e-18*5.475e4*(x-1)**2*x**(.5*2.963-5.5)/(1+math.sqrt(x/32.88))**2.963
def audit():
 contract=json.loads((BASE/"SOURCE_CONTRACT.json").read_text())
 for p,d in contract["source_sha256"].items():
  assert sha(S/p)==d,("SOURCE_BYTE_DRIFT",p)
 src=json.loads((R/"R54_RESULTS.json").read_text())
 full=R/"R54_REI_F05_DI_GROUP_CONSERVATIVE_46080.csv.gz"
 assert sha(full)==src["files"]["full_csv_sha256"]
 rates=[]
 with open(S/"canonical_time_resolved_forcing_nodes.csv") as f:
  rates=[r for r in csv.DictReader(f) if int(r["interval_index"])==0]
 assert len(rates)==17 and all(float(r["z_mid"])==5.95 for r in rates)
 times=np.array([float(r["time_s"]) for r in rates])
 ng=np.array([[float(r["N_"+g+"_cMpc-3"]) for g in GROUPS] for r in rates])
 ag=np.array([[float(r["absorption_"+g+"_s-1_cMpc-3"]) for g in GROUPS] for r in rates])
 gh=np.array([float(r["Gamma_HI_s-1"]) for r in rates])
 assert np.all(ng[:,3]==0) and np.all(ag[:,3]==0)
 sig=[]
 for a,b in BOUNDS:
  sig.append(quad(lambda e:e**-2.5*sigma(e),a,b,epsabs=0,epsrel=2e-9)[0]/
             quad(lambda e:e**-2.5,a,b,epsabs=0,epsrel=2e-9)[0])
 sig=np.array(sig)
 source_rel=float(np.max(np.abs(gh-(ng@sig)*C*(1+5.95)**3/MPC**3)/gh))
 assert source_rel<5e-12
 with (R/"R54_REI_F05_DI_PHOTON_GROUPS_4.csv").open() as f:g=list(csv.DictReader(f))
 assert len(g)==4
 P=np.array([float(r["initial_neutral_DI_photo_event_count"]) for r in g])
 D=np.array([float(r["initial_neutral_DI_photon_reservoir_depletion"]) for r in g])
 B=np.array([float(r["initial_neutral_native_absorption_displaced"]) for r in g])
 EG=np.array([float(r["mean_photon_energy_eV"]) for r in g])
 assert P[3]==D[3]==B[3]==0
 errPB=float(np.max(abs(P[:3]-D[:3]-B[:3])/P[:3]))
 assert errPB<3e-13
 z=np.load(S/"initial_material_state_z6.npz",allow_pickle=False)
 NH=np.array(z["N_HI"]+z["N_HII"])
 count=0;checks=np.zeros(4);maxenergy=maxcharge=maxstoich=0.
 with gzip.open(full,"rt") as f:
  for r in csv.DictReader(f):
   node=int(r["node"])
   assert node==count
   count+=1
   H=float(r["original_H_N"]);assert H==NH[node]
   pg=np.array([float(r["DI_neutral_photon_"+group+"_per_D"]) for group in GROUPS])
   checks+=ETA*H*pg
   total=float(r["DI_neutral_photon_all_per_D"])
   assert abs(total-pg.sum())<3e-14*max(total,1e-300)
   phot=ETA*EV*float(pg@EG)
   latent=ETA*EV*13.6017*total
   excess=phot-latent
   err=abs(float(r["DI_neutral_photo_latent_energy_erg_per_H"])-latent)
   err=max(err,abs(float(r["DI_neutral_photoelectron_gross_heat_erg_per_H"])-excess))
   maxenergy=max(maxenergy,err)
   maxcharge=max(maxcharge,abs(float(r["DI_neutral_charge_total_electron_residual_per_H"])))
   maxstoich=max(maxstoich,abs(float(r["DI_initial_neutral_isotope_5flux_ledger_residual"])))
   if err>4e-28 or maxcharge>4e-13 or maxstoich>4e-13:
    raise AssertionError("ORIGINAL_GROUP_CHEMICAL_CHARGE_ENERGY_MISMATCH")
 assert count==46080
 group_total_err=float(np.max(abs(checks[:3]-P[:3])/P[:3]))
 assert group_total_err<3e-14
 # Independent DOP853 photon equation, using actual archived 64-stage D-neutral
 # history instead of the producer's coupled RK4 group equation.
 with (R/"R54_GROUP_PHOTON_DEPLETION_TRAJECTORY_256.csv").open() as f:tr=list(csv.DictReader(f))
 assert len(tr)==256
 Ssample=[];neutral=[]
 for i in range(64):
  q=tr[i*4:(i+1)*4]
  assert tuple(x["group"] for x in q)==GROUPS
  s=float(q[0]["normalized_time"])
  y=float(q[0]["neutral_D_nuclei_count_per_cMpc3"])
  assert all(float(x["neutral_D_nuclei_count_per_cMpc3"])==y for x in q)
  Ssample.append(s);neutral.append(y)
 totalD=PchipInterpolator(np.r_[0.,Ssample],np.r_[ETA*float(NH.sum()),neutral],extrapolate=False)
 Nnative=PchipInterpolator(times,ng,axis=0,extrapolate=False)
 Anative=PchipInterpolator(times,ag,axis=0,extrapolate=False)
 Gamma=PchipInterpolator(times,gh,extrapolate=False)
 dt=(times[-1]-times[0])/131072.;start=160*dt
 def rhs(s,d):
  t=start+dt*s
  NN=Nnative(t);AA=Anative(t)
  w=NN*sig/np.dot(NN,sig)
  G=float(Gamma(t))*w[:3]
  source=G*float(totalD(s))*(1-d/NN[:3])
  return dt*(source-(AA[:3]/NN[:3])*d)
 sol=solve_ivp(rhs,(0,1),np.zeros(3),method="DOP853",rtol=3e-12,
               atol=np.full(3,1e39),max_step=1/32)
 assert sol.success
 dop=float(np.max(abs(sol.y[:,-1]-D[:3])/D[:3]))
 assert dop<5e-5,("ALT_DOP853_ORIGINAL_PHOTON_SOURCE",dop)
 out={
 "schema":"WU_R54_SAME_AUTHOR_ADVERSARIAL_46K_SOURCE_PHOTON_CONSERVATION_V1",
 "all_original_REI_nodes_checked":count,
 "real_original_source_17knot_GammaHI_independent_Verner_max_rel":source_rel,
 "source_original_G3_all_native_photons_exactly_zero":True,
 "four_group_photon_number_balance_max_relative_error":errPB,
 "independent_photo_group_reactions_max_relative_error":group_total_err,
 "max_source_ion_binding_plus_photoelectron_energy_residual_erg_per_H":maxenergy,
 "max_original_source_electron_charge_residual_per_H":maxcharge,
 "max_deuterium_five_reaction_ledger_abs":maxstoich,
 "independent_DOP853_three_group_photon_loss_using_archived_neutralD_max_rel":dop,
 "independent_method_not_original_HHe_Einstein_photon_owner":True,
 "same_author":True,"distinct_author":"NOT_RUN","native_subagent":"NOT_RUN",
 "original_accepted_tick161":False,
 "canonical_WU":"34/49","canonical_REI":"28/88","delta":0,
 "verdict":"NUMERICALLY_CHECKED_SOURCE_CONDITIONAL"}
 (R/"R54_ADVERSARIAL_AUDIT.json").write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
 print(json.dumps(out,sort_keys=True))
if __name__=="__main__":audit()
