import sys, pathlib, unittest
from fractions import Fraction as F
root=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from birth_count_bridge import *

class ConditionalBirthCount(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row=frozen_full_witness()
        cls.v=parse_row(cls.row)[0]
    def test_mass_energy(self):
        self.assertEqual(E,2*M-A+2*K0)
    def test_positive_kinematics(self):
        self.assertGreater(K0*K0,B2)
    def test_exact_original_full_witness(self):
        self.assertEqual(self.v, B2*F(24377,71485))
    def test_exact_row_covariance(self):
        self.assertEqual(parse_row(self.row),(self.v,self.v))
    def test_fixed_event_count_total_variance_zero(self):
        m=conditional_count_moments([self.v]*2,5,0)
        self.assertEqual(m['pair_total_variance_MeV2'],0)
        self.assertEqual(m['cross_covariance_MeV2'][0],-5*self.v)
    def test_poisson_event_count_positive_cross(self):
        m=poisson_from_mean([self.v]*2,5)
        self.assertGreater(m['cross_covariance_MeV2'][0],0)
        self.assertEqual(m['pair_total_variance_MeV2'],20*K0*K0)
    def test_compound_covariance_eigenvalues(self):
        m=conditional_count_moments([self.v]*2,F(3,2),F(9,4))
        self.assertEqual(m['eigen_sum'],2*F(9,4)*K0*K0)
        self.assertEqual(m['eigen_difference'][0],3*self.v)
        self.assertGreater(m['eigen_sum'],0)
    def test_fano_sign_threshold(self):
        m=conditional_count_moments([self.v]*2,1,self.v/(K0*K0))
        self.assertEqual(m['cross_covariance_MeV2'],(0,0))
    def test_interval_outward_order(self):
        m=conditional_count_moments([self.v-1,self.v+1],7,2)
        self.assertLess(m['diagonal_variance_MeV2'][0],m['diagonal_variance_MeV2'][1])
        self.assertLess(m['cross_covariance_MeV2'][0],m['cross_covariance_MeV2'][1])
    def test_invalid_variance_negative(self):
        with self.assertRaises(ValueError):conditional_count_moments([-1,0],1,1)
    def test_invalid_variance_upper(self):
        with self.assertRaises(ValueError):conditional_count_moments([0,B2+1],1,1)
    def test_invalid_count(self):
        with self.assertRaises(ValueError):conditional_count_moments([self.v]*2,-1,1)
    def test_no_variance_with_zero_mean(self):
        with self.assertRaises(ValueError):conditional_count_moments([self.v]*2,0,1)
    def test_no_physical_rate_or_pool_activation(self):
        p=no_physical_activation(self.row)
        self.assertFalse(p['activation']);self.assertIsNone(p['event_rate_m3s'])
        self.assertIsNone(p['D_thermal_deposition_J_m3s'])
    def test_manufactured_count_exact_and_not_physical(self):
        p=diagnostic_manufactured_event_rate('3/2','MANUFACTURED_TEST_ONLY')
        self.assertEqual(p['manufactured_D_count_m3s'],3)
        self.assertEqual(p['manufactured_pair_kinetic_J_m3s'],F(3,2)*2*K0*MEV_TO_J)
        self.assertFalse(p['physical_activation'])
    def test_manufactured_rate_reject_physical_label(self):
        with self.assertRaises(ValueError):diagnostic_manufactured_event_rate(1,'PHYSICAL')
    def test_reject_inconsistent_covariance(self):
        row=dict(self.row);row['daughter_covariance_MeV2']=['0','0']
        with self.assertRaises(ValueError):parse_row(row)
    def test_reject_float_source(self):
        with self.assertRaises(ValueError):q(0.5)
    def test_unavailable_full_source_does_not_fake_pass(self):
        with self.assertRaises(FileNotFoundError):read_pinned_birth_result(root/'DOES_NOT_EXIST.json')

if __name__=='__main__':unittest.main(verbosity=2)
