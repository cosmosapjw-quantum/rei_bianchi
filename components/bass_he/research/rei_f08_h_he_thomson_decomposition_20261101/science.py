#!/usr/bin/env python3
"""Source-authentic F08 S0 H/He-resolved Thomson observer response.
Uses actual original 16000-step paired S0 H/He source curves and exact REI PR349
emission clocks. No new Einstein/ionization IVP or new astronomical observations.
"""
from __future__ import annotations
import argparse,bisect,csv,gzip,hashlib,io,json,math,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/"source_inputs"
C_CGS=29979245800.0
SIGMA_T=6.6524587051e-25
OPACITY=C_CGS*SIGMA_T
SOURCE_PAIR_ID="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
SHAS={
 "S0_BI-curve.csv.gz":"3096dc923520ec98da8c2e1dd3f03605cbf0809e944eeb5e4ceb6f58eff58893",
 "S0_FLRW-curve.csv.gz":"cab6e37e0f375e06dc03218067fa74fe3f14455e2dcf41a03051965008acb521",
 "S0_BI-electron_density.csv.gz":"663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723",
 "S0_FLRW-electron_density.csv.gz":"0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa",
 "science_scenario_v1.json":"c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1",
 "ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz":"41fb767cc6c826047abf3799164f9e5b6a970c9dc879566147ad036226e4588d"}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
def csv_rows(p):
 with gzip.open(p,"rt",newline="") as f:return list(csv.DictReader(f))
def verify():
 for name,expected in SHAS.items():
  if sha(SRC/name)!=expected:raise ValueError("immutable original REI F08 source mismatch "+name)
 original=json.loads((SRC/"REI349_SOURCE_PROVENANCE.json").read_text())
 if original["source_pair_id"]!=SOURCE_PAIR_ID or original["original_F08_return"]["scientific_admission"]!="HOLD":
  raise ValueError("F08 original owner/source admission changed")
 sc=json.loads((SRC/"science_scenario_v1.json").read_text())
 if (sc["initial_state"]["fHe"]!=0.083 or sc["source"]["family"]!="S0"
     or sc["source"]["energy_at_birth_ev"]!=13.7
     or sc["time"]["t_end_s"]!=1e13 or sc["background"]["tilt"]!=[0.,0.,0.]):
  raise ValueError("different original scenario/source/clock")
 if sc["constants"]["c_cm_s"]!=C_CGS:raise ValueError("original c owner drift")
 return sc
def history(label,sc):
 density=csv_rows(SRC/f"S0_{label}-electron_density.csv.gz")
 curve=csv_rows(SRC/f"S0_{label}-curve.csv.gz")
 if len(density)!=16001 or len(curve)!=16000:raise ValueError("incomplete original F08 source history")
 initial=sc["initial_state"]["fractions"]
 curves=[dict(time_s="0",x_HII=initial["HII"],x_HeII=initial["HeII"],x_HeIII=initial["HeIII"])]+curve
 out=[]
 max_abs=0.;max_rel=0.
 for i,(d,r) in enumerate(zip(density,curves)):
  t=float(d["normal_time_s"]);tt=float(r["time_s"])
  if t!=tt or t!=i*625000000.:raise ValueError("F08 original times not exactly matched")
  nh=float(d["nH_proper_cm3"]);nhe=float(d["nHe_proper_cm3"]);ne=float(d["ne_proper_cm3"])
  xh=float(r["x_HII"]);xhe2=float(r["x_HeII"]);xhe3=float(r["x_HeIII"])
  if (not all(map(math.isfinite,(nh,nhe,ne,xh,xhe2,xhe3)))
      or min(nh,nhe,ne)<=0 or min(xh,xhe2,xhe3)<0
      or max(xh,xhe2,xhe3)>1 or xhe2+xhe3>1+1e-13):
   raise ValueError("nonphysical F08 original H/He source state")
  if abs(nhe/nh-0.083)>5e-13:raise ValueError("F08 helium nuclei normalization mismatch")
  eh=nh*xh; ehe=nhe*(xhe2+2*xhe3)
  error=abs(ne-(eh+ehe))
  max_abs=max(max_abs,error);max_rel=max(max_rel,error/max(ne,1e-300))
  if error>2e-18 or error/max(ne,1e-300)>5e-14:
   raise ValueError(f"original proper electron species source identity failed at {i}")
  out.append(dict(run=label,node=i,time_s=t,nH_proper_cm3=nh,nHe_proper_cm3=nhe,
    x_HII=xh,x_HeII=xhe2,x_HeIII=xhe3,
    ne_H_proper_cm3=eh,ne_He_proper_cm3=ehe,ne_total_reconstructed_cm3=eh+ehe,
    original_ne_proper_cm3=ne,He_electron_fraction=ehe/ne))
 return out,max_abs,max_rel
