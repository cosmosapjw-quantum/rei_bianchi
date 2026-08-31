from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

from rei_bianchi.certificate_graph import (
    CERTIFICATE_PAYLOAD_SIZE,
    CertificateGraphError,
    CertificateKind,
    CertificateSite,
    ImmutableAuthorityPin,
    ReferenceCertificateGraph,
    ReferenceCertificateNode,
    decode_certificate_reference,
    encode_certificate_reference,
)
from rei_bianchi.source_bound_mprk_sdirk_operator import (
    RUST_THERMAL_REPLAY_ABI_MISSING,
    RustThermalReplayAbiMissing,
    SourceBoundMprkSdirkOperator,
)


def pin(label: str) -> ImmutableAuthorityPin:
    return ImmutableAuthorityPin(
        authority_id=f"immutable:{label}",
        sha256=hashlib.sha256(label.encode("ascii")).hexdigest(),
    )


def reference(site: CertificateSite):
    kind = (
        CertificateKind.POPULATION_IMPLICIT
        if site in (CertificateSite.POPULATION_T0, CertificateSite.POPULATION_T1_PREDICTOR)
        else CertificateKind.THERMAL_IMPLICIT
    )
    authority = pin(site.name)
    payload = encode_certificate_reference(site=site, kind=kind, authority=authority)
    return decode_certificate_reference(payload, authority=authority)


def valid_graph() -> ReferenceCertificateGraph:
    p0 = CertificateSite.POPULATION_T0
    p1 = CertificateSite.POPULATION_T1_PREDICTOR
    tg = CertificateSite.THERMAL_TGAMMA
    t1 = CertificateSite.THERMAL_T1_FINAL
    return ReferenceCertificateGraph(
        (
            ReferenceCertificateNode(reference(p0), ()),
            ReferenceCertificateNode(reference(p1), (p0,)),
            ReferenceCertificateNode(reference(tg), (p0, p1)),
            ReferenceCertificateNode(reference(t1), (p0, p1, tg)),
        )
    )


class CertificateReferenceTests(unittest.TestCase):
    def test_payload_is_exactly_45_bytes(self):
        payload = encode_certificate_reference(
            site=CertificateSite.POPULATION_T0,
            kind=CertificateKind.POPULATION_IMPLICIT,
            authority=pin("p0"),
        )
        self.assertEqual(len(payload), CERTIFICATE_PAYLOAD_SIZE)
        self.assertEqual(CERTIFICATE_PAYLOAD_SIZE, 45)

    def test_reference_round_trip_requires_external_pin(self):
        authority = pin("p0")
        payload = encode_certificate_reference(
            site=CertificateSite.POPULATION_T0,
            kind=CertificateKind.POPULATION_IMPLICIT,
            authority=authority,
        )
        got = decode_certificate_reference(payload, authority=authority)
        self.assertEqual(got.site, CertificateSite.POPULATION_T0)
        self.assertEqual(got.kind, CertificateKind.POPULATION_IMPLICIT)
        self.assertEqual(got.authority_id, authority.authority_id)
        self.assertEqual(got.payload, payload)

    def test_wrong_external_authority_is_rejected(self):
        payload = encode_certificate_reference(
            site=CertificateSite.POPULATION_T0,
            kind=CertificateKind.POPULATION_IMPLICIT,
            authority=pin("p0"),
        )
        with self.assertRaisesRegex(CertificateGraphError, "CERTIFICATE_AUTHORITY_MISMATCH"):
            decode_certificate_reference(payload, authority=pin("different"))

    def test_authority_digest_must_be_canonical_lowercase_sha256(self):
        with self.assertRaisesRegex(CertificateGraphError, "CERTIFICATE_AUTHORITY_PIN_INVALID"):
            ImmutableAuthorityPin(authority_id="immutable:x", sha256="A" * 64)

    def test_wrong_magic_or_embedded_version_is_rejected(self):
        authority = pin("p0")
        original = encode_certificate_reference(
            site=CertificateSite.POPULATION_T0,
            kind=CertificateKind.POPULATION_IMPLICIT,
            authority=authority,
        )
        for offset in (0, 7):
            payload = bytearray(original)
            payload[offset] ^= 1
            with self.subTest(offset=offset):
                with self.assertRaisesRegex(
                    CertificateGraphError, "CERTIFICATE_PAYLOAD_MAGIC_INVALID"
                ):
                    decode_certificate_reference(bytes(payload), authority=authority)

    def test_unknown_kind_is_rejected(self):
        authority = pin("p0")
        payload = bytearray(
            encode_certificate_reference(
                site=CertificateSite.POPULATION_T0,
                kind=CertificateKind.POPULATION_IMPLICIT,
                authority=authority,
            )
        )
        payload[8] = 255
        with self.assertRaisesRegex(CertificateGraphError, "CERTIFICATE_KIND_INVALID"):
            decode_certificate_reference(bytes(payload), authority=authority)

    def test_wrong_size_and_trailing_bytes_are_rejected(self):
        authority = pin("p0")
        payload = encode_certificate_reference(
            site=CertificateSite.POPULATION_T0,
            kind=CertificateKind.POPULATION_IMPLICIT,
            authority=authority,
        )
        for malformed in (payload[:-1], payload + b"x"):
            with self.subTest(size=len(malformed)):
                with self.assertRaisesRegex(CertificateGraphError, "CERTIFICATE_PAYLOAD_SIZE_INVALID"):
                    decode_certificate_reference(malformed, authority=authority)

    def test_unknown_site_is_rejected(self):
        authority = pin("p0")
        payload = bytearray(
            encode_certificate_reference(
                site=CertificateSite.POPULATION_T0,
                kind=CertificateKind.POPULATION_IMPLICIT,
                authority=authority,
            )
        )
        payload[9:13] = (99).to_bytes(4, "big")
        with self.assertRaisesRegex(CertificateGraphError, "CERTIFICATE_SITE_INVALID"):
            decode_certificate_reference(bytes(payload), authority=authority)


