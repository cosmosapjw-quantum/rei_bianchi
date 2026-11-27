"""Independent WU R15 reference; original primitives, exact algebra, Decimal phi.

No production module is imported.  Authoring does not execute this module.
The root-owned bounded campaign measures imports through final serialization.
"""

from contextlib import contextmanager
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from fractions import Fraction
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import re


INPUT_BITS = 256
DERIVED_BITS = 16384
ALGEBRA_BITS = 1048576
INPUT_CHARS = 2048
DERIVED_CHARS = 10000
DECIMAL_PRECISION = 160
PHI_TERMS = 512
SUBDIVISION_DEPTH = 96
ROOT_DEPTH = 320
DYADIC_SCALE = 1 << 128
GUARD_FACTOR = Fraction(1, 10 ** 80)
INTERIOR_NODES = tuple(Fraction(i, 6) for i in range(1, 6))
OFF_STENCIL_NODES = tuple(Fraction(i, 7) for i in (1, 2, 4, 6))
CASE_IDS = (
    "ZERO", "CUBIC", "GE_CUBIC", "CONSTANT", "AFFINE", "QUADRATIC",
    "Q0_INITIAL_JUMP", "GLOBAL_MEMORY", "NONALIGNED_POSITIVE_D",
    "NONALIGNED_NEGATIVE_D", "SINGLETON", "MAX_COUNTS_ALIGNED",
    "ROOT_THREE_RATIONAL", "ROOT_THREE_MIXED_ALGEBRAIC", "ROOT_SIMPLE_DOUBLE",
    "ROOT_TRIPLE", "ROOT_ENDPOINT_INTERIOR", "ROOTLESS_MIXED_COEFFICIENTS",
    "ROOT_CONSTANT", "SIGNED_DOMAIN_POS16", "SIGNED_DOMAIN_NEG16",
)
ROOT_PATTERNS = {
    "ROOT_THREE_RATIONAL": ("three_simple_rational", [1, 1, 1], []),
    "ROOT_THREE_MIXED_ALGEBRAIC": ("three_simple_mixed_algebraic", [1, 1, 1], []),
    "ROOT_SIMPLE_DOUBLE": ("simple_and_double", [1, 2], []),
    "ROOT_TRIPLE": ("triple", [3], []),
    "ROOT_ENDPOINT_INTERIOR": ("endpoint_and_interior", [1], ["0", "1"]),
    "ROOTLESS_MIXED_COEFFICIENTS": ("rootless_mixed_coefficients", [], []),
    "ROOT_CONSTANT": ("constant", None, None),
}
IDENTITY_FIELDS = (
    "source_id", "clock_id", "clock_unit", "full_A_family_id", "source_locator",
    "source_sha256", "whole_forcing_source_sha256", "scientific_status",
    "state_order", "whole_forcing_hash_format",
)
TRUE_FLAGS = (
    "fixed_K_pi_d", "full_w_box", "all_start_times", "zero_mass_residual",
    "short_remainder_nonexpansive", "forcing_whole_fine_coarse_domain",
)
REQUIRED_INPUT = {
    "states", "q", "tau", "c", "d", "initial", "source_knots",
    "observation_knots", "g_r", "g_e", "binding", "certificate",
}
INPUT_RE = re.compile(r"[+-]?[0-9]+(?:/[+-]?[0-9]+)?", re.ASCII)
SAVED_RE = re.compile(r"-?[0-9]+(?:/[1-9][0-9]*)?", re.ASCII)
SHA_RE = re.compile(r"[0-9a-f]{64}", re.ASCII)


class ReferenceFailure(Exception):
    def __init__(self, category, message, **details):
        super().__init__(message)
        self.category = category
        self.message = message
        self.details = details

    def record(self):
        return {"category": self.category, "message": self.message, "details": self.details}


def need(condition, message, category="EXACT_MISMATCH", **details):
    if not condition:
        raise ReferenceFailure(category, message, **details)


def exact_int(value, label, minimum=None, maximum=None):
    need(type(value) is int, "Expected a JSON integer", "SCHEMA", field=label)
    if minimum is not None:
        need(value >= minimum, "Integer below bound", "SCHEMA", field=label)
    if maximum is not None:
        need(value <= maximum, "Integer above bound", "SCHEMA", field=label)
    return value


def input_rational(value, label="input"):
    if type(value) is int:
        n, d = value, 1
    else:
        need(type(value) is str and 0 < len(value) <= INPUT_CHARS,
             "Invalid input rational type or length", "INPUT_RATIONAL", field=label)
        need(INPUT_RE.fullmatch(value) is not None,
             "Invalid ASCII rational grammar", "INPUT_RATIONAL", field=label)
        parts = value.split("/")
        n = int(parts[0])
        d = int(parts[1]) if len(parts) == 2 else 1
    need(d != 0, "Zero input denominator", "INPUT_RATIONAL", field=label)
    need(abs(n).bit_length() <= INPUT_BITS and abs(d).bit_length() <= INPUT_BITS,
         "Original input component exceeds256bits", "INPUT_RATIONAL", field=label)
    return Fraction(n, d)


def saved_rational(value, label="saved"):
    need(type(value) is str and 0 < len(value) <= DERIVED_CHARS,
         "Invalid saved-derived rational type or length", "SAVED_RATIONAL", field=label)
    need(SAVED_RE.fullmatch(value) is not None,
         "Invalid saved-derived rational grammar", "SAVED_RATIONAL", field=label)
    parts = value.split("/")
    try:
        n = int(parts[0])
        d = int(parts[1]) if len(parts) == 2 else 1
    except ValueError as exc:
        raise ReferenceFailure("SAVED_RATIONAL", "Saved integer conversion failed", field=label) from exc
    need(abs(n).bit_length() <= DERIVED_BITS and d.bit_length() <= DERIVED_BITS,
         "Saved-derived component exceeds16384bits", "SAVED_RATIONAL", field=label)
    q = Fraction(n, d)
    need(str(q) == value, "Saved-derived rational is not canonical reduced text",
         "SAVED_RATIONAL", field=label)
    return q


def qlist(values, n=None, label="saved_list"):
    need(type(values) is list, "Expected rational list", "SCHEMA", field=label)
    if n is not None:
        need(len(values) == n, "Rational list length mismatch", "SCHEMA", field=label,
             expected=n, actual=len(values))
    return [saved_rational(v, label + "/" + str(i)) for i, v in enumerate(values)]


def qmatrix(values, n, label):
    need(type(values) is list and len(values) == n, "Matrix row count mismatch",
         "SCHEMA", field=label, expected=n)
    return [qlist(row, 2, label + "/" + str(i)) for i, row in enumerate(values)]


def canonical_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def file_fingerprint(path):
    data = Path(path).read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def rational_text(value):
    need(isinstance(value, Fraction), "Internal serialization expected Fraction", "REFERENCE_IMPLEMENTATION")
    need(abs(value.numerator).bit_length() <= DERIVED_BITS and value.denominator.bit_length() <= DERIVED_BITS,
         "Reference persisted-derived component exceeds16384bits", "REFERENCE_SERIALIZATION_CAP")
    text = str(value)
    need(len(text) <= DERIVED_CHARS, "Reference rational serialization exceeds10000chars",
         "REFERENCE_SERIALIZATION_CAP")
    return text


def json_ready(value):
    if isinstance(value, Fraction):
        return rational_text(value)
    if isinstance(value, Decimal):
        need(value.is_finite(), "Nonfinite Decimal serialization", "REFERENCE_NUMERICAL")
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    return value


class Arithmetic:
    """Separate output-sized arithmetic and unpersisted squarefree/Sturm cap."""

    def __init__(self):
        self.stats = {
            "max_reference_derived_numerator_bits": 0,
            "max_reference_derived_denominator_bits": 0,
            "max_internal_numerator_bits": 0,
            "max_internal_denominator_bits": 0,
            "polynomial_divisions": 0, "polynomial_eliminations": 0,
            "gcd_calls": 0, "Sturm_chains": 0, "Sturm_counts": 0,
            "squarefree_calls": 0, "nonnegativity_decisions": 0,
            "lower_existence_decisions": 0, "root_splits": 0, "root_visits": 0,
            "original_overlap_evaluations": 0, "original_integral_queries": 0,
        }

    def guard(self, value, algebra=False):
        q = value if isinstance(value, Fraction) else Fraction(value)
        n, d = abs(q.numerator).bit_length(), q.denominator.bit_length()
        prefix = "max_internal_" if algebra else "max_reference_derived_"
        self.stats[prefix + "numerator_bits"] = max(self.stats[prefix + "numerator_bits"], n)
        self.stats[prefix + "denominator_bits"] = max(self.stats[prefix + "denominator_bits"], d)
        cap = ALGEBRA_BITS if algebra else DERIVED_BITS
        need(n <= cap and d <= cap, "Reference exact arithmetic bit cap exceeded",
             "REFERENCE_ARITHMETIC_CAP_EXCEEDED", scope="squarefree_Sturm_unpersisted" if algebra else "derived",
             numerator_bits=n, denominator_bits=d, cap=cap)
        return q


