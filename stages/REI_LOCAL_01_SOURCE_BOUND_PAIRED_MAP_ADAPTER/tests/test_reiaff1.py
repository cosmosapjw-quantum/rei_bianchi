from __future__ import annotations

import base64
import hashlib
import json
import unittest

from rei_bianchi.reiaff1 import (
    AffineTerm,
    AsymmetricRemainder,
    CertificateGraph,
    CertificateNode,
    CertificatePayload,
    LegacyNormalization,
    MixedTerm,
    OwnerAlias,
    OwnerRecord,
    OwnerRegistry,
    RestartState,
    decode_reiaff1,
    encode_reiaff1,
)


ZERO_SHA = "0" * 64
ONE_SHA = "1" * 64
TWO_SHA = "2" * 64
MAGIC = b"REIAFF1\x00"


def _state() -> RestartState:
    certificate = b"native-certificate-bytes"
    return RestartState(
        run_id="node-38382-red",
        parent_state_sha256=ZERO_SHA,
        producer_sha256=ONE_SHA,
        registry=OwnerRegistry(
            owners=(
                OwnerRecord("parent.x", "PARENT_STATE"),
                OwnerRecord("site.t0", "POPULATION_T0"),
            ),
            aliases=(OwnerAlias("shared.parent.x", "parent.x"),),
        ),
        affine_terms=(AffineTerm("x_hii", "parent.x", "0x1.0p-4"),),
        mixed_terms=(
            MixedTerm("x_heiii", "parent.x", "site.t0", "-0x1.0p-9"),
        ),
        asymmetric_remainders=(
            AsymmetricRemainder("x_heiii", "-0x1.0p-30", "0x1.8p-30"),
        ),
        certificates=(
            CertificatePayload(
                "thermal.tgamma",
                "thermal_tgamma",
                "THERMAL_IMPLICIT",
                certificate,
                hashlib.sha256(certificate).hexdigest(),
                TWO_SHA,
            ),
        ),
        certificate_graph=CertificateGraph(
            nodes=(CertificateNode("thermal.tgamma", ()),)
        ),
        legacy_normalization=LegacyNormalization(
            "rei-legacy-normalization/v1", TWO_SHA, ONE_SHA, ZERO_SHA
        ),
    )


