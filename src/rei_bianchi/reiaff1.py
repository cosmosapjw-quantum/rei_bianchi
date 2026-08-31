"""Strict restart envelope for dependency-aware affine certificate state."""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping


REIAFF1_MAGIC = b"REIAFF1\x00"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_BLOCK_ORDER = (
    "OWNER_REGISTRY",
    "AFFINE_TERMS",
    "MIXED_TERMS",
    "ASYMMETRIC_REMAINDERS",
    "CERTIFICATE_PAYLOADS",
    "CERTIFICATE_GRAPH",
    "LEGACY_NORMALIZATION",
)


class Reiaff1Error(ValueError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        suffix = f": {detail}" if detail else ""
        super().__init__(f"{code}{suffix}")


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise Reiaff1Error("REIAFF1_FIELD_INVALID", field)
    return value


def _require_sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise Reiaff1Error("REIAFF1_SHA256_INVALID", field)
    return value


def _closed_mapping(value: object, keys: set[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise Reiaff1Error("REIAFF1_BLOCK_VALUE_INVALID", field)
    return value


def _closed_record_list(
    value: object, keys: set[str], field: str
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise Reiaff1Error("REIAFF1_BLOCK_VALUE_INVALID", field)
    records: list[dict[str, Any]] = []
    for item in value:
        records.append(_closed_mapping(item, keys, field))
    return records


def _decode_canonical_base64(value: object, field: str) -> bytes:
    if not isinstance(value, str):
        raise Reiaff1Error("REIAFF1_BLOCK_VALUE_INVALID", field)
    try:
        decoded = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise Reiaff1Error("REIAFF1_BASE64_INVALID", field) from exc
    if base64.b64encode(decoded).decode("ascii") != value:
        raise Reiaff1Error("REIAFF1_BASE64_NONCANONICAL", field)
    return decoded


@dataclass(frozen=True)
class OwnerRecord:
    owner_id: str
    owner_kind: str

    def __post_init__(self) -> None:
        _require_text(self.owner_id, "owner_id")
        _require_text(self.owner_kind, "owner_kind")


@dataclass(frozen=True)
class OwnerAlias:
    alias_id: str
    owner_id: str

    def __post_init__(self) -> None:
        _require_text(self.alias_id, "alias_id")
        _require_text(self.owner_id, "owner_id")


@dataclass(frozen=True)
class OwnerRegistry:
    owners: tuple[OwnerRecord, ...]
    aliases: tuple[OwnerAlias, ...]

    def __post_init__(self) -> None:
        owners = tuple(self.owners)
        aliases = tuple(self.aliases)
        if not owners:
            raise Reiaff1Error("REIAFF1_OWNER_REGISTRY_EMPTY")
        owner_ids = [item.owner_id for item in owners]
        alias_ids = [item.alias_id for item in aliases]
        if len(owner_ids) != len(set(owner_ids)) or len(alias_ids) != len(set(alias_ids)):
            raise Reiaff1Error("REIAFF1_OWNER_ID_DUPLICATE")
        if set(owner_ids) & set(alias_ids):
            raise Reiaff1Error("REIAFF1_OWNER_ALIAS_COLLISION")
        if any(item.owner_id not in set(owner_ids) for item in aliases):
            raise Reiaff1Error("REIAFF1_GHOST_OWNER_ALIAS")
        if owners != tuple(sorted(owners, key=lambda item: item.owner_id)) or aliases != tuple(
            sorted(aliases, key=lambda item: item.alias_id)
        ):
            raise Reiaff1Error("REIAFF1_RECORD_ORDER_INVALID", "OWNER_REGISTRY")
        object.__setattr__(self, "owners", owners)
        object.__setattr__(self, "aliases", aliases)


@dataclass(frozen=True)
class AffineTerm:
    component: str
    owner_id: str
    coefficient: str

    def __post_init__(self) -> None:
        _require_text(self.component, "affine.component")
        _require_text(self.owner_id, "affine.owner_id")
        _require_text(self.coefficient, "affine.coefficient")


@dataclass(frozen=True)
class MixedTerm:
    component: str
    left_owner_id: str
    right_owner_id: str
    coefficient: str

    def __post_init__(self) -> None:
        _require_text(self.component, "mixed.component")
        _require_text(self.left_owner_id, "mixed.left_owner_id")
        _require_text(self.right_owner_id, "mixed.right_owner_id")
        _require_text(self.coefficient, "mixed.coefficient")


@dataclass(frozen=True)
class AsymmetricRemainder:
    component: str
    lower: str
    upper: str

    def __post_init__(self) -> None:
        _require_text(self.component, "remainder.component")
        _require_text(self.lower, "remainder.lower")
        _require_text(self.upper, "remainder.upper")


@dataclass(frozen=True)
class CertificatePayload:
    certificate_id: str
    site: str
    certificate_kind: str
    payload: bytes
    payload_sha256: str
    external_receipt_sha256: str

    def __post_init__(self) -> None:
        _require_text(self.certificate_id, "certificate_id")
        _require_text(self.site, "site")
        _require_text(self.certificate_kind, "certificate_kind")
        if not isinstance(self.payload, bytes):
            raise Reiaff1Error("REIAFF1_CERTIFICATE_PAYLOAD_INVALID")
        _require_sha256(self.payload_sha256, "payload_sha256")
        _require_sha256(self.external_receipt_sha256, "external_receipt_sha256")
        if hashlib.sha256(self.payload).hexdigest() != self.payload_sha256:
            raise Reiaff1Error("REIAFF1_CERTIFICATE_DIGEST_MISMATCH")


@dataclass(frozen=True)
class CertificateNode:
    certificate_id: str
    parents: tuple[str, ...]


@dataclass(frozen=True)
class CertificateGraph:
    nodes: tuple[CertificateNode, ...]


@dataclass(frozen=True)
class LegacyNormalization:
    algorithm: str
    source_sha256: str
    normalizer_sha256: str
    normalized_sha256: str

    def __post_init__(self) -> None:
        if self.algorithm != "rei-legacy-normalization/v1":
            raise Reiaff1Error("REIAFF1_LEGACY_NORMALIZATION_ALGORITHM_INVALID")
        _require_sha256(self.source_sha256, "legacy.source_sha256")
        _require_sha256(self.normalizer_sha256, "legacy.normalizer_sha256")
        _require_sha256(self.normalized_sha256, "legacy.normalized_sha256")


@dataclass(frozen=True)
class RestartState:
    run_id: str
    parent_state_sha256: str
    producer_sha256: str
    registry: OwnerRegistry
    affine_terms: tuple[AffineTerm, ...]
    mixed_terms: tuple[MixedTerm, ...]
    asymmetric_remainders: tuple[AsymmetricRemainder, ...]
    certificates: tuple[CertificatePayload, ...]
    certificate_graph: CertificateGraph
    legacy_normalization: LegacyNormalization

    def __post_init__(self) -> None:
        _require_text(self.run_id, "run_id")
        _require_sha256(self.parent_state_sha256, "parent_state_sha256")
        _require_sha256(self.producer_sha256, "producer_sha256")
        admitted_owners = {item.owner_id for item in self.registry.owners} | {
            item.alias_id for item in self.registry.aliases
        }
        if any(item.owner_id not in admitted_owners for item in self.affine_terms):
            raise Reiaff1Error("REIAFF1_AFFINE_OWNER_NOT_REGISTERED")
        if any(
            item.left_owner_id not in admitted_owners
            or item.right_owner_id not in admitted_owners
            for item in self.mixed_terms
        ):
            raise Reiaff1Error("REIAFF1_MIXED_OWNER_NOT_REGISTERED")
        ordered_groups = (
            (
                self.affine_terms,
                lambda item: (item.component, item.owner_id),
                "AFFINE_TERMS",
            ),
            (
                self.mixed_terms,
                lambda item: (
                    item.component,
                    item.left_owner_id,
                    item.right_owner_id,
                ),
                "MIXED_TERMS",
            ),
            (
                self.asymmetric_remainders,
                lambda item: item.component,
                "ASYMMETRIC_REMAINDERS",
            ),
            (
                self.certificates,
                lambda item: item.certificate_id,
                "CERTIFICATE_PAYLOADS",
            ),
            (
                self.certificate_graph.nodes,
                lambda item: item.certificate_id,
                "CERTIFICATE_GRAPH",
            ),
        )
        for records, key, name in ordered_groups:
            keys = [key(item) for item in records]
            if keys != sorted(keys) or len(keys) != len(set(keys)):
                raise Reiaff1Error("REIAFF1_RECORD_ORDER_INVALID", name)
        certificate_ids = [item.certificate_id for item in self.certificates]
        graph_ids = [item.certificate_id for item in self.certificate_graph.nodes]
        if len(certificate_ids) != len(set(certificate_ids)) or len(graph_ids) != len(
            set(graph_ids)
        ):
            raise Reiaff1Error("REIAFF1_CERTIFICATE_ID_DUPLICATE")
        if set(certificate_ids) != set(graph_ids):
            raise Reiaff1Error("REIAFF1_CERTIFICATE_GRAPH_PAYLOAD_MISMATCH")
        graph_id_set = set(graph_ids)
        if any(
            parent not in graph_id_set or parent == node.certificate_id
            for node in self.certificate_graph.nodes
            for parent in node.parents
        ):
            raise Reiaff1Error("REIAFF1_CERTIFICATE_GRAPH_EDGE_INVALID")
        if any(
            node.parents != tuple(sorted(node.parents))
            or len(node.parents) != len(set(node.parents))
            for node in self.certificate_graph.nodes
        ):
            raise Reiaff1Error("REIAFF1_CERTIFICATE_GRAPH_EDGE_INVALID")
        children = {identifier: [] for identifier in graph_ids}
        indegree = {identifier: 0 for identifier in graph_ids}
        for node in self.certificate_graph.nodes:
            for parent in node.parents:
                children[parent].append(node.certificate_id)
                indegree[node.certificate_id] += 1
        queue = sorted(identifier for identifier, degree in indegree.items() if degree == 0)
        visited = 0
        while queue:
            current = queue.pop(0)
            visited += 1
            for child in sorted(children[current]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
                    queue.sort()
        if visited != len(graph_ids):
            raise Reiaff1Error("REIAFF1_CERTIFICATE_GRAPH_CYCLE")


def encode_reiaff1(state: RestartState) -> bytes:
    blocks: list[dict[str, Any]] = [
        {
            "kind": "OWNER_REGISTRY",
            "value": {
                "owners": [
                    {"owner_id": item.owner_id, "owner_kind": item.owner_kind}
                    for item in state.registry.owners
                ],
                "aliases": [
                    {"alias_id": item.alias_id, "owner_id": item.owner_id}
                    for item in state.registry.aliases
                ],
            },
        },
        {
            "kind": "AFFINE_TERMS",
            "value": [
                {
                    "component": item.component,
                    "owner_id": item.owner_id,
                    "coefficient": item.coefficient,
                }
                for item in state.affine_terms
            ],
        },
        {
            "kind": "MIXED_TERMS",
            "value": [
                {
                    "component": item.component,
                    "left_owner_id": item.left_owner_id,
                    "right_owner_id": item.right_owner_id,
                    "coefficient": item.coefficient,
                }
                for item in state.mixed_terms
            ],
        },
        {
            "kind": "ASYMMETRIC_REMAINDERS",
            "value": [
                {
                    "component": item.component,
                    "lower": item.lower,
                    "upper": item.upper,
                }
                for item in state.asymmetric_remainders
            ],
        },
        {
            "kind": "CERTIFICATE_PAYLOADS",
            "value": [
                {
                    "certificate_id": item.certificate_id,
                    "site": item.site,
                    "certificate_kind": item.certificate_kind,
                    "payload_base64": base64.b64encode(item.payload).decode("ascii"),
                    "payload_sha256": item.payload_sha256,
                    "external_receipt_sha256": item.external_receipt_sha256,
                }
                for item in state.certificates
            ],
        },
        {
            "kind": "CERTIFICATE_GRAPH",
            "value": {
                "nodes": [
                    {
                        "certificate_id": item.certificate_id,
                        "parents": list(item.parents),
                    }
                    for item in state.certificate_graph.nodes
                ]
            },
        },
        {
            "kind": "LEGACY_NORMALIZATION",
            "value": {
                "algorithm": state.legacy_normalization.algorithm,
                "source_sha256": state.legacy_normalization.source_sha256,
                "normalizer_sha256": state.legacy_normalization.normalizer_sha256,
                "normalized_sha256": state.legacy_normalization.normalized_sha256,
            },
        },
    ]
    envelope = {
        "schema": "REIAFF1",
        "metadata": {
            "run_id": state.run_id,
            "parent_state_sha256": state.parent_state_sha256,
            "producer_sha256": state.producer_sha256,
        },
        "blocks": blocks,
    }
    return REIAFF1_MAGIC + _canonical_json(envelope)


def decode_reiaff1(
    data: bytes,
    *,
    expected_sha256: str,
    expected_certificate_receipts: Mapping[str, str] | None = None,
) -> RestartState:
    if not isinstance(expected_sha256, str) or _SHA256.fullmatch(expected_sha256) is None:
        raise Reiaff1Error("REIAFF1_EXTERNAL_DIGEST_INVALID")
    if not isinstance(data, bytes):
        raise Reiaff1Error("REIAFF1_BYTES_INVALID")
    observed_sha256 = hashlib.sha256(data).hexdigest()
    if observed_sha256 != expected_sha256:
        raise Reiaff1Error("REIAFF1_EXTERNAL_DIGEST_MISMATCH")
    if not data.startswith(REIAFF1_MAGIC):
        raise Reiaff1Error("REIAFF1_MAGIC_INVALID")
    body = data[len(REIAFF1_MAGIC) :]
    try:
        envelope = json.loads(body.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Reiaff1Error("REIAFF1_ENVELOPE_INVALID", str(exc)) from exc
    if _canonical_json(envelope) != body:
        raise Reiaff1Error("REIAFF1_NONCANONICAL")
    if not isinstance(envelope, dict) or set(envelope) != {
        "schema",
        "metadata",
        "blocks",
    }:
        raise Reiaff1Error("REIAFF1_ENVELOPE_KEYS_INVALID")
    if envelope["schema"] != "REIAFF1":
        raise Reiaff1Error("REIAFF1_SCHEMA_INVALID")
    metadata = envelope["metadata"]
    if not isinstance(metadata, dict) or set(metadata) != {
        "run_id",
        "parent_state_sha256",
        "producer_sha256",
    }:
        raise Reiaff1Error("REIAFF1_METADATA_INVALID")
    blocks = envelope["blocks"]
    if (
        not isinstance(blocks, list)
        or len(blocks) != len(_BLOCK_ORDER)
        or any(
            not isinstance(block, dict) or set(block) != {"kind", "value"}
            for block in blocks
        )
        or tuple(block["kind"] for block in blocks) != _BLOCK_ORDER
    ):
        raise Reiaff1Error("REIAFF1_BLOCK_ORDER_INVALID")
    block_values = {block["kind"]: block["value"] for block in blocks}
    registry_value = _closed_mapping(
        block_values["OWNER_REGISTRY"], {"owners", "aliases"}, "OWNER_REGISTRY"
    )
    owner_values = _closed_record_list(
        registry_value["owners"], {"owner_id", "owner_kind"}, "OWNER_REGISTRY.owners"
    )
    alias_values = _closed_record_list(
        registry_value["aliases"], {"alias_id", "owner_id"}, "OWNER_REGISTRY.aliases"
    )
    affine_values = _closed_record_list(
        block_values["AFFINE_TERMS"],
        {"component", "owner_id", "coefficient"},
        "AFFINE_TERMS",
    )
    mixed_values = _closed_record_list(
        block_values["MIXED_TERMS"],
        {
            "component",
            "left_owner_id",
            "right_owner_id",
            "coefficient",
        },
        "MIXED_TERMS",
    )
    remainder_values = _closed_record_list(
        block_values["ASYMMETRIC_REMAINDERS"],
        {"component", "lower", "upper"},
        "ASYMMETRIC_REMAINDERS",
    )
    certificate_values = _closed_record_list(
        block_values["CERTIFICATE_PAYLOADS"],
        {
            "certificate_id",
            "site",
            "certificate_kind",
            "payload_base64",
            "payload_sha256",
            "external_receipt_sha256",
        },
        "CERTIFICATE_PAYLOADS",
    )
    graph_value = _closed_mapping(
        block_values["CERTIFICATE_GRAPH"], {"nodes"}, "CERTIFICATE_GRAPH"
    )
    graph_node_values = _closed_record_list(
        graph_value["nodes"], {"certificate_id", "parents"}, "CERTIFICATE_GRAPH.nodes"
    )
    if any(not isinstance(item["parents"], list) for item in graph_node_values):
        raise Reiaff1Error("REIAFF1_BLOCK_VALUE_INVALID", "CERTIFICATE_GRAPH.parents")
    legacy_value = _closed_mapping(
        block_values["LEGACY_NORMALIZATION"],
        {"algorithm", "source_sha256", "normalizer_sha256", "normalized_sha256"},
        "LEGACY_NORMALIZATION",
    )
    registry = OwnerRegistry(
        owners=tuple(OwnerRecord(**item) for item in owner_values),
        aliases=tuple(OwnerAlias(**item) for item in alias_values),
    )
    certificates = tuple(
        CertificatePayload(
            certificate_id=item["certificate_id"],
            site=item["site"],
            certificate_kind=item["certificate_kind"],
            payload=_decode_canonical_base64(
                item["payload_base64"], "CERTIFICATE_PAYLOADS.payload_base64"
            ),
            payload_sha256=item["payload_sha256"],
            external_receipt_sha256=item["external_receipt_sha256"],
        )
        for item in certificate_values
    )
    if not isinstance(expected_certificate_receipts, Mapping):
        raise Reiaff1Error("REIAFF1_EXTERNAL_RECEIPT_PINS_REQUIRED")
    receipt_pins = dict(expected_certificate_receipts)
    certificate_ids = {item.certificate_id for item in certificates}
    if set(receipt_pins) != certificate_ids:
        raise Reiaff1Error("REIAFF1_EXTERNAL_RECEIPT_PIN_SET_MISMATCH")
    for certificate in certificates:
        _require_sha256(
            receipt_pins[certificate.certificate_id],
            f"external receipt {certificate.certificate_id}",
        )
        if receipt_pins[certificate.certificate_id] != certificate.external_receipt_sha256:
            raise Reiaff1Error("REIAFF1_EXTERNAL_RECEIPT_DIGEST_MISMATCH")
    return RestartState(
        run_id=metadata["run_id"],
        parent_state_sha256=metadata["parent_state_sha256"],
        producer_sha256=metadata["producer_sha256"],
        registry=registry,
        affine_terms=tuple(AffineTerm(**item) for item in affine_values),
        mixed_terms=tuple(MixedTerm(**item) for item in mixed_values),
        asymmetric_remainders=tuple(
            AsymmetricRemainder(**item) for item in remainder_values
        ),
        certificates=certificates,
        certificate_graph=CertificateGraph(
            nodes=tuple(
                CertificateNode(item["certificate_id"], tuple(item["parents"]))
                for item in graph_node_values
            )
        ),
        legacy_normalization=LegacyNormalization(**legacy_value),
    )


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


__all__ = [
    "AffineTerm",
    "AsymmetricRemainder",
    "CertificateGraph",
    "CertificateNode",
    "CertificatePayload",
    "LegacyNormalization",
    "MixedTerm",
    "OwnerAlias",
    "OwnerRecord",
    "OwnerRegistry",
    "REIAFF1_MAGIC",
    "Reiaff1Error",
    "RestartState",
    "decode_reiaff1",
    "encode_reiaff1",
]
