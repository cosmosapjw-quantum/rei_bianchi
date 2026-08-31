"""Closed, reference-only certificate graph for the four evaluation sites.

The 45-byte payload defined here is an identifier, not a numerical
certificate.  Its SHA-256 field points at immutable certificate bytes held by
an external authority.  Admission therefore always requires an independently
supplied :class:`ImmutableAuthorityPin`; a payload cannot authenticate itself.

No parser in this module interprets the referenced numerical certificate.  In
particular, this module does not turn the current Rust thermal interval kernel
into a four-site replay ABI.  The admission token prevents accidental public
construction; it is not a hostile same-process capability boundary.  The pin
must come from the separately validated input-authority closure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
import hmac
import re
import struct
from typing import Final


CERTIFICATE_PAYLOAD_MAGIC: Final[bytes] = b"REICERT1"
CERTIFICATE_PAYLOAD_VERSION: Final[int] = 1
CERTIFICATE_PAYLOAD_SIZE: Final[int] = 45
_PAYLOAD_STRUCT: Final[struct.Struct] = struct.Struct(">BI32s")
_CANONICAL_SHA256 = re.compile(r"[0-9a-f]{64}").fullmatch


class CertificateGraphError(ValueError):
    """Fail-closed certificate graph error with a stable machine code."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        suffix = f": {detail}" if detail else ""
        super().__init__(f"{code}{suffix}")


class CertificateKind(IntEnum):
    """The only certificate families admitted by this reference graph."""

    POPULATION_IMPLICIT = 1
    THERMAL_IMPLICIT = 2


class CertificateSite(IntEnum):
    """Closed four-site MPRK22--SDIRK2 evaluation grammar."""

    POPULATION_T0 = 1
    POPULATION_T1_PREDICTOR = 2
    THERMAL_TGAMMA = 3
    THERMAL_T1_FINAL = 4


@dataclass(frozen=True)
class ImmutableAuthorityPin:
    """An immutable digest supplied outside the reference payload."""

    authority_id: str
    sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.authority_id, str) or not self.authority_id.strip():
            raise CertificateGraphError(
                "CERTIFICATE_AUTHORITY_PIN_INVALID", "authority_id must be non-empty"
            )
        if not isinstance(self.sha256, str) or _CANONICAL_SHA256(self.sha256) is None:
            raise CertificateGraphError(
                "CERTIFICATE_AUTHORITY_PIN_INVALID",
                "sha256 must be 64 lowercase hexadecimal characters",
            )


_AUTHORITY_ADMISSION_TOKEN = object()


@dataclass(frozen=True)
class CertificateReference:
    """An admitted reference; construction is restricted to the decoder."""

    site: CertificateSite
    kind: CertificateKind
    authority_id: str
    authority_sha256: str
    payload: bytes
    _admission: object = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self._admission is not _AUTHORITY_ADMISSION_TOKEN:
            raise CertificateGraphError(
                "CERTIFICATE_REFERENCE_NOT_ADMITTED",
                "use decode_certificate_reference with an external authority pin",
            )


def encode_certificate_reference(
    *,
    site: CertificateSite,
    kind: CertificateKind,
    authority: ImmutableAuthorityPin,
) -> bytes:
    """Encode the fixed-width reference for externally pinned certificate bytes."""

    if not isinstance(authority, ImmutableAuthorityPin):
        raise CertificateGraphError(
            "CERTIFICATE_AUTHORITY_PIN_INVALID", "external immutable pin required"
        )
    try:
        normalized_site = CertificateSite(site)
    except (TypeError, ValueError) as exc:
        raise CertificateGraphError("CERTIFICATE_SITE_INVALID") from exc
    try:
        normalized_kind = CertificateKind(kind)
    except (TypeError, ValueError) as exc:
        raise CertificateGraphError("CERTIFICATE_KIND_INVALID") from exc
    payload = CERTIFICATE_PAYLOAD_MAGIC + _PAYLOAD_STRUCT.pack(
        int(normalized_kind), int(normalized_site), bytes.fromhex(authority.sha256)
    )
    if len(payload) != CERTIFICATE_PAYLOAD_SIZE:  # defensive schema invariant
        raise AssertionError("internal certificate payload layout drift")
    return payload


