import unittest
from fractions import Fraction as F
from e11.budget_observability import reconstruct_total_absorption, unidentified_components

class BudgetObservabilityTests(unittest.TestCase):
    def test_scalar_energy_moment_sums_only(self):
        self.assertEqual(reconstruct_total_absorption(F(12),F(3),F(2),F(1)),F(6))

    def test_not_possible_to_reconstruct_species_from_total(self):
        candidates=unidentified_components(F(3))
        self.assertEqual(len(candidates),2)
        self.assertEqual([sum(x) for x in candidates],[F(3),F(3)])
        self.assertNotEqual(candidates[0],candidates[1])
        self.assertTrue(all(v>=0 for x in candidates for v in x))

    def test_negative_photon_budget_not_silently_clamped(self):
        with self.assertRaises(ValueError):
            reconstruct_total_absorption(F(1),F(3),F(2),F(1))

if __name__=='__main__':unittest.main()
