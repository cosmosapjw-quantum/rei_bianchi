import unittest
from fractions import Fraction

from remap_semigroup_identity import semigroup_witness


class ExactSemigroupWitnessTests(unittest.TestCase):
    def test_fractions_conserve_count_and_first_moment(self):
        for a in (Fraction(1,50),Fraction(1,5),Fraction(1,4),Fraction(2,5)):
            out=semigroup_witness(a)
            self.assertEqual(out["photon_number_repeated"],"1")
            self.assertEqual(out["photon_number_once"],"1")
            self.assertEqual(out["mean_grid_energy_shift_both"],str(-2*a))
            self.assertEqual(out["excess_variance_units_deltaE_squared"],str(2*a*a))

    def test_nonsemigroup_example_positive_excess(self):
        x=semigroup_witness(Fraction(1,5))
        self.assertEqual(Fraction(x["excess_variance_units_deltaE_squared"]),Fraction(2,25))
        self.assertNotEqual(x["weights_two_reprojections"],x["weights_one_projection"])

    def test_domain_conditions_enforced(self):
        for a in (Fraction(-1,10),Fraction(0),Fraction(1,2),Fraction(3,4)):
            with self.assertRaises(ValueError):
                semigroup_witness(a)

if __name__=="__main__":
    unittest.main()
