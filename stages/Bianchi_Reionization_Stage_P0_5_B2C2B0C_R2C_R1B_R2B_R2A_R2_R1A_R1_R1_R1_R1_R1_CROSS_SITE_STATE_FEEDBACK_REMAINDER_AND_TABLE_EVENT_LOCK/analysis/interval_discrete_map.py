#!/usr/bin/env python3
"""Outward componentwise enclosure of one four-site MPRK22--SDIRK2 microstep.

The implementation follows the actual discrete stage equations.  H/He linear
systems are certified with local interval Krawczyk tests; thermal roots are
bracketed uniformly over the uncertain context and refined by interval signs.
It is intentionally conservative: failure is a certificate about this
representation, never a physical non-existence claim.
"""
from __future__ import annotations
from dataclasses import dataclass
import importlib.util, math, sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]

def _load(name,path):
    if name in sys.modules:return sys.modules[name]
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise ImportError(path)
    m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

VALID=next(REPO.glob('stages/*R2_R1A_R1_VALIDATED_CONTINUOUS*'))
PRIOR=next(REPO.glob('stages/*EVALUATION_SITE_SPARSE_GENERATOR_VALIDATED_MPRK22_SDIRK2*'))
R1A=next(REPO.glob('stages/*R2_R1A_FOUR_CORNER*'))
rim=_load('crosssite_reduced_interval_rhs',VALID/'analysis/reduced_interval_rhs.py')
iv=rim.iv
cert=_load('crosssite_implicit_certificates',PRIOR/'analysis/implicit_certificates.py')
trial=_load('crosssite_parent_trial_interval',R1A/'analysis/uncertainty_trial.py')
policy=_load('crosssite_parent_policy_interval',R1A/'analysis/uncertainty_policy.py')
primitive=_load('crosssite_primitives',HERE/'cross_site_discrete_map.py')
mprk=trial.fast.base.mprk;sdirk=trial.fast.sdirk

KB=1.380649e-16;EV=1.602176634e-12

@dataclass(frozen=True)
class PopulationBox:
    lower: np.ndarray
    upper: np.ndarray
    certified: bool
    maximum_row_sum: float

@dataclass(frozen=True)
class EventBox:
    flux: object
    resolved_heat: object
    unresolved_energy: object
    escaped_energy: object
    chemical_energy: object
    photo_heat: object
    photon_identity: object

@dataclass(frozen=True)
class RootBox:
    log_temperature: object
    rhs: object
    certified: bool
    derivative_lower: np.ndarray
    minimum_derivative: float
    iterations: int

@dataclass(frozen=True)
class DiscreteMapResult:
    classification: str
    certified: bool
    population_box: PopulationBox|None
    log_temperature_box: object|None
    public_widths: dict[str,float]
    table_event: dict[str,object]
    set_ledgers: dict[str,tuple[float,float]]
    diagnostics: dict[str,object]


@dataclass(frozen=True)
class StepResult:
    certified: bool
    classification: str
    population: object|None
    log_temperature: object|None
    stage_event: EventBox|None
    final_event: EventBox|None
    table_events: tuple[object,...]
    diagnostics: dict[str,object]


def _I(lo,hi=None):return iv.Interval(lo,hi)
def _zero(shape):return _I(np.zeros(shape))

def _source_v(temp:object)->object:
    lo=np.asarray(temp.lo);hi=np.asarray(temp.hi)
    if np.any(hi>1e5*(1+32*np.finfo(float).eps)):raise ValueError('ABOVE_TABLE')
    elo=np.minimum(lo,1e5);ehi=np.minimum(hi,1e5)
    vlo=np.asarray(policy.build_v_field_from_temperature('CELL_LOWER_STRICT',elo))
    vhi=np.asarray(policy.build_v_field_from_temperature('CELL_UPPER_STRICT',ehi))
    cross=(lo<1e4)&(hi>=1e4)
    vlo=np.where(cross,0.0,vlo);vhi=np.where(cross,1.0,vhi)
    return _I(np.maximum(0,np.nextafter(vlo,-np.inf)),np.minimum(1,np.nextafter(vhi,np.inf)))

