"""Rational enclosures for continuous CM angular measures and paired apertures.

All set identities are modulo zero-measure endpoints. Fixed stored gamma/a are
exact rationals, including an explicitly supplied finite float's stored value.
This does not certify a mass-to-parameter conversion or physical uncertainties.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import comb, isfinite


class ContractError(ValueError):
    """Input is outside this finite conditional mathematical contract."""


class UnsupportedMeasureError(ContractError):
    """Atomic measures, including kappa=0, need a separate measure API."""


class StoppedDirectionError(ContractError):
    """The stopped daughter has no direction."""


def rational(value, name="value"):
    """Read int, Fraction, rational/decimal string, or exact stored finite float."""
    if isinstance(value, bool):
        raise ContractError(f"{name}: bool is not a rational scalar")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        if not isfinite(value):
            raise ContractError(f"{name}: finite stored float required")
        return Fraction.from_float(value)
    if isinstance(value, str):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise ContractError(f"{name}: finite rational string required") from exc
    raise ContractError(f"{name}: expected int, str, Fraction, or finite float")


def cosine(value, name="cosine"):
    value = rational(value, name)
    if not -1 <= value <= 1:
        raise ContractError(f"{name} must lie in [-1,1]; no clipping")
    return value


def checked_delta(value):
    value = rational(value, "delta")
    if not Fraction(1, 2**80) <= value <= 1:
        raise ContractError("delta must lie in [2^-80,1]")
    return value


def lab_window(window):
    try:
        if len(window) != 2:
            raise ContractError("lab window needs two cosine endpoints")
        low, high = cosine(window[0], "nu0"), cosine(window[1], "nu1")
    except TypeError as exc:
        raise ContractError("lab window needs two cosine endpoints") from exc
    if low > high:
        raise ContractError("lab window endpoints are reversed")
    return low, high


def sign(value):
    return (value > 0) - (value < 0)


def require_continuous(measure_kind="CONTINUOUS", kappa=None):
    if measure_kind != "CONTINUOUS":
        raise UnsupportedMeasureError("only continuous CM measures are supported")
    if kappa is not None:
        kappa = rational(kappa, "kappa")
        if kappa == 0:
            raise UnsupportedMeasureError("kappa=0 threshold atom is unsupported")
        if kappa < 0:
            raise ContractError("kappa cannot be negative")


def normalize(intervals):
    """Canonical union of CM intervals; drop singletons and merge contacts."""
    pieces = []
    try:
        for pair in intervals:
            if len(pair) != 2:
                raise ContractError("each interval needs two endpoints")
            lo, hi = cosine(pair[0], "lower endpoint"), cosine(pair[1], "upper endpoint")
            if lo > hi:
                raise ContractError("interval endpoints are reversed")
            if lo < hi:
                pieces.append((lo, hi))
    except TypeError as exc:
        raise ContractError("interval collection required") from exc
    result = []
    for lo, hi in sorted(pieces):
        if result and lo <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], hi))
        else:
            result.append((lo, hi))
    return tuple(result)


FULL = ((Fraction(-1), Fraction(1)),)


def union(*sets):
    return normalize(interval for intervals in sets for interval in intervals)


def intersection(left, right):
    left, right = normalize(left), normalize(right)
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        lo, hi = max(left[i][0], right[j][0]), min(left[i][1], right[j][1])
        if lo < hi:
            result.append((lo, hi))
        if left[i][1] < right[j][1]:
            i += 1
        else:
            j += 1
    return tuple(result)


def reflection(intervals):
    return normalize((-hi, -lo) for lo, hi in normalize(intervals))


def difference(left, right):
    left, right = normalize(left), normalize(right)
    result = []
    for lo, hi in left:
        cursor = lo
        for cut_lo, cut_hi in right:
            if cut_hi <= cursor:
                continue
            if cut_lo >= hi:
                break
            if cursor < cut_lo:
                result.append((cursor, min(hi, cut_lo)))
            cursor = max(cursor, cut_hi)
            if cursor >= hi:
                break
        if cursor < hi:
            result.append((cursor, hi))
    return normalize(result)


def length(intervals):
    return sum((hi - lo for lo, hi in normalize(intervals)), Fraction(0))


@dataclass(frozen=True)
class SetBounds:
    inner: tuple
    outer: tuple

    def __post_init__(self):
        inner, outer = normalize(self.inner), normalize(self.outer)
        if difference(inner, outer):
            raise ContractError("inner set is not contained in outer set")
        object.__setattr__(self, "inner", inner)
        object.__setattr__(self, "outer", outer)

    @property
    def uncertain(self):
        return difference(self.outer, self.inner)

    def reflected(self):
        return SetBounds(reflection(self.inner), reflection(self.outer))

    def union(self, other):
        return SetBounds(union(self.inner, other.inner), union(self.outer, other.outer))

    def intersection(self, other):
        return SetBounds(intersection(self.inner, other.inner), intersection(self.outer, other.outer))

    def difference(self, other):
        return SetBounds(difference(self.inner, other.outer), difference(self.outer, other.inner))


@dataclass(frozen=True)
class Preimage:
    sets: SetBounds
    delta: Fraction
    root_brackets: tuple

    @property
    def uncertainty_length(self):
        return length(self.sets.uncertain)


class AngularMap:
    """Fixed stored rational map, 1<=gamma<=1e6 and 0<=a<=1e6."""

    def __init__(self, gamma, a, *, measure_kind="CONTINUOUS", kappa=None):
        require_continuous(measure_kind, kappa)
        self.gamma, self.a = rational(gamma, "gamma"), rational(a, "a")
        if not 1 <= self.gamma <= 10**6 or not 0 <= self.a <= 10**6:
            raise ContractError("require 1<=gamma<=1e6 and 0<=a<=1e6")

    def compare(self, mu, nu):
        """Exact sign of F(mu)-nu, without a square root or spurious sign root."""
        return self._compare(mu, nu, auxiliary_stopped_limit=False)

    def _compare(self, mu, nu, *, auxiliary_stopped_limit):
        mu, nu = cosine(mu, "mu"), cosine(nu, "nu")
        x = self.gamma * (mu + self.a)
        d2 = 1 - mu * mu + x * x
        if d2 == 0:
            if auxiliary_stopped_limit:
                return -sign(nu)  # auxiliary continuous extension F(-1)=0
            raise StoppedDirectionError("a=1,mu=-1 is stopped; no physical direction")
        sx, sn = sign(x), sign(nu)
        if sx != sn:
            return sign(sx - sn)
        if sx == 0:
            return 0
        return sx * sign(x * x - nu * nu * d2)

    def _bracket(self, nu, lo, hi, increasing, delta):
        orientation = 1 if increasing else -1
        def predicate(mu):
            return orientation * self._compare(mu, nu, auxiliary_stopped_limit=True)
        if predicate(lo) >= 0:
            return lo, lo
        if predicate(hi) <= 0:
            return hi, hi
        while hi - lo > delta:
            mid = (lo + hi) / 2
            value = predicate(mid)
            if value == 0:
                return mid, mid
            if value < 0:
                lo = mid
            else:
                hi = mid
        return lo, hi

    def preimage(self, window, delta):
        """Inner/outer rational CM intervals for a closed annular lab window."""
        low, high = lab_window(window)
        delta = checked_delta(delta)
        if low == high:
            return Preimage(SetBounds((), ()), delta, ())
        branches = [(Fraction(-1), Fraction(1), True)]
        if self.a > 1:
            fold = -1 / self.a
            branches = [(Fraction(-1), fold, False), (fold, Fraction(1), True)]
        inner, outer, brackets = [], [], []
        for lo, hi, increasing in branches:
            left_target, right_target = (low, high) if increasing else (high, low)
            l0, u0 = self._bracket(left_target, lo, hi, increasing, delta)
            l1, u1 = self._bracket(right_target, lo, hi, increasing, delta)
            brackets.extend(((l0, u0), (l1, u1)))
            if u0 < l1:
                inner.append((u0, l1))
            if l0 < u1:
                outer.append((l0, u1))
        result = Preimage(SetBounds(tuple(inner), tuple(outer)), delta, tuple(brackets))
        return result


@dataclass(frozen=True)
class IntegralBounds:
    lower: Fraction
    upper: Fraction
    uncertainty_length: Fraction
    width_bound: Fraction

    def __post_init__(self):
        if self.lower > self.upper or self.width > self.width_bound:
            raise ContractError("invalid integral enclosure or width bound")

    @property
    def width(self):
        return self.upper - self.lower

    def scaled(self, factor):
        factor = rational(factor, "scale")
        lo, hi = factor * self.lower, factor * self.upper
        return IntegralBounds(min(lo, hi), max(lo, hi), self.uncertainty_length,
                              abs(factor) * self.width_bound)

    def added(self, other):
        return IntegralBounds(self.lower + other.lower, self.upper + other.upper,
                              self.uncertainty_length + other.uncertainty_length,
                              self.width_bound + other.width_bound)


class BernsteinDensity:
    """Positive Bernstein polynomial, degree<=8; event APIs require evenness."""

    def __init__(self, coefficients):
        if isinstance(coefficients, (str, bytes)):
            raise ContractError("coefficient sequence required, not one string")
        try:
            self.coefficients = tuple(rational(x, "Bernstein coefficient") for x in coefficients)
        except TypeError as exc:
            raise ContractError("coefficient sequence required") from exc
        if not 1 <= len(self.coefficients) <= 9 or any(x < 0 for x in self.coefficients):
            raise ContractError("need 1..9 nonnegative Bernstein coefficients")
        self.degree = n = len(self.coefficients) - 1
        self.maximum = max(self.coefficients)
        self.sigma = 2 * sum(self.coefficients, Fraction(0)) / (n + 1)
        self.symmetric = self.coefficients == self.coefficients[::-1]
        power = [Fraction(0)] * (n + 1)
        for k, coefficient in enumerate(self.coefficients):
            factor = coefficient * comb(n, k) / 2**n
            for i in range(k + 1):
                for j in range(n - k + 1):
                    power[i + j] += factor * comb(k, i) * comb(n - k, j) * (-1)**j
        self.power = tuple(power)

    def value(self, mu):
        mu = cosine(mu, "mu")
        result = Fraction(0)
        for coefficient in reversed(self.power):
            result = result * mu + coefficient
        return result

    def integral(self, intervals=FULL, w0=1, w1=0):
        w0, w1 = rational(w0, "w0"), rational(w1, "w1")
        weighted = [Fraction(0)] * (len(self.power) + 1)
        for k, coefficient in enumerate(self.power):
            weighted[k] += w0 * coefficient
            weighted[k + 1] += w1 * coefficient
        def primitive(mu):
            result = Fraction(0)
            for k in reversed(range(len(weighted))):
                result = result * mu + weighted[k] / (k + 1)
            return result * mu
        return sum((primitive(hi) - primitive(lo) for lo, hi in normalize(intervals)), Fraction(0))

    def default_delta(self):
        if self.maximum == 0:
            return Fraction(1)
        return self.sigma / (16 * self.maximum * 2**40)

    def bounds(self, sets, w0=1, w1=0):
        if not isinstance(sets, SetBounds):
            raise ContractError("SetBounds required")
        w0, w1 = rational(w0, "w0"), rational(w1, "w1")
        uncertain = sets.uncertain
        positive, negative = [], []
        root = -w0 / w1 if w1 else None
        for lo, hi in uncertain:
            cuts = [lo, hi]
            if root is not None and lo < root < hi:
                cuts = [lo, root, hi]
            for left, right in zip(cuts, cuts[1:]):
                midpoint = (left + right) / 2
                value = w0 + w1 * midpoint
                if value > 0:
                    positive.append((left, right))
                elif value < 0:
                    negative.append((left, right))
        core = self.integral(sets.inner, w0, w1)
        lower = core + self.integral(negative, w0, w1)
        upper = core + self.integral(positive, w0, w1)
        uncertain_length = length(uncertain)
        bound = self.maximum * max(abs(w0 - w1), abs(w0 + w1)) * uncertain_length
        return IntegralBounds(lower, upper, uncertain_length, bound)


def aperture_integral(angular_map, density, window, *, delta=None, w0=1, w1=0):
    """Asymmetric positive densities are allowed for a one-daughter integral."""
    if not isinstance(angular_map, AngularMap) or not isinstance(density, BernsteinDensity):
        raise ContractError("AngularMap and BernsteinDensity required")
    window = lab_window(window)
    delta = checked_delta(density.default_delta() if delta is None else delta)
    w0, w1 = rational(w0, "w0"), rational(w1, "w1")
    if density.maximum == 0:
        return {"preimage": None, "integral": IntegralBounds(Fraction(0), Fraction(0),
                Fraction(0), Fraction(0)), "zero_density_short_circuit": True}
    preimage = angular_map.preimage(window, delta)
    return {"preimage": preimage, "integral": density.bounds(preimage.sets, w0, w1)}


def pair_response(angular_map, density, window_a, window_b, *, delta=None,
                  energy0=1, energy1=0):
    """One shared CM event mu; paired directions use F(mu), F(-mu).

    Windows accept the whole azimuth. Positive-width overlap is rejected;
    endpoint contact is immaterial for this continuous measure. Energy inputs
    are declared MeV linear weights, with no heating or empirical-rate binding.
    """
    if not isinstance(angular_map, AngularMap):
        raise ContractError("AngularMap required")
    if not isinstance(density, BernsteinDensity) or not density.symmetric:
        raise ContractError("paired event API requires an even Bernstein density")
    window_a, window_b = lab_window(window_a), lab_window(window_b)
    wa, wb = normalize((window_a,)), normalize((window_b,))
    if intersection(wa, wb):
        raise ContractError("paired detector windows must not overlap with positive width")
    energy0, energy1 = rational(energy0, "E0 [MeV]"), rational(energy1, "E1 [MeV]")
    delta = checked_delta(density.default_delta() if delta is None else delta)
    if density.maximum == 0:
        zero = IntegralBounds(Fraction(0), Fraction(0), Fraction(0), Fraction(0))
        return {"delta": delta, "window_a": window_a, "window_b": window_b,
                "preimage_a": None, "preimage_b": None, "coincidence_sets": None,
                "hit_a_sets": None, "hit_b_sets": None,
                "coincidence": zero, "hit_a": zero, "hit_b": zero,
                "inclusive_a": zero, "inclusive_b": zero,
                "coincidence_daughters": zero, "pair_energy_MeV": zero,
                "selected_plus_energy_MeV": zero, "selected_minus_energy_MeV": zero,
                "zero_density_short_circuit": True}
    pa = angular_map.preimage(window_a, delta)
    pb = angular_map.preimage(window_b, delta)
    a, b = pa.sets, pb.sets
    ra, rb = a.reflected(), b.reflected()
    cab, cba = a.intersection(rb), b.intersection(ra)
    coincidence = cab.union(cba)
    hit_a, hit_b = a.union(ra), b.union(rb)
    y = density.bounds(coincidence)
    return {
        "delta": rational(delta), "window_a": tuple(map(cosine, window_a)),
        "window_b": tuple(map(cosine, window_b)),
        "preimage_a": pa, "preimage_b": pb,
        "coincidence_sets": coincidence,
        "hit_a_sets": hit_a, "hit_b_sets": hit_b,
        "coincidence": y,
        "hit_a": density.bounds(hit_a), "hit_b": density.bounds(hit_b),
        "inclusive_a": density.bounds(a).added(density.bounds(ra)),
        "inclusive_b": density.bounds(b).added(density.bounds(rb)),
        "coincidence_daughters": y.scaled(2),
        "pair_energy_MeV": y.scaled(2 * energy0),
        "selected_plus_energy_MeV": density.bounds(coincidence, energy0, energy1),
        "selected_minus_energy_MeV": density.bounds(coincidence, energy0, -energy1),
    }
