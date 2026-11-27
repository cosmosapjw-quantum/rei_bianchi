"""Directed Decimal intervals and second derivatives for E13C4.

Basic operations use explicit FLOOR/CEILING contexts. Decimal exp/ln are
correctly rounded HALF_EVEN (Python 3.12 contract); the immediate neighbours
enclose the exact result. sqrt additionally checks its square inequalities.
No operation relies on the ambient Decimal precision or noninteger power.
This module is a small transparent enclosure implementation, not formal proof
assistant software. Overflow, underflow, invalid domains and NaN are errors.
"""
from decimal import (Decimal as D, Context, ROUND_FLOOR, ROUND_CEILING,
                     ROUND_HALF_EVEN, InvalidOperation, DivisionByZero,
                     Overflow, Underflow, Subnormal, Clamped, FloatOperation)


def configure(precision=60):
    global DOWN, UP, NEAR, PRECISION, COUNTS
    if not 30 <= precision <= 150:
        raise ValueError('supported precision range is 30..150')
    PRECISION = precision
    DOWN = Context(prec=precision, rounding=ROUND_FLOOR, Emin=-999999, Emax=999999)
    UP = Context(prec=precision, rounding=ROUND_CEILING, Emin=-999999, Emax=999999)
    NEAR = Context(prec=precision, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999)
    for ctx in (DOWN, UP, NEAR):
        for signal in (InvalidOperation, DivisionByZero, Overflow, Underflow,
                       Subnormal, Clamped, FloatOperation):
            ctx.traps[signal] = True
    COUNTS = {'exp_endpoint_calls': 0, 'ln_endpoint_calls': 0,
              'sqrt_endpoint_calls': 0, 'sqrt_exact_square_checks': 0}


configure()


def exact(value):
    if isinstance(value, float):
        raise TypeError('Use explicit from_binary64 for captured floats')
    return value if isinstance(value, D) else D(value)


