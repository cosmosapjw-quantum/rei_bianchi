"""Outward Decimal intervals, including certified ln/exp/sqrt endpoint expansion.

Basic arithmetic uses directed contexts.  Python Decimal documents ln and exp
as correctly rounded to ROUND_HALF_EVEN; expanding that value by one adjacent
representable number encloses the exact endpoint.  No Decimal.power is used.
All input rationals are enclosed before evaluation.  This module has no
physical inputs or scientific calls at import time.
"""
from decimal import (Decimal, Context, ROUND_FLOOR, ROUND_CEILING,
                     ROUND_HALF_EVEN, InvalidOperation, DivisionByZero,
                     Overflow, Underflow)
from fractions import Fraction


class Arithmetic:
    def __init__(self, digits=90):
        self.digits = digits
        self.down = Context(prec=digits, rounding=ROUND_FLOOR)
        self.up = Context(prec=digits, rounding=ROUND_CEILING)
        self.near = Context(prec=digits, rounding=ROUND_HALF_EVEN)
        for ctx in (self.down, self.up, self.near):
            for signal in (InvalidOperation, DivisionByZero, Overflow, Underflow):
                ctx.traps[signal] = True
        self.elementary_endpoint_calls = {'ln': 0, 'exp': 0, 'sqrt': 0}

    def interval(self, value, upper=None):
        if isinstance(value, Interval):
            if value.ar is not self:
                raise ValueError('Mixed interval arithmetic contexts')
            if upper is not None:
                raise ValueError('Unexpected upper endpoint')
            return value
        if upper is not None:
            lo = self.interval(value).lo
            hi = self.interval(upper).hi
        elif isinstance(value, Fraction):
            n, d = Decimal(value.numerator), Decimal(value.denominator)
            lo, hi = self.down.divide(n, d), self.up.divide(n, d)
        else:
            if isinstance(value, float):
                raise TypeError('No implicit binary float intervals')
            lo = hi = Decimal(value)
        return Interval(self, lo, hi)

    def endpoint(self, kind, value, direction):
        self.elementary_endpoint_calls[kind] += 1
        # Exact mathematical special cases avoid introducing a subnormal
        # next-number interval around the exactly known zero log(1).
        if kind == 'ln' and value == 1:
            return Decimal(0)
        if kind == 'exp' and value == 0:
            return Decimal(1)
        rounded = getattr(self.near, kind)(value)
        if not rounded.is_finite():
            raise ArithmeticError('Nonfinite elementary result')
        return (self.near.next_minus(rounded) if direction < 0
                else self.near.next_plus(rounded))


