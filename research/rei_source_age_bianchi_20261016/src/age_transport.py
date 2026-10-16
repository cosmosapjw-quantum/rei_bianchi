"""Conditional source-age and signed-LRS-Bianchi photon transport oracle.

Scope: positive independent birth cohorts, prescribed homogeneous proper neutral
stocks, original Verner 1996 H I/He I/He II fit rows, exact collisionless Killing
energy, event-aligned exponential competing absorption. NOT a live native Grackle
chemistry, MD14 source, or Einstein backreaction solver.

Variables x=ln(a/a_ref), a_ref=1, b'=s/H, metric
(-,+,+,+): ds^2=-c^2 dt^2+a^2[e^(-2b) dX_perp^2 + e^(4b) dz^2].
Each emitted photon has physical E_birth [eV], mu_birth, x_birth.
Source j(x_birth) is photon count per reference H per d ln a, isotropic in mu.
Hazards d tau_i/dx=kappa_i exp(-3x) sigma_i(E)/sigma_i(chi_i),
with kappa_i = c n_i,ref sigma_i(chi_i)/H_ref dimensionless and H/H_ref=1.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, expm1, ceil, pi, sin, cos, sqrt, isfinite, fsum
from typing import Callable
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import solve_ivp, quad

# Verner et al. 1996 Table 1 original rows (Z,N)=(1,1),(2,2),(2,1).
# Original donor at https://www.pa.uky.edu/~verner/dima/photo//photo.dat
# Published complete donor SHA256: a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389.
# params: chi[eV], Emax[eV], E0[eV], sigma0[Mb], ya, P, yw, y0, y1.
VERNER = {
    "HI": (13.60, 5e4, .4298, 54750.0, 32.88, 2.963, 0., 0., 0.),
    "HeI": (24.59, 5e4, 13.61, 949.2, 1.469, 3.188, 2.039, .4434, 2.136),
    "HeII": (54.42, 5e4, 1.720, 13690.0, 32.88, 2.963, 0., 0., 0.),
}
SPECIES = tuple(VERNER)
FIT_THRESHOLDS_EV = tuple(VERNER[s][0] for s in SPECIES)
# Native HHeModel::controlled_fixture physical ionization binding, NOT the
# rounded spectral activation points in the Verner Table-1 fitting functions.
# Source: rei_bianchi PR150 rust/rei_microphysics/src/hhe_events.rs
BINDING_EV = (13.598434599702, 24.587389011, 54.41776)
CHI = FIT_THRESHOLDS_EV  # explicitly only for spectral activation/cut root



def sigma_mb(name: str, E: float) -> float:
    if name not in VERNER or not isfinite(E) or E < 0.:
        raise ValueError("invalid fit or energy")
    chi, emax, e0, sigma0, ya, power, yw, y0, y1 = VERNER[name]
    if E < chi:
        return 0.
    if E > emax:
        raise ValueError("energy outside original Verner fit domain")
    x = E/e0-y0
    y = sqrt(x*x+y1*y1)
    ans = sigma0*((x-1.)**2+yw*yw)*y**(.5*power-5.5)*(1.+sqrt(y/ya))**(-power)
    if not isfinite(ans) or ans < 0.:
        raise ArithmeticError("invalid Verner fit")
    return ans

SIGMA_AT_THRESHOLD = tuple(sigma_mb(s,c) for s,c in zip(SPECIES,CHI))


@dataclass(frozen=True)
class Model:
    x_end: float = .7
    e_birth_ev: float = 82.0
    kappa_th: tuple[float,float,float] = (.8,.45,.65)
    signed_v0: float = .04
    b_osc_amp: float = 0.
    b_osc_freq: float = 0.
    source_norm: float = 1.
    source_amplitude: float = .25
    def __post_init__(self):
        vals = (self.x_end, self.e_birth_ev, self.signed_v0, self.b_osc_amp,
                self.b_osc_freq, self.source_norm, self.source_amplitude, *self.kappa_th)
        if not all(isfinite(x) for x in vals) or self.x_end<=0. or self.e_birth_ev<=0. \
                or self.e_birth_ev>min(VERNER[s][1] for s in SPECIES) or self.b_osc_freq<0. \
                or self.source_norm<0. or abs(self.source_amplitude)>1. \
                or any(v<0 for v in self.kappa_th):
            raise ValueError("invalid model/domain")
        if abs(self.signed_v0*self.x_end)+abs(self.b_osc_amp)*2.>15.:
            raise ValueError("outside finite exponential domain")
    def b(self,x: float)->float:
        return self.signed_v0*x+self.b_osc_amp*sin(self.b_osc_freq*x)
    def v(self,x: float)->float:
        return self.signed_v0+self.b_osc_amp*self.b_osc_freq*cos(self.b_osc_freq*x)
    def source(self,x: float)->float:
        return self.source_norm*(1.+self.source_amplitude*sin(2*pi*x/self.x_end))


def ray_geometry(model: Model, x_birth: float, x: float, mu_birth: float)->tuple[float,float]:
    if not (0<=x_birth<=x<=model.x_end+1e-13 and -1.<=mu_birth<=1.):
        raise ValueError("ray domain")
    delta=model.b(x)-model.b(x_birth)
    aperp=exp(2*delta)*(1-mu_birth*mu_birth)
    az=exp(-4*delta)*mu_birth*mu_birth
    rr=sqrt(aperp+az)
    E=model.e_birth_ev*exp(x_birth-x)*rr
    mu2=az/(rr*rr)
    return E,mu2


def hazards(model: Model, x_birth: float, x:float, mu_birth:float)->tuple[float,float,float]:
    E,_=ray_geometry(model,x_birth,x,mu_birth)
    dilution=exp(-3*x)
    return tuple(k*dilution*sigma_mb(s,E)/sigma_t
                 for k,s,sigma_t in zip(model.kappa_th,SPECIES,SIGMA_AT_THRESHOLD))


def geometric_loss_rate(model: Model, x_birth:float,x:float, mu:float)->float:
    E,mu2=ray_geometry(model,x_birth,x,mu)
    # -dE/dln a = E [1+ (s/H)(3mu^2 -1)]. Work may be signed.
    return E*(1.+model.v(x)*(3.*mu2-1.))


def _roots_of_threshold(model: Model, x_birth:float, mu:float,chi:float,scan:int=96)->list[float]:
    if scan<8:
        raise ValueError("inadequate event scan")
    xs=np.linspace(x_birth,model.x_end,scan+1)
    values=[ray_geometry(model,x_birth,float(x),mu)[0]-chi for x in xs]
    roots=[]
    for i in range(scan):
        a,b=float(xs[i]),float(xs[i+1]);va,vb=values[i:i+2]
        if va == 0. and x_birth<a<model.x_end:roots.append(a)
        if va*vb<0.:
            roots.append(brentq(lambda xx: ray_geometry(model,x_birth,xx,mu)[0]-chi,a,b,xtol=1e-14))
    return roots


def photon_events(model: Model, x_birth: float,mu: float, scan:int=96)->tuple[float,...]:
    roots=[x_birth,model.x_end]
    for s in SPECIES:
        if model.kappa_th[SPECIES.index(s)]>0.:
            roots.extend(_roots_of_threshold(model,x_birth,mu,VERNER[s][0],scan=scan))
    # Never round the birth/endpoints: rounding x_birth upward can create a
    # noncausal x0<x_birth; only deduplicate interior roots near floating noise.
    inner=sorted(x for x in roots[2:] if x_birth+1e-13<x<model.x_end-1e-13)
    kept=[x_birth]
    for x in inner:
        if x-kept[-1]>1e-12: kept.append(x)
    kept.append(model.x_end)
    return tuple(kept)


@dataclass(frozen=True)
class RayLedger:
    survivor: float
    absorbed: tuple[float,float,float]
    heat_ev: float
    work_ev: float
    final_energy_ev: float
    final_pi_ev: float
    photon_residual: float
    energy_residual: float
    event_count: int
    substeps: int


def _ray_ledger(model:Model,x_birth:float,mu:float,n_time:int,scan:int=96,
                *,independent:bool=False)->RayLedger:
    if n_time<1:raise ValueError("n_time must be positive")
    edges=photon_events(model,x_birth,mu,scan=scan)
    if independent:
        # Independent continuous differential RHS, not invoking discrete survivor/heat/work.
        def rhs(x,z):
            E,_=ray_geometry(model,x_birth,x,mu)
            lam=hazards(model,x_birth,x,mu)
            n=z[0]
            return [-n*fsum(lam), *(n*t for t in lam),
                    n*fsum(t*(E-c) for t,c in zip(lam,BINDING_EV)),
                    n*geometric_loss_rate(model,x_birth,x,mu)]
        z=np.array([1.,0.,0.,0.,0.,0.])
        for xa,xb in zip(edges[:-1],edges[1:]):
            if xb<=xa:continue
            s=solve_ivp(rhs,(xa,xb),z,method="DOP853",rtol=2e-11,atol=2e-13,
                        max_step=(model.x_end-x_birth)/max(3,n_time))
            if not s.success: raise ArithmeticError(s.message)
            z=s.y[:,-1]
        n=float(z[0]);a=tuple(float(v) for v in z[1:4]);heat=float(z[4]);work=float(z[5]);steps=-1
    else:
        n=1.;aa=[0.,0.,0.];heat=0.;work=0.;steps=0
        target_h=(model.x_end-x_birth)/n_time
        for xa,xb in zip(edges[:-1],edges[1:]):
            if xb<=xa:continue
            count=max(1,ceil((xb-xa)/target_h))
            h=(xb-xa)/count
            for j in range(count):
                x0=xa+h*j;xm=x0+.5*h;x1=x0+h
                e0,_=ray_geometry(model,x_birth,x0,mu)
                em,_=ray_geometry(model,x_birth,xm,mu)
                e1,_=ray_geometry(model,x_birth,x1,mu)
                work+=n*(e0-em)
                rates=hazards(model,x_birth,xm,mu)
                total=fsum(rates)
                if total>0.:
                    absorbed=n*(-expm1(-total*h))
                    frac=[absorbed*(rate/total) for rate in rates]
                    for i,z in enumerate(frac):aa[i]+=z
                    heat+=fsum(z*(em-chi) for z,chi in zip(frac,BINDING_EV))
                    n*=exp(-total*h)
                work+=n*(em-e1)
                steps+=1
        a=tuple(aa)
    E,mu2=ray_geometry(model,x_birth,model.x_end,mu)
    bind=fsum(c*z for c,z in zip(BINDING_EV,a))
    final_pi=n*E*(3*mu2-1.)/2.
    photon_res=1.-n-fsum(a)
    energy_res=model.e_birth_ev-n*E-bind-heat-work
    return RayLedger(n,a,heat,work,E,final_pi,photon_res,energy_res,len(edges)-2,steps)


def integrate_ray(model:Model,x_birth:float,mu:float,n_time:int=64,scan:int=96)->RayLedger:
    return _ray_ledger(model,x_birth,mu,n_time,scan)


def reference_ray(model:Model,x_birth:float,mu:float,n_time:int=64,scan:int=96)->RayLedger:
    return _ray_ledger(model,x_birth,mu,n_time,scan,independent=True)


def _gl(a:float,b:float,n:int):
    if n<1:raise ValueError("n quadrature must be positive")
    z,w=np.polynomial.legendre.leggauss(n)
    return (.5*(a+b)+.5*(b-a)*z,.5*(b-a)*w)


def age_event_boundaries(model:Model,mu_nodes:list[float]|np.ndarray,scan:int=96):
    """Positive age panels split where the *terminal* energy crosses any H/He threshold.
    This does not replace per-ray propagation threshold event alignment.
    """
    ygrid=np.linspace(0,model.x_end,scan+1)
    roots=[0.,model.x_end]
    for mu in mu_nodes:
        for i,chi in enumerate(CHI):
            if model.kappa_th[i]==0.:continue
            vals=[ray_geometry(model,float(y),model.x_end,float(mu))[0]-chi for y in ygrid]
            for k in range(scan):
                ya,yb=float(ygrid[k]),float(ygrid[k+1])
                if vals[k]*vals[k+1]<0.:
                    roots.append(brentq(lambda y:ray_geometry(model,y,model.x_end,float(mu))[0]-chi,ya,yb,xtol=1e-14))
    return tuple(sorted(set(round(float(y),13) for y in roots)))


@dataclass(frozen=True)
class Aggregate:
    emitted_photons:float
    emitted_ev:float
    survivors:float
    absorbed:tuple[float,float,float]
    heat_ev:float
    binding_ev:float
    work_ev:float
    final_photon_ev:float
    final_pi_ev:float
    photon_residual:float
    energy_residual:float
    ray_calls:int
    event_count:int
    substeps:int
    age_panels:int


def integrate_source(model:Model,age_nodes:int,mu_nodes:int,n_time:int=64,
                     *,age_split:bool=False,scan:int=96,independent:bool=False)->Aggregate:
    mu,ww=_gl(-1.,1.,mu_nodes)
    ww*=.5
    if age_split:
        edges=age_event_boundaries(model,mu,scan=max(96,scan))
        alloc=max(2,round(age_nodes/max(1,len(edges)-1)))
        age_q=[(float(y),float(w)) for xa,xb in zip(edges[:-1],edges[1:])
               for nodes,weights in [_gl(xa,xb,alloc)] for y,w in zip(nodes,weights)]
    else:
        edges=(0.,model.x_end)
        age_q=list(zip(*_gl(0.,model.x_end,age_nodes)))
    Nborn=Em=surv=heat=work=final_E=pi_E=0.
    absorption=[0.,0.,0.];calls=nevents=nsteps=0
    for y,wy in age_q:
        born=float(wy)*model.source(float(y))
        for mm,wmu in zip(mu,ww):
            weight=born*float(wmu)
            r=reference_ray(model,float(y),float(mm),n_time=n_time,scan=scan) if independent else \
                 integrate_ray(model,float(y),float(mm),n_time=n_time,scan=scan)
            Nborn+=weight;Em+=weight*model.e_birth_ev
            surv+=weight*r.survivor
            heat+=weight*r.heat_ev;work+=weight*r.work_ev
            final_E+=weight*r.survivor*r.final_energy_ev
            pi_E+=weight*r.final_pi_ev
            for i in range(3):absorption[i]+=weight*r.absorbed[i]
            calls+=1;nevents+=r.event_count;nsteps+=max(0,r.substeps)
    bind=fsum(a*chi for a,chi in zip(absorption,BINDING_EV))
    return Aggregate(Nborn,Em,surv,tuple(absorption),heat,bind,work,final_E,pi_E,
                     Nborn-surv-fsum(absorption),Em-final_E-bind-heat-work,
                     calls,nevents,nsteps,len(edges)-1)


def source_free_sharp_pi_bounds(model:Model,*,method:str="quad",n_age:int=32)->tuple[float,float]:
    """Sharp positive pressure interval for arbitrary reflection-even emitted skies.
    Independent angular sky may be chosen separately for every birth age.
    Applicable only before direction/energy-dependent absorption.
    """
    xe=model.x_end
    def kernels(y):
        d=model.b(xe)-model.b(y)
        common=model.source(y)*model.e_birth_ev*exp(y-xe)
        return (-.5*common*exp(d), common*exp(-2*d))
    if method=="quad":
        return tuple(quad(lambda y:kernels(y)[i],0,xe,epsabs=1e-12,epsrel=1e-12)[0] for i in range(2))
    if method=="gl":
        ys,ws=_gl(0.,xe,n_age)
        return tuple(fsum(float(w)*kernels(float(y))[i] for y,w in zip(ys,ws)) for i in range(2))
    raise ValueError(method)


def source_free_pressure(model:Model,mu:float,*,n_age:int=32)->float:
    ys,ws=_gl(0.,model.x_end,n_age)
    total=0.
    for y,w in zip(ys,ws):
        E,mu2=ray_geometry(model,float(y),model.x_end,mu)
        total+=float(w)*model.source(float(y))*E*(3*mu2-1.)/2.
    return total


def positive_blackbody_nodes(n_energy:int,*,emin:float=17.,emax:float=100.,
                             kt_ev:float=19.,split_birth_thresholds:bool=True):
    """Positive *manufactured* normalized photon spectral quadrature, NOT MD14.
    Emission number density proportional E^2/(exp(E/kT)-1) on finite support.
    n_energy counts nodes in the full interval (approximate if panelized).
    """
    if n_energy<2 or not (0<emin<emax<=5e4 and kt_ev>0):
        raise ValueError("invalid positive spectral quadrature")
    edges=[emin]+([c for c in CHI if emin<c<emax] if split_birth_thresholds else [])+[emax]
    panels=len(edges)-1;alloc=max(2,round(n_energy/panels))
    nodes=[]
    for a,b in zip(edges[:-1],edges[1:]):
        es,ws=_gl(a,b,alloc)
        for E,w in zip(es,ws):
            weight=float(w)*float(E*E/np.expm1(E/kt_ev))
            nodes.append((float(E),weight))
    mass=fsum(w for _,w in nodes)
    return [(E,w/mass) for E,w in nodes]


def integrate_spectral_source(model:Model,n_energy:int,n_age:int,n_mu:int,n_time:int,
                              *,split_birth_thresholds:bool=True,
                              age_split:bool=False,scan:int=96)->Aggregate:
    """Independent positive birth-energy packets across photon energy/age/mu.
    Cross-section-shaped absorption changes the spectral weights of survivors.
    No chemistry feedback or native stellar donor is inferred.
    """
    from dataclasses import replace
    pieces=[]
    for E,w in positive_blackbody_nodes(n_energy,split_birth_thresholds=split_birth_thresholds):
        pieces.append((w,integrate_source(replace(model,e_birth_ev=E),n_age,n_mu,n_time,
                                          age_split=age_split,scan=scan)))
    scalar=lambda k:fsum(w*getattr(v,k) for w,v in pieces)
    vector=tuple(fsum(w*v.absorbed[i] for w,v in pieces) for i in range(3))
    bind=fsum(x*y for x,y in zip(vector,BINDING_EV))
    return Aggregate(scalar("emitted_photons"),scalar("emitted_ev"),scalar("survivors"),
                     vector,scalar("heat_ev"),bind,scalar("work_ev"),
                     scalar("final_photon_ev"),scalar("final_pi_ev"),
                     scalar("photon_residual"),scalar("energy_residual"),
                     sum(v.ray_calls for _,v in pieces),
                     sum(v.event_count for _,v in pieces),sum(v.substeps for _,v in pieces),
                     max(v.age_panels for _,v in pieces))


@dataclass(frozen=True)
class AdaptiveAgeResult:
    result: Aggregate
    estimated_max_absolute_error: float
    accepted_panels: int
    max_recursion: int
    tolerances:tuple[float,float]


def adaptive_birth_age_source(model:Model,mu_nodes:int,n_time:int,
                              *,rtol:float=2e-5,atol:float=2e-8,
                              max_depth:int=9,scan:int=96,
                              event_panels:bool=True)->AdaptiveAgeResult:
    """Positive adaptive source-birth quadrature using embedded GL4/GL8.

    Integrates *source-age resolved photon cohorts* at fixed emission spectrum.
    Each accepted GL8 term is nonnegative for photon/absorption/heat; signed
    work and Pi may be positive or negative. The GL8-GL4 embedded difference is
    an empirical local estimator, not a guaranteed mathematical error enclosure.
    Fixed gas opacity/horizon; the algorithm does not mutate Grackle chemistry.
    """
    if not (0<rtol<1 and 0<atol<1 and 1<=max_depth<=20):
        raise ValueError("invalid adaptive birth-time budget")
    mu,mu_weights=_gl(-1.,1.,mu_nodes)
    mu_weights*=.5
    total=np.zeros(10,dtype=np.float64)
    ray_calls=events=steps=0
    accepted=0;estimated=0.;deepest=0
    scale=model.source_norm*model.x_end
    for mm,wm in zip(mu,mu_weights):
        cache={}
        def point(y:float):
            nonlocal ray_calls,events,steps
            if y not in cache:
                r=integrate_ray(model,y,float(mm),n_time=n_time,scan=scan)
                rate=model.source(y)
                cache[y]=np.array((rate,rate*model.e_birth_ev,
                    rate*r.survivor,*(rate*a for a in r.absorbed),rate*r.heat_ev,
                    rate*r.work_ev,rate*r.survivor*r.final_energy_ev,
                    rate*r.final_pi_ev),dtype=np.float64)
                ray_calls+=1;events+=r.event_count;steps+=r.substeps
            return cache[y]
        def gaussian(a,b,n):
            y,w=_gl(a,b,n)
            values=(point(float(yi)) for yi in y)
            return np.sum(np.array([float(wi)*vi for wi,vi in zip(w,values)]),axis=0)
        def recursive(a,b,depth):
            nonlocal accepted,estimated,deepest
            q8=gaussian(a,b,8)
            q4=gaussian(a,b,4)
            delta=np.abs(q8-q4)
            # Compare dimensionless components to one fixed *global* source
            # scale, including optical-depth-sensitive tiny species via atol.
            norms=np.array((1.,1/model.e_birth_ev,1.,1.,1.,1.,
                            1/model.e_birth_ev,1/model.e_birth_ev,
                            1/model.e_birth_ev,1/model.e_birth_ev))
            scaled=delta*norms
            threshold=atol*(b-a)/model.x_end + rtol*np.maximum(
                np.abs(q8*norms),np.abs(q4*norms))
            if np.all(scaled<=threshold):
                accepted+=1;deepest=max(deepest,depth)
                estimated=max(estimated,float(np.max(scaled)))
                return q8
            if depth>=max_depth:
                raise ArithmeticError("adaptive age quadrature exceeded depth budget")
            mid=(a+b)/2
            return recursive(a,mid,depth+1)+recursive(mid,b,depth+1)
        edges=age_event_boundaries(model,[float(mm)],scan=max(96,scan)) if event_panels \
              else (0.,model.x_end)
        for a,b in zip(edges[:-1],edges[1:]):
            total+=float(wm)*recursive(a,b,0)
    absorbed=tuple(float(x) for x in total[3:6])
    bind=fsum(a*c for a,c in zip(absorbed,BINDING_EV))
    result=Aggregate(float(total[0]),float(total[1]),float(total[2]),absorbed,
                    float(total[6]),bind,float(total[7]),float(total[8]),
                    float(total[9]),float(total[0]-total[2]-fsum(absorbed)),
                    float(total[1]-total[8]-bind-total[6]-total[7]),
                    ray_calls,events,steps,accepted)
    return AdaptiveAgeResult(result,estimated,accepted,deepest,(rtol,atol))


def terminal_angular_panels(model:Model,x_birth:float)->tuple[float,...]:
    """Exact terminal angular threshold cut preimages for this birth age.

    For T=(chi*exp(x_end-y)/Ebirth)^2, A=e^(2db), B=e^(-4db),
    mu_birth^2=(T-A)/(B-A). At isotropy the terminal active condition is
    independent of direction and no artificial cut is introduced.
    """
    if not 0<=x_birth<=model.x_end:raise ValueError("invalid birth epoch")
    db=model.b(model.x_end)-model.b(x_birth)
    aa=exp(2*db);bb=exp(-4*db)
    edges=[-1.,1.]
    if abs(bb-aa)<=2e-14*max(aa,bb):return tuple(edges)
    for k,chi in zip(model.kappa_th,CHI):
        if k<=0:continue
        tt=(chi*exp(model.x_end-x_birth)/model.e_birth_ev)**2
        z=(tt-aa)/(bb-aa)
        if 1e-14<z<1.-1e-14:
            mu=sqrt(z)
            edges.extend((-mu,mu))
    return tuple(sorted(set(round(x,14) if abs(x)!=1 else x for x in edges)))


def integrate_angular_event_source(model:Model,n_age:int,n_mu:int,n_time:int,
                                    *,scan:int=96)->Aggregate:
    """Positive joint birth-time and angular quadrature with terminal-cut panels.
    Fixed grid source ages; angle split is re-evaluated per age. This is a
    diagnostic comparator, not a rigorous continuum convergence guarantee.
    """
    ages,aw=_gl(0.,model.x_end,n_age)
    total=np.zeros(10)
    count=events=steps=panels=0
    for y,weight_y in zip(ages,aw):
        y=float(y)
        boundaries=terminal_angular_panels(model,y)
        n_pan=len(boundaries)-1
        panels+=n_pan
        alloc=max(2,round(n_mu/n_pan))
        for amin,amax in zip(boundaries[:-1],boundaries[1:]):
            mus,ww=_gl(amin,amax,alloc)
            for mu,wm in zip(mus,ww):
                weight=model.source(y)*float(weight_y)*float(wm)*.5
                r=integrate_ray(model,y,float(mu),n_time=n_time,scan=scan)
                total+=weight*np.array((1.,model.e_birth_ev,r.survivor,
                    *r.absorbed,r.heat_ev,r.work_ev,
                    r.survivor*r.final_energy_ev,r.final_pi_ev))
                count+=1;events+=r.event_count;steps+=r.substeps
    ab=tuple(float(v) for v in total[3:6]);bind=fsum(a*c for a,c in zip(ab,BINDING_EV))
    return Aggregate(float(total[0]),float(total[1]),float(total[2]),ab,float(total[6]),
                     bind,float(total[7]),float(total[8]),float(total[9]),
                     float(total[0]-total[2]-fsum(ab)),
                     float(total[1]-total[8]-bind-total[6]-total[7]),
                     count,events,steps,panels)
