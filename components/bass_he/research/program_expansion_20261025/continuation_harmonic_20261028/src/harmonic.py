"""Certified second-harmonic declared measures on inherited paired geometry.

Production certificates use exact fractions, finite rational series, and inherited
polar enclosures. Stored masses and manufactured laws retain their declared scope.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import comb, factorial
from pathlib import Path
import importlib.util
import sys

_PARENT=Path(__file__).resolve().parents[2]/'continuation_azimuth_20261028/src/azimuth.py'
_SPEC=importlib.util.spec_from_file_location('_harmonic10_inherited_azimuth',_PARENT)
_Z=importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name]=_Z
_SPEC.loader.exec_module(_Z)
ContractError=_Z.ContractError
PhysicalAngularMap=_Z.PhysicalAngularMap
DetectorPatch=_Z.DetectorPatch
FiniteDetector=_Z.FiniteDetector
BernsteinDensity=_Z.BernsteinDensity
SetBounds=_Z.SetBounds
MeasureBounds=_Z.MeasureBounds
conditional_ratio=_Z.conditional_ratio
EVENTS,PARTS=_Z.EVENTS,_Z.PARTS
rational=_Z.rational
ZERO,ONE=F(0),F(1)


def floor_grid(x,bits):return F((x*2**bits).__floor__(),2**bits)
def ceil_grid(x,bits):return -floor_grid(-x,bits)

@dataclass(frozen=True)
class Interval:
    lower:F
    upper:F
    def __post_init__(self):
        object.__setattr__(self,'lower',rational(self.lower))
        object.__setattr__(self,'upper',rational(self.upper))
        if self.lower>self.upper:raise ContractError('reversed interval')
    @property
    def width(self):return self.upper-self.lower
    @staticmethod
    def point(x):return Interval(x,x)
    def __add__(self,other):
        other=other if isinstance(other,Interval) else Interval.point(other)
        return Interval(self.lower+other.lower,self.upper+other.upper)
    __radd__=__add__
    def __neg__(self):return Interval(-self.upper,-self.lower)
    def __sub__(self,other):return self+-other if isinstance(other,Interval) else self+(-other)
    def __mul__(self,other):
        other=other if isinstance(other,Interval) else Interval.point(other)
        v=[x*y for x in (self.lower,self.upper) for y in (other.lower,other.upper)]
        return Interval(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,other):
        other=other if isinstance(other,Interval) else Interval.point(other)
        if other.lower<=0<=other.upper:raise ContractError('interval denominator contains zero')
        return self*Interval(1/other.upper,1/other.lower)


def _atan_enclosure(inv,N):
    x=F(1,inv)
    partial=sum(((-1)**k*x**(2*k+1)/ (2*k+1) for k in range(N)),ZERO)
    following=partial+(-1)**N*x**(2*N+1)/(2*N+1)
    return Interval(min(partial,following),max(partial,following))

@lru_cache(maxsize=1)
def pi_interval():
    p=16*_atan_enclosure(5,24)-4*_atan_enclosure(239,8)
    p=Interval(floor_grid(p.lower,96),ceil_grid(p.upper,96))
    if not (p.lower>3 and p.width<F(1,2**94)):raise ContractError('pi width contract')
    return p

def sincos_turn(t):
    """Enclose sin(4 pi t), cos(4 pi t); exact rational phase cache keys."""
    t=rational(t,'phase')%1
    return _sincos_turn(t)

@lru_cache(maxsize=4096)
def _sincos_turn(t):
    u=(2*t)%1
    q=(4*u).__floor__()
    r=u-F(q,4)
    if r==0:
        return tuple(Interval.point(x) for x in ((0,1),(1,0),(0,-1),(-1,0))[q])
    x=pi_interval()*(2*r)
    w=floor_grid((x.lower+x.upper)/2,96)
    argument_error=max(abs(w-x.lower),abs(x.upper-w))
    if not (0<=w<2 and argument_error<F(1,2**94)):raise ContractError('phase argument contract')
    sn=sum(((-1)**k*w**(2*k+1)/factorial(2*k+1) for k in range(20)),ZERO)
    cs=sum(((-1)**k*w**(2*k)/factorial(2*k) for k in range(20)),ZERO)
    def enclose(value,remainder):
        err=remainder+argument_error
        a=Interval(max(-ONE,floor_grid(value-err,88)),min(ONE,ceil_grid(value+err,88)))
        if a.width>=F(1,2**86):raise ContractError('trigonometric width contract')
        return a
    s=enclose(sn,F(2**41,factorial(41)))
    c=enclose(cs,F(2**40,factorial(40)))
    return ((s,c),(c,-s),(-s,-c),(-c,s))[q]

@lru_cache(maxsize=4096)
def harmonic_integrals(lo,hi):
    lo,hi=rational(lo),rational(hi)
    if not 0<=lo<=hi<=1:raise ContractError('strip outside circle')
    if (2*(hi-lo))%1==0:return Interval.point(ZERO),Interval.point(ZERO)
    sl,cl=sincos_turn(lo);sh,ch=sincos_turn(hi)
    c=(sh-sl)/(4*pi_interval())
    s=(cl-ch)/(4*pi_interval())
    if c.width>F(1,2**84) or s.width>F(1,2**84):raise ContractError('strip arithmetic width contract')
    return c,s


def _power(coefficients):
    n=len(coefficients)-1
    power=[ZERO]*(n+1)
    for k,c in enumerate(coefficients):
        factor=c*comb(n,k)/2**n
        for i in range(k+1):
            for j in range(n-k+1):power[i+j]+=factor*comb(k,i)*comb(n-k,j)*(-1)**j
    return tuple(power)

class SecondHarmonicDensity:
    def __init__(self,b0,bc,bs):
        def coefficients(values):
            if isinstance(values,(str,bytes)):raise ContractError('coefficient sequence required')
            try:return tuple(rational(x,'harmonic coefficient') for x in values)
            except TypeError as exc:raise ContractError('coefficient sequence required') from exc
        self.b0,self.bc,self.bs=map(coefficients,(b0,bc,bs))
        if not 1<=len(self.b0)<=9 or len(self.bc)!=len(self.b0) or len(self.bs)!=len(self.b0):
            raise ContractError('equal coefficient lengths, degree at most 8 required')
        if any(v!=v[::-1] for v in (self.b0,self.bc,self.bs)):raise ContractError('reflection-even coefficients required')
        if any(a<0 or a*a<c*c+s*s for a,c,s in zip(self.b0,self.bc,self.bs)):
            raise ContractError('coefficient cone certificate required')
        self.degree=len(self.b0)-1
        self.sigma=2*sum(self.b0,ZERO)/(self.degree+1)
        self.B0=max(self.b0)
        self.uniform=not any(self.bc+self.bs)
        self.maximum=self.B0 if self.uniform else 2*self.B0
        self.power=tuple(_power(v) for v in (self.b0,self.bc,self.bs))
        self.polar=BernsteinDensity(self.b0)
    def integrals(self,intervals):
        def primitive(power,x):
            v=ZERO
            for k in reversed(range(len(power))):v=v*x+power[k]/(k+1)
            return v*x
        return tuple(sum((primitive(power,h)-primitive(power,l) for l,h in intervals),ZERO) for power in self.power)
    def value_components(self,mu):
        mu=_Z._API.cosine(mu)
        def evaluate(power):
            v=ZERO
            for c in reversed(power):v=v*mu+c
            return v
        return tuple(evaluate(p) for p in self.power)


def harmonic_pair_response(model,density,detA,detB,*,azimuth_law,delta=None):
    if not isinstance(model,PhysicalAngularMap) or not isinstance(density,SecondHarmonicDensity):
        raise ContractError('PhysicalAngularMap and SecondHarmonicDensity required')
    if azimuth_law!='SECOND_HARMONIC_DECLARED':raise ContractError('explicit SECOND_HARMONIC_DECLARED required')
    if not isinstance(detA,FiniteDetector) or not isinstance(detB,FiniteDetector):raise ContractError('FiniteDetector required')
    windows={p.window for p in detA.patches+detB.patches if p.active}
    N=len(windows)
    if N>8:raise ContractError('at most 8 active polar windows')
    default=delta is None
    delta=_Z._API.checked_delta((density.sigma/(20*N*density.maximum*2**40) if N and density.maximum else ONE) if default else delta)
    before=dict(model.operations)
    geo=_Z.azimuth_pair_response(model,density.polar,detA,detB,azimuth_law='UNIFORM_DECLARED',delta=delta)
    P=geo['strip_count']
    global_bound=10*N*density.maximum*delta+(ZERO if density.uniform else 4*density.sigma*P*F(1,2**84))
    arithmetic={key:ZERO for key in EVENTS+PARTS}
    if density.uniform:
        result=geo
    else:
        result={k:v for k,v in geo.items() if k not in EVENTS+PARTS}
        accum={key:[ZERO,ZERO,ZERO,ZERO] for key in EVENTS+PARTS}
        integral_cache={}
        def components(region):
            if region not in integral_cache:integral_cache[region]=density.integrals(region)
            return integral_cache[region]
        for strip in geo['strips']:
            lo,hi=strip['interval'];c,s=harmonic_integrals(lo,hi)
            def integrate(region):
                a0,ac,ass=components(region)
                return Interval.point(a0*(hi-lo))+c*ac+s*ass
            for key,sets in strip['sets'].items():
                inner,outer=integrate(sets.inner),integrate(sets.outer)
                area=_Z._API.length(sets.uncertain)*(hi-lo)
                values=accum[key]
                values[0]+=inner.lower;values[1]+=outer.upper;values[2]+=area
                values[3]+=inner.width+outer.width
        for key,(lower,upper,area,anum) in accum.items():
            arithmetic[key]=anum
            result[key]=MeasureBounds(max(ZERO,lower),min(density.sigma,upper),area,density.maximum*area+anum)
    result['inclusive_a']=result['ap'].added(result['am'])
    result['inclusive_b']=result['bp'].added(result['bm'])
    result['coincidence_assignments']=result['q1'].added(result['q2'])
    y=result['coincidence']
    result.update(coincidence_daughters=y.scaled(2),pair_energy_MeV=y.scaled(model.G),
                  selected_plus_energy_MeV=y.scaled(model.G/2),selected_minus_energy_MeV=y.scaled(model.G/2),
                  conditional_a=conditional_ratio(y,result['hit_a']),conditional_b=conditional_ratio(y,result['hit_b']),
                  event_global_width_bound=global_bound,arithmetic_widths=arithmetic,
                  polar_width_bounds={key:density.maximum*result[key].uncertainty_area for key in EVENTS+PARTS},
                  azimuth_law=azimuth_law,default_delta_used=default,density_sigma=density.sigma,density_bound=density.maximum,
                  operation_delta={k:model.operations[k]-before[k] for k in before})
    for key in EVENTS:
        if result[key].width>result[key].width_bound or result[key].width_bound>global_bound:raise ContractError('Boolean error bound violated')
        if default and N and density.sigma and not result[key].width<density.sigma/2**40:raise ContractError('default epsilon violated')
    return result
