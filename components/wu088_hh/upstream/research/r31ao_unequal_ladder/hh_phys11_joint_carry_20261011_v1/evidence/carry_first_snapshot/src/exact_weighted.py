"""Exact rational interval algebra over captured finite binary64 endpoints.

This is an offline reference, not a native source/solver/provider adapter.
All rational operations are exact; binary64 displays are rounded outward.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
import math
import struct


def bits(x):
    return struct.pack('>d', x).hex()


def unbits(s):
    if not isinstance(s, str) or len(s) != 16:
        raise ValueError('ENDPOINT_BITS')
    x = struct.unpack('>d', bytes.fromhex(s))[0]
    if not math.isfinite(x):
        raise ValueError('NONFINITE_ENDPOINT')
    return x


def outward(q, lower):
    f = float(q)
    if not math.isfinite(f):
        raise ValueError('DISPLAY_OVERFLOW')
    if (lower and Q(f) > q) or (not lower and Q(f) < q):
        f = math.nextafter(f, -math.inf if lower else math.inf)
    if not math.isfinite(f):
        raise ValueError('DISPLAY_OVERFLOW')
    return f


@dataclass(frozen=True)
class E:
    lo: Q
    hi: Q

    def __post_init__(self):
        object.__setattr__(self, 'lo', Q(self.lo))
        object.__setattr__(self, 'hi', Q(self.hi))
        if self.lo > self.hi:
            raise ValueError('REVERSED_INTERVAL')

    @staticmethod
    def point(x):
        return E(Q(x), Q(x))

    @staticmethod
    def leaf(s):
        return E.point(Q(unbits(s)))

    @staticmethod
    def saved(d):
        lo, hi = unbits(d['lo_bits']), unbits(d['hi_bits'])
        if bits(float(d['lo'])) != d['lo_bits'].lower() or bits(float(d['hi'])) != d['hi_bits'].lower():
            raise ValueError('PRINTED_ENDPOINT_BITS_MISMATCH')
        return E(Q(lo), Q(hi))

    def __add__(self, other):
        b = other if isinstance(other, E) else E.point(other)
        return E(self.lo + b.lo, self.hi + b.hi)

    __radd__ = __add__

    def __neg__(self):
        return E(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -(other if isinstance(other, E) else E.point(other))

    def __rsub__(self, other):
        return E.point(other) - self

    def __mul__(self, other):
        b = other if isinstance(other, E) else E.point(other)
        v = (self.lo*b.lo, self.lo*b.hi, self.hi*b.lo, self.hi*b.hi)
        return E(min(v), max(v))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = other if isinstance(other, E) else E.point(other)
        if b.lo <= 0 <= b.hi:
            raise ValueError('ZERO_IN_DIVISOR')
        return self * E(1/b.hi, 1/b.lo)

    def __rtruediv__(self, other):
        return E.point(other) / self

    def sign(self):
        return 'STRICT_NEGATIVE' if self.hi < 0 else 'STRICT_POSITIVE' if self.lo > 0 else 'ZERO_CONTAINING'

    def contains(self, other):
        return self.lo <= other.lo and other.hi <= self.hi

    def overlap(self, other):
        return self.lo <= other.hi and other.lo <= self.hi

    def binary_enclosure(self):
        return E.point(outward(self.lo, True)) + E(0, Q(outward(self.hi, False))-Q(outward(self.lo, True)))

    def serial(self, exact=True):
        lo, hi = outward(self.lo, True), outward(self.hi, False)
        d = {'lo':lo, 'hi':hi, 'lo_bits':bits(lo), 'hi_bits':bits(hi), 'sign':self.sign()}
        if exact:
            d['exact'] = {'lo':[str(self.lo.numerator),str(self.lo.denominator)],
                          'hi':[str(self.hi.numerator),str(self.hi.denominator)]}
        return d


def dot(a, b):
    if len(a) != len(b):
        raise ValueError('DOT_DIMENSION')
    return sum((x*y for x,y in zip(a,b)), E.point(0))


def weighted(p, w, fhat, v, temperature=None):
    if len(v) != 4:
        raise ValueError('VECTOR_DIMENSION')
    if p.lo <= 0 or w.lo <= 0 or fhat.lo < 0:
        raise ValueError('NONPOSITIVE_PHYSICAL_DOMAIN')
    if temperature is not None and temperature.lo <= 0:
        raise ValueError('NONPOSITIVE_TEMPERATURE')
    dparts = v[0]+fhat*v[1]+2*fhat*v[2]
    balance = p*v[3]-w*dparts
    dt = None if temperature is None else temperature/(w*p)*balance
    return {'dparts':dparts, 'B':balance, 'DT':dt}


def validate_saved_intervals(obj):
    count = 0
    if isinstance(obj, dict):
        if 'lo_bits' in obj and 'hi_bits' in obj:
            E.saved(obj)
            count += 1
        for v in obj.values():
            count += validate_saved_intervals(v)
    elif isinstance(obj, list):
        for v in obj:
            count += validate_saved_intervals(v)
    return count
