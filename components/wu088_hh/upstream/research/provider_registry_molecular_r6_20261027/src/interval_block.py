"""Exact outward intervals and finite-block certificates for WU R6.

Column-vector convention. The certificate is conditional on the declared
generator family, coefficient bounds and physical/source identities. Missing
source channels are not inferred to have zero physical rate. No computation
is launched by importing this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import importlib.util
from pathlib import Path
import re
import sys

VERSION = "1.0.0"
MAX_N = 9
MAX_N_TERMS = 512
MIN_BITS = 128
MAX_BITS = 768
MAX_MU = 256
MAX_LITERAL_CHARACTERS = 100000
SOURCE_SHA256 = "0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb"
PARSER_SHA256 = "ef10b34e1891755334083340b84ff1e298151df720c13f008b3762505813e275"
H_PLANCK = Fraction(662607015, 10**42)
C_LIGHT = Fraction(299792458)
K_BOLTZMANN = Fraction(1380649, 10**29)
RATE_SCALE_CM3_S = Fraction(1, 10**11)


class DomainError(ValueError):
    """The supplied input is outside the finite certificate contract."""


def _int_text(s: str) -> int:
    """Parse decimal chunks without Python's global decimal-digit setting."""
    if not re.fullmatch(r"[+-]?\d+", s):
        raise DomainError("Expected a canonical integer numerator or denominator")
    sign = -1 if s.startswith("-") else 1
    t = s.lstrip("+-")
    answer = 0
    for start in range(0, len(t), 9):
        part = t[start:start + 9]
        answer = answer * 10**len(part) + int(part)
    return sign * answer


def _text_int(n: int) -> str:
    if n == 0:
        return "0"
    negative, n = n < 0, abs(n)
    chunks = []
    while n:
        n, remainder = divmod(n, 10**9)
        chunks.append(remainder)
    result = str(chunks[-1]) + "".join(f"{x:09d}" for x in reversed(chunks[:-1]))
    return "-" + result if negative else result


def Q(value) -> Fraction:
    """Accept exact integers, Fraction or decimal/fraction text; reject floats."""
    if isinstance(value, bool) or isinstance(value, float):
        raise DomainError("Boolean and binary floating-point certified inputs are rejected")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str):
        raise DomainError("Use an exact integer, Fraction or rational string")
    value = value.strip()
    if not value or len(value) > MAX_LITERAL_CHARACTERS:
        raise DomainError("Empty or excessively large rational literal")
    if "/" in value:
        parts = value.split("/")
        if len(parts) != 2:
            raise DomainError("Expected one rational division bar")
        denominator = _int_text(parts[1])
        if denominator == 0:
            raise DomainError("Zero rational denominator")
        return Fraction(_int_text(parts[0]), denominator)
    match = re.fullmatch(r"([+-]?)(?:(\d+)(?:\.(\d*))?|\.(\d+))(?:[eE]([+-]?\d+))?", value)
    if match is None:
        raise DomainError("Invalid exact decimal literal")
    sign, whole, decimal, fraction_only, exponent = match.groups()
    decimal = fraction_only if whole is None else (decimal or "")
    whole = whole or "0"
    e = _int_text(exponent) if exponent is not None else 0
    if abs(e) > 10000:
        raise DomainError("Decimal exponent exceeds the bounded input contract")
    numerator = _int_text(("-" if sign == "-" else "") + whole + decimal)
    power = e - len(decimal)
    return Fraction(numerator * 10**power) if power >= 0 else Fraction(numerator, 10**(-power))


def rational_text(value) -> str:
    value = Q(value)
    numerator = _text_int(value.numerator)
    return numerator if value.denominator == 1 else numerator + "/" + _text_int(value.denominator)


def _nonnegative(value, name):
    result = Q(value)
    if result < 0:
        raise DomainError(name + " must be nonnegative")
    return result