class Interval:
    __slots__ = ('ar', 'lo', 'hi')

    def __init__(self, arithmetic, lo, hi):
        if not lo.is_finite() or not hi.is_finite() or lo > hi:
            raise ValueError('Invalid finite interval')
        self.ar, self.lo, self.hi = arithmetic, lo, hi

    def __add__(self, other):
        other = self.ar.interval(other)
        return Interval(self.ar, self.ar.down.add(self.lo, other.lo),
                        self.ar.up.add(self.hi, other.hi))

    __radd__ = __add__

    def __neg__(self):
        return Interval(self.ar, self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + -self.ar.interval(other)

    def __rsub__(self, other):
        return self.ar.interval(other) + -self

    def __mul__(self, other):
        other = self.ar.interval(other)
        pairs = ((a, b) for a in (self.lo, self.hi)
                 for b in (other.lo, other.hi))
        pairs = tuple(pairs)
        lows = [self.ar.down.multiply(a, b) for a, b in pairs]
        highs = [self.ar.up.multiply(a, b) for a, b in pairs]
        return Interval(self.ar, min(lows), max(highs))

    __rmul__ = __mul__

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError('Interval denominator contains zero')
        return Interval(self.ar, self.ar.down.divide(Decimal(1), self.hi),
                        self.ar.up.divide(Decimal(1), self.lo))

    def __truediv__(self, other):
        return self * self.ar.interval(other).reciprocal()

    def __rtruediv__(self, other):
        return self.ar.interval(other) * self.reciprocal()

    def __pow__(self, exponent):
        if not isinstance(exponent, int):
            raise TypeError('Use real_power for noninteger exponents')
        if exponent < 0:
            return (self ** (-exponent)).reciprocal()
        if exponent == 0:
            return self.ar.interval(1)
        if exponent == 2:
            if self.lo <= 0 <= self.hi:
                low = Decimal(0)
            else:
                low = min(self.ar.down.multiply(self.lo, self.lo),
                          self.ar.down.multiply(self.hi, self.hi))
            high = max(self.ar.up.multiply(self.lo, self.lo),
                       self.ar.up.multiply(self.hi, self.hi))
            return Interval(self.ar, low, high)
        result, base, n = self.ar.interval(1), self, exponent
        while n:
            if n & 1:
                result = result * base
            n //= 2
            if n:
                base = base * base
        return result

    def ln(self):
        if self.lo <= 0:
            raise ValueError('Logarithm requires strictly positive interval')
        return Interval(self.ar, self.ar.endpoint('ln', self.lo, -1),
                        self.ar.endpoint('ln', self.hi, 1))

    def exp(self):
        return Interval(self.ar, self.ar.endpoint('exp', self.lo, -1),
                        self.ar.endpoint('exp', self.hi, 1))

    def sqrt(self):
        if self.lo <= 0:
            raise ValueError('This positive-domain sqrt excludes zero')
        return Interval(self.ar, self.ar.endpoint('sqrt', self.lo, -1),
                        self.ar.endpoint('sqrt', self.hi, 1))

    def real_power(self, exponent):
        return (self.ln() * self.ar.interval(exponent)).exp()

    def abs_upper(self):
        return max(self.lo.copy_abs(), self.hi.copy_abs())

    def overlaps(self, other):
        other = self.ar.interval(other)
        return max(self.lo, other.lo) <= min(self.hi, other.hi)

    def contains_rational(self, value):
        value = Fraction(value)
        return Fraction(self.lo) <= value <= Fraction(self.hi)

    def as_json(self):
        return {'lower': str(self.lo), 'upper': str(self.hi)}


class EnergyJet:
    """Ordinary Taylor coefficients phi(E+u), with exact rational exponents.

    Independent of the rational-polynomial-in-sqrt(E) derivative recurrence.
    Constant term in the remainder is set exactly to zero, as a coefficient
    identity, rather than subtracting two interval copies of a constant.
    """
    def __init__(self, arithmetic, coeffs, order=6):
        self.ar, self.order = arithmetic, order
        if len(coeffs) > order + 1:
            raise ValueError('Jet degree overflow')
        self.c = [arithmetic.interval(v) for v in coeffs]
        self.c += [arithmetic.interval(0) for _ in range(order + 1-len(self.c))]

    def lift(self, value):
        if isinstance(value, EnergyJet):
            if value.ar is not self.ar or value.order != self.order:
                raise ValueError('Mixed jets')
            return value
        return EnergyJet(self.ar, [value], self.order)

    def __add__(self, other):
        other = self.lift(other)
        return EnergyJet(self.ar, [a+b for a, b in zip(self.c, other.c)], self.order)

    __radd__ = __add__

    def __neg__(self):
        return EnergyJet(self.ar, [-v for v in self.c], self.order)

    def __sub__(self, other):
        return self + -self.lift(other)

    def __rsub__(self, other):
        return self.lift(other) + -self

    def __mul__(self, other):
        other = self.lift(other)
        return EnergyJet(self.ar, [sum((self.c[j]*other.c[n-j]
                            for j in range(n+1)), self.ar.interval(0))
                            for n in range(self.order+1)], self.order)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        if isinstance(scalar, EnergyJet):
            raise TypeError('Only interval scalar division is needed')
        return EnergyJet(self.ar, [c/scalar for c in self.c], self.order)

    def power(self, exponent):
        exponent = Fraction(exponent)
        base = self.c[0]
        if base.lo <= 0:
            raise ValueError('Positive jet base required')
        rem = EnergyJet(self.ar, [0]+[c/base for c in self.c[1:]], self.order)
        term, total, binomial = self.lift(1), self.lift(1), Fraction(1)
        for j in range(1, self.order+1):
            term = term * rem
            binomial *= (exponent-j+1)/j
            total = total + term*self.ar.interval(binomial)
        return total*base.real_power(exponent)
