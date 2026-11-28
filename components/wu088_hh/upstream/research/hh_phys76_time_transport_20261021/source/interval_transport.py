"""Conditional continuous-time scalar transport enclosures.

Inputs are whole-cell enclosures supplied by an independent producer, not samples.
The arithmetic uses correctly rounded Decimal operations and outward endpoints.
Every result remains conditional_on_input_enclosures; this module cannot validate
the physical or analytic provenance of a supplied enclosure witness.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    Context, Decimal, DivisionByZero, FloatOperation, InvalidOperation, Overflow,
    ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, Subnormal, Underflow,
)
from collections.abc import Mapping


@dataclass(frozen=True)
class _Interval:
    lo: Decimal
    hi: Decimal

    def strings(self):
        return [str(self.lo), str(self.hi)]


def _decimal(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("FINITE_DECIMAL_STRING_REQUIRED")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("FINITE_DECIMAL_STRING_REQUIRED") from exc
    if not result.is_finite():
        raise ValueError("FINITE_DECIMAL_STRING_REQUIRED")
    return result


def _interval(values):
    if not isinstance(values, (list, tuple)) or len(values) != 2:
        raise ValueError("TWO_DECIMAL_ENDPOINTS_REQUIRED")
    lo, hi = map(_decimal, values)
    if lo > hi:
        raise ValueError("ORDERED_INTERVAL_REQUIRED")
    return _Interval(lo, hi)


def _witness(value, scope):
    required = ("source_identity", "method", "locator")
    if not isinstance(value, Mapping) or value.get("scope") != scope:
        raise ValueError("EXPLICIT_ENCLOSURE_WITNESS_REQUIRED")
    if any(not isinstance(value.get(k), str) or not value[k].strip() for k in required):
        raise ValueError("EXPLICIT_ENCLOSURE_WITNESS_REQUIRED")
    return {"scope": scope, **{k: value[k] for k in required}}


class _Arithmetic:
    def __init__(self, precision):
        if isinstance(precision, bool) or not isinstance(precision, int) or not 16 <= precision <= 10000:
            raise ValueError("PRECISION_INTEGER_16_TO_10000_REQUIRED")
        traps = [InvalidOperation, DivisionByZero, Overflow, Underflow, Subnormal, FloatOperation]
        self.down = Context(prec=precision, rounding=ROUND_FLOOR, traps=traps)
        self.up = Context(prec=precision, rounding=ROUND_CEILING, traps=traps)
        self.near = Context(prec=precision, rounding=ROUND_HALF_EVEN, traps=traps)
        self.precision = precision
        self.zero = _Interval(Decimal(0), Decimal(0))
        self.one = _Interval(Decimal(1), Decimal(1))

    def add(self, x, y):
        return _Interval(self.down.add(x.lo, y.lo), self.up.add(x.hi, y.hi))

    def negate(self, x):
        # copy_negate is exact and does not silently apply ambient precision.
        return _Interval(x.hi.copy_negate(), x.lo.copy_negate())

    def subtract(self, x, y):
        return self.add(x, self.negate(y))

    def multiply(self, x, y):
        pairs = [(a, b) for a in (x.lo, x.hi) for b in (y.lo, y.hi)]
        return _Interval(min(self.down.multiply(a, b) for a, b in pairs),
                         max(self.up.multiply(a, b) for a, b in pairs))

    def divide(self, x, y):
        if y.lo <= 0 <= y.hi:
            raise ValueError("INTERVAL_DIVISOR_CONTAINS_ZERO")
        pairs = [(a, b) for a in (x.lo, x.hi) for b in (y.lo, y.hi)]
        return _Interval(min(self.down.divide(a, b) for a, b in pairs),
                         max(self.up.divide(a, b) for a, b in pairs))

    def exp(self, x):
        # Decimal.exp is correctly rounded to nearest, regardless of context
        # rounding. One representable neighbor on each side encloses that error.
        lo = Decimal(1) if x.lo == 0 else x.lo.exp(context=self.near).next_minus(context=self.down)
        hi = Decimal(1) if x.hi == 0 else x.hi.exp(context=self.near).next_plus(context=self.up)
        # next_minus/next_plus are quiet at exponent boundaries, so their
        # subnormal results require an explicit check in addition to traps.
        if (not lo.is_finite() or not hi.is_finite() or lo <= 0
                or lo.is_subnormal(context=self.down)
                or hi.is_subnormal(context=self.up)):
            raise ArithmeticError("EXP_ENCLOSURE_OUTSIDE_REPRESENTABLE_RANGE")
        return _Interval(lo, hi)

    def phi1_small(self, x):
        """Enclose sum x**k/(k+1)! for |x|<=1/8 with a geometric tail."""
        u = max(x.lo.copy_abs(), x.hi.copy_abs())
        if u > Decimal("0.125"):
            raise ValueError("SMALL_PHI_DOMAIN_REQUIRED")
        term = total = self.one
        abs_term = Decimal(1)
        target = Decimal("1e-" + str(self.precision + 8))
        for k in range(self.precision * 2 + 64):
            # The next term has degree k+1 and denominator (k+2)!.
            next_abs = self.up.divide(self.up.multiply(abs_term, u), Decimal(k + 2))
            ratio = self.up.divide(u, Decimal(k + 3))
            tail = self.up.divide(next_abs, self.down.subtract(Decimal(1), ratio))
            if tail <= target:
                return self.add(total, _Interval(tail.copy_negate(), tail))
            term = self.divide(self.multiply(term, x),
                               _Interval(Decimal(k + 2), Decimal(k + 2)))
            total = self.add(total, term)
            abs_term = next_abs
        raise ArithmeticError("PHI_SERIES_REMAINDER_NOT_REACHED")

    def response_point(self, a, h):
        """Phi(a,h)=integral_0^h exp(-a*u)du, for exact decimal a,h."""
        hi = _Interval(h, h)
        if a == 0:
            return hi
        ai = _Interval(a, a)
        x = self.negate(self.multiply(ai, hi))
        if max(x.lo.copy_abs(), x.hi.copy_abs()) <= Decimal("0.125"):
            out = self.multiply(hi, self.phi1_small(x))
        else:
            out = self.divide(self.subtract(self.one, self.exp(x)), ai)
        if out.hi <= 0:
            raise ArithmeticError("NONPOSITIVE_RESPONSE_UPPER_BOUND")
        # The exact integral is positive; intersecting with [0,+infinity) is safe.
        return _Interval(max(Decimal(0), out.lo), out.hi)

    def propagators(self, a, h):
        hi = _Interval(h, h)
        g = self.exp(self.negate(self.multiply(a, hi)))
        # Phi is decreasing in a for every real a and h>0.
        lower = self.response_point(a.hi, h).lo
        upper = self.response_point(a.lo, h).hi
        return g, _Interval(lower, upper)


def propagate(cells, initial_s, initial_witness, precision=60):
    """Enclose initial, matter, radiation and total signed shear at cell ends.

    Each cell is {h: decimal_string, A: [lo,hi], P_m: [lo,hi],
    P_r: [lo,hi], witness: {scope:'entire_cell', source_identity, method, locator}}.
    Initial witness uses scope='initial_value'. The positive h sequence defines
    contiguous abstract cells; witnesses must bind these cells to the physical
    coordinate, common normal frame, equations and source identities.

    Certificate validity of those witnesses is not inferred by this function.
    All results have status='conditional_on_input_enclosures'. No sampled-history
    inputs are accepted or converted into continuum bounds here.
    """
    arithmetic = _Arithmetic(precision)
    if not isinstance(cells, (list, tuple)) or not cells:
        raise ValueError("NONEMPTY_CELL_SEQUENCE_REQUIRED")
    initial = _interval(initial_s)
    iw = _witness(initial_witness, "initial_value")
    parsed = []
    for cell in cells:
        if not isinstance(cell, Mapping):
            raise ValueError("CELL_MAPPING_REQUIRED")
        try:
            h = _decimal(cell["h"])
            if h <= 0:
                raise ValueError("POSITIVE_CELL_WIDTH_REQUIRED")
            parsed.append((h, _interval(cell["A"]), _interval(cell["P_m"]),
                           _interval(cell["P_r"]), _witness(cell["witness"], "entire_cell")))
        except KeyError as exc:
            raise ValueError("CELL_FIELDS_REQUIRED") from exc
    d, jm, jr = initial, arithmetic.zero, arithmetic.zero

    def record(index):
        total = arithmetic.add(arithmetic.add(d, jm), jr)
        return {"index": index, "initial_memory": d.strings(),
                "matter_memory": jm.strings(), "radiation_memory": jr.strings(),
                "total_signed_shear": total.strings()}

    nodes = [record(0)]
    kernels = []
    for index, (h, a, pm, pr, witness) in enumerate(parsed, 1):
        g, response = arithmetic.propagators(a, h)
        d = arithmetic.multiply(g, d)
        jm = arithmetic.add(arithmetic.multiply(g, jm), arithmetic.multiply(response, pm))
        jr = arithmetic.add(arithmetic.multiply(g, jr), arithmetic.multiply(response, pr))
        kernels.append({"index": index, "h": str(h), "A": a.strings(),
                        "P_m": pm.strings(), "P_r": pr.strings(),
                        "G": g.strings(), "R": response.strings(), "witness": witness})
        nodes.append(record(index))
    return {"schema": "PHYS76_CONDITIONAL_TIME_TRANSPORT_V1",
            "status": "conditional_on_input_enclosures", "precision_decimal_digits": precision,
            "arithmetic": "Decimal directed endpoints; correctly-rounded exp with neighboring bounds",
            "initial_witness": iw, "input_witnesses_verified": False,
            "physics": "signed half-contraction LRS coordinates, same normal frame; A=2-q",
            "HH_R10": "OFF", "production": "NOT_ISSUED",
            "nodes": nodes, "cell_propagators": kernels}
