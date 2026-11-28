from __future__ import annotations
import unittest
import hashlib
import subprocess
import sys
import json
from pathlib import Path
from fractions import Fraction as F
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from exfor_kinematic_atlas import (RAW_SHA256,RAW_GIT_BLOB,M_ALPHA,M_D,Q,E_THRESHOLD,
                                    parse_exfor,two_body,generate)
S=ROOT/'sources/M0475.x4'
class PhysicalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=S.read_bytes()
        cls.data=parse_exfor(cls.raw)
        cls.generated=generate(S,ROOT/'results')

    def test_source_byte_sha(self):
        self.assertEqual(len(self.raw),3349)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),RAW_SHA256)
    def test_original_git_blob(self):
        sha=subprocess.check_output(['git','hash-object',str(S)],text=True).strip()
        self.assertEqual(sha,RAW_GIT_BLOB)
    def test_raw_metadata(self):
        s=self.raw.decode('ascii')
        for sub in ['M0475001','M0475002','M0475003','(COINC,TOF)','(SCIN)','DATA-CM','ERR-S']:
            self.assertIn(sub,s)
    def test_exact_raw_table_row_counts(self):
        self.assertEqual((len(self.data['DA']),len(self.data['SIG'])),(12,6))
    def test_da_source_330(self):
        t={int(x['theta_CM_deg']):(x['DA_nb_sr'],x['ERR_S_nb_sr']) for x in self.data['DA'] if x['E_MeV']==330}
        self.assertEqual(t,{46:(F('0.14'),F('0.03')),61:(F('.16'),F('.05')),73:(F('.07'),F('.05')),87:(F('.19'),F('.05'))})
    def test_sig_source_exact_energies(self):
        self.assertEqual([int(x['E_MeV']) for x in self.data['SIG']],[201,225,253,285,320,359])
        self.assertTrue(all(x['E_MeV']!=330 for x in self.data['SIG']))
    def test_mutation_fails_closed(self):
        raw=self.raw.replace(b'  320.       0.61',b'  330.       0.61')
        with self.assertRaisesRegex(ValueError,'BYTE_IDENTITY'):parse_exfor(raw)
    def test_truncation_fails_closed(self):
        with self.assertRaises(ValueError):parse_exfor(self.raw[:-1])
    def test_mass_defect(self):
        self.assertEqual(Q,F('23.8464782'))
    def test_exact_recoil_threshold(self):
        self.assertEqual(E_THRESHOLD,Q+Q*Q/(2*M_ALPHA))
        self.assertGreater(E_THRESHOLD,Q)
        self.assertAlmostEqual(float(E_THRESHOLD),23.922758940396704,places=12)
    def test_all_sig_exact_weighted(self):
        for row,g in zip(self.data['SIG'],self.generated['data']['SIG']):
            self.assertEqual(F(g['SIG_reported_times_pairK_nb_MeV']),row['SIG_nb']*(row['E_MeV']-Q))
            self.assertEqual(F(g['ERR_S_times_pairK_nb_MeV']),row['ERR_S_nb']*(row['E_MeV']-Q))
    def test_sig_selected_exact_cases(self):
        rows={int(x['gamma_E_lab_MeV']):x for x in self.generated['data']['SIG']}
        self.assertEqual(F(rows[201]['SIG_reported_times_pairK_nb_MeV']),F('426.939987538'))
        self.assertEqual(F(rows[320]['SIG_reported_times_pairK_nb_MeV']),F('180.653648298'))
        self.assertEqual(F(rows[359]['SIG_reported_times_pairK_nb_MeV']),F('184.33443699'))
    def test_all_da_exact_pair_weighted(self):
        for x,g in zip(self.data['DA'],self.generated['data']['DA']):
            self.assertEqual(F(g['DA_times_pairK_nb_MeV_per_sr']),x['DA_nb_sr']*(x['E_MeV']-Q))
            self.assertEqual(F(g['DA_ERR_S_times_pairK_nb_MeV_per_sr']),x['ERR_S_nb_sr']*(x['E_MeV']-Q))
    def test_da_not_sig(self):
        self.assertEqual(self.generated['row_count'],{'DA':12,'SIG':6})
        self.assertEqual(self.generated['interpretation']['330MeV_total_SIG'],'NOT_MEASURED_IN_SOURCE')
        self.assertIsNone(self.generated['interpretation']['R_event'])
    def test_energy_conservation_exact_high_precision(self):
        for row in self.data['DA']:
            d=two_body(row['E_MeV'],row['theta_CM_deg'])
            self.assertLess(abs(d['pair_total_energy_residual_MeV']),mp.mpf('1e-75'))
            self.assertLess(abs(d['pair_momentum_parallel_residual_MeV']),mp.mpf('1e-75'))
            self.assertLess(abs(d['Kplus']+d['Kminus']-mp.mpf(row['E_MeV'].numerator)/row['E_MeV'].denominator+mp.mpf(Q.numerator)/Q.denominator),mp.mpf('1e-75'))
    def test_mass_shell_two_daughters(self):
        for row in self.data['DA']:
            d=two_body(row['E_MeV'],row['theta_CM_deg'])
            self.assertLess(abs(d['shell_residual_plus_MeV2']),mp.mpf('1e-73'))
            self.assertLess(abs(d['shell_residual_minus_MeV2']),mp.mpf('1e-73'))
    def test_physical_energy_positive(self):
        for row in self.data['DA']:
            d=two_body(row['E_MeV'],row['theta_CM_deg'])
            self.assertGreater(d['Kplus'],0)
            self.assertGreater(d['Kminus'],0)
    def test_cm_exchange_not_unique_arm(self):
        for row in self.data['DA']:
            d=two_body(row['E_MeV'],row['theta_CM_deg'])
            flipped=two_body(row['E_MeV'],F(180)-row['theta_CM_deg'])
            self.assertLess(abs(d['Kplus']-flipped['Kminus']),mp.mpf('1e-75'))
            self.assertLess(abs(d['Kminus']-flipped['Kplus']),mp.mpf('1e-75'))
    def test_threshold_reject(self):
        with self.assertRaises(ValueError):two_body(E_THRESHOLD-F('0.001'),F(60))
    def test_bad_angle_reject(self):
        for a in [F(-1),F(181)]:
            with self.assertRaises(ValueError):two_body(F(330),a)
    def test_kinematic_pair_total_independent_of_angle(self):
        a=[two_body(F(330),F(x)) for x in (0,46,61,73,87,180)]
        means=[(d['Kplus']+d['Kminus'])/2 for d in a]
        self.assertLess(max(means)-min(means),mp.mpf('1e-75'))
    def test_per_row_error_is_not_joint_covariance(self):
        self.assertEqual(self.generated['source']['stat_error_type'],'ERR-S')
        self.assertNotIn('covariance_matrix',self.generated)
    def test_kinetic_product_is_not_heat(self):
        i=self.generated['interpretation']
        self.assertEqual(i['pair_Ksum'],'kinematic identity, NOT heat')
        self.assertFalse(i['physical_activation'])
        self.assertEqual(i['production'],'HOLD')

if __name__=='__main__':unittest.main(verbosity=2)