class IV:
    __slots__ = ('lo', 'hi')

    def __init__(self, lo=0, hi=None):
        if isinstance(lo, IV):
            if hi is not None:
                raise TypeError('upper endpoint with interval input')
            self.lo, self.hi = lo.lo, lo.hi
        else:
            self.lo = exact(lo)
            self.hi = self.lo if hi is None else exact(hi)
        if not self.lo.is_finite() or not self.hi.is_finite() or self.lo > self.hi:
            raise ArithmeticError('nonfinite or reversed interval')

    @classmethod
    def from_binary64(cls, value):
        return cls(D.from_float(float(value)))

    def __add__(self, other):
        if isinstance(other, Jet2):
            return NotImplemented
        b = IV(other)
        return IV(DOWN.add(self.lo, b.lo), UP.add(self.hi, b.hi))

    __radd__ = __add__

    def __neg__(self):
        return IV(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        if isinstance(other, Jet2):
            return NotImplemented
        return self + (-IV(other))

    def __rsub__(self, other):
        return IV(other) + (-self)

    def __mul__(self, other):
        if isinstance(other, Jet2):
            return NotImplemented
        b = IV(other)
        if self.lo == self.hi == 0 or b.lo == b.hi == 0:
            return IV(0)
        pairs = [(a, c) for a in (self.lo, self.hi) for c in (b.lo, b.hi)]
        return IV(min(DOWN.multiply(a, c) for a, c in pairs),
                  max(UP.multiply(a, c) for a, c in pairs))

    __rmul__ = __mul__

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ArithmeticError('division interval contains zero')
        return IV(DOWN.divide(D(1), self.hi), UP.divide(D(1), self.lo))

    def __truediv__(self, other):
        if isinstance(other, Jet2):
            return NotImplemented
        return self * IV(other).reciprocal()

    def __rtruediv__(self, other):
        return IV(other) * self.reciprocal()

    def square(self):
        if self.lo >= 0:
            return IV(DOWN.multiply(self.lo, self.lo), UP.multiply(self.hi, self.hi))
        if self.hi <= 0:
            return IV(DOWN.multiply(self.hi, self.hi), UP.multiply(self.lo, self.lo))
        return IV(0, max(UP.multiply(self.lo, self.lo), UP.multiply(self.hi, self.hi)))

    def __abs__(self):
        if self.lo >= 0:
            return IV(self)
        if self.hi <= 0:
            return -self
        return IV(0, max(self.lo.copy_abs(), self.hi.copy_abs()))

    def exp(self):
        def endpoint(x, lower):
            if x == 0:
                return D(1)
            COUNTS['exp_endpoint_calls'] += 1
            rounded = NEAR.exp(x)
            return NEAR.next_minus(rounded) if lower else NEAR.next_plus(rounded)
        return IV(endpoint(self.lo, True), endpoint(self.hi, False))

    def ln(self):
        if self.lo <= 0:
            raise ArithmeticError('log interval is not strictly positive')
        def endpoint(x, lower):
            if x == 1:
                return D(0)
            COUNTS['ln_endpoint_calls'] += 1
            rounded = NEAR.ln(x)
            return NEAR.next_minus(rounded) if lower else NEAR.next_plus(rounded)
        return IV(endpoint(self.lo, True), endpoint(self.hi, False))

    def sqrt(self):
        if self.lo < 0:
            raise ArithmeticError('negative square root domain')
        def endpoint(x, lower):
            if x == 0:
                return D(0)
            COUNTS['sqrt_endpoint_calls'] += 1
            rounded = NEAR.sqrt(x)
            out = NEAR.next_minus(rounded) if lower else NEAR.next_plus(rounded)
            if lower:
                valid = out >= 0 and UP.multiply(out, out) <= x
            else:
                valid = DOWN.multiply(out, out) >= x
            if not valid:
                raise ArithmeticError('sqrt enclosure square check failed')
            COUNTS['sqrt_exact_square_checks'] += 1
            return out
        return IV(endpoint(self.lo, True), endpoint(self.hi, False))

    def positive_power(self, exponent):
        return (self.ln() * IV(exponent)).exp()

    def intersect_nonnegative(self):
        """Only call after an independently stated nonnegativity theorem."""
        if self.hi < 0:
            raise ArithmeticError('nonnegative-theorem intersection empty')
        return IV(max(self.lo, D(0)), self.hi)

    def contains(self, value):
        value = exact(value)
        return self.lo <= value <= self.hi

    def width(self):
        return UP.subtract(self.hi, self.lo)

    def json(self):
        return {'lo': str(self.lo), 'hi': str(self.hi)}

    def __repr__(self):
        return f'IV({self.lo!r}, {self.hi!r})'


class Jet2:
    """Function value, first derivative, and actual second derivative in t."""
    __slots__ = ('v', 'd1', 'd2')

    def __init__(self, value=0, d1=0, d2=0):
        if isinstance(value, Jet2):
            self.v, self.d1, self.d2 = value.v, value.d1, value.d2
        else:
            self.v, self.d1, self.d2 = IV(value), IV(d1), IV(d2)

    @classmethod
    def variable(cls, value):
        return cls(value, 1, 0)

    def __add__(self, other):
        b = Jet2(other)
        return Jet2(self.v + b.v, self.d1 + b.d1, self.d2 + b.d2)

    __radd__ = __add__

    def __neg__(self):
        return Jet2(-self.v, -self.d1, -self.d2)

    def __sub__(self, other):
        return self + (-Jet2(other))

    def __rsub__(self, other):
        return Jet2(other) + (-self)

    def __mul__(self, other):
        b = Jet2(other)
        return Jet2(self.v * b.v, self.d1 * b.v + self.v * b.d1,
                    self.d2 * b.v + 2 * self.d1 * b.d1 + self.v * b.d2)

    __rmul__ = __mul__

    def reciprocal(self):
        inv = self.v.reciprocal()
        return Jet2(inv, -self.d1 * inv.square(),
                    2 * self.d1.square() * inv.square() * inv - self.d2 * inv.square())

    def __truediv__(self, other):
        return self * Jet2(other).reciprocal()

    def __rtruediv__(self, other):
        return Jet2(other) * self.reciprocal()

    def square(self):
        return Jet2(self.v.square(), 2 * self.v * self.d1,
                    2 * self.d1.square() + 2 * self.v * self.d2)

    def exp(self):
        val = self.v.exp()
        return Jet2(val, val * self.d1, val * (self.d2 + self.d1.square()))

    def ln(self):
        inv = self.v.reciprocal()
        ratio = self.d1 * inv
        return Jet2(self.v.ln(), ratio, self.d2 * inv - ratio.square())

    def sqrt(self):
        if self.v.lo <= 0:
            raise ArithmeticError('Jet2 sqrt requires positive smooth domain')
        val = self.v.sqrt()
        return Jet2(val, self.d1 / (2 * val),
                    self.d2 / (2 * val) - self.d1.square() / (4 * val.square() * val))

    def positive_power(self, exponent):
        return (self.ln() * Jet2(exponent)).exp()


def value(x):
    return x.v if isinstance(x, Jet2) else IV(x)


def response_j(rate, width):
    """J(rate,width). rate is an interval enclosing a fixed nonnegative rate."""
    rate = IV(rate)
    if value(width).lo < 0:
        raise ArithmeticError('J requires nonnegative width')
    if rate.lo == rate.hi == 0:
        return width
    if rate.lo <= 0:
        raise ArithmeticError('J requires positive rate and nonnegative width')
    return (1 - (-rate * width).exp()) / rate