class Polynomials:
    """Ascending power arrays, degree at most four. No production polynomial code."""

    def __init__(self, arithmetic, algebra=False):
        self.a = arithmetic
        self.algebra = algebra

    def q(self, value):
        return self.a.guard(value, self.algebra)

    def trim(self, p):
        p = [self.q(c) for c in p] or [Fraction(0)]
        while len(p) > 1 and p[-1] == 0:
            p.pop()
        need(len(p) <= 5, "Polynomial degree exceeds4", "REFERENCE_POLYNOMIAL_CAP")
        return p

    def zero(self, p):
        return len(p) == 1 and p[0] == 0

    def add(self, p, r):
        n = max(len(p), len(r))
        return self.trim([(p[i] if i < len(p) else 0) + (r[i] if i < len(r) else 0) for i in range(n)])

    def scale(self, p, c):
        return self.trim([self.q(v * c) for v in p])

    def sub(self, p, r):
        return self.add(p, self.scale(r, -1))

    def mul(self, p, r):
        p, r = self.trim(p), self.trim(r)
        if self.zero(p) or self.zero(r):
            return [Fraction(0)]
        need(len(p) + len(r) - 2 <= 4, "Product degree exceeds4", "REFERENCE_POLYNOMIAL_CAP")
        out = [Fraction(0)] * (len(p) + len(r) - 1)
        for i, c in enumerate(p):
            for j, d in enumerate(r):
                out[i + j] = self.q(out[i + j] + self.q(c * d))
        return self.trim(out)

    def derivative(self, p):
        return self.trim([self.q(i * p[i]) for i in range(1, len(p))])

    def evaluate(self, p, x):
        value = Fraction(0)
        for c in reversed(p):
            value = self.q(self.q(value * x) + c)
        return value

    def affine(self, p, offset, width):
        out = [Fraction(0)]
        for c in reversed(p):
            out = self.add(self.mul(out, [offset, width]), [c])
        return self.trim(out)

    def monic(self, p):
        p = self.trim(p)
        return p if self.zero(p) else self.scale(p, self.q(1 / p[-1]))

    def divide(self, numerator, denominator):
        self.a.stats["polynomial_divisions"] += 1
        p, d = self.trim(numerator), self.trim(denominator)
        need(not self.zero(d), "Polynomial zero divisor", "REFERENCE_IMPLEMENTATION")
        out = [Fraction(0)] * max(1, len(p) - len(d) + 1)
        steps = 0
        while not self.zero(p) and len(p) >= len(d):
            steps += 1
            need(steps <= 5, "Long-division elimination cap exceeded", "REFERENCE_POLYNOMIAL_CAP")
            self.a.stats["polynomial_eliminations"] += 1
            shift = len(p) - len(d)
            lead = self.q(p[-1] / d[-1])
            out[shift] = self.q(out[shift] + lead)
            for i, c in enumerate(d):
                p[i + shift] = self.q(p[i + shift] - self.q(lead * c))
            p = self.trim(p)
        return self.trim(out), p

    def quotient(self, p, d):
        q, remainder = self.divide(p, d)
        need(self.zero(remainder), "Expected exact polynomial quotient", "REFERENCE_IMPLEMENTATION")
        return q

    def gcd(self, p, r):
        self.a.stats["gcd_calls"] += 1
        p, r = self.trim(p), self.trim(r)
        steps = 0
        while not self.zero(r):
            steps += 1
            need(steps <= 5, "Euclidean chain cap exceeded", "REFERENCE_POLYNOMIAL_CAP")
            _, rem = self.divide(p, r)
            p, r = r, rem
        return self.monic(p)

    def squarefree_factors(self, p):
        self.a.stats["squarefree_calls"] += 1
        p = self.trim(p)
        if len(p) <= 1:
            return []
        p = self.monic(p)
        c = self.gcd(p, self.derivative(p))
        w = self.quotient(p, c)
        factors = []
        for multiplicity in range(1, 5):
            if len(w) == 1:
                break
            y = self.gcd(w, c)
            factor = self.monic(self.quotient(w, y))
            if len(factor) > 1:
                factors.append((multiplicity, factor))
            w, c = y, self.quotient(c, y)
        need(len(w) == 1, "Squarefree multiplicity loop exceeded4", "REFERENCE_POLYNOMIAL_CAP")
        rebuilt = [Fraction(1)]
        for multiplicity, factor in factors:
            for _ in range(multiplicity):
                rebuilt = self.mul(rebuilt, factor)
        need(self.monic(rebuilt) == p, "Squarefree reconstruction mismatch", "REFERENCE_IMPLEMENTATION")
        return factors

    def squarefree(self, p):
        p = self.trim(p)
        if len(p) <= 1:
            return p
        return self.monic(self.quotient(p, self.gcd(p, self.derivative(p))))

    def sturm(self, squarefree):
        p = self.monic(squarefree)
        if len(p) <= 1:
            return [p]
        self.a.stats["Sturm_chains"] += 1
        chain = [p, self.derivative(p)]
        divisions = 0
        while not self.zero(chain[-1]):
            divisions += 1
            need(divisions <= 5, "Sturm division cap exceeded", "REFERENCE_POLYNOMIAL_CAP")
            _, remainder = self.divide(chain[-2], chain[-1])
            if self.zero(remainder):
                break
            chain.append(self.scale(remainder, -1))
            need(len(chain) <= 5, "Sturm sequence length exceeds5", "REFERENCE_POLYNOMIAL_CAP")
        return chain

    def sign_side(self, p, x, side):
        derivative = p
        for order in range(5):
            value = self.evaluate(derivative, x)
            if value:
                sign = 1 if value > 0 else -1
                return sign if side > 0 or order % 2 == 0 else -sign
            if len(derivative) == 1:
                return 0
            derivative = self.derivative(derivative)
        raise ReferenceFailure("REFERENCE_POLYNOMIAL_CAP", "One-sided sign order exceeded4")

    @staticmethod
    def variation(signs):
        nonzero = [s for s in signs if s]
        return sum(a != b for a, b in zip(nonzero, nonzero[1:]))

    def count_open(self, chain, left, right):
        need(left < right, "Invalid Sturm interval", "REFERENCE_IMPLEMENTATION")
        if len(chain[0]) <= 1:
            return 0
        self.a.stats["Sturm_counts"] += 1
        vl = self.variation([self.sign_side(p, left, 1) for p in chain])
        vr = self.variation([self.sign_side(p, right, -1) for p in chain])
        count = vl - vr
        need(0 <= count <= len(chain[0]) - 1, "Invalid Sturm root count", "REFERENCE_IMPLEMENTATION")
        return count

    def nonnegative(self, original):
        self.a.stats["nonnegativity_decisions"] += 1
        p = self.trim(original)
        if len(p) == 1:
            return p[0] >= 0
        if self.evaluate(p, Fraction(0)) < 0 or self.evaluate(p, Fraction(1)) < 0:
            return False
        factors = self.squarefree_factors(p)
        odd = [Fraction(1)]
        for multiplicity, factor in factors:
            if multiplicity % 2:
                odd = self.mul(odd, factor)
        for endpoint in (Fraction(0), Fraction(1)):
            if len(odd) > 1 and self.evaluate(odd, endpoint) == 0:
                odd = self.quotient(odd, [-endpoint, Fraction(1)])
        if len(odd) > 1 and self.count_open(self.sturm(odd), Fraction(0), Fraction(1)):
            return False
        for x in INTERIOR_NODES:
            value = self.evaluate(p, x)
            if value:
                return value > 0
        raise ReferenceFailure("REFERENCE_IMPLEMENTATION", "Nonzero degree<=4 polynomial vanished at five probes")

    def some_nonnegative(self, original):
        self.a.stats["lower_existence_decisions"] += 1
        p = self.trim(original)
        if len(p) == 1:
            return p[0] >= 0
        for x in (Fraction(0), Fraction(1)) + INTERIOR_NODES:
            if self.evaluate(p, x) >= 0:
                return True
        return self.count_open(self.sturm(self.squarefree(p)), Fraction(0), Fraction(1)) > 0

    def bernstein_to_power(self, bernstein):
        n = len(bernstein) - 1
        out = [Fraction(0)] * (n + 1)
        for i, b in enumerate(bernstein):
            for j in range(n - i + 1):
                out[i + j] = self.q(out[i + j] + b * comb(n, i) * comb(n - i, j) * ((-1) ** j))
        return self.trim(out)

    def power_to_bernstein(self, p, degree):
        need(0 <= degree <= 4 and len(p) - 1 <= degree, "Invalid Bernstein elevation degree", "REFERENCE_IMPLEMENTATION")
        return [self.q(sum((p[m] * Fraction(comb(i, m), comb(degree, m))
                            for m in range(min(i, len(p) - 1) + 1)), Fraction(0)))
                for i in range(degree + 1)]

    def interpolate(self, nodes, values):
        need(len(nodes) == len(values) == 5 and len(set(nodes)) == 5,
             "Quartic interpolation requires five distinct exact nodes", "REFERENCE_IMPLEMENTATION")
        out = [Fraction(0)]
        for i, x in enumerate(nodes):
            term = [Fraction(1)]
            denominator = Fraction(1)
            for j, y in enumerate(nodes):
                if i != j:
                    term = self.mul(term, [-y, Fraction(1)])
                    denominator = self.q(denominator * (x - y))
            out = self.add(out, self.scale(term, self.q(values[i] / denominator)))
        return self.trim(out)

    def interval_evaluate(self, p, left, right):
        lower = upper = Fraction(0)
        for coefficient in reversed(p):
            products = [self.q(lower * left), self.q(lower * right),
                        self.q(upper * left), self.q(upper * right)]
            lower, upper = self.q(min(products) + coefficient), self.q(max(products) + coefficient)
        return lower, upper


