"""Bounded plan construction and interval difference diagnostics."""
from eventwise import refine

def build_32(parent16):
    return refine(parent16)

from fractions import Fraction
from collections.abc import Sequence

def split_difference(a: Sequence[float], b: Sequence[float]):
    """Exact rational rectangle-difference upper, split into centre and radii.

    The result encloses matched-parameter differences; it does not estimate
    continuous error, and a large upper bound does not imply actual failure.
    """
    if len(a)!=2 or len(b)!=2:
        raise ValueError('TWO_ENDPOINT_INTERVAL_REQUIRED')
    x0,x1=map(Fraction,a); y0,y1=map(Fraction,b)
    if x0>x1 or y0>y1:
        raise ValueError('ORDERED_INTERVAL_REQUIRED')
    centre=abs((x0+x1-y0-y1)/2)
    radii=(x1-x0+y1-y0)/2
    upper=max(abs(x0-y1),abs(x1-y0))
    assert upper==centre+radii
    return dict(upper=upper,centre_difference=centre,radii_sum=radii)

def signed_ratio(a,b,c):
    """Enclose (a-b)/(b-c), only when both differences have one common sign."""
    x=tuple(map(Fraction,a));y=tuple(map(Fraction,b));z=tuple(map(Fraction,c))
    if any(p>q for p,q in (x,y,z)):raise ValueError('ORDERED_INTERVAL_REQUIRED')
    d1=(x[0]-y[1],x[1]-y[0]);d2=(y[0]-z[1],y[1]-z[0])
    if d1[0]<=0<=d1[1] or d2[0]<=0<=d2[1]:
        return None
    if (d1[0]>0)!=(d2[0]>0):return None
    ratios=[u/v for u in d1 for v in d2]
    return min(ratios),max(ratios)
