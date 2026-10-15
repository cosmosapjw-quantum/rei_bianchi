"""Independent SciPy q-ray age-mixed source and H/He Verner frozen-gas benchmark.
Not an ODE or H/He-ion fraction solver. Uses original MD14 spectrum (not Rust
source centroid) and the selected actual Bianchi-I background geometry.
"""
import sys,math,csv,json,statistics
from pathlib import Path
from scipy.integrate import quad
from numpy.polynomial.legendre import leggauss
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/"research/source07_c1_baseline_20261014"))
from q_emission_baseline import Scenario,Spectrum
model=Scenario(root);spec=Spectrum()
z_ref=20.0;z_end=4.0;af=1.0/5.0
kT=50000*1.380649e-16/1.602176634e-12
C=29979245800.0
fit=[
(13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),
(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),
(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)
]
bind=[13.598434599702,24.587389011,54.41776]
dt=1e10
n_HI=model.nh*5**3*(1-.0002)
n_HeI=model.nh*5**3*.2454/(4*(1-.2454))
gas=[n_HI,n_HeI,0.]
gauss_mu,gauss_w=leggauss(32)
srcN=model.rate(model.ar)*dt
def sigma(E,par):
    chi,e0,s0,ya,p,yw,y0,y1=par
    if E<chi:return 0.
    x=E/e0-y0; y=math.hypot(x,y1)
    return s0*((x-1.)**2+yw*yw)*y**(p/2-5.5)*(1.+math.sqrt(y/ya))**(-p)*1e-18
def reaction(E):
    lam=[C*ni*sigma(E,p) for ni,p in zip(gas,fit)]
    total=sum(lam)
    if total<=0.:return (0.,0.,0.,0.)
    ev=-math.expm1(-total*dt)
    w=[ev*x/total for x in lam]
    heat=sum(x*(E-bind[j]) for j,x in enumerate(w))
    return (w[0],w[1],w[2],heat)
def integrate_moments(scale):
    cut=[13.6,100.]
    for th in [13.60,24.59,54.42]:
        e=th/scale
        if cut[0]<e<cut[1]:cut.append(e)
    cut.sort()
    out=[0.,0.,0.,0.]
    for l,h in zip(cut,cut[1:]):
        for j in range(4):
            v=quad(lambda emission_E:spec.phi(emission_E)*reaction(emission_E*scale)[j],
                l,h,epsabs=4e-14,epsrel=8e-12,limit=180)[0]
            out[j]+=v
    return out
results={}
for q in [-.01,0.,.01]:
    rp,rz=model.ratios(af,q)
    vol=(model.ar/af)**3
    out=[0.,0.,0.,0.]
    for mu,w in zip(gauss_mu,gauss_w):
        R=math.sqrt(rp*rp*(1-mu*mu)+rz*rz*mu*mu)
        jac=vol/(R**3)
        old=integrate_moments(R)
        fresh=integrate_moments(1.)
        for j in range(4):
            out[j]+=w/2*(old[j]+jac*fresh[j])
    results[f"{q:+.2f}"]={"frozen_HI_absorbed_photons_per_H":out[0]*srcN,
        "frozen_HeI_absorbed_photons_per_H":out[1]*srcN,
        "frozen_HeII_absorbed_photons_per_H":out[2]*srcN,
        "frozen_photoheat_eV_per_H":out[3]*srcN}
native=list(csv.DictReader((Path(__file__).parent/"evidence/TWO_AGE_NATIVE.csv").open()))
compare=[]
for row in native:
    q=f"{float(row['q_ref']):+.2f}"
    truth=results[q]
    ne=int(row["nE"])
    record={"q":q,"energy_bins":ne,"clipped_bins":int(row["clipped_populated_cells"]),
            "buffer_bytes":int(row["reference_state_bytes"])}
    for label,field,key in [
        ("HI","HI","frozen_HI_absorbed_photons_per_H"),
        ("HeI","HeI","frozen_HeI_absorbed_photons_per_H"),
        ("heat","heat","frozen_photoheat_eV_per_H")]:
        tr=truth[key]
        record[f"legacy_{label}_relative_error"]=float(row[f"old_rep_{field}"])/tr-1.
        record[f"support_{label}_relative_error"]=float(row[f"support_rep_{field}"])/tr-1.
        record[f"two_age_{label}_relative_error"]=float(row[f"two_age_{field}"])/tr-1.
    record["two_age_payload_bytes"]=int(row["two_age_payload_bytes"])
    record["single_lane_payload_bytes"]=int(row["reference_state_bytes"])
    compare.append(record)
report={"scope":"C7 two age instantaneous MD14 injection z20 and z4, equal photons per H, frozen proper gas at z4, no gas evolution",
    "gas_proper_cm3":{"nHI":gas[0],"nHeI":gas[1],"nHeII":gas[2]},
    "old_and_late_source_photons_per_H":srcN,
    "source_geometry":results,
    "comparison":compare}
Path(__file__).parent.joinpath("evidence/INDEPENDENT_TWO_AGE.json").write_text(json.dumps(report,indent=2))
print(json.dumps({"q0_truth":results["+0.00"],"q0_rows":[x for x in compare if x["q"]=="+0.00"]},indent=2))