def _add_flux(lo,hi,dest,source,rate):
    lo[:,dest,source]=np.nextafter(lo[:,dest,source]+rate.lo,-np.inf)
    hi[:,dest,source]=np.nextafter(hi[:,dest,source]+rate.hi,np.inf)

def event_box(model,pop:object,temp:object,time_s:float)->EventBox:
    """Source-safe interval event flux at one evaluation site."""
    pops=tuple(_I(pop.lo[:,i],pop.hi[:,i]) for i in range(5))
    nhi,nhii,nhei,nheii,nheiii=pops
    forcing=model.forcing_bounds(time_s,time_s);volume=forcing.volume_cm3
    T=temp;ne=(nhii+nheii+2*nheiii)/volume
    phi,phe,phe2,primary=model._explicit_photo_fields(pops,forcing)
    n_hi=nhi/volume;n_hei=nhei/volume;n_heii=nheii/volume
    y=(n_hi*rim.SIGMA_OTS_H24)/(n_hi*rim.SIGMA_OTS_H24+n_hei*rim.SIGMA_OTS_HEI24+1e-300)
    z=(n_hi*rim.SIGMA_OTS_H41)/(n_hi*rim.SIGMA_OTS_H41+n_hei*rim.SIGMA_OTS_HEI41+1e-300)
    oh=n_hi*rim.SIGMA_OTS_H54;oe=n_hei*rim.SIGMA_OTS_HEI54;oe2=n_heii*rim.SIGMA_OTS_HEII54
    total=oh+oe+oe2+1e-300;y2a=oe2/total;y2b=oe/total
    v=_source_v(temp);f=_I(np.full_like(temp.lo,0.1),np.full_like(temp.hi,1.0))
    AH,AHe=rim._multi_affine_branches(v,f,y,z)
    rhi=phi+nhi*ne*rim._beta_hi(T);rhei=phe+nhei*ne*rim._beta_hei(T);rheii=phe2+nheii*ne*rim._beta_heii(T)
    aa2=rim._alpha_a_heii(T);ab2=rim._alpha_b_heii(T);aa3=rim._alpha_a_heiii(T);ab3=rim._alpha_b_heiii(T)
    an2=iv.minimum(rim._alpha_heiii_n2(T),ab3);acas=iv.maximum(ab3-an2,0.0)
    rhb=nhii*ne*rim._alpha_b_hii(T);r2g=nheii*ne*iv.maximum(aa2-ab2,0.0);r2b=nheii*ne*ab2
    r3g=nheiii*ne*iv.maximum(aa3-ab3,0.0);r3n=nheiii*ne*an2;r3c=nheiii*ne*acas
    n=len(temp.lo);flo=np.zeros((n,5,5));fhi=np.zeros((n,5,5))
    for d,s,r in ((1,0,rhi),(3,2,rhei),(4,3,rheii),(0,1,rhb),(2,3,r2g),(1,0,r2g*y),(3,2,r2g*(1-y)),
                  (2,3,r2b),(1,0,r2b*rim.P_EXC),(3,4,r3g),(1,0,r3g*(1-y2a-y2b)),(3,2,r3g*y2b),(4,3,r3g*y2a),
                  (3,4,r3n),(1,0,r3n),(3,4,r3c),(1,0,r3c*AH),(3,2,r3c*AHe)):_add_flux(flo,fhi,d,s,r)
    heat_event=r3c*(1-v)*f*(z*(rim.HEII_LYA_EV-rim.CHI_H_EV)+(1-z)*(rim.HEII_LYA_EV-rim.CHI_HEI_EV))*rim.EV_ERG
    escaped=r3c*(1-v)*(1-f)*rim.HEII_LYA_EV*rim.EV_ERG
    chemical=(rhb*(-rim.CHI_H_EV)+r2g*(-rim.CHI_HEI_EV+y*rim.CHI_H_EV+(1-y)*rim.CHI_HEI_EV)
      +r2b*(-rim.CHI_HEI_EV+rim.P_EXC*rim.CHI_H_EV)
      +r3g*(-rim.CHI_HEII_EV+(1-y2a-y2b)*rim.CHI_H_EV+y2b*rim.CHI_HEI_EV+y2a*rim.CHI_HEII_EV)
      +r3n*(-rim.CHI_HEII_EV+rim.CHI_H_EV)
      +r3c*(-rim.CHI_HEII_EV+v*(((rim.ELL-rim.M_CAS)+rim.M_CAS*y)*rim.CHI_H_EV+rim.M_CAS*(1-y)*rim.CHI_HEI_EV)
             +(1-v)*f*(z*rim.CHI_H_EV+(1-z)*rim.CHI_HEI_EV)))*rim.EV_ERG
    unresolved=-chemical-heat_event-escaped
    photon_identity=AH+AHe+v*(2-rim.ELL)+(1-v)*(1-f)-(1+v)
    return EventBox(_I(flo,fhi),heat_event,unresolved,escaped,chemical,primary+heat_event,photon_identity)