class Screen:
 def __init__(self,history,field):
  self.t=[r["time_s"] for r in history]
  self.n=[r[field] for r in history]
  if len(self.t)!=16001:raise ValueError("wrong source history")
  self.right=[0.]*len(self.t)
  for j in range(len(self.t)-2,-1,-1):
   dt=self.t[j+1]-self.t[j]
   if dt<=0 or min(self.n[j],self.n[j+1])<0:raise ValueError("negative density/time")
   self.right[j]=self.right[j+1]+(self.n[j]+self.n[j+1])*dt/2
 def eval(self,t):
  if not self.t[0]<=t<=self.t[-1]:raise ValueError("invalid original emission time")
  i=min(max(bisect.bisect_right(self.t,t)-1,0),len(self.t)-2)
  f=(t-self.t[i])/(self.t[i+1]-self.t[i])
  return self.n[i]+f*(self.n[i+1]-self.n[i])
 def integral(self,t):
  i=min(max(bisect.bisect_right(self.t,t)-1,0),len(self.t)-2)
  v=self.eval(t)
  return self.right[i+1]+(v+self.n[i+1])*(self.t[i+1]-t)/2
def write_csv(path,rows):
 if not rows:raise ValueError("empty scientific output")
 with path.open("wb") as f:
  with gzip.GzipFile(fileobj=f,filename="",mode="wb",mtime=0,compresslevel=6) as g:
   with io.TextIOWrapper(g,encoding="utf8",newline="") as txt:
    w=csv.DictWriter(txt,fieldnames=list(rows[0]),lineterminator="\n")
    w.writeheader();w.writerows(rows)
 return sha(path)
def sky_row(r,bi,fl,Hbar):
 te=float(r["emission_time_s"]);tf=float(r["flrw_reference_emission_time_s"])
 z=float(r["relative_redshift"]);Hdir=float(r["effective_directional_H_s_inv"])
 attenBI=float(r["transmission_BI"]);attenFL=float(r["transmission_FLRW"])
 values={}
 for label,screen_b,screen_f in (("H",bi["H"],fl["H"]),("He",bi["He"],fl["He"])):
  tbi=OPACITY*screen_b.integral(te)
  tfl=OPACITY*screen_f.integral(tf)
  tfixed=OPACITY*screen_b.integral(tf)
  material=tfixed-tfl
  geometry=tbi-tfixed
  gbi=OPACITY*screen_b.eval(te)*attenBI/((1+z)*Hdir)
  gfl=OPACITY*screen_f.eval(tf)*attenFL/((1+z)*Hbar)
  values.update({f"tau_BI_{label}":tbi,f"tau_FLRW_{label}":tfl,
    f"tau_BI_fixed_time_{label}":tfixed,
    f"delta_tau_material_{label}":material,
    f"delta_tau_geometry_{label}":geometry,
    f"visibility_BI_{label}":gbi,
    f"visibility_FLRW_{label}":gfl,
    f"ne_BI_{label}_emitter_cm3":screen_b.eval(te)})
 for origin,keys in (
   ("tau_BI",("tau_BI_H","tau_BI_He")),
   ("tau_FLRW",("tau_FLRW_H","tau_FLRW_He")),
   ("tau_BI_fixed_FLRW_emission_time",("tau_BI_fixed_time_H","tau_BI_fixed_time_He")),
   ("visibility_BI_per_relative_z",("visibility_BI_H","visibility_BI_He")),
   ("visibility_FLRW_per_relative_z",("visibility_FLRW_H","visibility_FLRW_He")),
   ("delta_tau_geometry_fixed_relative_z",("delta_tau_geometry_H","delta_tau_geometry_He")),
   ("delta_tau_material_fixed_time",("delta_tau_material_H","delta_tau_material_He")),
   ("ne_BI_emitter_cm3",("ne_BI_H_emitter_cm3","ne_BI_He_emitter_cm3"))):
  ref=float(r[origin]);got=math.fsum(values[k] for k in keys)
  if abs(ref-got)>max(6e-18,abs(ref)*1e-11):
   raise ValueError("species decomposition failed original REI observer row: "+origin)
 out={k:r[k] for k in ("window_fraction","angular_nmu","angular_nphi","mu_bin","phi_bin",
      "nx","ny","nz","relative_redshift","emission_time_s","flrw_reference_emission_time_s")}
 out.update(values)
 out["He_tau_BI_fraction"]=values["tau_BI_He"]/(values["tau_BI_H"]+values["tau_BI_He"])
 out["He_visibility_BI_fraction"]=values["visibility_BI_He"]/(values["visibility_BI_H"]+values["visibility_BI_He"])
 return out
