import hashlib,json,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
class SourceEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((HERE/"DELIVERY_EVIDENCE_MANIFEST.json").read_text())
    def test_issuer_held_and_source_identities_are_distinct(self):
        r=self.m
        self.assertEqual(r["pairs"],24)
        self.assertEqual(r["lanes"],48)
        self.assertTrue(r["two_native_MD14_source_methods_byte_equal"])
        self.assertFalse(r["full_native_compilation_identities_equal"])
        self.assertEqual(r["scientific_admission"],"HOLD_FULL_EOR_AND_CMB")
        self.assertEqual(r["native_casea_rec_photons"],"energy_ESCAPE_ledger_only_no_OTS_spectrum")
    def test_all_source_scoped_artifacts_hash_match(self):
        for row in self.m["files"]:
            p=HERE/row["relative_path"]
            self.assertEqual(p.stat().st_size,row["bytes"])
            h=hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(h,row["sha256"])
if __name__=="__main__":unittest.main()
