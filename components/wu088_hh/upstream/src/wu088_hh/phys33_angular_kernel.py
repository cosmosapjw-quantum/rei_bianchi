"""PHYS39 C7B: exact positive-distance angular screened multipole kernels.

For each rational r>0, R=7/10 and integer n>=0, certify
  K_lm(n;r)=1/2 int_-1^1 P_l(mu)P_m(mu)e^{-n s(r,mu)}dmu,
s=sqrt(r^2+R^2-2rRmu).
Substitution mu=(r²+R²-s²)/(2rR) makes the integrand a polynomial
in s² times s e^{-n s}. All finite moments are exact rational /
explicit rational brackets of exponential endpoints. Includes s=0
at r=R without artificial smoothing.
The full 3D radial strong residual is NOT thereby certified.
"""
from __future__ import annotations
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
from time import perf_counter

from .phys33_coupled_source import exp_negative_bounds,outward_decimal

R=Q(7,10)


def _add(a:list[Q],b:list[Q])->list[Q]:
    z=[Q(0)]*max(len(a),len(b))
    for i,v in enumerate(a):z[i]+=v
    for i,v in enumerate(b):z[i]+=v
    return z


def _scale(a:list[Q],c:Q)->list[Q]:
    return [v*c for v in a]


def _mul(a:list[Q],b:list[Q])->list[Q]:
    z=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b):
                if y:z[i+j]+=x*y
    return z


def legendre_in_s2(ell:int,r:Q)->list[Q]:
    """P_ell((r²+R²-s²)/(2rR)), polynomial in z=s²."""
    if ell<0 or ell>40 or r<=0:
        raise ValueError("ell range 0..40 and strictly positive rational r")
    mu=[(r*r+R*R)/(2*r*R), -Q(1)/(2*r*R)]
    if ell==0:return [Q(1)]
    if ell==1:return mu
    p0=[Q(1)];p1=mu
    for j in range(2,ell+1):
        p2=_add(_scale(_mul(mu,p1),Q(2*j-1,j)),
                _scale(p0,Q(-(j-1),j)))
        p0,p1=p1,p2
    return p1


@lru_cache(maxsize=10000)
def power_exponential_moment(k:int,n:int,a:Q,b:Q,
                             terms:int=192)->tuple[Q,Q]:
    """Rigorous ∫_a^b s^k exp(-n s)ds, nonnegative k,n, 0<=a<b."""
    if not 0<=k<=161 or not 0<=n<=64 or not 0<=a<b:
        raise ValueError("moment requires nonnegative powers and finite ordered points")
    if n==0:
        z=(b**(k+1)-a**(k+1))/(k+1)
        return z,z
    if terms<=n*b:
        raise ValueError("Taylor order too low to majorize exp(n*b)")
    def polynomial(x:Q)->Q:
        coeff=Q(1);acc=coeff
        for j in range(1,k+1):
            coeff*=x/j;acc+=coeff
        return acc
    el,eh=exp_negative_bounds(n*a,terms)
    fl,fh=exp_negative_bounds(n*b,terms)
    scale=Q(factorial(k),n**(k+1))
    low=scale*(el*polynomial(n*a)-fh*polynomial(n*b))
    high=scale*(eh*polynomial(n*a)-fl*polynomial(n*b))
    if high<0:
        raise ArithmeticError("physical exponential moment upper negative")
    return max(Q(0),low),high


def angular_multipole_element(l:int,m:int,n:int,r:Q,
                              terms:int=192)->tuple[Q,Q]:
    if r<=0 or not isinstance(r,Q):
        raise ValueError("r must be an exact positive Fraction")
    if l<0 or m<0 or n<0:
        raise ValueError("nonnegative angular and screening indices")
    p_l=legendre_in_s2(l,r);p_m=legendre_in_s2(m,r)
    poly=_mul(p_l,p_m)
    a,b=abs(r-R),r+R
    lo,hi=Q(0),Q(0)
    for j,c in enumerate(poly):
        if c==0:continue
        mlo,mhi=power_exponential_moment(2*j+1,n,a,b,terms)
        if c>0:lo+=c*mlo;hi+=c*mhi
        else:lo+=c*mhi;hi+=c*mlo
    norm=2*r*R
    lo/=norm;hi/=norm
    if lo>hi:
        raise ArithmeticError("inverted angular kernel enclosure")
    return lo,hi


def angular_multipole_matrix(r:Q,n:int,lmax:int=5,terms:int=192,
                             digits:int=16)->dict:
    if not isinstance(r,Q) or r<=0 or not 0<=lmax<=16 or not 0<=n<=32:
        raise ValueError("invalid physical radius and indices")
    start=perf_counter()
    rows=[]
    for l in range(lmax+1):
        row=[]
        for m in range(lmax+1):
            lo,hi=angular_multipole_element(l,m,n,r,terms)
            row.append([outward_decimal(lo,digits,False),
                        outward_decimal(hi,digits,True)])
        rows.append(row)
    return {
       "schema":"WU088_HH_PHYS39_GLOBAL_S_ANGULAR_KERNEL_V1",
       "radius_a0":str(r),"spectator_R_a0":"7/10",
       "power_of_E":n,"lmax":lmax,
       "normalization":"K_lm=1/2 int_-1^1 P_lP_m exp(-n s)dmu (not Y_l0 normalized)",
       "interval_matrix":rows,
       "Taylor_terms":terms,"wall_s":perf_counter()-start,
       "scope":"complete angular integral for ONE arbitrary positive r, all m/l<=lmax; no radial integration",
       "not_claimed":["whole radial PDE integration","generic screened derivative U/q mixed kernels",
           "continuous resolvent/physical scattering amplitude or thermal rate"],
    }
