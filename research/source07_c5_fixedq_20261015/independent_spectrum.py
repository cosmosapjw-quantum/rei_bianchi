#!/usr/bin/env python3
"""Independent continuum BB50k + Verner event/heat integral at z=20.
Used only as C5 numerical comparison, not an all-time physical error envelope.
"""
from pathlib import Path
import csv,json,math,sys
from scipy.integrate import quad
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source07_c1_baseline_20261014'))
from q_emission_baseline import Scenario

ROOT=Path(__file__).resolve().parents[2]
sc=Scenario(ROOT)
a_ref=1/21
dens_H=sc.nh/a_ref**3*(1-0.0002)
fHe=0.2454/(4*(1-0.2454))
dens_HeI=sc.nh/a_ref**3*fHe
neutrals=[dens_H,dens_HeI,0.0]
C=29979245800.0
BIND=(13.598434599702,24.587389011,54.41776)
FIT={
  "HI":(13.60,0.4298,5.475e4,32.88,2.963,0.0,0.0,0.0),
  "HeI":(24.59,13.61,949.2,1.469,3.188,2.039,0.4434,2.136),
  "HeII":(54.42,1.720,1.369e4,32.88,2.963,0.0,0.0,0.0)
}
kT=50000*1.380649e-16/1.602176634e-12
def src(E):
    return E*E/math.expm1(E/kT)
segments=[13.6,24.59,54.42,100.]
norm=sum(quad(src,lo,hi,epsabs=1e-14,epsrel=2e-13)[0] for lo,hi in zip(segments,segments[1:]))
def sigma(E,p):
    eth,e0,s0,ya,expo,yw,y0,y1=p
    if E<eth:return 0.
    x=E/e0-y0
    y=math.hypot(x,y1)
    return s0*((x-1)**2+yw*yw)*y**(expo/2-5.5)*(1+math.sqrt(y/ya))**(-expo)*1e-18

def spectral_integrand(E,dt,which):
    rates=[C*d*sigma(E,FIT[key]) for key,d in zip(("HI","HeI","HeII"),neutrals)]
    rate=sum(rates)
    total=(-math.expm1(-rate*dt)) if rate else 0.
    if which=="mean_E":return src(E)/norm*E
    if which=="count":return src(E)/norm
    if which=="total_absorb":return src(E)/norm*total
    if which=="HI_absorb":return src(E)/norm*(total*rates[0]/rate if rate>0 else 0.)
    if which=="HeI_absorb":return src(E)/norm*(total*rates[1]/rate if rate>0 else 0.)
    if which=="heat":return src(E)/norm*sum(total*rt/rate*(E-BIND[i]) if rate>0 else 0. for i,rt in enumerate(rates))
    if which=="binding":return src(E)/norm*sum(total*rt/rate*BIND[i] if rate>0 else 0. for i,rt in enumerate(rates))
    raise ValueError(which)

DT=1e10
obs={}
for name in ("count","mean_E","total_absorb","HI_absorb","HeI_absorb","heat","binding"):
    parts=[quad(lambda E:spectral_integrand(E,DT,name),lo,hi,
                epsabs=2e-14,epsrel=2e-12,limit=250)[0] for lo,hi in zip(segments,segments[1:])]
    obs[name]=sum(parts)
source_count=sc.rate(a_ref)*DT
ref_abs=obs["total_absorb"]*source_count
ref_heat=obs["heat"]*source_count
native=list(csv.DictReader((Path(__file__).parent/"evidence/PILOT.csv").open()))
compare=[]
for row in native:
    n=int(row["n_energy"])
    if float(row["q_ref"])!=0.0: continue
    a=float(row["one_source_abs_per_H"])
    h=float(row["one_source_heat_eV_per_H"])
    compare.append({"energy_cells":n,"absorbed_per_H":a,"heat_eV_per_H":h,
        "abs_relative_to_continuum":a/ref_abs-1,
        "heat_relative_to_continuum":h/ref_heat-1,
        "abs_relative_to_native_cohort":a/float(row["cohort_abs_per_H"])-1,
        "heat_relative_to_native_cohort":h/float(row["cohort_heat_eV_per_H"])-1})
assert abs(obs["count"]-1)<1e-12
assert obs["total_absorb"]>=0 and obs["heat"]>=0 and obs["binding"]>=0
assert len(compare)==4
result={"kind":"independent SCIpy continuous BB50k/Verner frozen gas at z20",
"reference_source_number_per_H":source_count,"source_emission_mean_ev":obs["mean_E"],
"neutral_density_cm3":{"HI":dens_H,"HeI":dens_HeI,"HeII":0},
"dt_s":DT,"continuous_source_only":{"absorbed_per_H":ref_abs,"heating_eV_per_H":ref_heat,
"binding_eV_per_H":obs["binding"]*source_count,
"HI_absorbed_per_H":obs["HI_absorb"]*source_count,
"HeI_absorbed_per_H":obs["HeI_absorb"]*source_count},
"rust_refinement_comparison":compare,
"scope":"Frozen proper neutrals and photoabsorption only; not certified coupled HHe universe"}
out=Path(__file__).parent/"evidence/INDEPENDENT_SPECTRUM.json"
out.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
