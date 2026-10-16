"""Independent time-variable positive photon reference for REI PR166 diagnosis.

Prescribed smooth j(x), piecewise kappa_i(x), no native gas feedback.  One
analytic optical-depth primitive defines an independent Duhamel reference;
positive frozen exact substeps provide event-aligned and adaptive approximations.
These inputs are *manufactured*, not original MD14/Grackle cross sections.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, fsum, isfinite
from typing import Sequence
from scipy.integrate import quad
from positive_reference import frozen_slab, phi1_negative


@dataclass(frozen=True)
class ManufacturedCase:
    event_x: float = 0.73
    energy_ev: float = 80.0
    old: float = 0.002
    source_level: float = 1.0
    source_growth: float = 0.3
    hi_base: float = 95.0
    hi_growth: float = 35.0
    hei_base: float = 35.0
    hei_growth: float = 25.0
    heii_on: float = 85.0

    def __post_init__(self):
        if not (0 < self.event_x < 1) or self.energy_ev < 54.42:
            raise ValueError('well-ordered artificial HeII event, E>=fit threshold')
        if not all(isfinite(v) and v >= 0 for v in (
            self.old,self.source_level,self.source_growth,self.hi_base,
            self.hi_growth,self.hei_base,self.hei_growth,self.heii_on)):
            raise ValueError('positive finite manufactured parameters required')

    def source(self, x: float) -> float:
        return self.source_level * (1 + self.source_growth * x)

    def rates(self, x: float) -> tuple[float, float, float]:
        return (self.hi_base + self.hi_growth*x,
                self.hei_base + self.hei_growth*x,
                self.heii_on if x >= self.event_x else 0.0)

    def depth(self, x: float) -> float:
        """Exact primitive of summed hazards from x=0 (right/left continuous event)."""
        return ((self.hi_base+self.hei_base)*x
                + 0.5*(self.hi_growth+self.hei_growth)*x*x
                + self.heii_on * max(0.0, x-self.event_x))


def _integrate(f,a,b,event,epsabs=2e-14):
    if b<=a: return 0.0
    pts=[event] if a<event<b else None
    value,err=quad(f,a,b,points=pts,epsabs=epsabs,epsrel=2e-12,limit=180)
    return value


def duhamel_survivor(case: ManufacturedCase, x: float) -> float:
    """Analytic-hazard positive mild IVP reference, no numerical time stepping."""
    if not (isfinite(x) and 0<=x<=1): raise ValueError('0<=x<=1 required')
    hx=case.depth(x)
    fun=lambda y: case.source(y)*exp(-(hx-case.depth(y)))
    return case.old*exp(-hx)+_integrate(fun,0,x,case.event_x)


def independent_reference(case: ManufacturedCase) -> dict:
    """Nested QUAD species integrals, independent from frozen-slab time stepping."""
    n=duhamel_survivor(case,1)
    born=case.source_level*(1+case.source_growth/2)
    absorptions=[]
    for i in range(3):
        v=_integrate(lambda x: case.rates(x)[i]*duhamel_survivor(case,x),
                     0,1,case.event_x)
        absorptions.append(v)
    # Reference defines binding using native physical thresholds, NOT Verner fits.
    bind=(13.598434599702,24.587389011,54.41776)
    b=fsum(a*e for a,e in zip(absorptions,bind))
    q=fsum(a*(case.energy_ev-e) for a,e in zip(absorptions,bind))
    return dict(survived=n,emitted=born,initial=case.old,absorbed=absorptions,
                heat_ev=q,binding_ev=b,
                photon_residual=case.old+born-n-fsum(absorptions),
                energy_residual_ev=case.energy_ev*(case.old+born-n)-q-b)


def finite_slab_history(case:ManufacturedCase,n:int,split:bool=True) -> dict:
    """Piecewise frozen exponential source map, event aligned when split=True."""
    if not isinstance(n,int) or n<1:raise ValueError('positive integer panels')
    e=[0.,case.event_x,1.] if split else [0.,1.]
    state=case.old
    born=0.
    absorb=[0.,0.,0.]; heat=0.; binding=0.
    for a,b in zip(e[:-1],e[1:]):
        for k in range(n):
            l=a+(b-a)*k/n
            r=a+(b-a)*(k+1)/n
            m=(l+r)/2
            src=case.source(m)*(r-l)
            s=frozen_slab(state,src,case.rates(m),r-l,case.energy_ev)
            state=s.survived
            born+=src
            for j in range(3):absorb[j]+=s.absorbed[j]
            heat+=s.photoheat_ev; binding+=s.binding_ev
    return dict(survived=state,emitted=born,initial=case.old,
                absorbed=absorb,heat_ev=heat,binding_ev=binding,
                photon_residual=case.old+born-state-fsum(absorb),
                energy_residual_ev=case.energy_ev*(case.old+born-state)-heat-binding,
                panels=n*len(e[:-1]))


def midpoint_impulse_hazard_reference(case:ManufacturedCase,n:int) -> float:
    """Birth-time midpoint with exact analytic future optical-depth (source only)."""
    if not isinstance(n,int) or n<1:raise ValueError('n>=1')
    tot=case.old*exp(-case.depth(1))
    for i in range(n):
        mid=(i+.5)/n
        tot+=case.source(mid)/n*exp(-(case.depth(1)-case.depth(mid)))
    return tot


def adaptive_positive(case:ManufacturedCase,rtol:float=1e-7,max_leaf:int=20000) -> dict:
    """Binary subdivision with local two-half error in survivor AND all species.

    Uses the finer two halves for an accepted step, never a negative RK trial.
    A bounded leaf/attempt budget refuses to hide underresolution.
    """
    if not (isfinite(rtol) and 0<rtol<1) or max_leaf<2:
        raise ValueError('positive tolerance and budget required')
    current=case.old
    totals=[0.,0.,0.]; em=0.;heat=0.;binding=0.;accepted=0;rejected=0
    # Two temporal panels separated by the exact HeII event.  Critically,
    # the right panel begins with the ACCEPTED survivor from the left panel.
    for left,right in ((0.,case.event_x),(case.event_x,1.)):
        result=_adaptive_segment(case,left,right,current,rtol,max_leaf-accepted-rejected)
        current=result['end'];em+=result['source']
        heat+=result['heat'];binding+=result['binding']
        for k in range(3): totals[k]+=result['absorbed'][k]
        accepted+=result['accepted'];rejected+=result['rejected']
        if accepted+rejected>max_leaf:raise RuntimeError('exhausted adaptive budget')
    return dict(survived=current,initial=case.old,emitted=em,absorbed=totals,
                binding_ev=binding,heat_ev=heat,accepted_halfsteps=accepted,
                rejected=rejected,
                photon_residual=case.old+em-current-fsum(totals),
                energy_residual_ev=case.energy_ev*(case.old+em-current)-binding-heat)


def _adaptive_segment(case,a,b,previous,rtol,budget):
    m=(a+b)/2; leftx=(a+m)/2;rightx=(m+b)/2
    whole=frozen_slab(previous,case.source(m)*(b-a),case.rates(m),b-a,case.energy_ev)
    p=frozen_slab(previous,case.source(leftx)*(m-a),case.rates(leftx),m-a,case.energy_ev)
    q=frozen_slab(p.survived,case.source(rightx)*(b-m),case.rates(rightx),b-m,case.energy_ev)
    err=max([abs(whole.survived-q.survived)]+[
        abs(whole.absorbed[k]-p.absorbed[k]-q.absorbed[k]) for k in range(3)])
    scale=max(previous+case.source_level*(b-a),1e-8)
    if err<=rtol*scale:
        return dict(end=q.survived,source=case.source(leftx)*(m-a)+case.source(rightx)*(b-m),
                    absorbed=[p.absorbed[k]+q.absorbed[k] for k in range(3)],
                    heat=p.photoheat_ev+q.photoheat_ev,binding=p.binding_ev+q.binding_ev,
                    accepted=2,rejected=0)
    if budget<=2 or abs(b-a)<1e-14: raise RuntimeError('exhausted adaptive budget')
    t=_adaptive_segment(case,a,m,previous,rtol,budget-1)
    u=_adaptive_segment(case,m,b,t['end'],rtol,budget-t['accepted']-t['rejected']-1)
    return dict(end=u['end'],source=t['source']+u['source'],
                absorbed=[t['absorbed'][k]+u['absorbed'][k] for k in range(3)],
                heat=t['heat']+u['heat'],binding=t['binding']+u['binding'],
                accepted=t['accepted']+u['accepted'],rejected=t['rejected']+u['rejected']+1)