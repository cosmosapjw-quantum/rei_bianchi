"""Positive N/U subcells for a moving HeII threshold; research pilot only."""
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import brentq
L=np.longdouble
T=54.42; BIND=54.41776; C=2.99792458e10
@dataclass(frozen=True)
class Cell:
    n:float
    u:float
    lo:float
    hi:float
def combine(cs):
    cs=[c for c in cs if c is not None]
    if not cs:return None
    return Cell(sum((L(c.n) for c in cs),L(0)),sum((L(c.u) for c in cs),L(0)),min(c.lo for c in cs),max(c.hi for c in cs))
@lru_cache(None)
def gl(n):return leggauss(n)
def emean(b):
    if b<1e-3:return .5-b/12+b**3/720-b**5/30240
    if b>700:return 1/b
    return 1/b-1/np.expm1(b)
def nodes(c,cuts=(),order=24):
    n,u,l,r=map(L,(c.n,c.u,c.lo,c.hi))
    assert n>0 and 0<l<=r
    ld=u-l*n;ud=r*n-u
    m=l+ld/n if ld<=ud else r-ud/n
    # An endpoint equality is a delta. Reject inconsistent moment inputs
    # (do not clip); exact inputs can have representation-scale rounding.
    if m<l or m>r:
        if min(abs(m-l),abs(m-r))>8*np.finfo(L).eps*max(l,r):raise ValueError('invalid moment')
        m=l if m<l else r
    if l==r or m==l or m==r:return np.array([m],dtype=L),np.array([n],dtype=L)
    w=r-l;flip=m>(l+r)/2
    d=float((r-m if flip else m-l)/w)
    b=0. if d==.5 else brentq(lambda z:emean(z)-d,0.,max(2.,2/d),xtol=1e-14)
    norm=max(1.,b);end=min(norm,60.) if b>1 else 1.
    points=[0.,end];points.extend(float(v) for v in np.arange(2.,end,2.))
    for edge in cuts:
        x=float((r-L(edge) if flip else L(edge)-l)/w)*norm
        if 0<x<end:points.append(x)
    points=sorted(set(points));x,ww=gl(order);q=[];wt=[]
    for a,z in zip(points[:-1],points[1:]):
        v=(a+z)/2+(z-a)*x/2;t=np.asarray(v/norm,dtype=L)
        q.extend(r-w*t if flip else l+w*t)
        wt.extend((z-a)*ww/2*np.exp(-b*v/norm))
    q=np.asarray(q,dtype=L);wt=np.asarray(wt,dtype=L);wt*=n/wt.sum()
    assert abs(wt@q-u)<=3e-12*abs(u)
    return q,wt
def from_nodes(q,w,lo,hi):
    n=w.sum()
    if n<=0:return None
    return Cell(n,w@q,lo,hi)
def split(c,cut,order=32):
    if c is None:return None,None
    if c.hi<cut:return c,None
    if c.lo>=cut:return None,c
    q,w=nodes(c,[cut],order);mask=q>=cut
    a=from_nodes(q[~mask],w[~mask],c.lo,min(c.hi,cut))
    b=from_nodes(q[mask],w[mask],max(c.lo,cut),c.hi)
    m=combine([a,b]);assert abs(m.n-c.n)<2e-12*c.n and abs(m.u-c.u)<3e-12*c.u
    return a,b
def sigma(E):
    x=np.asarray(E)/1.720
    return np.where(E>=T,1.369e4*(x-1)**2*x**(2.963/2-5.5)*(1+np.sqrt(x/32.88))**(-2.963)*1e-18,0.)
def rates(cells,scale,nh):
    g=L(0);h=L(0);above=L(0)
    for c in cells:
        if c is None:continue
        q,w=nodes(c,[T/scale],32);e=q*scale;s=sigma(e);g+=w@s;h+=w@(s*(e-BIND));above+=w[e>=T].sum()
    return np.array([C*nh*g,C*nh*h,above],float)
def debit(c,mid_scale,dt,nh_heii,new_cut,split_out,order=24):
    q,w=nodes(c,[T/mid_scale,new_cut],order);E=q*mid_scale
    opacity=L(C*nh_heii*dt)*sigma(E)
    lost=w*(-np.expm1(-opacity));remain=w*np.exp(-opacity)
    if split_out:
        k=q>=new_cut
        cc=[from_nodes(q[~k],remain[~k],c.lo,min(c.hi,new_cut)),
            from_nodes(q[k],remain[k],max(c.lo,new_cut),c.hi)]
    else:cc=[from_nodes(q,remain,c.lo,c.hi)]
    cc=[x for x in cc if x is not None];m=combine(cc)
    nloss=lost.sum();uloss=lost@q
    assert abs((m.n if m else 0)+nloss-c.n)<3e-12*c.n
    assert abs((m.u if m else 0)+uloss-c.u)<4e-12*c.u
    return cc,nloss,uloss,lost@(E-BIND)
