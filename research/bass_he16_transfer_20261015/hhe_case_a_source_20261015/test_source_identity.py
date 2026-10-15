"""Independent evidence-file/hash check against source-scoped scientific receipts."""
import json,hashlib
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent
class FrozenSourceIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((ROOT/"DELIVERY_EVIDENCE_MANIFEST.json").read_text())
    def test_raw_science_source_ledger_identity(self):
        self.assertEqual(self.m["physical_A_B_pairs"],54)
        self.assertEqual(self.m["transport_lanes"],108)
        self.assertEqual(self.m["source_rate_method_body_count_byte_equal"],7)
        self.assertFalse(self.m["original_native_source_and_rlib_whole_epoch_identical"])
        self.assertLess(self.m["full_photo_chem_cmb_escape_energy_ledger_max_abs_eV_per_H"],3e-12)
        self.assertEqual(self.m["recombination_photon_fate"],
                         "Case-A escaping radiation ledger, not coupled OTS or photon stock")
    def test_sha256_all_authored_data(self):
        self.assertGreaterEqual(self.m["file_count"],12)
        for row in self.m["files"]:
            path=ROOT/row["relative_path"]
            self.assertTrue(path.is_file(),row["relative_path"])
            self.assertEqual(path.stat().st_size,row["bytes"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),row["sha256"])

if __name__=="__main__":unittest.main()