def _rewrite(encoded: bytes, mutate: object) -> bytes:
    envelope = json.loads(encoded[len(MAGIC) :].decode("ascii"))
    mutate(envelope)  # type: ignore[operator]
    return MAGIC + json.dumps(
        envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _decode_pinned(encoded: bytes) -> RestartState:
    return decode_reiaff1(
        encoded,
        expected_sha256=hashlib.sha256(encoded).hexdigest(),
        expected_certificate_receipts={"thermal.tgamma": TWO_SHA},
    )


class Reiaff1RestartTests(unittest.TestCase):
    def test_restart_codec_is_available(self) -> None:
        """Removing the restart codec must break the public import boundary."""

        self.assertEqual(encode_reiaff1.__module__, "rei_bianchi.reiaff1")

    def test_round_trip_preserves_every_restart_block_byte_for_byte(self) -> None:
        """Dropping registry, mixed, remainder, cert, graph, or legacy data is a bug."""

        state = _state()
        encoded = encode_reiaff1(state)
        decoded = _decode_pinned(encoded)

        self.assertEqual(decoded, state)
        self.assertEqual(encode_reiaff1(decoded), encoded)

    def test_decoder_requires_the_external_envelope_digest(self) -> None:
        """Trusting an internal or ignored digest would make mutation self-attested."""

        encoded = encode_reiaff1(_state())
        with self.assertRaises(ValueError):
            decode_reiaff1(
                encoded,
                expected_sha256=TWO_SHA,
                expected_certificate_receipts={"thermal.tgamma": TWO_SHA},
            )

    def test_noncanonical_json_is_rejected_even_with_a_new_external_pin(self) -> None:
        """Whitespace or alternate key encoding must not create semantic aliases."""

        mutated = encode_reiaff1(_state()) + b" "
        with self.assertRaises(ValueError):
            _decode_pinned(mutated)

    def test_block_order_is_closed(self) -> None:
        """Swapping two restart blocks must not be accepted as the same state."""

        def swap(envelope: dict[str, object]) -> None:
            blocks = envelope["blocks"]
            blocks[0], blocks[1] = blocks[1], blocks[0]  # type: ignore[index]

        mutated = _rewrite(encode_reiaff1(_state()), swap)
        with self.assertRaises(ValueError):
            _decode_pinned(mutated)

    def test_ghost_owner_alias_is_rejected(self) -> None:
        """An alias may not resurrect an owner absent from the stored registry."""

        def ghost(envelope: dict[str, object]) -> None:
            envelope["blocks"][0]["value"]["aliases"][0]["owner_id"] = "ghost"  # type: ignore[index]

        mutated = _rewrite(encode_reiaff1(_state()), ghost)
        with self.assertRaises(ValueError):
            _decode_pinned(mutated)

    def test_certificate_payload_is_bound_to_its_digest(self) -> None:
        """A certificate byte mutation must fail even under a repinned envelope."""

        def tamper(envelope: dict[str, object]) -> None:
            envelope["blocks"][4]["value"][0]["payload_base64"] = (  # type: ignore[index]
                base64.b64encode(b"tampered").decode("ascii")
            )

        mutated = _rewrite(encode_reiaff1(_state()), tamper)
        with self.assertRaises(ValueError):
            _decode_pinned(mutated)

    def test_certificate_graph_cannot_reference_a_ghost_payload(self) -> None:
        """Restarting a graph without its exact certificate payload is a loss."""

        def ghost(envelope: dict[str, object]) -> None:
            envelope["blocks"][5]["value"]["nodes"][0]["certificate_id"] = "ghost"  # type: ignore[index]

        mutated = _rewrite(encode_reiaff1(_state()), ghost)
        with self.assertRaises(ValueError):
            _decode_pinned(mutated)

    def test_legacy_normalization_hashes_are_mandatory(self) -> None:
        """A legacy restart cannot silently change its normalization identity."""

        def invalidate(envelope: dict[str, object]) -> None:
            envelope["blocks"][6]["value"]["normalized_sha256"] = "not-a-digest"  # type: ignore[index]

        mutated = _rewrite(encode_reiaff1(_state()), invalidate)
        with self.assertRaises(ValueError):
            _decode_pinned(mutated)

    def test_affine_and_mixed_terms_cannot_name_ghost_owners(self) -> None:
        """Stored coefficients must remain attached to admitted registry owners."""

        def ghost(envelope: dict[str, object]) -> None:
            envelope["blocks"][1]["value"][0]["owner_id"] = "ghost"  # type: ignore[index]

        mutated = _rewrite(encode_reiaff1(_state()), ghost)
        with self.assertRaises(ValueError):
            _decode_pinned(mutated)

    def test_unknown_record_field_fails_with_a_typed_value_error(self) -> None:
        """Schema drift must fail closed, not escape as an incidental TypeError."""

        def extend(envelope: dict[str, object]) -> None:
            envelope["blocks"][0]["value"]["owners"][0]["extra"] = True  # type: ignore[index]

        mutated = _rewrite(encode_reiaff1(_state()), extend)
        try:
            _decode_pinned(mutated)
        except Exception as exc:  # the assertion distinguishes typed schema failure
            self.assertIsInstance(exc, ValueError)
        else:
            self.fail("unknown owner field was accepted")

    def test_registry_record_order_is_canonical(self) -> None:
        """Permuting equivalent registry records must not create a second encoding."""

        def reverse(envelope: dict[str, object]) -> None:
            envelope["blocks"][0]["value"]["owners"].reverse()  # type: ignore[index]

        mutated = _rewrite(encode_reiaff1(_state()), reverse)
        with self.assertRaises(ValueError):
            _decode_pinned(mutated)

    def test_certificate_receipt_requires_an_external_pin(self) -> None:
        """A digest stored beside a certificate cannot attest to itself."""

        encoded = encode_reiaff1(_state())
        with self.assertRaises(ValueError):
            decode_reiaff1(
                encoded, expected_sha256=hashlib.sha256(encoded).hexdigest()
            )

    def test_noncanonical_base64_payload_is_rejected(self) -> None:
        """Distinct base64 spellings of the same payload must not be aliases."""

        def alias(envelope: dict[str, object]) -> None:
            certificate = envelope["blocks"][4]["value"][0]  # type: ignore[index]
            certificate["payload_base64"] = "YR=="  # decodes to b"a", but is not canonical
            certificate["payload_sha256"] = hashlib.sha256(b"a").hexdigest()

        mutated = _rewrite(encode_reiaff1(_state()), alias)
        with self.assertRaisesRegex(ValueError, "REIAFF1_BASE64_NONCANONICAL"):
            _decode_pinned(mutated)


if __name__ == "__main__":
    unittest.main()
