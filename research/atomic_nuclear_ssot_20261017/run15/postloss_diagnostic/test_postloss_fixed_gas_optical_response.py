"""Focused checks for the new postloss diagnostic; no native IVP calls."""
from decimal import Decimal, localcontext
import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np
from scipy.integrate import quad

import postloss_fixed_gas_optical_response as diagnostic


class PostlossFixedGasTests(unittest.TestCase):
    def test_cubic_extrema_include_both_interior_stationary_points(self):
        lower, upper = diagnostic.polynomial_extrema([0, 0.5, -1.5, 1], 0, 1)
        exact = 1/(12*np.sqrt(3))
        self.assertAlmostEqual(lower, -exact, places=14)
        self.assertAlmostEqual(upper, exact, places=14)

    def test_narrow_tail_integral_agrees_with_high_precision_expression(self):
        rate, left, right = 65000.0, 0.00048, 0.000480000001
        actual = diagnostic.exponential_integral(rate, left, right)
        with localcontext() as context:
            context.prec = 75
            r, a, b = map(Decimal.from_float, [rate, left, right])
            reference = float(((-r*a).exp()-(-r*b).exp())/r)
        self.assertLess(abs(actual/reference-1), 7e-15)

    def test_source_decrease_gives_conservative_positive_tail(self):
        lo, hi, rate = diagnostic.H_FIT+0.00048, diagnostic.H_FIT+0.0035, 65000.0
        source = diagnostic.number_shape
        measured, _ = quad(lambda e: float(source(e))*np.exp(-rate*(e-diagnostic.H_FIT)),
                           lo, hi, epsabs=1e-30, epsrel=1e-11, limit=100)
        upper = float(source(diagnostic.H_FIT))*diagnostic.exponential_integral(
            rate, lo-diagnostic.H_FIT, hi-diagnostic.H_FIT)
        self.assertGreater(measured, 0)
        self.assertLess(measured, upper)
        self.assertLess(upper/measured-1, 1e-3)

    def test_archive_reader_rejects_mutated_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = b"immutable original input\n"
            path = root/"input.txt"
            path.write_bytes(original)
            (root/"SHA256SUMS.txt").write_text(
                hashlib.sha256(original).hexdigest()+"  input.txt\n")
            archive = diagnostic.ArchiveInputs(root)
            self.assertEqual(archive.verify("input.txt"), path)
            path.write_bytes(b"mutated input\n")
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                archive.verify("input.txt")

    def test_profile_selection_is_explicit(self):
        with self.assertRaisesRegex(ValueError, "profile must"):
            diagnostic.FixedResponse("/unused", "arbitrary")


if __name__ == "__main__":
    unittest.main(verbosity=2)
