import unittest
from fractions import Fraction as F
from atomic_decay_reference import IV,row_factors,rotational_multiplicity,weighted_average,cascade_table,require_physical,ContractError,SourceUnavailable
class RequiredBehavior(unittest.TestCase):
    def test_one_branch_exact_one(self):
        self.assertEqual(row_factors([IV(2,7)])['branches'],[IV(1,1)])
    def test_shared_denominator_bounds(self):
        self.assertEqual(row_factors([IV(1,2),IV(3,4)])['branches'][0],IV(F(1,5),F(2,5)))
    def test_zero_subset_not_physical_infinite_lifetime(self):
        self.assertIsNone(row_factors([])['lifetime'])
    def test_s_to_full_p_has_three_but_reverse_does_not(self):
        self.assertEqual((rotational_multiplicity(0,1),rotational_multiplicity(1,0)),(3,1))
    def test_shared_weight_constant_identity(self):
        self.assertEqual(weighted_average([IV(1,7),IV(2,9)],[IV(3,3),IV(3,3)]),IV(3,3))
    def test_non_descending_edge_refused(self):
        with self.assertRaises(ContractError): cascade_table({'a':F(0),'b':F(1)},[('a','b',IV(1,1))])
    def test_physical_rate_unavailable(self):
        with self.assertRaises(SourceUnavailable): require_physical()
    def test_deterministic_two_photon_chain(self):
        c=cascade_table({'a':F(0),'b':F(1),'c':F(3)},[('b','a',IV(2,3)),('c','b',IV(3,4))])
        self.assertEqual(c.get('c',{}).get('photon_count'),IV(2,2))
