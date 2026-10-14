"""FT03 standalone controlled research model. NOT a production provider.
Direct analytic Case-A RR rates with a derivative-defined kinetic moment;
HG97 CI fits; explicit two-resonance Grackle DR interpretation.
The model has an open escaping-radiation reservoir, not detailed emissivity.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
from moment_api import kinetic_moment, KB
ROOT=Path(__file__).resolve().parents[1]
EV=1.602176634e-12
C=29979245800.0
F=.083
NH=1e-4
CHI=np.array([13.598434599702,24.587389011,54.41776])
ENERGY=np.array([20.,35.,70.])
TMIN,TMAX=30000.,110000.
TEND=1e14
X0=np.array([.9,.3,.6])
P0=np.array([.05,.005,.001])
T0=50000.
LAM=np.array([315614.,570670.,1263030.])
DR_A=1.54e-9*11605.**1.5
DR_B1=40.49664394833662*11605.
DR_B2=8.099328789667*11605.

def check_temperature(T: float)->float:
    T=float(T)
    if not math.isfinite(T) or not TMIN<=T<=TMAX:
        raise ValueError('FT03 temperature domain violated; no floor/extrapolation')
    return T

def recombination(T: float, case: str='A'):
    """Return alpha[HII,HeII,HeIII], log-slopes g, and g' (dimensionless)."""
    T=float(T)
    if case not in ('A','B'): raise ValueError('case must be A or B')
    if T<=0 or not math.isfinite(T): raise ValueError('invalid T')
    l=LAM/T
    if case=='A': a,p,c,r,d,hcoef,hpow=1.269e-13,1.503,.522,.470,1.923,3e-14,.654
    else: a,p,c,r,d,hcoef,hpow=2.753e-14,1.5,2.740,.407,2.242,1.26e-14,.750
    u=(l[[0,2]]/c)**r
    rr=np.array([a*l[0]**p/(1+u[0])**d,hcoef*l[1]**hpow,
                 2*a*l[2]**p/(1+u[1])**d])
    g=np.array([-p+d*r*u[0]/(1+u[0]),-hpow,-p+d*r*u[1]/(1+u[1])])
    gp=np.array([-d*r*r*u[0]/(1+u[0])**2,0.,-d*r*r*u[1]/(1+u[1])**2])
    return rr,g,gp

def dr_components(T:float):
    """Two positive resonance measures, with the EXACT pinned decimal exponents.
    A T^-3/2 exp(-B/T) has kinetic loss kB*B per capture.
    """
    a1=DR_A*T**-1.5*math.exp(-DR_B1/T)
    a2=.3*DR_A*T**-1.5*math.exp(-(DR_B1+DR_B2)/T)
    return np.array([a1,a2]), np.array([KB*DR_B1,KB*(DR_B1+DR_B2)])

def collisional(T:float):
    l=LAM/T
    A=np.array([21.11,32.38,19.95])
    p=np.array([-1.089,-1.146,-1.089])
    c=np.array([.354,.416,.553])
    r=np.array([.874,.987,.735])
    d=np.array([1.101,1.056,1.275])
    return A*T**-1.5*np.exp(-l/2)*l**p/(1+(l/c)**r)**d

def cross_section(species:int,E:float):
    if not math.isfinite(E) or E<0: raise ValueError('invalid E')
    rows=json.loads((ROOT/'inputs/VERNER96_HHE_PARAMETERS.json').read_text())['rows']
    row=[float(x) for x in rows[species]]
    _,_,eth,emax,e0,s0,ya,p,yw,y0,y1=row
    if E>emax: raise ValueError('Verner high energy domain')
    if E<eth: return 0.
    x=E/e0-y0; y=math.sqrt(x*x+y1*y1)
    return s0*1e-18*((x-1)**2+yw*yw)*y**(.5*p-5.5)/(1+math.sqrt(y/ya))**p

SIGMA=np.array([[cross_section(s,E) for E in ENERGY] for s in range(3)])

def thermodynamics(v):
    x,y,z=v[:3]
    e=x+F*(y+2*z); nu=1+F+e
    return e,nu,2*v[6]*EV/(3*KB*nu)

def binding(v):
    x,y,z=v[:3]
    return CHI[0]*x+F*(CHI[1]*y+(CHI[1]+CHI[2])*z)

