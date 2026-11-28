"""PHYS40 C7B: exact arbitrary-r *fully coupled* screened angular shell certificates.

For the original frozen-direct H(1s)+H(1s) model at R=kappa=7/10
and exact rational radius r>0, set a=|r-R|, t=s-a, 0<=t<=w=2*min(r,R).

G(s)=sqrt(4*pi) times the strong transformed PDE residual. The apparent
1/s potential and direction singularities cancel algebraically in N=s*G.
The TRUE angular L2(S²) squared is (2*r*R)^-1 int_a^(r+R) |N(s)|²/s ds.
We build N_N(t) by finite rational Taylor series for E=e^-s,
E²=e^-2s and exp(-E), integrate the ENTIRE complex polynomial norm exactly
with rational/log moments, then add explicit Taylor, coefficient, and
source/normalisation error envelopes. This admits the coalescence s=0
when r=R without artificially smoothing it.

This is one arbitrary fixed-radius SHELL, not a radial continuum certificate
or a physical scattering amplitude.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import factorial
from pathlib import Path
from time import perf_counter
import hashlib

from .phys33_residual import load_frozen,dyadic,ceil_sqrt_fixed
from .phys33_coupled_source import exp_negative_bounds,outward_decimal
from .phys33_cusp_shell import _coeff_at_r,_qrt_sqrt,_cauchy_assumptions
from .phys33_moments import log_ratio_bounds,_floor_sqrt_fixed
from .phys33_angular_kernel import _add,_scale,_mul

R=F(7,10)
K2=F(49,100)
L_MAX=20


def _polyeval(a:list[F],x:F)->F:
    z=F(0)
    for c in reversed(a):z=z*x+c
    return z


def _complex_add(a:list[list[F]],b:list[list[F]])->list[list[F]]:
    return [_add(x,y) for x,y in zip(a,b)]


def _complex_mul(a:list[list[F]],p:list[F])->list[list[F]]:
    return [_mul(x,p) for x in a]


def _complex_scale(a:list[list[F]],c:F)->list[list[F]]:
    return [_scale(x,c) for x in a]


def _expand_legendre(mu:list[F],lmax:int)->list[list[F]]:
    allp=[[F(1)]]
    if lmax==0:return allp
    allp.append(mu)
    for l in range(2,lmax+1):
        allp.append(_add(_scale(_mul(mu,allp[-1]),F(2*l-1,l)),
                         _scale(allp[-2],F(1-l,l))))
    return allp


def _physical_radial_data(filename:str|Path,r:F,side:str|None=None):
    radial,u,identity=load_frozen(filename,True)
    if side not in (None,"left","right"):
        raise ValueError("side is left/right/None")
    candidates=[]
    for j in range(6):
        lo=dyadic(radial[j,0]);hi=dyadic(radial[j,-1])
        if lo<=r<=hi:candidates.append(j)
    if not candidates:
        raise ValueError("chosen exact radius outside frozen six panels")
    if len(candidates)==2:
        j=min(candidates) if side=="left" else max(candidates)
    else:
        j=candidates[0]
        if side=="left" and j==2 and r==R:j=1
        if side=="right" and j==1 and r==R:j=2
    nodes=[dyadic(z) for z in radial[j]]
    modes=[]
    for l in range(L_MAX+1):
        parts=[]
        for arr in (u[l,j].real,u[l,j].imag):
            vals=[dyadic(float(x)) for x in arr]
            parts.append(_coeff_at_r(vals,nodes,j,r))
        modes.append(parts)
    return modes,identity,j


def _center_exp(x:F,terms:int)->tuple[F,F]:
    lo,hi=exp_negative_bounds(x,terms)
    # Enclose exact e^-x but REPRESENT the polynomial coefficient by a
    # small fixed-decimal rational. Without this, the rational denominator
    # of a 192-term exponential midpoint is repeatedly exponentiated in
    # g(t)=exp(-c*exp(-t)) and grows prohibitively. Keep every lost bit
    # rigorously as an outward interval error, never a float heuristic.
    mid=(lo+hi)/2
    decimal_scale=10**48
    nearest=(mid.numerator*decimal_scale + mid.denominator//2)//mid.denominator
    center=F(nearest,decimal_scale)
    err=max(abs(lo-center),abs(hi-center))
    return center,err


def _series_E(c:F,n:int,power:int=1)->list[F]:
    return [c*F((-power)**k,factorial(k)) for k in range(n+1)]


def _g_series(a:F,n:int,terms:int)->tuple[list[F],F]:
    if not _cauchy_assumptions():
        raise ArithmeticError("complex Cauchy assumption is not certified")
    c,ec=_center_exp(a,terms)
    g0,eg0=_center_exp(c,terms)
    h=[F(1)]
    for k in range(1,n+1):
        accum=sum((h[k-1-j]*F((-1)**j,factorial(j))
                   for j in range(k)),F(0))
        h.append(c*accum/k)
    g=[g0*v for v in h]
    w=2*min(a+R,R) # conservative max <=2R; caller overrides exact w
    return g, ec+eg0*sum((abs(q)*(2*R)**k for k,q in enumerate(h)),F(0))


def _series_bundle(a:F,w:F,n:int,terms:int)->dict:
    c,ec=_center_exp(a,terms)
    c2,ec2=_center_exp(2*a,terms)
    e=_series_E(c,n)
    e2=_series_E(c2,n,power=2)
    g,gerr_base=_g_series(a,n,terms)
    # Bound Taylor remainder on the real interval [0,w]:
    # exp(-p t) derivatives <=p^n for t>=0.
    e_tail=w**(n+1)/factorial(n+1)
    e2_tail=(2*w)**(n+1)/factorial(n+1)
    if not F(0)<=w<=2*R<F(3):
        raise ValueError("angular s-panel width exceeds Cauchy radius")
    cauchy=F(2**31)*(w/F(3))**(n+1)/(1-w/F(3))
    # The fixed g coefficient recurrence was centered at e^-a; its errors
    # depend only on exp(-a) midpoint and g(0)=exp(-c).
    eg=gerr_base+cauchy
    # gerr_base includes ec and eg0*sum(...), so avoid double ec.
    if a==0:
        assert ec==0 and ec2==0
        e_over_s=w**n/factorial(n+1)
        e2_over_s=F(2)**(n+1)*w**n/factorial(n+1)
    else:
        e_over_s=(ec+e_tail)/a
        e2_over_s=(ec2+e2_tail)/a
    return {"E":e,"E2":e2,"g":g,
            "epsilon_E":ec+e_tail,
            "epsilon_E2":ec2+e2_tail,
            "epsilon_E_over_s":e_over_s,
            "epsilon_E2_over_s":e2_over_s,
            "epsilon_g":eg}


def _exact_rational_log_integral(poly:list[F],a:F,w:F,
                                 log_terms:int)->tuple[F,F]:
    """Exact rational combination A+B log((a+w)/a) of integral poly(t)/(a+t)."""
    if a<0 or w<=0:
        raise ValueError("ordered s interval required")
    if a==0:
        if poly[0] !=0:
            raise ArithmeticError("n(s=0) not zero, cannot cancel cusp")
        result=sum((c*w**k/k for k,c in enumerate(poly) if k>0),F(0))
        return result,result
    L,H=log_ratio_bounds(a,a+w,log_terms)
    A,B=F(0),F(1)
    ac,bc=F(0),F(0)
    for k,c in enumerate(poly):
        ac+=c*A;bc+=c*B
        if k+1<len(poly):
            A,B=w**(k+1)/F(k+1)-a*A,-a*B
    if bc>=0:return ac+bc*L,ac+bc*H
    return ac+bc*H,ac+bc*L


def _rational_angular_shell(filename:str|Path,r:F,side:str|None,
                             order:int,terms:int,digits:int)->dict:
    if not isinstance(r,F) or r<=0 or order<32 or order>144 or terms<max(128,order):
        raise ValueError("radius exact Fraction positive, order32..144 and terms>=order")
    tic=perf_counter()
    modes,identity,panel=_physical_radial_data(filename,r,side)
    a=abs(r-R);b=r+R;w=b-a
    mu=[(r*r+R*R-a*a)/(2*r*R),-a/(r*R),-F(1,2*r*R)]
    polys=_expand_legendre(mu,L_MAX)
    s_poly=[a,F(1)]
    # H=(r-Rmu)C-(R/r)T, with T=l(P_(l-1)-mu P_l) multiplied by u_l/r.
    r_minus_mu=_add([r],_scale(mu,-R))
    A=[[F(0)],[F(0)]]
    B=[[F(0)],[F(0)]]
    H=[[F(0)],[F(0)]]
    # Mode-normalisation envelope, computed in the physical [-1,1] basis.
    max_A,max_B,max_C,tweighted=F(0),F(0),F(0),F(0)
    dev_A,dev_B,dev_C,dev_T=F(0),F(0),F(0),F(0)
    for l,parts in enumerate(modes):
        (vr,v1,v2),(vi,i1,i2)=parts
        v=(vr,vi)
        first=(v1,i1)
        sec=(v2,i2)
        lap=tuple(sec[j]+(K2+2/r-F(l*(l+1))/r**2)*v[j] for j in (0,1))
        aa=tuple(x/r for x in lap)
        bb=tuple(x/r for x in v)
        cc=tuple(first[j]/r-v[j]/r**2 for j in (0,1))
        P=polys[l]
        prev=polys[l-1] if l>0 else [F(0)]
        T=_scale(_add(prev,_scale(_mul(mu,P),-1)),F(l))
        alpha_lo,alpha_hi=_qrt_sqrt(2*l+1)
        alpha=(alpha_lo+alpha_hi)/2
        err=(alpha_hi-alpha_lo)/2
        hp=_add(_mul(r_minus_mu,P),_scale(T,-R/r))
        for component in range(2):
            A[component]=_add(A[component],_scale(P,alpha*aa[component]))
            B[component]=_add(B[component],_scale(P,alpha*bb[component]))
            H[component]=_add(H[component],
                    _scale(_add(_mul(r_minus_mu,_scale(P,cc[component])),
                                _scale(T,-R/r*bb[component])),alpha))
        absA=abs(aa[0])+abs(aa[1])
        absB=abs(bb[0])+abs(bb[1])
        absC=abs(cc[0])+abs(cc[1])
        max_A+=alpha_hi*absA;max_B+=alpha_hi*absB;max_C+=alpha_hi*absC
        tweighted+=alpha_hi*absB*l*(l+1)/2
        dev_A+=err*absA;dev_B+=err*absB;dev_C+=err*absC
        dev_T+=err*absB*l*(l+1)/2
    # |(r-R mu)/s|<=1; |1-mu²|/s <= b³/(4r²R²).
    angular_T_factor=b**3/(4*r*r*R*R)
    Hdivmax=max_C+(R/r)*tweighted*angular_T_factor
    dev_Hdiv=dev_C+(R/r)*dev_T*angular_T_factor
    exp=_series_bundle(a,w,order,terms)
    e1,e2,g=exp["E"],exp["E2"],exp["g"]
    radial_center,radial_err=_center_exp(r,terms)
    src=2*(1+K2)*radial_center
    N=_complex_mul(A,s_poly)
    N=_complex_add(N,_complex_scale(_complex_mul(H,e1),F(-2)))
    N=_complex_add(N,_complex_scale(_complex_mul(B,_add(e1,_scale(e2,-1))),F(-2)))
    N=_complex_add(N,_complex_mul(B,_mul(s_poly,e1)))
    N=_complex_add(N,_complex_scale(_complex_mul(B,_mul(s_poly,e2)),F(3)))
    N[0]=_add(N[0],_scale(_mul(s_poly,g),-src))
    sq=[F(0)]
    for t in N:sq=_add(sq,_mul(t,t))
    pl,ph=_exact_rational_log_integral(sq,a,w,128)
    if not F(0)<=pl<=ph:
        raise ArithmeticError("nonnegative integrated polynomial physical norm required")
    pl/=2*r*R;ph/=2*r*R
    polynomial_upper=F(ceil_sqrt_fixed(ph,digits))
    polynomial_lower=F(_floor_sqrt_fixed(pl,digits))
    # Uniform error upper on G. Mode coefficients are exact except bounded
    # rational sqrt(2ell+1) rounding.
    eerr=exp["epsilon_E"]
    e2err=exp["epsilon_E2"]
    gerr=exp["epsilon_g"]
    residual_norm_err = (
        dev_A+2*dev_Hdiv+2*dev_B+
        2*eerr*Hdivmax+
        (2*exp["epsilon_E_over_s"]+2*exp["epsilon_E2_over_s"]+
         eerr+3*e2err)*max_B+
        2*(1+K2)*gerr + 2*(1+K2)*radial_err*(1+gerr)
    )
    true_low=max(F(0),polynomial_lower-residual_norm_err)
    true_high=polynomial_upper+residual_norm_err
    return {
        "schema":"WU088_HH_PHYS40_FULL_COUPLED_FIXED_RADIUS_SHELL_V1",
        "source_sha256":identity,"physical_r_a0":str(r),
        "physical_s_interval":[str(a),str(b)],
        "chosen_panel":panel,"one_sided_choice":side,
        "full_original_lambda":"1","R_and_kappa":"7/10",
        "Taylor_order":order,"exp_positive_terms":terms,
        "angular_norm_L2_lower":outward_decimal(true_low,digits,False),
        "angular_norm_L2_upper":outward_decimal(true_high,digits,True),
        "exact_polynomial_norm_upper":outward_decimal(polynomial_upper,digits,True),
        "rounding_and_Taylor_error_upper":outward_decimal(residual_norm_err,digits,True),
        "degree_numerator":max(len(p) for p in N)-1,
        "complex_norm_integral":"(2rR)^-1 int_a^b |N(s)|²/s ds exact Fraction + directed logarithm",
        "scientific_scope":"rigorous full coupled screened source+derivative+potential ANGULAR residual at one radius only",
        "elapsed_s":perf_counter()-tic,
        "not_certified":["whole radial 3D integral","origin/exterior and interface inverse",
                         "continuous low Schur/dual","scattering intensity or thermal rate"]
    }


def full_coupled_angular_shell(filename:str|Path,r:F,side:str|None=None,
                               order:int=96,exp_terms:int=192,digits:int=12)->dict:
    return _rational_angular_shell(filename,r,side,order,exp_terms,digits)
