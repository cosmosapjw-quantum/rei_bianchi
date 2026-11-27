"""NASA TN D-3134 (1965): declared direct-product model, not a calibrated cross section.

Coordinates: eps = E_CM / I_model; rho = R / a0. Source sigma is kept as
one tagged active-electron channel; the mutually-exclusive symmetric-event
adapter has sigma_event = 2*sigma_tag, k_network=<sigma_tag*v>.
Only 1 <= eps <= 2 is the stated sudden-approximation application window.
"""
from __future__ import annotations
from fractions import Fraction
from functools import lru_cache
from typing import Literal
from mpmath import mp, iv

Spin = Literal['singlet', 'triplet']
A0_M = '5.29177210544e-11'
I_RY_EV = '13.605693122990'
I_RECEIVER_EV = '13.598434599702'
M_H_KG = '1.67262192369e-27'  # inherited mass-number approximation, unchanged
KB_SI = '1.380649e-23'
EV_J = '1.602176634e-19'
T_BOX = ('49999.63846', '50000.36154')


def potential(r, spin: Spin, ctx=mp):
    if spin == 'triplet':
        return ctx.mpf('3.6')*ctx.exp(-ctx.mpf('1.48')*r)
    if spin == 'singlet':
        z=ctx.exp(-ctx.mpf('1.08')*(r-ctx.mpf('1.5')))
        return ctx.mpf('.35')*(z*z-2*z)
    raise ValueError('spin must be singlet or triplet')


def potential_prime(r, spin: Spin, ctx=mp):
    if spin == 'triplet': return -ctx.mpf('1.48')*potential(r,spin,ctx)
    if spin == 'singlet':
        B=ctx.mpf('1.08'); z=ctx.exp(-B*(r-ctx.mpf('1.5')))
        return 2*ctx.mpf('.35')*B*(z-z*z)
    raise ValueError('unknown spin')


def turning(eps, spin: Spin, ctx=mp):
    if spin == 'triplet': return ctx.log(ctx.mpf('3.6')/eps)/ctx.mpf('1.48')
    if spin == 'singlet':
        return ctx.mpf('1.5')-ctx.log(1+ctx.sqrt(1+eps/ctx.mpf('.35')))/ctx.mpf('1.08')
    raise ValueError('unknown spin')


def phase(eps, ctx=mp):
    """Positive beta integral in mp; source primitive in interval context."""
    if ctx is mp:
        eps=mp.mpf(eps)
        if eps<1: return mp.mpf(0)
        if eps>2: raise ValueError('outside source window; tail model must be explicit')
        return mp.betainc(mp.mpf('1.5'),mp.mpf('4.5'),0,1-1/eps)/2
    x=ctx.sqrt(eps-1); u=1+x*x
    return -x/(10*u**5)+x/(80*u**4)+7*x/(480*u**3)+7*x/(384*u**2)+7*x/(256*u)+ctx.atan2(x,ctx.mpf(1))*7/256


def _fraction_mpf(t):
    sign,man,exponent,bc=t
    if bc<0: raise ValueError('non-finite interval endpoint')
    value=Fraction((-1 if sign else 1)*man)
    return value*(2**exponent) if exponent>=0 else value/Fraction(2**(-exponent))


def endpoints(value):
    """Exact rational endpoints of the outward-rounded interval."""
    return tuple(_fraction_mpf(t) for t in value._mpi_)


def interval_from_fractions(lo: Fraction, hi: Fraction):
    if lo>hi: raise ValueError('reversed interval')
    a=iv.mpf(lo.numerator)/lo.denominator
    b=iv.mpf(hi.numerator)/hi.denominator
    return iv.mpf([a.a,b.b])