class OriginalModel:
    def __init__(self, raw, arithmetic):
        need(type(raw) is dict and set(raw) == REQUIRED_INPUT, "Input key set mismatch", "INPUT_SCHEMA")
        self.raw = raw
        self.a = arithmetic
        self.p = Polynomials(arithmetic)
        self.states = exact_int(raw["states"], "states", 1, 13)
        self.q, self.tau, self.c, self.d = [input_rational(raw[k], k) for k in ("q", "tau", "c", "d")]
        need(0 <= self.q <= 1 and self.tau > 0 and self.c >= 0, "Comparison parameter domain", "INPUT_DOMAIN")
        need(type(raw["initial"]) is list and len(raw["initial"]) == 2, "Initial pair shape", "INPUT_SCHEMA")
        self.initial = [input_rational(v, "initial") for v in raw["initial"]]
        need(min(self.initial) >= 0, "Negative initial value", "INPUT_DOMAIN")
        self.source = self._knots(raw["source_knots"], 17, "source_knots")
        self.observation = self._knots(raw["observation_knots"], 33, "observation_knots")
        self.t0, self.T = self.source[0], self.source[-1]
        need((self.observation[0], self.observation[-1]) == (self.t0, self.T),
             "Source/observation horizon mismatch", "INPUT_DOMAIN")
        self.blocks = (self.T - self.t0) // self.tau
        need(self.blocks <= 8 and abs(self.d) * (self.T - self.t0) <= 16,
             "Block or scalar horizon exceeds contract", "INPUT_DOMAIN")
        self.gr = self._rows(raw["g_r"], "g_r")
        self.ge = self._rows(raw["g_e"], "g_e")
        if self.states == 1:
            need(self.initial[0] == 0 and all(v == 0 for row in self.gr for v in row),
                 "Singleton zero-mass premise violated", "INPUT_DOMAIN")
        self.gr_power = [self.p.bernstein_to_power(row) for row in self.gr]
        self.ge_power = [self.p.bernstein_to_power(row) for row in self.ge]
        clock = set(self.observation)
        for s in self.source:
            for k in range(self.blocks + 1):
                shifted = s + k * self.tau
                if self.t0 <= shifted <= self.T:
                    clock.add(shifted)
        self.base = sorted(clock)
        self.nbase = len(self.base) - 1
        self.overlap_precharge = self.nbase * len(self.gr) * (self.blocks + 1)
        need(self.nbase <= 512 and self.overlap_precharge <= 73728, "Base work precharge exceeds contract", "INPUT_WORK")
        self.qpowers = [self.a.guard(self.q ** k) for k in range(self.blocks + 1)]
        self._F_cache = {}

    def _knots(self, raw, maximum, label):
        need(type(raw) is list and 2 <= len(raw) <= maximum, "Knot count outside domain", "INPUT_SCHEMA", field=label)
        knots = [input_rational(v, label) for v in raw]
        need(all(a < b for a, b in zip(knots, knots[1:])), "Knots not strictly increasing", "INPUT_DOMAIN", field=label)
        return knots

    def _rows(self, rows, label):
        need(type(rows) is list and len(rows) == len(self.source) - 1, "Source row count mismatch", "INPUT_SCHEMA", field=label)
        out = []
        for row in rows:
            need(type(row) is list and len(row) == 4, "Source row is not B3", "INPUT_SCHEMA", field=label)
            values = [input_rational(v, label) for v in row]
            need(min(values) >= 0, "Source B3 coefficient negative", "INPUT_DOMAIN", field=label)
            out.append(values)
        return out

    def kernel(self, time):
        need(self.t0 <= time <= self.T, "Kernel query outside horizon", "REFERENCE_IMPLEMENTATION")
        k = (time - self.t0) // self.tau
        return self.qpowers[k]

    def F(self, time):
        if time in self._F_cache:
            return self._F_cache[time]
        need(self.t0 <= time <= self.T, "Integral query outside horizon", "REFERENCE_IMPLEMENTATION")
        self.a.stats["original_integral_queries"] += 1
        total = Fraction(0)
        for j, coefficients in enumerate(self.gr_power):
            a, b = self.source[j:j + 2]
            length = b - a
            for k, weight in enumerate(self.qpowers):
                self.a.stats["original_overlap_evaluations"] += 1
                left = max(a, time - (k + 1) * self.tau)
                right = min(b, time - k * self.tau)
                if right <= left or weight == 0:
                    continue
                xl, xr = self.a.guard((left - a) / length), self.a.guard((right - a) / length)
                integral = Fraction(0)
                for m, coefficient in enumerate(coefficients):
                    primitive = self.a.guard(length * self.a.guard(xr ** (m + 1) - xl ** (m + 1)) / (m + 1))
                    integral = self.a.guard(integral + self.a.guard(coefficient * primitive))
                total = self.a.guard(total + self.a.guard(weight * integral))
        self._F_cache[time] = total
        return total

    def R(self, time):
        return self.a.guard(self.kernel(time) * self.initial[0] + self.F(time))

    def cell(self, index):
        left, right = self.base[index:index + 2]
        duration = right - left
        values = [self.R(left + duration * u) for u in INTERIOR_NODES]
        power = self.p.interpolate(INTERIOR_NODES, values)
        for u in OFF_STENCIL_NODES:
            need(self.p.evaluate(power, u) == self.R(left + duration * u),
                 "Original integral and independent quartic disagree off stencil", "QUARTIC_IDENTITY", cell=index)
        midpoint = (left + right) / 2
        source_index = next(j for j, (a, b) in enumerate(zip(self.source, self.source[1:])) if a < midpoint < b)
        a, b = self.source[source_index:source_index + 2]
        ge_power = self.p.affine(self.ge_power[source_index], (left - a) / (b - a), duration / (b - a))
        forcing = self.p.add(self.p.scale(power, self.c), ge_power)
        initial_piece = self.a.guard(self.kernel(left) * self.initial[0])
        return {
            "left": left, "right": right, "duration": duration, "power": power,
            "bernstein": self.p.power_to_bernstein(power, 4), "initial_piece": initial_piece,
            "F_power": self.p.sub(power, [initial_piece]), "ge_power": ge_power,
            "ge_bernstein": self.p.power_to_bernstein(ge_power, 3), "forcing_power": forcing,
            "forcing_bernstein": self.p.power_to_bernstein(forcing, 4),
            "actual_right_endpoint": self.R(right), "right_left_limit": self.p.evaluate(power, Fraction(1)),
        }

    def nonempty_overlap_count(self):
        count = 0
        for left, right in zip(self.base, self.base[1:]):
            t = (left + right) / 2
            for a, b in zip(self.source, self.source[1:]):
                for k in range(self.blocks + 1):
                    count += min(b, t - k * self.tau) > max(a, t - (k + 1) * self.tau)
        return count


class DecimalReference:
    def __init__(self):
        self.cache = {}

    @staticmethod
    def decimal(q):
        return Decimal(q.numerator) / Decimal(q.denominator)

    def functions(self, z):
        if z in self.cache:
            return self.cache[z]
        zd = self.decimal(z)
        need(abs(z) <= 16, "Reference phi argument outside fixed domain", "REFERENCE_NUMERICAL")
        phis = []
        for k in range(1, 6):
            term = Decimal(1) / Decimal(factorial(k))
            total = term
            for j in range(1, PHI_TERMS):
                term = term * zd / Decimal(j + k)
                total += term
            phis.append(+total)
        result = (zd.exp(), tuple(phis))
        self.cache[z] = result
        return result

    def integral(self, coefficients, duration, phis):
        # Coefficients are powers of normalized u. Exactly one duration factor.
        total = Decimal(0)
        for m, coefficient in enumerate(coefficients):
            total += self.decimal(coefficient) * Decimal(factorial(m)) * phis[m]
        return self.decimal(duration) * total

    def weights(self, duration, phis):
        out = []
        for i in range(5):
            coefficients = [Fraction(0)] * 5
            for j in range(5 - i):
                coefficients[i + j] = Fraction(comb(4, i) * comb(4 - i, j) * ((-1) ** j))
            out.append(self.integral(coefficients, duration, phis))
        return out


class Audit:
    def __init__(self):
        self.checks = []
        self.strict_misses = 0
        self.strict_examples = []
        self.guarded_comparisons = 0
        self.guarded_failures = 0
        self.strict_by_case = {}
        self.current_details = None

    @contextmanager
    def phase(self, case_id, check_id, kind="EXACT"):
        row = {"id": check_id, "case_id": case_id, "kind": kind, "status": "RUNNING", "details": {}}
        self.checks.append(row)
        old = self.current_details
        self.current_details = row["details"]
        try:
            yield row["details"]
        except ReferenceFailure as exc:
            row["status"] = "FAIL"
            row["error"] = exc.record()
            raise
        except Exception as exc:
            row["status"] = "FAIL"
            row["error"] = {"category": "REFERENCE_IMPLEMENTATION_EXCEPTION", "message": str(exc), "exception_type": type(exc).__name__}
            raise
        else:
            row["status"] = "PASS"
        finally:
            self.current_details = old

    def contains(self, reference, lower, upper, case_id, label):
        need(lower <= upper, "Reversed saved interval", "SAVED_INTERVAL", field=label)
        need(isinstance(reference, Decimal) and reference.is_finite(), "Nonfinite Decimal reference", "REFERENCE_NUMERICAL", field=label)
        # Compare the Decimal's exact rational value against exact saved bounds.
        # Rounding the bounds to Decimal first would hide strict misses.
        value = Fraction(reference)
        strict = lower <= value <= upper
        guard = GUARD_FACTOR * max(Fraction(1), abs(value), abs(lower), abs(upper))
        guarded = lower - guard <= value <= upper + guard
        self.guarded_comparisons += 1
        if not strict:
            self.strict_misses += 1
            self.strict_by_case[case_id] = self.strict_by_case.get(case_id, 0) + 1
            if len(self.strict_examples) < 50:
                self.strict_examples.append({
                    "case_id": case_id, "field": label, "reference": str(reference),
                    "lower_exact": rational_text(lower), "upper_exact": rational_text(upper),
                    "guard_decimal": str(DecimalReference.decimal(guard)), "within_guard": guarded,
                })
        if not guarded:
            self.guarded_failures += 1
        need(guarded, "Decimal reference outside fixed guarded interval", "GUARDED_CORROBORATION_FAILURE",
             case_id=case_id, field=label, strict_membership=strict, reference=str(reference))


