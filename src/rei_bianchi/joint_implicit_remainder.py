"""Closed records for the Rust joint implicit-remainder certificate kernel.

This module intentionally performs no interval arithmetic and no linear solve.
It owns request validation, canonical serialization, and structural certificate
checks.  Claim-bearing replay is the responsibility of the authenticated
Rust/MPFR bridge in the REI-LOCAL-01 stage.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from typing import Any, ClassVar, Mapping, Sequence


REQUEST_SCHEMA = "rei-joint-implicit-request/v1"
CERTIFICATE_SCHEMA = "rei-source-bound-mpfr256/v2"
ROUNDING_POLICY = "MPFR_RNDD_RNDU"
PRECISION_BITS = 256


class CertificateValidationError(ValueError):
    """A closed request or certificate failed validation."""

    def __init__(self, classification: str, detail: str = "") -> None:
        self.classification = classification
        super().__init__(f"{classification}: {detail}" if detail else classification)


def _closed_keys(mapping: Mapping[str, Any], expected: set[str]) -> None:
    unknown = set(mapping) - expected
    if unknown:
        raise CertificateValidationError("UNKNOWN_FIELD", ",".join(sorted(unknown)))
    missing = expected - set(mapping)
    if missing:
        raise CertificateValidationError("MISSING_FIELD", ",".join(sorted(missing)))


def _dimension(value: int) -> int:
    if type(value) is not int or value not in (2, 3):
        raise CertificateValidationError("INVALID_DIMENSION", repr(value))
    return value


def _finite_tuple(
    name: str,
    values: Sequence[float] | None,
    length: int,
    *,
    missing: str = "MISSING_FIELD",
) -> tuple[float, ...]:
    if values is None:
        raise CertificateValidationError(missing, name)
    if not isinstance(values, (tuple, list)) or len(values) != length:
        raise CertificateValidationError("INVALID_SHAPE", name)
    converted = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in converted):
        raise CertificateValidationError("NONFINITE_VALUE", name)
    return converted


def _bounds(
    name: str,
    lower: Sequence[float] | None,
    upper: Sequence[float] | None,
    length: int,
    *,
    missing: str = "MISSING_FIELD",
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    lo = _finite_tuple(f"{name}_lower", lower, length, missing=missing)
    hi = _finite_tuple(f"{name}_upper", upper, length, missing=missing)
    if any(left > right for left, right in zip(lo, hi)):
        raise CertificateValidationError("INVALID_INTERVAL", name)
    return lo, hi


def _digest(name: str, value: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or value.lower() != value
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise CertificateValidationError("INVALID_SHA256", name)
    return value


def _canonical_value(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CertificateValidationError("NONFINITE_VALUE")
        return {"f64_hex": value.hex()}
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _canonical_value(value[key]) for key in sorted(value)}
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise CertificateValidationError("UNSERIALIZABLE_VALUE", type(value).__name__)


def _canonical_bytes(mapping: Mapping[str, Any]) -> bytes:
    return json.dumps(
        _canonical_value(dict(mapping)),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("ascii")


class _CanonicalRequest:
    """Shared canonical request behavior; dataclass fields remain in subclasses."""

    _KIND: ClassVar[str]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": REQUEST_SCHEMA,
            "kind": self._KIND,
            **{field.name: getattr(self, field.name) for field in fields(self)},
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.to_mapping())

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _set_bounds(
    instance: object,
    name: str,
    length: int,
    *,
    missing: str = "MISSING_FIELD",
) -> None:
    lower, upper = _bounds(
        name,
        getattr(instance, f"{name}_lower"),
        getattr(instance, f"{name}_upper"),
        length,
        missing=missing,
    )
    object.__setattr__(instance, f"{name}_lower", lower)
    object.__setattr__(instance, f"{name}_upper", upper)


def _set_digests(instance: object, names: Sequence[str]) -> None:
    for name in names:
        object.__setattr__(instance, name, _digest(name, getattr(instance, name)))


def _set_candidate(instance: object, dimension: int) -> None:
    lower = getattr(instance, "candidate_lower")
    upper = getattr(instance, "candidate_upper")
    if (lower is None) != (upper is None):
        raise CertificateValidationError("INCOMPLETE_CANDIDATE", "candidate")
    if lower is not None:
        candidate = _bounds("candidate", lower, upper, dimension)
        object.__setattr__(instance, "candidate_lower", candidate[0])
        object.__setattr__(instance, "candidate_upper", candidate[1])


@dataclass(frozen=True)
class LinearRequest(_CanonicalRequest):
    dimension: int
    a_lower: tuple[float, ...]
    a_upper: tuple[float, ...]
    b_lower: tuple[float, ...]
    b_upper: tuple[float, ...]
    candidate_lower: tuple[float, ...] | None
    candidate_upper: tuple[float, ...] | None
    authority_sha256: str
    owner_sha256: str
    context_sha256: str

    _KIND: ClassVar[str] = "LINEAR"

    def __post_init__(self) -> None:
        n = _dimension(self.dimension)
        object.__setattr__(self, "dimension", n)
        _set_bounds(self, "a", n * n)
        _set_bounds(self, "b", n)
        _set_candidate(self, n)
        _set_digests(self, ("authority_sha256", "owner_sha256", "context_sha256"))


@dataclass(frozen=True)
class TangentRequest(_CanonicalRequest):
    dimension: int
    a_lower: tuple[float, ...]
    a_upper: tuple[float, ...]
    z_lower: tuple[float, ...]
    z_upper: tuple[float, ...]
    delta_a_lower: tuple[float, ...] | None
    delta_a_upper: tuple[float, ...] | None
    delta_b_lower: tuple[float, ...]
    delta_b_upper: tuple[float, ...]
    authority_sha256: str
    owner_sha256: str
    context_sha256: str
    candidate_lower: tuple[float, ...] | None = None
    candidate_upper: tuple[float, ...] | None = None

    _KIND: ClassVar[str] = "TANGENT"

    def __post_init__(self) -> None:
        n = _dimension(self.dimension)
        object.__setattr__(self, "dimension", n)
        _set_bounds(self, "a", n * n)
        _set_bounds(self, "z", n)
        _set_bounds(self, "delta_a", n * n, missing="MISSING_DELTA_A")
        _set_bounds(self, "delta_b", n)
        _set_candidate(self, n)
        _set_digests(self, ("authority_sha256", "owner_sha256", "context_sha256"))


@dataclass(frozen=True)
class MixedRhsRequest(_CanonicalRequest):
    dimension: int
    b_vf_lower: tuple[float, ...]
    b_vf_upper: tuple[float, ...]
    a_vf_lower: tuple[float, ...] | None
    a_vf_upper: tuple[float, ...] | None
    z_lower: tuple[float, ...]
    z_upper: tuple[float, ...]
    a_v_lower: tuple[float, ...] | None
    a_v_upper: tuple[float, ...] | None
    z_f_lower: tuple[float, ...]
    z_f_upper: tuple[float, ...]
    a_f_lower: tuple[float, ...] | None
    a_f_upper: tuple[float, ...] | None
    z_v_lower: tuple[float, ...]
    z_v_upper: tuple[float, ...]
    authority_sha256: str

    _KIND: ClassVar[str] = "MIXED_VF"

    def __post_init__(self) -> None:
        n = _dimension(self.dimension)
        object.__setattr__(self, "dimension", n)
        _set_bounds(self, "b_vf", n)
        _set_bounds(self, "a_vf", n * n, missing="MISSING_MIXED_TERM")
        _set_bounds(self, "z", n)
        _set_bounds(self, "a_v", n * n, missing="MISSING_MIXED_TERM")
        _set_bounds(self, "z_f", n)
        _set_bounds(self, "a_f", n * n, missing="MISSING_MIXED_TERM")
        _set_bounds(self, "z_v", n)
        _set_digests(self, ("authority_sha256",))


@dataclass(frozen=True)
class MixedVfRequest(_CanonicalRequest):
    """Atomic mixed-partial request binding its base solve and every role."""

    dimension: int
    a_lower: tuple[float, ...]
    a_upper: tuple[float, ...]
    b_vf_lower: tuple[float, ...]
    b_vf_upper: tuple[float, ...]
    a_vf_lower: tuple[float, ...] | None
    a_vf_upper: tuple[float, ...] | None
    z_lower: tuple[float, ...]
    z_upper: tuple[float, ...]
    a_v_lower: tuple[float, ...] | None
    a_v_upper: tuple[float, ...] | None
    z_f_lower: tuple[float, ...]
    z_f_upper: tuple[float, ...]
    a_f_lower: tuple[float, ...] | None
    a_f_upper: tuple[float, ...] | None
    z_v_lower: tuple[float, ...]
    z_v_upper: tuple[float, ...]
    candidate_lower: tuple[float, ...] | None
    candidate_upper: tuple[float, ...] | None
    authority_sha256: str
    owner_sha256: str
    context_sha256: str

    _KIND: ClassVar[str] = "MIXED_VF_ATOMIC"

    def __post_init__(self) -> None:
        n = _dimension(self.dimension)
        object.__setattr__(self, "dimension", n)
        _set_bounds(self, "a", n * n)
        _set_bounds(self, "b_vf", n)
        _set_bounds(self, "a_vf", n * n, missing="MISSING_MIXED_TERM")
        _set_bounds(self, "z", n)
        _set_bounds(self, "a_v", n * n, missing="MISSING_MIXED_TERM")
        _set_bounds(self, "z_f", n)
        _set_bounds(self, "a_f", n * n, missing="MISSING_MIXED_TERM")
        _set_bounds(self, "z_v", n)
        _set_candidate(self, n)
        _set_digests(self, ("authority_sha256", "owner_sha256", "context_sha256"))


@dataclass(frozen=True)
class TangentCertificate:
    """Closed ABI-v4 certificate record.

    ``residual_lower`` and ``residual_upper`` are retained serialized field
    names for compatibility with the recovered v2 schema.  Their mathematical
    meaning is the *implicit right-hand side*: ``b`` for a linear request,
    ``delta_b - delta_A Z`` for a tangent request, and the complete mixed RHS
    for an atomic mixed request.  They are not ``b - A center`` residuals.
    Prefer the unambiguous ``implicit_rhs_*`` properties in new code.
    """

    request_sha256: str
    precision_bits: int
    rounding_policy: str
    backend_schema: str
    solution_lower: tuple[float, ...]
    solution_upper: tuple[float, ...]
    krawczyk_lower: tuple[float, ...]
    krawczyk_upper: tuple[float, ...]
    center: tuple[float, ...]
    residual_lower: tuple[float, ...]
    residual_upper: tuple[float, ...]
    preconditioner: tuple[float, ...]
    rho_upper: float
    lower_margins: tuple[float, ...]
    upper_margins: tuple[float, ...]
    iterations: int
    strict_self_inclusion: bool
    backend_identity_sha256: str

    _FIELD_NAMES: ClassVar[set[str]] = {
        "request_sha256",
        "precision_bits",
        "rounding_policy",
        "backend_schema",
        "solution_lower",
        "solution_upper",
        "krawczyk_lower",
        "krawczyk_upper",
        "center",
        "residual_lower",
        "residual_upper",
        "preconditioner",
        "rho_upper",
        "lower_margins",
        "upper_margins",
        "iterations",
        "strict_self_inclusion",
        "backend_identity_sha256",
    }

    @property
    def implicit_rhs_lower(self) -> tuple[float, ...]:
        """Compatibility-safe name for the ABI-v4 lower RHS slot."""

        return self.residual_lower

    @property
    def implicit_rhs_upper(self) -> tuple[float, ...]:
        """Compatibility-safe name for the ABI-v4 upper RHS slot."""

        return self.residual_upper

    def to_mapping(self) -> dict[str, Any]:
        return {field.name: getattr(self, field.name) for field in fields(self)}

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "TangentCertificate":
        _closed_keys(mapping, cls._FIELD_NAMES)
        tuple_fields = {
            "solution_lower",
            "solution_upper",
            "krawczyk_lower",
            "krawczyk_upper",
            "center",
            "residual_lower",
            "residual_upper",
            "preconditioner",
            "lower_margins",
            "upper_margins",
        }
        values = {
            name: tuple(mapping[name]) if name in tuple_fields else mapping[name]
            for name in cls._FIELD_NAMES
        }
        return cls(**values)

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.to_mapping())


def _validate_certificate_structure(
    request: TangentRequest | MixedVfRequest,
    certificate: TangentCertificate,
) -> None:
    n = request.dimension
    if certificate.request_sha256 != request.sha256():
        raise CertificateValidationError("REQUEST_DIGEST_MISMATCH")
    if certificate.precision_bits != PRECISION_BITS:
        raise CertificateValidationError("PRECISION_MISMATCH")
    if certificate.rounding_policy != ROUNDING_POLICY:
        raise CertificateValidationError("ROUNDING_POLICY_MISMATCH")
    if certificate.backend_schema != CERTIFICATE_SCHEMA:
        raise CertificateValidationError("BACKEND_SCHEMA_MISMATCH")
    _digest("backend_identity_sha256", certificate.backend_identity_sha256)

    for name in (
        "solution_lower",
        "solution_upper",
        "krawczyk_lower",
        "krawczyk_upper",
        "center",
        "residual_lower",
        "residual_upper",
        "lower_margins",
        "upper_margins",
    ):
        _finite_tuple(name, getattr(certificate, name), n)
    _finite_tuple("preconditioner", certificate.preconditioner, n * n)

    rho = float(certificate.rho_upper)
    if not math.isfinite(rho) or rho < 0.0 or rho >= 1.0:
        raise CertificateValidationError("KRAWCZYK_CONTRACTION_NOT_PROVED")
    if type(certificate.iterations) is not int or certificate.iterations < 1:
        raise CertificateValidationError("INVALID_ITERATION_COUNT")

    strict = all(
        outer_lo < inner_lo and inner_hi < outer_hi
        for outer_lo, inner_lo, inner_hi, outer_hi in zip(
            certificate.solution_lower,
            certificate.krawczyk_lower,
            certificate.krawczyk_upper,
            certificate.solution_upper,
        )
    )
    positive_margins = all(value > 0.0 for value in certificate.lower_margins) and all(
        value > 0.0 for value in certificate.upper_margins
    )
    if not certificate.strict_self_inclusion or not strict or not positive_margins:
        raise CertificateValidationError("KRAWCZYK_NOT_STRICT_INTERIOR")


def validate_tangent_certificate(
    request: TangentRequest,
    certificate: TangentCertificate,
) -> None:
    """Validate shape only; this does not admit a claim-bearing certificate."""

    _validate_certificate_structure(request, certificate)


def validate_mixed_vf_certificate(
    request: MixedVfRequest,
    certificate: TangentCertificate,
) -> None:
    """Validate shape only for an atomic mixed request."""

    _validate_certificate_structure(request, certificate)


__all__ = (
    "CERTIFICATE_SCHEMA",
    "CertificateValidationError",
    "LinearRequest",
    "MixedRhsRequest",
    "MixedVfRequest",
    "PRECISION_BITS",
    "ROUNDING_POLICY",
    "TangentCertificate",
    "TangentRequest",
    "validate_mixed_vf_certificate",
    "validate_tangent_certificate",
)