def group_photon_residuals(model,pop:object,time_s:float):
    """Interval closure of canonical group absorption among atomic+subgrid owners."""
    forcing=model.forcing_bounds(time_s,time_s)
    pops=[_I(pop.lo[:,i],pop.hi[:,i]) for i in range(5)]
    nhi,nhei,nheii=pops[0],pops[2],pops[3]
    sum_nhi=iv.sum_interval(nhi);sum_nhei=iv.sum_interval(nhei);sum_nheii=iv.sum_interval(nheii)
    scale=rim.NH0_CM3*iv.pow_const(1+forcing.z,2)*rim.MPC_CM
    rows=[]
    for gi in range(4):
        chi=scale*(model.inputs.sigma_cm2[0,gi] if model.inputs.owner_support[1,gi] else 0.0)
        che=rim.YHE*scale*(model.inputs.sigma_cm2[1,gi] if model.inputs.owner_support[2,gi] else 0.0)
        che2=rim.YHE*scale*(model.inputs.sigma_cm2[2,gi] if model.inputs.owner_support[3,gi] else 0.0)
        rhi=chi*(sum_nhi/model.n_h_total);rhe=che*(sum_nhei/model.n_he_total);rhe2=che2*(sum_nheii/model.n_h_total)
        total=forcing.external_subgrid[gi]+rhi+rhe+rhe2
        current=forcing.current[gi]
        assigned=current*(forcing.external_subgrid[gi]+rhi+rhe+rhe2)/total
        rows.append(assigned-current)
    return tuple(rows)

def _constrain_invariants(lo,hi,total_h,total_he):
    lo=lo.copy();hi=hi.copy()
    # fixed-point bound propagation for sum constraints
    for _ in range(3):
        lo[:,0]=np.maximum(lo[:,0],np.nextafter(total_h-hi[:,1],-np.inf));hi[:,0]=np.minimum(hi[:,0],np.nextafter(total_h-lo[:,1],np.inf))
        lo[:,1]=np.maximum(lo[:,1],np.nextafter(total_h-hi[:,0],-np.inf));hi[:,1]=np.minimum(hi[:,1],np.nextafter(total_h-lo[:,0],np.inf))
        for j in range(2,5):
            others=[k for k in range(2,5) if k!=j]
            lo[:,j]=np.maximum(lo[:,j],np.nextafter(total_he-np.sum(hi[:,others],axis=1),-np.inf))
            hi[:,j]=np.minimum(hi[:,j],np.nextafter(total_he-np.sum(lo[:,others],axis=1),np.inf))
    if np.any(lo<=0)|np.any(lo>hi):raise FloatingPointError('POPULATION_CONE')
    return lo,hi

def _matrix_interval(flux:object,den:object,dt:float):
    n,s,_=flux.lo.shape
    lo=np.zeros((n,s,s));hi=np.zeros_like(lo)
    for d in range(s):
      for src in range(s):
        if d==src:continue
        rate=_I(flux.lo[:,d,src],flux.hi[:,d,src])/_I(den.lo[:,src],den.hi[:,src])
        lo[:,d,src]=np.nextafter(-dt*rate.hi,-np.inf);hi[:,d,src]=np.nextafter(-dt*rate.lo,np.inf)
    for src in range(s):
        outgoing=_zero((n,))
        for d in range(s):
            if d!=src:outgoing=outgoing+_I(flux.lo[:,d,src],flux.hi[:,d,src])
        rate=outgoing/_I(den.lo[:,src],den.hi[:,src])
        lo[:,src,src]=np.nextafter(1+dt*rate.lo,-np.inf);hi[:,src,src]=np.nextafter(1+dt*rate.hi,np.inf)
    return lo,hi