def dyadic_pair(lower, upper):
    return (Fraction((lower.numerator * DYADIC_SCALE) // lower.denominator, DYADIC_SCALE),
            Fraction(-((-upper.numerator * DYADIC_SCALE) // upper.denominator), DYADIC_SCALE))


def check_supremum_record(record, lower, upper, mb, cmax, gap_bound):
    expected = {
        "exact_lower": lower, "exact_upper": upper, "exact_gap": upper - lower,
        "M_B": mb, "Cmax": cmax, "proved_gap_bound": gap_bound,
    }
    for key, value in expected.items():
        need(saved_rational(record[key], "supremum/" + key) == value,
             "Supremum record mismatch", "SUPREMUM_RECORD", field=key)
    need(lower <= upper and upper - lower <= gap_bound, "Exact supremum gap bound failed", "SUPREMUM_GAP")
    dlo, dhi = dyadic_pair(lower, upper)
    need(saved_rational(record["dyadic_lower"]) == dlo and saved_rational(record["dyadic_upper"]) == dhi,
         "Dyadic outward conversion differs", "DYADIC_ROUNDING")
    need(dlo <= lower <= upper <= dhi and (dhi - dlo) - (upper - lower) <= Fraction(2, DYADIC_SCALE),
         "Dyadic width overhead failed", "DYADIC_ROUNDING")
    return dlo, dhi


def verify_partition(cell, record, arithmetic):
    p = Polynomials(arithmetic)
    alg = Polynomials(arithmetic, algebra=True)
    power, bernstein = cell["power"], cell["bernstein"]
    derivative = p.derivative(power)
    sub = record["subdivision"]
    need(sub["method"] == "BERNSTEIN_DERIVATIVE_VARIATION_V1" and sub["depth_limit"] == 96,
         "Subdivision method/depth mismatch", "PARTITION")
    need(qlist(sub["derivative_bernstein"], 4) == p.power_to_bernstein(derivative, 3),
         "Original derivative B3 mismatch", "PARTITION")
    leaves = sub["leaves"]
    need(type(leaves) is list and 1 <= len(leaves) <= 289, "Leaf allocation outside cap", "PARTITION")
    previous = Fraction(0)
    lower_values, upper_values, parsed = [], [], []
    depths = []
    unresolved = []
    for index, leaf in enumerate(leaves):
        left, right = saved_rational(leaf["left"]), saved_rational(leaf["right"])
        depth = exact_int(leaf["depth"], "leaf/depth", 0, 96)
        width = right - left
        need(left == previous and 0 <= left < right <= 1, "Incomplete/overlapping leaf partition", "PARTITION", leaf=index)
        need(width == Fraction(1, 1 << depth) and (left * (1 << depth)).denominator == 1,
             "Leaf does not lie on declared dyadic grid", "PARTITION", leaf=index)
        previous = right
        restricted = p.affine(power, left, width)
        rd = p.derivative(restricted)
        rb = p.power_to_bernstein(restricted, 4)
        db = p.power_to_bernstein(rd, 3)
        variation = Polynomials.variation([1 if v > 0 else -1 if v < 0 else 0 for v in db])
        need(exact_int(leaf["variation"], "leaf/variation", 0, 3) == variation,
             "Leaf variation metadata differs from own restricted derivative", "PARTITION", leaf=index)
        endpoint_values = [p.evaluate(power, left), p.evaluate(power, right)]
        need(qlist(leaf["endpoint_values"], 2) == endpoint_values, "Leaf endpoint value mismatch", "PARTITION", leaf=index)
        kind = leaf["kind"]
        if kind == "CONSTANT":
            need(p.zero(rd) and variation == 0, "False constant leaf", "PARTITION", leaf=index)
            lo = hi = endpoint_values[0]
        elif kind in ("NONDECREASING", "NONINCREASING"):
            need(not p.zero(rd) and variation == 0, "Monotone leaf variation invalid", "PARTITION", leaf=index)
            signed = rd if kind == "NONDECREASING" else p.scale(rd, -1)
            need(alg.nonnegative(signed), "Independent derivative-sign check failed", "PARTITION", leaf=index)
            lo = hi = max(endpoint_values)
        elif kind == "DEPTH_LIMIT":
            need(depth == 96 and variation > 0, "False depth-limit leaf", "PARTITION", leaf=index)
            midpoint = (left + right) / 2
            midpoint_value = p.evaluate(power, midpoint)
            need(saved_rational(leaf["midpoint"]) == midpoint and saved_rational(leaf["midpoint_value"]) == midpoint_value,
                 "Depth-limit midpoint mismatch", "PARTITION", leaf=index)
            need(qlist(leaf["bernstein"], 5) == rb, "Independent restricted B4 mismatch", "PARTITION", leaf=index)
            lo, hi = max(endpoint_values + [midpoint_value]), max(rb)
            unresolved.append(width)
        else:
            raise ReferenceFailure("PARTITION", "Unknown terminal leaf kind", kind=str(kind))
        need(saved_rational(leaf["lower"]) == lo and saved_rational(leaf["upper"]) == hi,
             "Leaf maximum rule mismatch", "PARTITION", leaf=index)
        lower_values.append(lo)
        upper_values.append(hi)
        depths.append(depth)
        parsed.append({"left": left, "right": right, "kind": kind, "depth": depth})
    need(previous == 1, "Terminal partition does not reach1", "PARTITION")
    splits = exact_int(sub["splits_actual"], "splits_actual", 0, 288)
    visits = exact_int(sub["nodes_visited"], "nodes_visited", 1, 577)
    need(len(leaves) == splits + 1 and visits == 2 * splits + 1, "Binary-tree counter mismatch", "PARTITION_WORK")
    need(exact_int(sub["terminal_leaves"], "terminal_leaves") == len(leaves)
         and exact_int(sub["max_depth"], "max_depth") == max(depths)
         and exact_int(sub["depth_limit_leaves"], "depth_limit_leaves", 0, 3) == len(unresolved),
         "Terminal count/depth mismatch", "PARTITION_WORK")
    need(saved_rational(sub["max_unresolved_width"]) == max(unresolved, default=Fraction(0)),
         "Unresolved width mismatch", "PARTITION_WORK")
    actual = cell["actual_right_endpoint"]
    lower, upper = max(lower_values + [actual]), max(upper_values + [actual])
    mb = 4 * max(abs(b - a) for a, b in zip(bernstein, bernstein[1:]))
    cmax = max(bernstein)
    gap_bound = mb / (1 << 96)
    return {"lower": lower, "upper": upper, "M_B": mb, "Cmax": cmax,
            "gap_bound": gap_bound, "dyadic": dyadic_pair(lower, upper), "splits": splits, "visits": visits,
            "leaves": parsed, "left_limit_witness": cell["right_left_limit"]}


def root_diagnostic(cell, verified, case_id, arithmetic):
    p = Polynomials(arithmetic)
    alg = Polynomials(arithmetic, algebra=True)
    power = cell["power"]
    derivative = alg.derivative(power)
    pattern, expected_multiplicities, expected_endpoints = ROOT_PATTERNS[case_id]
    if alg.zero(derivative):
        need(pattern == "constant", "Unexpected zero derivative", "ROOT_PATTERN")
        return {"pattern": pattern, "derivative_identically_zero": True,
                "root_count": None, "semantics": "Every point critical; no finite root count"}
    need(pattern != "constant", "Expected constant derivative branch", "ROOT_PATTERN")
    factors = alg.squarefree_factors(derivative)
    squarefree = alg.squarefree(derivative)
    chain = alg.sturm(squarefree)
    factor_chains = [(m, f, alg.sturm(f)) for m, f in factors]
    multiplicities = []
    endpoint_records = []
    for multiplicity, factor, fc in factor_chains:
        multiplicities.extend([multiplicity] * alg.count_open(fc, Fraction(0), Fraction(1)))
        for endpoint in (Fraction(0), Fraction(1)):
            if alg.evaluate(factor, endpoint) == 0:
                endpoint_records.append({"point": endpoint, "multiplicity": multiplicity})
    need(sorted(multiplicities) == expected_multiplicities,
         "Interior root multiplicities differ from frozen control", "ROOT_PATTERN", case_id=case_id)
    need(sorted(str(row["point"]) for row in endpoint_records) == sorted(expected_endpoints),
         "Endpoint root pattern differs", "ROOT_PATTERN", case_id=case_id)
    count = alg.count_open(chain, Fraction(0), Fraction(1))
    need(count == len(multiplicities), "Squarefree root-count mismatch", "ROOT_PATTERN")
    todo = [(Fraction(0), Fraction(1), 0, count)] if count else []
    boxes, points = [], []
    splits = 0
    while todo:
        left, right, depth, number = todo.pop()
        if depth == ROOT_DEPTH:
            boxes.append({"left": left, "right": right, "depth": depth, "distinct_roots": number})
            continue
        midpoint = (left + right) / 2
        at_root = alg.evaluate(squarefree, midpoint) == 0
        nl = alg.count_open(chain, left, midpoint)
        nr = alg.count_open(chain, midpoint, right)
        need(nl + nr + int(at_root) == number, "Root split lost multiplicity-free count", "ROOT_ISOLATION")
        splits += 1
        need(splits <= 3 * ROOT_DEPTH, "Root diagnostic split cap exceeded", "REFERENCE_POLYNOMIAL_CAP")
        if at_root:
            mult = next(m for m, factor, _ in factor_chains if alg.evaluate(factor, midpoint) == 0)
            points.append({"point": midpoint, "multiplicity": mult})
        if nr:
            todo.append((midpoint, right, depth + 1, nr))
        if nl:
            todo.append((left, midpoint, depth + 1, nl))
    need(sum(row["distinct_roots"] for row in boxes) + len(points) == count,
         "Root diagnostic coverage incomplete", "ROOT_ISOLATION")
    values_lower = [p.evaluate(power, Fraction(0)), p.evaluate(power, Fraction(1))]
    values_upper = list(values_lower)
    for row in points:
        row["value"] = p.evaluate(power, row["point"])
        values_lower.append(row["value"])
        values_upper.append(row["value"])
    for row in boxes:
        left, right = row["left"], row["right"]
        row["multiplicities"] = {str(m): alg.count_open(fc, left, right) for m, _, fc in factor_chains}
        need(sum(row["multiplicities"].values()) == row["distinct_roots"], "Root cluster multiplicity accounting failed", "ROOT_ISOLATION")
        row["value_interval"] = p.interval_evaluate(power, left, right)
        row["midpoint_value"] = p.evaluate(power, (left + right) / 2)
        row["midpoint_Decimal"] = DecimalReference.decimal(row["midpoint_value"])
        row["interval_semantics"] = "OPEN_ROOT_COUNT_WITH_CLOSED_VALUE_HULL"
        values_lower.append(row["midpoint_value"])
        values_upper.append(row["value_interval"][1])
    lower, upper = max(values_lower), max(values_upper)
    need(verified["upper"] >= lower and verified["lower"] <= upper,
         "Independent critical-value bracket disjoint from supplied supremum", "ROOT_EXTREMUM")
    boundaries = {row["left"] for row in verified["leaves"]} | {row["right"] for row in verified["leaves"]}
    boundary_count = sum(alg.evaluate(squarefree, x) == 0 for x in boundaries if 0 < x < 1)
    interior_count = 0
    for leaf in verified["leaves"]:
        number = alg.count_open(chain, leaf["left"], leaf["right"])
        if leaf["kind"] in ("NONDECREASING", "NONINCREASING"):
            need(number == 0, "A V0 nonconstant Bernstein derivative has an unexpected interior root", "ROOT_LEAF_COVERAGE")
        interior_count += number
    need(interior_count + boundary_count == count, "Production partition root coverage incomplete", "ROOT_LEAF_COVERAGE")
    arithmetic.stats["root_splits"] += splits
    arithmetic.stats["root_visits"] += 2 * splits + 1
    return {"pattern": pattern, "derivative_identically_zero": False, "distinct_open_roots": count,
            "open_multiplicities": sorted(multiplicities), "endpoint_roots": endpoint_records,
            "point_roots": sorted(points, key=lambda row: row["point"]),
            "root_intervals_or_clusters": sorted(boxes, key=lambda row: row["left"]),
            "root_clusters_unresolved": sum(row["distinct_roots"] > 1 for row in boxes),
            "critical_supremum_bracket": [lower, upper], "splits": splits, "visits": 2 * splits + 1,
            "partition_open_root_count": interior_count, "partition_internal_boundary_root_count": boundary_count}


def verify_binding(model, fixture, source_row, source_sha256, result):
    raw = model.raw
    binding, certificate = raw["binding"], raw["certificate"]
    need(type(binding) is dict and set(binding) == set(IDENTITY_FIELDS), "Binding key set mismatch", "BINDING")
    need(type(certificate) is dict and set(certificate) == set(IDENTITY_FIELDS) | set(TRUE_FLAGS) | {"generator", "q", "tau", "t0", "T", "w_box"},
         "Certificate key set mismatch", "BINDING")
    for key in IDENTITY_FIELDS:
        need(certificate.get(key) == binding[key], "Certificate identity mismatch", "BINDING", field=key)
    for key in TRUE_FLAGS:
        need(certificate.get(key) is True, "Required full-A declaration not true", "BINDING", field=key)
    need(certificate.get("generator") == "A=K+wH;H=pi*d^T-diag(d)", "Wrong declared generator", "BINDING")
    need(binding["scientific_status"] == "ARITHMETIC_CONTROL_PREMISE"
         and binding["whole_forcing_hash_format"] == "WU_R15_WHOLE_FORCING_V1",
         "Control scientific/hash schema mismatch", "BINDING")
    state_order = binding["state_order"]
    need(type(state_order) is list and len(state_order) == model.states
         and len(set(state_order)) == model.states
         and all(type(s) is str and 0 < len(s) <= 128 for s in state_order),
         "State order mismatch", "BINDING")
    for key in ("source_id", "clock_id", "clock_unit", "full_A_family_id", "source_locator"):
        need(type(binding[key]) is str and 0 < len(binding[key]) <= 256, "Identity text invalid", "BINDING", field=key)
    need(binding["source_locator"] == "verification/ARITHMETIC_SOURCE.json#" + fixture["id"],
         "Arithmetic source locator mismatch", "BINDING")
    need(binding["source_sha256"] == source_sha256, "Frozen source bytes hash mismatch", "BINDING")
    bare_input = {k: v for k, v in raw.items() if k not in ("binding", "certificate")}
    need(source_row["input"] == bare_input and source_row["expected"] == fixture["expected"],
         "Source model differs from frozen input or expected design target", "BINDING")
    for key, value in (("q", model.q), ("tau", model.tau), ("t0", model.t0), ("T", model.T)):
        need(input_rational(certificate[key], "certificate/" + key) == value,
             "Certificate parameter mismatch", "BINDING", field=key)
    need(type(certificate["w_box"]) is list and len(certificate["w_box"]) == 2, "Invalid w box", "BINDING")
    w0, w1 = [input_rational(v, "w_box") for v in certificate["w_box"]]
    need(0 <= w0 <= w1, "Unordered/negative w box", "BINDING")
    payload = {
        "schema": "WU_R15_WHOLE_FORCING_V1", "source_id": binding["source_id"],
        "clock_id": binding["clock_id"], "clock_unit": binding["clock_unit"],
        "state_order": state_order, "source_knots": [str(x) for x in model.source],
        "g_r": [[str(v) for v in row] for row in model.gr],
        "g_e": [[str(v) for v in row] for row in model.ge],
    }
    digest = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    need(binding["whole_forcing_source_sha256"] == digest, "Canonical whole-forcing hash mismatch", "BINDING")
    parameters = result["parameters"]
    for key, value in (("q", model.q), ("tau", model.tau), ("c", model.c), ("d", model.d), ("t0", model.t0), ("T", model.T)):
        need(saved_rational(parameters[key], "parameters/" + key) == value, "Saved parameter mismatch", "BINDING", field=key)
    need(qlist(parameters["initial"], 2) == model.initial
         and exact_int(parameters["states"], "parameters/states") == model.states
         and exact_int(parameters["full_blocks"], "parameters/full_blocks") == model.blocks,
         "Saved initial/count parameter mismatch", "BINDING")
    need(parameters["binding"] == binding and parameters["certificate"] == certificate,
         "Saved binding/certificate differs from frozen declared input", "BINDING")
    saved_source = result["source"]
    need(qlist(saved_source["knots"]) == model.source, "Saved source clock mismatch", "BINDING")
    for key, rows in (("g_r", model.gr), ("g_e", model.ge)):
        need(type(saved_source[key]) is list and len(saved_source[key]) == len(rows), "Saved source row count mismatch", "BINDING")
        need([qlist(row, 4) for row in saved_source[key]] == rows, "Saved source coefficients mismatch", "BINDING", field=key)
    need(result["certificate_status"] == "DECLARED_PREMISES_BOUND_TO_EXACT_INPUT;PHYSICAL_VERIFICATION_NOT_INFERRED"
         and result["input_scientific_status"] == "ARITHMETIC_CONTROL_PREMISE"
         and result["R_history"] == "GLOBAL_FROM_ORIGINAL_T0" and result["cap_application"] == "NONE",
         "Saved source/certificate/history scope differs", "SCOPE")
    provenance = result["source_provenance"]
    for key in ("source_locator", "source_sha256", "whole_forcing_source_sha256"):
        need(provenance[key] == binding[key], "Saved provenance mismatch", "BINDING", field=key)
    need(provenance["source_classification"] == "ARITHMETIC_CONTROL_PREMISE", "Physical provenance promotion", "SCOPE")
    arithmetic = result["arithmetic"]
    for key, value in {
        "rational_bits": 16384, "dyadic_bits": 128, "Taylor_degree": 96,
        "subdivision_depth": 96, "derivative_degree_max": 3,
        "runtime_int_max_str_digits": 6000, "output_rational_text_max_characters": 10000,
        "coarse_l1_multiplier": 4,
    }.items():
        need(exact_int(arithmetic[key], "arithmetic/" + key) == value, "Arithmetic contract metadata mismatch", "SCOPE", field=key)
    need(arithmetic["subdivision_points_are_propagation_clocks"] is False,
         "Subdivision clock changed propagation", "SCOPE")
    for key in ("lower_meaning", "whole_meaning"):
        need(type(arithmetic[key]) is str and arithmetic[key], "Missing output-meaning metadata", "SCOPE", field=key)
    return digest


def parse_raw(result, model):
    raw = result["raw"]
    nb, no = model.nbase, len(model.observation) - 1
    return {
        "endpoints_lower": qmatrix(raw["endpoints_lower"], no + 1, "endpoints_lower"),
        "endpoints_upper": qmatrix(raw["endpoints_upper"], no + 1, "endpoints_upper"),
        "whole_cells_lower": qmatrix(raw["whole_cells_lower"], no, "whole_cells_lower"),
        "whole_cells_upper": qmatrix(raw["whole_cells_upper"], no, "whole_cells_upper"),
        "refined_endpoints_lower": qmatrix(raw["refined_endpoints_lower"], nb + 1, "refined_endpoints_lower"),
        "refined_endpoints_upper": qmatrix(raw["refined_endpoints_upper"], nb + 1, "refined_endpoints_upper"),
        "refined_whole_cells_lower": qmatrix(raw["refined_whole_cells_lower"], nb, "refined_whole_cells_lower"),
        "refined_whole_cells_upper": qmatrix(raw["refined_whole_cells_upper"], nb, "refined_whole_cells_upper"),
    }


def verify_work(model, result, verified):
    work = result["work"]
    targets = {
        "original_source_cells": len(model.gr), "base_cells": model.nbase,
        "refined_cells": model.nbase, "full_blocks": model.blocks,
        "overlap_terms_upper": model.overlap_precharge,
        "overlap_terms_actual": model.overlap_precharge,
        "nonempty_overlap_terms": model.nonempty_overlap_count(),
        "subdivision_splits_upper": 3 * 96 * model.nbase,
        "subdivision_nodes_upper": (6 * 96 + 1) * model.nbase,
        "subdivision_splits_actual": sum(v["splits"] for v in verified),
        "subdivision_nodes_actual": sum(v["visits"] for v in verified),
        "coefficient_cell_builds": model.nbase,
        "overlap_limit": 100000, "split_limit": 147456, "node_limit": 295424,
    }
    for key, value in targets.items():
        need(exact_int(work[key], "work/" + key, 0) == value,
             "Work counter/precharge mismatch", "FINITE_WORK", field=key, expected=value)
    need(work["guard_applied_before_overlap"] is True and work["guard_applied_before_subdivision"] is True,
         "Missing pre-loop work guard declaration", "FINITE_WORK")
    need(targets["subdivision_splits_actual"] <= targets["subdivision_splits_upper"] <= 147456
         and targets["subdivision_nodes_actual"] <= targets["subdivision_nodes_upper"] <= 295424,
         "Global work count cap failed", "FINITE_WORK")
    return targets


def verify_depth_sweeps(case_id, fixture_sweeps, primary_checks, cells, arithmetic):
    p = Polynomials(arithmetic)
    alg = Polynomials(arithmetic, algebra=True)
    rows_out = []
    controls = [row for row in fixture_sweeps["controls"] if row["model"] == case_id]
    for control in controls:
        matching = [row for row in primary_checks if row.get("kind") == "DEPTH_SWEEP" and row.get("id") == control["id"]]
        need(len(matching) == 1, "Missing or duplicate depth sweep", "DEPTH_SWEEP", id=control["id"])
        saved = matching[0]
        need(saved["status"] == "PASS", "Primary depth sweep failed", "DEPTH_SWEEP", id=control["id"])
        index = exact_int(control["base_cell_index"], "depth/base_cell_index", 0, len(cells) - 1)
        cell = cells[index]
        need(qlist(control["bernstein"], 5) == cell["bernstein"] == qlist(saved["bernstein"], 5),
             "Depth sweep B4 not bound to own original-integral cell", "DEPTH_SWEEP")
        mb = 4 * max(abs(b - a) for a, b in zip(cell["bernstein"], cell["bernstein"][1:]))
        rows = saved["rows"]
        need(type(rows) is list and [row["depth"] for row in rows] == [0, 4, 8, 16, 32, 64, 96],
             "Depth sweep row set differs", "DEPTH_SWEEP")
        previous_gap = None
        for row in rows:
            depth = exact_int(row["depth"], "depth_sweep/depth", 0, 96)
            lower, upper = saved_rational(row["exact_lower"]), saved_rational(row["exact_upper"])
            gap = upper - lower
            need(saved_rational(row["exact_gap"]) == gap and 0 <= gap <= mb / (1 << depth),
                 "Depth-dependent exact gap failed", "DEPTH_SWEEP", depth=depth)
            need(saved_rational(row["M_B"]) == mb and saved_rational(row["proved_gap_bound"]) == mb / (1 << depth),
                 "Depth-dependent MB/gap metadata differs", "DEPTH_SWEEP", depth=depth)
            need(alg.nonnegative(alg.sub([upper], cell["power"]))
                 and alg.some_nonnegative(alg.sub(cell["power"], [lower])),
                 "Independent depth upper or lower existence failed", "DEPTH_SWEEP", depth=depth)
            splits = exact_int(row["splits_actual"], "depth_sweep/splits", 0, 3 * depth)
            visits = exact_int(row["nodes_visited"], "depth_sweep/visits", 1, 6 * depth + 1)
            need(visits == 2 * splits + 1, "Depth-sweep tree count mismatch", "DEPTH_SWEEP", depth=depth)
            if "expected_supremum" in control:
                expected = input_rational(control["expected_supremum"])
                need(lower <= expected <= upper, "Named rational supremum outside depth enclosure", "DEPTH_SWEEP", depth=depth)
            # The nesting diagnostic is reported, not an uncontracted rejection gate.
            rows_out.append({"id": control["id"], "depth": depth, "exact_lower": lower,
                             "exact_upper": upper, "exact_gap": gap, "M_B": mb,
                             "splits": splits, "visits": visits,
                             "gap_nonincreasing_from_previous": None if previous_gap is None else gap <= previous_gap})
            previous_gap = gap
    return rows_out


def verify_case(fixture, primary_case, source_row, source_sha256, fixture_sweeps, primary_checks, arithmetic, audit, engine):
    case_id = fixture["id"]
    report = {"id": case_id, "status": "RUNNING", "blocked_after_failure": False}
    first_check = len(audit.checks)
    try:
        with audit.phase(case_id, "REF01_SCHEMA_IDENTITY", "EXACT_METADATA"):
            need(primary_case["id"] == case_id and primary_case["status"] == "PASS", "Primary full model failed or mismatched", "PRIMARY_CASE_STATUS")
            model = OriginalModel(fixture["input"], arithmetic)
            result = primary_case["result"]
            raw = parse_raw(result, model)
            saved_cells = result["exact"]["R_quartic_cells"]
            need(type(saved_cells) is list and len(saved_cells) == model.nbase, "Saved quartic cell count mismatch", "SCHEMA")
            need(type(result["weights"]) is list and len(result["weights"]) == model.nbase, "Saved weight count mismatch", "SCHEMA")
            need(len(result["exact"]["observation_R_suprema"]) == len(model.observation) - 1, "Saved observation supremum count mismatch", "SCHEMA")
        with audit.phase(case_id, "REF02_BINDING", "EXACT_METADATA") as details:
            details["whole_forcing_sha256"] = verify_binding(model, fixture, source_row, source_sha256, result)
        with audit.phase(case_id, "REF03_CLOCK_MEMORY") as details:
            need(qlist(result["requested_times"]) == model.observation
                 and qlist(result["base_times"]) == model.base
                 and qlist(result["refined_times"]) == model.base,
                 "Independent source/observation/kernel clock differs", "CLOCK_OR_MEMORY_MISMATCH")
            if "base_times" in fixture["expected"]:
                need([input_rational(v) for v in fixture["expected"]["base_times"]] == model.base, "Frozen base-clock target mismatch", "CLOCK_OR_MEMORY_MISMATCH")
            details.update({"base_cells": model.nbase, "full_blocks": model.blocks, "overlap_precharge": model.overlap_precharge})
        with audit.phase(case_id, "REF04_ORIGINAL_ENDPOINTS") as details:
            F_values = [model.F(t) for t in model.base]
            R_values = [model.R(t) for t in model.base]
            kernel_values = [model.kernel(t) for t in model.base]
            need(qlist(result["exact"]["F_at_refined"], model.nbase + 1) == F_values
                 and qlist(result["exact"]["R_at_refined"], model.nbase + 1) == R_values
                 and qlist(result["exact"]["kernel_at_refined"], model.nbase + 1) == kernel_values,
                 "Original primitive endpoint identity failed", "ORIGINAL_INTEGRAL_ENDPOINT_MISMATCH")
            for i, value in enumerate(R_values):
                need(raw["refined_endpoints_lower"][i][0] == value == raw["refined_endpoints_upper"][i][0],
                     "Raw R endpoint is not exact original integral", "ORIGINAL_INTEGRAL_ENDPOINT_MISMATCH", endpoint=i)
                lo, hi = raw["refined_endpoints_lower"][i][1], raw["refined_endpoints_upper"][i][1]
                need(0 <= lo <= hi, "Endpoint E interval invalid", "SAVED_INTERVAL", endpoint=i)
            need(raw["refined_endpoints_lower"][0][1] <= model.initial[1] <= raw["refined_endpoints_upper"][0][1],
                 "Initial E not enclosed exactly", "SAVED_INTERVAL")
            need(R_values[-1] == input_rational(fixture["expected"]["R_final"])
                 if "R_final" in fixture["expected"] else True, "Frozen exact final R target failed", "EXACT_CONTROL")
            details["endpoint_values_checked"] = len(R_values)
        with audit.phase(case_id, "REF05_QUARTIC_IDENTITY") as details:
            cells = [model.cell(i) for i in range(model.nbase)]
            for i, (cell, saved) in enumerate(zip(cells, saved_cells)):
                need(saved_rational(saved["left"]) == cell["left"] and saved_rational(saved["right"]) == cell["right"], "Cell physical clock mismatch", "QUARTIC_IDENTITY", cell=i)
                power5 = cell["power"] + [Fraction(0)] * (5 - len(cell["power"]))
                need(qlist(saved["coefficients_normalized"], 5) == power5
                     and qlist(saved["bernstein"], 5) == cell["bernstein"]
                     and qlist(saved["F_bernstein"], 5) == model.p.power_to_bernstein(cell["F_power"], 4)
                     and qlist(saved["ge_bernstein"], 4) == cell["ge_bernstein"]
                     and qlist(saved["forcing_bernstein"], 5) == cell["forcing_bernstein"]
                     and saved_rational(saved["initial_piece"]) == cell["initial_piece"],
                     "Saved coefficients differ from original-integral power construction", "QUARTIC_IDENTITY", cell=i)
                need(min(cell["bernstein"]) >= 0 and min(cell["ge_bernstein"]) >= 0 and min(cell["forcing_bernstein"]) >= 0,
                     "Model positive Bernstein cone failed independently", "QUARTIC_POSITIVITY", cell=i)
            details.update({"cells": len(cells), "interior_interpolation_points_per_cell": 5, "off_stencil_points_per_cell": 4})
        with audit.phase(case_id, "REF06_ONE_SIDED"):
            for i, (cell, saved) in enumerate(zip(cells, saved_cells)):
                need(saved_rational(saved["right_left_limit"]) == cell["right_left_limit"]
                     and saved_rational(saved["actual_right_endpoint"]) == cell["actual_right_endpoint"],
                     "Actual right endpoint confused with left limit", "ENDPOINT_LEFT_LIMIT_CONFUSION", cell=i)
                need(model.p.evaluate(cell["power"], Fraction(0)) == R_values[i], "Cell left branch not right-continuous", "ENDPOINT_LEFT_LIMIT_CONFUSION", cell=i)
                need(cell["right_left_limit"] - cell["initial_piece"] == F_values[i + 1], "Convolution left limit not continuous", "ENDPOINT_LEFT_LIMIT_CONFUSION", cell=i)
                need(cell["right_left_limit"] - cell["actual_right_endpoint"]
                     == (model.kernel(cell["left"]) - model.kernel(cell["right"])) * model.initial[0],
                     "Initial kernel jump identity failed", "ENDPOINT_LEFT_LIMIT_CONFUSION", cell=i)
            if "R_final_left_limit" in fixture["expected"]:
                need(cells[-1]["right_left_limit"] == input_rational(fixture["expected"]["R_final_left_limit"]), "Frozen left-limit target failed", "EXACT_CONTROL")
        with audit.phase(case_id, "REF07_PARTITION") as details:
            verified = [verify_partition(cell, saved, arithmetic) for cell, saved in zip(cells, saved_cells)]
            details.update({"cells": len(verified), "terminal_leaves": sum(len(v["leaves"]) for v in verified)})
        with audit.phase(case_id, "REF08_SUPREMUM_EXACT"):
            alg = Polynomials(arithmetic, algebra=True)
            for i, (cell, saved, v) in enumerate(zip(cells, saved_cells, verified)):
                lower = saved_rational(saved["supremum"]["exact_lower"])
                upper = saved_rational(saved["supremum"]["exact_upper"])
                need(lower == v["lower"] and upper == v["upper"] and lower <= upper,
                     "Supremum not equal to independent rational witness/hull maxima", "EXACT_SUPREMUM_ENCLOSURE_FAILURE", cell=i)
                need(alg.nonnegative(alg.sub([upper], cell["power"])) and cell["actual_right_endpoint"] <= upper,
                     "Independent exact U-P nonnegativity failed", "EXACT_SUPREMUM_ENCLOSURE_FAILURE", cell=i)
            if "R_last_cell_sup" in fixture["expected"]:
                target = input_rational(fixture["expected"]["R_last_cell_sup"])
                need(verified[-1]["lower"] <= target <= verified[-1]["upper"], "Named last-cell supremum target outside exact enclosure", "EXACT_CONTROL")
        with audit.phase(case_id, "REF09_GAP_DYADIC"):
            for i, (cell, saved, v) in enumerate(zip(cells, saved_cells, verified)):
                need(v["M_B"] <= 4 * v["Cmax"], "MB positivity bound failed", "SUPREMUM_GAP", cell=i)
                dyadic = check_supremum_record(saved["supremum"], v["lower"], v["upper"], v["M_B"], v["Cmax"], v["gap_bound"])
                need(raw["refined_whole_cells_lower"][i][0] == dyadic[0]
                     and raw["refined_whole_cells_upper"][i][0] == dyadic[1],
                     "Raw whole R does not equal dyadic supremum enclosure", "RAW_MAPPING", cell=i)
            base_index = {time: i for i, time in enumerate(model.base)}
            for j, (left, right) in enumerate(zip(model.observation, model.observation[1:])):
                a, b = base_index[left], base_index[right]
                subset = verified[a:b]
                lower, upper = max(v["lower"] for v in subset), max(v["upper"] for v in subset)
                mb, cmax = max(v["M_B"] for v in subset), max(v["Cmax"] for v in subset)
                gap = max(v["gap_bound"] for v in subset)
                dyadic = check_supremum_record(result["exact"]["observation_R_suprema"][j], lower, upper, mb, cmax, gap)
                need(raw["whole_cells_lower"][j][0] == dyadic[0] and raw["whole_cells_upper"][j][0] == dyadic[1], "Observation whole R aggregation failed", "RAW_MAPPING")
        with audit.phase(case_id, "REF10_WORK", "EXACT_INTEGER") as details:
            work = verify_work(model, result, verified)
            details.update(work)
            for key in ("full_blocks", "overlap_precharge"):
                if key in fixture["expected"]:
                    actual = model.blocks if key == "full_blocks" else model.overlap_precharge
                    need(actual == fixture["expected"][key], "Frozen work boundary target failed", "FINITE_WORK", field=key)
        root_result = None
        if case_id in ROOT_PATTERNS:
            with audit.phase(case_id, "REF11_ROOT_PATTERNS", "EXACT_DIAGNOSTIC"):
                need(fixture["expected"]["derivative_root_pattern"] == ROOT_PATTERNS[case_id][0], "Frozen derivative pattern label mismatch", "ROOT_PATTERN")
                index = next(i for i, cell in enumerate(cells) if cell["left"] == 1 and cell["right"] == 2)
                root_result = root_diagnostic(cells[index], verified[index], case_id, arithmetic)
        exact_E = None
        if model.d == 0:
            with audit.phase(case_id, "REF12_ZERO_D_E"):
                exact_E = [model.initial[1]]
                for cell in cells:
                    increment = arithmetic.guard(cell["duration"] * sum((coefficient / (m + 1) for m, coefficient in enumerate(cell["forcing_power"])), Fraction(0)))
                    exact_E.append(arithmetic.guard(exact_E[-1] + increment))
                for i, value in enumerate(exact_E):
                    need(raw["refined_endpoints_lower"][i][1] <= value <= raw["refined_endpoints_upper"][i][1], "Exact d0 scalar endpoint outside interval", "EXACT_SCALAR_CONTROL_FAILURE", endpoint=i)
                if "E_final" in fixture["expected"]:
                    need(exact_E[-1] == input_rational(fixture["expected"]["E_final"]), "Frozen exact final E target failed", "EXACT_SCALAR_CONTROL_FAILURE")
        parsed_weights = []
        with audit.phase(case_id, "REF13_MOMENTS", "GUARDED_DECIMAL_WITH_STRICT_AUDIT") as details:
            for i, (cell, weight) in enumerate(zip(cells, result["weights"])):
                z = arithmetic.guard(model.d * cell["duration"])
                need(saved_rational(weight["left"]) == cell["left"] and saved_rational(weight["right"]) == cell["right"]
                     and saved_rational(weight["z"]) == z, "Weight clock/z differs", "MOMENT_RECORD", cell=i)
                exponential, phis = engine.functions(z)
                moment_values = engine.weights(cell["duration"], phis)
                parsed = {key: qlist(weight[key], 2, "weights/" + key) for key in ("exp", "phi", "W0", "W1", "W2", "W3", "W4")}
                reference_values = {"exp": exponential, "phi": engine.decimal(cell["duration"]) * phis[0]}
                reference_values.update({"W" + str(j): value for j, value in enumerate(moment_values)})
                for key, value in reference_values.items():
                    lo, hi = parsed[key]
                    need(0 <= lo <= hi, "Positive moment interval invalid", "MOMENT_RECORD", cell=i, field=key)
                    audit.contains(value, lo, hi, case_id, "cell/" + str(i) + "/" + key)
                    if z == 0:
                        exact = Fraction(1) if key == "exp" else cell["duration"] if key == "phi" else cell["duration"] / 5
                        need(lo <= exact <= hi, "Exact zero-z moment outside interval", "EXACT_MOMENT_CONTROL", cell=i, field=key)
                parsed_weights.append({"intervals": parsed, "exp": exponential, "phis": phis, "z": z})
            details.update({"weight_rows": len(parsed_weights), "Decimal_precision": 160, "phi_terms": 512})
        with audit.phase(case_id, "REF14_SCALAR_ENDPOINTS", "GUARDED_DECIMAL_WITH_STRICT_AUDIT"):
            decimal_E = [engine.decimal(model.initial[1])]
            for i, (cell, weight) in enumerate(zip(cells, parsed_weights)):
                value = weight["exp"] * decimal_E[-1] + engine.integral(cell["forcing_power"], cell["duration"], weight["phis"])
                decimal_E.append(+value)
                intervals = weight["intervals"]
                formula_lower = raw["refined_endpoints_lower"][i][1] * intervals["exp"][0]
                formula_upper = raw["refined_endpoints_upper"][i][1] * intervals["exp"][1]
                for j, coefficient in enumerate(cell["forcing_bernstein"]):
                    formula_lower += coefficient * intervals["W" + str(j)][0]
                    formula_upper += coefficient * intervals["W" + str(j)][1]
                need(raw["refined_endpoints_lower"][i + 1][1] <= formula_lower
                     and raw["refined_endpoints_upper"][i + 1][1] >= formula_upper,
                     "Endpoint propagation has wrong outward direction for polynomial forcing", "SCALAR_PROPAGATION", cell=i)
            for i, value in enumerate(decimal_E):
                audit.contains(value, raw["refined_endpoints_lower"][i][1], raw["refined_endpoints_upper"][i][1], case_id, "endpoint/" + str(i) + "/E")
            for j, time in enumerate(model.observation):
                i = base_index[time]
                need(raw["endpoints_lower"][j] == raw["refined_endpoints_lower"][i]
                     and raw["endpoints_upper"][j] == raw["refined_endpoints_upper"][i],
                     "Requested endpoint is not the base-clock endpoint", "RAW_MAPPING", observation=j)
                audit.contains(decimal_E[i], raw["endpoints_lower"][j][1], raw["endpoints_upper"][j][1], case_id, "observation_endpoint/" + str(j) + "/E")
            if case_id in ("SIGNED_DOMAIN_POS16", "SIGNED_DOMAIN_NEG16"):
                sign = 16 if case_id == "SIGNED_DOMAIN_POS16" else -16
                exponential = Decimal(sign).exp()
                expected = exponential + (exponential - 1) / Decimal(sign)
                # This is a second frozen symbolic control, still guarded Decimal evidence.
                audit.contains(expected, raw["refined_endpoints_lower"][-1][1], raw["refined_endpoints_upper"][-1][1], case_id, "signed_domain_symbolic_control")
        with audit.phase(case_id, "REF15_WHOLE_E", "EXACT_STRUCTURE_PLUS_GUARDED_DECIMAL"):
            for i, (cell, saved, v, weight) in enumerate(zip(cells, saved_cells, verified, parsed_weights)):
                majorant = saved["whole_E_majorant"]
                qmax = arithmetic.guard(model.c * v["upper"] + max(cell["ge_bernstein"]))
                left_upper = raw["refined_endpoints_upper"][i][1]
                right_upper = saved_rational(majorant["right_majorant_upper"])
                need(saved_rational(majorant["Qmax"]) == qmax and saved_rational(majorant["left_E_upper"]) == left_upper,
                     "Whole E majorant input differs", "WHOLE_SCALAR_CERTIFICATE_FAILURE", cell=i)
                need(alg.nonnegative(alg.sub([qmax], cell["forcing_power"])), "Qmax not above original forcing", "WHOLE_SCALAR_CERTIFICATE_FAILURE", cell=i)
                interval_upper = left_upper * weight["intervals"]["exp"][1] + qmax * weight["intervals"]["phi"][1]
                need(right_upper >= interval_upper, "Majorant endpoint rounding is inward", "WHOLE_SCALAR_CERTIFICATE_FAILURE", cell=i)
                right_ref = weight["exp"] * engine.decimal(left_upper) + engine.decimal(cell["duration"]) * weight["phis"][0] * engine.decimal(qmax)
                # No lower enclosure for the majorant is supplied; positivity supplies zero.
                audit.contains(right_ref, Fraction(0), right_upper, case_id, "cell/" + str(i) + "/whole_E_majorant")
                whole_lower = max(raw["refined_endpoints_lower"][i][1], raw["refined_endpoints_lower"][i + 1][1])
                whole_upper = max(left_upper, raw["refined_endpoints_upper"][i + 1][1], right_upper)
                need(raw["refined_whole_cells_lower"][i][1] == whole_lower
                     and raw["refined_whole_cells_upper"][i][1] == whole_upper,
                     "Whole E supremum bounds not assembled from declared endpoints/majorant", "WHOLE_SCALAR_CERTIFICATE_FAILURE", cell=i)
                if exact_E is not None:
                    need(whole_lower <= exact_E[i + 1] <= whole_upper, "Exact nondecreasing d0 whole E not enclosed", "EXACT_SCALAR_CONTROL_FAILURE", cell=i)
            for j, (left, right) in enumerate(zip(model.observation, model.observation[1:])):
                a, b = base_index[left], base_index[right]
                for coordinate in range(2):
                    need(raw["whole_cells_lower"][j][coordinate] == max(row[coordinate] for row in raw["refined_whole_cells_lower"][a:b])
                         and raw["whole_cells_upper"][j][coordinate] == max(row[coordinate] for row in raw["refined_whole_cells_upper"][a:b]),
                         "Observation whole-cell maxima not aggregated", "RAW_MAPPING", observation=j, coordinate=coordinate)
        depth_results = []
        if any(row["model"] == case_id for row in fixture_sweeps["controls"]):
            with audit.phase(case_id, "REF18_DEPTH_SWEEP", "EXACT_DIAGNOSTIC"):
                depth_results = verify_depth_sweeps(case_id, fixture_sweeps, primary_checks, cells, arithmetic)
        report.update({
            "status": "PASS", "base_times": model.base, "requested_times": model.observation,
            "original_R_endpoints": R_values, "original_F_endpoints": F_values,
            "exact_d0_E_endpoints": exact_E, "Decimal_E_endpoints": decimal_E,
            "reference_cells": [{"left": cell["left"], "right": cell["right"], "power_normalized": cell["power"],
                                 "actual_right_endpoint": cell["actual_right_endpoint"], "right_left_limit": cell["right_left_limit"],
                                 "exact_supremum_lower": v["lower"], "exact_supremum_upper": v["upper"],
                                 "lower_right_witness_kind": "LEFT_LIMIT", "M_B": v["M_B"], "gap_bound": v["gap_bound"]}
                                for cell, v in zip(cells, verified)],
            "root_diagnostic": root_result, "depth_sweeps": depth_results,
            "work": work, "scientific_status": "ARITHMETIC_CONTROL_PREMISE",
        })
    except ReferenceFailure as exc:
        report.update({"status": "FAIL", "error": exc.record(), "blocked_after_failure": True})
    except Exception as exc:
        report.update({"status": "FAIL", "error": {"category": "REFERENCE_IMPLEMENTATION_EXCEPTION", "message": str(exc), "exception_type": type(exc).__name__}, "blocked_after_failure": True})
    report["semantic_check_records"] = len(audit.checks) - first_check
    report["strict_Decimal_misses_observed_before_any_failure"] = audit.strict_by_case.get(case_id, 0)
    return report


def index_unique(records, label):
    need(type(records) is list, "Expected indexed record list", "SCHEMA", field=label)
    indexed = {}
    for row in records:
        need(type(row) is dict and type(row.get("id")) is str and row["id"] not in indexed,
             "Missing/duplicate record ID", "SCHEMA", field=label)
        indexed[row["id"]] = row
    return indexed


def verify_primary_records(primary, audit):
    with audit.phase("__campaign__", "REF16_PRIMARY_GUARD_RECORDS", "METADATA_ONLY_NOT_INDEPENDENT_REEXECUTION") as details:
        guards = primary["guard_cases"]
        index_unique(guards, "guard_cases")
        for row in guards:
            need(row["status"] == "PASS" and row["exception_type"] == "DomainError"
                 and type(row["message"]) is str and row["message"],
                 "Primary rejection guard failed or omitted evidence", "PRIMARY_GUARD_RECORD", id=row["id"])
        checks = primary["checks"]
        need(type(checks) is list and all(type(row) is dict and row.get("status") in ("PASS", "FAIL") for row in checks),
             "Primary semantic check records malformed", "PRIMARY_STATUS")
        passed = sum(row["status"] == "PASS" for row in checks)
        failed = sum(row["status"] == "FAIL" for row in checks)
        summary = primary["summary"]
        for key, value in {
            "valid_cases": len(primary["valid_cases"]), "extrema_controls": len(primary["extrema_controls"]),
            "rejection_guards": len(guards), "checks": len(checks), "passed": passed, "failed": failed,
        }.items():
            need(exact_int(summary[key], "primary_summary/" + key, 0) == value,
                 "Primary summary does not equal retained records", "PRIMARY_STATUS", field=key)
        need(primary["status"] == "PASS_SCOPED" and failed == 0, "Primary campaign did not pass", "PRIMARY_STATUS")
        details.update({"guard_records": len(guards), "primary_check_records": len(checks),
                        "independent_guard_reexecution": False, "claim": "Saved rejection records inspected only"})


def run_reference_campaign(fixtures, primary, source, source_sha256, progress=None):
    arithmetic, audit, engine = Arithmetic(), Audit(), DecimalReference()
    reports = []
    campaign_errors = []
    try:
        with audit.phase("__campaign__", "REF01_SCHEMA_IDENTITY", "EXACT_METADATA"):
            need(fixtures["schema"] == "WU_R15_FIXED_CASES_V1"
                 and primary["schema"] == "WU_R15_PRIMARY_RESULTS_V1"
                 and source["schema"] == "WU_R15_ARITHMETIC_SOURCE_V1",
                 "Frozen source/result schema mismatch", "SCHEMA")
            fixture_index = index_unique(fixtures["cases"], "fixtures")
            primary_index = index_unique(primary["valid_cases"], "primary valid_cases")
            source_index = index_unique(source["models"], "source models")
            need(set(fixture_index) == set(primary_index) == set(source_index) == set(CASE_IDS),
                 "Full fixed case set is missing or changed", "FROZEN_CASE_SET")
            need(fixtures["extrema_cases"] == [] and primary["extrema_controls"] == [],
                 "Unplanned standalone extrema fixture", "FROZEN_CASE_SET")
            need(source["classification"] == "ARITHMETIC_CONTROL_PREMISE", "Source classification changed", "SCOPE")
            sweeps = fixtures["depth_sweep"]
            need(sweeps == source["depth_sweep"] and sweeps["depths"] == [0, 4, 8, 16, 32, 64, 96],
                 "Frozen depth plan differs", "FROZEN_CASE_SET")
            need([(row["id"], row["model"], row["base_cell_index"]) for row in sweeps["controls"]]
                 == [("DEPTH_SWEEP_RATIONAL", "ROOT_THREE_RATIONAL", 1),
                     ("DEPTH_SWEEP_ALGEBRAIC", "ROOT_THREE_MIXED_ALGEBRAIC", 1)],
                 "Depth sweep identity changed", "FROZEN_CASE_SET")
            need(sweeps["combined_precharge"] == {"splits_max": 1320, "visits_max": 2654},
                 "Depth sweep precharge changed", "FROZEN_CASE_SET")
            depth_records = [row for row in primary["checks"] if row.get("kind") == "DEPTH_SWEEP"]
            need(len(depth_records) == 2 and {row["id"] for row in depth_records} == {"DEPTH_SWEEP_RATIONAL", "DEPTH_SWEEP_ALGEBRAIC"},
                 "Missing/extra primary depth-sweep records", "FROZEN_CASE_SET")
        with localcontext() as context:
            context.prec = DECIMAL_PRECISION
            context.rounding = ROUND_HALF_EVEN
            for index, case_id in enumerate(CASE_IDS):
                report = verify_case(fixture_index[case_id], primary_index[case_id], source_index[case_id],
                                     source_sha256, sweeps, primary["checks"], arithmetic, audit, engine)
                reports.append(report)
                if progress is not None:
                    progress({"case": case_id, "completed": index + 1, "total": len(CASE_IDS), "status": report["status"]})
        try:
            verify_primary_records(primary, audit)
        except ReferenceFailure as exc:
            campaign_errors.append(exc.record())
        with audit.phase("__campaign__", "REF17_RESOURCE_AND_SCOPE", "EXACT_METADATA") as details:
            passed_reports = [row for row in reports if row["status"] == "PASS"]
            if len(passed_reports) == len(CASE_IDS):
                need(sum(row["work"]["base_cells"] for row in reports) == 75
                     and sum(row["work"]["overlap_terms_upper"] for row in reports) == 4811
                     and sum(len(row["depth_sweeps"]) for row in reports) == 14,
                     "Fixed campaign actual count differs from predeclared design", "FROZEN_CASE_SET")
            need(arithmetic.stats["root_splits"] <= 6720 and arithmetic.stats["root_visits"] <= 13447,
                 "Root diagnostic total work exceeds cap", "REFERENCE_POLYNOMIAL_CAP")
            details.update({"production_imports": 0, "fixed_case_count": len(CASE_IDS),
                            "physical_promotion": False, "CPU_wall_memory_measured_by": "ROOT_BOUNDED_WRAPPER"})
    except ReferenceFailure as exc:
        campaign_errors.append(exc.record())
    except Exception as exc:
        campaign_errors.append({"category": "REFERENCE_IMPLEMENTATION_EXCEPTION", "message": str(exc), "exception_type": type(exc).__name__})
    seen = {row["id"] for row in reports}
    for case_id in CASE_IDS:
        if case_id not in seen:
            reports.append({"id": case_id, "status": "FAIL", "blocked_after_failure": True,
                            "error": {"category": "BLOCKED_BY_CAMPAIGN_INPUT_FAILURE", "message": "Declared case retained; prerequisites failed"}})
    failed_cases = sum(row["status"] != "PASS" for row in reports)
    failed_checks = sum(row["status"] != "PASS" for row in audit.checks)
    ok = failed_cases == 0 and failed_checks == 0 and not campaign_errors and audit.guarded_failures == 0
    return {
        "schema": "WU_R15_REFERENCE_RESULTS_V1", "unit": "WU_CUBIC_BERNSTEIN_FORCING_R15",
        "status": "PASS_SCOPED" if ok else "FAIL",
        "classification": "EXACT_COMPONENTS_AND_GUARDED_CORROBORATION_NOT_INTERVAL_REFERENCE",
        "summary": {"valid_cases": len(reports), "cases_passed": len(reports) - failed_cases,
                    "cases_failed": failed_cases, "semantic_check_records": len(audit.checks),
                    "checks_passed": len(audit.checks) - failed_checks, "checks_failed": failed_checks,
                    "exact_check_records": sum(row["kind"] in ("EXACT", "EXACT_INTEGER", "EXACT_DIAGNOSTIC", "EXACT_METADATA") for row in audit.checks),
                    "mixed_exact_guarded_check_records": sum(row["kind"] == "EXACT_STRUCTURE_PLUS_GUARDED_DECIMAL" for row in audit.checks),
                    "guarded_comparisons": audit.guarded_comparisons, "guarded_failures": audit.guarded_failures,
                    "strict_Decimal_misses": audit.strict_misses, "strict_examples_retained": len(audit.strict_examples)},
        "valid_cases": reports, "checks": audit.checks, "campaign_errors": campaign_errors,
        "strict_Decimal_miss_examples": audit.strict_examples, "strict_Decimal_misses_by_case": audit.strict_by_case,
        "arithmetic": {"input_bits": INPUT_BITS, "saved_derived_bits": DERIVED_BITS,
                       "saved_derived_text_max_characters": DERIVED_CHARS,
                       "reference_unpersisted_squarefree_Sturm_bits": ALGEBRA_BITS,
                       "Decimal_precision": DECIMAL_PRECISION, "phi_terms": PHI_TERMS,
                       "guard": "1e-80*max(1,abs(reference),abs(lower),abs(upper))",
                       "strict_membership": "Exact Fraction(Decimal) versus exact saved rational bounds",
                       "observed": arithmetic.stats},
        "independence": {"production_implementation_read": False, "production_imports": 0,
                         "original_integral": "Unsplit source power J0..J3 on moving overlaps",
                         "supremum": "Own power polynomial and squarefree odd-factor Sturm nonnegativity",
                         "root_diagnostic": "Seven fixed model cells; count-preserving depth320 clusters allowed",
                         "scalar": "Normalized-u power forcing; Delta*m!*phi_(m+1); fixed Decimal160"},
        "physical_status": {"actual_HD": "INPUT_PENDING_IN_INSPECTED_SCOPE", "named_consumer_state_density_clock": "INPUT_PENDING",
                            "native_v": "UNSPECIFIED", "missingness": "MISSING_NOT_ZERO", "TIQM_SQM": "DISTINCT",
                            "HH_R10": "OFF", "production": "NOT_ISSUED", "L4": False, "central_delta": 0, "physical_delta": 0},
    }
