"""PHYS42: signed, joint radial-angle rigorous original screened PDE certificate.

Preserves the entire 21-wave original operator, exact dyadic source and
Coulomb source cancellation before range evaluation. Each (r,mu) rectangle
uses exact rational Bernstein ranges of radial u/ru'-u/r²D_l u and
Legendre/derivative angular polynomials. Exponentials and sqrt use
explicit outward rational intervals; full 3D volume is integrated via
positive cell masses. The coalescence radius r=R is delegated to
existing PHYS38 log-direction certificate, never smoothed.

This is a conservative pointwise interval method with symbolic
cancellation, not a continuous scattering inverse or physical rate.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from fractions import Fraction as F
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from math import comb
from pathlib import Path
import hashlib
from time import perf_counter

from .phys33_residual import (
    load_frozen,dyadic,interpolants,reconstruct,value,derivative,mul,add,scale,
    ceil_sqrt_fixed,
)
from .phys33_panel_bernstein import _bernstein_transform,source_numerator_polynomial,radial_cuts
from .phys33_full_coupled_shell import R,K2,_expand_legendre
from .phys33_cusp_shell import _qrt_sqrt
from .phys33_coupled_source import exp_negative_bounds,outward_decimal

L_MAX=20
SCHEMA="WU088_HH_PHYS42_JOINT_SIGNED_RADIAL_ANGULAR_INTERVAL_V1"


@dataclass(frozen=True,slots=True)
class I:
    lo:F
    hi:F
    def __post_init__(self):
        if self.lo>self.hi:raise ValueError("inverted exact interval")
    @staticmethod
    def const(z:F|int)->"I":
        z=F(z)
        return I(z,z)
    def __add__(self,other:"I"|F|int)->"I":
        z=_interval(other)
        return I(self.lo+z.lo,self.hi+z.hi)
    __radd__=__add__
    def __neg__(self)->"I":return I(-self.hi,-self.lo)
    def __sub__(self,other:"I"|F|int)->"I":return self+-_interval(other)
    def __rsub__(self,other:"I"|F|int)->"I":return _interval(other)+-self
    def __mul__(self,other:"I"|F|int)->"I":
        z=_interval(other)
        corners=(self.lo*z.lo,self.lo*z.hi,self.hi*z.lo,self.hi*z.hi)
        return I(min(corners),max(corners))
    __rmul__=__mul__
    def __truediv__(self,other:"I"|F|int)->"I":
        z=_interval(other)
        if z.lo<=0<=z.hi:raise ZeroDivisionError("interval denominator contains zero")
        return self*I(1/z.hi,1/z.lo)
    def absup(self)->F:return max(abs(self.lo),abs(self.hi))
    def cut(self,digits:int=18)->"I":
        return I(F(outward_decimal(self.lo,digits,False)),
                 F(outward_decimal(self.hi,digits,True)))


def _interval(x:I|F|int)->I:
    return x if isinstance(x,I) else I.const(x)


def bernstein_range(coeff:list[F],x0:F,x1:F)->I:
    if x0>=x1 or not coeff:raise ValueError("nonempty positive tile")
    rows=_bernstein_transform(x0,x1,len(coeff)-1)
    bounds=[sum((w*c for w,c in zip(row,coeff)),F(0)) for row in rows]
    return I(min(bounds),max(bounds))


@lru_cache(maxsize=2)
def _angular_polynomials()->tuple:
    P=_expand_legendre([F(0),F(1)],L_MAX)
    Ts=[]
    for l,pol in enumerate(P):
        prev=P[l-1] if l else [F(0)]
        Ts.append(scale(add(prev,scale(mul([F(0),F(1)],pol),F(-1))),F(l)))
    return P,Ts


@lru_cache(maxsize=1000)
def angular_ranges(mu0:F,mu1:F)->tuple:
    P,T=_angular_polynomials()
    return tuple(bernstein_range(p,mu0,mu1).cut() for p in P),tuple(
        bernstein_range(t,mu0,mu1).cut() if l else I.const(0)
        for l,t in enumerate(T))


def prepare_radial_panel(filename:str|Path,j:int)->dict:
    rr,uu,digest=load_frozen(filename,True)
    nodes=[dyadic(z) for z in rr[j]]
    lo,hi=nodes[0],nodes[-1]
    mid,half=(lo+hi)/2,(hi-lo)/2
    scaled=[(v-mid)/half for v in nodes]
    basis=interpolants(scaled)
    poly=[]
    rp=[mid,half]
    rp2=mul(rp,rp)
    for ell in range(L_MAX+1):
        re,im=reconstruct(uu[ell,j],basis)
        p=[]
        for y in (re,im):
            v1=scale(derivative(y),1/half)
            v2=scale(derivative(v1),1/half)
            L=F(ell*(ell+1))
            nu=add(mul(rp2,v2),mul(add(add(scale(rp2,K2),scale(rp,F(2))),[-L]),y))
            vru=add(mul(rp,v1),scale(y,F(-1)))
            p.append((y,vru,nu))
        poly.append(p)
    return {"panel":j,"radial":[lo,hi],"mid":mid,"half":half,
            "source_sha256":digest,"polynomials":poly}


def _sqrt_bracket_nonnegative(x:F,digits:int=18)->I:
    if x<0:raise ValueError("negative squared distance")
    scale=10**digits
    from math import isqrt
    n=isqrt(x.numerator*scale*scale//x.denominator)
    lo=F(n,scale)
    hi=lo if n*n*x.denominator==x.numerator*scale*scale else F(n+1,scale)
    return I(lo,hi)


def _s_interval(a:F,b:F,mlo:F,mhi:F)->I:
    if not F(0)<a<b or not -1<=mlo<mhi<=1:
        raise ValueError("physical radius and cosine bounds")
    dmin=F(0) if a<=R<=b else min(abs(a-R),abs(b-R))
    dmax=max(abs(a-R),abs(b-R))
    l=dmin**2+2*a*R*(1-mhi)
    h=dmax**2+2*b*R*(1-mlo)
    if l<0 or h<l:raise ArithmeticError("invalid s bracket")
    return I(_sqrt_bracket_nonnegative(l).lo,_sqrt_bracket_nonnegative(h).hi)


@lru_cache(maxsize=4096)
def _exp_minus(x:F)->I:
    a,b=exp_negative_bounds(x,terms=96)
    return I(a,b).cut()


def _e_q_U_source(r:I,s:I)->tuple[I,I,I,I]:
    if s.lo<=0:raise ValueError("spectator zero excluded from this tile")
    elo=_exp_minus(s.hi).lo
    ehi=_exp_minus(s.lo).hi
    E=I(elo,ehi)
    # q(s)=int_0^1 exp(-st)dt is positive decreasing.
    qlo=(1-_exp_minus(s.hi).hi)/s.hi
    qhi=(1-_exp_minus(s.lo).lo)/s.lo
    q=I(qlo,qhi)
    U=E*q -E/2-I.const(F(3,2))*E*E
    # Source correction S0(1-exp(-E)) is positive and monotone in E.
    src=2*(1+K2)*I(_exp_minus(r.hi).lo,_exp_minus(r.lo).hi)
    xi=I(1-_exp_minus(E.lo).hi,1-_exp_minus(E.hi).lo)
    return E,U,src,src*xi


@lru_cache(maxsize=1)
def _alphas()->tuple[I,...]:
    return tuple(I(*_qrt_sqrt(2*l+1)).cut(18) for l in range(L_MAX+1))


def _radial_ranges(prepared:dict,a:F,b:F,order:int=24)->dict:
    mid,half=prepared["mid"],prepared["half"]
    xa,xb=(a-mid)/half,(b-mid)/half
    srce,eps=source_numerator_polynomial(a,b,mid,half,order)
    terms=[]
    for l,modes in enumerate(prepared["polynomials"]):
        row=[]
        for comp, (up,ru,nu) in enumerate(modes):
            if l==0 and comp==0:
                nu=add(nu,scale(srce,F(-1)))
            row.append(tuple(bernstein_range(p,xa,xb).cut(18)
                             for p in (up,ru,nu)))
        terms.append(row)
    return {"terms":terms,"source_error":I(-eps,eps).cut(18)}


def certify_cell(prepared:dict,a:F,b:F,mlo:F,mhi:F,radial:dict|None=None)->dict:
    if a<prepared["radial"][0] or b>prepared["radial"][1]:
        raise ValueError("cell outside its actual parent panel")
    if a<=R<=b:raise ValueError("spectator cusp cylinder requires PHYS38")
    ri=I(a,b)
    mi=I(mlo,mhi)
    s=_s_interval(a,b,mlo,mhi)
    E,U,src,source_correction=_e_q_U_source(ri,s)
    P,Ts=angular_ranges(mlo,mhi)
    radial=_radial_ranges(prepared,a,b) if radial is None else radial
    ar=[I.const(0),I.const(0)]
    B=[I.const(0),I.const(0)]
    C=[I.const(0),I.const(0)]
    T=[I.const(0),I.const(0)]
    iR=I.const(R)
    ialph=_alphas()
    for l,components in enumerate(radial["terms"]):
        co=ialph[l]*P[l]
        to=ialph[l]*Ts[l]
        for k,(u,ru,nu) in enumerate(components):
            ar[k]=(ar[k]+co*nu/(ri*ri*ri)).cut(18)
            B[k]=(B[k]+co*u/ri).cut(18)
            C[k]=(C[k]+co*ru/(ri*ri)).cut(18)
            T[k]=(T[k]+to*u/ri).cut(18)
    rminus=ri-iR*mi
    q=[]
    for k in (0,1):
        H=rminus*C[k]-(iR/ri)*T[k]
        G=ar[k]-2*(E/s)*H-2*U*B[k]
        if k==0:G=G+source_correction+radial["source_error"]
        q.append(G.cut(16).absup())
    vol=(b**3-a**3)*F(mhi-mlo,6)
    sq=(q[0]**2+q[1]**2)*vol
    return {"radial":[str(a),str(b)],"mu":[str(mlo),str(mhi)],
            "max_abs_real_upper":outward_decimal(q[0],12,True),
            "max_abs_imag_upper":outward_decimal(q[1],12,True),
            "residual_squared_volume_upper":outward_decimal(sq,18,True),
            "_sq_exact":sq}


def joint_strip(filename:str|Path,center:F,delta:F,radial_bins:int=2,
                mu_bins:int=64,digits:int=12,workers:int=1)->dict:
    if not isinstance(center,F) or not isinstance(delta,F) or not center>delta>0:
        raise ValueError("exact positive physical strip")
    if radial_bins<1 or radial_bins>128 or mu_bins<4 or mu_bins>1024:
        raise ValueError("bounded rational mesh resolution")
    if workers not in (1,2,3,4,6):
        raise ValueError("bounded safe worker counts 1,2,3,4,6")
    started=perf_counter()
    rr,_,sha=load_frozen(filename,True)
    a,b=center-delta,center+delta
    if a<=R<=b:raise ValueError("cusp strip cannot be ordinary joint rectangle")
    js=[j for j in range(6) if dyadic(rr[j,0])<=a and b<=dyadic(rr[j,-1])]
    if len(js)!=1:raise ValueError("strip needs exactly one original frozen panel")
    rcuts=[a+(b-a)*F(k,radial_bins) for k in range(radial_bins+1)]
    mucuts=[-F(1)+F(2*k,mu_bins) for k in range(mu_bins+1)]
    jobs=[(str(filename),js[0],ra,rb,tuple(mucuts))
          for ra,rb in zip(rcuts,rcuts[1:])]
    if workers==1:
        rows=list(map(_joint_radial_job,jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers,
                                 mp_context=get_context("forkserver")) as pool:
            rows=list(pool.map(_joint_radial_job,jobs))
    if any(x["source_sha256"]!=sha for x in rows):
        raise ArithmeticError("mixed frozen original source identities")
    sq=sum((F(x["_sq_exact"]) for x in rows),F(0))
    preview=[{"radial":row["radial"],"squared_upper":row["squared_upper"]}
             for row in rows]
    result=ceil_sqrt_fixed(sq,digits)
    return {"schema":SCHEMA,"source_sha256":sha,
            "panel":js[0],"center_a0":str(center),"delta_a0":str(delta),
            "full_3D_broken_L2_upper":result,
            "radial_bins":radial_bins,"angular_mu_bins":mu_bins,
            "cells":radial_bins*mu_bins,"per_radial_tile":preview,
            "workers":workers,"elapsed_s":perf_counter()-started,"physical_rate":None,
            "scope":"rigorous (r,mu) coupled signed interval L2 on specified noncusp strip"}


def _joint_radial_job(job:tuple)->dict:
    """One independently source-verified radial slab, all angular bins."""
    filename,j,ra,rb,mucuts=job
    base=prepare_radial_panel(filename,j)
    radial=_radial_ranges(base,ra,rb)
    subtotal=F(0)
    for ma,mb in zip(mucuts,mucuts[1:]):
        result=certify_cell(base,ra,rb,ma,mb,radial)
        subtotal+=result["_sq_exact"]
    return {"radial":[str(ra),str(rb)],
            "squared_upper":outward_decimal(subtotal,18,True),
            "_sq_exact":str(subtotal),
            "source_sha256":base["source_sha256"]}
