"""Independent factor-isolation comparator for photon births and absorption clocks.

Toy 0D photon/neutral physics only. This is NOT PR150 native radiation/chemistry.
Number units: photons and HI/HII stocks per TOTAL hydrogen nucleus.
Time variable X=ln(a/a0), S=dN_birth/dX, k(X)=rate factor per dX
(per neutral stock), with ONE fixed-energy photon group E >= HI binding chi.
No photon redshift or geometric work, no RR/CI/DR or physical EoR source.

Equations: N' = S-k*N*M, M'=-k*N*M, I'=k*N*M, B'=S, A'=k*N*M.
The exact positive mass-action pair flow is used for the controlled midpoint
Strang implementation; other variants isolate birth timing, rate timing, or BE.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import ceil, exp, expm1, fsum, isfinite, sqrt
from typing import Literal
import numpy as np
from scipy.integrate import solve_ivp

Mode=Literal['mid_mid','source_left','opacity_left','both_left','birth_start','chem_be']
MODES=('mid_mid','source_left','opacity_left','both_left','birth_start','chem_be')

@dataclass(frozen=True)
class Experiment:
    n0:float=.23
    neutral0:float=.8
    source0:float=.31
    source_slope:float=.85
    opacity0:float=2.1
    opacity_slope:float=.9
    t_end:float=.8
    energy_ev:float=80.0
    threshold_ev:float=13.6

    def __post_init__(self):
        vals=(self.n0,self.neutral0,self.source0,self.source_slope,
              self.opacity0,self.opacity_slope,self.t_end,self.energy_ev,
              self.threshold_ev)
        if not all(isfinite(v) for v in vals):raise ValueError('all inputs finite')
        if min(self.n0,self.neutral0,self.source0,self.opacity0)<0:
            raise ValueError('nonnegative photon, neutral, source and rate required')
        if not (0<self.neutral0<=1 and self.t_end>0 and
                self.energy_ev>=self.threshold_ev>0):
            raise ValueError('invalid physical support')
        if min(self.source(0.),self.source(self.t_end),
               self.opacity(0.),self.opacity(self.t_end))<0:
            raise ValueError('time-dependent source/opacity must be positive')

    def source(self,t:float)->float:
        return self.source0*(1+self.source_slope*t)

    def opacity(self,t:float)->float:
        return self.opacity0*(1+self.opacity_slope*t)

@dataclass(frozen=True)
class Output:
    photons:float
    neutral:float
    ionized:float
    births:float
    absorptions:float
    binding_ev:float
    heat_ev:float
    stages:int
    max_exposure:float
    mode:str

    @property
    def ledger_photon(self):
        raise AttributeError('need initial photon stock; use ledgers(output, experiment)')


def pair_exact(n:float,m:float,z:float)->float:
    """Reacted amount for N'=M'=-k N M, exposure z=k*DeltaX."""
    if not all(isfinite(v) and v>=0 for v in (n,m,z)):
        raise ValueError('nonnegative finite pair required')
    if not min(n,m,z):return 0.
    lo,hi=min(n,m),max(n,m)
    d=hi-lo
    if d==0:return lo*lo*z/(1+lo*z)
    u=-expm1(-d*z)
    return min(lo,lo*hi*u/(d+lo*u))


def pair_be(n:float,m:float,z:float)->float:
    """Implicit backward Euler pair flow as an explicit positive quadratic root."""
    if not all(isfinite(v) and v>=0 for v in (n,m,z)):
        raise ValueError('nonnegative finite pair required')
    if not min(n,m,z):return 0.
    # z a^2 - [1+z(n+m)]a + z*n*m = 0, smaller root.
    b=1+z*(n+m)
    return min(n,m,2*z*n*m/(b+sqrt(b*b-4*z*z*n*m)))


def evolve(problem:Experiment,steps:int,mode:Mode='mid_mid')->Output:
    if mode not in MODES:raise ValueError('unknown placement mode')
    if not isinstance(steps,int) or steps<=0 or steps>100000:
        raise ValueError('invalid step count')
    n,m=problem.n0,problem.neutral0
    born,reacted,bind,heat=0.,0.,0.,0.
    most=0.
    h=problem.t_end/steps
    for i in range(steps):
        t=i*h;tm=t+h/2
        source=problem.source(t if mode in ('source_left','both_left') else tm)
        rate=problem.opacity(t if mode in ('opacity_left','both_left') else tm)
        db=h*source; z=h*rate
        old_n=n
        if mode=='birth_start':
            n+=db
            a=pair_exact(n,m,z)
        else:
            n+=db/2
            a=(pair_be if mode=='chem_be' else pair_exact)(n,m,z)
        n-=a;m-=a
        if mode!='birth_start':n+=db/2
        if n < -1e-14 or m < -1e-14:
            raise ArithmeticError('negative stock')
        most=max(most,z*problem.neutral0)
        born+=db;reacted+=a
        bind+=problem.threshold_ev*a
        heat+=(problem.energy_ev-problem.threshold_ev)*a
    return Output(n,m,problem.neutral0-m,born,reacted,bind,heat,steps,most,mode)


def ledgers(out:Output,p:Experiment)->dict:
    return {
        'photons':p.n0+out.births-out.absorptions-out.photons,
        'neutral_atoms':p.neutral0-out.absorptions-out.neutral,
        'ion_reactions':out.ionized-out.absorptions,
        'energy_ev':p.energy_ev*(p.n0+out.births-out.photons)-out.binding_ev-out.heat_ev,
        'min_stock':min(out.photons,out.neutral,out.ionized,out.binding_ev,out.heat_ev),
    }


def radau(p:Experiment,rtol:float=1e-12)->np.ndarray:
    def rhs(t,y):
        n,m=y[0],y[1]
        react=p.opacity(t)*n*m
        source=p.source(t)
        return [source-react,-react,source,react]
    y0=[p.n0,p.neutral0,0.,0.]
    ref=solve_ivp(rhs,(0.,p.t_end),y0,method='Radau',rtol=rtol,
                  atol=1e-14,max_step=p.t_end/150)
    if not ref.success:raise RuntimeError(ref.message)
    return ref.y[:,-1]


def independent_exact_photon(p:Experiment)->tuple[float,float,float]:
    """Independent manufactured linear *prescribed* rate k(x) (no gas reaction)."""
    from scipy.integrate import quad
    def tau(t):
        k0,b=p.opacity0,p.opacity_slope
        return k0*((p.t_end-t)+.5*b*(p.t_end**2-t**2))
    n=p.n0*exp(-tau(0.)) + quad(lambda t:p.source(t)*exp(-tau(t)),0,p.t_end,epsabs=5e-14,epsrel=5e-13)[0]
    births=quad(p.source,0,p.t_end,epsabs=5e-14,epsrel=5e-13)[0]
    return n,births,p.n0+births-n


def linear_frozen_midpoint(p:Experiment,steps:int,mode:Mode='mid_mid'):
    if mode not in MODES:raise ValueError('bad mode')
    n=p.n0;b=0.;a=0.;h=p.t_end/steps
    for i in range(steps):
        t=i*h;tm=t+h/2
        s=p.source(t+h if mode == 'chem_be' else (t if mode in ('source_left','both_left') else tm))
        k=p.opacity(t if mode in ('opacity_left','both_left') else tm)
        kh=k*h
        decay=exp(-kh)
        phi=-expm1(-kh)/kh if kh else 1.
        new=(n+s*h)*decay if mode=='birth_start' else (
            (n+h*p.source(t+h))/(1+h*p.opacity(t+h)) if mode=='chem_be' else
            n*decay+s*h*phi)
        absorbed=n+s*h-new
        n=new;b+=s*h;a+=absorbed
    return np.array((n,b,a))


def slope(e1:float,e2:float)->float:
    from math import log2
    if min(e1,e2)<=0:return float('nan')
    return log2(e1/e2)