def population_step(parent:object,flux:object,den:object,dt:float,total_h,total_he)->PopulationBox:
    A_lo,A_hi=_matrix_interval(flux,den,dt);n=len(parent.lo);out_lo=np.empty_like(parent.lo);out_hi=np.empty_like(parent.hi);rows=[];allc=True
    for sl in (slice(0,2),slice(2,5)):
        c=cert.linear_interval_krawczyk(A_lo[:,sl,sl],A_hi[:,sl,sl],parent.lo[:,sl],parent.hi[:,sl])
        allc=allc and bool(np.all(c.certified));rows.append(float(np.max(c.row_sum_bound)))
        # Once K(X) is strictly contained in X, every solution lies in the
        # Krawczyk image itself.  Use that tighter image instead of the larger
        # construction tube; this matters for trace HeIII populations.
        out_lo[:,sl]=np.nextafter(c.center-c.krawczyk_radius,-np.inf);out_hi[:,sl]=np.nextafter(c.center+c.krawczyk_radius,np.inf)
    out_lo,out_hi=_constrain_invariants(out_lo,out_hi,total_h,total_he)
    return PopulationBox(out_lo,out_hi,allc,max(rows))

def average_flux(a:object,b:object):return _I(np.nextafter(0.5*(a.lo+b.lo),-np.inf),np.nextafter(0.5*(a.hi+b.hi),np.inf))

@dataclass(frozen=True)
class ThermalIntervalContext:
    photoheat: object; expansion: object; ecoef: object
    factors: tuple[object,...]

def thermal_context(pop:object,volume:object,photoheat:object,hubble:object)->ThermalIntervalContext:
    p=[_I(pop.lo[:,i],pop.hi[:,i]) for i in range(5)];nhi,nhii,nhei,nheii,nheiii=p
    ne=(nhii+nheii+2*nheiii)/volume;particles=nhi+nhii+nhei+nheii+nheiii+nhii+nheii+2*nheiii
    factors=(ne*nhii,ne*nheii,ne*nheiii,ne*nhi,ne*nheii,ne*nhi*13.598*EV,ne*nhei*24.587*EV,ne*nheii*54.416*EV,ne*(nhii+nheii+4*nheiii))
    return ThermalIntervalContext(photoheat,3*hubble*KB*particles,1.5*KB*particles,factors)

def thermal_rhs(ctx:ThermalIntervalContext,x:object):
    T=iv.exp(x);lh=315614/T;le=570670/T;le2=1263030/T
    rec_h=3.435e-30*T*iv.pow_const(lh,1.970)/iv.pow_const(1+iv.pow_const(lh/2.250,0.376),3.720)
    rec_e=KB*T*(1.26e-14*iv.pow_const(le,0.750))
    rec_e3=8*3.435e-30*T*iv.pow_const(le2,1.970)/iv.pow_const(1+iv.pow_const(le2/2.250,0.376),3.720)
    sq=iv.sqrt(T/1e5);exc_h=7.5e-19*iv.exp(-118348/T)/(1+sq);exc_e=5.54e-17*iv.pow_const(T,-0.397)*iv.exp(-473638/T)/(1+sq)
    bh=5.835e-11*iv.sqrt(T)*iv.exp(-157804/T);be=2.71e-11*iv.sqrt(T)*iv.exp(-285331/T);be2=5.707e-12*iv.sqrt(T)*iv.exp(-631495/T)
    q=5.5-iv.log(T)/math.log(10);ff=1.42e-27*iv.sqrt(T)*(1.1+0.34*iv.exp(-iv.pow_const(q,2)/3))
    terms=(rec_h,rec_e,rec_e3,exc_h,exc_e,bh,be,be2,ff);cool=_zero(T.lo.shape)
    for fac,term in zip(ctx.factors,terms):cool=cool+fac*term
    return ctx.photoheat-cool-ctx.expansion*T


