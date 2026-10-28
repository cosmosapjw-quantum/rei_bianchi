"""Targeted structural tests; not an IVP or numerical accuracy admission."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import project_saved as p


class ProjectionTests(unittest.TestCase):
    def test_registry_exact_17_and_hidden_four(self):
        labels, mass, scales, totals, B = p.registry_from_pinned_source(
            p.SOURCE / "vendor/c22/atomic_network.py")
        self.assertEqual(tuple(labels[:17]), p.DISPLAY)
        self.assertEqual(labels[17:], ["Li6_0", "Li6_1", "Li6_2", "Li6_3"])
        self.assertEqual(len(labels), 21)
        self.assertEqual((totals["n"], totals["T"]), (0, 0))
        self.assertGreater(B, 1)

    def test_table_preserves_all_21_columns_and_zero(self):
        example = {"labels": [f"s{i}" for i in range(21)],
                   "eta": np.array([0., np.log(7.)]), "z": np.array([20., 2.]),
                   "per_href": np.zeros((21, 2)), "per_baryon": np.zeros((21, 2))}
        example["per_href"][16] = [0.25, 0.5]
        example["per_baryon"][16] = [0.125, 0.25]
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "table.csv"
            p.write_table(example, output)
            import csv
            with output.open() as f:
                rows = list(csv.reader(f))
            self.assertEqual(len(rows[0]), 44)
            self.assertEqual(len(rows), 3)
            self.assertEqual(float(rows[2][2 + 16]), 0.5)
            self.assertEqual(float(rows[2][2 + 21 + 16]), 0.25)
            self.assertEqual(float(rows[2][2]), 0.)

    def test_log_display_never_invents_values_for_zero(self):
        self.assertIsNone(p.log_series(np.array([0., 0.])))
        masked = p.log_series(np.array([0., 1e-12, 2e-12]))
        self.assertEqual(masked.mask.tolist(), [True, False, False])
        self.assertEqual(masked.compressed().tolist(), [1e-12, 2e-12])
        with self.assertRaises(ValueError):
            p.log_series(np.array([-1e-30, 1.]))


if __name__ == "__main__":
    unittest.main()