def stats(rows):
 grp={}
 for r in rows:
  key=(int(r["angular_nmu"]),int(r["angular_nphi"]),float(r["window_fraction"]))
  grp.setdefault(key,[]).append(r)
 out=[]
 for (nmu,nphi,frac),rs in sorted(grp.items()):
  mu=nmu*nphi
  if len(rs)!=mu:raise ValueError("original F08 angular group incomplete")
  def mean(k):return statistics.fmean(x[k] for x in rs)
  def Q(k,i):
   avg=mean(k)
   return statistics.fmean((x[k]-avg)*(float(x["n"+("x","y","z")[i]])**2-1/3) for x in rs)
  qH=[Q("delta_tau_geometry_H",i) for i in range(3)]
  qHe=[Q("delta_tau_geometry_He",i) for i in range(3)]
  out.append(dict(n_mu=nmu,n_phi=nphi,window_fraction=frac,relative_z=float(rs[0]["relative_redshift"]),
   ray_rows=mu,tau_BI_H_mean=mean("tau_BI_H"),tau_BI_He_mean=mean("tau_BI_He"),
   He_tau_fraction_of_mean=mean("tau_BI_He")/(mean("tau_BI_H")+mean("tau_BI_He")),
   He_tau_fraction_min=min(x["He_tau_BI_fraction"] for x in rs),
   He_tau_fraction_max=max(x["He_tau_BI_fraction"] for x in rs),
   H_geometry_quadrupole_diag=qH,He_geometry_quadrupole_diag=qHe,
   He_geometry_Qxx_fraction=qHe[0]/(qH[0]+qHe[0]),
   He_visibility_fraction_mean=mean("He_visibility_BI_fraction"),
   tau_FLRW_He=mean("tau_FLRW_He"),
   tau_FLRW_H=mean("tau_FLRW_H")))
 return out
def run(out):
 sc=verify()
 BI,berr,brel=history("BI",sc)
 FL,ferr,frel=history("FLRW",sc)
 screens={}
 for label,rows in (("BI",BI),("FLRW",FL)):
  screens[label]={x:Screen(rows,"ne_"+x+"_proper_cm3") for x in ("H","He")}
 Hbar=sc["background"]["H_mean_per_s"]
 original=csv_rows(SRC/"ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz")
 if len(original)!=10752:raise ValueError("original REI ray count mismatch")
 scientific=[sky_row(r,screens["BI"],screens["FLRW"],Hbar) for r in original]
 summary=stats(scientific)
 out.mkdir(parents=True,exist_ok=True)
 hist_path=out/"ORIGINAL_F08_S0_H_HE_PROPER_ELECTRONS_32002.csv.gz"
 ray_path=out/"ORIGINAL_F08_S0_H_HE_THOMSON_SKY_10752.csv.gz"
 h_sha=write_csv(hist_path,BI+FL)
 r_sha=write_csv(ray_path,scientific)
 result={"schema":"BASS_HE_REI_F08_S0_H_HE_SOURCE_MATCHED_THOMSON_V1",
  "origin_REI_PR":349,"origin_REI_HEAD":"58f7ffb685c3758f1fed1113ff8134a24478c3df",
  "source_pair_id":SOURCE_PAIR_ID,"source_hashes":SHAS,
  "source_scenario_fHe":sc["initial_state"]["fHe"],"original_f05_fHe_not_transported":0.079,
  "original_source_16k_accepted_steps_per_history":16000,
  "original_source_16001_time_points_per_history":16001,
  "source_history_rows":len(BI)+len(FL),"source_sky_rows":len(scientific),
  "electron_identity_max_abs_cm3":max(berr,ferr),
  "electron_identity_max_relative":max(brel,frel),
  "species_history_csv_sha256":h_sha,"species_ray_csv_sha256":r_sha,
  "observer_time_s":sc["time"]["t_end_s"],
  "model":"prescribed S0 13.7eV source and BI/FLRW geometry, not real EoR photon spectrum",
  "visibility_definition":"g_s=(d tau_s/d z_rel)*exp[-(tau_H+tau_He)] with COMMON total attenuation",
  "physics":"tau_s=c sigmaT integral_{t_e(n,z_rel)}^{tobs} n_e,s^proper(t) dt",
  "quad_summary":summary,"new_cosmological_IVPs":0,"new_astronomical_observations":0,
  "REI_central":"28/88_REPORTED","REI_working":"33/88_REPORTED",
  "REI_fast":"4/7_REPORTED","BASS_HE_physical":"14/18_REPORTED",
  "canonical_delta":0,"RUX03":"NOT_ADMITTED","RUX04":"NOT_ADMITTED",
  "original_F08":"COMPLETED_SCIENCE_HOLD","F09":"BLOCKED","production":"HOLD",
  "native_subagent":"NOT_RUN","distinct_author_referee":"NOT_RUN"}
 (out/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"history_rows":len(BI)+len(FL),"ray_rows":len(scientific),"h_sha":h_sha,"sky_sha":r_sha,
  "source_electron_identity_relative_max":max(brel,frel),"primary_high_z":next(x for x in summary if x["n_mu"]==16 and x["window_fraction"]==0.95)},sort_keys=True))
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.out)
