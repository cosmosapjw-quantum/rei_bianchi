"""Exact represented-input event algebra. No physical-source admission occurs here.

R = sum(q q^T / mass), K = trace(R)/2, J = STF(R).
Normalization is mandatory: conditional_event has event mass Z=1;
cross_section_weighted has event mass Z=sigma. All numbers are exact.
"""
from dataclasses import dataclass
from fractions import Fraction
import re


class ContractError(ValueError):
    """Malformed or inconsistent exact contract input."""


F = Fraction
ZERO_V = (F(0),) * 3
ZERO_M = (ZERO_V,) * 3
IDENTITY = tuple(tuple(F(i == j) for j in range(3)) for i in range(3))
NORMALIZATIONS = {"conditional_event", "cross_section_weighted"}


def exact(value, name="value"):
    """Accept int, Fraction, or integer/rational string; reject bool and float."""
    if type(value) is int or isinstance(value, Fraction):
        return F(value)
    if isinstance(value, str) and re.fullmatch(r"[+-]?\d+(?:/[1-9]\d*)?", value):
        try:
            return F(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise ContractError(f"{name}: invalid rational") from exc
    raise ContractError(f"{name}: exact int or rational string required; binary float/bool refused")


def vector(value, name="vector"):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ContractError(f"{name}: exactly three components required")
    return tuple(exact(x, f"{name}[{i}]") for i, x in enumerate(value))


def matrix(value, name="matrix"):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ContractError(f"{name}: 3 by 3 matrix required")
    return tuple(vector(row, f"{name}[{i}]") for i, row in enumerate(value))


def vadd(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def vscale(k, a):
    return tuple(k * x for x in a)


def dot(a, b):
    return sum((a[i] * b[i] for i in range(3)), F(0))


def outer(a, b):
    return tuple(tuple(a[i] * b[j] for j in range(3)) for i in range(3))


def madd(a, b):
    return tuple(tuple(a[i][j] + b[i][j] for j in range(3)) for i in range(3))


def mscale(k, a):
    return tuple(tuple(k * x for x in row) for row in a)


def transpose(a):
    return tuple(tuple(a[j][i] for j in range(3)) for i in range(3))


def matmul(a, b):
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(3)), F(0))
                       for j in range(3)) for i in range(3))


def matvec(a, b):
    return tuple(dot(row, b) for row in a)


def trace(a):
    return sum((a[i][i] for i in range(3)), F(0))


@dataclass(frozen=True)
class Event:
    weight: Fraction
    q1: tuple
    q2: tuple
    qp: tuple

    def __post_init__(self):
        object.__setattr__(self, "weight", exact(self.weight, "weight"))
        if self.weight < 0:
            raise ContractError("weight: nonnegative event weight required")
        for name in ("q1", "q2", "qp"):
            object.__setattr__(self, name, vector(getattr(self, name), name))

    @classmethod
    def from_dict(cls, value):
        if not isinstance(value, dict) or set(value) != {"weight", "q1", "q2", "qp"}:
            raise ContractError("event: exactly weight,q1,q2,qp fields required")
        return cls(**value)


@dataclass(frozen=True)
class RawMoments:
    """Algebraic raw-moment container; this class does not certify PSD or realizability.

    Exact event integration supplies its own event-support evidence. Arbitrary raw
    inputs and their boosts are not HE-X1 certificates or physical admissions.
    """
    mass: Fraction
    N: Fraction
    P: tuple
    R: tuple
    normalization: str
    kind: str = "gain"

    def __post_init__(self):
        object.__setattr__(self, "mass", exact(self.mass, "mass"))
        object.__setattr__(self, "N", exact(self.N, "N"))
        object.__setattr__(self, "P", vector(self.P, "P"))
        object.__setattr__(self, "R", matrix(self.R, "R"))
        if self.mass <= 0:
            raise ContractError("mass: strictly positive kinetic mass required")
        if not isinstance(self.normalization, str) or self.normalization not in NORMALIZATIONS:
            raise ContractError("normalization: explicit supported normalization required")
        if not isinstance(self.kind, str) or self.kind not in {"gain", "signed_source"}:
            raise ContractError("kind: gain or signed_source required")
        if self.R != transpose(self.R):
            raise ContractError("R: exact symmetry required; no symmetrizing projection")
        if self.kind == "gain" and self.N < 0:
            raise ContractError("N: negative gain count refused")
        if self.kind == "gain" and self.N == 0 and (self.P != ZERO_V or self.R != ZERO_M):
            raise ContractError("zero gain count requires zero gain moments")

    @property
    def K(self):
        return trace(self.R) / 2

    @property
    def J(self):
        return madd(self.R, mscale(-trace(self.R) / 3, IDENTITY))


