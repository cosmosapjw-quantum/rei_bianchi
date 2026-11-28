"""Targeted change-scope regression, not a BASS_HE full-science suite."""
import sys
from pathlib import Path
import unittest
from fractions import Fraction as F
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from nonthermal_d_birth import *

class BirthLedger(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(2*K0_MEV, GAMMA_MEV + HE4_REST_MEV-2*D_REST_MEV)
    def test_exact_SI(self):
        self.assertEqual(MEV_TO_J, F(1602176634,10**28)*10**6)
    def test_missing_not_zero(self):
        s=birth_source()
        self.assertIsNone(s['event_rate_m3_s'])
        self.assertIsNone(s['event_energy_residual_J_m3_s'])
        self.assertFalse(s['physical_activation'])
    def test_missing_rate_with_class_rejected(self):
        with self.assertRaises(ValueError):birth_source(source_class=REQUIRED_CLASS)
    def test_manufactured_baryon_charge(self):
        s=birth_source('3/2',source_class=REQUIRED_CLASS)
        self.assertEqual(s['fast_D_count_m3_s'],3)
        self.assertEqual(s['he4_count_m3_s'],-F(3,2))
        self.assertEqual(s['baryon_number_residual_m3_s'],0)
        self.assertEqual(s['charge_residual_m3_s'],0)
    def test_energy_partition(self):
        s=birth_source('3/2',source_class=REQUIRED_CLASS)
        self.assertEqual(s['event_energy_residual_J_m3_s'],0)
        self.assertEqual(s['fast_D_kinetic_J_m3_s'],3*K0_MEV*MEV_TO_J)
    def test_beam_momentum(self):
        s=birth_source('2',source_class=REQUIRED_CLASS,photon_direction=(0,0,1))
        self.assertEqual(s['event_momentum_residual_N_m3'],(0,0,0))
        self.assertEqual(s['fast_D_total_momentum_N_m3'][2],2*GAMMA_MEV*MEV_TO_J/C_M_S)
    def test_oblique_momentum(self):
        s=birth_source('1',source_class=REQUIRED_CLASS,photon_direction=('3/5','4/5',0))
        self.assertEqual(s['event_momentum_residual_N_m3'],(0,0,0))
    def test_no_direction_does_not_assume_zero(self):
        s=birth_source('1',source_class=REQUIRED_CLASS)
        self.assertIsNone(s['fast_D_total_momentum_N_m3'])
    def test_no_thermalization_or_closure(self):
        s=birth_source(1,source_class=REQUIRED_CLASS)
        for name in ('thermal_deposition_J_m3_s','Gamma_thermal','Cv','coupled_population_RHS','daughter_pressure_tensor'):
            self.assertIsNone(s[name])
    def test_no_physical_promotion(self):
        s=birth_source(1,source_class=REQUIRED_CLASS)
        self.assertFalse(s['physical_pool_admitted']);self.assertFalse(s['L4'])
    def test_zero_rate_manufactured(self):
        s=birth_source(0,source_class=REQUIRED_CLASS,photon_direction=(0,0,1))
        self.assertEqual(s['fast_D_count_m3_s'],0)
    def test_bad_float_and_bool(self):
        for q in (0.4,True):
            with self.assertRaises(ValueError):birth_source(q,source_class=REQUIRED_CLASS)
    def test_negative(self):
        with self.assertRaises(ValueError):birth_source('-1/4',source_class=REQUIRED_CLASS)
    def test_bad_frame(self):
        with self.assertRaises(ValueError):birth_source(1,source_class=REQUIRED_CLASS,frame='FLRW_GLOBAL')
    def test_bad_source_class(self):
        with self.assertRaises(ValueError):birth_source(1,source_class='PHYSICAL')
    def test_non_unit_dir(self):
        with self.assertRaises(ValueError):birth_source(1,source_class=REQUIRED_CLASS,photon_direction=(1,1,0))
    def test_bad_dir_components(self):
        with self.assertRaises(ValueError):birth_source(1,source_class=REQUIRED_CLASS,photon_direction=(1,0))
if __name__ == '__main__':unittest.main()
