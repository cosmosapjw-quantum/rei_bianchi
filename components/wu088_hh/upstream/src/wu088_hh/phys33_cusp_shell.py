"""C7B proof-of-concept: exact angular cusp-shell polynomial certificate at r=R.

At r=R=7/10, x=s/(2R) in [0,1] and mu=1-2*x*x.
Every Y_l0 and angular derivative is an exact polynomial in x; the apparent
1/s factor cancels analytically. Polynomial E=e^(-2Rx), q=(1-E)/(2Rx)
and g=exp(-E) are approximated by rational Taylor polynomials with a
separate provable UNIFORM Cauchy/Taylor remainder. Each input coefficient is
an exact rational extrapolation of the archived IEEE binary64 Chebyshev nodes.

This certifies *one physical spherical shell* (two one-sided radial polynomial
traces), NOT the full broken radial L2 norm, origin, interface or rate.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb, factorial, isqrt
from pathlib import Path
from time import perf_counter
import hashlib

from .phys33_residual import (load_frozen, interpolants, reconstruct,
                               derivative, value, mul, add, scale,
                               ceil_sqrt_fixed)
from .phys33_coupled_source import exp_negative_bounds, outward_decimal

R=F(7,10)
S=2*R
K2=F(49,100)
QDEC=10**64


def abs_complex(pair:tuple[F,F])->F:
    return abs(pair[0])+abs(pair[1])


def _qrt_sqrt(m:int)->tuple[F,F]:
    if m<0:raise ValueError("expected nonnegative radicand")
    n=isqrt(m*QDEC*QDEC)
    return F(n,QDEC), F(n+1,QDEC)


def _quantize(lo:F,hi:F)->tuple[F,F]:
    if not lo<=hi:raise ValueError("inverted input bracket")
    center=(lo+hi)/2
    scaled=center.numerator*QDEC//center.denominator
    z=F(scaled,QDEC)
    err=max(abs(lo-z),abs(hi-z))
    return z,err


def _legendre_cusp(l:int)->list[F]:
    """P_l(1-2x²)=sum_k (-1)^k C(l,k) C(l+k,k) x^(2k)."""
    out=[F(0)]*(2*l+1)
    for k in range(l+1):
        out[2*k]=F((-1)**k*comb(l,k)*comb(l+k,k))
    return out


def _coeff_at_r(arr:list[F],nodes:list[F],j:int,r:F)->tuple[F,F,F]:
    # Returns (value,dr,d²r) at the mathematical r=7/10, even though
    # the stored binary64 shared endpoint is a neighbouring exact dyadic.
    lo,hi=nodes[0],nodes[-1]
    mid,half=(lo+hi)/2,(hi-lo)/2
    absc=[(z-mid)/half for z in nodes]
    basis=interpolants(absc)
    poly=[sum((w*val for w,val in zip(arr,bcol)),F(0))
          for bcol in zip(*basis)]
    xx=(r-mid)/half
    v=value(poly,xx)
    p1=scale(derivative(poly),1/half)
    p2=scale(derivative(p1),1/half)
    return v,value(p1,xx),value(p2,xx)


def _read_shell(filename:str|Path,side:str)->tuple[list,list,list,list,dict]:
    if side not in ("left","right"):
        raise ValueError("side must specify one frozen radial trace")
    radial,u,sha=load_frozen(filename,True)
    j=1 if side=="left" else 2
    nodes=[F(*float(v).as_integer_ratio()) for v in radial[j]]
    lp=[_legendre_cusp(l) for l in range(21)]
    a,b,c,t=[([F(0)],[F(0)]) for _ in range(4)]
    modes={"A":[],"B":[],"C":[],"T":[]}
    mags={"A":F(0),"B":F(0),"H":F(0)}
    deltas={"A":F(0),"B":F(0),"H":F(0)}
    for ell in range(21):
        vals=[]
        for typ in (0,1):
            arr=[F(*float(v).as_integer_ratio())
                 for v in (u[ell,j].real if typ==0 else u[ell,j].imag)]
            vals.append(_coeff_at_r(arr,nodes,j,R))
        v=(vals[0][0],vals[1][0])
        dv=(vals[0][1],vals[1][1])
        d2v=(vals[0][2],vals[1][2])
        dl=tuple(d2v[i]+(K2+2/R-F(ell*(ell+1))/R**2)*v[i] for i in (0,1))
        bb=tuple(z/R for z in v)
        cc=tuple(dv[i]/R-v[i]/R**2 for i in (0,1))
        aa=tuple(z/R for z in dl)
        P=lp[ell]
        T=scale(add(lp[ell-1] if ell>0 else [F(0)],
                    scale(mul([F(1),F(0),F(-2)],P),F(-1))),
                F(ell))
        assert T[0]==0 and (ell==0 or T[1]==0)
        s0,s1=_qrt_sqrt(2*ell+1)
        z=(s0+s1)/2
        de=(s1-s0)/2
        for k,ve in (("A",aa),("B",bb),("C",cc),("T",bb)):
            vec= P if k!="T" else T
            modes[k].append([scale(vec,z*ve[0]),scale(vec,z*ve[1])])
        mags["A"]+=s1*abs_complex(aa)
        mags["B"]+=s1*abs_complex(bb)
        mags["H"]+=s1*(abs_complex(cc)+F(ell*(ell+1))/R*abs_complex(bb))
        deltas["A"]+=de*abs_complex(aa)
        deltas["B"]+=de*abs_complex(bb)
        deltas["H"]+=de*(abs_complex(cc)+F(ell*(ell+1))/R*abs_complex(bb))
    def total(key):
        part=modes[key]
        re=[F(0)];im=[F(0)]
        for zr,zi in part:
            re=add(re,zr);im=add(im,zi)
        return re,im
    AA,BB,CC,TT=[total(x) for x in ("A","B","C","T")]
    # H = x*C - T/(2Rx); since T(0)=0 exactly, division is polynomial.
    hh=[]
    for ce,te in zip(CC,TT):
        assert te[0]==0
        hh.append(add([F(0)]+ce,scale(te[1:],-1/S)))
    return AA,BB,hh,mags,{"source_sha256":sha,"side":side,"coefficient_max":mags,
                           "sqrt_coefficient_error":deltas,"radial_panel":j}


def _exp_series(n:int)->list[F]:
    return [F((-1)**k*S**k,factorial(k)) for k in range(n+1)]


def _q_series(n:int)->list[F]:
    return [F((-1)**k*S**k,factorial(k+1)) for k in range(n)]


@__import__("functools").lru_cache(maxsize=1)
def _cauchy_assumptions()->bool:
    """Prove by positive rational Taylor tails that e^3<21 and e^21<2^31."""
    def exp_plus_upper(x:int,n:int=128)->F:
        t=F(1); sm=t
        for k in range(1,n+1):
            t*=F(x,k);sm+=t
        first=t*F(x,n+1)
        tail=first/(1-F(x,n+2))
        return sm+tail
    return exp_plus_upper(3)<21 and exp_plus_upper(21)<2**31


def _g_series(n:int)->tuple[list[F],F]:
    # G(s)=e^{-1} H(s); H'(s)=e^{-s}H(s), H(0)=1.
    if not _cauchy_assumptions():
        raise ArithmeticError("unproven complex Cauchy majorant")
    h=[F(1)]
    for k in range(1,n+1):
        total=sum((F((-1)**j,factorial(j))*h[k-1-j]
                   for j in range(k)),F(0))
        h.append(total/k)
    elo,ehi=exp_negative_bounds(F(1),128)
    g0,e0=_quantize(elo,ehi)
    poly=[g0*h[k]*S**k for k in range(n+1)]
    major=sum((abs(h[k])*S**k for k in range(n+1)),F(0))
    # Cauchy circle |s|=3. |e^-exp(-s)| <= exp(e^3) < 2^31:
    # exp(3)<21, exp(21)<2^31, each independently verified by rational Taylor.
    cauchy=F(2**31)*(S/F(3))**(n+1)/(1-S/F(3))
    return poly,cauchy+e0*major


def _multiply_complex_real(v:list[list[F]],p:list[F])->list[list[F]]:
    return [mul(component,p) for component in v]


def _add_complex(a:list[list[F]],b:list[list[F]])->list[list[F]]:
    return [add(u,v) for u,v in zip(a,b)]


def _scale_complex(v:list[list[F]],c:F)->list[list[F]]:
    return [scale(a,c) for a in v]


def _real_complex(poly:list[F])->list[list[F]]:
    return [poly,[F(0)]]


def _shell_poly(filename:str|Path,side:str,n:int)->tuple[list[list[F]],F,dict]:
    if n<40 or n>180:
        raise ValueError("Taylor order must be in [40,180]")
    A,B,H,mag,identity=_read_shell(filename,side)
    E=_exp_series(n)
    Q=_q_series(n)
    U=add(add(mul(E,Q),scale(E,F(-1,2))),
          scale(mul(E,E),F(-3,2)))
    g,eg=_g_series(n)
    expRlo,expRhi=exp_negative_bounds(R,128)
    expR,errR=_quantize(expRlo,expRhi)
    C0=2*(1+K2)*expR
    P=_add_complex(A,_scale_complex(_multiply_complex_real(H,E),F(-2)))
    P=_add_complex(P,_scale_complex(_multiply_complex_real(B,U),F(-2)))
    P=_add_complex(P,_real_complex(scale(g,-C0)))
    epsE=S**(n+1)/factorial(n+1)
    epsQ=S**n/factorial(n+1)
    epsU=5*epsE+2*epsQ  # requires epsE,epsQ<=1, both true for n>=40
    error=identity["sqrt_coefficient_error"]["A"]+2*identity["sqrt_coefficient_error"]["H"]+2*identity["sqrt_coefficient_error"]["B"]
    error+=2*epsE*mag["H"]+2*epsU*mag["B"]
    error+=2*(1+K2)*eg+4*(1+K2)*errR
    assert error>0
    identity.update({"taylor_order":n,"poly_degree":max(map(len,P))-1})
    return P,error,identity


def shell_certificate(filename:str|Path,side:str,n:int=112,digits:int=12)->dict:
    tic=perf_counter()
    P,error,meta=_shell_poly(filename,side,n)
    # Exact rational 2 int_0^1 x |P|² dx
    square=F(0)
    for component in P:
        for i,ai in enumerate(component):
            if not ai:continue
            for j,aj in enumerate(component):
                if not aj:continue
                square+=F(2)*ai*aj/(i+j+2)
    if square<0:
        raise ArithmeticError("exact polynomial angular square must be nonnegative")
    central=ceil_sqrt_fixed(square,digits)
    final=outward_decimal(F(central)+error,digits,True)
    return {"schema":"WU088_HH_PHYS37_CUSP_SHELL_C7B_V1",
            **{k:v for k,v in meta.items() if k in ("source_sha256","side","radial_panel","taylor_order","poly_degree")},
            "physical_shell_r_a0":"7/10","physical_cusp":"s=0 included at mu=1",
            "angular_measure":"2 integral_0^1 x abs(sqrt(4pi)*residual(x))^2 dx",
            "exact_polynomial_angular_norm_upper":central,
            "rigorous_uniform_angular_polynomial_error_upper":outward_decimal(error,digits,True),
            "certified_true_shell_L2_upper":final,
            "elapsed_s":perf_counter()-tic,
            "status":"RIGOROUS_FIXED_RADIUS_SHELL_ONLY",
            "unresolved":["radial whole-cell integral","global origin and interfaces","outgoing boundary/low inverse","full scattering intensity and thermal rate"]}
