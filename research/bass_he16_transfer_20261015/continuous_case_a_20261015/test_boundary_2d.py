"""Original Rust MD14 source grid × proper-time refinement and synthetic failures."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from analyze_boundary_2d import audit

HERE=Path(__file__).resolve().parent
RESULTS=HERE/"results"

class NativeSourceBoundary2DTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=audit(RESULTS/"SOURCE_BOUNDARY_2D.csv")
        cls.records=cls.result["grid"]

    def test_twenty_native_grid_time_cases_and_five_resolutions(self):
        self.assertEqual(self.result["cases"],20)
        self.assertEqual(len(self.records),5)
        self.assertEqual(self.result["source_energy_bins_per_segment"],[4,8,16,32,64])
        self.assertEqual(self.result["time_steps"],[1,8,32,128])

    def test_exact_single_step_leakage_is_first_cell_projection(self):
        for data in self.records:
            self.assertLess(
                abs(data["loss_fraction_one_step"]-data["initial_two_node_exact_loss"]),5e-15)

    def test_fixed_time_refinement_does_not_eliminate_boundary_loss(self):
        for data in self.records:
            self.assertGreater(data["loss_fraction_128_steps"],.99*data["loss_fraction_one_step"])
            self.assertGreater(data["loss_fraction_128_steps"],0.)

    def test_true_finite_centroid_photons_do_not_physically_cross_lower_support(self):
        for data in self.records:
            self.assertGreater(data["minimum_exact_centroid_endpoint_eV"],13.6)

    def test_energy_double_resolution_approximately_halves_ghost(self):
        pairs=self.result["energy_refinement_pairs"]
        self.assertEqual(len(pairs),4)
        for p in pairs:
            self.assertGreater(p["boundary_ratio_fine_over_coarse"],.49)
            self.assertLess(p["boundary_ratio_fine_over_coarse"],.51)

    def test_native_energy_first_order_scaling_empirical_not_theorem(self):
        scaled=[p["m_times_loss_fraction_128"] for p in self.records]
        self.assertLess(max(scaled)-min(scaled),.005)
        self.assertEqual(self.result["scientific_admission"],
            "SCOPED_SOURCE_ONLY_C8_NUMERICALLY_CHECKED_NOT_FULL_EOR")

    def test_original_16cell_previous_control_reproduced(self):
        with (RESULTS/"SOURCE_ONLY_BOUNDARY.csv").open(newline="") as f:
            old=list(csv.DictReader(f))
        expected={int(x["substeps"]):float(x["boundary_fraction"]) for x in old
                  if float(x["q_ref"])==0 and int(x["substeps"]) in (1,128)}
        row=next(v for v in self.records
                 if v["source_cells_per_threshold_segment"]==16)
        self.assertLess(abs(row["loss_fraction_one_step"]-expected[1]),1e-11)
        self.assertLess(abs(row["loss_fraction_128_steps"]-expected[128]),1e-11)

    def test_native_source_photon_count_residuals(self):
        with (RESULTS/"SOURCE_BOUNDARY_2D.csv").open(newline="") as f:
            values=list(csv.DictReader(f))
        self.assertEqual(len(values),20)
        self.assertLess(max(abs(float(v["photon_count_residual_per_H"])) for v in values),2e-18)

    def test_incompatible_missing_source_case_fails_closed(self):
        lines=(RESULTS/"SOURCE_BOUNDARY_2D.csv").read_text().splitlines()
        with tempfile.TemporaryDirectory() as temp:
            short=Path(temp)/"short.csv"
            short.write_text("\n".join(lines[:-1])+"\n")
            with self.assertRaises(ValueError):
                audit(short)

    def test_corrupt_low_support_receipt_fails_closed(self):
        p=RESULTS/"SOURCE_BOUNDARY_2D.csv"
        with p.open(newline="") as f:
            rows=list(csv.DictReader(f));cols=list(rows[0])
        rows[0]["min_exact_source_centroid_end_eV"]="13.5"
        with tempfile.TemporaryDirectory() as temp:
            bad=Path(temp)/"corrupted.csv"
            with bad.open("w",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=cols)
                writer.writeheader();writer.writerows(rows)
            with self.assertRaises(ValueError):
                audit(bad)

if __name__=="__main__":
    unittest.main()
