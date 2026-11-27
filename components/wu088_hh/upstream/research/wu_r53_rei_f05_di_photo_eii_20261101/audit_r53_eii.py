#!/usr/bin/env python3
"""Same-author independent source-native EII rate and scalar DOP853 audit."""
import bisect,csv,gzip,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
ROOT=Path(__file__).resolve().parent
S=ROOT/"sources"
R=ROOT/"results"
ETA=2.5e-5
def hashfile(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for q in iter(lambda:f.read(1<<20),b""):h.update(q)
 return h.hexdigest()
def run():
 contract=json.loads((ROOT/"EII_SOURCE_CONTRACT.json").read_text())
 assert hashfile(S/"REI_joint_sink_reservoir_history.py")==contract["original_REI_module_SHA256"]
 with open(S/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv") as f:
  rates=[(float(z["T_K"]),float(z["k_forward_cm3_s"]),float(z["k_reverse_cm3_s"])) for z in csv.DictReader(f)]
 with open(S/"canonical_time_resolved_forcing_nodes.csv") as f:
  nodes=[z for z in csv.DictReader(f) if int(z["interval_index"])==0]
 assert len(nodes)==17 and all(float(z["z_mid"])==5.95 for z in nodes)
 t=np.array([float(z["time_s"]) for z in nodes])
 gamma=PchipInterpolator(t,[float(z["Gamma_HI_s-1"]) for z in nodes],extrapolate=False)
 dt=(t[-1]-t[0])/131072.
 output=R/"R53_REI_F05_EII_SOURCE_SENSITIVITY_46080.csv.gz"
 main=R/"R53_ORIGINAL_REI_F05_D_PHOTO_CX_46080.csv.gz"
 res=json.loads((R/"R53_EII_RESULTS.json").read_text())
 if hashfile(output)!=res["full_source_five_flux_sha256"]:raise AssertionError("EII_FULL_SHA_DRIFT")
 examples=set([0,1,2,15,99,1000,2345,8000,12000,23040,34560,46079]+list(range(611,46079,1403)))
 selected=[]
 count=0;maxledger=0.;maxenergy=0.;count_gtpct=0;sumeii=0.;sumphoto=0.
 with gzip.open(output,"rt") as fa,gzip.open(main,"rt") as fb:
  for a,b in zip(csv.DictReader(fa),csv.DictReader(fb)):
   j=int(a["node"])
   if j!=count or j!=int(b["node"]):raise AssertionError("SOURCE_CELL_ORDER_DISJOINT")
   count+=1
   nh=float(a["original_proper_nH_cm3"]);e0=float(a["original_n_e_HHe160_cm3"])
   T0=float(a["original_T160_K"]);x0=float(b["source_xHII160"])
   beta=5.835e-11*math.sqrt(T0)*math.exp(-157804.0/T0)
   if abs(beta-float(a["native_beta_HI_cm3_s"]))>5e-16*beta:raise AssertionError("ORIGINAL_REI_EII_FORMULA_MISMATCH")
   E=float(a["EII_collisional_ionizations_per_D_neutral"])
   P=float(a["EII_photons_per_D_neutral"])
   if E<0 or P<0:raise AssertionError("NEGATIVE_EII_OR_DI_PHOTON")
   maxledger=max(maxledger,abs(float(a["EII_5flux_stoich_residual"])))
   heat=-ETA*(13.598+.0037)*1.602176634e-12*E
   maxenergy=max(maxenergy,abs(heat-float(a["EII_thermal_threshold_sink_erg_per_H_neutral"])))
   if abs(float(a["EII_sink_over_original_native_F05_thermal_abs_neutral"]))>.01:count_gtpct+=1
   sumeii+=E*ETA*nh*float(b["proper_volume_cm3"])
   sumphoto+=P*ETA*nh*float(b["proper_volume_cm3"])
   if j in examples:selected.append((a,b))
 if count!=46080 or maxledger>4e-13 or maxenergy>3e-29:raise AssertionError("EII_STOICHIOMETRY_OR_ENERGY_FAILED")
 if count_gtpct!=res["N_EII_sink_gt1pct_native_F05_thermal"]:raise AssertionError("SCIENTIFIC_EII_ENERGY_POPULATION_MISMATCH")
 if abs(sumphoto-res["total_DI_photo_reactions_with_EII_initial_neutral"])/sumphoto>3e-14:raise AssertionError("PHOTO_NUMBER_REBUILD_FAILED")
 def savin(T,k):
  j=max(0,min(len(rates)-2,bisect.bisect_right([r[0] for r in rates],T)-1))
  a,b=rates[j],rates[j+1]
  w=math.log(T/a[0])/math.log(b[0]/a[0])
  return math.exp((1-w)*math.log(a[k])+w*math.log(b[k]))
 diffs=[];budget=[]
 for a,b in selected:
  nh=float(a["original_proper_nH_cm3"])
  x0=float(b["source_xHII160"]);x1=float(b["preview_xHII161"])
  T0=float(a["original_T160_K"]);T1=float(b["preview_T161_K"])
  ne0=float(a["original_n_e_HHe160_cm3"]);ne1=float(b["n_e_HHe_preview161_cm3"])
  kf=savin(T0,1);kr=savin(T0,2)
  yeq=kf*x0/(kf*x0+kr*(1-x0))
  for name,y0,expected in [
   ("neutral",0.,float(a["caseB_withEII_neutral_y"])),
   ("ionized",1.,float(a["caseB_withEII_ionized_y"])),
   ("eq160",yeq,float(a["caseB_withEII_eq160_y"]))
  ]:
   def ode(s,z):
    y,c,p,r,e=z
    xeff=x0+s*(x1-x0)-ETA*c
    T=T0*math.exp(s*math.log(T1/T0))
    ne=ne0+s*(ne1-ne0)+ETA*nh*(y-c)
    Kf=savin(T,1);Kr=savin(T,2)
    beta=5.835e-11*math.sqrt(T)*math.exp(-157804.0/T)
    ll=315614./T
    alpha=2.753e-14*ll**1.5/(1+(ll/2.740)**.407)**2.242
    C=nh*(Kf*xeff*(1-y)-Kr*(1-xeff)*y)
    P=float(gamma(160*dt+s*dt))*(1-y)
    R=alpha*ne*y
    EI=beta*ne*(1-y)
    return np.asarray([C+P+EI-R,C,P,R,EI])*dt
   z=solve_ivp(ode,(0.,1.),[y0,0.,0.,0.,0.],method="DOP853",rtol=3e-12,atol=3e-13)
   if not z.success:raise AssertionError("DOP853_NATIVE_EII_ORIGINAL_SOURCE_FAIL")
   delta=abs(float(z.y[0,-1])-expected)
   diffs.append(delta)
   if delta>1e-7:raise AssertionError("REI_NATIVE_EII_ALTERNATE_DOP853_MISMATCH")
   if name=="neutral":budget.append(abs(z.y[4,-1]-float(a["EII_collisional_ionizations_per_D_neutral"])))
 result={
  "schema":"WU_R53_SAME_AUTHOR_NATIVE_REI_EII_C9_HOSTILE_DOP853_V1",
  "source_original_REI_module_sha":contract["original_REI_module_SHA256"],
  "source_original_REI_full_cells_checked":count,
  "N_EII_energy_gt1pct_native_reproduced":count_gtpct,
  "original_source_photons_added_by_DI_ionization_EII_on":sumphoto,
  "original_source_EII_DI_collisional_ionizations_global":sumeii,
  "max_stoichiometric_source_residual":maxledger,
  "max_independent_EII_threshold_energy_diff":maxenergy,
  "original_source_nodes_DOP853_checked":len(selected),
  "independent_scalar_DOP853_EII_5state_samples":len(diffs),
  "DOP853_EII_max_abs_Dplus_difference":max(diffs),
  "DOP853_EII_max_abs_gross_EII_count_perD_difference":max(budget),
  "distinct_author":"NOT_RUN","same_author":True,
  "source_review_status":"SCOPED_PASS_NOT_OWNER_ACCEPTANCE",
  "canonical_WU":"34/49","canonical_REI":"28/88","delta":0
 }
 (R/"R53_EII_ADVERSARIAL_AUDIT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps(result,sort_keys=True))
if __name__=="__main__":run()
