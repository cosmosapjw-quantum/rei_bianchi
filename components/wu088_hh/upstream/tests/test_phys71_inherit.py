"""Saved-data contract tests only: no inherited integration is replayed.

Set PHYS71_ARCHIVE_ROOT to a source/evidence capsule when the two pinned ZIPs
are not present in the checkout.  The complete accessor executes once in
setUpClass; negative tests use copies of two stored JSON objects.
"""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from wu088_hh import phys71_inherit as inherit


REPO = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = Path(os.environ.get("PHYS71_ARCHIVE_ROOT", str(REPO)))


class InheritedProfilesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = inherit.load_inherited_profiles(
            REPO, low_archive=ARCHIVE_ROOT/inherit.LOW_ARCHIVE,
            band_archive=ARCHIVE_ROOT/inherit.BAND_ARCHIVE)
        bound = json.loads((REPO/inherit.LOW_RUN/"REQUEST.json").read_text())
        cls.request, cls.fingerprint = bound["binding"]["request"], bound["fingerprint"]
        with ZipFile(ARCHIVE_ROOT/inherit.LOW_ARCHIVE) as archive:
            cls.saved0 = json.loads(archive.read("run_l28_t65_completed/panel_0000.json"))
            cls.saved1 = json.loads(archive.read("run_l28_t65_completed/panel_0001.json"))
        cls.state0 = {f"{r['pair'][0]},{r['pair'][1]}": r["q_left"]
                      for r in cls.saved0["payload"]["pairs"]}

    def check_panel(self, saved, *, index=0, previous=None):
        # Rebind the mutated payload locally so semantic failures are exercised
        # beyond the outer hash guard. Production gets this SHA from pinned cert.
        digest = sha256(inherit.canonical(saved["payload"])).hexdigest()
        saved["payload_sha256"] = digest
        return inherit.validate_panel(saved, index=index, request=self.request,
                                      fingerprint=self.fingerprint,
                                      expected_payload_sha256=digest,
                                      previous_state=previous, band=False)

    def test_actual_152_saved_payloads_and_full_radial_coverage(self):
        data = self.data
        self.assertEqual(data.provenance["inherited_payloads_verified"], 152)
        self.assertEqual(len(data.panels), 76)
        self.assertEqual(data.panels[0].right, Fraction(65))
        self.assertEqual(data.panels[-1].left, Fraction(27))
        self.assertTrue(all(a.left == b.right for a, b in zip(data.panels, data.panels[1:])))
        self.assertEqual(data.provenance["boundary_pair_enclosures_verified"], 5548)

    def test_combined_73_pairs_and_precisions_preserved(self):
        expected = {tuple(sorted((a, j))) for a in (20, 21) for j in range(37)}
        self.assertEqual(len(expected), 73)
        for panel in self.data.panels:
            self.assertEqual(set(panel.pairs), expected)
            self.assertEqual(panel.pairs[(20, 21)]["q_coefficient_count"], 82)
            self.assertEqual(panel.pairs[(20, 36)]["q_coefficient_count"], 98)
            self.assertEqual(panel.coulomb_modes, tuple(range(37)))

    def test_producer_runtime_is_provenance(self):
        provenance = self.data.provenance
        self.assertFalse(provenance["producer_runtime_equality_required"])
        self.assertFalse(provenance["reader_runtime_is_producer_runtime_claim"])
        self.assertEqual(provenance["Coulomb_evaluations"], 0)
        self.assertEqual(provenance["new_integrals"], 0)
        self.assertEqual(provenance["old_payload_writes"], 0)
        for family in provenance["families"]:
            self.assertEqual(family["producer_runtime"],
                             {"python": "3.12.14", "python_flint": "0.8.0", "flint": "3.3.1"})

    def test_wrong_archive_sha_is_rejected_before_zip_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"wrong.zip"
            path.write_bytes(b"not the pinned archive")
            with self.assertRaisesRegex(inherit.InheritedDataError, "pinned SHA256 mismatch"):
                inherit.load_inherited_profiles(REPO, low_archive=path,
                                                band_archive=ARCHIVE_ROOT/inherit.BAND_ARCHIVE)

    def test_duplicate_pair_is_rejected_even_with_new_local_digest(self):
        saved = deepcopy(self.saved0)
        saved["payload"]["pairs"][1] = deepcopy(saved["payload"]["pairs"][0])
        with self.assertRaisesRegex(inherit.InheritedDataError, "pair order/coverage"):
            self.check_panel(saved)

    def test_float_pair_is_not_coerced(self):
        saved = deepcopy(self.saved0)
        saved["payload"]["pairs"][0]["pair"][0] = 0.0
        with self.assertRaisesRegex(inherit.InheritedDataError, "two exact integers"):
            self.check_panel(saved)

    def test_negative_serialized_radius_is_rejected(self):
        saved = deepcopy(self.saved0)
        saved["payload"]["pairs"][0]["q_center"]["real"]["radius"]["mantissa"] = "-1"
        with self.assertRaisesRegex(inherit.InheritedDataError, "negative serialized radius"):
            self.check_panel(saved)

    def test_noninteger_dyadic_cannot_silently_truncate(self):
        for bad in (True, False, 1.25):
            with self.subTest(value=bad), self.assertRaises(inherit.InheritedDataError):
                inherit.dyadic({"mantissa": bad, "exponent2": -4})
        for bad in (True, 1.25, "2"):
            with self.subTest(exponent=bad), self.assertRaises(inherit.InheritedDataError):
                inherit.dyadic({"mantissa": "1", "exponent2": bad})

    def test_predecessor_serialization_hash_is_bound(self):
        saved = deepcopy(self.saved1)
        saved["right_state_sha256"] = "0"*64
        with self.assertRaisesRegex(inherit.InheritedDataError, "predecessor serialization SHA256"):
            self.check_panel(saved, index=1, previous=self.state0)

    def test_carry_must_enclose_predecessor_not_only_hash_it(self):
        saved = deepcopy(self.saved1)
        saved["payload"]["pairs"][0]["q_right"] = deepcopy(self.saved0["payload"]["pairs"][0]["q_right"])
        with self.assertRaisesRegex(inherit.InheritedDataError, "does not enclose"):
            self.check_panel(saved, index=1, previous=self.state0)

    def test_terminal_value_is_exact_zero(self):
        saved = deepcopy(self.saved0)
        saved["payload"]["pairs"][0]["q_right"]["real"]["midpoint"]["mantissa"] = "1"
        with self.assertRaisesRegex(inherit.InheritedDataError, "terminal q"):
            self.check_panel(saved)

    def test_wrong_radial_panel_is_rejected(self):
        saved = deepcopy(self.saved0)
        saved["payload"]["center"] = "65"
        with self.assertRaisesRegex(inherit.InheritedDataError, "center mismatch"):
            self.check_panel(saved)

    def test_json_duplicate_keys_and_nonfinite_tokens_rejected(self):
        for text in (b'{"index":0,"index":1}', b'{"bad":NaN}', b'{"bad":Infinity}'):
            with self.subTest(text=text), self.assertRaises(inherit.InheritedDataError):
                inherit._json(text)


if __name__ == "__main__":
    unittest.main()