def initial_state():
    e=X0[0]+F*(X0[1]+2*X0[2]); nu=1+F+e
    return np.r_[X0,P0,1.5*KB*T0*nu/EV,0.,np.zeros(12)]

# ledger columns: photo3, CI3, RR3, DR2, reserved_zero1; escape at index7.
def rhs(tau,v, frozen_rates=False, helium_raw_cooling=False, guards=True):
    e,nu,T=thermodynamics(v)
    if guards: check_temperature(T)
    Tf=T0 if frozen_rates else T
    x,y,z=v[:3]; lower=np.array([1-x,F*(1-y-z),F*y]); upper=np.array([x,F*y,F*z])
    alpha,g,_=recombination(Tf)
    beta=collisional(Tf)
    dr,epsdr=dr_components(Tf)
    photo=C*NH*SIGMA*lower[:,None]*v[3:6][None,:]
    ci=NH*e*lower*beta
    rr=NH*e*upper*alpha
    dr_events=NH*e*(F*y)*dr
    net=photo.sum(axis=1)+ci-rr
    net[1]-=dr_events.sum()
    out=np.zeros_like(v)
    out[:3]=[net[0],(net[1]-net[2])/F,net[2]/F]
    out[3:6]=-photo.sum(axis=0)
    # frozen-rates control freezes alpha/beta, but retains kinetic energy at actual T.
    epsrr=KB*T*(1.5+g)/EV
    if helium_raw_cooling:
        lam=LAM[2]/T
        raw=8*1.778e-29*T*lam**1.965/(1+(lam/.541)**.502)**2.697
        epsrr[2]=raw/alpha[2]/EV
    heat=np.sum(photo*(ENERGY[None,:]-CHI[:,None]))
    kinetic=rr@epsrr+dr_events@(epsdr/EV)
    out[6]=heat-ci@CHI-kinetic
    out[7]=rr@(CHI+epsrr)+dr_events.sum()*CHI[1]+dr_events@(epsdr/EV)
    out[8:11]=photo.sum(axis=1);out[11:14]=ci;out[14:17]=rr;out[17:19]=dr_events
    return TEND*out

MODEL_POLICY={
 'id':'REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1',
 'geometry':'static homogeneous gas rest frame',
 'T_guard_K':[TMIN,TMAX], 'time_end_s':TEND,
 'rr_rate_source':'Hui-Gnedin Appendix A Case A, direct analytic fit',
 'rr_kinetic_cooling':'kB*T*(1.5*alpha+T*dalpha/dT), NEW derived model, not raw cooling parity',
 'ci_rate_source':'Hui-Gnedin Appendix A three CI fits',
 'ci_thermal_per_event':'-chi_s, not raw source q',
 'DR':'two positive exponential terms of pinned Grackle k4 high-T Case A; no cutoff within declared domain',
 'DR_domain_evidence':'implementation-defined guard; HG family range overlaps, exact-fit physical error unresolved',
 'disabled_effective_channels':['ceHeI','ciHeIS','ceHI','ceHeII','brem','Compton','HH','charge_exchange','molecules','metals'],
 'disabled_policy':'exact zero by explicit controlled-model definition, no negligibility claim',
 'recombination_emission':'all energy escapes; capture counts NOT emitted-photon multiplicity',
 'atomic_cascade':'instantaneous cascade to ground; all emitted energy escapes, no level-resolved kinetics',
 'primary_only':'controlled truncation, no secondary-ionization accuracy claim',
 'threshold':'retain Verner fit threshold distinct from binding chi',
 'state':'x_HII,x_HeII,x_HeIII,p1,p2,p3,w,escaped_energy,12 event ledgers',
 'density_units':'proper cm^-3', 'thermal_energy':'eV per hydrogen nucleus',
 'source_physical_uncertainty':'not a rigorous bound; rate fit error does not bound differentiated cooling error',
 'physical_provider_admitted':False,'canonical_task_changes':[],
 'initial':{'n_H':NH,'n_He_over_n_H':F,'fractions':X0.tolist(),'T_K':T0,'p':P0.tolist(),'E_eV':ENERGY.tolist()}
}
if __name__=='__main__':
    (ROOT/'MODEL_POLICY.json').write_text(json.dumps(MODEL_POLICY,indent=2)+'\n')