def thermal_rhs_derivative(ctx:ThermalIntervalContext,x:object):
    """Outward interval of d(thermal RHS)/d log(T)."""
    T=iv.exp(x);lh=315614/T;le=570670/T;le2=1263030/T
    xr=iv.pow_const(lh/2.250,0.376);rec_h=3.435e-30*T*iv.pow_const(lh,1.970)/iv.pow_const(1+xr,3.720)
    sr=-0.970+(3.720*0.376)*xr/(1+xr)
    rec_e=KB*T*(1.26e-14*iv.pow_const(le,0.750));se=_I(np.full_like(T.lo,0.250))
    xr3=iv.pow_const(le2/2.250,0.376);rec_e3=8*3.435e-30*T*iv.pow_const(le2,1.970)/iv.pow_const(1+xr3,3.720)
    sr3=-0.970+(3.720*0.376)*xr3/(1+xr3)
    sq=iv.sqrt(T/1e5);exc_h=7.5e-19*iv.exp(-118348/T)/(1+sq);sh=118348/T-0.5*sq/(1+sq)
    exc_e=5.54e-17*iv.pow_const(T,-0.397)*iv.exp(-473638/T)/(1+sq);she=-0.397+473638/T-0.5*sq/(1+sq)
    bh=5.835e-11*iv.sqrt(T)*iv.exp(-157804/T);sbh=0.5+157804/T
    be=2.71e-11*iv.sqrt(T)*iv.exp(-285331/T);sbe=0.5+285331/T
    be2=5.707e-12*iv.sqrt(T)*iv.exp(-631495/T);sbe2=0.5+631495/T
    q=5.5-iv.log(T)/math.log(10);gauss=iv.exp(-iv.pow_const(q,2)/3);gaunt=1.1+0.34*gauss
    ff=1.42e-27*iv.sqrt(T)*gaunt;sff=0.5+(0.34*gauss/gaunt)*(2*q/(3*math.log(10)))
    terms=(rec_h,rec_e,rec_e3,exc_h,exc_e,bh,be,be2,ff);slopes=(sr,se,sr3,sh,she,sbh,sbe,sbe2,sff)
    dcool=_zero(T.lo.shape)
    for fac,term,slope in zip(ctx.factors,terms,slopes):dcool=dcool+fac*term*slope
    return -dcool-ctx.expansion*T


def thermal_root_derivative(ctx:ThermalIntervalContext,x:object,weighted_step:float):
    T=iv.exp(x)
    return ctx.ecoef*T-float(weighted_step)*thermal_rhs_derivative(ctx,x)

def thermal_root(ctx:ThermalIntervalContext,U0,step,constant,weight,seed_lo,seed_hi,max_iter=10)->RootBox:
    """Uniform parametric root enclosure by sign bracket + interval Newton.

    The endpoint sign test proves one root for every admissible parameter when
    the derivative is strictly positive.  Interval Newton then contracts that
    already-valid bracket without losing any parameter realization.
    """
    U=U0 if hasattr(U0,'lo') else _I(U0);w=float(weight);dt=float(step);const=constant if hasattr(constant,'lo') else _I(constant)
    def F(x):
        T=iv.exp(x);return ctx.ecoef*T-U-dt*(const+w*thermal_rhs(ctx,x))
    lo=np.nextafter(np.asarray(seed_lo,dtype=float)-1e-8,-np.inf)
    hi=np.nextafter(np.asarray(seed_hi,dtype=float)+1e-8,np.inf)
    for _ in range(20):
        fl=F(_I(lo));fh=F(_I(hi));need_lo=fl.hi>0;need_hi=fh.lo<0
        if not(np.any(need_lo)|np.any(need_hi)):break
        span=np.maximum(hi-lo,1e-5)
        lo=np.where(need_lo,lo-1.25*span,lo);hi=np.where(need_hi,hi+1.25*span,hi)
    fl=F(_I(lo));fh=F(_I(hi));bracket=(fl.hi<=0)&(fh.lo>=0)
    iterations=0
    for iterations in range(1,max_iter+1):
        X=_I(lo,hi);D=thermal_root_derivative(ctx,X,dt*w)
        if np.any(D.lo<=0.0):break
        mid=0.5*(lo+hi);Fm=F(_I(mid));N=_I(mid)-Fm/D
        nlo=np.maximum(lo,N.lo);nhi=np.minimum(hi,N.hi)
        valid=nlo<=nhi
        if not np.all(valid):break
        improvement=float(np.max((hi-lo)-(nhi-nlo)))
        lo=np.nextafter(nlo,-np.inf);hi=np.nextafter(nhi,np.inf)
        if improvement<=1e-14:break
    box=_I(lo,hi);D=thermal_root_derivative(ctx,box,dt*w);rhs=thermal_rhs(ctx,box)
    certed=bracket&(D.lo>0.0)
    return RootBox(box,rhs,bool(np.all(certed)),D.lo,float(np.min(D.lo)),iterations)

