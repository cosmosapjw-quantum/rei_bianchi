#!/usr/bin/env python3
"""Independent R14 reference, authored without execution.

Read frozen CASES.json, FIXTURE_SOURCE.json and saved PRIMARY_RESULTS.json only.
No production/predecessor imports, dynamic import, eval, subprocess, ODE, or CAS.
Exact J0/J1/J2 primitives and power interpolation are independent of positive
Simpson assembly. Decimal160 monomial moments and analytic quadratic roots are
independent of production Bernstein moments and bisection. The frozen 1e-80
relative guard is numerical corroboration, not interval-reference arithmetic.
The root runner meters the single execution externally.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from math import isqrt
from pathlib import Path
import sys
import traceback

PRECISION = 160
RELATIVE_GUARD = Decimal("1e-80")
PHI_THRESHOLD = Decimal("1e-12")
PHI_STOP = Decimal("1e-150")
PHI_TERMS = 512
BITS = 128
ROOT_DEPTH = 96
SCALE = 1 << BITS
MAX_SOURCE = 16
MAX_OBSERVATION = 32
MAX_EFFECTIVE = 48
MAX_BASE = 512
MAX_BLOCKS = 8
MAX_OVERLAP = 250000
MAX_ROOT_STEPS = 98304
MAX_DERIVED_BITS = 16384
MAX_SAVED_RATIONAL_TEXT = 10000
INTEGER_DECIMAL_DIGIT_LIMIT = 6000
ZERO = Fraction(0)
ONE = Fraction(1)


def ascii_signed_integer(text):
    """Independent ASCII grammar check before any integer/Fraction conversion."""
    if not text:
        raise ValueError("Rational text requires an ASCII signed integer or p/q")
    digits = text[1:] if text[0] in "+-" else text
    if (not digits or len(digits) > INTEGER_DECIMAL_DIGIT_LIMIT or
            any(character < "0" or character > "9" for character in digits)):
        raise ValueError("Rational text requires bounded ASCII signed integers")
    return int(text)


def rat(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, Fraction)):
        raise ValueError("Exact rational text/integer required")
    if isinstance(value, str):
        if len(value) > MAX_SAVED_RATIONAL_TEXT:
            raise ValueError("Saved rational text exceeds 10000 characters")
        pieces = value.split("/")
        if len(pieces) not in (1, 2):
            raise ValueError("Rational text requires an ASCII signed integer or p/q")
        numerator = ascii_signed_integer(pieces[0])
        denominator = ascii_signed_integer(pieces[1]) if len(pieces) == 2 else 1
        result = Fraction(numerator, denominator)
        if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_DERIVED_BITS:
            raise ValueError("Saved rational exceeds 16384 derived bits")
        return result
    return Fraction(value)


def input_rat(value):
    if isinstance(value, str) and len(value) > 2048:
        raise ValueError("Input rational text length exceeds finite limit")
    result = rat(value)
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > 256:
        raise ValueError("Input rational exceeds 256 bits")
    return result


def dec(value):
    if isinstance(value, Decimal):
        return value
    value = rat(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def json_safe(value):
    if isinstance(value, (Fraction, Decimal)):
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    return value


def display(value):
    text = json.dumps(json_safe(value), sort_keys=True, ensure_ascii=False)
    return text if len(text) <= 1200 else text[:1200] + "..."


def down(value):
    value = rat(value)
    return Fraction((value.numerator * SCALE) // value.denominator, SCALE)


def up(value):
    value = rat(value)
    return Fraction(-((-value.numerator * SCALE) // value.denominator), SCALE)


def sign(value):
    return (value > 0) - (value < 0)


def power_value(coefficients, x):
    value = ZERO
    for coefficient in reversed(coefficients):
        value = value * x + coefficient
    return value


def quadratic_power(coefficients):
    b0, b1, b2 = coefficients
    return b0, 2 * (b1 - b0), b0 - 2 * b1 + b2


def cubic_bernstein(coefficients):
    a0, a1, a2, a3 = coefficients
    return (a0, a0 + a1 / 3, a0 + 2 * a1 / 3 + a2 / 3,
            a0 + a1 + a2 + a3)


def cubic_power(coefficients):
    b0, b1, b2, b3 = coefficients
    return b0, 3 * (b1 - b0), 3 * (b0 - 2 * b1 + b2), -b0 + 3*b1 - 3*b2 + b3


def restrict_power(coefficients, left, right):
    """Independent binomial composition, degree <=3, normalized old coordinate."""
    a = list(coefficients) + [ZERO] * (4 - len(coefficients))
    width = right - left
    return (
        a[0] + a[1]*left + a[2]*left**2 + a[3]*left**3,
        width * (a[1] + 2*a[2]*left + 3*a[3]*left**2),
        width**2 * (a[2] + 3*a[3]*left),
        width**3 * a[3],
    )


def quadratic_min(coefficients):
    a0, a1, a2 = coefficients
    candidates = [a0, a0+a1+a2]
    if a2 > 0:
        vertex = -a1 / (2*a2)
        if 0 < vertex < 1:
            candidates.append(power_value(coefficients, vertex))
    return min(candidates)


def quadratic_max(coefficients):
    a0, a1, a2 = coefficients
    candidates = [a0, a0+a1+a2]
    if a2 < 0:
        vertex = -a1 / (2*a2)
        if 0 < vertex < 1:
            candidates.append(power_value(coefficients, vertex))
    return max(candidates)


class Audit:
    def __init__(self):
        self.counts = Counter()
        self.failed_counts = Counter()
        self.groups = []
        self.failures = []
        self.current = None
        self.strict_decimal_failures = 0
        self.strict_decimal_examples = []

    def group(self, identity):
        self.current = {"id": identity, "components": 0, "failures": 0}
        self.groups.append(self.current)

    def require(self, category, identity, condition, actual=None, expected=None):
        if self.current is None:
            self.group("ungrouped")
        self.counts[category] += 1
        self.current["components"] += 1
        if not condition:
            self.failed_counts[category] += 1
            self.current["failures"] += 1
            if len(self.failures) < 200:
                self.failures.append({
                    "group": self.current["id"], "id": identity,
                    "category": category, "actual": display(actual),
                    "expected": display(expected),
                })

    def equal(self, identity, actual, expected, category="metadata"):
        self.require(category, identity, actual == expected, actual, expected)

    def rational(self, identity, actual, expected, category="exact"):
        try:
            observed = rat(actual)
        except Exception as exc:
            self.require(category, identity, False, repr(exc), expected)
            return
        self.require(category, identity, observed == expected, observed, expected)

    def vector(self, identity, actual, expected, category="exact"):
        if not isinstance(actual, (list, tuple)):
            self.require("metadata", identity+".sequence", False, actual, "list/tuple")
            return
        self.equal(identity+".length", len(actual), len(expected))
        for i, (observed, wanted) in enumerate(zip(actual, expected)):
            if isinstance(wanted, (list, tuple)):
                self.vector(f"{identity}[{i}]", observed, wanted, category)
            else:
                self.rational(f"{identity}[{i}]", observed, wanted, category)

    def decimal_equal(self, identity, a, b, category="Decimal"):
        a, b = dec(a), dec(b)
        guard = RELATIVE_GUARD * max(Decimal(1), abs(a), abs(b))
        self.require(category, identity, abs(a-b) <= guard, a, b)

    def decimal_le(self, identity, a, b, category="Decimal"):
        a, b = dec(a), dec(b)
        guard = RELATIVE_GUARD * max(Decimal(1), abs(a), abs(b))
        self.require(category, identity, a <= b+guard, a, b)

    def between(self, identity, value, lower, upper, category="Decimal"):
        value, lower, upper = dec(value), dec(lower), dec(upper)
        guard = RELATIVE_GUARD * max(Decimal(1), abs(value), abs(lower), abs(upper))
        self.require(category, identity+".lower", lower <= value+guard, value, lower)
        self.require(category, identity+".upper", value <= upper+guard, value, upper)
        if not lower <= value <= upper:
            self.strict_decimal_failures += 1
            if len(self.strict_decimal_examples) < 50:
                self.strict_decimal_examples.append({
                    "group": self.current["id"], "id": identity,
                    "value": str(value), "lower": str(lower), "upper": str(upper),
                    "meaning": "Strict Decimal comparison only; frozen guarded verdict reported separately.",
                })


def phi_values(z):
    """phi1 through phi4: exp/recurrence, frozen small-z series."""
    z = dec(z)
    if not z:
        return (Decimal(1), Decimal(1)/2, Decimal(1)/6, Decimal(1)/24)
    if abs(z) >= PHI_THRESHOLD:
        phi1 = (z.exp() - Decimal(1)) / z
        phi2 = (phi1 - Decimal(1)) / z
        phi3 = (phi2 - Decimal(1)/2) / z
        phi4 = (phi3 - Decimal(1)/6) / z
        return phi1, phi2, phi3, phi4
    result = []
    for order, factorial in ((1, 1), (2, 2), (3, 6), (4, 24)):
        term = Decimal(1) / factorial
        total = term
        for n in range(1, PHI_TERMS+1):
            term *= z / Decimal(n+order)
            total += term
            if abs(term) <= PHI_STOP * max(Decimal(1), abs(total)):
                result.append(total)
                break
        else:
            raise ArithmeticError("Frozen small-z reference series limit reached")
    return tuple(result)


def monomial_step(eleft, d, duration, normalized_coefficients):
    """Q(x)=a0+a1*x+a2*x^2+a3*x^3, x=u/duration."""
    duration, d = dec(duration), dec(d)
    z = d * duration
    phi = phi_values(z)
    coefficients = list(normalized_coefficients) + [ZERO] * (4-len(normalized_coefficients))
    moments = (phi[0], phi[1], 2*phi[2], 6*phi[3])
    integral = duration * sum((dec(a)*m for a, m in zip(coefficients, moments)), Decimal(0))
    return z.exp() * dec(eleft) + integral


def monomial_step_exact(eleft, duration, coefficients):
    return eleft + duration * sum((a/Fraction(i+1) for i, a in enumerate(coefficients)), ZERO)


def weight_references(d, duration):
    """Signed power-moment combination; not production positive beta series."""
    z = dec(d) * dec(duration)
    p1, p2, p3, p4 = phi_values(z)
    span = dec(duration)
    weights = (
        span * (p1-3*p2+6*p3-6*p4),
        3*span * (p2-4*p3+6*p4),
        6*span * (p3-3*p4),
        6*span * p4,
    )
    return z.exp(), weights, span*p1


def algebraic_sign(offset, multiplier, radicand):
    """Exact sign of offset+multiplier*sqrt(radicand), radicand>0."""
    if not multiplier:
        return sign(offset)
    if not offset:
        return sign(multiplier)
    if sign(offset) == sign(multiplier):
        return sign(offset)
    difference = offset*offset - multiplier*multiplier*radicand
    return sign(offset) * sign(difference)


class Root:
    def __init__(self, rational=None, offset=ZERO, multiplier=ZERO,
                 radicand=ZERO, decimal_value=None, multiplicity=1):
        self.rational = rational
        self.offset = offset
        self.multiplier = multiplier
        self.radicand = radicand
        self.value = dec(rational) if rational is not None else decimal_value
        self.multiplicity = multiplicity

    def compare(self, rational):
        rational = rat(rational)
        if self.rational is not None:
            return sign(self.rational-rational)
        return algebraic_sign(self.offset-rational, self.multiplier, self.radicand)

    def in_closed_unit(self):
        return self.compare(ZERO) >= 0 and self.compare(ONE) <= 0

    def interior(self):
        return self.compare(ZERO) > 0 and self.compare(ONE) < 0

    def describe(self):
        return {
            "kind": "RATIONAL" if self.rational is not None else "QUADRATIC_SURD",
            "rational": None if self.rational is None else str(self.rational),
            "offset": str(self.offset), "sqrt_coefficient": str(self.multiplier),
            "radicand": str(self.radicand), "Decimal": str(self.value),
            "multiplicity": self.multiplicity,
        }


def derivative_roots(power):
    """Exact quadratic discriminant + analytic sqrt. No numerical bisection."""
    _, a1, a2, a3 = power
    c, b, a = a1, 2*a2, 3*a3
    if not a:
        if not b:
            return [], (-1 if not c else 0)
        return [Root(rational=-c/b)], 1
    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return [], 2
    if not discriminant:
        return [Root(rational=-b/(2*a), multiplicity=2)], 2
    sn, sd = isqrt(discriminant.numerator), isqrt(discriminant.denominator)
    if sn*sn == discriminant.numerator and sd*sd == discriminant.denominator:
        square_root = Fraction(sn, sd)
        roots = sorted(((-b-square_root)/(2*a), (-b+square_root)/(2*a)))
        return [Root(rational=x) for x in roots], 2
    midpoint = -b/(2*a)
    radius_multiplier = ONE/(2*abs(a))
    sqrt_decimal = dec(discriminant).sqrt()
    b_decimal = dec(b)
    stable_q = -(b_decimal + (sqrt_decimal if b >= 0 else -sqrt_decimal))/2
    # This product-of-roots route avoids cancellation for a root near zero.
    decimals = sorted((stable_q/dec(a), dec(c)/stable_q))
    return [
        Root(offset=midpoint, multiplier=-radius_multiplier, radicand=discriminant,
             decimal_value=decimals[0]),
        Root(offset=midpoint, multiplier=radius_multiplier, radicand=discriminant,
             decimal_value=decimals[1]),
    ], 2


def positive_cubic_value(bernstein, x):
    """High-precision evaluation after independent power-to-B3 conversion."""
    x = dec(x)
    one_minus = Decimal(1)-x
    return (dec(bernstein[0])*one_minus**3 +
            3*dec(bernstein[1])*x*one_minus**2 +
            3*dec(bernstein[2])*x*x*one_minus +
            dec(bernstein[3])*x**3)


class Model:
    def __init__(self, record):
        self.record = record
        self.q, self.tau, self.c, self.d = map(input_rat, (
            record["q"], record["tau"], record["c"], record["d"]))
        if len(record["initial"]) != 2:
            raise ValueError("Initial vector length must equal two")
        self.r0, self.e0 = map(input_rat, record["initial"])
        self.source = tuple(map(input_rat, record["source_knots"]))
        self.observation = tuple(map(input_rat, record["observation_knots"]))
        self.gr = tuple(tuple(map(input_rat, row)) for row in record["g_r"])
        self.ge = tuple(tuple(map(input_rat, row)) for row in record["g_e"])
        if not (2 <= len(self.source) <= MAX_SOURCE+1):
            raise ValueError("Original source count outside reference finite domain")
        if not (2 <= len(self.observation) <= MAX_OBSERVATION+1):
            raise ValueError("Observation count outside reference finite domain")
        if any(a >= b for a, b in zip(self.source, self.source[1:])):
            raise ValueError("Source knots must be strictly increasing")
        if any(a >= b for a, b in zip(self.observation, self.observation[1:])):
            raise ValueError("Observation knots must be strictly increasing")
        if (self.source[0], self.source[-1]) != (self.observation[0], self.observation[-1]):
            raise ValueError("Source and observation endpoint mismatch")
        if len(self.gr) != len(self.source)-1 or len(self.ge) != len(self.gr):
            raise ValueError("Quadratic source row count mismatch")
        if any(len(row) != 3 for row in self.gr+self.ge):
            raise ValueError("Quadratic source triplet required")
        if not 0 <= self.q <= 1 or self.tau <= 0 or self.c < 0:
            raise ValueError("Comparison parameter domain failed")
        if self.r0 < 0 or self.e0 < 0:
            raise ValueError("Initial nonnegative values required")
        if any(quadratic_min(quadratic_power(row)) < 0 for row in self.gr+self.ge):
            raise ValueError("Quadratic source negative within original cell")
        self.t0, self.end = self.source[0], self.source[-1]
        self.blocks = int((self.end-self.t0)//self.tau)
        if self.blocks > MAX_BLOCKS or abs(self.d)*(self.end-self.t0) > 16:
            raise ValueError("Horizon block/argument domain exceeded")
        self.qpowers = [ONE if k == 0 else self.q**k for k in range(self.blocks+1)]
        self.primitive_cache = {}
        self.f_cache = {}
        self.prefix = [[ZERO] for _ in range(3)]
        for k in range(self.blocks):
            for m in range(3):
                piece = self.qpowers[k] * (
                    ((k+1)*self.tau)**(m+1)-(k*self.tau)**(m+1)
                ) / (m+1)
                self.prefix[m].append(self.prefix[m][-1]+piece)
        self.source_power = []
        for j, row in enumerate(self.gr):
            span = self.source[j+1]-self.source[j]
            a0, a1, a2 = quadratic_power(row)
            self.source_power.append((a0, a1/span, a2/(span*span)))
        self.vertices = []
        self.effective_knots = []
        self.effective = []
        self.base = []
        self.cells = []
        self.e_decimal = []
        self.e_exact = None

    def kernel(self, t):
        n = int((t-self.t0)//self.tau)
        return ONE if n == 0 else self.q**n

    def primitives(self, age):
        if age <= 0:
            return ZERO, ZERO, ZERO
        if age in self.primitive_cache:
            return self.primitive_cache[age]
        n = int(age//self.tau)
        start = n*self.tau
        result = tuple(
            self.prefix[m][n] + self.qpowers[n]*(age**(m+1)-start**(m+1))/(m+1)
            for m in range(3)
        )
        self.primitive_cache[age] = result
        return result

    def forcing(self, t):
        if t in self.f_cache:
            return self.f_cache[t]
        total = ZERO
        for j, (left, right) in enumerate(zip(self.source, self.source[1:])):
            alpha, beta, gamma = self.source_power[j]
            x = t-left
            p = self.primitives(t-left)
            q = self.primitives(t-right)
            delta = tuple(a-b for a, b in zip(p, q))
            total += ((alpha+beta*x+gamma*x*x)*delta[0] -
                      (beta+2*gamma*x)*delta[1] + gamma*delta[2])
        self.f_cache[t] = total
        return total

    def rpoint(self, t):
        return self.kernel(t)*self.r0 + self.forcing(t)

    def original_index(self, t):
        return min(bisect_right(self.source, t)-1, len(self.source)-2)

    def source_restriction(self, family, original_index, left, right):
        a, b = self.source[original_index:original_index+2]
        row = self.gr[original_index] if family == "r" else self.ge[original_index]
        power = quadratic_power(row)
        restricted = restrict_power(power, (left-a)/(b-a), (right-a)/(b-a))[:3]
        p0, p1, p2 = restricted
        return restricted, (p0, p0+p1/2, p0+p1+p2)

    def construct(self):
        vertices = set()
        self.effective_knots = [self.t0]
        for j, (left, right) in enumerate(zip(self.source, self.source[1:])):
            interior = set()
            for row in (self.gr[j], self.ge[j]):
                _, p1, p2 = quadratic_power(row)
                if p2:
                    vertex = -p1/(2*p2)
                    if 0 < vertex < 1:
                        interior.add(left+(right-left)*vertex)
            vertices.update(interior)
            pieces = [left]+sorted(interior)+[right]
            for a, b in zip(pieces, pieces[1:]):
                _, rbern = self.source_restriction("r", j, a, b)
                _, ebern = self.source_restriction("e", j, a, b)
                self.effective.append({
                    "left": a, "right": b, "original": j, "g_r": rbern, "g_e": ebern,
                })
                self.effective_knots.append(b)
        self.vertices = sorted(vertices)
        if len(self.effective) > MAX_EFFECTIVE:
            raise ValueError("Effective source count exceeds reference domain")
        events = set(self.observation)
        for a in self.effective_knots:
            for k in range(self.blocks+1):
                t = a+k*self.tau
                if self.t0 <= t <= self.end:
                    events.add(t)
        self.base = sorted(events)
        if len(self.base)-1 > MAX_BASE:
            raise ValueError("Base count exceeds reference domain")
        for left, right in zip(self.base, self.base[1:]):
            span = right-left
            initial = self.kernel(left)*self.r0
            values = [initial+self.forcing(left+span*Fraction(i,3)) for i in range(4)]
            d1 = values[1]-values[0]
            d2 = values[2]-2*values[1]+values[0]
            d3 = values[3]-3*values[2]+3*values[1]-values[0]
            power = (values[0], 3*d1-3*d2/2+d3, 9*(d2-d3)/2, 9*d3/2)
            bern = cubic_bernstein(power)
            j = self.original_index((left+right)/2)
            epower, ebern = self.source_restriction("e", j, left, right)
            qpower = tuple(self.c*power[k] + (epower[k] if k < 3 else ZERO) for k in range(4))
            roots, degree = derivative_roots(power)
            roots = [r for r in roots if r.in_closed_unit()]
            maximum = max(
                [dec(bern[0]), dec(bern[3]), dec(self.rpoint(right))] +
                [positive_cubic_value(bern, r.value) for r in roots if r.interior()]
            )
            self.cells.append({
                "left": left, "right": right, "initial": initial, "power": power,
                "bernstein": bern, "ge_power": epower, "ge_bernstein": ebern,
                "Q_power": qpower, "Q_bernstein": cubic_bernstein(qpower),
                "roots": roots, "derivative_degree": degree,
                "whole_R_Decimal": maximum,
            })
        self.e_decimal = [dec(self.e0)]
        self.e_exact = [self.e0] if self.d == 0 else None
        for cell in self.cells:
            span = cell["right"]-cell["left"]
            self.e_decimal.append(monomial_step(self.e_decimal[-1], self.d, span, cell["Q_power"]))
            if self.e_exact is not None:
                self.e_exact.append(monomial_step_exact(self.e_exact[-1], span, cell["Q_power"]))
        return self

    def e_at(self, t):
        if t == self.end:
            return self.e_decimal[-1]
        i = bisect_right(self.base, t)-1
        cell = self.cells[i]
        theta = (t-cell["left"])/(cell["right"]-cell["left"])
        coefficients = tuple(a*theta**k for k, a in enumerate(cell["Q_power"]))
        return monomial_step(self.e_decimal[i], self.d, t-cell["left"], coefficients)

    def overlap_nonempty(self):
        count = 0
        for cell in self.cells:
            mid = (cell["left"]+cell["right"])/2
            for source in self.effective:
                for k in range(self.blocks+1):
                    low = max(source["left"], mid-(k+1)*self.tau)
                    high = min(source["right"], mid-k*self.tau)
                    count += high > low
        return count


def forcing_hash(model, binding):
    payload = {
        "schema": "WU_R14_WHOLE_FORCING_V1",
        "source_id": binding["source_id"], "clock_id": binding["clock_id"],
        "clock_unit": binding["clock_unit"], "state_order": binding["state_order"],
        "source_knots": [str(x) for x in model.source],
        "g_r": [[str(x) for x in row] for row in model.gr],
        "g_e": [[str(x) for x in row] for row in model.ge],
    }
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")) + "\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def check_binding(audit, model, source_sha):
    record = model.record
    binding, certificate = record["binding"], record["certificate"]
    states = record["states"]
    audit.require("metadata", "states_finite", isinstance(states, int) and
                  not isinstance(states, bool) and 1 <= states <= 13, states, "integer 1..13")
    for key in ("source_id", "clock_id", "clock_unit", "full_A_family_id", "source_locator",
                "scientific_status", "state_order", "source_sha256",
                "whole_forcing_source_sha256", "whole_forcing_hash_format"):
        audit.equal("binding/"+key, certificate.get(key), binding.get(key))
    audit.equal("fixture_source_bytes_sha", binding["source_sha256"], source_sha)
    audit.equal("forcing_hash_format", binding["whole_forcing_hash_format"],
                "WU_R14_WHOLE_FORCING_V1")
    audit.equal("original_source_function_hash", binding["whole_forcing_source_sha256"],
                forcing_hash(model, binding))
    order = binding["state_order"]
    audit.equal("state_order_length", len(order), states)
    audit.equal("state_order_unique", len(set(order)), states)
    audit.equal("generator", certificate["generator"], "A=K+wH;H=pi*d^T-diag(d)")
    for key in ("fixed_K_pi_d", "full_w_box", "all_start_times", "zero_mass_residual",
                "short_remainder_nonexpansive", "forcing_whole_fine_coarse_domain"):
        audit.equal("premise/"+key, certificate.get(key), True)
    for key, value in (("q", model.q), ("tau", model.tau), ("t0", model.t0), ("T", model.end)):
        audit.rational("certificate/"+key, certificate[key], value)
    w0, w1 = map(rat, certificate["w_box"])
    audit.require("exact", "whole_w_box", 0 <= w0 <= w1, [w0, w1], "0<=w0<=w1")
    if states == 1:
        audit.require("exact", "singleton_zero_mass", model.r0 == 0 and
                      all(all(v == 0 for v in row) for row in model.gr),
                      [model.r0, model.gr], "zero singleton residual and residual forcing")
    audit.require("metadata", "no_generic_caps", "caps" not in record, "caps" in record, False)


def exact_derivative(power, x):
    return power[1]+2*power[2]*x+3*power[3]*x*x


def derivative_branches(power):
    a, b = 3*power[3], 2*power[2]
    if a:
        v = -b/(2*a)
        if 0 < v < 1:
            return [(ZERO, v), (v, ONE)]
    return [(ZERO, ONE)]


def check_critical_and_supremum(audit, model, cell, reported, index):
    tag = f"cell{index}"
    power, bern = cell["power"], cell["bernstein"]
    critical, supremum = reported["critical"], reported["supremum"]
    derivative = (power[1], 2*power[2], 3*power[3])
    audit.vector(tag+"/derivative_power", critical["derivative_power"], derivative)
    audit.equal(tag+"/constant_polynomial", critical.get("constant_polynomial", False),
                cell["derivative_degree"] == -1)
    if "degree" in critical or cell["derivative_degree"] == -1:
        audit.equal(tag+"/derivative_degree", critical.get("degree"), cell["derivative_degree"])
    exact_rows, box_rows = critical["exact_roots"], critical["root_boxes"]
    exact_values = [rat(row["x"]) for row in exact_rows]
    audit.equal(tag+"/unique_exact_roots", len(set(exact_values)), len(exact_values))
    independent_roots = cell["roots"]
    branch_intervals = derivative_branches(power)
    actual_steps = 0

    for j, (row, x) in enumerate(zip(exact_rows, exact_values)):
        prefix = f"{tag}/exact_root{j}"
        audit.require("exact", prefix+"/unit_domain", 0 <= x <= 1, x, "[0,1]")
        audit.rational(prefix+"/zero", exact_derivative(power, x), ZERO)
        multiplicity = 2 if derivative[2] and derivative[1]+2*derivative[2]*x == 0 else 1
        audit.equal(prefix+"/multiplicity", row["multiplicity"], multiplicity)
        location = "LEFT_ENDPOINT" if x == 0 else "RIGHT_ENDPOINT" if x == 1 else "INTERIOR"
        audit.equal(prefix+"/location", row["location"], location)
        matches = sum(root.compare(x) == 0 for root in independent_roots)
        audit.equal(prefix+"/analytic_root_matches", matches, 1)
        # A non-vertex quadratic exact hit occurs first at this dyadic depth.
        if derivative[2] and 0 < x < 1 and derivative[1]+2*derivative[2]*x != 0:
            containing = [(a, b) for a, b in branch_intervals if a < x < b]
            audit.equal(prefix+"/one_monotone_branch", len(containing), 1)
            if containing:
                a, b = containing[0]
                theta = (x-a)/(b-a)
                denominator = theta.denominator
                is_dyadic = denominator > 1 and denominator & (denominator-1) == 0
                depth = denominator.bit_length()-1
                audit.require("exact", prefix+"/exact_hit_dyadic_depth",
                              is_dyadic and 1 <= depth <= ROOT_DEPTH,
                              [theta, depth], "dyadic midpoint depth 1..96")
                if is_dyadic:
                    actual_steps += depth

    parsed_boxes = []
    audit.require("coverage", tag+"/at_most_two_boxes", len(box_rows) <= 2, len(box_rows), "<=2")
    for j, row in enumerate(box_rows):
        prefix = f"{tag}/root_box{j}"
        lo, hi = rat(row["lo"]), rat(row["hi"])
        iterations = row["iterations"]
        branch = tuple(map(rat, row["branch"]))
        audit.require("exact", prefix+"/strict_interval", 0 <= lo < hi <= 1, [lo, hi], "[0,1]")
        audit.require("exact", prefix+"/width", hi-lo <= Fraction(1, 1 << ROOT_DEPTH),
                      hi-lo, Fraction(1, 1 << ROOT_DEPTH))
        audit.equal(prefix+"/iterations", iterations, ROOT_DEPTH)
        audit.require("exact", prefix+"/valid_branch", branch in branch_intervals,
                      branch, branch_intervals)
        dlo, dhi = exact_derivative(power, lo), exact_derivative(power, hi)
        audit.rational(prefix+"/reported_left_sign", row["derivative_at_lo"], dlo)
        audit.rational(prefix+"/reported_right_sign", row["derivative_at_hi"], dhi)
        audit.require("exact", prefix+"/strict_sign_change", dlo*dhi < 0, [dlo, dhi], "opposite signs")
        if branch in branch_intervals and isinstance(iterations, int) and 0 <= iterations <= ROOT_DEPTH:
            a, b = branch
            audit.require("exact", prefix+"/inside_branch", a <= lo < hi <= b,
                          [lo, hi], [a, b])
            audit.require("exact", prefix+"/initial_branch_sign_change",
                          exact_derivative(power, a)*exact_derivative(power, b) < 0,
                          [exact_derivative(power, a), exact_derivative(power, b)], "opposite signs")
            audit.rational(prefix+"/exact_bisection_width", hi-lo, (b-a)/(1 << iterations))
            mesh_index = (lo-a)*(1 << iterations)/(b-a)
            audit.equal(prefix+"/dyadic_mesh_index", mesh_index.denominator, 1)
        represented = [root for root in independent_roots
                       if root.compare(lo) > 0 and root.compare(hi) < 0]
        audit.equal(prefix+"/unique_analytic_interior_root", len(represented), 1)
        if represented:
            audit.require("coverage", prefix+"/root_is_interior", represented[0].interior(),
                          represented[0].describe(), "strict interior")
        parsed_boxes.append((lo, hi))
        actual_steps += iterations

    for j, root in enumerate(independent_roots):
        representations = sum(root.compare(x) == 0 for x in exact_values)
        representations += sum(root.compare(a) > 0 and root.compare(b) < 0 for a, b in parsed_boxes)
        audit.equal(f"{tag}/analytic_root{j}_covered_once", representations, 1, "coverage")
    audit.equal(tag+"/bisections_actual", critical["bisections_actual"], actual_steps)
    audit.require("metadata", tag+"/bisections_cap", 0 <= actual_steps <= 2*ROOT_DEPTH,
                  actual_steps, "0..192")

    m_b = 3*max(abs(bern[i+1]-bern[i]) for i in range(3))
    cmax = max(bern)
    bound = m_b/Fraction(1 << ROOT_DEPTH)
    audit.rational(tag+"/M_B", supremum["M_B"], m_b)
    audit.rational(tag+"/Cmax", supremum["Cmax"], cmax)
    audit.rational(tag+"/proved_gap_bound", supremum["proved_gap_bound"], bound)
    audit.require("exact", tag+"/M_B_le_3Cmax", m_b <= 3*cmax, m_b, 3*cmax)

    box_bounds = supremum["box_bounds"]
    audit.equal(tag+"/box_bounds_count", len(box_bounds), len(parsed_boxes))
    hulls, witnesses = [], []
    for j, (row, interval) in enumerate(zip(box_bounds, parsed_boxes)):
        lo, hi = interval
        prefix = f"{tag}/restricted_box{j}"
        audit.rational(prefix+"/lo", row["lo"], lo)
        audit.rational(prefix+"/hi", row["hi"], hi)
        restricted = cubic_bernstein(restrict_power(power, lo, hi))
        midpoint = (lo+hi)/2
        value = power_value(power, midpoint)
        hull = max(restricted)
        audit.vector(prefix+"/bernstein_by_power_composition", row["bernstein"], restricted)
        audit.rational(prefix+"/midpoint", row["midpoint"], midpoint)
        audit.rational(prefix+"/midpoint_value", row["midpoint_value"], value)
        audit.rational(prefix+"/hull_upper", row["hull_upper"], hull)
        audit.require("exact", prefix+"/hull_range_bound",
                      max(restricted)-min(restricted) <= m_b*(hi-lo),
                      max(restricted)-min(restricted), m_b*(hi-lo))
        audit.require("exact", prefix+"/midpoint_in_hull",
                      min(restricted) <= value <= hull, value, [min(restricted), hull])
        for k in range(3):
            audit.require("exact", f"{prefix}/chain_difference{k}",
                          3*abs(restricted[k+1]-restricted[k]) <= m_b*(hi-lo),
                          3*abs(restricted[k+1]-restricted[k]), m_b*(hi-lo))
        hulls.append(hull)
        witnesses.append(value)

    candidates = [bern[0], bern[3], model.rpoint(cell["right"])]
    candidates.extend(power_value(power, x) for x in exact_values if 0 < x < 1)
    candidate_records = supremum["exact_candidates"]
    seen_left, seen_right_limit = False, False
    seen_interior = set()
    for j, row in enumerate(candidate_records):
        x, kind = rat(row["x"]), row["kind"]
        if kind == "ACTUAL_RIGHT_ENDPOINT":
            expected = model.rpoint(cell["right"])
            audit.rational(f"{tag}/candidate{j}_right_x", x, ONE)
        else:
            expected = power_value(power, x)
        audit.rational(f"{tag}/candidate{j}_value", row["value"], expected)
        if kind == "ACTUAL_LEFT_ENDPOINT":
            audit.rational(f"{tag}/candidate{j}_left_x", x, ZERO)
            seen_left = True
        elif kind == "RIGHT_LEFT_LIMIT":
            audit.rational(f"{tag}/candidate{j}_limit_x", x, ONE)
            seen_right_limit = True
        elif kind == "EXACT_INTERIOR_CRITICAL":
            audit.require("exact", f"{tag}/candidate{j}_critical",
                          0 < x < 1 and x in exact_values, x, exact_values)
            seen_interior.add(x)
        elif kind != "ACTUAL_RIGHT_ENDPOINT":
            audit.require("metadata", f"{tag}/candidate{j}_kind", False, kind, "declared candidate kind")
    audit.require("coverage", tag+"/left_endpoint_candidate", seen_left, seen_left, True)
    audit.require("coverage", tag+"/right_left_limit_candidate", seen_right_limit, seen_right_limit, True)
    audit.equal(tag+"/exact_critical_candidates", sorted(seen_interior),
                sorted(x for x in exact_values if 0 < x < 1), "coverage")
    lower, upper = max(candidates+witnesses), max(candidates+hulls)
    audit.rational(tag+"/supremum_exact_lower", supremum["exact_lower"], lower)
    audit.rational(tag+"/supremum_exact_upper", supremum["exact_upper"], upper)
    audit.rational(tag+"/supremum_exact_gap", supremum["exact_gap"], upper-lower)
    audit.require("exact", tag+"/gap_nonnegative", lower <= upper, lower, upper)
    audit.require("exact", tag+"/gap_within_bound", upper-lower <= bound, upper-lower, bound)
    audit.rational(tag+"/supremum_dyadic_lower", supremum["dyadic_lower"], down(lower))
    audit.rational(tag+"/supremum_dyadic_upper", supremum["dyadic_upper"], up(upper))
    audit.between(tag+"/analytic_supremum", cell["whole_R_Decimal"], lower, upper, "coverage")
    return {"lower": lower, "upper": upper, "gap": upper-lower, "bound": bound,
            "root_steps": actual_steps}


def matrix(audit, name, value, rows):
    audit.equal(name+"/row_count", len(value), rows)
    for i, row in enumerate(value):
        audit.equal(f"{name}/{i}/width", len(row), 2)
    return [tuple(map(rat, row)) for row in value]


def check_case(audit, case, record, source_sha):
    cid = case["id"]
    audit.group(cid+"/input_binding")
    audit.equal("saved_input", record["input"], case)
    audit.require("metadata", "no_execution_error", not record.get("execution_error"),
                  record.get("execution_error"), None)
    model = Model(case).construct()
    result = record["result"]
    check_binding(audit, model, source_sha)
    parameters = result["parameters"]
    for key, expected in (("q", model.q), ("tau", model.tau), ("c", model.c), ("d", model.d),
                          ("t0", model.t0), ("T", model.end)):
        audit.rational("parameters/"+key, parameters[key], expected)
    audit.vector("parameters/initial", parameters["initial"], (model.r0, model.e0))
    audit.equal("parameters/states", parameters["states"], case["states"])
    audit.equal("parameters/full_blocks", parameters["full_blocks"], model.blocks)
    audit.equal("parameters/binding", parameters["binding"], case["binding"])
    audit.equal("parameters/certificate", parameters["certificate"], case["certificate"])
    audit.equal("global_history", result["R_history"], "GLOBAL_FROM_ORIGINAL_T0")
    audit.equal("cap_application", result["cap_application"], "NONE")

    audit.group(cid+"/source_preprocessing_and_grid")
    original = result["source"]
    audit.vector("original_knots", original["knots"], model.source)
    audit.vector("original_gr", original["g_r"], model.gr)
    audit.vector("original_ge", original["g_e"], model.ge)
    effective = result["effective_source"]
    audit.vector("effective_knots", effective["knots"], model.effective_knots)
    audit.vector("source_vertex_times", effective["source_vertex_times"], model.vertices)
    audit.equal("original_cell_indices", effective["original_cell_indices"],
                [row["original"] for row in model.effective])
    audit.vector("effective_gr_exact_equivalence", effective["g_r"],
                 [row["g_r"] for row in model.effective])
    audit.vector("effective_ge_exact_equivalence", effective["g_e"],
                 [row["g_e"] for row in model.effective])
    for j, row in enumerate(model.effective):
        for family in ("g_r", "g_e"):
            audit.require("exact", f"effective{j}/{family}_coefficients_nonnegative",
                          min(row[family]) >= 0, row[family], "all>=0")
    audit.vector("requested_times", result["requested_times"], model.observation)
    audit.vector("base_times", result["base_times"], model.base)
    audit.vector("refined_times_same_rational_grid", result["refined_times"], model.base)

    audit.group(cid+"/independent_primitives_and_cubics")
    exact = result["exact"]
    audit.vector("F_at_base", exact["F_at_refined"], [model.forcing(t) for t in model.base])
    audit.vector("R_actual_at_base", exact["R_at_refined"], [model.rpoint(t) for t in model.base])
    audit.vector("kernel_at_base", exact["kernel_at_refined"], [model.kernel(t) for t in model.base])
    reported_cells = exact["R_cubic_cells"]
    audit.equal("cubic_cell_count", len(reported_cells), len(model.cells))
    suprema = []
    for i, (reported, cell) in enumerate(zip(reported_cells, model.cells)):
        tag = f"cell{i}"
        audit.rational(tag+"/left", reported["left"], cell["left"])
        audit.rational(tag+"/right", reported["right"], cell["right"])
        audit.vector(tag+"/power_from_J_primitives", reported["coefficients_normalized"], cell["power"])
        audit.vector(tag+"/Bernstein_from_power", reported["bernstein"], cell["bernstein"])
        audit.vector(tag+"/F_Bernstein", reported["F_bernstein"],
                     [v-cell["initial"] for v in cell["bernstein"]])
        audit.rational(tag+"/initial_piece", reported["initial_piece"], cell["initial"])
        audit.rational(tag+"/right_left_limit", reported["right_left_limit"], cell["bernstein"][-1])
        audit.rational(tag+"/actual_right_endpoint", reported["actual_right_endpoint"],
                       model.rpoint(cell["right"]))
        audit.vector(tag+"/ge_Bernstein", reported["ge_bernstein"], cell["ge_bernstein"])
        audit.vector(tag+"/forcing_Bernstein", reported["forcing_bernstein"], cell["Q_bernstein"])
        for family in ("bernstein", "ge_bernstein", "Q_bernstein"):
            audit.require("exact", tag+"/"+family+"_nonnegative", min(cell[family]) >= 0,
                          cell[family], "all>=0")
        midpoint = (cell["left"]+cell["right"])/2
        audit.rational(tag+"/independent_midpoint_identity",
                       power_value(cell["power"], Fraction(1,2)), model.rpoint(midpoint))
        audit.require("exact", tag+"/right_jump_downward",
                      model.rpoint(cell["right"]) <= cell["bernstein"][-1],
                      model.rpoint(cell["right"]), cell["bernstein"][-1])
        audit.group(cid+f"/critical_and_supremum/{i}")
        suprema.append(check_critical_and_supremum(audit, model, cell, reported, i))

    audit.group(cid+"/positive_weight_enclosures")
    weights = result["weights"]
    audit.equal("weight_row_count", len(weights), len(model.cells))
    for i, (row, cell) in enumerate(zip(weights, model.cells)):
        tag = f"cell{i}"
        duration = cell["right"]-cell["left"]
        audit.rational(tag+"/left", row["left"], cell["left"])
        audit.rational(tag+"/right", row["right"], cell["right"])
        audit.rational(tag+"/d_delta", row["d_delta"], model.d*duration)
        exp_ref, moment_refs, phi_ref = weight_references(model.d, duration)
        interval_values = {}
        for key, value in [("exp", exp_ref), ("phi", phi_ref)] + [
                ("W"+str(k), value) for k, value in enumerate(moment_refs)]:
            interval = tuple(map(rat, row[key]))
            audit.equal(tag+"/"+key+"_interval_width", len(interval), 2)
            lo, hi = interval
            audit.require("exact", tag+"/"+key+"_nonnegative_order", 0 <= lo <= hi,
                          interval, "0<=lo<=hi")
            audit.between(tag+"/"+key, value, lo, hi)
            interval_values[key] = interval
            if model.d == 0:
                true = ONE if key == "exp" else duration if key == "phi" else duration/4
                audit.require("exact", tag+"/"+key+"_zero_d_exact_inclusion",
                              lo <= true <= hi, interval, true)
        for side in (0, 1):
            summed = sum((interval_values["W"+str(k)][side] for k in range(4)), ZERO)
            audit.rational(f"{tag}/phi_sum_side{side}", interval_values["phi"][side], summed)
        audit.decimal_equal(tag+"/independent_weight_sum", sum(moment_refs, Decimal(0)), phi_ref)

    audit.group(cid+"/endpoint_enclosures")
    raw = result["raw"]
    lower = matrix(audit, "base_lower", raw["refined_endpoints_lower"], len(model.base))
    upper = matrix(audit, "base_upper", raw["refined_endpoints_upper"], len(model.base))
    whole_lower = matrix(audit, "base_whole_lower", raw["refined_whole_cells_lower"], len(model.cells))
    whole_upper = matrix(audit, "base_whole_upper", raw["refined_whole_cells_upper"], len(model.cells))
    for i, t in enumerate(model.base):
        r = model.rpoint(t)
        audit.require("exact", f"point{i}/R_inclusion", lower[i][0] <= r <= upper[i][0],
                      [lower[i][0], upper[i][0]], r)
        audit.require("exact", f"point{i}/E_order", 0 <= lower[i][1] <= upper[i][1],
                      [lower[i][1], upper[i][1]], "nonnegative interval")
        audit.between(f"point{i}/E", model.e_decimal[i], lower[i][1], upper[i][1])
        if model.e_exact is not None:
            true_e = model.e_exact[i]
            audit.require("exact", f"point{i}/E_exact_inclusion",
                          lower[i][1] <= true_e <= upper[i][1],
                          [lower[i][1], upper[i][1]], true_e)

    audit.group(cid+"/whole_cell_majorants")
    majorants = []
    for i, (cell, sup) in enumerate(zip(model.cells, suprema)):
        span = cell["right"]-cell["left"]
        audit.rational(f"cell{i}/R_whole_lower", whole_lower[i][0], down(sup["lower"]), "coverage")
        audit.rational(f"cell{i}/R_whole_upper", whole_upper[i][0], up(sup["upper"]), "coverage")
        audit.rational(f"cell{i}/E_whole_lower", whole_lower[i][1],
                       max(lower[i][1], lower[i+1][1]), "coverage")
        qmax = model.c*sup["upper"] + max(cell["ge_bernstein"])
        yend = monomial_step(upper[i][1], model.d, span, (qmax, ZERO, ZERO, ZERO))
        required = max(dec(upper[i][1]), yend)
        majorants.append(required)
        audit.decimal_le(f"cell{i}/E_constant_majorant", required, whole_upper[i][1], "coverage")
        majorant_record = reported_cells[i]["whole_E_majorant"]
        audit.rational(f"cell{i}/majorant_forcing_upper", majorant_record["forcing_upper"], qmax)
        audit.rational(f"cell{i}/majorant_left_upper", majorant_record["left_E_upper"], upper[i][1])
        audit.decimal_le(f"cell{i}/majorant_right_upper", yend,
                         majorant_record["right_majorant_upper"], "coverage")
        audit.rational(f"cell{i}/majorant_supremum_upper", majorant_record["supremum_upper"],
                       whole_upper[i][1], "coverage")
        audit.between(f"cell{i}/analytic_R_sup", cell["whole_R_Decimal"],
                      whole_lower[i][0], whole_upper[i][0], "coverage")
        for side in (0, 1):
            for component in (0, 1):
                audit.require("coverage", f"cell{i}/endpoint{side}_component{component}",
                              upper[i+side][component] <= whole_upper[i][component],
                              upper[i+side][component], whole_upper[i][component])
        theta = Fraction(1,2)
        mid = (cell["left"]+cell["right"])/2
        midpoint_e = monomial_step(model.e_decimal[i], model.d, span/2,
                                  tuple(a*theta**k for k, a in enumerate(cell["Q_power"])))
        audit.decimal_le(f"cell{i}/interior_E_corroboration", midpoint_e, whole_upper[i][1], "coverage")
        audit.require("coverage", f"cell{i}/interior_R_corroboration",
                      model.rpoint(mid) <= whole_upper[i][0], model.rpoint(mid), whole_upper[i][0])

    audit.group(cid+"/observation_aggregation")
    obs_lower = matrix(audit, "observation_lower", raw["endpoints_lower"], len(model.observation))
    obs_upper = matrix(audit, "observation_upper", raw["endpoints_upper"], len(model.observation))
    obs_whole_lower = matrix(audit, "observation_whole_lower", raw["whole_cells_lower"],
                             len(model.observation)-1)
    obs_whole_upper = matrix(audit, "observation_whole_upper", raw["whole_cells_upper"],
                             len(model.observation)-1)
    lookup = {t: i for i, t in enumerate(model.base)}
    indices = [lookup[t] for t in model.observation]
    for j, k in enumerate(indices):
        audit.vector(f"observation{j}/lower_select", obs_lower[j], lower[k])
        audit.vector(f"observation{j}/upper_select", obs_upper[j], upper[k])
    obs_suprema = exact["observation_R_suprema"]
    audit.equal("observation_suprema_count", len(obs_suprema), len(model.observation)-1)
    for j, (first, last) in enumerate(zip(indices, indices[1:])):
        row = obs_suprema[j]
        audit.require("coverage", f"observation{j}/contiguous_cells",
                      0 <= first < last <= len(model.cells), [first, last], "ordered nonempty range")
        audit.rational(f"observation{j}/left", row["left"], model.observation[j])
        audit.rational(f"observation{j}/right", row["right"], model.observation[j+1])
        lo = max(s["lower"] for s in suprema[first:last])
        hi = max(s["upper"] for s in suprema[first:last])
        gap_bound = max(s["bound"] for s in suprema[first:last])
        for key, value in (("exact_lower", lo), ("exact_upper", hi),
                           ("exact_gap", hi-lo), ("proved_gap_bound", gap_bound)):
            audit.rational(f"observation{j}/{key}", row[key], value, "coverage")
        audit.require("coverage", f"observation{j}/max_gap_bound", hi-lo <= gap_bound, hi-lo, gap_bound)
        for component in (0, 1):
            audit.rational(f"observation{j}/whole_lower_component{component}",
                           obs_whole_lower[j][component],
                           max(v[component] for v in whole_lower[first:last]), "coverage")
            audit.rational(f"observation{j}/whole_upper_component{component}",
                           obs_whole_upper[j][component],
                           max(v[component] for v in whole_upper[first:last]), "coverage")
        independent_max = max(cell["whole_R_Decimal"] for cell in model.cells[first:last])
        audit.between(f"observation{j}/analytic_supremum", independent_max, lo, hi, "coverage")
        audit.decimal_le(f"observation{j}/E_majorant_union", max(majorants[first:last]),
                         obs_whole_upper[j][1], "coverage")

    audit.group(cid+"/resource_accounting")
    work = result["work"]
    expected_work = {
        "original_source_cells": len(model.source)-1,
        "effective_source_cells": len(model.effective),
        "base_cells": len(model.cells), "refined_cells": len(model.cells),
        "full_blocks": model.blocks,
        "overlap_terms_upper": len(model.cells)*len(model.effective)*(model.blocks+1),
        "overlap_terms_actual": len(model.cells)*len(model.effective)*(model.blocks+1),
        "nonempty_overlap_terms": model.overlap_nonempty(),
        "root_bisections_upper": 2*ROOT_DEPTH*len(model.cells),
        "root_bisections_actual": sum(s["root_steps"] for s in suprema),
        "guard_applied_before_overlap": True, "guard_applied_before_root_isolation": True,
        "coefficient_cell_builds": len(model.cells),
        "overlap_limit": MAX_OVERLAP, "root_limit": MAX_ROOT_STEPS,
    }
    for key, value in expected_work.items():
        audit.equal("work/"+key, work[key], value)
    audit.require("metadata", "overlap_precharge_finite",
                  expected_work["overlap_terms_upper"] <= MAX_OVERLAP,
                  expected_work["overlap_terms_upper"], MAX_OVERLAP)
    audit.require("metadata", "root_precharge_finite",
                  expected_work["root_bisections_upper"] <= MAX_ROOT_STEPS,
                  expected_work["root_bisections_upper"], MAX_ROOT_STEPS)
    audit.equal("coarse_l1_multiplier", raw.get("coarse_l1_multiplier",
                result.get("coarse_l1_multiplier")), 4)
    check_controls(audit, model, result, suprema)
    return model, {
        "id": cid, "base_cells": len(model.cells),
        "effective_source_cells": len(model.effective),
        "source_vertex_times": [str(t) for t in model.vertices],
        "requested_times": [str(t) for t in model.observation],
        "exact_R_at_requested": [str(model.rpoint(t)) for t in model.observation],
        "Decimal_E_at_requested": [str(model.e_at(t)) for t in model.observation],
        "exact_E_at_base_if_d_zero": None if model.e_exact is None else [str(x) for x in model.e_exact],
        "analytic_critical_roots": [
            {"left": str(cell["left"]), "right": str(cell["right"]),
             "roots": [r.describe() for r in cell["roots"]]}
            for cell in model.cells
        ],
        "Decimal_R_suprema_by_base_cell": [str(cell["whole_R_Decimal"]) for cell in model.cells],
        "independent_root_bisections": 0,
        "root_bisections_actual_verified": sum(s["root_steps"] for s in suprema),
        "whole_E_reference": "Same-cell constant-forcing majorant; interior midpoint only additional corroboration.",
    }


def control_value(value):
    if not isinstance(value, dict):
        return dec(value)
    result = dec(value["rational"])
    if "sqrt_coefficient" in value:
        radicand = dec(value["radicand"])
        if radicand < 0:
            raise ValueError("Control radicand must be nonnegative")
        result += dec(value["sqrt_coefficient"])*radicand.sqrt()
    return result


def check_controls(audit, model, result, suprema):
    controls = model.record.get("controls", {})
    if not controls:
        return
    audit.group(model.record["id"]+"/separate_authored_exact_controls")
    endpoint = controls.get("endpoint", {})
    if "R" in endpoint:
        audit.rational("control_endpoint_R", model.rpoint(model.end), rat(endpoint["R"]))
    if "E" in endpoint:
        expected = rat(endpoint["E"])
        if model.e_exact is not None:
            audit.rational("control_endpoint_E_exact", model.e_exact[-1], expected)
        audit.decimal_equal("control_endpoint_E_Decimal", model.e_decimal[-1], expected)
    if "F_final" in controls:
        audit.rational("control_F_final", model.forcing(model.end), rat(controls["F_final"]))
    if "right_left_limit" in controls:
        audit.rational("control_final_left_limit", model.cells[-1]["bernstein"][-1],
                       rat(controls["right_left_limit"]))
    if "source_vertex_times" in controls:
        audit.vector("control_source_vertices", model.vertices, tuple(map(rat, controls["source_vertex_times"])))
    counts = {
        "effective_source_cells": len(model.effective),
        "original_source_cells": len(model.source)-1,
        "observation_cells": len(model.observation)-1,
        "full_blocks": model.blocks,
    }
    for key, actual in counts.items():
        if key in controls:
            audit.equal("control_"+key, actual, controls[key])
    if controls.get("all_zero"):
        audit.require("exact", "zero_comparison_R", all(model.rpoint(t) == 0 for t in model.base),
                      [model.rpoint(t) for t in model.base], "all zero")
        audit.require("exact", "zero_comparison_E", model.e_exact is not None and all(x == 0 for x in model.e_exact),
                      model.e_exact, "all zero")
        for key in ("endpoints_lower", "endpoints_upper", "whole_cells_lower", "whole_cells_upper",
                    "refined_endpoints_lower", "refined_endpoints_upper",
                    "refined_whole_cells_lower", "refined_whole_cells_upper"):
            audit.require("exact", "zero_raw_"+key,
                          all(rat(x) == 0 for row in result["raw"][key] for x in row),
                          result["raw"][key], "all zero")
    if "whole_R_sup" in controls:
        specification = controls["whole_R_sup"]
        observation = specification.get("observation_cell", 0) if isinstance(specification, dict) else 0
        left, right = model.observation[observation:observation+2]
        included = [i for i, cell in enumerate(model.cells) if left <= cell["left"] and cell["right"] <= right]
        expected = control_value(specification)
        independent = max(model.cells[i]["whole_R_Decimal"] for i in included)
        audit.decimal_equal("control_whole_R_analytic", independent, expected)
        lower = max(suprema[i]["lower"] for i in included)
        upper = max(suprema[i]["upper"] for i in included)
        audit.between("control_whole_R_enclosure", expected, lower, upper, "coverage")
    if "critical_cell" in controls:
        specification = controls["critical_cell"]
        left, right = rat(specification["left"]), rat(specification["right"])
        included = [i for i, cell in enumerate(model.cells)
                    if cell["left"] == left and cell["right"] == right]
        audit.equal("control_critical_cell_unique", len(included), 1)
        if included:
            index = included[0]
            reported = result["exact"]["R_cubic_cells"][index]
            independent = model.cells[index]
            critical = reported["critical"]
            audit.equal("control_root_box_count", len(critical["root_boxes"]), specification["root_boxes"])
            wanted_roots = specification.get("exact_roots", [])
            got_roots = [{
                "x": str(rat(row["x"])), "multiplicity": row["multiplicity"], "location": row["location"],
            } for row in critical["exact_roots"]]
            normalized_wanted = [{
                "x": str(rat(row["x"])), "multiplicity": row["multiplicity"], "location": row["location"],
            } for row in wanted_roots]
            audit.equal("control_exact_roots", got_roots, normalized_wanted)
            if "bernstein" in specification:
                audit.vector("control_cubic_Bernstein", independent["bernstein"],
                             tuple(map(rat, specification["bernstein"])))
            if "M_B" in specification:
                actual = 3*max(abs(independent["bernstein"][i+1]-independent["bernstein"][i]) for i in range(3))
                audit.rational("control_M_B", actual, rat(specification["M_B"]))
            if "constant_polynomial" in specification:
                audit.equal("control_constant_polynomial", independent["derivative_degree"] == -1,
                            specification["constant_polynomial"])


def shared_parameters(left, right):
    return (left.q, left.tau, left.c, left.d, left.r0, left.e0, left.t0, left.end) == (
        right.q, right.tau, right.c, right.d, right.r0, right.e0, right.t0, right.end)


def source_function_relation(left, right, ordering):
    if not shared_parameters(left, right):
        return False
    knots = sorted(set(left.source) | set(right.source))
    for a, b in zip(knots, knots[1:]):
        il = left.original_index((a+b)/2)
        ir = right.original_index((a+b)/2)
        for family in ("r", "e"):
            pleft, _ = left.source_restriction(family, il, a, b)
            pright, _ = right.source_restriction(family, ir, a, b)
            difference = tuple(y-x for x, y in zip(pleft, pright))
            if ordering == "equal" and any(x != 0 for x in difference):
                return False
            if ordering == "le" and quadratic_min(difference) < 0:
                return False
    return True


def check_relations(audit, models, fixture_relations):
    relations = list(fixture_relations)
    for cid, model in models.items():
        local = list(model.record.get("relations", []))
        if "relation" in model.record:
            local.append(model.record["relation"])
        for specification in local:
            relations.append({"left": cid, "right": specification["other"], "kind": specification["kind"]})
    summaries = []
    for specification in relations:
        left_id, right_id, kind = specification["left"], specification["right"], specification["kind"]
        audit.group("relation/"+left_id+"/"+right_id+"/"+kind)
        present = left_id in models and right_id in models
        audit.require("metadata", "both_cases_verified", present, [left_id, right_id], "both models present")
        if not present:
            continue
        left, right = models[left_id], models[right_id]
        audit.require("exact", "common_parameters", shared_parameters(left, right),
                      [left_id, right_id], "same q/tau/c/d/initial/clock endpoints")
        if kind == "same_function":
            audit.require("exact", "equal_whole_quadratic_functions",
                          source_function_relation(left, right, "equal"), None, True)
            for t in sorted(set(left.observation) | set(right.observation)):
                audit.rational("F_at_"+str(t), left.forcing(t), right.forcing(t))
                audit.rational("R_at_"+str(t), left.rpoint(t), right.rpoint(t))
                audit.decimal_equal("E_at_"+str(t), left.e_at(t), right.e_at(t))
        elif kind in ("pointwise_smaller_source", "supremum_constant"):
            audit.require("exact", "whole_quadratic_forcing_order",
                          source_function_relation(left, right, "le"), None, True)
            for t in sorted(set(left.observation) | set(right.observation)):
                audit.require("exact", "R_order_at_"+str(t), left.rpoint(t) <= right.rpoint(t),
                              left.rpoint(t), right.rpoint(t))
                audit.decimal_le("E_order_at_"+str(t), left.e_at(t), right.e_at(t))
            denominator_r = right.rpoint(right.end)
            ratio_r = None if denominator_r == 0 else ONE-left.rpoint(left.end)/denominator_r
            denominator_e = None if right.e_exact is None else right.e_exact[-1]
            ratio_e = None if denominator_e is None or denominator_e == 0 else ONE-left.e_exact[-1]/denominator_e
            if "endpoint_R_relative_reduction" in specification:
                expected = specification["endpoint_R_relative_reduction"]
                if expected is None:
                    audit.equal("R_zero_denominator_ratio", ratio_r, None)
                else:
                    audit.rational("R_relative_reduction", ratio_r, rat(expected))
            if "endpoint_E_relative_reduction" in specification:
                expected = specification["endpoint_E_relative_reduction"]
                if expected is None:
                    audit.equal("E_zero_denominator_ratio", ratio_e, None)
                elif ratio_e is not None:
                    audit.rational("E_relative_reduction", ratio_e, rat(expected))
                else:
                    audit.require("exact", "E_ratio_exact_control_available", False, ratio_e, expected)
        else:
            audit.require("metadata", "supported_relation_kind", False, kind,
                          ["same_function", "pointwise_smaller_source", "supremum_constant"])
        summaries.append(dict(specification))
    return summaries


def independent_guard_violation(specification, source_sha):
    """Inspect invalid premises/finite scalar challenges; never call production."""
    if "input" in specification:
        probe = Audit()
        probe.group("independent_invalid_input")
        try:
            candidate = Model(specification["input"])
            check_binding(probe, candidate, source_sha)
        except Exception as exc:
            return True, {"mode": "independent_invalid_input", "class": type(exc).__name__, "reason": str(exc)}
        return bool(sum(probe.failed_counts.values())), {
            "mode": "independent_invalid_input", "failed_components": sum(probe.failed_counts.values()),
            "failures": probe.failures[:8],
        }
    operation = specification.get("operation")
    if operation == "source_count":
        value = specification["cells"]
        return not 1 <= value <= MAX_SOURCE, {"mode": operation, "value": value, "limit": MAX_SOURCE}
    if operation == "observation_count":
        value = specification["cells"]
        return not 1 <= value <= MAX_OBSERVATION, {"mode": operation, "value": value, "limit": MAX_OBSERVATION}
    if operation in ("input_scalar_power_of_two", "derived_scalar_power_of_two"):
        exponent = specification["exponent"]
        limit = 256 if operation == "input_scalar_power_of_two" else 16384
        return exponent+1 > limit, {"mode": operation, "exact_bit_length": exponent+1, "limit": limit}
    if operation == "work_budget":
        base, effective, blocks = specification["counts"]
        violation = not (1 <= base <= MAX_BASE and 1 <= effective <= MAX_EFFECTIVE and 0 <= blocks <= MAX_BLOCKS)
        violation = violation or base*effective*(blocks+1) > MAX_OVERLAP or 2*ROOT_DEPTH*base > MAX_ROOT_STEPS
        return violation, {"mode": operation, "counts": [base, effective, blocks],
                           "overlap_precharge": base*effective*(blocks+1),
                           "root_precharge": 2*ROOT_DEPTH*base}
    return False, {"mode": "UNSUPPORTED_GUARD_OPERATION", "operation": operation}


def check_guards(audit, specifications, observed, source_sha):
    audit.group("guard_collection")
    expected_ids = [row["id"] for row in specifications]
    actual_ids = [row["id"] for row in observed]
    audit.equal("guard_ids_and_order", actual_ids, expected_ids)
    audit.equal("guard_ids_unique", len(set(actual_ids)), len(actual_ids))
    lookup = {row["id"]: row for row in observed}
    summaries = []
    for specification in specifications:
        identity = specification["id"]
        audit.group("guard/"+identity)
        audit.require("metadata", "saved_guard_exists", identity in lookup, identity, "present")
        if identity not in lookup:
            continue
        row = lookup[identity]
        expected = specification["expected_error_substring"]
        audit.equal("expected_error_bound_to_fixture", row["expected_error_substring"], expected)
        audit.equal("observed_rejection_status", row["status"], "PASS")
        observed_class, observed_error = row["observed_error_class"], row["observed_error"]
        audit.require("metadata", "observed_exception_class", isinstance(observed_class, str) and bool(observed_class),
                      observed_class, "nonempty exception class")
        audit.require("metadata", "expected_substring_in_observed_error",
                      isinstance(observed_error, str) and expected in observed_error,
                      observed_error, expected)
        invalid, reason = independent_guard_violation(specification, source_sha)
        audit.require("exact", "independent_invalid_premise_or_resource", invalid, reason,
                      "independently invalid without production execution")
        summaries.append({"id": identity, "independent_reason": reason})
    return summaries


def run(cases_path, primary_path, source_path):
    case_bytes = cases_path.read_bytes()
    primary_bytes = primary_path.read_bytes()
    source_bytes = source_path.read_bytes()
    case_data = json.loads(case_bytes)
    primary = json.loads(primary_bytes)
    fixture_source = json.loads(source_bytes)
    cases = case_data["cases"]
    records = primary["cases"]
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    audit = Audit()
    audit.group("frozen_inputs_and_saved_primary")
    ids = [case["id"] for case in cases]
    record_ids = [record["id"] for record in records]
    audit.equal("valid_case_ids", record_ids, ids)
    audit.equal("input_case_ids_unique", len(set(ids)), len(ids))
    audit.equal("primary_case_ids_unique", len(set(record_ids)), len(record_ids))
    audit.equal("valid_case_count", case_data["valid_case_count"], len(cases))
    audit.equal("guard_count", case_data["guard_count"], len(case_data["guards"]))
    audit.equal("reference_guard_frozen_in_inputs",
                case_data["reference_relative_guard"], "1e-80")
    audit.equal("reference_precision_frozen_in_inputs", case_data["reference_precision"], PRECISION)
    audit.equal("finite_integer_decimal_digit_limit", sys.get_int_max_str_digits(),
                INTEGER_DECIMAL_DIGIT_LIMIT)
    audit.equal("saved_primary_status", primary["status"], "PASS_SCOPED")
    audit.equal("source_is_not_actual_HD", fixture_source["actual_HD_array"], False)
    audit.equal("source_is_not_physical_consumer", fixture_source["named_physical_consumer"], False)
    by_id = {record["id"]: record for record in records}
    models, summaries = {}, []
    for case in cases:
        cid = case["id"]
        try:
            if cid not in by_id:
                audit.group(cid+"/missing_saved_case")
                audit.require("metadata", "saved_result_present", False, None, cid)
                continue
            model, summary = check_case(audit, case, by_id[cid], source_sha)
            models[cid] = model
            summaries.append(summary)
            audit.group(cid+"/source_artifact_identity")
            audit.equal("source_artifact_canonical_hash",
                        fixture_source["whole_forcing_identities"][cid], forcing_hash(model, case["binding"]))
        except Exception as exc:
            audit.group(cid+"/reference_case_exception")
            audit.require("metadata", "complete_case_verification", False,
                          {"class": type(exc).__name__, "error": str(exc),
                           "traceback": traceback.format_exc()}, "no exception")
            summaries.append({"id": cid, "status": "REFERENCE_CASE_EXCEPTION",
                              "class": type(exc).__name__, "error": str(exc)})
    audit.group("complete_valid_case_coverage")
    audit.equal("independently_constructed_case_count", len(models), len(cases), "coverage")
    relations = check_relations(audit, models, case_data.get("relations", []))
    guards = check_guards(audit, case_data["guards"], primary["guards"], source_sha)
    failures = sum(audit.failed_counts.values())
    for group in audit.groups:
        group["status"] = "PASS" if group["failures"] == 0 else "FAIL"
    return {
        "schema": "WU_R14_INDEPENDENT_REFERENCE_V1",
        "unit": "WU_QUADRATIC_FORCING_R14",
        "status": "PASS" if failures == 0 else "FAIL",
        "checks_total": len(audit.groups),
        "checks_passed": sum(group["failures"] == 0 for group in audit.groups),
        "checks_failed": sum(group["failures"] != 0 for group in audit.groups),
        "component_comparisons": sum(audit.counts.values()),
        "component_counts": dict(audit.counts),
        "component_failures": failures,
        "component_failure_counts": dict(audit.failed_counts),
        "checks": audit.groups, "failures": audit.failures,
        "failure_log_truncated": failures > len(audit.failures),
        "cases": summaries, "relations": relations, "guards": guards,
        "input_identities": {
            "cases_sha256": hashlib.sha256(case_bytes).hexdigest(),
            "primary_sha256": hashlib.sha256(primary_bytes).hexdigest(),
            "fixture_source_sha256": source_sha,
            "reference_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "numeric_reference": {
            "Decimal_precision": PRECISION, "relative_guard": str(RELATIVE_GUARD),
            "guard_fixed_before_execution": True,
            "phi_series_threshold": str(PHI_THRESHOLD), "phi_series_stop": str(PHI_STOP),
            "phi_series_max_terms": PHI_TERMS,
            "integer_decimal_digit_limit": INTEGER_DECIMAL_DIGIT_LIMIT,
            "integer_decimal_digit_limit_actual": sys.get_int_max_str_digits(),
            "rational_text_policy": {
                "grammar": "[+-]?[0-9]+(?:/[+-]?[0-9]+)?",
                "input_max_chars": 2048, "input_max_bits": 256,
                "saved_max_chars": MAX_SAVED_RATIONAL_TEXT,
                "component_max_digits": INTEGER_DECIMAL_DIGIT_LIMIT,
                "saved_max_derived_bits": MAX_DERIVED_BITS,
                "grammar_checked_before_numeric_conversion": True,
                "whitespace_decimal_exponent_rejected": True,
            },
            "strict_decimal_containment_failures_without_guard": audit.strict_decimal_failures,
            "strict_decimal_examples": audit.strict_decimal_examples,
            "meaning": "Independent high-precision numerical corroboration, not interval reference or physical sample validation.",
        },
        "independence": {
            "production_or_predecessor_imports": False,
            "current_R14_production_source_read_by_author": False,
            "predecessor_text_read_as_context": [
                "R13 proof and API", "R13 independent runner text", "R13 source-hash/validation prefix"
            ],
            "inputs_read": ["frozen CASES.json", "frozen FIXTURE_SOURCE.json", "saved PRIMARY_RESULTS.json", "own source identity"],
            "F": "Exact independent J0/J1/J2 age primitives on original unsplit source",
            "grid": "Independent source vertices and translated effective knots",
            "cubic": "Four exact primitive values and Newton power interpolation; independent power/Bernstein conversion",
            "roots": "Exact discriminant and rational/surd comparisons; stable Decimal square roots; zero bisections",
            "E": "Decimal160 signed monomial phi1..phi4 recurrence and exact d=0 fractions",
            "whole": "Exact rootbox/sign/hull/gap checks plus analytic supremum and same-cell E majorants",
            "guard_cases": "Independent invalid-premise/resource checks and saved actual exception metadata; no production guard rerun",
        },
        "physical_status": {
            "actual_HD_reactive_array": "INPUT_PENDING",
            "named_consumer_density_clock": "INPUT_PENDING",
            "HH_R10": "OFF", "production": "NOT_ISSUED", "L4": False,
            "central_delta": 0, "physical_delta": 0,
        },
    }


def main():
    # Finite policy: derived 16384-bit integers need at most 4933 decimal digits.
    # Set a bounded 6000-digit limit for parsing and serialization, never zero.
    sys.set_int_max_str_digits(INTEGER_DECIMAL_DIGIT_LIMIT)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--cases", type=Path)
    parser.add_argument("--primary", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    cases_path = args.cases or root/"verification"/"CASES.json"
    primary_path = args.primary or root/"raw"/"PRIMARY_RESULTS.json"
    source_path = args.source or root/"verification"/"FIXTURE_SOURCE.json"
    output = args.output or root/"raw"/"REFERENCE_RESULTS.json"
    if output.exists():
        raise SystemExit("Refusing to overwrite an existing R14 reference result")
    try:
        with localcontext() as context:
            context.prec = PRECISION
            result = run(cases_path, primary_path, source_path)
    except Exception as exc:
        result = {
            "schema": "WU_R14_INDEPENDENT_REFERENCE_V1",
            "unit": "WU_QUADRATIC_FORCING_R14", "status": "EXECUTION_FAILED",
            "error_class": type(exc).__name__, "error": str(exc),
            "traceback": traceback.format_exc(),
            "meaning": "Observed reference input/runner failure; no success inferred.",
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(json_safe(result), handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({
        "status": result["status"], "output": str(output),
        "checks_passed": result.get("checks_passed"),
        "checks_total": result.get("checks_total"),
        "component_comparisons": result.get("component_comparisons"),
        "component_failures": result.get("component_failures"),
    }, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())


