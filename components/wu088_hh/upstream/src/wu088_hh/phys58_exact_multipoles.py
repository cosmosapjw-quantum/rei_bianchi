"""PHYS58 C5-C8 exact elementary off-centre screened S multipole intervals.

Original S=(1+1/s)exp(-2s) for s=|r-0.7 z|, r>=27 Bohr.
For rational r, Legendre coefficient A_n is an exact rational
linear combination of exp(-2(r-R)) and exp(-2(r+R)). Both exponentials
are independently enclosed by rational positive Taylor bounds. All
coefficients here are SOURCE-LOCKED *multiplication*, not DtN.
"""
from __future__ import annotations

from fractions import Fraction as F
from pathlib import Path
from math import isfinite
import mpmath as mp

from .phys58_screen_multipoles import (
 R, B, FROZEN_SHA, original_source_sha_guard, legendre_tail_upper,
 low_to_high_2s_bound, make_certificate,
)

SCHEMA="WU088_HH_PHYS58_C5_C8_ELEMENTARY_MULTIPOLE_INTERVAL_V1"


def _scale(a:list[F],factor:F)->list[F]:
    return [x*factor for x in a]


def _plus(a:list[F],b:list[F])->list[F]:
    return [(a[i] if i<len(a) else F(0))+(b[i] if i<len(b) else F(0)) for i in range(max(len(a),len(b)))]


def _legendre_s_squared_polynomial(n:int,r:F)->list[F]:
    """Exact coefficients for P_n(c-d s^2), in ascending s powers."""
    if type(n) is not int or not 0<=n<=20 or not isinstance(r,F) or not B<=r<=F(60):
        raise ValueError("finite n 0..20, rational r in [27,60]")
    c=(r*r+R*R)/(2*r*R)
    d=F(1)/(2*r*R)
    def mul_z(p:list[F])->list[F]:
        out=[F(0)]*(len(p)+2)
        for i,q in enumerate(p):
            out[i]+=c*q
            out[i+2]-=d*q
        return out
    p0=[F(1)]
    if n==0:return p0
    p1=mul_z(p0)
    if n==1:return p1
    for ell in range(2,n+1):
        pn=_scale(_plus(_scale(mul_z(p1),F(2*ell-1)),_scale(p0,F(1-ell))),F(1,ell))
        p0,p1=p1,pn
    return p1


def _integrating_polynomial(n:int,r:F)->list[F]:
    """Q(s)=(s+1)P_n(c-d s^2), polynomial coefficients in ascending s."""
    p=_legendre_s_squared_polynomial(n,r)
    return _plus(p,[F(0)]+p)


def _primitive_coefficients(n:int,r:F)->list[F]:
    """B(s)=sum_{j=0}^deg Q^(j)(s)/2^(j+1), so derivative(-e^-2s B)=e^-2s Q."""
    q=_integrating_polynomial(n,r)
    poly=[F(0)]*len(q)
    cur=q
    for j in range(len(q)):
        poly=_plus(poly,_scale(cur,F(1,2**(j+1))))
        cur=[(k+1)*cur[k+1] for k in range(len(cur)-1)]
    return poly


def polynomial_eval(p:list[F],s:F)->F:
    y=F(0)
    for x in reversed(p):y=y*s+x
    return y


def rational_exp_minus_interval(x:F,terms:int=320)->tuple[F,F]:
    """e^-x rational enclosure using positive exp(x) Taylor and geometric remainder.

    exp(x) in [T_N, T_N + (x^(N+1)/(N+1)!)/(1-x/(N+2))].
    Thus exp(-x) in [1/T_up,1/T_down].
    """
    if not isinstance(x,F) or x<=0 or type(terms) is not int or terms<128 or terms>700 or F(terms+2)<=x:
        raise ValueError("positive rational x and Taylor order past geometric-convergence threshold")
    curr=F(1)
    acc=F(1)
    for j in range(1,terms+1):
        curr*=x/j
        acc+=curr
    tnext=curr*x/(terms+1)
    upper=acc + tnext/(1-x/F(terms+2))
    assert acc<=upper
    return F(1)/upper,F(1)/acc


def _interval_times_rational(interval:tuple[F,F],a:F)->tuple[F,F]:
    left=a*interval[0]
    right=a*interval[1]
    return (min(left,right),max(left,right))


