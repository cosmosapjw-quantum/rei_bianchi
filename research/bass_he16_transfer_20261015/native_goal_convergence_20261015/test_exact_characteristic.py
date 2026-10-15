"""Direct signed-q exact covariant characteristic versus reprojected native stock."""
import csv
from pathlib import Path
import unittest


class ExactSignedCharacteristicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        csv_path=Path(__file__).parent/"results"/"REMAP_VS_COVARIANT_CHARACTERISTIC.csv"
        with csv_path.open(newline="") as f:
            cls.rows=list(csv.DictReader(f))
        if len(cls.rows)!=6:
            raise ValueError("Expected 3 signed native q values times 2 remap stages")

    def test_all_signed_native_mean_energies_one_map_match_exact(self):
        for row in self.rows:
            if row["remap_steps"]!="1":
                continue
            self.assertLess(abs(float(row["relative_energy_bias"])),1e-14)
            self.assertEqual(float(row["number_boundary"]),0.)
            self.assertAlmostEqual(float(row["number_surviving"]),1.,places=13)

    def test_all_signed_repeated_projection_means_are_biased(self):
        for row in self.rows:
            if row["remap_steps"]!="4096":
                continue
            self.assertGreater(float(row["number_boundary"]),8e-6)
            self.assertGreater(float(row["relative_energy_bias"]),1e-6)
            self.assertLess(float(row["relative_energy_bias"]),2e-6)
            self.assertGreater(float(row["exact_end_E_eV"]),13.6)

    def test_native_ledger_number_and_energy_balance_each_case(self):
        for row in self.rows:
            n=float(row["number_surviving"])+float(row["number_boundary"])
            self.assertAlmostEqual(n,1.,places=12)
            self.assertLess(abs(float(row["number_ledger_residual"])),1e-12)
            self.assertLess(abs(float(row["energy_ledger_residual"])),1e-12)

    def test_signed_sources_correctly_tagged(self):
        values={(float(r["q_ref"]),int(r["remap_steps"])) for r in self.rows}
        self.assertEqual(values,{(q,k) for q in (-.005,0.,.005) for k in (1,4096)})


if __name__=="__main__":
    unittest.main()