def _state_box(pop:PopulationBox,temp:object):return _I(pop.lower,pop.upper),temp

def _point_pop(y):return _I(y,y)

def energy_box(pop:object,temp:object):
    p=[_I(pop.lo[:,i],pop.hi[:,i]) for i in range(5)]
    particles=p[0]+p[1]+p[2]+p[3]+p[4]+p[1]+p[3]+2*p[4]
    return 1.5*KB*particles*temp

def _subset(inner,outer,tol=0.0):
    return bool(np.all(inner.lo>=outer.lo-tol)&np.all(inner.hi<=outer.hi+tol))

def _hull(a,b):return _I(np.minimum(a.lo,b.lo),np.maximum(a.hi,b.hi))

def run_step(model,base,*,parent_pop:object,parent_logt:object,t0:float,t1:float,total_h,total_he)->StepResult:
    dt=float(t1-t0);tg=t0+sdirk.GAMMA*dt
    parent_temp=iv.exp(parent_logt);parent_energy=energy_box(parent_pop,parent_temp)
    e0=event_box(model,parent_pop,parent_temp,t0)
    pred=population_step(parent_pop,e0.flux,parent_pop,dt,total_h,total_he)
    gamma=population_step(parent_pop,e0.flux,parent_pop,sdirk.GAMMA*dt,total_h,total_he)
    if not(pred.certified and gamma.certified):return StepResult(False,'LOCAL_POPULATION_CERTIFICATE_FAILURE',None,None,None,None,(),{'pred_row':pred.maximum_row_sum,'gamma_row':gamma.maximum_row_sum})
    fp0=model.forcing_bounds(t0,t0)
    ctxp=thermal_context(_I(pred.lower,pred.upper),fp0.volume_cm3,e0.photo_heat,fp0.hubble_s_inv)
    pr=thermal_root(ctxp,parent_energy,dt,np.zeros_like(parent_logt.lo),1.0,parent_logt.lo-0.02,parent_logt.hi+0.02)
    if not pr.certified:return StepResult(False,'PREDICTOR_THERMAL_ROOT_FAILURE',None,pr.log_temperature,None,None,(primitive.detect_table_events(pr.log_temperature.lo,pr.log_temperature.hi),),{'min_derivative':pr.minimum_derivative})
    pred_temp=iv.exp(pr.log_temperature);e1=event_box(model,_I(pred.lower,pred.upper),pred_temp,t1)
    corr=population_step(parent_pop,average_flux(e0.flux,e1.flux),_I(pred.lower,pred.upper),dt,total_h,total_he)
    if not corr.certified:return StepResult(False,'CORRECTOR_POPULATION_CERTIFICATE_FAILURE',None,None,None,None,(),{'row':corr.maximum_row_sum})
    xs=_I(parent_logt.lo-0.02,parent_logt.hi+0.02);xf=_I(parent_logt.lo-0.02,parent_logt.hi+0.02)
    stage_root=final_root=None;eg=ef=None;self_inclusion=False
    for outer in range(8):
        eg=event_box(model,_I(gamma.lower,gamma.upper),iv.exp(xs),tg);fg=model.forcing_bounds(tg,tg)
        csg=thermal_context(_I(gamma.lower,gamma.upper),fg.volume_cm3,eg.photo_heat,fg.hubble_s_inv)
        stage_root=thermal_root(csg,parent_energy,sdirk.GAMMA*dt,np.zeros_like(parent_logt.lo),1.0,xs.lo,xs.hi)
        if not stage_root.certified:return StepResult(False,'THERMAL_STAGE_ROOT_FAILURE',None,stage_root.log_temperature,eg,None,(primitive.detect_table_events(stage_root.log_temperature.lo,stage_root.log_temperature.hi),),{'outer':outer,'min_derivative':stage_root.minimum_derivative})
        ef=event_box(model,_I(corr.lower,corr.upper),iv.exp(xf),t1);ff=model.forcing_bounds(t1,t1)
        csf=thermal_context(_I(corr.lower,corr.upper),ff.volume_cm3,ef.photo_heat,ff.hubble_s_inv)
        final_root=thermal_root(csf,parent_energy,dt,(1-sdirk.GAMMA)*stage_root.rhs,sdirk.GAMMA,xf.lo,xf.hi)
        if not final_root.certified:return StepResult(False,'THERMAL_FINAL_ROOT_FAILURE',None,final_root.log_temperature,eg,ef,(primitive.detect_table_events(final_root.log_temperature.lo,final_root.log_temperature.hi),),{'outer':outer,'min_derivative':final_root.minimum_derivative})
        nxs=stage_root.log_temperature;nxf=final_root.log_temperature
        if _subset(nxs,xs) and _subset(nxf,xf):
            xs,xf=nxs,nxf;self_inclusion=True;break
        xs=_hull(xs,nxs);xf=_hull(xf,nxf)
    if not self_inclusion:
        return StepResult(False,'THERMAL_OUTER_TUBE_NOT_SELF_INCLUDED',None,xf,eg,ef,(),{'outer_iterations':outer+1})
    events=(
        primitive.detect_table_events(pr.log_temperature.lo,pr.log_temperature.hi),
        primitive.detect_table_events(xs.lo,xs.hi),
        primitive.detect_table_events(xf.lo,xf.hi),
        primitive.detect_path_table_events(
            primitive.IntervalVector(parent_logt.lo,parent_logt.hi),
            primitive.IntervalVector(pr.log_temperature.lo,pr.log_temperature.hi),
            primitive.IntervalVector(xs.lo,xs.hi),
            primitive.IntervalVector(xf.lo,xf.hi),
        ),
    )
    if any(x.any_event for x in events):return StepResult(False,'TABLE_EVENT_REQUIRES_RESTART',_I(corr.lower,corr.upper),xf,eg,ef,events,{'outer_iterations':outer+1})
    return StepResult(True,'PASS',_I(corr.lower,corr.upper),xf,eg,ef,events,
      {'predictor_row_sum':pred.maximum_row_sum,'gamma_row_sum':gamma.maximum_row_sum,'corrector_row_sum':corr.maximum_row_sum,'outer_iterations':outer+1,'predictor_root_min_derivative':pr.minimum_derivative,'stage_root_min_derivative':stage_root.minimum_derivative,'final_root_min_derivative':final_root.minimum_derivative})