def _e1_series_interval(x, terms: int=80):
    """E1(x) from a finite convergent series plus proved alternating tail.

    E1(x)=-EulerGamma-log(x)-sum_{n>=1}(-x)^n/(n n!).
    For n>=terms>=sup(x), the tail terms decrease. Add a symmetric
    next-term majorant, never relying on unsupported iv special functions.
    """
    xl,xu=endpoints(x)
    if xl<=0 or terms<xu: raise ValueError('E1 series domain or tail monotonicity fails')
    term=iv.mpf(1); total=iv.mpf(0)
    for n in range(1,terms+1):
        term *= -x/n; total += term/n
    rem=abs(term*(-x/(terms+1))/(terms+1))
    R=endpoints(rem)[1]
    return -iv.euler-iv.log(x)-total+interval_from_fractions(-R,R)


def e1_interval(x, terms: int=80):
    # E1 is strictly decreasing on positive reals. Evaluate its series only
    # at the exact binary endpoints to avoid alternating-series dependency.
    a,b=endpoints(x)
    lower=_e1_series_interval(interval_from_fractions(b,b),terms)
    upper=_e1_series_interval(interval_from_fractions(a,a),terms)
    return interval_from_fractions(endpoints(lower)[0],endpoints(upper)[1])


def hfun(s,r,ctx=mp):
    ex=ctx.exp(-s*r)
    ei=mp.e1(s*r) if ctx is mp else e1_interval(s*r)
    return ei+ex*(2/s+(s*r+1)/s**2)


def kfun(s,r,ctx=mp):
    return ctx.exp(-s*r)*((r+1)**2/s+2*(r+1)/s**2+2/s**3)


def gfun(eps,spin: Spin,ctx=mp):
    e=ctx.mpf(eps); t=turning(e,spin,ctx); h=lambda s:hfun(ctx.mpf(s),t,ctx); k=lambda s:kfun(ctx.mpf(s),t,ctx)
    if spin=='triplet':
        a=ctx.mpf('3.6');b=ctx.mpf('1.48')
        return h(4)-a/e*h(4+b)+a*b/(2*e)*k(4+b)
    D=ctx.mpf('.35');B=ctx.mpf('1.08');gam=ctx.mpf('1.5')
    return h(4)-D/e*ctx.exp(2*B*gam)*h(4+2*B)+2*D/e*ctx.exp(B*gam)*h(4+B)+D*B/e*ctx.exp(2*B*gam)*k(4+2*B)-D*B/e*ctx.exp(B*gam)*k(4+B)


def sigma_tag_a02(eps, spin: str='unpolarized'):
    e=mp.mpf(eps)
    if e<1: return mp.mpf(0)
    if e>2: raise ValueError('outside source window; tail unspecified')
    if spin=='unpolarized': gg=(gfun(e,'singlet')+3*gfun(e,'triplet'))/4
    else: gg=gfun(e,spin)
    return 256*phase(e)*gg


def screened(r): return (1+1/r)*mp.exp(-2*r)

def c0_closed(r):
    # C0=(1/(8*pi))*convolution(exp(-r), exp(-2r)*(1+1/r)).
    return mp.exp(-r)*(mp.mpf(7)/18-mp.mpf(11)/(27*r))+mp.exp(-2*r)*(mp.mpf(1)/9+mp.mpf(11)/(27*r))

def c0_radial(r):
    """Independent angularly integrated configuration-space convolution."""
    F=lambda a:mp.exp(-2*a)*(a/2+mp.mpf(3)/4)
    return mp.quad(lambda x:x*mp.exp(-x)*(F(abs(x-r))-F(x+r)),[0,r,r+2,mp.inf])/(4*r)

def restored(r): return screened(r)-c0_closed(r)


def threshold_g(spin: Spin, mode: str='source'):
    vertex=screened if mode=='source' else restored
    r0=turning(mp.mpf(1),spin)
    J=lambda r:1-potential(r,spin)-r*potential_prime(r,spin)/2
    return mp.quad(lambda r:r*vertex(r)**2*J(r),[r0,1,2,5,mp.inf])


