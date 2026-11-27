"""Exact finite-sector enclosures for a declared uniform-azimuth paired measure.

The relative KINEMATIC08 source is reused without changing its polar solver.
Circle endpoints and singleton polar windows have continuous measure zero.
"""
from dataclasses import dataclass
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

_PARENT=Path(__file__).resolve().parents[2]/'continuation_kinematic_20261028/src/kinematic.py'
_SPEC=importlib.util.spec_from_file_location('_azimuth09_inherited_kinematic',_PARENT)
_K=importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name]=_K
_SPEC.loader.exec_module(_K)
_API=_K._API
ContractError=_K.ContractError
PhysicalAngularMap=_K.PhysicalAngularMap
BernsteinDensity=_K.BernsteinDensity
SetBounds=_K.SetBounds
rational=_K.rational
ZERO=Fraction(0)
HALF=Fraction(1,2)


def turn_arc(start,width):
    """Canonical rational-turn intervals; full width 1 differs from empty 0."""
    start,width=rational(start,'arc start'),rational(width,'arc width')
    if not 0<=start<1 or not 0<=width<=1:
        raise ContractError('arc requires 0<=start<1 and 0<=width<=1')
    if width==0:return ()
    if width==1:return ((ZERO,Fraction(1)),)
    end=start+width
    return ((start,end),) if end<=1 else ((ZERO,end-1),(start,Fraction(1)))


def shifted(intervals,amount=HALF):
    pieces=[]
    for lo,hi in intervals:pieces.extend(turn_arc((lo+amount)%1,hi-lo))
    # Inherited normalization supports [0,1] and merges all contacts exactly.
    return _API.normalize(pieces)


@dataclass(frozen=True)
class DetectorPatch:
    window: tuple
    arc: tuple

    def __post_init__(self):
        window=_API.lab_window(self.window)
        try:
            if len(self.arc)!=2:raise ContractError('arc needs (start,width)')
            start,width=(rational(x,n) for x,n in zip(self.arc,('arc start','arc width')))
        except TypeError as exc:raise ContractError('arc needs (start,width)') from exc
        turn_arc(start,width)
        object.__setattr__(self,'window',window)
        object.__setattr__(self,'arc',(start,width))

    @property
    def intervals(self):return turn_arc(*self.arc)

    @property
    def active(self):return self.window[0]<self.window[1] and self.arc[1]>0


@dataclass(frozen=True)
class FiniteDetector:
    patches: tuple

    def __post_init__(self):
        try:patches=tuple(self.patches)
        except TypeError as exc:raise ContractError('patch sequence required') from exc
        if len(patches)>8:raise ContractError('at most 8 patches per detector')
        if any(not isinstance(p,DetectorPatch) for p in patches):raise ContractError('DetectorPatch entries required')
        object.__setattr__(self,'patches',patches)


@dataclass(frozen=True)
class MeasureBounds:
    lower: Fraction
    upper: Fraction
    uncertainty_area: Fraction
    width_bound: Fraction

    def __post_init__(self):
        if self.lower>self.upper or self.width>self.width_bound or self.uncertainty_area<0:
            raise ContractError('invalid measure bounds')

    @property
    def width(self):return self.upper-self.lower

    def added(self,other):
        return MeasureBounds(self.lower+other.lower,self.upper+other.upper,
                             self.uncertainty_area+other.uncertainty_area,self.width_bound+other.width_bound)

    def scaled(self,factor):
        factor=rational(factor,'scale')
        return MeasureBounds(min(factor*self.lower,factor*self.upper),max(factor*self.lower,factor*self.upper),
                             self.uncertainty_area,abs(factor)*self.width_bound)


def conditional_ratio(num,den):
    if den.upper==0:return dict(lower=None,upper=None,width=None,status='UNDEFINED_ZERO_DENOMINATOR')
    if den.lower==0:return dict(lower=None,upper=None,width=None,status='UNRESOLVED_DENOMINATOR')
    lo,hi=num.lower/den.upper,min(Fraction(1),num.upper/den.lower)
    return dict(lower=lo,upper=hi,width=hi-lo,status='CERTIFIED_ENCLOSURE')


EVENTS=('coincidence','hit_a','hit_b','double_a','double_b','both_detectors_hit','assignment_overlap')
PARTS=('ap','am','bp','bm','q1','q2')


