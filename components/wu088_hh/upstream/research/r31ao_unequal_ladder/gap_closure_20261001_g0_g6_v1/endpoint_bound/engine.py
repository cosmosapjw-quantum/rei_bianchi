"""Positive endpoint majorants using rational outward arithmetic.

The evaluator accepts explicit mathematical parameters; it never opens HH data.
Returned upper bounds can be very conservative. They are not producer errors.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import factorial, isqrt

class ResourceLimit(RuntimeError):
    pass

def fraction(x):
    if isinstance(x,bool) or not isinstance(x,(int,F)):
        raise TypeError('Use exact int/Fraction input, never host floating conversion')
    x=F(x)
    if max(x.numerator.bit_length(),x.denominator.bit_length())>16384:
        raise ResourceLimit('Input integer bit cap exceeded')
    return x

@dataclass(frozen=True)
class Interval:
    lo:F
    hi:F
    def __post_init__(self):
        object.__setattr__(self,'lo',fraction(self.lo));object.__setattr__(self,'hi',fraction(self.hi))
        if self.lo>self.hi:raise ValueError('Reversed interval')
    def __add__(self,b):
        b=as_interval(b);return Interval(self.lo+b.lo,self.hi+b.hi)
    __radd__=__add__
    def __neg__(self):return Interval(-self.hi,-self.lo)
    def __sub__(self,b):return self+-as_interval(b)
    def __rsub__(self,b):return as_interval(b)+-self
    def __mul__(self,b):
        b=as_interval(b);p=[self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi]
        return Interval(min(p),max(p))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=as_interval(b)
        if b.lo<=0<=b.hi:raise ValueError('Division interval contains zero')
        return self*Interval(1/b.hi,1/b.lo)
    def __rtruediv__(self,b):return as_interval(b)/self
    @property
    def width(self):return self.hi-self.lo

def as_interval(x):
    return x if isinstance(x,Interval) else Interval(fraction(x),fraction(x))

def precision(bits):
    if isinstance(bits,bool) or not isinstance(bits,int) or not 16<=bits<=1024:
        raise ResourceLimit('Precision must be an integer in [16,1024]')

def quantize(a,bits):
    precision(bits);a=as_interval(a)
    scale=1<<bits
    lo=(a.lo.numerator*scale)//a.lo.denominator
    hi=-((-a.hi.numerator*scale)//a.hi.denominator)
    return Interval(F(lo,scale),F(hi,scale))

def sqrt_bounds(x,bits=128):
    precision(bits);x=fraction(x)
    if x<0:raise ValueError('sqrt domain')
    scale=1<<bits
    k=isqrt((x.numerator*scale*scale)//x.denominator)
    lo=F(k,scale)
    return Interval(lo,lo if lo*lo==x else F(k+1,scale))

def sqrt_interval(a,bits=128):
    a=as_interval(a)
    return Interval(sqrt_bounds(a.lo,bits).lo,sqrt_bounds(a.hi,bits).hi)

def positive_power(a,n):
    if type(n) is not int or abs(n)>128:raise ResourceLimit('Power cap')
    a=as_interval(a)
    if a.lo<0 or n<0 and a.lo==0:raise ValueError('Positive power domain')
    if n>=0:return Interval(a.lo**n,a.hi**n)
    return Interval(a.hi**n,a.lo**n)

def half_power(a,twice_exponent,bits=128):
    precision(bits)
    if type(twice_exponent) is not int or abs(twice_exponent)>128:raise ResourceLimit('Half-power cap')
    if twice_exponent%2==0:return positive_power(a,twice_exponent//2)
    return positive_power(sqrt_interval(a,bits),twice_exponent)

def _atan_inv(q,bits):
    x=F(1,q);s=F(0);lo=F(0);hi=x;target=F(1,1<<(bits+12))
    for n in range(1024):
        term=x**(2*n+1)/(2*n+1)
        s+=term if n%2==0 else -term
        if n%2:lo=s
        else:hi=s
        if hi-lo<=target:return Interval(lo,hi)
    raise ResourceLimit('Arctan series cap')

@lru_cache(maxsize=16)
def pi_bounds(bits=128):
    precision(bits)
    return quantize(16*_atan_inv(5,bits)-4*_atan_inv(239,bits),bits)

def exp_neg_bounds(x,bits=128,max_terms=512,max_squarings=64):
    precision(bits);x=fraction(x)
    if type(max_terms) is not int or not 2<=max_terms<=4096:raise ResourceLimit('Taylor term cap')
    if type(max_squarings) is not int or not 0<=max_squarings<=64:raise ResourceLimit('Range-reduction cap must be integer in [0,64]')
    if x<0:raise ValueError('exp(-x) requires x>=0')
    if x==0:return Interval(F(1),F(1))
    y=x;m=0
    while y>1:
        y/=2;m+=1
        if m>max_squarings:raise ResourceLimit('exp range-reduction cap')
    guard=min(bits+16,1024);target=F(1,1<<guard)
    s=F(1);term=F(1);lo=F(0);hi=F(1)
    for n in range(1,max_terms+1):
        term*=y/n;s+=(-term if n%2 else term)
        if n%2:lo=s
        else:hi=s
        if hi-lo<=target:break
    else:raise ResourceLimit('exp alternating-series cap')
    out=quantize(Interval(max(F(0),lo),hi),guard)
    for _ in range(m):out=quantize(positive_power(out,2),guard)
    return quantize(out,bits)

def gamma_half_bounds(twice_shape,x,bits=128):
    """Enclose upper unregularized Gamma(m+1/2,x), x>0, by positive recurrence."""
    x=fraction(x)
    if type(twice_shape) is not int or twice_shape<1 or twice_shape%2==0 or twice_shape>41 or x<=0:
        raise ValueError('Require positive odd twice_shape<=41 and x>0')
    e=exp_neg_bounds(x,bits);base=e/sqrt_interval(x,bits)
    # Integration by parts and t^(-3/2)<=t^(-1/2)/x give the lower bound.
    g=Interval((base/(1+F(1,2)/x)).lo,base.hi)
    shape2=1
    while shape2<twice_shape:
        g=F(shape2,2)*g+half_power(x,shape2,bits)*e
        shape2+=2
    return g

def radial_gaussian_moment(n,bits=128):
    if type(n) is not int or not 0<=n<=12:raise ValueError('Moment degree outside 0..12')
    p=pi_bounds(bits)
    if n%2:return 2*factorial((n+1)//2)*p
    coefficient=F(1)
    for j in range(1,n//2+1):coefficient*=F(2*j+1,2)
    return coefficient*p*sqrt_interval(p,bits)

def hermite_coefficient(i,r,mu,bits=128):
    mu=fraction(mu)
    if type(i) is not int or not 0<=i<=8 or type(r) is not int or not 0<=r<=(i+1)//2 or mu<=0:
        raise ValueError('Invalid Hermite index/mu')
    a=F(factorial(i+1),2**(i+1)*factorial(r)*factorial(i+1-2*r))*mu**(i+1-2*r)
    return a/sqrt_interval(pi_bounds(bits),bits)

def _parameters(i,mu,a=None):
    mu=fraction(mu)
    if type(i) is not int or not 0<=i<=8 or mu<=0:raise ValueError('Require i=0..8 and mu>0')
    if a is not None:
        a=fraction(a)
        if a<=0:raise ValueError('Require a>0')
    return mu,a

def lower_mass_bound(i,mu,a,l,bits=128):
    mu,a=_parameters(i,mu,a);l=fraction(l)
    if l<=0:raise ValueError('lower split must be positive')
    lam=mu*mu/4;total=Interval(F(0),F(0))
    for r in range((i+1)//2+1):
        nu2=2*i+3-2*r
        total+=hermite_coefficient(i,r,mu,bits)*half_power(lam,2-nu2,bits)*gamma_half_bounds(nu2-2,lam/l,bits)
    return (half_power(a,-3,bits)*total).hi

def upper_mass_bound(i,mu,T,bits=128):
    mu,_=_parameters(i,mu);T=fraction(T)
    if T<=0:raise ValueError('upper split must be positive')
    total=Interval(F(0),F(0))
    for r in range((i+1)//2+1):
        power=i+2-r
        total+=hermite_coefficient(i,r,mu,bits)*(T**(-power))/power
    return total.hi

def interior_mass_bound(i,mu,a,l,T,bits=128,panels=8):
    mu,a=_parameters(i,mu,a);l=fraction(l);T=fraction(T)
    if not 0<l<T:raise ValueError('Require 0<l<T')
    if type(panels) is not int or not 1<=panels<=128:raise ResourceLimit('Interior mass panels cap128')
    width=(T-l)/panels;lam=mu*mu/4;bound=F(0)
    for n in range(panels):
        left=l+n*width;right=left+width;total=Interval(F(0),F(0))
        for r in range((i+1)//2+1):
            nu2=2*i+3-2*r;star=min(right,max(left,2*lam/nu2))
            total+=hermite_coefficient(i,r,mu,bits)*half_power(star,-nu2,bits)*exp_neg_bounds(lam/star,bits)
        bound+=(width*half_power(a+left,-3,bits)*total).hi
    return bound

def _poly_add(a,b):
    out=dict(a)
    for key,v in b.items():out[key]=out.get(key,F(0))+v
    return out

def _poly_mul(a,b):
    out={}
    for (i,j),u in a.items():
        for (k,l),v in b.items():out[(i+k,j+l)]=out.get((i+k,j+l),F(0))+u*v
    return out

def _poly_pow(p,k):
    out={(0,0):F(1)}
    for _ in range(k):out=_poly_mul(out,p)
    return out

def gaussian_field_majorant(a,b,d1,d2,k,angular,field,bits=128):
    a=fraction(a);b=fraction(b)
    if a<=0 or b<=0 or type(k) is not int or not 0<=k<=8 or angular not in ('s','px','pz') or field not in ('O','G1','G2'):
        raise ValueError('Invalid Gaussian majorant target')
    if len(d1)!=3 or len(d2)!=3:raise ValueError('Three-dimensional real centers required')
    d1=tuple(fraction(x) for x in d1);d2=tuple(fraction(x) for x in d2)
    D1=sqrt_bounds(sum(x*x for x in d1),bits).hi;D2=sqrt_bounds(sum(x*x for x in d2),bits).hi
    ia=(1/sqrt_interval(a,bits)).hi;ib=(1/sqrt_interval(b,bits)).hi
    L1={(0,0):D1,(1,0):ia};L2={(0,0):D2,(0,1):ib};R=_poly_add(L1,L2)
    angular_poly={(0,0):F(1)} if angular=='s' else L1
    if field=='O':factor=angular_poly
    elif field=='G1':
        factor={key:2*a*v for key,v in _poly_mul(L1,angular_poly).items()}
        if angular=='pz':factor=_poly_add(factor,{(0,0):F(1)})
    else:factor={key:2*b*v for key,v in _poly_mul(L2,angular_poly).items()}
    p=_poly_mul(_poly_pow(R,k),factor);out=Interval(F(0),F(0))
    for (m,n),coef in p.items():out+=coef*radial_gaussian_moment(m,bits)*radial_gaussian_moment(n,bits)
    return out.hi

def complement_bound(i,j,mu,a,b,l_t,T_t,l_u,T_u,C_F,bits=128,panels=8,pivot_u=F(1)):
    C_F=fraction(C_F)
    if C_F<0:raise ValueError('C_F must be a proved nonnegative upper bound')
    if not 0<fraction(l_t)<fraction(T_t) or not 0<fraction(l_u)<fraction(T_u):raise ValueError('Invalid complement rectangle')
    Et=lower_mass_bound(i,mu,a,l_t,bits)+upper_mass_bound(i,mu,T_t,bits)
    Eu=lower_mass_bound(j,mu,b,l_u,bits)+upper_mass_bound(j,mu,T_u,bits)
    Wu=lower_mass_bound(j,mu,b,pivot_u,bits)+upper_mass_bound(j,mu,pivot_u,bits)
    Jt=interior_mass_bound(i,mu,a,l_t,T_t,bits,panels)
    return {'E_t':Et,'E_u':Eu,'W_u':Wu,'J_t':Jt,'C_F':C_F,'bound':C_F*(Et*Wu+Jt*Eu),'accounting':'(outside_t x all_u) disjoint_union (inside_t x outside_u)','backend':'EXACT_RATIONAL_OUTWARD_BOUNDS','input_scope':'CALLER_SUPPLIED_EXACT_PARAMETERS_NOT_CLASSIFIED','actual_hh_evaluation_assertion':None}
