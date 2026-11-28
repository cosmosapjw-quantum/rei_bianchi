"""Synthetic rational/static contracts. Does not load FLINT or any HH inputs."""
import math
from fractions import Fraction as Q
from pathlib import Path
import unittest

from synthetic_oracle import radial_even, gaussian_cartesian_moment, domain_ok, Box


class ExactRadialTests(unittest.TestCase):
    def test_terminating_even_independent_cartesian(self):
        for sigma in (Q(1, 2), Q(2), Q(3, 7)):
            for s in (Q(0), Q(1, 3), Q(7, 2)):
                for k in (0, 2, 4, 6, 8):
                    self.assertEqual(radial_even(k, 0, sigma, s),
                                     gaussian_cartesian_moment(k, sigma, s))

    def test_low_k_derivative_closed_forms(self):
        sig, s = Q(3, 7), Q(11, 5)
        self.assertEqual(radial_even(0, 0, sig, s), 1)
        self.assertEqual(radial_even(0, 1, sig, s), 0)
        self.assertEqual(radial_even(0, 2, sig, s), 0)
        self.assertEqual(radial_even(2, 0, sig, s), s + 3 * sig)
        self.assertEqual(radial_even(2, 1, sig, s), 1)
        self.assertEqual(radial_even(2, 2, sig, s), 0)
        self.assertEqual(radial_even(4, 0, sig, s), s*s + 10*sig*s + 15*sig*sig)
        self.assertEqual(radial_even(4, 1, sig, s), 2*s + 10*sig)
        self.assertEqual(radial_even(4, 2, sig, s), 2)

    def test_reject_invalid_degree(self):
        for k, r in ((1,0),(-2,0),(10,0),(2,-1),(2,3)):
            with self.assertRaises(ValueError):
                radial_even(k,r,Q(1),Q(1))


class DomainTests(unittest.TestCase):
    def test_full_box_margin(self):
        self.assertTrue(domain_ok(Box(Q(1),Q(2),Q(-100),Q(100)),Q(1,8)))
        self.assertFalse(domain_ok(Box(Q(-1),Q(2),Q(0),Q(0)),Q(1,8)))
        self.assertFalse(domain_ok(Box(Q(1,8),Q(2),Q(0),Q(0)),Q(1,8)))
        self.assertFalse(domain_ok(Box(Q(0),Q(2),Q(0),Q(0)),Q(1,8)))

    def test_invalid_margin_and_box(self):
        for margin in (Q(0), Q(-1)):
            with self.assertRaises(ValueError):
                domain_ok(Box(Q(1),Q(2),Q(0),Q(0)),margin)
        with self.assertRaises(ValueError):
            Box(Q(2),Q(1),Q(0),Q(0))


class StaticBackendContract(unittest.TestCase):
    def test_unregularized_and_no_legacy_or_conjugation(self):
        source=Path(__file__).with_name('callback.cpp').read_text()
        self.assertIn('acb_hypgeom_m(out.v, a.v, b.v, z.v, 0, p)', source)
        self.assertNotIn('acb_conj(',source)
        self.assertNotIn('radial_wide',source)
        self.assertNotIn('std::complex',source)
        self.assertNotIn('double',source)
        self.assertIn('arb_is_positive',source)
        self.assertIn('order != 0 && order != 1',source)
        self.assertIn('acb_indeterminate(out)',source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
