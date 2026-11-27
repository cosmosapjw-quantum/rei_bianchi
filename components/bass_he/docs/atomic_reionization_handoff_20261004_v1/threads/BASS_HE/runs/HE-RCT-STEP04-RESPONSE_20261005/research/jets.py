"""Order-two Taylor scalar. c[2] is half the second derivative.

Operations propagate formal coefficients; they do not enclose roundoff. Numeric
values may be float, Fraction, or mpmath.mpf. Comparisons inspect the base value
only, so a base-state domain check is NOT a finite-parameter tube certificate.
"""
from __future__ import annotations
import math

class Jet2:
    __slots__=('c',)
    def __init__(self,v,d1=0,d2=0): self.c=(v,d1,d2)
    @staticmethod
    def _co(x): return x if isinstance(x,Jet2) else Jet2(x)
    def __add__(self,x):
        b=self._co(x).c;a=self.c
        return Jet2(a[0]+b[0],a[1]+b[1],a[2]+b[2])
    __radd__=__add__
    def __neg__(self):return Jet2(*(-x for x in self.c))
    def __sub__(self,x):return self+-self._co(x)
    def __rsub__(self,x):return self._co(x)+-self
    def __mul__(self,x):
        a=self.c;b=self._co(x).c
        return Jet2(a[0]*b[0],a[0]*b[1]+a[1]*b[0],a[0]*b[2]+a[1]*b[1]+a[2]*b[0])
    __rmul__=__mul__
    def reciprocal(self):
        a,b,c=self.c
        if a==0:raise ZeroDivisionError('zero base coefficient')
        return Jet2(1/a,-b/(a*a),b*b/(a*a*a)-c/(a*a))
    def __truediv__(self,x):return self*self._co(x).reciprocal()
    def __rtruediv__(self,x):return self._co(x)*self.reciprocal()
    def __pow__(self,p):
        if isinstance(p,Jet2):raise TypeError('variable exponent not in this source contract')
        a,b,c=self.c
        if a<=0:raise ValueError('constant-power jet requires positive base')
        value=a**p
        return Jet2(value,value*p*b/a,value*(p*c/a+p*(p-1)*b*b/(2*a*a)))
    def exp(self):
        a,b,c=self.c
        if hasattr(a,'_mpf_'):
            import mpmath
            value=mpmath.exp(a)
        else:value=math.exp(a)
        return Jet2(value,value*b,value*(c+b*b/2))
    def __lt__(self,x):return self.c[0]<self._co(x).c[0]
    def __le__(self,x):return self.c[0]<=self._co(x).c[0]
    def __gt__(self,x):return self.c[0]>self._co(x).c[0]
    def __ge__(self,x):return self.c[0]>=self._co(x).c[0]
    def __repr__(self):return 'Jet2'+repr(self.c)