class CertificateGraphTests(unittest.TestCase):
    def test_closed_four_site_graph_is_accepted(self):
        graph = valid_graph()
        self.assertEqual(graph.sites, tuple(CertificateSite))
        self.assertTrue(graph.reference_only)

    def test_graph_requires_all_four_sites(self):
        nodes = valid_graph().nodes[:-1]
        with self.assertRaisesRegex(CertificateGraphError, "CERTIFICATE_GRAPH_SITE_SET_INVALID"):
            ReferenceCertificateGraph(nodes)

    def test_graph_rejects_duplicate_site(self):
        nodes = list(valid_graph().nodes)
        nodes[-1] = nodes[0]
        with self.assertRaisesRegex(CertificateGraphError, "CERTIFICATE_GRAPH_SITE_SET_INVALID"):
            ReferenceCertificateGraph(tuple(nodes))

    def test_graph_rejects_noncanonical_parent_edges(self):
        nodes = list(valid_graph().nodes)
        nodes[-1] = ReferenceCertificateNode(nodes[-1].reference, (CertificateSite.THERMAL_TGAMMA,))
        with self.assertRaisesRegex(CertificateGraphError, "CERTIFICATE_GRAPH_EDGE_INVALID"):
            ReferenceCertificateGraph(tuple(nodes))

    def test_graph_rejects_kind_site_mismatch(self):
        authority = pin("wrong-kind")
        payload = encode_certificate_reference(
            site=CertificateSite.THERMAL_T1_FINAL,
            kind=CertificateKind.POPULATION_IMPLICIT,
            authority=authority,
        )
        wrong = decode_certificate_reference(payload, authority=authority)
        nodes = list(valid_graph().nodes)
        nodes[-1] = ReferenceCertificateNode(wrong, nodes[-1].parents)
        with self.assertRaisesRegex(CertificateGraphError, "CERTIFICATE_GRAPH_KIND_INVALID"):
            ReferenceCertificateGraph(tuple(nodes))

    def test_operator_fails_typed_when_real_four_site_abi_is_absent(self):
        for constructor in (
            lambda: SourceBoundMprkSdirkOperator.from_repo(Path.cwd()),
            lambda: SourceBoundMprkSdirkOperator(Path.cwd()),
        ):
            with self.subTest(constructor=constructor):
                with self.assertRaises(RustThermalReplayAbiMissing) as caught:
                    constructor()
                self.assertEqual(caught.exception.code, RUST_THERMAL_REPLAY_ABI_MISSING)
                self.assertIn(RUST_THERMAL_REPLAY_ABI_MISSING, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
