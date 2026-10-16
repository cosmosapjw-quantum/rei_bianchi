"""Source-free native-Grackle Case-A CI/CE/free-free/CMB clock comparator.

Source authority: rei_bianchi PR150 at frozen 6ea2b1b4b3875c9163cafc45efe720afded43fc4.
Exact owner igm_rates.rs SHA256: 310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf.
Exact owner igm_thermal.rs SHA256: 30515d96270ec73a37829ba298513a42112991168479d3cb40f33b67fd469ab2.
This is a standalone Python translation of the *specified subset* of native rate
and thermal point equations; it is NOT the original Rust Driver::fixed_step.

State X=ln(a/a0); x=(HII, HeII, HeIII), W thermal eV per *total-H nucleus*.
No photons, stellar birth, photoheating, or spectral transfer. Background H(a),
proper nH(a) and EOS are from the original owner. The microphysics is Case A.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, expm1, log, log10, sqrt, pi, isfinite, fsum
from typing import Mapping
import numpy as np
from scipy.optimize import root
from scipy.integrate import solve_ivp

# Import actual independent V7 frozen-owner FLRW cosmology reference already in repo.
import sys
from pathlib import Path
V7DIR = Path(__file__).resolve().parents[2] / 'v7' / 'reference'
if not V7DIR.exists():
    # Local archive presentation: copied original V7 file only, with source SHA noted.
    V7DIR = Path(__file__).resolve().parent / 'v7_native'
if str(V7DIR) not in sys.path:
    sys.path.insert(0, str(V7DIR))
import radau_casea_reference as v7

KB = v7.KB_ERG_K
EV = v7.EV_ERG
Y = v7.HE_H
CHI = np.asarray(v7.THRESHOLD_EV,float)
C_CM_S = 2.99792458e10
SIGMA_T = 6.6524587051e-25
M_E = 9.1093837139e-28
PLANCK = 6.62607015e-27
A_RAD = 8*pi**5*KB**4/(15*PLANCK**3*C_CM_S**3)
CMB_COEFF = 4*SIGMA_T*A_RAD*KB/(M_E*C_CM_S)
LOG_CAP = 69.07755278982137

@dataclass(frozen=True)
class NativeRates:
    ci: tuple[float,float,float]
    rr: tuple[float,float,float]
    dr: float
    ce: tuple[float,float,float]
    rr_cool: tuple[float,float,float]
    dr_cool: float
    dr_raw_cool: float
    ff: float


def native_rates(t:float)->NativeRates:
    """Independent literal Python port of frozen igm_rates.rs, all native 13 rates.

    Native floors for collisional ionization and caps for collisional excitation
    are left unchanged; no clipping *state* or retroactive rate correction.
    """
    if not isfinite(t) or not 1.0<=t<=1e6:
        raise ValueError('IGM_TEMPERATURE_DOMAIN')
    te=t/11605.0
    l=log(te)
    def xp(cs):
        return exp(sum(c*l**i for i,c in enumerate(cs)))
    k1=xp((-32.71396786375,13.53655609057,-5.739328757388,1.563154982022,
           -0.2877056004391,0.03482559773736999,-0.00263197617559,0.0001119543953861,-2.039149852002e-6))
    if te<=0.8:k1=max(k1,1e-20)
    k3=xp((-44.09864886561001,23.91596563469,-10.75323019821,3.058038757198,
           -0.5685118909884001,0.06795391233790001,-0.005009056101857001,0.0002067236157507,-3.649161410833e-6)) if te>0.8 else 1e-20
    k5=xp((-68.71040990212001,43.93347632635,-18.48066993568,4.701626486759002,
           -0.7692466334492,0.08113042097303,-0.005324020628287001,0.0001975705312221,-3.165581065665e-6)) if te>0.8 else 1e-20
    he_rr=3.92e-13/te**0.6353
    k2=xp((-28.61303380689232,-0.7241125657826851,-0.02026044731984691,
           -0.002380861877349834,-0.0003212605213188796,-0.00001421502914054107,
           4.989108920299513e-6,5.755614137575758e-7,-1.856767039775261e-8,
           -3.071135243196595e-9)) if t>5500 else he_rr
    k6=3.36e-10/sqrt(t)/(t/1e3)**0.2/(1+(t/1e6)**0.7)
    dr=0.0 if te<=0.8 else 1.54e-9*(1+0.3/exp(8.099328789667/te))/(exp(40.49664394833662/te)*te**1.5)
    ci=(k1,k3,k5)
    ce=(7.5e-19*exp(-min(118348.0/t,LOG_CAP))/(1+sqrt(t/1e5)),
        9.1e-27*exp(-min(13179.0/t,LOG_CAP))*t**(-0.1687)/(1+sqrt(t/1e5)),
        5.54e-17*exp(-min(473638.0/t,LOG_CAP))*t**(-0.3970)/(1+sqrt(t/1e5)))
    lh=2*157807.0/t; li=2*285335.0/t; l3=2*631515.0/t
    def rec(lam):return 1.778e-29*t*lam**1.965/(1+(lam/0.541)**0.502)**2.697
    rrc=(rec(lh),3e-14*1.3806504e-16*t*li**0.654,8*rec(l3))
    drraw=1.24e-13*t**-1.5*exp(-min(470000.0/t,LOG_CAP))*(1+0.3*exp(-min(94000.0/t,LOG_CAP)))
    ff=1.43e-27*sqrt(t)*(1.1+0.34*exp(-(5.5-log10(t))**2/3.0))
    rates=NativeRates(ci,(k2,he_rr,k6),dr,ce,rrc,0. if te<=0.8 else drraw,drraw,ff)
    if not all(isfinite(a) and a>=0 for a in (*ci,*rates.rr,dr,*ce,*rrc,drraw,ff)):
        raise ArithmeticError('INVALID_GRACKLE_RATE')
    return rates


def grackle_literal_table_parity(path:Path)->dict:
    """Original checked-in independent C table: all 129 rows, 16 coefficients."""
    import csv
    with Path(path).open(newline='') as f:rows=list(csv.DictReader(f))
    worst=0.0
    for row in rows:
        t=float(row['T_K']);o=native_rates(t)
        vals=(*o.ci,*o.rr,o.dr,*o.ce,*o.rr_cool,o.dr_raw_cool,o.ff,o.rr[1]+o.dr,o.dr_cool)
        keys=tuple(row)[1:]
        assert len(vals)==len(keys)==17,(len(vals),len(keys))
        for k,v in zip(keys,vals):
            true=float(row[k]);worst=max(worst,abs(v-true)/max(abs(true),1e-200))
    return {'rows':len(rows),'columns':17,'max_relative_difference':worst}

@dataclass(frozen=True)
class Clock:
    ci:str='end'
    rr:str='end'
    ce:str='end'
    ff:str='end'
    cmb:str='end'

    def __post_init__(self):
        if any(getattr(self,s) not in ('end','mid') for s in ('ci','rr','ce','ff','cmb')):
            raise ValueError('CLOCK_PHASE_INVALID')

CLOCKS={
 'owner_like_be':Clock(),
 'ci_mid':Clock(ci='mid'),
 'ce_mid':Clock(ce='mid'),
 'ff_mid':Clock(ff='mid'),
 'cmb_mid':Clock(cmb='mid'),
 'thermal_mid':Clock(ce='mid',ff='mid',cmb='mid'),
 'chemical_mid':Clock(ci='mid',rr='mid'),
 'all_mid':Clock(ci='mid',rr='mid',ce='mid',ff='mid',cmb='mid'),
}

COMPONENTS=('CI_HI','CI_HeI','CI_HeII','RR_HII','RR_HeII','RR_HeIII','DR_HeII',
            'CE_HI','CE_HeI','CE_HeII','FreeFree','CMB')


def temperature(st:np.ndarray)->float:
    x,y,z,w=np.asarray(st)[:4]
    gas_particles=1+Y+x+Y*(y+2*z)
    if gas_particles<=0 or w<=0:raise ValueError('NONPOSITIVE_GAS_THERMAL')
    return w*EV/(1.5*KB*gas_particles)


def valid_state(q:np.ndarray)->bool:
    x,y,z,w=q[:4]
    return all(np.isfinite(q[:4])) and 0<=x<=1 and 0<=y and 0<=z and y+z<=1 and w>0 and 1.0<=temperature(q)<=1e6


def initial_state(T0:float=15000.0, fractions:tuple[float,float,float]=v7.INITIAL_FRACTIONS)->np.ndarray:
    x,y,z=fractions
    w=1.5*KB*T0*(1+Y+x+Y*(y+2*z))/EV
    q=np.array([x,y,z,w],dtype=float)
    if not valid_state(q):raise ValueError('INVALID_INITIAL_STATE')
    return q


def analytic_components(x:float,q:np.ndarray,density_factor:float=1.0):
    """Rates per *total H per unit X* and energy eV/H per unit X.

    Return 12 positive/signed ledger rates, independent of the discrete scheme.
    Same Grackle coefficients and thermal point transformations as the frozen Rust.
    """
    if density_factor<0 or not isfinite(density_factor):raise ValueError('DENSITY_FACTOR')
    a=v7.A0*exp(x)
    H=v7.hubble(a)
    nh=density_factor*v7.density(a)[0]
    Yloc=Y
    xx,yy,zz,w=q[:4]
    if not valid_state(q):raise ValueError('NONPHYSICAL_GAS_STATE')
    T=temperature(q)
    ne=nh*(xx+Yloc*(yy+2*zz))
    r=native_rates(T)
    neutral=np.array([1-xx,Yloc*(1-yy-zz),Yloc*yy],dtype=float)
    ions=np.array([xx,Yloc*yy,Yloc*zz],dtype=float)
    # CI, RR/DR rates normalized by total H, not neutral HI or helium per-nucleus.
    ci=ne*neutral*np.array(r.ci)/H
    rr=ne*ions*np.array(r.rr)/H
    dr=ne*ions[1]*r.dr/H
    ce=np.array([ne*neutral[0]*r.ce[0],ne**2*ions[1]*r.ce[1],ne*ions[1]*r.ce[2]])/(H*EV)
    ff=ne*(ions[0]+ions[1]+4*ions[2])*r.ff/(H*EV)
    tcmb=2.7255/a
    cmb=CMB_COEFF*(ne)*(tcmb**4)*(tcmb-T)/(nh*H*EV) if nh else 0.0
    return np.array([*ci,*rr,dr,*ce,ff,cmb],dtype=float), np.array([*r.rr_cool,r.dr_cool])*(ne*np.array([*ions,ions[1]]))/(H*EV)


def sample_rates(x:float,q:np.ndarray,density_factor:float):
    return analytic_components(x,q,density_factor)


def integrated_effects(x:float,q:np.ndarray,density_factor:float=1.0):
    """Return fraction/thermal derivative and 12 rate ledgers + 4 RR cooling."""
    vals,rrc=sample_rates(x,q,density_factor)
    ci=vals[0:3];rr=vals[3:6];dr=vals[6]
    ce=vals[7:10];ff=vals[10];cmb=vals[11]
    xx=(ci[0]-rr[0]);zz=(ci[2]-rr[2])/Y
    yy=(ci[1]-rr[1]-dr-ci[2]+rr[2])/Y
    micro=-float(np.dot(ci,CHI))-sum(rrc)-sum(ce)-ff+cmb
    return np.array([xx,yy,zz,micro]), vals,rrc


def rhs_continuous(x:float,y:np.ndarray,density_factor:float=1.0)->np.ndarray:
    """Actually independent continuous RHS, *not* a call to an integration method."""
    ff,vals,cool=integrated_effects(x,y,density_factor)
    out=np.zeros_like(y)
    out[:3]=ff[:3];out[3]=ff[3]-2*y[3]
    if len(out)>4:
        out[4:16]=vals;out[16:20]=cool;out[20]=2*y[3]
    return out


def binding(q:np.ndarray)->float:
    xx,yy,zz=q[:3]
    return CHI[0]*xx+Y*(CHI[1]*(yy+zz)+CHI[2]*zz)


def energy_ledger(y:np.ndarray, y0:np.ndarray)->float:
    ci,rr,dr=y[4:7],y[7:10],y[10]
    escaped=(float(np.dot(rr,CHI))+CHI[1]*dr+float(np.sum(y[16:20]))+
             float(np.sum(y[11:14]))+y[14])
    cmb_input=y[15]
    return y0[3]+binding(y0)-(y[3]+binding(y)+escaped+y[20]-cmb_input)


def reference(x_end:float=1e-5,density_factor:float=1.,rtol:float=2e-12):
    y=np.zeros(21);y[:4]=initial_state()
    sol=solve_ivp(lambda x,v:rhs_continuous(x,v,density_factor),(0,x_end),y,
                  method='Radau',rtol=rtol,atol=np.array([1e-14]*3+[1e-14]+[1e-17]*16+[1e-14]),
                  max_step=x_end/80)
    if not sol.success:raise RuntimeError(sol.message)
    return sol


def piecewise_advance(y0:np.ndarray,x0:float,x1:float,clock:Clock, density_factor:float=1.,
                      *,resid_tol:float=2e-11):
    """Discrete source-free native-like adiabatic / chemistry / adiabatic composition.

    Chemistry micro (all H and He CI/RR/DR, CE, FF, CMB) is solved with a
    single nonlinear root. Each process's time evaluation is independently
    selected at the state midpoint or endpoint; the same process rates feed
    both state and ledger, preventing double ownership. No silent projection.
    """
    h=x1-x0;xm=0.5*(x1+x0)
    if not h>0:raise ValueError('NONPOSITIVE_STEP')
    H=v7.hubble(v7.A0*exp(xm));dtX=h  # explicit time equation dY/dX=R/H
    pre=np.array(y0,copy=True)
    pre[3]*=exp(-h)
    # For freeze homogeneous geometry during chemistry at the physical half-step
    # the evolving coordinate density is evaluated at xm.
    def probe(q):
        mid=0.5*(pre[:4]+q)
        if not valid_state(q) or not valid_state(mid):
            return None
        mend,mcool=analytic_components(xm,q,density_factor)
        mmid,mcool_mid=analytic_components(xm,mid,density_factor)
        # evaluate source/driven elements at different time state clocks
        ci=mend[:3] if clock.ci=='end' else mmid[:3]
        rr=mend[3:7] if clock.rr=='end' else mmid[3:7]
        ce=mend[7:10] if clock.ce=='end' else mmid[7:10]
        ff=mend[10] if clock.ff=='end' else mmid[10]
        cmb=mend[11] if clock.cmb=='end' else mmid[11]
        rr_cool=mcool if clock.rr=='end' else mcool_mid
        vals=np.concatenate([ci,rr,ce,[ff,cmb]])
        # 3 CI, 3 RR, 1 DR, 3 CE, 1 FF, 1 CMB = 12
        dx=ci[0]-rr[0];dz=(ci[2]-rr[2])/Y
        dy=(ci[1]-rr[1]-rr[3]-ci[2]+rr[2])/Y
        dw=-float(np.dot(ci,CHI))-float(np.sum(rr_cool))-float(np.sum(ce))-ff+cmb
        return np.array([dx,dy,dz,dw]),vals,rr_cool
    def residual(q):
        checked=probe(q)
        if checked is None:
            # We allow no projection on the accepted state; an intermediate nonlinear
            # probe can be outside simplex, but must not be used to evaluate rates.
            return q-pre[:4]+1e4*np.maximum(-q,0.) + 1e4*np.array([max(0,q[0]-1),max(0,q[1]+q[2]-1),0,0])
        dy,*_=checked
        return q-pre[:4]-dtX*dy
    q0=pre[:4].copy()
    ff0=probe(q0)
    if ff0 is None: raise ArithmeticError('BAD_OLD_STATE')
    q0+=h*ff0[0]
    q0=np.array([*np.clip(q0[:3],1e-15,1-1e-15),max(q0[3],1e-12)])
    if q0[1]+q0[2]>=1:q0[1:3]*=.99/(q0[1]+q0[2])
    rootans=root(residual,q0,method='hybr',options={'xtol':1e-12,'maxfev':450})
    q=rootans.x
    actual=probe(q)
    r=residual(q)
    if actual is None or not valid_state(q) or not np.all(np.isfinite(q)) or np.linalg.norm(r,np.inf)>resid_tol:
        raise ArithmeticError(f'MICROSTEP_NOT_CONVERGED: {rootans.message} res={np.linalg.norm(r,np.inf)}')
    # Exact geometry half-flow, applied to the chemistry output.
    nextY=np.array(pre,copy=True)
    nextY[:4]=q
    nextY[3]*=exp(-h)
    nextY[4:16]+=h*actual[1]
    nextY[16:20]+=h*actual[2]
    # precise gas work on two half flows (e^-h each)
    nextY[20]+=(y0[3]-pre[3])+(q[3]-nextY[3])
    return nextY, float(np.linalg.norm(r,np.inf))


def integrate_clock(clock:Clock,steps:int,x_end:float=1e-5,density_factor:float=1.0)->tuple[np.ndarray,float]:
    if not (1<=steps<=8192): raise ValueError('STEP_BUDGET')
    y=np.zeros(21,dtype=float);y[:4]=initial_state()
    residual=0.0
    for i in range(steps):
        y,rr=piecewise_advance(y,x_end*i/steps,x_end*(i+1)/steps,clock,density_factor)
        residual=max(residual,rr)
    return y,residual