def thermal_partial(T, threshold=I_RY_EV, spin='unpolarized'):
    """Only I_model <= E_CM <= 2 I_model. No implicit tail extrapolation."""
    T=mp.mpf(T); I0=mp.mpf(threshold);theta=mp.mpf(KB_SI)*T/mp.mpf(EV_J)
    mu=mp.mpf(M_H_KG)/2; a02=(100*mp.mpf(A0_M))**2
    pref=100*mp.sqrt(8*mp.mpf(EV_J)/(mp.pi*mu))*theta**(-mp.mpf('1.5'))
    # Tagged sigma: the symmetric two-branch event sum cancels pair 1/2.
    fn=lambda e:sigma_tag_a02(e,spin)*a02*(I0*e)*mp.exp(-I0*e/theta)*I0
    return pref*mp.quad(fn,[1,mp.mpf('1.1'),mp.mpf('1.25'),mp.mpf('1.5'),2])


def gbox(a: Fraction,b: Fraction,spin: Spin):
    """Natural interval extension; no monotonicity of g assumed."""
    return gfun(interval_from_fractions(a,b),spin,iv)


def phasebox(a: Fraction,b: Fraction):
    # f' is nonnegative, so use endpoint values rather than a wide interval x.
    aa=iv.mpf(a.numerator)/a.denominator;bb=iv.mpf(b.numerator)/b.denominator
    la=endpoints(phase(aa,iv))[0] if a>1 else Fraction(0)
    ub=endpoints(phase(bb,iv))[1]
    return interval_from_fractions(max(Fraction(0),la),ub)


def weight_tag(a: Fraction,b: Fraction,T: str,threshold=I_RY_EV):
    aa=(iv.mpf(a.numerator)/a.denominator)*iv.mpf(threshold)
    bb=(iv.mpf(b.numerator)/b.denominator)*iv.mpf(threshold)
    theta=iv.mpf(KB_SI)*iv.mpf(T)/iv.mpf(EV_J);mu=iv.mpf(M_H_KG)/2
    return 100*iv.sqrt(8*iv.mpf(EV_J)/(iv.pi*mu))/iv.sqrt(theta)*((aa+theta)*iv.exp(-aa/theta)-(bb+theta)*iv.exp(-bb/theta))


def partial_rate_enclosure(cells:int=256):
    """Continuous T-box and source-energy interval enclosure by positive bins."""
    if cells<8: raise ValueError('at least 8 cells required')
    sums=[iv.mpf(0),iv.mpf(0)]; rows=[]; a02=(100*iv.mpf(A0_M))**2
    for j in range(cells):
        a=Fraction(cells+j,cells);b=Fraction(cells+j+1,cells)
        gg=(gbox(a,b,'singlet')+3*gbox(a,b,'triplet'))/4
        gl,gu=endpoints(gg);gg=interval_from_fractions(max(Fraction(0),gl),gu)
        sg=256*phasebox(a,b)*gg*a02
        sl,su=endpoints(sg)
        wl=weight_tag(a,b,T_BOX[0]);wh=weight_tag(a,b,T_BOX[1])
        sums[0]+=interval_from_fractions(sl,sl)*wl
        sums[1]+=interval_from_fractions(su,su)*wh
        rows.append([str(a),str(b),str(sl),str(su)])
    return (endpoints(sums[0])[0],endpoints(sums[1])[1]),rows


def jfun(s,r,ctx=mp):
    """Integral of exp(-s r)*(2 r^2+4 r+3+1/r), from r to infinity."""
    ex=ctx.exp(-s*r)
    ee=mp.e1(s*r) if ctx is mp else e1_interval(s*r)
    return ee+ex*(2*(r*r/s+2*r/s**2+2/s**3)+4*(r/s+1/s**2)+3/s)


def gprime(eps,spin: Spin,ctx=mp):
    e=ctx.mpf(eps);r=turning(e,spin,ctx)
    if spin=='triplet': return ctx.mpf('3.6')/e**2*jfun(4+ctx.mpf('1.48'),r,ctx)
    D=ctx.mpf('.35');B=ctx.mpf('1.08');ga=ctx.mpf('1.5')
    return D/e**2*(ctx.exp(2*B*ga)*jfun(4+2*B,r,ctx)-2*ctx.exp(B*ga)*jfun(4+B,r,ctx))


