"""Finite positive HI measure massive-stress consumer; all energies are eV.

No source history, density, rest-energy ledger, or thermal heat is inferred.
Only individual terms use general rational denominators. Accumulation is integer
on a dynamic dyadic grid; derived endpoint arithmetic has bounded-size inputs.
"""
from fractions import Fraction
import math
import sys


def rational(value):
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite input")
        return Fraction.from_float(value)
    try:
        return Fraction(value)
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError("invalid finite rational input") from exc


def record(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def from_record(value):
    return Fraction(int(value["numerator"]), int(value["denominator"]))


class Interval:
    def __init__(self, lo, hi):
        self.lo, self.hi = rational(lo), rational(hi)
        if self.lo > self.hi:
            raise ValueError("reversed interval")

    @classmethod
    def point(cls, value):
        return cls(value, value)

    def scale(self, scalar):
        scalar = rational(scalar)
        a, b = self.lo * scalar, self.hi * scalar
        return Interval(min(a, b), max(a, b))

    def __add__(self, other):
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other):
        return Interval(self.lo - other.hi, self.hi - other.lo)

    def divide_positive(self, other):
        if other.lo <= 0:
            raise ValueError("positive denominator interval required")
        products = [a / b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return Interval(min(products), max(products))

    def contains(self, value):
        return self.lo <= value <= self.hi

    def nested_in(self, other):
        return other.lo <= self.lo <= self.hi <= other.hi

    def certified(self):
        try:
            left, right = float(self.lo), float(self.hi)
        except OverflowError as exc:
            raise OverflowError("binary64 output overflow") from exc
        if not math.isfinite(left) or not math.isfinite(right):
            raise OverflowError("binary64 output overflow")
        exact_zero = self.lo == self.hi == 0
        # Numeric equality identifies -0.0 with +0.0; a rounding certificate
        # must retain the sign bit, including a tiny enclosure across zero.
        if left != right or left.hex() != right.hex():
            return {"status": "ROUNDING_UNRESOLVED", "value": None,
                    "tag": "enclosure_unresolved", "exact_zero": False}
        if exact_zero:
            tag = "exact_zero"
        elif left == 0 and (self.hi < 0 or self.lo > 0):
            tag = "final_underflow_to_zero"
        elif left == 0:
            tag = "zero_in_enclosure"
        elif abs(left) < sys.float_info.min:
            tag = "subnormal"
        else:
            tag = "normal"
        return {"status": "CERTIFIED_BINARY64", "value": left,
                "tag": tag, "exact_zero": exact_zero}

    def payload(self):
        return {"lo": record(self.lo), "hi": record(self.hi),
                "width": record(self.hi - self.lo), "rounding": self.certified()}


def floor_log2(value):
    if value <= 0:
        raise ValueError("positive value required")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    power = Fraction(2 ** exponent) if exponent >= 0 else Fraction(1, 2 ** -exponent)
    return exponent if value >= power else exponent - 1


def enclose(terms, precision):
    """Direct signed exact-term enclosure; never sum general Fractions."""
    if precision not in (128, 160):
        raise ValueError("only frozen P128/P160 allowed")
    terms = [rational(term) for term in terms]
    largest = max((abs(term) for term in terms), default=Fraction(0))
    if largest == 0:
        return Interval.point(0), {"N": len(terms), "P": precision, "E": None,
                                   "delta": record(Fraction(0)), "width_bound_pass": True}
    exponent = floor_log2(largest)
    shift = exponent - precision
    delta = Fraction(2 ** shift) if shift >= 0 else Fraction(1, 2 ** -shift)
    lower_integer = upper_integer = 0
    for term in terms:
        numerator = term.numerator * delta.denominator
        denominator = term.denominator * delta.numerator
        lower_integer += numerator // denominator
        upper_integer += -((-numerator) // denominator)
    interval = Interval(lower_integer * delta, upper_integer * delta)
    bound_pass = interval.hi - interval.lo <= len(terms) * delta
    if not bound_pass:
        raise ArithmeticError("dyadic width bound failed")
    return interval, {"N": len(terms), "P": precision, "E": exponent,
                      "delta": record(delta), "width_bound_pass": bound_pass}


def massive_terms(atoms, mass):
    mass = rational(mass)
    if mass <= 0:
        raise ValueError("mass must be positive")
    stress, derivative = [], []
    for kinetic, weight in atoms:
        kinetic, weight = rational(kinetic), rational(weight)
        if kinetic < 0 or weight < 0:
            raise ValueError("kinetic energy and positive-measure weight must be nonnegative")
        denominator = kinetic + mass
        stress.append(weight * kinetic * (kinetic + 2 * mass) / denominator)
        derivative.append(weight * kinetic * kinetic / (denominator * denominator))
    return stress, derivative


def pressure_source(stress, derivative, a, X, da, dX, dM):
    a, X, da, dX, dM = map(rational, (a, X, da, dX, dM))
    if a < 0 or X < 0:
        raise ValueError("nonnegative source amplitudes required")
    amplitude, direction = a * X, a * dX + X * da
    return {"pressure": stress.scale(Fraction(1, 3)),
            "source": stress.scale(amplitude / 3),
            "jvp": stress.scale(direction / 3) + derivative.scale(amplitude * dM / 3),
            "flux": [0, 0, 0], "STF": [0, 0, 0, 0, 0], "thermal_heat": None}
