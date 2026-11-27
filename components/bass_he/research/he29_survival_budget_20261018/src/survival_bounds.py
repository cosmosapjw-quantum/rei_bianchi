"""Sharp positive-measure survival envelopes, not a continuum-error certificate.

Rates: nonnegative s^-1; age: proper seconds; weights: photons/H or normalized
source mass. Exact inequalities follow from convexity. Floating evaluations
carry a conservative diagnostic guard, not interval-arithmetic certification.
Partitioning donor atoms never changes the physical photon solver.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

@dataclass(frozen=True)
class Envelope:
    lower: float
    upper: float
    mass: float
    groups: int
    roundoff_guard: float = 0.
    @property
    def width(self): return self.upper-self.lower


def moment_bounds(mass: float, mean: float, lo: float, hi: float, age_s: float):
    """Jensen lower / endpoint-chord upper for a measure with specified moments.

    All values are finite. N=0 requires mean/support domain consistency but is
    otherwise a zero contribution. Sharp for a Dirac mean and endpoint mixture.
    """
    values=(mass,mean,lo,hi,age_s)
    if not all(math.isfinite(float(x)) for x in values):
        raise ValueError('HE29_NONFINITE_MOMENT')
    if mass<0 or age_s<0 or lo<0 or not lo<=mean<=hi:
        raise ValueError('HE29_MOMENT_DOMAIN')
    if mass==0: return (0.,0.)
    if age_s==0: return (mass,mass)
    if not math.isfinite(age_s*hi): raise ValueError('HE29_OPTICAL_DEPTH_OVERFLOW')
    lower=mass*math.exp(-age_s*mean)
    if hi==lo: return lower,lower
    right=(mean-lo)/(hi-lo)
    # Positive combination avoids cancellation at very large optical depth.
    upper=mass*((1-right)*math.exp(-age_s*lo)+right*math.exp(-age_s*hi))
    return lower,max(lower,upper)


def survival_envelope(rates, weights, age_s: float, depth: int=0) -> Envelope:
    """Nested dyadic rate partitions of a *finite positive donor measure*.

    Support extrema are those of each donor subset, not continuum energy
    extrema. A continuum interpretation needs independently bounded omitted
    quadrature error. No value from a native gas history is modified.
    """
    r=np.asarray(rates,dtype=float);w=np.asarray(weights,dtype=float)
    if (r.ndim!=1 or w.shape!=r.shape or r.size==0 or
        not np.isfinite(r).all() or not np.isfinite(w).all() or
        np.any(r<0) or np.any(w<0) or not math.isfinite(age_s) or age_s<0):
        raise ValueError('HE29_DONOR_DOMAIN')
    if type(depth) is not int or not 0<=depth<=16: raise ValueError('HE29_DEPTH_DOMAIN')
    pos=w>0;r=r[pos];w=w[pos]
    if r.size==0:return Envelope(0.,0.,0.,0)
    mass=math.fsum(map(float,w))
    if not math.isfinite(mass):raise ValueError('HE29_MASS_OVERFLOW')
    if not math.isfinite(float(r.max())*age_s):raise ValueError('HE29_OPTICAL_DEPTH_OVERFLOW')
    if age_s==0 or r.max()==r.min():
        v=mass*math.exp(-age_s*float(r[0]));return Envelope(v,v,mass,1)
    bins=1<<depth
    scaled=(r-r.min())/(r.max()-r.min())
    codes=np.minimum((scaled*bins).astype(np.int64),bins-1)
    order=np.argsort(codes,kind='stable');r=r[order];w=w[order];codes=codes[order]
    starts=np.r_[0,np.flatnonzero(np.diff(codes))+1];ends=np.r_[starts[1:],len(r)]
    lows=[];highs=[]
    for a,b in zip(starts,ends):
        rr=r[a:b];ww=w[a:b];n=math.fsum(map(float,ww));lo=float(rr.min());hi=float(rr.max())
        # Mean of shifted rates is well conditioned at narrow support width.
        mean=lo+math.fsum(float(v/n)*float(x-lo) for x,v in zip(rr,ww))
        mean=min(hi,max(lo,mean))  # convex mean roundoff only, never physical state clipping
        lb,ub=moment_bounds(n,mean,lo,hi,age_s);lows.append(lb);highs.append(ub)
    lower=math.fsum(lows);upper=math.fsum(highs)
    guard=64*np.finfo(float).eps*mass
    return Envelope(max(0.,lower-guard),min(mass,upper+guard),mass,len(starts),guard)


def distance_interval(value: float, envelope: Envelope):
    """Conditional bounds for |value - true_target|, not a gas-temperature error."""
    if not math.isfinite(value):raise ValueError('HE29_NONFINITE_ESTIMATE')
    lo,hi=envelope.lower,envelope.upper
    return max(0.,lo-value,value-hi),max(abs(value-lo),abs(value-hi))


def difference_interval(a: float,b: float,ea: float,eb: float):
    """If |A-a|<=ea and |B-b|<=eb, return bounds for |A-B|.

    The caller owns validity of ea/eb. Two-integrator agreement by itself is
    empirical reference stability and does not prove either radius.
    """
    if not all(math.isfinite(x) for x in (a,b,ea,eb)) or min(ea,eb)<0:
        raise ValueError('HE29_DIFFERENCE_DOMAIN')
    delta=abs(a-b);e=ea+eb
    return max(0.,delta-e),delta+e