@dataclass(frozen=True)
class EventMoments:
    electron: RawMoments
    proton: RawMoments
    C12: tuple
    E: Fraction
    I: Fraction
    measure_mass: Fraction

    def __post_init__(self):
        if not isinstance(self.electron, RawMoments) or not isinstance(self.proton, RawMoments):
            raise ContractError("event moments require two RawMoments records")
        if self.electron.kind != "gain" or self.proton.kind != "gain":
            raise ContractError("event moments require gain records")
        if self.electron.normalization != self.proton.normalization:
            raise ContractError("event moments require one common normalization")
        for name in ("E", "I", "measure_mass"):
            object.__setattr__(self, name, exact(getattr(self, name), name))
        object.__setattr__(self, "C12", matrix(self.C12, "C12"))
        Z, m, M = self.measure_mass, self.electron.mass, self.proton.mass
        if self.E < 0 or self.I <= 0 or Z < 0 or (Z > 0 and self.E < self.I):
            raise ContractError("invalid event energy or measure mass")
        if self.normalization == "conditional_event" and Z != 1:
            raise ContractError("conditional event measure mass must be one")
        if self.electron.N != 2 * Z or self.proton.N != Z:
            raise ContractError("inclusive electron count2 and ion count1 must share event mass Z")
        if vadd(self.electron.P, self.proton.P) != ZERO_V:
            raise ContractError("event moments violate COM momentum ledger")
        if self.electron.K + self.proton.K != Z * (self.E - self.I):
            raise ContractError("event moments violate the Z-weighted energy ledger")
        if self.C12 != transpose(self.C12) or self.proton.R != madd(mscale(m / M, self.electron.R), mscale(1 / M, self.C12)):
            raise ContractError("event moments violate the pair-correlation identity")

    @property
    def normalization(self):
        return self.electron.normalization


def parameters(m, M, E, I, require_event_shell=True):
    m, M, E, I = (exact(v, n) for v, n in zip((m, M, E, I), ("m", "M", "E", "I")))
    if m <= 0 or M <= 0 or I <= 0 or E < 0:
        raise ContractError("m,M,I must be positive and E nonnegative")
    if require_event_shell and E < I:
        raise ContractError("E<I: no conditional ionization event shell")
    return m, M, E, I


def integrate_events(events, m, M, E, I):
    """Integrate a finite normalized event law with exact momentum/energy support."""
    m, M, E, I = parameters(m, M, E, I)
    if not isinstance(events, (list, tuple)) or not events:
        raise ContractError("events: nonempty ordered sequence required")
    if any(not isinstance(event, Event) for event in events):
        raise ContractError("events: validated Event instances required")
    if sum((event.weight for event in events), F(0)) != 1:
        raise ContractError("weights: conditional event weights must sum exactly to one")
    Pe, Pp, Re, Rp, C = ZERO_V, ZERO_V, ZERO_M, ZERO_M, ZERO_M
    for index, event in enumerate(events):
        w, q1, q2, qp = event.weight, event.q1, event.q2, event.qp
        if vadd(vadd(q1, q2), qp) != ZERO_V:
            raise ContractError(f"event[{index}]: momentum support violated")
        if (dot(q1, q1) + dot(q2, q2)) / (2 * m) + dot(qp, qp) / (2 * M) != E - I:
            raise ContractError(f"event[{index}]: energy support violated")
        Pe, Pp = vadd(Pe, vscale(w, vadd(q1, q2))), vadd(Pp, vscale(w, qp))
        Re = madd(Re, mscale(w / m, madd(outer(q1, q1), outer(q2, q2))))
        Rp = madd(Rp, mscale(w / M, outer(qp, qp)))
        C = madd(C, mscale(w, madd(outer(q1, q2), outer(q2, q1))))
    return EventMoments(RawMoments(m, 2, Pe, Re, "conditional_event"),
                        RawMoments(M, 1, Pp, Rp, "conditional_event"), C, E, I, F(1))


