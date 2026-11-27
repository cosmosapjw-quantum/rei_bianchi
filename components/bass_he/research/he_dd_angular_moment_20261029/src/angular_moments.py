"""Conditional EXFOR M0475002 angular second-moment enclosure.

Assumes the PR105 nonnegative |f'|<=L [nb/sr/degree], identical-deuteron
theta -> pi-theta symmetry, azimuthal averaging and coordinatewise ERR-S
sensitivity boxes.  Neither a physical photon history nor event multiplicity
is inferred.  Numerical transcendental endpoints are NOT outward-certified.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from decimal import Decimal
from typing import Iterable

# Pinned EXFOR IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871
SOURCE_GIT_BLOB = "c49433293921dbb012d7f1b0387745732a598efa"
SOURCE_SHA256 = "b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f"
SOURCE_REACTION = "(2-HE-4(G,D)1-H-2,,DA)"
M = F("3727.3794118")    # M_alpha*c**2 [MeV] frozen in PR104
m = F("1875.61294500")   # m_D*c**2 [MeV] frozen in PR104
SOURCE_330 = (
    (F(46), F("0.14"), F("0.03")),
    (F(61), F("0.16"), F("0.05")),
    (F(73), F("0.07"), F("0.05")),
    (F(87), F("0.19"), F("0.05")),
)
PRODUCTION_GATE = {
    "kappa": None, "R_event": None, "physical_activation": False,
    "L4": False, "production": "HOLD"
}

def Q(x):
    if isinstance(x, (float, bool)) or not isinstance(x, (int, F, str, Decimal)):
        raise TypeError("Exact integer/Fraction/str/Decimal required; float or bool rejected")
    return F(x)

def source_rows(rows=SOURCE_330):
    rows = tuple(tuple(Q(v) for v in row) for row in rows)
    if len(rows) != 4 or tuple(x[0] for x in rows) != (46,61,73,87):
        raise ValueError("Wrong 330 MeV source-row identity or angles")
    if any(da <= 0 or err < 0 or err > da for _, da, err in rows):
        raise ValueError("Source data must have nonnegative lower endpoints")
    return rows

def source_limits(rows=SOURCE_330):
    return tuple((t,max(F(0),da-er),da+er) for t,da,er in source_rows(rows))

def min_L(rows=SOURCE_330):
    p=source_limits(rows)
    return max([F(0)] + [
        max(F(0),p[i][1]-p[j][2])/abs(p[i][0]-p[j][0])
        for i in range(4) for j in range(4) if i != j
    ])

def segments(L, kind="lower", rows=SOURCE_330):
    """Exact Fraction piecewise-affine pointwise f_-/f_+ on theta in [0,90] deg."""
    L=Q(L)
    if L<min_L(rows): raise ValueError("L below source-feasibility lower bound")
    if kind not in ("lower","upper"):raise ValueError("Expected lower/upper")
    p=source_limits(rows)
    knots=sorted(set([F(0),F(90)]+[t for t,_,_ in p]))
    out=[]
    for t0,t1 in zip(knots[:-1],knots[1:]):
        mid=(t0+t1)/2
        lines=[(F(0),F(0))] if kind=="lower" else []
        for t,lo,hi in p:
            sign=1 if mid>=t else -1
            if kind=="lower":lines.append((lo+L*sign*t, -L*sign))
            else: lines.append((hi-L*sign*t, L*sign))
        cuts=set([t0,t1])
        for i,(a,b) in enumerate(lines):
            for c,d in lines[i+1:]:
                if b!=d:
                    z=(c-a)/(b-d)
                    if t0<z<t1:cuts.add(z)
        cut=sorted(cuts)
        for x,y in zip(cut[:-1],cut[1:]):
            tm=(x+y)/2
            a,b=(max if kind=="lower" else min)(lines,key=lambda u:u[0]+u[1]*tm)
            if out and out[-1][1]==x and out[-1][2:]==(a,b):
                out[-1]=(out[-1][0],y,a,b)
            else:
                out.append((x,y,a,b))
    if not out or out[0][0]!=0 or out[-1][1]!=90:
        raise ArithmeticError("incomplete envelope partition")
    return tuple(out)

def value_at(segs,theta):
    x=Q(theta)
    if x<0 or x>90:raise ValueError("theta domain")
    for lo,hi,a,b in segs:
        if lo<=x<=hi:return a+b*x
    raise AssertionError("partition gap")

def delta2(E):
    E=Q(E)
    s=M*M+2*M*E
    if s < 4*m*m:raise ValueError("below threshold")
    return E*E*(s-4*m*m)/(4*s)

def K0(E):
    E=Q(E)
    if E < (4*m*m-M*M)/(2*M):raise ValueError("below threshold")
    return (M+E-2*m)/2

def _mp_fraction(v):
    import mpmath as mp
    return mp.mpf(v.numerator)/v.denominator

def segment_integral(segment, left=None, right=None, moment=0):
    """Exact-affine f times sin(theta) or cos^2(theta)sin(theta) analytic primitive.

    Angle endpoints are exact degrees, 0<=moment<=1.
    Caller must establish mp.workdps; no outward rounding assertion.
    """
    import mpmath as mp
    lo,hi,a,b=segment
    l=lo if left is None else left
    r=hi if right is None else right
    if not (_mp_fraction(lo)<=(_mp_fraction(l) if isinstance(l,F) else mp.mpf(l)) <=(_mp_fraction(r) if isinstance(r,F) else mp.mpf(r))<=_mp_fraction(hi)):
        raise ValueError("bad subsegment")
    if not (moment==0 or moment==1):raise ValueError("moment must be 0 or 1")
    k=mp.pi/180
    A,B=_mp_fraction(a),_mp_fraction(b)/k
    def primitive(x):
        z=k*(x if not isinstance(x,F) else _mp_fraction(x))
        sin,cos=mp.sin(z),mp.cos(z)
        if moment==0:
            return -A*cos+B*(-z*cos+sin)
        return -A*cos**3/3+B*(-z*cos**3/3+sin/3-sin**3/9)
    return primitive(r)-primitive(l)

def integrals(L, kind, dps=60):
    """D=int_0^(pi/2) f sin(theta) dtheta; N=int f cos²theta sin(theta)."""
    import mpmath as mp
    if type(dps)!=int or not 35<=dps<=150:raise ValueError("precision")
    with mp.workdps(dps):
        segs=segments(L,kind)
        D=mp.fsum(segment_integral(z,moment=0) for z in segs)
        N=mp.fsum(segment_integral(z,moment=1) for z in segs)
        return D,N

def _outer_signed(t, L, bound, dps=60):
    """Unconstrained selection of pointwise bounds gives a VALID OUTER ratio enclosure.

    The selected patched function is not presumed Lipschitz/feasible.
    """
    import mpmath as mp
    with mp.workdps(dps):
        tt=mp.mpf(t)
        if not 0<=tt<=1:raise ValueError("b must be in [0,1]")
        turn=mp.acos(mp.sqrt(tt))*180/mp.pi
        lp=segments(L,"lower")
        up=segments(L,"upper")
        acc=mp.mpf(0)
        for kind,segs in [("lower",lp),("upper",up)]:
            for seg in segs:
                lo,hi,_,_=seg
                x,y=_mp_fraction(lo),_mp_fraction(hi)
                mid=mp.mpf((x+y)/2)
                # signed (cos²-t) nonnegative to the left of turn
                use_pos = (kind=="upper") if bound=="upper" else (kind=="lower")
                if x<min(y,turn) and use_pos:
                    aa,bb=x,min(y,turn)
                    acc+=segment_integral(seg,aa,bb,1)-tt*segment_integral(seg,aa,bb,0)
                if max(x,turn)<y and not use_pos:
                    aa,bb=max(x,turn),y
                    acc+=segment_integral(seg,aa,bb,1)-tt*segment_integral(seg,aa,bb,0)
        return +acc

def outer_interval(L, dps=60, iterations=100):
    """Mathematically valid conditional outer b bounds, endpoints numeric approx."""
    import mpmath as mp
    L=Q(L)
    if L<min_L():raise ValueError("infeasible")
    if type(iterations)!=int or not 30<=iterations<=500:raise ValueError("iterations")
    with mp.workdps(dps):
        bounds=[]
        for bound in ("lower","upper"):
            a,b=mp.mpf(0),mp.mpf(1)
            for _ in range(iterations):
                mid=(a+b)/2
                res=_outer_signed(mid,L,bound,dps)
                if res>=0:a=mid
                else:b=mid
            bounds.append((a+b)/2)
        lo,hi=bounds
        if not (0<=lo<=hi<=1):raise ArithmeticError("invalid enclosure")
        dlo,nlo=integrals(L,"lower",dps)
        dhi,nhi=integrals(L,"upper",dps)
        return {
            "L":str(L),
            "b_outer_lower":mp.nstr(lo,dps-15),
            "b_outer_upper":mp.nstr(hi,dps-15),
            "b_feasible_lower_envelope":mp.nstr(nlo/dlo,dps-15),
            "b_feasible_upper_envelope":mp.nstr(nhi/dhi,dps-15),
            "I_min_nb":mp.nstr(4*mp.pi*dlo,dps-15),
            "I_max_nb":mp.nstr(4*mp.pi*dhi,dps-15),
            "variance_outer_lower_MeV2":mp.nstr(_mp_fraction(delta2(330))*lo,dps-15),
            "variance_outer_upper_MeV2":mp.nstr(_mp_fraction(delta2(330))*hi,dps-15),
            "kappa":None,"R_event":None,"thermal_deposition_rate":None,
            "numeric_rounding_certified":False,
            "claim":"conditional outer enclosure; not sharp; not a joint confidence interval"
        }

def manufactured_quadratic_deposition(E, mu_weights, Kstar):
    """For manufactured h(K)=K²/K*, outputs pair deposited energy proxy only.

    K* must cover the largest possible daughter energy, never physical D stopping.
    """
    import mpmath as mp
    star=Q(Kstar);e=Q(E)
    if star<=0 or star*star<0:raise ValueError("invalid scale")
    with mp.workdps(65):
        k0=_mp_fraction(K0(e));d2=_mp_fraction(delta2(e))
        if _mp_fraction(star)<k0+mp.sqrt(d2):raise ValueError("scale below physical K_max")
        atoms=tuple((Q(u),Q(w)) for u,w in mu_weights)
        if not atoms or any(w<0 or abs(u)>1 for u,w in atoms):raise ValueError("bad atoms")
        wt=sum((w for _,w in atoms),F())
        if wt<=0:raise ValueError("zero weights")
        b=sum((w*u*u for u,w in atoms),F())/wt
        val=2*(k0*k0+d2*_mp_fraction(b))/_mp_fraction(star)
        return {
            "pair_manufactured_deposit_MeV":mp.nstr(val,48),
            "birth_energy_MeV":str(2*K0(e)),
            "b_exact":str(b),
            "R_event":None,"physical_deposition_rate":None,
            "physical_activation":False
        }
