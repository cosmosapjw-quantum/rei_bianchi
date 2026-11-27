"""Exact rational rectangle range integration with cooperative work guards.

Valid conditional on callback range inclusion over the ENTIRE t x parameter
box. The engine validates this declared contract; it cannot prove an arbitrary
callback truthful. This synthetic implementation has no HH/backend admission.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
import heapq
import time


class DomainFailure(ValueError): pass
class ResourceLimit(RuntimeError): pass
class InvalidRangeContract(ValueError): pass


def rational(x):
    if type(x) not in (int, F):
        raise TypeError('exact int/Fraction required; no bool or float conversion')
    return F(x)


@dataclass(frozen=True)
class Interval:
    lo: F
    hi: F

    def __post_init__(self):
        object.__setattr__(self, 'lo', rational(self.lo))
        object.__setattr__(self, 'hi', rational(self.hi))
        if self.lo > self.hi: raise ValueError('reversed interval')

    @property
    def width(self): return self.hi-self.lo

    def contains(self, other):
        if isinstance(other, Interval): return self.lo <= other.lo and other.hi <= self.hi
        return self.lo <= rational(other) <= self.hi

    def __add__(self, other): return Interval(self.lo+other.lo, self.hi+other.hi)
    def __neg__(self): return Interval(-self.hi, -self.lo)
    def __sub__(self, other): return self + (-other)
    def __mul__(self, other):
        p = (self.lo*other.lo, self.lo*other.hi, self.hi*other.lo, self.hi*other.hi)
        return Interval(min(p), max(p))
    def scale(self, x):
        x = rational(x)
        return Interval(min(self.lo*x,self.hi*x), max(self.lo*x,self.hi*x))


@dataclass(frozen=True)
class Rectangle:
    real: Interval
    imag: Interval

    def __post_init__(self):
        if type(self.real) is not Interval or type(self.imag) is not Interval:
            raise TypeError('real and imaginary exact intervals required')

    @property
    def max_width(self): return max(self.real.width,self.imag.width)
    def contains(self, other): return self.real.contains(other.real) and self.imag.contains(other.imag)
    def __add__(self, other): return Rectangle(self.real+other.real,self.imag+other.imag)
    def __mul__(self, other):
        return Rectangle(self.real*other.real-self.imag*other.imag,
                         self.real*other.imag+self.imag*other.real)
    def scale(self, x): return Rectangle(self.real.scale(x),self.imag.scale(x))


@dataclass(frozen=True)
class RangeClaim:
    enclosure: Rectangle
    integration_box: Interval
    parameter_box: Rectangle
    uniform: bool
    proof_reference: str


@dataclass(frozen=True)
class Caps:
    target_width: F = F(1, 64)
    max_evaluations: int = 20000
    max_panels: int = 2048
    max_wall_seconds: float = 10.0
    max_memory_bytes: int = 16*1024*1024
    max_rational_bits: int = 32768
    max_depth: int = 20
    max_stalled_splits: int = 3
    require_hard_memory_limit: bool = False

    def __post_init__(self):
        object.__setattr__(self,'target_width',rational(self.target_width))
        if self.target_width <= 0: raise ValueError('positive target width required')
        for name in ('max_evaluations','max_panels','max_memory_bytes','max_rational_bits','max_depth','max_stalled_splits'):
            if type(getattr(self,name)) is not int or getattr(self,name)<=0:
                raise ValueError('positive integer cap required: '+name)
        if type(self.max_wall_seconds) not in (int,float) or not 0 < self.max_wall_seconds < float('inf'):
            raise ValueError('finite positive wall limit required')
        if self.require_hard_memory_limit:
            raise ValueError('hard process memory isolation is not implemented; tracked state estimate only')


class Budget:
    """One shared budget across nested integrals; count all nested work.

    Wall checks are cooperative before/after callbacks and subdivisions. A
    blocking callback is NOT interrupted. State bytes are a tracked estimate
    (fixed per-panel allowance plus rational limbs), NOT RSS or a hard memory
    limit. Callbacks may allocate outside this estimate. External subprocess
    limits are required for an admitted hard host resource contract.
    """
    def __init__(self,caps: Caps,*,clock=time.monotonic):
        self.caps=caps
        self.clock=clock
        self.start=clock()
        self.evaluations=0
        self.live_panels=0
        self.peak_live_panels=0
        self.live_state_bytes=0
        self.peak_state_bytes=0
        self.subdivisions=0

    def check_time(self):
        if self.clock()-self.start >= self.caps.max_wall_seconds:
            raise ResourceLimit('MAX_WALL_SECONDS')

    def reserve(self,panels,state_bytes):
        self.check_time()
        if self.live_panels+panels>self.caps.max_panels: raise ResourceLimit('MAX_LIVE_PANELS')
        if self.live_state_bytes+state_bytes>self.caps.max_memory_bytes: raise ResourceLimit('MAX_TRACKED_STATE_BYTES')
        self.live_panels+=panels
        self.live_state_bytes+=state_bytes
        self.peak_live_panels=max(self.peak_live_panels,self.live_panels)
        self.peak_state_bytes=max(self.peak_state_bytes,self.live_state_bytes)

    def release(self,panels,state_bytes):
        self.live_panels-=panels
        self.live_state_bytes-=state_bytes
        assert self.live_panels>=0 and self.live_state_bytes>=0

    def before_callback(self):
        self.check_time()
        if self.evaluations>=self.caps.max_evaluations: raise ResourceLimit('MAX_EVALUATIONS')
        self.evaluations+=1

    def snapshot(self):
        return {'evaluations':self.evaluations,'subdivisions':self.subdivisions,
                'peak_live_panels':self.peak_live_panels,'peak_tracked_state_bytes':self.peak_state_bytes,
                'live_panels':self.live_panels,'live_tracked_state_bytes':self.live_state_bytes,
                'wall_seconds':self.clock()-self.start,'wall_limit_kind':'COOPERATIVE_CALLBACK_BOUNDARIES',
                'memory_limit_kind':'TRACKED_STATE_ESTIMATE_NOT_PROCESS_HARD_LIMIT'}


@dataclass(frozen=True)
class Result:
    status: str
    reason: str
    enclosure: Rectangle | None
    metrics: dict
    target_width: F
    parameter_box: Rectangle


def _rational_bytes(rect, limit):
    total=0
    for x in (rect.real.lo,rect.real.hi,rect.imag.lo,rect.imag.hi):
        bits=max(abs(x.numerator).bit_length(),x.denominator.bit_length())
        if bits>limit: raise ResourceLimit('MAX_RATIONAL_BITS')
        total+=(abs(x.numerator).bit_length()+7)//8+(x.denominator.bit_length()+7)//8+128
    return total


def _replace_sum(total,old,left,right):
    # Exact endpoint sums, not interval subtraction. Remove the SAME endpoint.
    return Rectangle(
        Interval(total.real.lo-old.real.lo+left.real.lo+right.real.lo,
                 total.real.hi-old.real.hi+left.real.hi+right.real.hi),
        Interval(total.imag.lo-old.imag.lo+left.imag.lo+right.imag.lo,
                 total.imag.hi-old.imag.hi+left.imag.hi+right.imag.hi))


def integrate_range(callback,integration_box: Interval,parameter_box: Rectangle,
                    *,caps: Caps|None=None,budget: Budget|None=None,target_width=None):
    """Integrate a proven whole-box range extension over a finite real interval.

    For each panel P, length(P)*range(callback,P,Z) contains its integral for
    every parameter in Z. Summing endpoint bounds is rigorous exact arithmetic;
    no analyticity theorem or Petras tolerance is inferred.
    """
    if type(integration_box) is not Interval or type(parameter_box) is not Rectangle:
        raise TypeError('exact finite interval and parameter rectangle required')
    if budget is None: budget=Budget(caps or Caps())
    elif caps is not None: raise ValueError('supply shared budget or new caps, not both')
    target=budget.caps.target_width if target_width is None else rational(target_width)
    if target<=0: raise ValueError('positive target width required')
    owned_panels=0
    owned_bytes=0
    total=None
    zero=Rectangle(Interval(0,0),Interval(0,0))
    status,reason='CALLBACK_IMPLEMENTATION_FAILURE','NO_RESULT'
    serial=0

    def reserve(panels,amount):
        nonlocal owned_panels,owned_bytes
        budget.reserve(panels,amount)
        owned_panels+=panels
        owned_bytes+=amount

    def evaluate(panel):
        panel_bytes=_rational_bytes(Rectangle(panel,Interval(0,0)),budget.caps.max_rational_bits)
        budget.before_callback()
        claim=callback(panel,parameter_box)
        budget.check_time()
        if (type(claim) is not RangeClaim or type(claim.enclosure) is not Rectangle or
            claim.uniform is not True or claim.integration_box!=panel or
            claim.parameter_box!=parameter_box or type(claim.proof_reference) is not str or
            not claim.proof_reference.strip()):
            raise InvalidRangeContract('whole-panel/whole-parameter uniform range witness required')
        payload=panel_bytes+_rational_bytes(claim.enclosure,budget.caps.max_rational_bits)
        contribution=claim.enclosure.scale(panel.width)
        payload+=_rational_bytes(contribution,budget.caps.max_rational_bits)
        reserve(0,payload)
        return contribution,2048+payload

    try:
        budget.check_time()
        _rational_bytes(parameter_box,budget.caps.max_rational_bits)
        _rational_bytes(Rectangle(integration_box,Interval(0,0)),budget.caps.max_rational_bits)
        _rational_bytes(Rectangle(Interval(target,target),Interval(0,0)),budget.caps.max_rational_bits)
        if integration_box.width==0:
            total=zero
        else:
            reserve(1,2048)
            value,cost=evaluate(integration_box)
            total=value
            heap=[(-value.max_width,serial,0,integration_box,value,cost)]
            stalled=0
            while total.max_width>target:
                budget.check_time()
                _,_,depth,panel,old,old_cost=heapq.heappop(heap)
                if depth>=budget.caps.max_depth: raise ResourceLimit('MAX_SUBDIVISION_DEPTH')
                reserve(2,4096) # Parent retained until both children succeed.
                midpoint=(panel.lo+panel.hi)/2
                lp,rp=Interval(panel.lo,midpoint),Interval(midpoint,panel.hi)
                lv,lc=evaluate(lp)
                rv,rc=evaluate(rp)
                replacement=_replace_sum(total,old,lv,rv)
                _rational_bytes(replacement,budget.caps.max_rational_bits)
                budget.release(1,old_cost)
                owned_panels-=1
                owned_bytes-=old_cost
                for child,value,child_cost in ((lp,lv,lc),(rp,rv,rc)):
                    serial+=1
                    heapq.heappush(heap,(-value.max_width,serial,depth+1,child,value,child_cost))
                budget.subdivisions+=1
                stalled=stalled+1 if replacement.max_width>=total.max_width else 0
                total=replacement
                if stalled>=budget.caps.max_stalled_splits:
                    status,reason='CERTIFICATE_INCONCLUSIVE_WIDTH','PARAMETER_IMAGE_OR_RANGE_DEPENDENCY_FLOOR'
                    break
            else:
                status,reason='TARGET_WIDTH_MET','ACHIEVED_EXACT_RECTANGLE_WIDTH'
        if integration_box.width==0:
            status,reason='TARGET_WIDTH_MET','ZERO_LENGTH_INTEGRAL'
    except ResourceLimit as exc:
        status,reason='CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT',str(exc)
    except InvalidRangeContract as exc:
        status,reason,total='INVALID_RANGE_CONTRACT',str(exc),None
    except DomainFailure as exc:
        status,reason,total='CALLBACK_DOMAIN_FAILURE',str(exc),None
    except Exception as exc:
        status,reason,total='CALLBACK_IMPLEMENTATION_FAILURE',type(exc).__name__+': '+str(exc),None
    finally:
        budget.release(owned_panels,owned_bytes)
    return Result(status,reason,total,budget.snapshot(),target,parameter_box)