def certify_g_monotonic(cells=128):
    records=[]
    for spin in ['singlet','triplet']:
        lower=None
        for j in range(cells):
            a=Fraction(cells+j,cells);b=Fraction(cells+j+1,cells)
            lo,_=endpoints(gprime(interval_from_fractions(a,b),spin,iv))
            if lo<=0: return False,{'spin':spin,'bin':j,'lower':str(lo)}
            lower=lo if lower is None else min(lower,lo)
        records.append({'spin':spin,'cells':cells,'uniform_derivative_lower':str(lower)})
    return True,records


def partial_rate_monotonic_enclosure(cells=512):
    ok,proof=certify_g_monotonic()
    if not ok: raise ArithmeticError(f'monotonicity not certified: {proof}')
    sig=[];a02=(100*iv.mpf(A0_M))**2
    for j in range(cells+1):
        e=iv.mpf(cells+j)/cells
        gg=(gfun(e,'singlet',iv)+3*gfun(e,'triplet',iv))/4
        fs=phase(e,iv) if j else iv.mpf(0)
        sig.append(endpoints(256*gg*fs*a02))
    sums=[iv.mpf(0),iv.mpf(0)];rows=[]
    for j in range(cells):
        a=Fraction(cells+j,cells);b=Fraction(cells+j+1,cells)
        sl=max(Fraction(0),sig[j][0]);su=sig[j+1][1]
        sums[0]+=interval_from_fractions(sl,sl)*weight_tag(a,b,T_BOX[0])
        sums[1]+=interval_from_fractions(su,su)*weight_tag(a,b,T_BOX[1])
        rows.append([str(a),str(b),str(sl),str(su)])
    return (endpoints(sums[0])[0],endpoints(sums[1])[1]),rows,proof


def exponential_moment(power:int,s,r,ctx=mp):
    """Integral_r^infty rho**power*exp(-s*rho) drho; power=-1 or 0,1,2."""
    if power == -1:
        return mp.e1(s*r) if ctx is mp else e1_interval(s*r)
    if power not in (0,1,2): raise ValueError('supported moment powers: -1,0,1,2')
    import math
    return ctx.exp(-s*r)*sum(ctx.mpf(math.factorial(power))/math.factorial(j)*r**j/s**(power-j+1) for j in range(power+1))


def threshold_g_closed(spin:Spin,mode:str='restored',ctx=mp):
    """Exact finite E1/elementary basis for the zero-momentum coefficient."""
    r=turning(ctx.mpf(1),spin,ctx)
    if mode=='source': groups=[(ctx.mpf(4),{1:ctx.mpf(1),0:ctx.mpf(2),-1:ctx.mpf(1)})]
    elif mode=='restored':
        a=ctx.mpf(8)/9;b=ctx.mpf(16)/27;c=ctx.mpf(11)/27;d=ctx.mpf(7)/18
        groups=[(ctx.mpf(4),{1:a*a,0:2*a*b,-1:b*b}),
                (ctx.mpf(3),{1:-2*a*d,0:2*(a*c-b*d),-1:2*b*c}),
                (ctx.mpf(2),{1:d*d,0:-2*c*d,-1:c*c})]
    else: raise ValueError('mode must be source or restored')
    if spin=='triplet': pots=[(ctx.mpf('3.6'),ctx.mpf('1.48'))]
    elif spin=='singlet':
        D=ctx.mpf('.35');B=ctx.mpf('1.08');ga=ctx.mpf('1.5')
        pots=[(D*ctx.exp(2*B*ga),2*B),(-2*D*ctx.exp(B*ga),B)]
    else: raise ValueError('unknown spin')
    total=ctx.mpf(0)
    for s,coeff in groups:
        for p,v in coeff.items():
            total+=v*exponential_moment(p,s,r,ctx)
            for u,t in pots:
                total+=v*u*(-exponential_moment(p,s+t,r,ctx)+t/2*exponential_moment(p+1,s+t,r,ctx))
    return total