def exact_legendre_coefficient_interval(n:int,r:F=F(27),terms:int=320)->tuple[F,F]:
    """Exact endpoint-rational interval containing physical A_n(r).

    Avoid uncertified Gaussian quadrature; even exact symbolic cancellation
    is enclosed via outward rational exponential intervals.
    """
    q=_primitive_coefficients(n,r)
    a,b=r-R,r+R
    qa=polynomial_eval(q,a)
    qb=polynomial_eval(q,b)
    Ia=_interval_times_rational(rational_exp_minus_interval(2*a,terms),qa)
    Ib=_interval_times_rational(rational_exp_minus_interval(2*b,terms),-qb)
    f=F(2*n+1,2*r*R)
    lo=f*(Ia[0]+Ib[0]);hi=f*(Ia[1]+Ib[1])
    assert lo<=hi
    return lo,hi


def fraction_to_decimal(a:F,places:int=38,upper:bool=False)->str:
    """Outward rational => fixed decimal. Exact negative floor/ceiling."""
    if not isinstance(a,F) or type(places) is not int or not 0<=places<=100:
        raise ValueError("fraction + decimal places")
    x=a.numerator*(10**places)
    n=-( (-x)//a.denominator) if upper else x//a.denominator
    s='-' if n<0 else ''
    w,d=divmod(abs(n),10**places)
    return s+str(w)+(f'.{d:0{places}d}' if places else '')


def independent_mp_angular_coeff(n:int,r:F=F(27),dps:int=240)->mp.mpf:
    """NONCERTIFYING independent direct physical s(mu) angular quadrature."""
    if not 180<=dps<=450:raise ValueError("high enough dps to resolve rigorous narrow rational intervals")
    with mp.workdps(dps):
        rf=mp.mpf(r.numerator)/r.denominator
        rr=mp.mpf(7)/10
        def f(mu):
            s=mp.sqrt(rf*rf+rr*rr-2*rf*rr*mu)
            return (1+1/s)*mp.exp(-2*s)*mp.legendre(n,mu)
        return mp.mpf(2*n+1)/2*mp.quad(f,[-1,0,1])


def make_interval_rows(frozen:str|Path,ns=tuple(range(10)),r:F=F(27),terms=320,dps=240)->dict:
    actual=original_source_sha_guard(frozen)
    rows=[]
    for n in ns:
        left,right=exact_legendre_coefficient_interval(n,r,terms)
        numerical=independent_mp_angular_coeff(n,r,dps)
        with mp.workdps(dps):
            lmp=mp.mpf(left.numerator)/left.denominator
            rmp=mp.mpf(right.numerator)/right.denominator
            inside=lmp<numerical<rmp
            if not inside:
                raise ArithmeticError("mpmath noncertifying value disagrees with exact-rational exponential enclosure")
            width=(right-left)
            rows.append({
                "n":n,"r_Bohr":str(r),
                "coefficient_interval":{
                    "lower_decimal_floor_45":fraction_to_decimal(left,45,False),
                    "upper_decimal_ceil_45":fraction_to_decimal(right,45,True)
                },
                "mpmath_noncertifying":mp.nstr(numerical,35),
                "highprecision_in_exact_interval":inside,
                "strict_positive_exact_enclosure":left>0,
                "interval_width_decimal_up_45":fraction_to_decimal(width,45,True)
            })
    return {"schema":SCHEMA,"source_sha256":actual,"r_Bohr":str(r),
            "Taylor_exp_order":terms,"independent_mpmath_dps":dps,
            "rows":rows,
            "theorem_provenance":"All exact intervals via rational Taylor remainder, not interval quadrature",
            "noncertifying_numeric":"mpmath angular integration uses independent path; numerical matrix is not a DtN",
            "analytic_transfer_bound_N8_2S":str(2*legendre_tail_upper(8)),
            "HH_R10":"OFF"}


def exact_neighbour_m0_lower(r:F=F(27),terms:int=320)->dict:
    """Rigorous ORIGINAL 2S angular P20,m0 -> Q21,m0 *positive* lower at r27.

    For all n, A_n(r)>0 via strict heat/Laplace kernel positivity.
    For m=0 the Gaunt coefficient is (2l+1)(2l'+1))^1/2
    times the square of real 3j(ell,ellprime,n;0,0,0), so >=0.
    For n=1, g=<21,0|cos theta|20,0>=21/sqrt(41*43)>1/2
    since 41*43=1763<42²=1764.
    Hence <21,0|2S|20,0> > A_1(27) > 6e-24, certified.
    """
    if r!=F(27):raise ValueError("this explicit numerical lower is r=27 Bohr only")
    lo,hi=exact_legendre_coefficient_interval(1,r,terms)
    certified=F(6,10**24)
    if lo<=certified:raise ArithmeticError("original A1 rigorous lower not achieved")
    assert 41*43<42**2
    return {"radius_Bohr":"27","ell_lower":20,"ell_upper":21,"m":0,
            "Gaunt_P1_exact":"21/sqrt(41*43)","Gaunt_P1_strictly_gt_half":True,
            "A1_exact_lower_gt":"6/10^24",
            "physical_V_2S_P20_to_Q21_strict_gt":"6/10^24",
            "proof":"all nonnegative m0 Gaunt coefficients and all A_n(r)>0; n1 term alone > A1",
            "status":"RIGOROUS_NONZERO_ORIGINAL_NONCENTRAL_P_Q_MULTIPLICATION"}


def gaunt_legendre(l:int,lp:int,n:int,m:int):
    """Exact SymPy (not a numerical interval) <Y_lm,P_n Y_l'p>.

    Supported integer angular quantum numbers. m is conserved and
    axisymmetry gives equal ±m blocks.
    """
    from sympy import sqrt, Integer
    from sympy.physics.wigner import wigner_3j
    if any(type(q) is not int for q in (l,lp,n,m)) or min(l,lp,n)<0 or abs(m)>min(l,lp):
        raise ValueError("valid spherical harmonic integers only")
    if n<abs(l-lp) or n>l+lp or (l+lp+n)%2:
        return Integer(0)
    return (-1 if m%2 else 1)*sqrt(Integer((2*l+1)*(2*lp+1))) * wigner_3j(l,lp,n,0,0,0)*wigner_3j(l,lp,n,-m,m,0)


def truncated_original_screen_matrix(ells:tuple[int,...],m:int,r:F=F(27),degree:int=10,terms:int=320,dps:int=75):
    """mpmath numerical matrix from certified exact Legendre coefficient intervals.

    The discrete coefficients are their rational midpoint, but Gaunt sqrt
    and output are floating. The *rigorous angular truncation error* is
    independently 2*legendre_tail_upper(degree) in operator norm, and exact
    coefficient interval widths can be propagated separately.
    """
    if not ells or any(type(l) is not int or l<abs(m) or l>50 for l in ells) or len(set(ells))!=len(ells):
        raise ValueError("distinct valid ell <=50, |m|<=ell")
    if type(degree) is not int or not 0<=degree<=14:
        raise ValueError("bounded polynomial degree")
    with mp.workdps(dps):
        coeff=[]
        max_interval_width=F(0)
        for n in range(degree+1):
            lo,hi=exact_legendre_coefficient_interval(n,r,terms)
            coeff.append(mp.mpf((lo+hi).numerator)/((lo+hi).denominator*2))
            max_interval_width=max(max_interval_width,hi-lo)
        A=mp.matrix(len(ells))
        for i,l in enumerate(ells):
            for j,lp in enumerate(ells):
                total=mp.mpf(0)
                for n in range(degree+1):
                    g=gaunt_legendre(l,lp,n,m)
                    if not g:continue
                    # High-precision numerical evaluation of exactly algebraic g.
                    total+=coeff[n]*mp.mpf(str(g.evalf(dps)))
                A[i,j]=2*total
        return A, max_interval_width


def independent_numpy_angular_matrix(ells:tuple[int,...],m:int,r:float=27.0,nodes:int=192):
    """Noncertifying independent Gauss-Legendre integral for original 2S."""
    import numpy as np
    from scipy.special import gammaln,lpmv
    if not 64<=nodes<=512:raise ValueError("bounded quadrature nodes")
    mu,w=np.polynomial.legendre.leggauss(nodes)
    b=[]
    for l in ells:
        ma=abs(m)
        norm=np.sqrt((2*l+1)/2*np.exp(gammaln(l-ma+1)-gammaln(l+ma+1)))
        b.append(norm*lpmv(ma,l,mu))
    Y=np.asarray(b)
    s=np.sqrt(r*r+float(R)**2-2*r*float(R)*mu)
    screen=2*(1+1/s)*np.exp(-2*s)
    return (Y*(w*screen)[None,:])@Y.T
