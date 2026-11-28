"""Scoped, source-locked tests; not an end-to-end BASS_HE science suite."""
import sys,unittest,tempfile
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from reciprocity import *

class ReciprocityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=ROOT/'source/M0475.x4'
    def test_source_twelve_rows(self):self.assertEqual(len(read_DA(self.src)),12)
    def test_packaged_default_source(self):self.assertEqual(len(read_DA()),12)
    def test_source_three_energies(self):self.assertEqual(sorted(set(r[0] for r in read_DA(self.src))),[213,258,330])
    def test_213_row_73(self):self.assertIn((F(213),F(73),F('0.41'),F('0.09')),read_DA(self.src))
    def test_330_row_73(self):self.assertIn((F(330),F(73),F('0.07'),F('0.05')),read_DA(self.src))
    def test_exact_213_Td(self):self.assertLess(abs(float(T_matching(213))-375.7505606070078),1e-12)
    def test_exact_330_Td(self):self.assertLess(abs(float(T_matching(330))-608.2630266481291),1e-12)
    def test_376_corresponds_213_not_330(self):
        self.assertLess(abs(float(E_matching(376))-213.12551760977376),1e-12)
        self.assertNotEqual(E_matching(376),F(330))
    def test_inverse_round_trip(self):
        for e in [F(213),F(258),F(330),F(1,2)+gamma_threshold()]:
            self.assertEqual(E_matching(T_matching(e)),e)
    def test_invariant_s_match(self):
        for e in [213,330]:self.assertEqual(s_gamma(e),s_dd(T_matching(e)))
    def test_mismatch_diagnostic(self):
        r=alignment(213,376)
        self.assertFalse(r['same_s']);self.assertNotEqual(r['delta_s_MeV2'],0)
    def test_exact_match_diagnostic(self):self.assertTrue(alignment(213,T_matching(213))['same_s'])
    def test_source_213_376_refusal(self):
        with self.assertRaisesRegex(ValueError,'invariant-energy mismatch'):
            conditional_inverse_DA(213,73,ORDERED,self.src,376)
    def test_threshold_positive(self):self.assertGreater(gamma_threshold(),0)
    def test_threshold_kinematics_zero_rejected(self):
        with self.assertRaises(ValueError):cm_momenta_squared(gamma_threshold())
    def test_near_threshold_finite(self):
        e=gamma_threshold()+F(1,1000000)
        self.assertGreater(reciprocity_ratio(e,ORDERED),0)
    def test_negative_energy_rejected(self):
        for f in (s_gamma,s_dd):
            with self.assertRaises(ValueError):f(-1)
    def test_rounded_input_rejected(self):
        for x in [1.5,True,False]:
            with self.assertRaises(ValueError):exact(x)
    def test_spin_degeneracy(self):self.assertEqual(F(2,9),F(2*1,3*3))
    def test_ratio_exact_formula(self):
        for e in (213,258,330):
            s=s_gamma(e)
            self.assertEqual(reciprocity_ratio(e,ORDERED),F(2,9)*(s-MA**2)**2/(s*(s-4*MD**2)))
    def test_ratio_convention_factor(self):
        for e in (213,330):self.assertEqual(reciprocity_ratio(e,FULL_EVENT),2*reciprocity_ratio(e,ORDERED))
    def test_ratio_numeric_330(self):
        self.assertLess(abs(float(reciprocity_ratio(330,ORDERED))-0.03604202060960059241),1e-16)
    def test_source_interval_213_73(self):
        a=conditional_inverse_DA(213,73,ORDERED,self.src)
        self.assertEqual(a['inverse_lower_nb_sr'],F('0.32')*reciprocity_ratio(213,ORDERED))
        self.assertEqual(a['inverse_upper_nb_sr'],F('0.50')*reciprocity_ratio(213,ORDERED))
    def test_source_interval_330_73(self):
        a=conditional_inverse_DA(330,73,ORDERED,self.src)
        self.assertEqual(a['inverse_lower_nb_sr'],F('0.02')*reciprocity_ratio(330,ORDERED))
        self.assertEqual(a['inverse_upper_nb_sr'],F('0.12')*reciprocity_ratio(330,ORDERED))
    def test_unknown_source_convention_rejected(self):
        with self.assertRaises(ValueError):conditional_inverse_DA(213,73,'physical_event',self.src)
    def test_source_missing_row_rejected(self):
        with self.assertRaises(ValueError):conditional_inverse_DA(213,90,ORDERED,self.src)
    def test_mutated_source_rejected(self):
        raw=self.src.read_bytes()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'M0475.x4';p.write_bytes(raw.replace(b'0.41',b'0.42'))
            with self.assertRaises(ValueError):read_DA(p)
    def test_thermal_pair_factor_distinct(self):
        self.assertEqual(THERMAL_DD_PAIR_FACTOR,F(1,2))
        self.assertNotEqual(THERMAL_DD_PAIR_FACTOR,reciprocity_ratio(213,ORDERED))
    def test_event_conservation(self):
        for e in [gamma_threshold(),213,330]:
            r=forward_event_ledger(e)
            self.assertEqual((r['energy_residual_MeV'],r['baryon_residual'],r['charge_residual']),(0,0,0))
            self.assertFalse(r['physical_activation'])
    def test_lab_boost_mass_shell(self):
        with mp.workdps(60):
            for e in [213,330]:
                for mu in ['-1','0','1/3','1']:
                    a=lab_daughters(e,mu,80)
                    for key in ['E_sum_residual_MeV','pz_sum_residual_MeV','mass_shell_plus_residual_MeV2','mass_shell_minus_residual_MeV2']:
                        self.assertLess(abs(mp.mpf(a[key])),mp.mpf('1e-50'))
    def test_lab_daughter_sum_exact(self):
        with mp.workdps(50):
            r=lab_daughters(330,'1/3',75)
            self.assertLess(abs(mp.mpf(r['E_plus_MeV'])+mp.mpf(r['E_minus_MeV'])-mp.mpf('4057.3794118')),mp.mpf('1e-55'))
    def test_no_physical_source_admission(self):
        for e in [213,330]:
            for conv in [ORDERED,FULL_EVENT]:
                r=conditional_inverse_DA(e,73,conv,self.src)
                self.assertIsNone(r['inverse_measured']);self.assertIsNone(r['event_rate'])
                self.assertFalse(r['physical_activation']);self.assertFalse(r['L4'])
    def test_angular_source_not_joint_ci(self):
        r=conditional_inverse_DA(213,73,ORDERED,self.src)
        self.assertIn('not_joint_CI',r['uncertainty'])

if __name__=='__main__':unittest.main(verbosity=2)