def _positive(value, name):
    result = Q(value)
    if result <= 0:
        raise DomainError(name + " must be positive")
    return result


def _integer(value, minimum, maximum, name):
    if type(value) is not int or not minimum <= value <= maximum:
        raise DomainError(f"{name} must be an integer in [{minimum},{maximum}]")
    return value


def floor_scaled(value: Fraction, scale: int) -> int:
    return value.numerator * scale // value.denominator


def ceil_scaled(value: Fraction, scale: int) -> int:
    return -((-value.numerator * scale) // value.denominator)


@dataclass(frozen=True)
class Interval:
    lo: Fraction
    hi: Fraction

    def __post_init__(self):
        object.__setattr__(self, "lo", Q(self.lo))
        object.__setattr__(self, "hi", Q(self.hi))
        if self.lo > self.hi:
            raise DomainError("Interval lower endpoint exceeds upper endpoint")

    def export(self):
        return {"lo": rational_text(self.lo), "hi": rational_text(self.hi)}

    @property
    def width(self):
        return self.hi - self.lo


def outward_dyadic(interval: Interval, bits: int) -> Interval:
    _integer(bits, MIN_BITS, MAX_BITS, "bits")
    scale = 1 << bits
    return Interval(Fraction(floor_scaled(interval.lo, scale), scale),
                    Fraction(ceil_scaled(interval.hi, scale), scale))


@lru_cache(maxsize=128)
def _exp_neg_cached(z: Fraction, bits: int) -> Interval:
    if z == 0:
        return Interval(Fraction(1), Fraction(1))
    y, squarings = z, 0
    while y > Fraction(1, 2):
        y /= 2
        squarings += 1
    # Two consecutive alternating partial sums enclose exp(-y). The precision
    # target controls cost/width; enclosure validity does not depend on it.
    threshold = Fraction(1, 1 << (bits + 16 + squarings))
    partial, term = Fraction(1), Fraction(1)
    even_sum = Fraction(1)
    odd_sum = None
    for degree in range(1, 1025):
        term *= y / degree
        partial = partial - term if degree % 2 else partial + term
        if degree % 2:
            odd_sum = partial
            if degree >= 3 and term <= threshold:
                break
        else:
            even_sum = partial
    else:
        raise DomainError("Taylor enclosure exceeded the finite primitive bound")
    if odd_sum is None or not 0 < odd_sum <= even_sum <= 1:
        raise ArithmeticError("Alternating Taylor enclosure invariant failed")
    scale = 1 << bits
    lower = floor_scaled(odd_sum, scale)
    upper = ceil_scaled(even_sum, scale)
    for _ in range(squarings):
        lower = lower * lower // scale
        upper = (upper * upper + scale - 1) // scale
        # exp(-z) <= 1 is an independent exact global upper bound.
        upper = min(upper, scale)
    return Interval(Fraction(lower, scale), Fraction(upper, scale))


def exp_neg(value, bits=256) -> Interval:
    """Outward dyadic enclosure of exp(-z) for exact 0<=z<=256."""
    z = _nonnegative(value, "z")
    _integer(bits, MIN_BITS, MAX_BITS, "bits")
    if z > MAX_MU:
        raise DomainError("z exceeds the declared exp primitive domain 0..256")
    return _exp_neg_cached(z, bits)


def exp_neg_interval(z: Interval, bits=256) -> Interval:
    if not isinstance(z, Interval):
        raise DomainError("Expected an Interval")
    return Interval(exp_neg(z.hi, bits).lo, exp_neg(z.lo, bits).hi)


def normalize_weights(weights) -> tuple[Interval, ...]:
    weights = tuple(weights)
    _integer(len(weights), 1, MAX_N, "state count")
    if any(not isinstance(w, Interval) or w.lo <= 0 for w in weights):
        raise DomainError("Normalization requires strictly positive weight lower bounds")
    lower_sum = sum((w.lo for w in weights), Fraction())
    upper_sum = sum((w.hi for w in weights), Fraction())
    return tuple(Interval(w.lo / (w.lo + upper_sum - w.hi),
                          w.hi / (w.hi + lower_sum - w.lo)) for w in weights)


def thermal_from_levels(energies_cm_inverse, degeneracies, temperature_K="100", bits=256):
    energies = tuple(Q(e) for e in energies_cm_inverse)
    gs = tuple(_positive(g, "degeneracy") for g in degeneracies)
    _integer(len(energies), 1, MAX_N, "state count")
    if len(energies) != len(gs):
        raise DomainError("Energy/degeneracy dimension mismatch")
    if any(e < energies[0] for e in energies):
        raise DomainError("Reference level must have minimum supplied energy")
    temperature = _positive(temperature_K, "temperature_K")
    factor = H_PLANCK * C_LIGHT * 100 / (K_BOLTZMANN * temperature)
    zs = tuple(factor * (e - energies[0]) for e in energies)
    exponentials = tuple(exp_neg(z, bits) for z in zs)
    weights = tuple(Interval(g * b.lo, g * b.hi) for g, b in zip(gs, exponentials))
    pis = normalize_weights(weights)
    return {"z": zs, "exp_neg_z": exponentials, "weights": weights, "pi": pis,
            "degeneracies": gs, "energies_cm_inverse": energies, "temperature_K": temperature,
            "precision_bits": bits}


def pair_ratio(thermal, upper_index: int, lower_index: int) -> Interval:
    n = len(thermal["z"])
    _integer(upper_index, 0, n - 1, "upper_index")
    _integer(lower_index, 0, n - 1, "lower_index")
    gap = thermal["z"][upper_index] - thermal["z"][lower_index]
    if gap < 0:
        raise DomainError("Upward pair must have nonnegative energy gap")
    b = exp_neg(gap, thermal["precision_bits"])
    ratio = thermal["degeneracies"][upper_index] / thermal["degeneracies"][lower_index]
    return Interval(ratio * b.lo, ratio * b.hi)


def matrix(values):
    n = len(values)
    _integer(n, 1, MAX_N, "matrix size")
    if any(len(row) != n for row in values):
        raise DomainError("Expected a square matrix")
    return tuple(tuple(Q(v) for v in row) for row in values)


def export_matrix(values):
    return [[rational_text(v) for v in row] for row in values]


@dataclass(frozen=True)
class GeneratorBox:
    lower: tuple
    upper: tuple

    def __post_init__(self):
        lower, upper = matrix(self.lower), matrix(self.upper)
        if len(lower) != len(upper):
            raise DomainError("Generator bound dimension mismatch")
        n = len(lower)
        for j in range(n):
            for i in range(n):
                if lower[i][j] > upper[i][j] or (i != j and lower[i][j] < 0):
                    raise DomainError("Invalid ordered nonnegative offdiagonal bounds")
            if lower[j][j] != -sum(upper[i][j] for i in range(n) if i != j):
                raise DomainError("Lower diagonal must be minus upper total exit")
            if upper[j][j] != -sum(lower[i][j] for i in range(n) if i != j):
                raise DomainError("Upper diagonal must be minus lower total exit")
        object.__setattr__(self, "lower", lower)
        object.__setattr__(self, "upper", upper)

    @property
    def n(self):
        return len(self.lower)


def generator_from_offdiagonal(lower, upper=None) -> GeneratorBox:
    lower, upper = matrix(lower), matrix(lower if upper is None else upper)
    if len(lower) != len(upper):
        raise DomainError("Offdiagonal bound dimension mismatch")
    n = len(lower)
    if any(lower[i][i] or upper[i][i] for i in range(n)):
        raise DomainError("This constructor requires zero diagonal placeholders")
    lo, hi = [list(row) for row in lower], [list(row) for row in upper]
    for j in range(n):
        lo[j][j] = -sum(upper[i][j] for i in range(n) if i != j)
        hi[j][j] = -sum(lower[i][j] for i in range(n) if i != j)
    return GeneratorBox(tuple(map(tuple, lo)), tuple(map(tuple, hi)))


def exact_generator(values) -> GeneratorBox:
    values = matrix(values)
    n = len(values)
    if any(sum(values[i][j] for i in range(n)) for j in range(n)):
        raise DomainError("Generator column sum must be exactly zero")
    return GeneratorBox(values, values)


def reset_generator_bounds(K: GeneratorBox, pi, v, kappa=0) -> GeneratorBox:
    """Bound the full A=K+pi(v-kappa*1)^T-diag(v-kappa*1)."""
    pi, v, kappa = tuple(pi), tuple(v), _nonnegative(kappa, "kappa")
    n = K.n
    if len(pi) != n or len(v) != n or any(not isinstance(a, Interval) for a in pi + v):
        raise DomainError("Reset inputs must be n-dimensional interval vectors")
    if any(p.lo < 0 or p.hi > 1 for p in pi):
        raise DomainError("Probability intervals must lie in [0,1]")
    if not sum(p.lo for p in pi) <= 1 <= sum(p.hi for p in pi):
        raise DomainError("Probability intervals do not contain a simplex point")
    if any(a.lo < kappa for a in v):
        raise DomainError("kappa exceeds a supplied destruction lower bound")
    lo = [[Fraction() for _ in range(n)] for _ in range(n)]
    hi = [[Fraction() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                lo[i][j] = K.lower[i][j] + pi[i].lo * (v[j].lo - kappa)
                hi[i][j] = K.upper[i][j] + pi[i].hi * (v[j].hi - kappa)
    return generator_from_offdiagonal(lo, hi)


def uniformization_lower(A: GeneratorBox, rate=None):
    n = A.n
    exits = tuple(sum(A.upper[i][j] for i in range(n) if i != j) for j in range(n))
    max_exit = max(exits)
    rate = (2 * max_exit if max_exit else Fraction(1)) if rate is None else _positive(rate, "lambda")
    if rate < max_exit:
        raise DomainError("lambda fails the full-generator upper exit bound")
    lower = tuple(tuple((1 - exits[j] / rate) if i == j else A.lower[i][j] / rate
                        for j in range(n)) for i in range(n))
    if any(v < 0 for row in lower for v in row):
        raise ArithmeticError("Negative lower transition entry")
    if any(sum(lower[i][j] for i in range(n)) > 1 for j in range(n)):
        raise ArithmeticError("Lower transition matrix is not substochastic")
    return rate, lower


def _matmul_down(left, right, scale):
    n = len(left)
    columns = tuple(zip(*right))
    return [[sum(a * b for a, b in zip(row, col)) // scale for col in columns] for row in left]


def _overlap_integer(R, scale):
    n = len(R)
    if n == 1:
        return scale  # The zero-sum subspace is {0}; no matrix-overlap claim is needed.
    return min(sum(min(R[i][j], R[i][k]) for i in range(n))
               for j in range(n) for k in range(j + 1, n))


def finite_block(A: GeneratorBox, H, degree: int, bits=512, rate=None, identifier="block"):
    H = _positive(H, "H")
    _integer(degree, 0, MAX_N_TERMS, "degree")
    _integer(bits, MIN_BITS, MAX_BITS, "bits")
    rate, P = uniformization_lower(A, rate)
    mu = rate * H
    if mu > MAX_MU:
        raise DomainError("lambda*H exceeds the finite 256 bound")
    exponential = exp_neg(mu, bits)
    n, scale = A.n, 1 << bits
    P_int = [[floor_scaled(x, scale) for x in row] for row in P]
    power = [[scale if i == j else 0 for j in range(n)] for i in range(n)]
    R = [[0] * n for _ in range(n)]
    weight = floor_scaled(exponential.lo, scale)
    trace = []
    trace_degrees = {0, 1, 8, 32, 64, 128, 320, degree}
    for m in range(degree + 1):
        for i in range(n):
            for j in range(n):
                R[i][j] += weight * power[i][j] // scale
        if m in trace_degrees:
            trace.append({"degree": m, "beta_lower": rational_text(Fraction(_overlap_integer(R, scale), scale))})
        if m != degree:
            power = _matmul_down(power, P_int, scale)
            weight = weight * mu.numerator // (mu.denominator * (m + 1))
    if any(sum(R[i][j] for i in range(n)) > scale for j in range(n)):
        raise ArithmeticError("Computed lower propagator exceeds stochastic column mass")
    beta = Fraction(_overlap_integer(R, scale), scale)
    if not 0 <= beta <= 1:
        raise ArithmeticError("Computed overlap outside [0,1]")
    return {"id": str(identifier), "H": rational_text(H), "lambda": rational_text(rate),
            "mu": rational_text(mu), "N": degree, "precision_bits": bits,
            "P_lower": export_matrix(P), "exp_neg_mu": exponential.export(),
            "R_lower": export_matrix([[Fraction(x, scale) for x in row] for row in R]),
            "beta_lower": rational_text(beta), "rho_upper": rational_text(1 - beta),
            "partial_overlap_trace": trace,
            "method": "downward dyadic matrix powers and Poisson-weight recurrence; all omitted terms nonnegative",
            "n1_zero_sum_convention": n == 1}


def instantaneous_coefficient(K: GeneratorBox) -> Fraction:
    """Lower Dobrushin generator coefficient, for comparison only."""
    if K.n == 1:
        return Fraction(0)
    A, n = K.lower, K.n
    return min(A[i][j] + A[j][i] + sum(min(A[k][i], A[k][j])
               for k in range(n) if k not in (i, j)) for i in range(n) for j in range(i + 1, n))


def forced_step(state, coefficients, H, rho, kappa=0):
    """One rational endpoint update plus independent whole-block envelopes.

    The caller supplies valid interval-wide nonnegative lower damping and upper
    forcing/coupling bounds. rho must certify the full reset generator A over H.
    """
    H, rho, kappa = _positive(H, "H"), _nonnegative(rho, "rho"), _nonnegative(kappa, "kappa")
    if rho > 1:
        raise DomainError("rho must lie in [0,1]")
    if set(state) != {"M", "U", "E"}:
        raise DomainError("State must contain exactly M,U,E")
    required = {"k_lower", "b_lower", "q_upper", "g_upper", "s_upper", "F_upper"}
    if set(coefficients) != required:
        raise DomainError("Coefficient names do not match the forced-block contract")
    M, U, E = (_nonnegative(state[k], k) for k in ("M", "U", "E"))
    k, b, q, g, s, F = (_nonnegative(coefficients[key], key) for key in
                         ("k_lower", "b_lower", "q_upper", "g_upper", "s_upper", "F_upper"))
    M_star = M + F * H
    G = q * M_star + g
    integral_U = H * U + G * H * H / 2
    end = {"M": M / (1 + k * H) + F * H,
           "U": rho * U / (1 + kappa * H) + G * H,
           "E": E / (1 + b * H) + s * integral_U}
    whole = {"M": M_star, "U": U + G * H, "E": E + s * integral_U}
    return {"endpoint": end, "whole_block": whole, "forcing_bound": G,
            "integral_U_bound": integral_U}


def constant_coefficients(K, pi, v, f):
    """Exact bounds for a declared constant mathematical fixture."""
    K = exact_generator(K).lower
    pi, v, f = tuple(map(Q, pi)), tuple(map(Q, v)), tuple(map(Q, f))
    n = len(K)
    if len(pi) != n or len(v) != n or len(f) != n:
        raise DomainError("Constant fixture vector dimension mismatch")
    if sum(pi) != 1 or any(x < 0 for x in pi + v + f):
        raise DomainError("Constant fixture violates positivity/simplex conditions")
    vbar, F = sum(pi[i] * v[i] for i in range(n)), sum(f)
    c = [sum(K[i][j] * pi[j] for j in range(n)) - v[i] * pi[i] + pi[i] * vbar for i in range(n)]
    Qf = [f[i] - pi[i] * F for i in range(n)]
    return {"k_lower": min(v), "b_lower": vbar, "q_upper": sum(map(abs, c)),
            "g_upper": sum(map(abs, Qf)), "s_upper": (max(v) - min(v)) / 2,
            "F_upper": F}


def native_hd_source(source_path=None, parser_path=None, bits=256):
    """Use pinned REC source parser; compute no old REC diagnostic suite."""
    reused = Path(__file__).resolve().parents[2] / "provider_registry_molecular_r5_20261027" / "authority" / "reused"
    source_path = Path(source_path) if source_path else reused / "lamda_hd_20261025.dat"
    parser_path = Path(parser_path) if parser_path else reused / "rec_lamda_hd.py"
    source_bytes, parser_bytes = source_path.read_bytes(), parser_path.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != SOURCE_SHA256:
        raise DomainError("Native source byte identity mismatch")
    if hashlib.sha256(parser_bytes).hexdigest() != PARSER_SHA256:
        raise DomainError("Reused parser byte identity mismatch")
    spec = importlib.util.spec_from_file_location("wu_r6_pinned_rec_parser", parser_path)
    if spec is None or spec.loader is None:
        raise DomainError("Pinned parser cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    data = module.parse_hd(source_bytes)
    levels = data.levels
    thermal = thermal_from_levels([x.energy_cm_inverse.literal for x in levels],
                                  [x.degeneracy.literal for x in levels], "100", bits)
    collider = data.collider(2)
    indexes = [i for i, t in enumerate(collider.temperature_nodes_K) if Q(t.literal) == 100]
    if len(indexes) != 1:
        raise DomainError("Pinned source lacks a unique native 100 K column")
    n = len(levels)
    lower = [[Fraction() for _ in range(n)] for _ in range(n)]
    upper = [[Fraction() for _ in range(n)] for _ in range(n)]
    ratios = []
    for pair in collider.downward_pairs:
        u, l = pair.upper - 1, pair.lower - 1
        down = Q(pair.downward_cm3_per_s[indexes[0]].literal) / RATE_SCALE_CM3_S
        ratio = pair_ratio(thermal, u, l)
        lower[l][u] += down; upper[l][u] += down
        lower[u][l] += down * ratio.lo; upper[u][l] += down * ratio.hi
        ratios.append(dict(upper_id=u + 1, lower_id=l + 1, **ratio.export()))
    K = generator_from_offdiagonal(lower, upper)
    export = {"level_ids": [x.id for x in levels],
              "energies_cm_inverse": [x.energy_cm_inverse.literal for x in levels],
              "degeneracies": [x.degeneracy.literal for x in levels],
              "z": [rational_text(z) for z in thermal["z"]],
              "exp_neg_z": [x.export() for x in thermal["exp_neg_z"]],
              "weights": [x.export() for x in thermal["weights"]],
              "pi": [x.export() for x in thermal["pi"]],
              "pair_ratios": ratios, "precision_bits": bits,
              "source_sha256": SOURCE_SHA256, "parser_sha256": PARSER_SHA256,
              "temperature_K": "100", "collider_id": 2,
              "vibrational_state": "UNSPECIFIED", "missing_transitions": "MISSING_NOT_ZERO",
              "selected_graph": "9 native downward pairs plus their declared detailed-balance reverses",
              "literal_equilibrium_identity": "K*pi=0 by shared exact Gibbs pair ratios; independent box corners need not have that correlation"}
    return K, thermal, export