def run_lane(repo_root:Path,*,lane:str,partition:int=2048)->DiscreteMapResult:
    repo=Path(repo_root).resolve();model=rim.ReducedIntervalModel.from_repo(repo)
    base=trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=lane)
    parent=base.inputs.state0.mutable_copy();y0=np.asarray(parent.values[:5].T);duration=base.forcing.duration_seconds(0);t1=duration/partition;mid=0.5*t1
    total_h=y0[:,0]+y0[:,1];total_he=np.sum(y0[:,2:5],axis=1)
    full=run_step(model,base,parent_pop=_point_pop(y0),parent_logt=_I(np.log(parent.temperature_K)),t0=0.0,t1=t1,total_h=total_h,total_he=total_he)
    if not full.certified:return DiscreteMapResult(full.classification,False,None,full.log_temperature,{}, {'events':[vars(x) for x in full.table_events]}, {}, {'full_step':full.diagnostics})
    first=run_step(model,base,parent_pop=_point_pop(y0),parent_logt=_I(np.log(parent.temperature_K)),t0=0.0,t1=mid,total_h=total_h,total_he=total_he)
    if not first.certified:return DiscreteMapResult(first.classification,False,None,first.log_temperature,{}, {'events':[vars(x) for x in first.table_events]}, {}, {'full_step':full.diagnostics,'first_half':first.diagnostics})
    second=run_step(model,base,parent_pop=first.population,parent_logt=first.log_temperature,t0=mid,t1=t1,total_h=total_h,total_he=total_he)
    if not second.certified:return DiscreteMapResult(second.classification,False,None,second.log_temperature,{}, {'events':[vars(x) for x in second.table_events]}, {}, {'first_half':first.diagnostics,'second_half':second.diagnostics})
    pop=second.population;xf=second.log_temperature
    xhii=_I(pop.lo[:,1]/total_h,pop.hi[:,1]/total_h);xheii=_I(pop.lo[:,3]/total_he,pop.hi[:,3]/total_he);xheiii=_I(pop.lo[:,4]/total_he,pop.hi[:,4]/total_he)
    widths={'x_HII':float(np.max(xhii.hi-xhii.lo)),'x_HeII':float(np.max(xheii.hi-xheii.lo)),'x_HeIII':float(np.max(xheiii.hi-xheiii.lo)),'log_T':float(np.max(xf.hi-xf.lo))}
    full_pop=full.population;full_logt=full.log_temperature
    full_coords={
      'x_HII':_I(full_pop.lo[:,1]/total_h,full_pop.hi[:,1]/total_h),
      'x_HeII':_I(full_pop.lo[:,3]/total_he,full_pop.hi[:,3]/total_he),
      'x_HeIII':_I(full_pop.lo[:,4]/total_he,full_pop.hi[:,4]/total_he),
      'log_T':full_logt,
    }
    half_coords={'x_HII':xhii,'x_HeII':xheii,'x_HeIII':xheiii,'log_T':xf}
    local_error_bounds={}
    for key in ('x_HII','x_HeII','x_HeIII','log_T'):
        a=full_coords[key];b=half_coords[key]
        local_error_bounds[key]=float(np.max(np.maximum(np.abs(b.lo-a.hi),np.abs(b.hi-a.lo))))
    maximum_local_error=max(local_error_bounds.values())
    # Integrate endpoint source identities as set inclusions. Exact population invariants are additionally enforced in each local solve.
    ledgers={
      'H_nuclei':(float(np.min((pop.lo[:,0]+pop.lo[:,1])-total_h)),float(np.max((pop.hi[:,0]+pop.hi[:,1])-total_h))),
      'He_nuclei':(float(np.min(np.sum(pop.lo[:,2:5],axis=1)-total_he)),float(np.max(np.sum(pop.hi[:,2:5],axis=1)-total_he))),
    }
    for prefix,ev,pbox,ts in (('stage',second.stage_event,second.population,mid+sdirk.GAMMA*(t1-mid)),('final',second.final_event,second.population,t1)):
        ledgers[prefix+'_photon_identity']=(float(np.min(ev.photon_identity.lo)),float(np.max(ev.photon_identity.hi)))
        total=ev.resolved_heat+ev.unresolved_energy+ev.escaped_energy+ev.chemical_energy
        ledgers[prefix+'_total_energy']=(float(np.min(total.lo)),float(np.max(total.hi)))
        for gi,res in enumerate(group_photon_residuals(model,pbox,ts)):
            ledgers[f'{prefix}_group_{gi}_photon']=(float(np.asarray(res.lo)),float(np.asarray(res.hi)))
    la=primitive.audit_set_ledgers(ledgers)
    if not la.all_include_zero:classification='SET_LEDGER_EXCLUDES_ZERO'
    elif max(widths.values())>=0.002:classification='PUBLIC_WIDTH_GATE_FAILURE'
    elif maximum_local_error>=2.0e-4:classification='VALIDATED_LOCAL_ERROR_GATE_FAILURE'
    else:classification='PASS'
    all_events=full.table_events+first.table_events+second.table_events
    return DiscreteMapResult(classification,classification=='PASS',PopulationBox(pop.lo,pop.hi,True,max(first.diagnostics['corrector_row_sum'],second.diagnostics['corrector_row_sum'])),xf,widths,
      {'any_event':any(e.any_event for e in all_events),'node_count':sum(len(e.node_indices) for e in all_events),'minimum_distance':min(e.minimum_distance for e in all_events)},ledgers,
      {'full_step':full.diagnostics,'first_half':first.diagnostics,'second_half':second.diagnostics,'failed_ledgers':la.failed,
       'validated_local_error_bounds':local_error_bounds,'maximum_validated_local_error':maximum_local_error,'map_enclosed':True})

__all__=['PopulationBox','EventBox','RootBox','DiscreteMapResult','event_box','population_step','thermal_root','run_lane']
