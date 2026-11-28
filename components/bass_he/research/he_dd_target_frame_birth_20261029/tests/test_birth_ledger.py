"""Fresh scoped tests only, without previous suite, IVP or physical source."""
import sys, unittest
from pathlib import Path
from decimal import Decimal
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from birth_ledger import *

class KinematicLedgerTests(unittest.TestCase):
    def test_frozen_masses(self):
        self.assertEqual(M,F('3727.3794118'));self.assertEqual(m,F('1875.61294500'))
    def test_mass_defect(self):self.assertEqual(2*m-M,F('23.8464782'))
    def test_330_pair_energy(self):self.assertEqual(event_ledger(330)['pair_kinetic_MeV'],F('306.1535218'))
    def test_213_pair_energy(self):self.assertEqual(event_ledger(213)['pair_kinetic_MeV'],F('189.1535218'))
    def test_single_D_mean(self):self.assertEqual(event_ledger(330)['single_D_pair_mean_kinetic_MeV'],F('153.0767609'))
    def test_threshold_qzero(self):self.assertEqual(event_ledger(threshold())['q2_c2_MeV2'],0)
    def test_below_threshold(self):
        with self.assertRaises(ValueError):event_ledger(threshold()-F(1,10**8))
    def test_no_rate_promotion(self):
        for e in (213,330):
            a=event_ledger(e)
            self.assertIsNone(a['R_event']);self.assertIsNone(a['kappa']);self.assertFalse(a['physical_activation']);self.assertFalse(a['L4']);self.assertEqual(a['production'],'HOLD')
    def test_energy_and_baryon_charge_conservation(self):
        for e in (threshold(),213,258,330):
            a=event_ledger(e)
            self.assertEqual((a['energy_balance_MeV'],a['baryon_delta'],a['charge_delta']),(0,0,0))
    def test_split_square_is_nonnegative(self):
        for e in (threshold(),213,258,330):self.assertGreaterEqual(event_ledger(e)['splitting_coefficient_squared_MeV2'],0)
    def test_pair_mean_asymmetric_law(self):
        a=moment_packet(330,[('-1','1'),('0','2'),('1/3','5')])
        self.assertEqual(a['single_D_pair_mean_kinetic_MeV'],F('153.0767609'))
        self.assertNotEqual(a['mean_cosine'],0)
    def test_single_D_variance_asymmetric(self):
        d=event_ledger(330)['splitting_coefficient_squared_MeV2']
        x=moment_packet(330,[(0,1),(1,3)])
        self.assertEqual(x['single_D_pair_variance_MeV2'],d*F(3,4))
        self.assertEqual(x['labelled_D_cross_covariance_MeV2'],-d*F(3,16))
        self.assertEqual(x['pair_centered_cross_moment_MeV2'],-d*F(3,4))
    def test_even_distribution_labelled_cov(self):
        d=event_ledger(213)['splitting_coefficient_squared_MeV2']
        x=moment_packet(213,[(-1,1),(1,1)])
        self.assertEqual(x['mean_cosine'],0)
        self.assertEqual(x['labelled_D_cross_covariance_MeV2'],-d)
    def test_mu_zero_variance_zero(self):
        x=moment_packet(330,[(0,20)])
        self.assertEqual(x['single_D_pair_variance_MeV2'],0)
    def test_probabilities_scale_invariant(self):
        a=moment_packet(330,[(-1,1),(0,3),(1,2)])
        b=moment_packet(330,[(-1,17),(0,51),(1,34)])
        self.assertEqual(a,b)
    def test_zero_negative_empty_weights_rejected(self):
        for atoms in ([],[(0,0)],[(0,-1)],[(2,1)]):
            with self.assertRaises(ValueError):moment_packet(330,atoms)
    def test_no_implicit_distribution_physical(self):
        a=moment_packet(213,[('0.1','2')])
        self.assertIsNone(a['R_event']);self.assertIsNone(a['thermal_deposition_rate'])
        self.assertEqual(a['input_class'],'MANUFACTURED_DIMENSIONLESS_ANGULAR_WEIGHTS')
    def test_float_and_bool_rejected(self):
        for x in (330.0,True,False,complex(1,0)):
            with self.assertRaises(TypeError):exact(x)
    def test_target_frame_static(self):self.assertEqual(photon_target_energy_squared(330,0,1),330**2)
    def test_target_frame_coflow(self):
        self.assertEqual(photon_target_energy_squared(330,F(3,5),1),F(330**2,4))
    def test_target_frame_counterflow(self):
        self.assertEqual(photon_target_energy_squared(330,F(3,5),-1),4*330**2)
    def test_target_frame_transverse(self):
        self.assertEqual(photon_target_energy_squared(330,F(3,5),0),F(25,16)*330**2)
    def test_invalid_beta_or_mu_rejected(self):
        for e,b,mu in [(-1,0,0),(330,1,1),(330,-1,0),(330,0,2)]:
            with self.assertRaises(ValueError):photon_target_energy_squared(e,b,mu)
    def test_lab_samples(self):
        for e in (213,330):
            for mu in ('-1','0','1/3','1'):
                r=daughter_lab_sample(e,mu,90)
                for k in ('mass_shell_plus_residual_MeV2','mass_shell_minus_residual_MeV2','E_total_residual_MeV','pz_total_residual_MeV'):
                    self.assertLess(abs(Decimal(r[k])),Decimal('1e-75'),(e,mu,k,r[k]))
                self.assertFalse(r['rounding_certified']);self.assertIsNone(r['R_event'])
    def test_lab_sum_matches_exact_pair(self):
        for mu in ('-1','0','1/3','1'):
            r=daughter_lab_sample(330,mu,90)
            self.assertLess(abs(Decimal(r['Ksum_MeV'])-Decimal('306.1535218')),Decimal('1e-75'))
    def test_lab_precision_reject(self):
        with self.assertRaises(ValueError):daughter_lab_sample(330,0,digits=30)
        with self.assertRaises(ValueError):daughter_lab_sample(330,0,digits=True)
    def test_lab_cosine_reject(self):
        with self.assertRaises(ValueError):daughter_lab_sample(330,2)

if __name__=='__main__':unittest.main()
