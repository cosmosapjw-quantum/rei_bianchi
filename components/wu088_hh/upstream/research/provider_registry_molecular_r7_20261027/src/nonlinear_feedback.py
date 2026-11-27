"""Exact-rational event feedback and causal finite-block comparison.

The mathematical contract is theory/NONLINEAR_FEEDBACK_PROOF_KO.md (R7.1--32).
This module computes conditional bounds; it does not integrate a physical ODE
or infer source ensembles, branching, density histories, or clock conversions.
All inputs that affect arithmetic are exact integers, rational/decimal strings,
or Fraction objects. Binary floating-point input is rejected deliberately.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Mapping, Sequence


class DomainError(ValueError):
    """An explicit finite-domain or input-binding condition was not met."""


def _int_text(text: str) -> int:
    s = text.strip()
    sign = -1 if s.startswith("-") else 1
    if s[:1] in ("-", "+"):
        s = s[1:]
    if not s or not s.isascii() or not s.isdigit():
        raise DomainError("Expected a base-10 integer")
    value = 0
    for i in range(0, len(s), 9):
        chunk = s[i:i + 9]
        value = value * (10 ** len(chunk)) + int(chunk)
    return sign * value


def Q(value) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise DomainError("Use an exact integer, Fraction, or decimal/rational string")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        s = value.strip()
        try:
            if "/" in s:
                left, right = s.split("/")
                return Fraction(_int_text(left), _int_text(right))
            return Fraction(s)
        except (ValueError, ZeroDivisionError) as exc:
            raise DomainError("Invalid finite exact scalar") from exc
    raise DomainError("Unsupported scalar type")


def _int_string(value: int) -> str:
    if value == 0:
        return "0"
    sign = "-" if value < 0 else ""
    n = abs(value)
    chunks = []
    while n:
        n, rem = divmod(n, 10**9)
        chunks.append(rem)
    return sign + str(chunks[-1]) + "".join(f"{x:09d}" for x in reversed(chunks[:-1]))


def rational_text(value) -> str:
    q = Q(value)
    n = _int_string(q.numerator)
    return n if q.denominator == 1 else n + "/" + _int_string(q.denominator)


def export(value):
    """JSON-ready exact output, without changing Python's integer-string limit."""
    if isinstance(value, Fraction):
        return rational_text(value)
    if isinstance(value, Interval):
        return {"lo": export(value.lo), "hi": export(value.hi)}
    if isinstance(value, Mapping):
        return {str(k): export(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [export(v) for v in value]
    return value


def _nonnegative(value, name):
    q = Q(value)
    if q < 0:
        raise DomainError(name + " must be nonnegative")
    return q


def _positive(value, name):
    q = Q(value)
    if q <= 0:
        raise DomainError(name + " must be positive")
    return q


def _integer(value, lower, upper, name):
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise DomainError(f"{name} must be an integer in [{lower}, {upper}]")
    return value


def _vector(values, name, length=None, nonnegative=False):
    if isinstance(values, (str, bytes)):
        raise DomainError(name + " must be a vector")
    try:
        out = tuple(Q(x) for x in values)
    except TypeError as exc:
        raise DomainError(name + " must be a vector") from exc
    if length is not None and len(out) != length:
        raise DomainError(name + " has incompatible dimension")
    if nonnegative and any(x < 0 for x in out):
        raise DomainError(name + " must be componentwise nonnegative")
    return out


def _matrix(values, name, rows=None, columns=None):
    try:
        out = tuple(_vector(row, name + " row") for row in values)
    except TypeError as exc:
        raise DomainError(name + " must be a matrix") from exc
    if not out or not out[0] or any(len(row) != len(out[0]) for row in out):
        raise DomainError(name + " must be a nonempty rectangular matrix")
    if rows is not None and len(out) != rows:
        raise DomainError(name + " has incompatible row count")
    if columns is not None and len(out[0]) != columns:
        raise DomainError(name + " has incompatible column count")
    return out


def _mm(A, B):
    return tuple(tuple(sum((A[i][k] * B[k][j] for k in range(len(B))), Fraction(0))
                       for j in range(len(B[0]))) for i in range(len(A)))


def _mv(A, v):
    return tuple(sum((a * b for a, b in zip(row, v)), Fraction(0)) for row in A)


def _eye(n):
    return tuple(tuple(Fraction(i == j) for j in range(n)) for i in range(n))


def _ceil_div(n, d):
    return -(-n // d)


def _floor_scaled(value, scale):
    return value.numerator * scale // value.denominator


def _ceil_scaled(value, scale):
    return _ceil_div(value.numerator * scale, value.denominator)


@dataclass(frozen=True)
class Interval:
    lo: Fraction
    hi: Fraction

    def __post_init__(self):
        lo, hi = Q(self.lo), Q(self.hi)
        if lo > hi:
            raise DomainError("Interval lower endpoint exceeds upper endpoint")
        object.__setattr__(self, "lo", lo)
        object.__setattr__(self, "hi", hi)


def interval(value, name="interval", *, nonnegative=False, probability=False):
    if isinstance(value, Interval):
        out = value
    elif isinstance(value, (tuple, list)):
        if len(value) != 2:
            raise DomainError(name + " requires two endpoints")
        out = Interval(value[0], value[1])
    else:
        q = Q(value)
        out = Interval(q, q)
    if (nonnegative or probability) and out.lo < 0:
        raise DomainError(name + " has a negative lower endpoint")
    if probability and out.hi > 1:
        raise DomainError(name + " exceeds probability one")
    return out


def _simplex(values, name="simplex"):
    out = _vector(values, name, nonnegative=True)
    if not out or sum(out) != 1:
        raise DomainError(name + " must sum exactly to one")
    return out


def _simplex_box(values, name="simplex box"):
    out = tuple(interval(v, name, probability=True) for v in values)
    if not out or sum(x.lo for x in out) > 1 or sum(x.hi for x in out) < 1:
        raise DomainError(name + " has no simplex point")
    return out


@dataclass(frozen=True)
class Event:
    name: str
    reactants: tuple[int, ...]
    products: tuple[int, ...]
    rate: Fraction
    source_variant: str = "mathematical"

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise DomainError("Each event needs a nonempty identity")
        reactants, products = tuple(self.reactants), tuple(self.products)
        if not 1 <= len(reactants) <= 16 or len(products) != len(reactants):
            raise DomainError("Event dimension must be between one and sixteen")
        for a in reactants + products:
            _integer(a, 0, 4, "stoichiometric multiplicity")
        if sum(reactants) > 4:
            raise DomainError("This finite implementation supports reaction order at most four")
        if not isinstance(self.source_variant, str) or not self.source_variant:
            raise DomainError("Event source variant must be explicitly labelled")
        object.__setattr__(self, "reactants", reactants)
        object.__setattr__(self, "products", products)
        object.__setattr__(self, "rate", _nonnegative(self.rate, "rate"))

    @property
    def column(self):
        return tuple(b - a for a, b in zip(self.reactants, self.products))


def mass_action_jacobian_upper(exponents, rates_upper, state_upper):
    """Reaction-by-state Jacobian upper; orders zero are handled before powers."""
    upper = _vector(state_upper, "state upper", nonnegative=True)
    if not 1 <= len(upper) <= 16:
        raise DomainError("State dimension must be between one and sixteen")
    orders = tuple(tuple(row) for row in exponents)
    if len(orders) > 64:
        raise DomainError("At most sixty-four event channels are supported")
    rates = _vector(rates_upper, "rate upper", len(orders), nonnegative=True)
    result = []
    for alpha, rate in zip(orders, rates):
        if len(alpha) != len(upper):
            raise DomainError("Exponent/state dimension mismatch")
        for degree in alpha:
            _integer(degree, 0, 4, "reaction exponent")
        if sum(alpha) > 4:
            raise DomainError("Reaction order exceeds four")
        row = []
        for i, order in enumerate(alpha):
            if order == 0:
                row.append(Fraction(0))
                continue
            derivative = rate * order
            for j, power in enumerate(alpha):
                derivative *= upper[j] ** (power - (i == j))
            row.append(derivative)
        result.append(tuple(row))
    return tuple(result)


@dataclass(frozen=True)
class ReactionNetwork:
    species: tuple[str, ...]
    events: tuple[Event, ...]
    invariants: tuple[tuple[Fraction, ...], ...] = ()

    def __post_init__(self):
        names, events = tuple(self.species), tuple(self.events)
        if not 1 <= len(names) <= 16 or len(set(names)) != len(names):
            raise DomainError("Require one to sixteen distinct species identities")
        if any(not isinstance(x, str) or not x for x in names):
            raise DomainError("Species identities must be nonempty strings")
        if len(events) > 64 or any(not isinstance(e, Event) for e in events):
            raise DomainError("Require at most sixty-four Event objects")
        if len({e.name for e in events}) != len(events):
            raise DomainError("Event identities must be distinct")
        if any(len(e.reactants) != len(names) for e in events):
            raise DomainError("Event/species dimension mismatch")
        W = tuple(_vector(row, "invariant row", len(names)) for row in self.invariants)
        for row in W:
            if any(sum(a * b for a, b in zip(row, event.column)) != 0 for event in events):
                raise DomainError("Declared invariant does not annihilate every event column")
        object.__setattr__(self, "species", names)
        object.__setattr__(self, "events", events)
        object.__setattr__(self, "invariants", W)

    @property
    def stoichiometry(self):
        return tuple(tuple(event.column[i] for event in self.events) for i in range(len(self.species)))

    def propensities(self, state):
        x = _vector(state, "state", len(self.species), nonnegative=True)
        rates = []
        for event in self.events:
            value = event.rate
            for xi, power in zip(x, event.reactants):
                value *= xi ** power
            rates.append(value)
        return tuple(rates)

    def rhs(self, state):
        rates = self.propensities(state)
        return tuple(sum((event.column[i] * rate for event, rate in zip(self.events, rates)), Fraction(0))
                     for i in range(len(self.species)))

    def jacobian_upper(self, box, rates_upper=None):
        bounds = tuple(interval(x, "state box", nonnegative=True) for x in box)
        if len(bounds) != len(self.species):
            raise DomainError("Box/species dimension mismatch")
        rates = tuple(e.rate for e in self.events) if rates_upper is None else _vector(rates_upper, "rate upper", len(self.events), nonnegative=True)
        if any(u < e.rate for u, e in zip(rates, self.events)):
            raise DomainError("Rate upper excludes the network's declared rate")
        return mass_action_jacobian_upper(tuple(e.reactants for e in self.events), rates, tuple(x.hi for x in bounds))


def mass_action_rhs(network: ReactionNetwork, state):
    if not isinstance(network, ReactionNetwork):
        raise DomainError("Require a ReactionNetwork")
    return network.rhs(state)


_FORMATION_VARIANTS = frozenset({
    "TIQM", "SQM", "SYNTHETIC",
    "HONVAULT2013_CORRECTED_HD_FORMATION_TIQM",
    "HONVAULT2013_CORRECTED_HD_FORMATION_SQM",
})


def _formation_variant(value):
    if not isinstance(value, str) or value not in _FORMATION_VARIANTS:
        raise DomainError("Select exactly one TIQM, SQM, or explicitly SYNTHETIC formation model")
    return value


def hd_network(alpha, kf, destruction, *, formation_variant, source_scope):
    """Conditional u+v <-> w+HD_i channels; alpha is required, never inferred."""
    branch = _simplex(alpha, "formation branch")
    if not 1 <= len(branch) <= 13:
        raise DomainError("HD state count must be between one and thirteen")
    k = _nonnegative(kf, "formation coefficient")
    d = _vector(destruction, "destruction coefficients", len(branch), nonnegative=True)
    variant = _formation_variant(formation_variant)
    if not isinstance(source_scope, str) or not source_scope.strip():
        raise DomainError("An explicit conditional source/common-pool scope is required")
    n = len(branch)
    events = []
    for i in range(n):
        reactants = (1, 1, 0) + (0,) * n
        products = (0, 0, 1) + tuple(int(i == j) for j in range(n))
        events.append(Event(f"HD_FORM_{i}", reactants, products, k * branch[i], variant))
        events.append(Event(f"HD_DEST_{i}", products, reactants, d[i], "explicit_state_d_vector"))
    W = ((2, 0, 1) + (1,) * n, (0, 1, 0) + (1,) * n, (0, 1, 1) + (0,) * n)
    return ReactionNetwork(("H2_pool", "Dplus_pool", "Hplus_pool") + tuple(f"HD_state_{i}" for i in range(n)), tuple(events), W)


def hd_aggregate(fine_state):
    x = _vector(fine_state, "fine state", nonnegative=True)
    if not 4 <= len(x) <= 16:
        raise DomainError("HD fine state requires three reservoirs and one to thirteen HD states")
    return x[:3] + (sum(x[3:]),)


def hd_invariants(aggregate):
    u, v, w, X = _vector(aggregate, "HD aggregate", 4, nonnegative=True)
    return (2 * u + w + X, v + X, v + w)


def hd_lift(coarse_state, pi):
    y = _vector(coarse_state, "coarse state", 4, nonnegative=True)
    p = _simplex(pi, "population lift")
    if len(p) > 13:
        raise DomainError("At most thirteen HD states are supported")
    return y[:3] + tuple(y[3] * value for value in p)


def hd_scalar_error(fine_state, coarse_state, pi):
    x = _vector(fine_state, "fine state", nonnegative=True)
    y = hd_aggregate(x)
    ybar = _vector(coarse_state, "coarse state", 4, nonnegative=True)
    p = _simplex(pi, "population lift")
    if len(x) != len(p) + 3:
        raise DomainError("Fine/lift dimension mismatch")
    if hd_invariants(y) != hd_invariants(ybar):
        raise DomainError("Scalar eta requires identical initial H, D, and charge invariants")
    eta = y[3] - ybar[3]
    difference = tuple(a - b for a, b in zip(y, ybar))
    if difference != (-eta, -eta, eta, eta):
        raise DomainError("Coarse difference is not in the invariant nullspace")
    r = tuple(xi - pj * y[3] for xi, pj in zip(x[3:], p))
    return {"eta": eta, "R": sum(abs(z) for z in r), "E": abs(eta),
            "residual": r, "aggregate": y, "coarse_error": difference,
            "coarse_error_l1": 4 * abs(eta), "invariants": hd_invariants(y)}


def hd_invariant_box(fine_state, coarse_state=None):
    y = hd_aggregate(fine_state)
    invariants = hd_invariants(y)
    if coarse_state is not None and hd_invariants(coarse_state) != invariants:
        raise DomainError("A common invariant box requires equal invariant classes")
    H, D, charge = invariants
    return {"u": (Fraction(0), H / 2), "v": (Fraction(0), min(D, charge)),
            "w": (Fraction(0), min(H, charge)), "X": (Fraction(0), min(H, D))}


def _hd_generator(K, n):
    A = _matrix(K, "HD generator", n, n)
    if any(A[i][j] < 0 for i in range(n) for j in range(n) if i != j):
        raise DomainError("Nominal HD generator must be Metzler")
    if any(sum(A[i][j] for i in range(n)) != 0 for j in range(n)):
        raise DomainError("Nominal HD generator must have zero column sums")
    return A


def hd_lift_defect_norm(K, pi, pi_dot):
    p = _simplex(pi, "population lift")
    derivative = _vector(pi_dot, "lift derivative", len(p))
    if sum(derivative) != 0:
        raise DomainError("A simplex lift derivative must sum to zero")
    Kp = _mv(_hd_generator(K, len(p)), p)
    return sum(abs(a - b) for a, b in zip(Kp, derivative))


def hd_rhs(fine_state, K, alpha, kf, destruction, *, formation_variant, source_scope):
    net = hd_network(alpha, kf, destruction, formation_variant=formation_variant, source_scope=source_scope)
    x = _vector(fine_state, "fine state", len(net.species), nonnegative=True)
    rhs = net.rhs(x)
    internal = _mv(_hd_generator(K, len(x) - 3), x[3:])
    return rhs[:3] + tuple(a + b for a, b in zip(rhs[3:], internal))


def hd_coarse_rhs(coarse_state, pi, kf, destruction):
    u, v, w, X = _vector(coarse_state, "coarse state", 4, nonnegative=True)
    p = _simplex(pi, "population lift")
    d = _vector(destruction, "destruction coefficients", len(p), nonnegative=True)
    flow = _nonnegative(kf, "formation coefficient") * u * v - w * X * sum(di * pj for di, pj in zip(d, p))
    return (-flow, -flow, flow, flow)


def _coefficient_metadata(metadata, n):
    if not isinstance(metadata, Mapping):
        raise DomainError("Coefficient source/clock metadata is required")
    required = ("state_ids", "source_variant_selection", "source_map_identity", "positive_box_evidence",
                "initial_invariant_compatibility", "clock", "time_unit", "density_unit",
                "nominal_generator_certificate_identity", "nominal_generator_block_H", "common_pool_binding")
    if any(key not in metadata for key in required):
        raise DomainError("Missing coefficient source/clock/box/invariant metadata")
    ids = metadata["state_ids"]
    if isinstance(ids, (str, bytes)) or len(ids) != n or len(set(ids)) != n or any(not isinstance(x, str) or not x for x in ids):
        raise DomainError("Coefficient state IDs must be unique and match the declared HD dimension")
    _formation_variant(metadata["source_variant_selection"])
    if metadata["initial_invariant_compatibility"] is not True:
        raise DomainError("Scalar HD coefficients require initial invariant compatibility")
    for name in ("source_map_identity", "clock", "time_unit", "density_unit", "nominal_generator_certificate_identity", "common_pool_binding"):
        if not isinstance(metadata[name], str) or not metadata[name].strip():
            raise DomainError("Nonempty " + name + " is required")
    if not metadata["positive_box_evidence"]:
        raise DomainError("The box requires an explicit validity evidence pointer")
    _positive(metadata["nominal_generator_block_H"], "nominal block length")
    return deepcopy(dict(metadata))


def hd_feedback_coefficients(density_box, kf, destruction, pi, *, q_norm_upper,
                             branch_distance_upper, coarse_scalar_defect_upper, metadata):
    """R7.28 safe coefficients. Bounds/box validity are explicit caller evidence."""
    if not isinstance(density_box, Mapping) or set(density_box) != {"u", "v", "w", "X"}:
        raise DomainError("Density box must have exactly u,v,w,X entries")
    boxes = {key: interval(density_box[key], key, nonnegative=True) for key in ("u", "v", "w", "X")}
    rate = interval(kf, "formation coefficient", nonnegative=True)
    dboxes = tuple(interval(value, "destruction coefficient", nonnegative=True) for value in destruction)
    pboxes = _simplex_box(pi)
    if not 1 <= len(pboxes) <= 13 or len(dboxes) != len(pboxes):
        raise DomainError("Destruction/lift dimension mismatch")
    meta = _coefficient_metadata(metadata, len(pboxes))
    qstar = _nonnegative(q_norm_upper, "lift defect bound")
    theta = _nonnegative(branch_distance_upper, "branch distance bound")
    if theta > 2:
        raise DomainError("Simplex branch distance bound must be in [0,2]")
    ge = _nonnegative(coarse_scalar_defect_upper, "coarse scalar defect bound")
    delta = max(x.hi for x in dboxes) - min(x.lo for x in dboxes)
    hstar = 2 * max(d.hi * (1 - p.lo) for d, p in zip(dboxes, pboxes))
    vstar = delta / 2
    dbar_lower = min(x.lo for x in dboxes)
    mu, mv, mw, mx = (boxes[k].lo for k in ("u", "v", "w", "X"))
    Mu, Mv, Mw, MX = (boxes[k].hi for k in ("u", "v", "w", "X"))
    a = Mw * hstar
    b = qstar + rate.hi * (Mu + Mv) * theta + (Mw + MX) * vstar
    c = Mw * delta / 2
    damping = -(rate.lo * (mu + mv) + dbar_lower * (mw + mx))
    gr = qstar * MX + rate.hi * Mu * Mv * theta + Mw * MX * vstar
    return {"B": ((a, b), (c, damping)), "g": (gr, ge), "a": a, "b": b, "c": c,
            "d": damping, "g_r": gr, "g_e": ge,
            "auxiliary": {"Delta_d": delta, "h_star": hstar, "v_star": vstar,
                          "dbar_lower": dbar_lower, "q_star": qstar, "theta_star": theta},
            "coefficient_units": {"B": "inverse declared time", "g": "declared density / declared time"},
            "metadata": meta}


def _controls(degree, bits):
    _integer(degree, 0, 256, "Taylor degree")
    _integer(bits, 128, 512, "dyadic bits")


def _scalar_positive_series(q_int, scale, degree, *, upward):
    term = scale
    total = scale
    for k in range(1, degree + 1):
        numerator = term * q_int
        denominator = scale * k
        term = _ceil_div(numerator, denominator) if upward else numerator // denominator
        total += term
    return total, term


def _geometric_tail_upper(z_int, scale, degree, final_term_upper):
    denom = (degree + 2) * scale - z_int
    if denom <= 0:
        raise DomainError("Taylor degree must satisfy N+2 > rounded scaled norm")
    first = _ceil_div(final_term_upper * z_int, scale * (degree + 1))
    return _ceil_div(first * (degree + 2) * scale, denom)


def exp_neg_enclosure(value, *, degree=96, bits=256):
    """Outward dyadic exp(-value) via reciprocals of positive Taylor bounds."""
    _controls(degree, bits)
    q = _nonnegative(value, "negative exponential argument")
    scale = 1 << bits
    lo_arg, hi_arg = _floor_scaled(q, scale), _ceil_scaled(q, scale)
    if hi_arg > 16 * scale or hi_arg >= (degree + 2) * scale:
        raise DomainError("Negative exponential argument exceeds its finite Taylor domain")
    low_sum, _ = _scalar_positive_series(lo_arg, scale, degree, upward=False)
    high_sum, high_term = _scalar_positive_series(hi_arg, scale, degree, upward=True)
    tail = _geometric_tail_upper(hi_arg, scale, degree, high_term)
    lo = Fraction(scale * scale // (high_sum + tail), scale)
    hi = Fraction(_ceil_div(scale * scale, low_sum), scale)
    return Interval(lo, hi)


def _comparison(B, g):
    matrix = _matrix(B, "comparison B", 2, 2)
    forcing = _vector(g, "comparison g", 2, nonnegative=True)
    if matrix[0][0] < 0 or matrix[0][1] < 0 or matrix[1][0] < 0:
        raise DomainError("Comparison requires a,b,c>=0; d may be signed")
    return matrix, forcing


def _scales(values):
    scales = _vector(values, "error coordinate scales", 2)
    if any(x <= 0 for x in scales):
        raise DomainError("Both error coordinate scales must be positive")
    return scales


@lru_cache(maxsize=256)
def _affine_kernel(B, g, H, degree, bits, scales):
    """Private immutable matrix/vector output; public metadata is copied."""
    if H == 0:
        return _eye(2), (Fraction(0), Fraction(0)), {"algorithm": "exact_identity", "degree": degree, "bits": bits}
    s0, s1 = scales
    M = ((B[0][0], B[0][1] * s1 / s0, g[0] / s0),
         (B[1][0] * s0 / s1, B[1][1], g[1] / s1),
         (Fraction(0), Fraction(0), Fraction(0)))
    shift = max(Fraction(0), -B[1][1])
    C = tuple(tuple(H * (M[i][j] + (shift if i == j else 0)) for j in range(3)) for i in range(3))
    if any(value < 0 for row in C for value in row):
        raise DomainError("Shifted augmented matrix is not nonnegative")
    scale = 1 << bits
    C_up = tuple(tuple(_ceil_scaled(value, scale) for value in row) for row in C)
    z_int = max(sum(row) for row in C_up)
    if z_int > 16 * scale:
        raise DomainError("Rounded scaled augmented matrix norm exceeds sixteen")
    if z_int >= (degree + 2) * scale:
        raise DomainError("Taylor degree must satisfy N+2 > rounded scaled norm")
    # This exact branch avoids any inverse and retains the singular controls.
    if all(v == 0 for row in _mm(B, B) for v in row):
        W = tuple(tuple(Fraction(i == j) + H * B[i][j] for j in range(2)) for i in range(2))
        Bg = _mv(B, g)
        q = tuple(H * g[i] + H * H * Bg[i] / 2 for i in range(2))
        return W, q, {"algorithm": "exact_B_squared_zero", "degree": degree, "bits": bits,
                      "shift": shift, "scaled_norm_upper": Fraction(z_int, scale), "tail_upper": Fraction(0)}
    term = [[scale if i == j else 0 for j in range(3)] for i in range(3)]
    partial = [row[:] for row in term]
    terminated = False
    terms_used = 0
    for k in range(1, degree + 1):
        term = [[_ceil_div(sum(term[i][p] * C_up[p][j] for p in range(3)), scale * k)
                 for j in range(3)] for i in range(3)]
        terms_used = k
        for i in range(3):
            for j in range(3):
                partial[i][j] += term[i][j]
        if not any(value for row in term for value in row):
            terminated = True
            break
    if not terminated:
        next_numerators = [[sum(term[i][p] * C_up[p][j] for p in range(3)) for j in range(3)] for i in range(3)]
        terminated = not any(value for row in next_numerators for value in row)
    if terminated:
        tail_int = 0
    else:
        _, scalar_term = _scalar_positive_series(z_int, scale, degree, upward=True)
        tail_int = _geometric_tail_upper(z_int, scale, degree, scalar_term)
    factor = exp_neg_enclosure(shift * H, degree=degree, bits=bits)
    factor_int = _ceil_scaled(factor.hi, scale)
    augmented_upper = tuple(tuple(Fraction(_ceil_div(factor_int * (partial[i][j] + tail_int), scale), scale)
                                   for j in range(3)) for i in range(3))
    W = tuple(tuple(scales[i] * augmented_upper[i][j] / scales[j] for j in range(2)) for i in range(2))
    q = tuple(scales[i] * augmented_upper[i][2] for i in range(2))
    trace = {"algorithm": "positive_shifted_dyadic_upper_with_geometric_tail", "degree": degree,
             "bits": bits, "terms_used": terms_used, "shift": shift, "shift_times_H": shift * H,
             "coordinate_scales": scales, "scaled_norm_upper": Fraction(z_int, scale),
             "tail_upper_before_exp_factor": Fraction(tail_int, scale),
             "exp_minus_shift_interval": (factor.lo, factor.hi),
             "finite_polynomial_terminated": terminated,
             "rounding": "C and each positive matrix/Poisson term upward; exp-minus uses reciprocal outward bounds",
             "norm": "induced infinity norm in explicitly scaled augmented coordinates"}
    return W, q, trace


def interior_feedback_upper(B, g, u, w0, *, degree=96, bits=256, coordinate_scales=(1, 1)):
    """Pointwise uncontracted comparison at u>=0; no block rho is used here."""
    matrix, forcing = _comparison(B, g)
    time = _nonnegative(u, "interior time")
    state = _vector(w0, "initial error bounds", 2, nonnegative=True)
    scales = _scales(coordinate_scales)
    _controls(degree, bits)
    W, q, trace = _affine_kernel(matrix, forcing, time, degree, bits, scales)
    linear = _mv(W, state)
    return {"u": time, "W_upper": W, "q": q, "w_upper": tuple(a + b for a, b in zip(linear, q)),
            "tail_certificate": deepcopy(trace)}


def _binding(binding, H, rho):
    if not isinstance(binding, Mapping):
        raise DomainError("A nominal-generator certificate binding is required")
    required = ("certificate_id", "H", "rho", "clock", "norm", "generator_scope", "feedback_accounted")
    if any(k not in binding for k in required):
        raise DomainError("Incomplete nominal-generator certificate binding")
    if Q(binding["H"]) != H or Q(binding["rho"]) != rho:
        raise DomainError("Block H/rho does not match the supplied certificate")
    if binding["norm"] != "l1_on_kerP" or binding["generator_scope"] != "nominal_K":
        raise DomainError("This causal subtraction is bound to the nominal K on ker(P)")
    if binding["feedback_accounted"] is not True:
        raise DomainError("Reaction/reset feedback must remain in the comparison coefficients")
    for name in ("certificate_id", "clock"):
        if not isinstance(binding[name], str) or not binding[name].strip():
            raise DomainError("Nonempty " + name + " is required")
    return deepcopy(dict(binding))


def block_feedback_upper(B, g, H, rho, w0, *, degree=96, bits=256, coordinate_scales=(1, 1), binding):
    """Causal endpoint bound plus a separate bound over the entire block.

    With negative d the second comparison coordinate may decrease. The uniform
    whole-block result therefore uses Bplus[d]=max(d,0), not V(H) for signed B.
    """
    matrix, forcing = _comparison(B, g)
    length = _positive(H, "block length")
    contraction = _nonnegative(rho, "block contraction")
    if contraction > 1:
        raise DomainError("Block contraction must not exceed one")
    state = _vector(w0, "initial error bounds", 2, nonnegative=True)
    scales = _scales(coordinate_scales)
    _controls(degree, bits)
    identity = _binding(binding, length, contraction)
    W, q, trace = _affine_kernel(matrix, forcing, length, degree, bits, scales)
    T = ((W[0][0] - 1 + contraction, W[0][1]), W[1])
    if any(value < 0 for row in T for value in row):
        raise ArithmeticError("The certified positive endpoint matrix became negative")
    endpoint = tuple(a + b for a, b in zip(_mv(T, state), q))
    Bplus = (matrix[0], (matrix[1][0], max(matrix[1][1], Fraction(0))))
    Wplus, qplus, plus_trace = _affine_kernel(Bplus, forcing, length, degree, bits, scales)
    whole = tuple(a + b for a, b in zip(_mv(Wplus, state), qplus))
    return {"B": matrix, "g": forcing, "H": length, "rho": contraction, "w0": state,
            "W_upper": W, "T": T, "q": q, "w_next_upper": endpoint,
            "whole_block_upper": whole, "coordinate_scales": scales, "binding": identity,
            "tail_certificate": deepcopy(trace),
            "whole_block_certificate": {"Bplus": Bplus, "reason": "nonnegative comparison is monotone in time and dominates signed-d comparison",
                                         "tail_certificate": deepcopy(plus_trace)}}