def cross_section_weighted(result, sigma):
    """Multiply conditional moments by sigma; there is no inverse normalization API."""
    sigma = exact(sigma, "sigma")
    if not isinstance(result, EventMoments) or result.normalization != "conditional_event" or result.measure_mass != 1:
        raise ContractError("conditional EventMoments with Z=1 required; double sigma weighting refused")
    if sigma < 0:
        raise ContractError("sigma: nonnegative cross section required")
    def scale(raw):
        return RawMoments(raw.mass, sigma * raw.N, vscale(sigma, raw.P),
                          mscale(sigma, raw.R), "cross_section_weighted", raw.kind)
    return EventMoments(scale(result.electron), scale(result.proton), mscale(sigma, result.C12),
                        result.E, result.I, sigma)


def zero_cross_section(m, M, E, I):
    """Return sigma=0 moments directly, without constructing a conditional law."""
    m, M, E, I = parameters(m, M, E, I, require_event_shell=False)
    return EventMoments(RawMoments(m, 0, ZERO_V, ZERO_M, "cross_section_weighted"),
                        RawMoments(M, 0, ZERO_V, ZERO_M, "cross_section_weighted"),
                        ZERO_M, E, I, F(0))


def transform_raw(raw, boost, rotation=IDENTITY):
    """Passive boost then basis change: q'=O(q-mU), valid also for signed N."""
    if not isinstance(raw, RawMoments):
        raise ContractError("raw: RawMoments required")
    U, O = vector(boost, "boost"), matrix(rotation, "rotation")
    if matmul(O, transpose(O)) != IDENTITY:
        raise ContractError("rotation: exact orthogonal matrix required; no normalization")
    P = vadd(raw.P, vscale(-raw.mass * raw.N, U))
    R = madd(madd(raw.R, mscale(-1, madd(outer(U, raw.P), outer(raw.P, U)))),
             mscale(raw.mass * raw.N, outer(U, U)))
    return RawMoments(raw.mass, raw.N, matvec(O, P), matmul(matmul(O, R), transpose(O)),
                      raw.normalization, raw.kind)


def numbers(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (tuple, list)):
        return [numbers(item) for item in value]
    return value


def serialize_raw(raw):
    multiplier = "1" if raw.normalization == "conditional_event" else "m^2"
    return {"mass_kg": str(raw.mass), "N": str(raw.N), "P": numbers(raw.P),
            "R": numbers(raw.R), "K": str(raw.K), "J": numbers(raw.J),
            "normalization": raw.normalization, "kind": raw.kind,
            "units": {"N": multiplier, "P": f"{multiplier}*(kg*m/s)",
                      "R": f"{multiplier}*J", "K": f"{multiplier}*J"}}


def serialize_bundle(result):
    m, M, Z, W = result.electron.mass, result.proton.mass, result.measure_mass, result.E - result.I
    identity = madd(mscale(m / M, result.electron.R), mscale(1 / M, result.C12))
    return {"electron": serialize_raw(result.electron), "proton": serialize_raw(result.proton),
            "C12": numbers(result.C12), "measure_mass_Z": str(Z),
            "C12_units": "kg*J" if result.normalization == "conditional_event" else "m^2*kg*J",
            "normalization": result.normalization, "E_J": str(result.E), "I_J": str(result.I),
            "ledger": {"Kp_expected": str(Z * W - result.electron.K),
                       "Kp_actual": str(result.proton.K),
                       "trace_C12_expected": str(2 * M * Z * W - 2 * (M + m) * result.electron.K),
                       "trace_C12_actual": str(trace(result.C12)),
                       "ion_R_identity_exact": result.proton.R == identity},
            "empirical_admission": False, "runtime_activation": False}