def decode_certificate_reference(
    payload: bytes, *, authority: ImmutableAuthorityPin
) -> CertificateReference:
    """Admit a payload only when its digest equals an external immutable pin."""

    if not isinstance(authority, ImmutableAuthorityPin):
        raise CertificateGraphError(
            "CERTIFICATE_AUTHORITY_PIN_INVALID", "external immutable pin required"
        )
    if not isinstance(payload, bytes) or len(payload) != CERTIFICATE_PAYLOAD_SIZE:
        raise CertificateGraphError(
            "CERTIFICATE_PAYLOAD_SIZE_INVALID",
            f"expected {CERTIFICATE_PAYLOAD_SIZE} bytes",
        )
    if payload[: len(CERTIFICATE_PAYLOAD_MAGIC)] != CERTIFICATE_PAYLOAD_MAGIC:
        raise CertificateGraphError("CERTIFICATE_PAYLOAD_MAGIC_INVALID")
    kind_code, site_code, digest = _PAYLOAD_STRUCT.unpack(
        payload[len(CERTIFICATE_PAYLOAD_MAGIC) :]
    )
    try:
        kind = CertificateKind(kind_code)
    except ValueError as exc:
        raise CertificateGraphError("CERTIFICATE_KIND_INVALID") from exc
    try:
        site = CertificateSite(site_code)
    except ValueError as exc:
        raise CertificateGraphError("CERTIFICATE_SITE_INVALID") from exc
    digest_hex = digest.hex()
    if not hmac.compare_digest(digest_hex, authority.sha256):
        raise CertificateGraphError(
            "CERTIFICATE_AUTHORITY_MISMATCH",
            "payload reference does not match the external immutable pin",
        )
    return CertificateReference(
        site=site,
        kind=kind,
        authority_id=authority.authority_id,
        authority_sha256=authority.sha256,
        payload=payload,
        _admission=_AUTHORITY_ADMISSION_TOKEN,
    )


@dataclass(frozen=True)
class ReferenceCertificateNode:
    """One node in the closed graph; parents are site identities, not aliases."""

    reference: CertificateReference
    parents: tuple[CertificateSite, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reference, CertificateReference):
            raise CertificateGraphError("CERTIFICATE_GRAPH_REFERENCE_INVALID")
        try:
            normalized = tuple(CertificateSite(parent) for parent in self.parents)
        except (TypeError, ValueError) as exc:
            raise CertificateGraphError("CERTIFICATE_GRAPH_EDGE_INVALID") from exc
        object.__setattr__(self, "parents", normalized)


_EXPECTED_PARENTS: Final[dict[CertificateSite, tuple[CertificateSite, ...]]] = {
    CertificateSite.POPULATION_T0: (),
    CertificateSite.POPULATION_T1_PREDICTOR: (CertificateSite.POPULATION_T0,),
    CertificateSite.THERMAL_TGAMMA: (
        CertificateSite.POPULATION_T0,
        CertificateSite.POPULATION_T1_PREDICTOR,
    ),
    CertificateSite.THERMAL_T1_FINAL: (
        CertificateSite.POPULATION_T0,
        CertificateSite.POPULATION_T1_PREDICTOR,
        CertificateSite.THERMAL_TGAMMA,
    ),
}

_EXPECTED_KIND: Final[dict[CertificateSite, CertificateKind]] = {
    CertificateSite.POPULATION_T0: CertificateKind.POPULATION_IMPLICIT,
    CertificateSite.POPULATION_T1_PREDICTOR: CertificateKind.POPULATION_IMPLICIT,
    CertificateSite.THERMAL_TGAMMA: CertificateKind.THERMAL_IMPLICIT,
    CertificateSite.THERMAL_T1_FINAL: CertificateKind.THERMAL_IMPLICIT,
}


@dataclass(frozen=True)
class ReferenceCertificateGraph:
    """Exactly the four source sites and their declared dependency edges."""

    nodes: tuple[ReferenceCertificateNode, ...]

    def __post_init__(self) -> None:
        nodes = tuple(self.nodes)
        expected_sites = tuple(CertificateSite)
        observed_sites = tuple(node.reference.site for node in nodes)
        if observed_sites != expected_sites:
            raise CertificateGraphError(
                "CERTIFICATE_GRAPH_SITE_SET_INVALID",
                "graph must contain each canonical site exactly once and in order",
            )
        for node in nodes:
            site = node.reference.site
            if node.parents != _EXPECTED_PARENTS[site]:
                raise CertificateGraphError(
                    "CERTIFICATE_GRAPH_EDGE_INVALID", f"noncanonical parents for {site.name}"
                )
            if node.reference.kind is not _EXPECTED_KIND[site]:
                raise CertificateGraphError(
                    "CERTIFICATE_GRAPH_KIND_INVALID", f"wrong certificate kind for {site.name}"
                )
        object.__setattr__(self, "nodes", nodes)

    @property
    def sites(self) -> tuple[CertificateSite, ...]:
        return tuple(node.reference.site for node in self.nodes)

    @property
    def reference_only(self) -> bool:
        """Always true: raw numerical certificate bytes are deliberately absent."""

        return True


__all__ = [
    "CERTIFICATE_PAYLOAD_MAGIC",
    "CERTIFICATE_PAYLOAD_SIZE",
    "CERTIFICATE_PAYLOAD_VERSION",
    "CertificateGraphError",
    "CertificateKind",
    "CertificateReference",
    "CertificateSite",
    "ImmutableAuthorityPin",
    "ReferenceCertificateGraph",
    "ReferenceCertificateNode",
    "decode_certificate_reference",
    "encode_certificate_reference",
]
