"""Frozen nominal equal-sharing PWBE diagonal and weighted minimax, no old suites.

Source errors are numerical weights, not deterministic bounds or p-value inputs.
"""
from fractions import Fraction
import json
import math
import numbers
from pathlib import Path

E=Fraction(125,17)
E0=Fraction(517,34)
K2=Fraction(250,17)
R2=Fraction(517,17)
SELECTED_ANGLES=(32,34,36,38,40,42,43,44,50,52,54,56,60)
EXCLUDED_ANGLES=(45,46,48)


def real(x,name):
    if isinstance(x,bool) or not isinstance(x,numbers.Real):raise ValueError(name+' must be finite real')
    try:x=float(x)
    except (ValueError,OverflowError):raise ValueError(name+' nonfinite') from None
    if not math.isfinite(x):raise ValueError(name+' nonfinite')
    return x


def decimal(s,name):
    if not isinstance(s,str):raise ValueError(name+' must retain source decimal string')
    try:x=Fraction(s)
    except (ValueError,ZeroDivisionError):raise ValueError(name+' invalid decimal') from None
    real(x,name)
    return x


def load_source(path=None):
    path=Path(path) if path else Path(__file__).resolve().parents[1]/'source/SELECTED_INPUT.json'
    obj=json.loads(path.read_text());rows=obj['rows'];excluded=obj['excluded_rows']
    if tuple(decimal(r['theta_deg'],'theta') for r in rows)!=SELECTED_ANGLES:raise ValueError('fixed13sourceangle selection required')
    if tuple(decimal(r['theta_deg'],'excludedtheta') for r in excluded)!=EXCLUDED_ANGLES:raise ValueError('fixed3exclusions required')
    if any(r['y'] is not None or r['s'] is not None for r in excluded):raise ValueError('excluded numerical fit cells must be null')
    out=[]
    for r in rows:
        theta=decimal(r['theta_deg'],'theta');y=decimal(r['y'],'y');s=decimal(r['s'],'s')
        if y<0 or s<=0:raise ValueError('source requires y>=0,s>0')
        out.append({'theta_deg':theta,'y':y,'s':s,'printed':r['printed']})
    if not any(r['y']>0 for r in out):raise ValueError('positive y required')
    return obj,out


def diagonal(theta_deg):
    theta=real(theta_deg,'theta_deg')
    if not 32<=theta<=60:raise ValueError('frozen diagonal domain is32..60degrees')
    try:
        k=math.sqrt(float(K2));r=math.sqrt(float(R2));mu=math.cos(math.radians(theta))
        z=r-2*k*mu;gap=float(K2)+r*z
        if not gap>0:raise ValueError('positive momentum transfer required')
        h=(1/(1+float(K2)))**2;t=(1/(1+z*z))**2
        d=(t-h)/gap;K=(32/math.pi**2)*(float(K2)/r)*d*d
        result={'theta_deg':theta,'mu':mu,'z':z,'q2':z*z,'Delta2':gap,'d':d,'x':d,'triplet_reduced':0.0,'K':K}
        if not all(math.isfinite(x) for x in result.values()) or K<=0:raise ValueError('nonpositive/nonfinite model arithmetic')
        return result
    except (OverflowError,ZeroDivisionError):raise ValueError('model overflow') from None


def shape(theta_deg):return diagonal(theta_deg)['K']/diagonal(44)['K']


def validate_fit(f,y,s):
    if not len(f)==len(y)==len(s) or not len(f):raise ValueError('nonempty equal lengths required')
    f=[real(x,'f') for x in f];y=[real(x,'y') for x in y];s=[real(x,'s') for x in s]
    if any(x<=0 for x in f) or any(x<0 for x in y) or any(x<=0 for x in s) or not any(x>0 for x in y):raise ValueError('require f>0,s>0,y>=0 and at leastonepositive y')
    return f,y,s


def feasible_interval(f,y,s,kappa):
    f,y,s=validate_fit(f,y,s);kappa=real(kappa,'kappa')
    if kappa<0:raise ValueError('kappa>=0 required')
    lower=max([0.0]+[(a-kappa*b)/c for c,a,b in zip(f,y,s)])
    upper=min((a+kappa*b)/c for c,a,b in zip(f,y,s))
    if not math.isfinite(lower) or not math.isfinite(upper):raise ValueError('interval overflow')
    return {'lower':lower,'upper':upper,'feasible':lower<=upper,'lower_minus_upper':lower-upper,'meaning':'binary64 evaluation of exact-real formula; not directed rounding'}


def minimax(f,y,s):
    f,y,s=validate_fit(f,y,s);best=0.0;pair=None
    try:
        for i in range(len(f)):
            for j in range(len(f)):
                den=s[i]*f[j]+s[j]*f[i]
                if den<=0 or not math.isfinite(den):raise ValueError('pair denominator overflow/underflow')
                q=(y[i]*f[j]-y[j]*f[i])/den
                if not math.isfinite(q):raise ValueError('pair arithmetic nonfinite')
                if q>best:best=q;pair=(i,j)
        interval=feasible_interval(f,y,s,best)
        if pair is None:a=y[0]/f[0]
        else:
            i,j=pair;a=(y[i]*s[j]+y[j]*s[i])/(f[i]*s[j]+f[j]*s[i])
        residuals=[(a*c-b)/w for c,b,w in zip(f,y,s)]
        if not all(math.isfinite(q) for q in [a,best,*residuals]) or a<0:raise ValueError('minimax nonfinite')
        return {'a':a,'kappa':best,'active_pair_1based':None if pair is None else [pair[0]+1,pair[1]+1],
                'feasible_optimum':interval,'residuals':residuals,'objective':max(abs(q) for q in residuals)}
    except (OverflowError,ZeroDivisionError):raise ValueError('minimax invalid arithmetic') from None


def minimax_bisection(f,y,s):
    f,y,s=validate_fit(f,y,s);lo=0.0;hi=max(a/b for a,b in zip(y,s))
    for _ in range(100):
        mid=(lo+hi)/2
        if feasible_interval(f,y,s,mid)['feasible']:hi=mid
        else:lo=mid
    iv=feasible_interval(f,y,s,hi)
    return {'kappa':hi,'a':(iv['lower']+iv['upper'])/2,'interval':iv}


def peak_N(z):
    z=real(z,'z');r=math.sqrt(float(R2));h=(1/(1+float(K2)))**2
    return r*h*(1+z*z)**3-r*(1+5*z*z)-4*float(K2)*z


def peak():
    lo,hi=-.5,0.0
    if not (peak_N(lo)>0 and peak_N(hi)<0):raise ValueError('frozen peak bracket violated')
    for _ in range(100):
        mid=(lo+hi)/2
        if mid==lo or mid==hi:break
        if peak_N(mid)>0:lo=mid
        else:hi=mid
    z=(lo+hi)/2;k=math.sqrt(float(K2));r=math.sqrt(float(R2))
    return {'z':z,'theta_deg':math.degrees(math.acos((r-z)/(2*k))),
            'theta_q0_deg':math.degrees(math.acos(r/(2*k))),'root_residual':peak_N(z),
            'z_bracket':[lo,hi],'bracket_signs':[peak_N(-.5),peak_N(0)],
            'uniqueness':'THEORY Section4 on fixed nominaltheta32..60; not inferred from scan'}
