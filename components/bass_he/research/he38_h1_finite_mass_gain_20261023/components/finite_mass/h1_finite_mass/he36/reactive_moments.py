"""Incoming reactive pressure moments in the HE36 common-T Grad model.

Equation references are to ``theory/DERIVATION.md`` (the independently derived
HE36 document; its original is /tmp/he36_theory_independent/DERIVATION.md).
The implementation supplies incoming LOSS only.  Product motion, recoil,
radiation and daughter branching must be supplied separately.  In particular,
the removed-parent energy in Eq. (6) is not a net reaction heating law.

All arguments use SI: n [m^-3], m [kg], T [K], pi [Pa], alpha [m^3/s],
beta [J m^3/s], gamma [J^2 m^3/s].  The pair consists of DISTINCT species;
there is no identical-reactant symmetry factor or automated species inference.
The reference distributions share a temperature and a bulk rest frame.
The STF calculation is a linear first variation, not a globally positive Grad
distribution or a finite-anisotropy realizability/accuracy certificate.

Only Python's standard library and NumPy are required.  No IVP is executed.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numbers
import sys
from typing import ClassVar

import numpy as np


K_B = 1.380649e-23  # exact SI J/K
C_LIGHT = 299792458.0  # exact SI m/s; classical-domain responsibility is external
EPS = sys.float_info.epsilon
MOMENT_ROUNDOFF = 128.0 * EPS
TENSOR_ROUNDOFF = 128.0 * EPS


class MomentDomainError(ValueError):
    """Inputs do not satisfy the explicitly admitted model or moment domain."""


class MomentRepresentabilityError(ArithmeticError):
    """A requested nonzero result/product cannot be represented in binary64."""


def _scalar(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, numbers.Real):
        raise MomentDomainError(f"{name}: REAL_SCALAR_REQUIRED")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise MomentDomainError(f"{name}: FINITE_SCALAR_REQUIRED") from exc
    if not math.isfinite(value):
        raise MomentDomainError(f"{name}: FINITE_SCALAR_REQUIRED")
    if positive and value <= 0:
        raise MomentDomainError(f"{name}: POSITIVE_VALUE_REQUIRED")
    if nonnegative and value < 0:
        raise MomentDomainError(f"{name}: NONNEGATIVE_VALUE_REQUIRED")
    return value


def _muldiv(numerators, denominators=(), *, label="product"):
    """Multiply/divide with a separate binary exponent, avoiding false overflow.

    True zero factors give zero.  A mathematically nonzero product that rounds
    to zero is rejected rather than silently being treated as a support zero.
    Final subnormals are retained.  Inputs here have already been validated.
    """
    if any(v == 0 for v in denominators):
        raise MomentDomainError(f"{label}: ZERO_DENOMINATOR")
    if any(v == 0 for v in numerators):
        return 0.0
    mantissa, exponent = 1.0, 0
    for values, divide in ((numerators, False), (denominators, True)):
        for value in values:
            part, power = math.frexp(value)
            if divide:
                mantissa /= part
                exponent -= power
            else:
                mantissa *= part
                exponent += power
            mantissa, power = math.frexp(mantissa)
            exponent += power
    try:
        answer = math.ldexp(mantissa, exponent)
    except OverflowError as exc:
        raise MomentRepresentabilityError(f"{label}: BINARY64_OVERFLOW") from exc
    if not math.isfinite(answer):
        raise MomentRepresentabilityError(f"{label}: BINARY64_OVERFLOW")
    if answer == 0.0:
        raise MomentRepresentabilityError(f"{label}: NONZERO_BINARY64_UNDERFLOW")
    return answer


def _sum(values, *, label="sum"):
    try:
        result = math.fsum(values)
    except OverflowError as exc:
        raise MomentRepresentabilityError(f"{label}: BINARY64_OVERFLOW") from exc
    if not math.isfinite(result):
        raise MomentRepresentabilityError(f"{label}: BINARY64_OVERFLOW")
    return result


def _readonly(array):
    # bytes-backed arrays cannot be made writeable by setflags(write=True).
    data = np.asarray(array, dtype=np.float64)
    return np.frombuffer(data.tobytes(order="C"), dtype=np.float64).reshape(data.shape)


def _matrix(value, name, *, traceless):
    try:
        original = np.asarray(value)
        if original.dtype.kind not in "fiu":
            raise MomentDomainError(f"{name}: REAL_NUMERIC_ARRAY_REQUIRED")
        array = np.asarray(original, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise MomentDomainError(f"{name}: FINITE_3_BY_3_REQUIRED") from exc
    if array.shape != (3, 3) or not np.all(np.isfinite(array)):
        raise MomentDomainError(f"{name}: FINITE_3_BY_3_REQUIRED")
    scale = float(np.max(np.abs(array)))
    if scale == 0:
        return _readonly(array), 0.0, 0.0, 0.0
    normalized = array / scale
    symmetry = max(abs(float(normalized[i, j] - normalized[j, i]))
                   for i in range(3) for j in range(3))
    trace = abs(math.fsum(float(normalized[i, i]) for i in range(3)))
    if symmetry > TENSOR_ROUNDOFF:
        raise MomentDomainError(f"{name}: NOT_SYMMETRIC")
    if traceless and trace > TENSOR_ROUNDOFF:
        raise MomentDomainError(f"{name}: NOT_TRACELESS")
    # No symmetrization, trace subtraction or eigenvalue clipping is done.
    norm = math.hypot(*(float(v) for v in array.flat))
    if not math.isfinite(norm):
        raise MomentRepresentabilityError(f"{name}: FROBENIUS_NORM_OVERFLOW")
    return _readonly(array), norm, symmetry, trace


def _vector(value, name):
    try:
        original = np.asarray(value)
        if original.dtype.kind not in "fiu":
            raise MomentDomainError(f"{name}: REAL_NUMERIC_ARRAY_REQUIRED")
        result = np.asarray(original, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise MomentDomainError(f"{name}: FINITE_THREE_VECTOR_REQUIRED") from exc
    if result.shape != (3,) or not np.all(np.isfinite(result)):
        raise MomentDomainError(f"{name}: FINITE_THREE_VECTOR_REQUIRED")
    return result


def _cauchy_defect(alpha, beta, gamma):
    """Return (beta^2-alpha*gamma)/max(...) without those raw products."""
    fa, ea = math.frexp(alpha)
    fb, eb = math.frexp(beta)
    fg, eg = math.frexp(gamma)
    left, right = fa * fg, fb * fb
    difference = ea + eg - 2 * eb
    if difference >= 0:
        right = math.ldexp(right, -difference)
    else:
        left = math.ldexp(left, difference)
    return (right - left) / max(right, left)


@dataclass(frozen=True, slots=True)
class MomentCoefficients:
    """Eq. (3)/(5) radial coefficients, each in m^3/s; theta is in joules."""
    alpha: float
    k1: float
    k2: float
    theta: float


@dataclass(frozen=True, slots=True)
class RawMoments:
    """Immutable supplied Maxwellian moment triple with necessary gates only.

    alpha*gamma>=beta^2 is checked with a normalized 128-epsilon allowance.
    Original supplied values are retained, including an admitted tiny negative
    Cauchy residual; this check never repairs the input or certifies its source.
    Nonzero channels require all three positive finite moments, as appropriate
    to the declared nonnegative integrable kernel on positive energy.
    All-zero moments require a nonempty ``zero_reason`` stating a declared
    physical/support zero. A floating-point underflow flag is NOT such a reason;
    callers importing numerical providers must reject underflow before this API.
    """
    alpha: float
    beta: float
    gamma: float
    provenance: str = ""
    interpretation: str = "supplied_moments"
    temperature_K: float | None = None
    unit_system: str = "SI"
    zero_reason: str | None = None
    units: ClassVar[tuple[str, str, str]] = ("m^3/s", "J m^3/s", "J^2 m^3/s")

    def __post_init__(self):
        if self.unit_system != "SI":
            raise MomentDomainError("MOMENTS_REQUIRE_EXPLICIT_SI_UNITS")
        if not isinstance(self.provenance, str) or not isinstance(self.interpretation, str) or not self.interpretation:
            raise MomentDomainError("INVALID_PROVENANCE_OR_INTERPRETATION")
        for name in ("alpha", "beta", "gamma"):
            object.__setattr__(self, name, _scalar(getattr(self, name), name, nonnegative=True))
        if self.temperature_K is not None:
            object.__setattr__(self, "temperature_K", _scalar(self.temperature_K, "temperature_K", positive=True))
        values = (self.alpha, self.beta, self.gamma)
        if any(value == 0 for value in values):
            if not all(value == 0 for value in values):
                raise MomentDomainError("INCOHERENT_PARTIALLY_ZERO_MOMENTS")
            if not isinstance(self.zero_reason, str) or not self.zero_reason.strip():
                raise MomentDomainError("EXPLICIT_PHYSICAL_ZERO_REASON_REQUIRED")
            return
        if self.zero_reason is not None:
            raise MomentDomainError("NONZERO_MOMENTS_WITH_ZERO_REASON")
        if _cauchy_defect(*values) > MOMENT_ROUNDOFF:
            raise MomentDomainError("MOMENT_CAUCHY_INEQUALITY_FAILED")

    @property
    def cauchy_normalized_defect(self):
        return 0.0 if self.alpha == 0 else _cauchy_defect(self.alpha, self.beta, self.gamma)

    def coefficients(self, T):
        T = _scalar(T, "T", positive=True)
        if self.temperature_K is not None and T != self.temperature_K:
            raise MomentDomainError("MOMENT_TEMPERATURE_IDENTITY_MISMATCH")
        theta = _muldiv((K_B, T), label="theta")
        if self.alpha == 0:
            return MomentCoefficients(0.0, 0.0, 0.0, theta)
        k1 = _muldiv((2.0, self.beta), (3.0, theta), label="k1")
        k2 = _muldiv((4.0, self.gamma), (15.0, theta, theta), label="k2")
        return MomentCoefficients(self.alpha, k1, k2, theta)


def mass_fractions(ma, mb):
    """Stable a=mA/(mA+mB), b=mB/(mA+mB), without forming the mass sum."""
    ma = _scalar(ma, "ma", positive=True)
    mb = _scalar(mb, "mb", positive=True)
    if ma <= mb:
        ratio = _muldiv((ma,), (mb,), label="mass_ratio")
        a, b = ratio / (1.0 + ratio), 1.0 / (1.0 + ratio)
    else:
        ratio = _muldiv((mb,), (ma,), label="mass_ratio")
        a, b = 1.0 / (1.0 + ratio), ratio / (1.0 + ratio)
    if a == 0 or b == 0:
        raise MomentRepresentabilityError("NONZERO_MASS_FRACTION_UNDERFLOW")
    return a, b


@dataclass(frozen=True, slots=True)
class BinaryLoss:
    """Eq. (5)/(6) incoming sources; all arrays are immutable binary64 copies."""
    Rn_a: float
    Rn_b: float
    Q_a: float
    Q_b: float
    J_a: np.ndarray
    J_b: np.ndarray
    S_a: np.ndarray
    S_b: np.ndarray
    coefficient_block: np.ndarray
    loss_block: np.ndarray
    loss_eigenvalues: tuple[float, float]
    mass_fraction_a: float
    mass_fraction_b: float
    relative_anisotropy_a: float
    relative_anisotropy_b: float
    tensor_residuals: tuple[float, float, float, float]
    radial_coefficients: MomentCoefficients
    scope: str = "incoming_only_common_T_common_bulk_linear_Grad_distinct_species"
    grad_budget_interpretation: str = "optional_amplitude_diagnostic_not_truncation_error_bound"


def _tensor_combination(ca, a, cb, b, label):
    result = np.empty((3, 3))
    for i in range(3):
        for j in range(3):
            result[i, j] = -_sum((
                _muldiv((ca, float(a[i, j])), label=label + "_a"),
                _muldiv((cb, float(b[i, j])), label=label + "_b")), label=label)
    return _readonly(result)


def _pressure_source(J, Q, label):
    trace_part = _muldiv((2.0, Q), (3.0,), label=label + "_trace_part")
    result = np.array(J, copy=True)
    for i in range(3):
        result[i, i] = _sum((float(J[i, i]), trace_part), label=label)
    return _readonly(result)


def _loss_eigenvalues(na, nb, a, b, coeff, A, B, C):
    d0 = _muldiv((nb, A), label="loss00")
    d1 = _muldiv((na, B), label="loss11")
    if na == 0 or nb == 0 or coeff.alpha == 0:
        return tuple(sorted((d0, d1)))
    off = _muldiv((math.sqrt(na), math.sqrt(nb), C), label="weighted_loss_offdiagonal")
    scale = max(d0, d1, abs(off))
    x, y, z = d0 / scale, d1 / scale, off / scale
    high = _muldiv((scale, 0.5 * (x + y + math.hypot(x - y, 2.0*z))), label="loss_eigenvalue_high")
    # Eq. (7): determinant/high avoids subtracting nearly equal eigenvalues.
    common = (na, nb, a+b, a+b)
    low = _sum((
        _muldiv((*common, a-b, a-b, coeff.alpha, coeff.k2), (high,), label="eigenvalue_low_term1"),
        _muldiv((*common, 2.0, a, b, coeff.k1, coeff.alpha), (high,), label="eigenvalue_low_term2"),
        _muldiv((*common, 2.0, a, b, coeff.k1, coeff.k2), (high,), label="eigenvalue_low_term3")),
        label="loss_eigenvalue_low")
    return tuple(sorted((low, high)))


def binary_loss(na, nb, ma, mb, T, pi_a, pi_b, moments: RawMoments,
                *, linear_response: bool, grad_budget: float | None = None):
    """Incoming source for a distinct binary pair, Eqs. (5)--(7).

    ``linear_response=True`` is mandatory. ``grad_budget``, when given, limits
    ||pi_s||_F/(n_s k_B T) only as a caller-selected amplitude diagnostic; it is
    NOT a certified nonlinear truncation/physical-validity bound. With None,
    arbitrary directions of the infinitesimal derivative are accepted.
    Positive kernel moments do not make C nonnegative; signed C is preserved.
    The returned loss_block is positive in J=-L*pi; its weighted similarity is
    symmetric at strictly positive densities. At an absent-species boundary,
    the reported eigenvalues are only the algebraic matrix spectrum; nonzero
    pressure perturbations of that absent species are not admitted.
    Its eigenvalues describe a frozen instantaneous incoming block,
    not a complete reactive relaxation spectrum or an entropy theorem.
    """
    if linear_response is not True:
        raise MomentDomainError("EXPLICIT_LINEAR_RESPONSE_TRUE_REQUIRED")
    if not isinstance(moments, RawMoments):
        raise MomentDomainError("VALIDATED_RAW_MOMENTS_REQUIRED")
    na = _scalar(na, "na", nonnegative=True)
    nb = _scalar(nb, "nb", nonnegative=True)
    a, b = mass_fractions(ma, mb)
    coeff = moments.coefficients(T)
    pa, norm_a, symmetry_a, trace_a = _matrix(pi_a, "pi_a", traceless=True)
    pb, norm_b, symmetry_b, trace_b = _matrix(pi_b, "pi_b", traceless=True)
    for n, norm, name in ((na, norm_a, "a"), (nb, norm_b, "b")):
        if n == 0 and norm != 0:
            raise MomentDomainError(f"ABSENT_SPECIES_{name}_HAS_NONZERO_PRESSURE")
    relative_a = 0.0 if norm_a == 0 else _muldiv((norm_a,), (na, coeff.theta), label="relative_anisotropy_a")
    relative_b = 0.0 if norm_b == 0 else _muldiv((norm_b,), (nb, coeff.theta), label="relative_anisotropy_b")
    if grad_budget is not None:
        budget = _scalar(grad_budget, "grad_budget", nonnegative=True)
        if max(relative_a, relative_b) > budget:
            raise MomentDomainError("CALLER_GRAD_AMPLITUDE_BUDGET_EXCEEDED")
    A = _sum((
        _muldiv((a, a, coeff.alpha), label="A1"),
        _muldiv((2.0, a, b, coeff.k1), label="A2"),
        _muldiv((b, b, coeff.k2), label="A3")), label="A")
    B = _sum((
        _muldiv((b, b, coeff.alpha), label="B1"),
        _muldiv((2.0, a, b, coeff.k1), label="B2"),
        _muldiv((a, a, coeff.k2), label="B3")), label="B")
    C = _sum((
        _muldiv((a, b, coeff.alpha), label="C1"),
        -_muldiv((2.0, a, b, coeff.k1), label="C2"),
        _muldiv((a, b, coeff.k2), label="C3")), label="C")
    L = _readonly([
        [_muldiv((nb, A), label="L00"), _muldiv((na, C), label="L01")],
        [_muldiv((nb, C), label="L10"), _muldiv((na, B), label="L11")]])
    ja = _tensor_combination(float(L[0, 0]), pa, float(L[0, 1]), pb, "J_a")
    jb = _tensor_combination(float(L[1, 0]), pa, float(L[1, 1]), pb, "J_b")
    number = -_muldiv((na, nb, coeff.alpha), label="number_source")
    qa = -_sum((
        _muldiv((na, nb, 1.5, a, coeff.theta, coeff.alpha), label="Q_a_COM"),
        _muldiv((na, nb, b, moments.beta), label="Q_a_relative")), label="Q_a")
    qb = -_sum((
        _muldiv((na, nb, 1.5, b, coeff.theta, coeff.alpha), label="Q_b_COM"),
        _muldiv((na, nb, a, moments.beta), label="Q_b_relative")), label="Q_b")
    return BinaryLoss(number, number, qa, qb, ja, jb,
                      _pressure_source(ja, qa, "S_a"), _pressure_source(jb, qb, "S_b"),
                      _readonly([[A, C], [C, B]]), L,
                      _loss_eigenvalues(na, nb, a, b, coeff, A, B, C), a, b,
                      relative_a, relative_b, (symmetry_a, trace_a, symmetry_b, trace_b), coeff)


def centralize_reactive_source(mass, Rn, momentum_source, raw_second_source, velocity):
    """Eq. (10): R2-u F^T-F u^T+m Rn u u^T, with supplied raw sources.

    Momentum source is the derivative of m*n*u, and raw_second_source is the
    derivative of m*integral(v v f dv). Rn is the number source. Both this
    function and its caller retain source signs. This instantaneous algebra
    does not infer a birth distribution, bulk evolution or thermalization.
    """
    mass = _scalar(mass, "mass", positive=True)
    Rn = _scalar(Rn, "Rn")
    F = _vector(momentum_source, "momentum_source")
    u = _vector(velocity, "velocity")
    R2, _, _, _ = _matrix(raw_second_source, "raw_second_source", traceless=False)
    result = np.empty((3, 3))
    for i in range(3):
        for j in range(3):
            result[i, j] = _sum((
                float(R2[i, j]),
                -_muldiv((float(u[i]), float(F[j])), label="central_uF"),
                -_muldiv((float(F[i]), float(u[j])), label="central_Fu"),
                _muldiv((mass, Rn, float(u[i]), float(u[j])), label="central_number_term")),
                label="central_pressure_source")
    return _readonly(result)


def moments_from_rate_derivatives(T, alpha, T_alpha_prime, T2_alpha_second,
                                 *, kernel_temperature_independent: bool,
                                 differentiation_justified: bool,
                                 provenance: str = ""):
    """Eq. (1) conditional derivative-of-rate closure, not source validation.

    Inputs after alpha are T*dalpha/dT and T^2*d^2alpha/dT^2, each [m^3/s].
    The second is NOT the second derivative with respect to log T.
    Both caller obligations must be explicitly True. The output remains
    labeled conditional_rate_fit_derivative even when these flags are True.
    Moment feasibility is necessary and does not bound fit-derivative error.
    """
    if kernel_temperature_independent is not True:
        raise MomentDomainError("TEMPERATURE_DEPENDENT_KERNEL_NEEDS_EXTRA_MOMENTS")
    if differentiation_justified is not True:
        raise MomentDomainError("DIFFERENTIATION_UNDER_INTEGRAL_NOT_DECLARED")
    T = _scalar(T, "T", positive=True)
    alpha = _scalar(alpha, "alpha", nonnegative=True)
    d1 = _scalar(T_alpha_prime, "T_alpha_prime")
    d2 = _scalar(T2_alpha_second, "T2_alpha_second")
    theta = _muldiv((K_B, T), label="derivative_theta")
    beta = _sum((
        _muldiv((theta, d1), label="beta_derivative"),
        _muldiv((theta, 1.5, alpha), label="beta_number")), label="beta")
    gamma = _sum((
        _muldiv((theta, theta, d2), label="gamma_second_derivative"),
        _muldiv((theta, theta, 5.0, d1), label="gamma_first_derivative"),
        _muldiv((theta, theta, 3.75, alpha), label="gamma_number")), label="gamma")
    return RawMoments(alpha, beta, gamma, provenance=provenance,
                      interpretation="conditional_rate_fit_derivative", temperature_K=T)
