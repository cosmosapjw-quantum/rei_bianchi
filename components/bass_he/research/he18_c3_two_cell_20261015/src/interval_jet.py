"""Univariate Taylor jets over mpmath's outward interval primitives.
A coefficient k encloses f^(k)(x)/k! for every base point x in coeff[0]'s seed domain.
This is not a Taylor model: a separate Taylor remainder is always required.
"""
from fractions import Fraction as Q
from mpmath import iv
iv.dps = 70

def val(x):
    if hasattr(x, '_mpi_'): return x
    if isinstance(x, Q): return iv.mpf(x.numerator)/x.denominator
    if isinstance(x, float): return val(Q.from_float(x))
    return iv.mpf(x)

def rational(t):
    sign,m,ex,bc=t
    if bc < 0: raise ValueError('NONFINITE_INTERVAL_ENDPOINT')
    return Q((-1 if sign else 1)*m)*(Q(2)**ex)

def endpoints(x): return tuple(rational(t) for t in val(x)._mpi_)
def bound(lo,hi):
    a,b=val(lo),val(hi)
    return iv.make_mpf((a._mpi_[0],b._mpi_[1]))
def absup(x):
    a,b=endpoints(x);return max(abs(a),abs(b))
def lo(x): return endpoints(x)[0]
def hi(x): return endpoints(x)[1]
def record(x): return [str(t) for t in endpoints(x)]

class Jet:
    __slots__=('c','n')
    def __init__(self,c): self.c=[val(x) for x in c]; self.n=len(c)-1
    @classmethod
    def constant(cls,x,n): return cls([val(x)]+[val(0)]*n)
    @classmethod
    def variable(cls,x,n): return cls([val(x),val(1)]+[val(0)]*(n-1)) if n else cls([val(x)])
    def coerce(self,o):
        if isinstance(o,Jet):
            if o.n!=self.n:raise ValueError('JET_ORDER_MISMATCH')
            return o
        return Jet.constant(o,self.n)
    def __add__(self,o):
        o=self.coerce(o);return Jet([a+b for a,b in zip(self.c,o.c)])
    __radd__=__add__
    def __neg__(self):return Jet([-a for a in self.c])
    def __sub__(self,o):return self+(-self.coerce(o))
    def __rsub__(self,o):return self.coerce(o)+(-self)
    def __mul__(self,o):
        o=self.coerce(o);return Jet([sum((self.c[k]*o.c[j-k] for k in range(j+1)),val(0)) for j in range(self.n+1)])
    __rmul__=__mul__
    def reciprocal(self):
        if lo(self.c[0])<=0<=hi(self.c[0]):raise ValueError('ZERO_IN_RECIPROCAL_DOMAIN')
        y=[1/self.c[0]]
        for j in range(1,self.n+1):y.append(-sum((self.c[k]*y[j-k] for k in range(1,j+1)),val(0))/self.c[0])
        return Jet(y)
    def __truediv__(self,o):return self*self.coerce(o).reciprocal()
    def __rtruediv__(self,o):return self.coerce(o)*self.reciprocal()
    def exp(self):
        y=[iv.exp(self.c[0])]
        for j in range(1,self.n+1):
            y.append(sum((k*self.c[k]*y[j-k] for k in range(1,j+1)),val(0))/j)
        return Jet(y)
    def log(self):
        if lo(self.c[0])<=0:raise ValueError('NONPOSITIVE_LOG_DOMAIN')
        r=self.reciprocal();y=[iv.log(self.c[0])]
        for j in range(1,self.n+1):
            y.append(sum(((k+1)*self.c[k+1]*r.c[j-1-k] for k in range(j)),val(0))/j)
        return Jet(y)
    def __pow__(self,p):
        if isinstance(p,int):
            if p<0:return (self**(-p)).reciprocal()
            out=Jet.constant(1,self.n);base=self
            while p:
                if p&1:out=out*base
                p//=2
                if p:base=base*base
            return out
        return (self.log()*val(p)).exp()
    def sqrt(self):return self**Q(1,2)
    def sinh(self):return (self.exp()-(-self).exp())/2
    def cosh(self):return (self.exp()+(-self).exp())/2

def polynomial(coeff,z):
    y=Jet.constant(coeff[-1],z.n)
    for c in coeff[-2::-1]:y=y*z+c
    return y