def azimuth_pair_response(model,density,detA,detB,*,azimuth_law,delta=None):
    if not isinstance(model,PhysicalAngularMap) or not isinstance(density,BernsteinDensity):
        raise ContractError('PhysicalAngularMap and BernsteinDensity required')
    if azimuth_law!='UNIFORM_DECLARED':raise ContractError('explicit UNIFORM_DECLARED azimuth law required')
    if not density.symmetric:raise ContractError('paired API requires even Bernstein density')
    if not isinstance(detA,FiniteDetector) or not isinstance(detB,FiniteDetector):raise ContractError('FiniteDetector required')
    patches=detA.patches+detB.patches
    if len(patches)>16:raise ContractError('at most 16 patches total')
    windows=sorted({p.window for p in patches if p.active})
    N=len(windows)
    if N>8:raise ContractError('at most 8 distinct active polar windows')
    delta=_API.checked_delta((density.sigma/(10*N*density.maximum*2**40) if N and density.maximum else Fraction(1)) if delta is None else delta)
    global_bound=10*N*density.maximum*delta
    empty=MeasureBounds(ZERO,ZERO,ZERO,ZERO)
    result={key:empty for key in EVENTS+PARTS}
    result.update(delta=delta,unique_window_count=N,patch_count=len(patches),strip_count=0,
                  event_global_width_bound=global_bound,strips=[],preimages={},azimuth_law=azimuth_law,
                  semantic_status='ZERO_DENSITY' if not density.maximum else 'EMPTY_GEOMETRY' if not N else 'CERTIFIED_ENCLOSURE')
    if N and density.maximum:
        preimages={w:model.preimage(w,delta) for w in windows}
        result['preimages']=preimages
        endpoints={ZERO,Fraction(1)}
        for p in patches:
            if p.active:
                for intervals in (p.intervals,shifted(p.intervals)):
                    endpoints.update(x for interval in intervals for x in interval)
        endpoints=sorted(endpoints)
        def membership(det,t,reflect=False):
            sets=SetBounds((),())
            for p in det.patches:
                if p.active and any(lo<=t<hi for lo,hi in p.intervals):
                    item=preimages[p.window].sets
                    sets=sets.union(item.reflected() if reflect else item)
            return sets
        for lo,hi in zip(endpoints,endpoints[1:]):
            t=(lo+hi)/2
            ap,am=membership(detA,t),membership(detA,(t+HALF)%1,True)
            bp,bm=membership(detB,t),membership(detB,(t+HALF)%1,True)
            q1,q2=ap.intersection(bm),bp.intersection(am)
            ha,hb=ap.union(am),bp.union(bm)
            sets=dict(ap=ap,am=am,bp=bp,bm=bm,q1=q1,q2=q2,
                      coincidence=q1.union(q2),hit_a=ha,hit_b=hb,double_a=ap.intersection(am),
                      double_b=bp.intersection(bm),both_detectors_hit=ha.intersection(hb),assignment_overlap=q1.intersection(q2))
            for key,region in sets.items():
                bound=density.bounds(region)
                result[key]=result[key].added(MeasureBounds(bound.lower*(hi-lo),bound.upper*(hi-lo),bound.uncertainty_length*(hi-lo),bound.width_bound*(hi-lo)))
            result['strips'].append(dict(interval=(lo,hi),midpoint=t,sets=sets))
        result['strip_count']=len(result['strips'])
    result['inclusive_a']=result['ap'].added(result['am'])
    result['inclusive_b']=result['bp'].added(result['bm'])
    result['coincidence_assignments']=result['q1'].added(result['q2'])
    y=result['coincidence']
    result.update(coincidence_daughters=y.scaled(2),pair_energy_MeV=y.scaled(model.G),
                  selected_plus_energy_MeV=y.scaled(model.G/2),selected_minus_energy_MeV=y.scaled(model.G/2),
                  conditional_a=conditional_ratio(y,result['hit_a']),conditional_b=conditional_ratio(y,result['hit_b']))
    for key in EVENTS:
        if result[key].width>result[key].width_bound or result[key].width_bound>global_bound:
            raise ContractError('Boolean event uncertainty exceeds global width bound')
    return result
