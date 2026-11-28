import unittest
import atomic_data as a
from fractions import Fraction as F
class Behaviors(unittest.TestCase):
    def test_negative_defect_is_not_clamped(self):
        self.assertEqual(a.signed_defect('-3/5',('-1/2','-1/2'),('-1/20','-1/20')),('-1/20','-1/20'))
    def test_interval_defect_orders_endpoints(self):
        self.assertEqual(a.signed_defect('-1/2',('-2/5','-3/10'),('-1/5','-1/10')),('-1/10','1/10'))
    def test_ground_reused_twice(self):
        self.assertEqual(a.signed_defect('-3/5',('-1/2','-2/5'),('-1/2','-2/5')),('1/5','2/5'))
    def test_model_affinity_different_reference(self):
        self.assertEqual(a.model_affinity('-3/5',('-2/5','-2/5')),('1/5','1/5'))
    def test_float_is_not_exact_input(self):
        with self.assertRaises(a.ContractError):a.fraction(.1)
    def test_bool_is_not_exact_input(self):
        with self.assertRaises(a.ContractError):a.fraction(True)
    def test_energy_identity_required(self):
        with self.assertRaises(a.ContractError):a.check_energy_parts({'N':'2','T':'1','T_strong':'1','V_nuclear':'-4','V_ee':'1','E':'-9'})
    def test_physical_threshold_is_unavailable(self):
        with self.assertRaises(a.SourceUnavailable):a.physical_threshold({'defect':'1'})
if __name__=='__main__':unittest.main()
