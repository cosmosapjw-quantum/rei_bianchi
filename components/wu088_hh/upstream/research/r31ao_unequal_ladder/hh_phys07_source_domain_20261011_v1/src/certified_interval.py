"""Directed rational intervals and second jets for the PHYS07 reference.

Binary64 inputs are lifted exactly. Arithmetic endpoints are rounded to 112
significand bits by integer floor/ceiling, without using floating point.
exp/log enclosures use positive series with explicit rational tail bounds.
This is not the native Rust interval implementation or a native certificate.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import factorial, isfinite, isqrt

PRECISION_BITS = 112
LOG_TERMS = 64
EXP_TERMS = 32


def fraction(x):
    if isinstance(x, F):
        return x
    if isinstance(x, float):
        if not isfinite(x):
            raise ValueError('nonfinite leaf')
        return F.from_float(x)
    return F(x)


def pow2(k):
    return F(1 << k) if k >= 0 else F(1, 1 << -k)


def floor_log2(q):
    q = fraction(q)
    if q <= 0:
        raise ValueError('positive argument required')
    k = q.numerator.bit_length() - q.denominator.bit_length()
    if q < pow2(k):
        k -= 1
    return k


def outward(q, upper=False):
    q = fraction(q)
    if not q:
        return F(0)
    step = pow2(floor_log2(abs(q)) - PRECISION_BITS + 1)
    v = q / step
    n = -((-v.numerator) // v.denominator) if upper else v.numerator // v.denominator
    return n * step


class I:
    __slots__ = ('lo', 'hi')

    def __init__(self, lo=0, hi=None):
        if isinstance(lo, I) and hi is None:
            self.lo, self.hi = lo.lo, lo.hi
            return
        self.lo = fraction(lo)
        self.hi = self.lo if hi is None else fraction(hi)
        if self.lo > self.hi:
            raise ValueError('reversed interval')

    @classmethod
    def rounded(cls, lo, hi):
        return cls(outward(lo), outward(hi, True))

    def __repr__(self):
        return 'I(%r,%r)' % (self.lo, self.hi)

    def __eq__(self, other):
        other = I(other)
        return self.lo == other.lo and self.hi == other.hi

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __add__(self, other):
        if isinstance(other, J):
            return NotImplemented
        other = I(other)
        if other.lo == other.hi == 0:
            return self
        if self.lo == self.hi == 0:
            return other
        return I.rounded(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, J):
            return NotImplemented
        return self + (-I(other))

    def __rsub__(self, other):
        return I(other) + (-self)

    def __mul__(self, other):
        if isinstance(other, J):
            return NotImplemented
        other = I(other)
        if self.lo == self.hi == 0 or other.lo == other.hi == 0:
            return I(0)
        if other.lo == other.hi == 1:
            return self
        if self.lo == self.hi == 1:
            return other
        v = [self.lo*other.lo, self.lo*other.hi, self.hi*other.lo, self.hi*other.hi]
        return I.rounded(min(v), max(v))

    __rmul__ = __mul__

    def inverse(self):
        if self.lo <= 0 <= self.hi:
            raise ValueError('division by interval containing zero')
        return I.rounded(1/self.hi, 1/self.lo)

    def __truediv__(self, other):
        if isinstance(other, J):
            return NotImplemented
        return self * I(other).inverse()

    def __rtruediv__(self, other):
        return I(other) * self.inverse()

    def __pow__(self, p):
        if not isinstance(p, int):
            return self.powf(p)
        if p < 0:
            return (self ** (-p)).inverse()
        if p == 0:
            return I(1)
        if p % 2 == 0:
            v = [self.lo ** p, self.hi ** p]
            return I.rounded(0 if self.lo <= 0 <= self.hi else min(v), max(v))
        return I.rounded(self.lo ** p, self.hi ** p)

    def contains(self, x):
        x = I(x)
        return self.lo <= x.lo and x.hi <= self.hi

    def mag(self):
        return max(abs(self.lo), abs(self.hi))

    def width(self):
        return self.hi - self.lo

    def midpoint(self):
        return (self.lo + self.hi)/2

    def exp(self):
        return I(_exp_point(self.lo).lo, _exp_point(self.hi).hi)

    def log(self):
        if self.lo <= 0:
            raise ValueError('logarithm domain')
        return I(_log_point(self.lo).lo, _log_point(self.hi).hi)

    ln = log

    def sqrt(self):
        if self.lo < 0:
            raise ValueError('square root domain')
        return I(_sqrt_point(self.lo).lo, _sqrt_point(self.hi).hi)

    def powf(self, p):
        p = fraction(p)
        if self.lo <= 0:
            raise ValueError('positive base required for source powf')
        if p.denominator == 1:
            return self ** p.numerator
        if p == F(1, 2):
            return self.sqrt()
        return (self.log() * I(p)).exp()

    def as_dict(self):
        return {'lo': str(self.lo), 'hi': str(self.hi),
                'lo_approx': float(self.lo), 'hi_approx': float(self.hi)}


def _sqrt_point(q):
    if q == 0:
        return I(0)
    # q / step^2 is bracketed by n^2 and (n+1)^2 using integer sqrt.
    step = pow2(floor_log2(q)//2 - PRECISION_BITS + 1)
    v = q/(step*step)
    n = isqrt(v.numerator // v.denominator)
    lo = n * step
    hi = lo if lo*lo == q else (n+1)*step
    return I(lo, hi)


def _log_unit(m):
    if not (1 <= m <= 2):
        raise ValueError('log reduction domain')
    z = I((m-1)/(m+1))
    z2 = z*z
    term, total = z, I(0)
    for n in range(LOG_TERMS):
        total = total + term/I(2*n+1)
        term = term*z2
    # 0 <= z <= 1/3, omitted terms start at power 2*M+1.
    tail = F(2, (2*LOG_TERMS+1)*3**(2*LOG_TERMS+1)) / (1-F(1,9))
    total = 2*total
    return I.rounded(total.lo, total.hi + tail)


@lru_cache(maxsize=1)
def _ln2():
    return _log_unit(F(2))


@lru_cache(maxsize=4096)
def _log_point(q):
    if q <= 0:
        raise ValueError('logarithm domain')
    if q == 1:
        return I(0)
    k = floor_log2(q)
    return _log_unit(q/pow2(k)) + k*_ln2()


@lru_cache(maxsize=4096)
def _exp_point(q):
    if abs(q) > 1024:
        raise ValueError('reference exp budget domain |argument| <= 1024')
    if q == 0:
        return I(1)
    if q < 0:
        return _exp_point(-q).inverse()
    s = max(0, floor_log2(q)+4)
    t = q/pow2(s)
    if not (0 <= t <= F(1,8)):
        raise ValueError('exp reduction domain')
    term, total = I(1), I(1)
    for n in range(1, EXP_TERMS+1):
        term = term*I(t)/I(n)
        total = total+term
    # All omitted terms are positive; successive ratios are <= t/(M+2).
    tail = t**(EXP_TERMS+1)/factorial(EXP_TERMS+1)/(1-t/F(EXP_TERMS+2))
    value = I.rounded(total.lo, total.hi+tail)
    for _ in range(s):
        value = value*value
    return value


class J:
    __slots__ = ('v', 'g', 'h', 'n')

    def __init__(self, value, gradient, hessian):
        self.v = I(value)
        self.g = [I(x) for x in gradient]
        self.n = len(self.g)
        if len(hessian) != self.n or any(len(r) != self.n for r in hessian):
            raise ValueError('jet shape')
        self.h = [[I(x) for x in row] for row in hessian]

    @classmethod
    def constant(cls, value, n=6):
        return cls(value, [0]*n, [[0]*n for _ in range(n)])

    @classmethod
    def variable(cls, value, slot, n=6):
        if not 0 <= slot < n:
            raise ValueError('jet variable slot')
        j = cls.constant(value, n)
        j.g[slot] = I(1)
        return j

    @property
    def value(self):
        return self.v

    @property
    def gradient(self):
        return self.g

    @property
    def hessian(self):
        return self.h

    def _coerce(self, other):
        if isinstance(other, J):
            if other.n != self.n:
                raise ValueError('jet dimension mismatch')
            return other
        return J.constant(other, self.n)

    def __add__(self, other):
        b = self._coerce(other)
        return J(self.v+b.v, [self.g[i]+b.g[i] for i in range(self.n)],
                 [[self.h[i][j]+b.h[i][j] for j in range(self.n)] for i in range(self.n)])

    __radd__ = __add__

    def __neg__(self):
        return J(-self.v, [-x for x in self.g], [[-x for x in row] for row in self.h])

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) + (-self)

    def __mul__(self, other):
        b = self._coerce(other)
        g = [self.g[i]*b.v+self.v*b.g[i] for i in range(self.n)]
        h = [[self.h[i][j]*b.v+self.g[i]*b.g[j]+self.g[j]*b.g[i]+self.v*b.h[i][j]
              for j in range(self.n)] for i in range(self.n)]
        return J(self.v*b.v, g, h)

    __rmul__ = __mul__

    def chain(self, value, first, second):
        first, second = I(first), I(second)
        return J(value, [first*x for x in self.g],
                 [[first*self.h[i][j]+second*self.g[i]*self.g[j]
                   for j in range(self.n)] for i in range(self.n)])

    def inverse(self):
        v = self.v.inverse()
        return self.chain(v, -(v*v), 2*v*v*v)

    def __truediv__(self, other):
        return self*self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other)*self.inverse()

    def exp(self):
        v = self.v.exp()
        return self.chain(v, v, v)

    def log(self):
        d = self.v.inverse()
        return self.chain(self.v.log(), d, -(d*d))

    ln = log

    def powf(self, p):
        p = fraction(p)
        if self.v.lo <= 0:
            raise ValueError('positive base required for source jet powf')
        if p == 0:
            return J.constant(1, self.n)
        if p == 1:
            return self
        v = self.v.powf(p)
        ip = I(p)
        first = ip*v/self.v
        second = ip*(ip-I(1))*v/(self.v*self.v)
        return self.chain(v, first, second)

    def __pow__(self, p):
        if isinstance(p, int) and p >= 0:
            result = J.constant(1, self.n)
            for _ in range(p):
                result = result*self
            return result
        return self.powf(p)

    def sqrt(self):
        return self.powf(F(1,2))

    def as_dict(self):
        return {'value': self.v.as_dict(), 'gradient': [x.as_dict() for x in self.g],
                'hessian': [[x.as_dict() for x in row] for row in self.h]}
