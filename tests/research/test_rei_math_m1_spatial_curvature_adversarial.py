#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "research"
    / "rei_math_m1_generic_background"
    / "adversarial_curvature_residuals.py"
)
SPEC = importlib.util.spec_from_file_location("rei_m1_adversarial", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SpatialCurvatureAdversarialRegression(unittest.TestCase):
    def test_correct_formula_and_jacobi_residuals_are_exact_zero(self) -> None:
        records = MODULE.generate_records()
        self.assertEqual(len(records), 8)
        self.assertTrue(
            all(record["jacobi_residual_max"] == 0.0 for record in records)
        )
        self.assertTrue(
            all(
                record["correct_ricci_residual_max"] == 0.0
                for record in records
            )
        )

    def test_mixed_sign_mutation_has_negative_and_positive_controls(self) -> None:
        records = MODULE.generate_records()
        class_a = [record for record in records if record["class"] == "A"]
        class_b = [record for record in records if record["class"] == "B"]
        self.assertEqual(len(class_a), 4)
        self.assertEqual(len(class_b), 4)
        self.assertTrue(
            all(
                record["mixed_sign_mutation_residual_max"] == 0.0
                for record in class_a
            )
        )
        self.assertTrue(
            all(
                record["mixed_sign_mutation_residual_max"] > 0.0
                for record in class_b
            )
        )

    def test_plot_and_machine_readable_outputs_are_emitted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = MODULE.write_outputs(Path(directory))
            for key in ("csv", "svg", "summary"):
                path = Path(result[key])
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 0)
            self.assertEqual(result["correct_formula_exact_zero_count"], 8)
            self.assertEqual(result["jacobi_exact_zero_count"], 8)
            self.assertEqual(result["class_a_mutation_zero_count"], 4)
            self.assertEqual(result["class_b_mutation_detected_count"], 4)
            self.assertEqual(
                result["authority_effect"],
                "NUMERICAL_ADVERSARIAL_REGRESSION_ONLY",
            )
            self.assertEqual(result["native_runtime"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
