"""Independent manufactured arithmetic controls; NOT_RUN at authoring."""
import unittest
from fractions import Fraction as F

from caloric_branch import CaloricBranch, exact


def branch(rows=((1, 2), (2, 4), (4, 10))):
    return CaloricBranch(rows, "V0", "gas_thermal_only", "manufactured")


class CaloricBranchTests(unittest.TestCase):
    def test_three_knot_inverse_and_direct_values(self):
        b = branch()
        self.assertEqual(b.m0, F(2))
        for temperature, energy in ((F(1), F(2)), (F(3, 2), F(3)),
                                    (F(2), F(4)), (F(3), F(7)), (F(4), F(10))):
            self.assertEqual(b.evaluate(temperature), energy)
            self.assertEqual(b.inverse(energy), temperature)

    def test_manufactured_uncertainty_and_radius(self):
        b = branch()
        self.assertEqual(b.enclose_energy(5, 6, 1), (F(2), F(3)))
        self.assertEqual(b.residual_radius(F(5, 2), 5, 1, 1), F(5, 4))
        # Upper and lower are attained by distinct admissible constant shifts,
        # with independently chosen interval endpoint energies.
        self.assertEqual(b.evaluate(2)+1, F(5))
        self.assertEqual(b.evaluate(3)-1, F(6))

    def test_absent_uncertainty_stays_unknown(self):
        b = branch()
        self.assertIsNone(b.enclose_energy(5, 6, None))
        self.assertIsNone(b.residual_radius(F(5, 2), 5, None, 1))
        self.assertIsNone(b.residual_radius(F(5, 2), 5, 1, None))
        for energy_radius, eos_radius in ((-1, None), (None, -1),
                                          (0.1, None), (None, 0.1)):
            with self.subTest(eE=energy_radius, eta=eos_radius), self.assertRaises((ValueError, TypeError)):
                b.residual_radius(2, 4, energy_radius, eos_radius)

    def test_energy_origin_and_scale_covariance(self):
        b = branch()
        transformed = branch(((1, -11), (2, -5), (4, 13)))  # 3F-17
        self.assertEqual(transformed.enclose_energy(-2, 1, 3), b.enclose_energy(5, 6, 1))
        self.assertEqual(transformed.residual_radius(F(5, 2), -2, 3, 3),
                         b.residual_radius(F(5, 2), 5, 1, 1))
        scaled = branch(((1, 6), (2, 12), (4, 30)))
        self.assertEqual(scaled.inverse(21), b.inverse(7))
        self.assertEqual(scaled.enclose_energy(15, 18, 3), b.enclose_energy(5, 6, 1))

    def test_nonlinear_truth_contained_by_secant(self):
        # F*=T^2; F0=4T-3; (T-1)(3-T) in [0,1] on [1,3].
        secant = branch(((1, 1), (3, 9)))
        self.assertEqual(secant.enclose_energy(4, 4, 1), (F(3, 2), F(2)))
        self.assertEqual(F(2)**2, F(4))
        self.assertTrue(F(3, 2) <= F(2) <= F(2))

    def test_domain_failures_and_exact_data_boundary(self):
        for rows in ((), ((1, 1),), ((0, 1), (2, 3)),
                     ((1, 1), (1, 3)), ((1, 1), (2, 1)),
                     ((1, 2), (2, 1)), ((1.0, 2), (2, 4))):
            with self.subTest(rows=rows), self.assertRaises((ValueError, TypeError)):
                branch(rows)
        b = branch()
        for fn in (lambda: b.evaluate(0), lambda: b.evaluate(5),
                   lambda: b.inverse(1), lambda: b.inverse(11),
                   lambda: b.enclose_energy(7, 6, 0),
                   lambda: b.enclose_energy(5, 6, -1),
                   lambda: b.enclose_energy(2, 10, 1),
                   lambda: b.residual_radius(2, 4, -1, 0),
                   lambda: b.residual_radius(2, 4, 0, -1),
                   lambda: b.inverse(7.0)):
            with self.subTest(fn=fn), self.assertRaises((ValueError, TypeError)):
                fn()
        self.assertEqual(exact({"num": "3", "den": "2"}), F(3, 2))
        with self.assertRaises((ValueError, TypeError)):
            exact({"num": 3, "den": 0})


if __name__ == "__main__":
    unittest.main()
