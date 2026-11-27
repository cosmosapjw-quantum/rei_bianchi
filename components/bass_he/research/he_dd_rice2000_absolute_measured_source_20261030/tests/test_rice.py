import unittest
import json
import math
import sys
from decimal import Decimal as D
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
import build_rice as m

class RiceSourceAndPhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.raw, cls.fit, cls.thesis = m.load_sources(ROOT); cls.atlas=m.science(ROOT)
    def test_original_immutable_sources(self):self.assertEqual(len(m.SOURCE_HASHES),4)
    def test_lit_differential_12_not_24(self):self.assertEqual(len(self.atlas['observations']),12)
    def test_two_energy_bins(self):self.assertEqual(set(self.atlas['energy_bins']),{'150-190','190-250'})
    def test_cm_angles_source(self):self.assertEqual(self.atlas['observations'][0]['theta_cm'],44.7)
    def test_cm_angles_high_source(self):self.assertEqual(self.atlas['observations'][8]['theta_cm'],91.4)
    def test_published_12_values(self):self.assertEqual([r['sigma'] for r in self.atlas['observations']],[.77,1.26,2.32,1.73,1.50,1.03,.14,.59,1.42,1.11,.68,.43])
    def test_reported_total_eight_alternative_fits(self):self.assertEqual(len(self.atlas['alternative_author_fit_rows']),8)
    def test_total_factor_two_identical_d(self):self.assertAlmostEqual(2*math.pi*1.32,8.29,delta=.02)
    def test_author_fit_anomaly_preserved(self):
        issues=self.atlas['fit_author_identity_discrepancies'];self.assertEqual(len(issues),1)
        self.assertEqual(issues[0]['author_total'],'8.32')
    def test_systematic_7_1_and_13(self):self.assertEqual([self.atlas['energy_bins'][x]['reported_sys_total_fraction'] for x in ['150-190','190-250']],[.071,.13])
    def test_systematic_correlation_unresolved(self):self.assertIsNone(self.atlas['sys_decomposition_from_thesis']['source_covariance_matrix'])
    def test_source_1998_different_not_new_experiment(self):
        x=self.atlas['preliminary_1998_vs_2000'];self.assertEqual(len(x),6)
        self.assertGreater(float(x[0]['published_over_thesis_ratio']),1.20)
    def test_source_1998_truncated(self):self.assertFalse(self.atlas['raw_pdf_1998_complete'])
    def test_x4_request_not_rice(self):self.assertEqual(self.atlas['X4R8587_role'].count('M0826'),1)
    def test_threshold(self):self.assertAlmostEqual(float(m.threshold()),23.9227589404,places=9)
    def test_ratio_threshold_protection(self):
        with self.assertRaises(ValueError):m.cap_to_photo_ordered(m.threshold())
    def test_ratio_monotonic_150_250(self):
        vals=[m.cap_to_photo_ordered(i) for i in range(150,251)]
        self.assertTrue(all(a<b for a,b in zip(vals,vals[1:])))
    def test_ratio_ordered_vs_full_sphere_event(self):self.assertEqual(m.cap_to_photo_event_full_sphere(190),2*m.cap_to_photo_ordered(190))
    def test_exact_same_s(self):
        for eg in [D('150'),D('190'),D('250')]:
            td=m.matching_Td(eg)
            self.assertLess(abs((4*m.MD**2+2*m.MD*td)-m.s_gamma(eg)),D('1e-18'))
    def test_pair_birth_energy_conservation(self):
        for lo,hi in [('150','190'),('190','250')]:
            pair=self.atlas['energy_bins'][f'{lo}-{hi}']['pair_birth_kinetic_support_MeV']
            self.assertEqual(D(pair[0]),D(lo)-m.Q); self.assertEqual(D(pair[1]),D(hi)-m.Q)
    def test_silverman1984_1984_factor_38_9(self):
        # Silverman PRC 29 (1984) Fig.1 reported 38.9 detailed-balance factor at E_gamma~213 MeV.
        self.assertAlmostEqual(float(1/m.cap_to_photo_ordered(213)),38.9,delta=.07)
    def test_bin_are_not_monochromatic_points(self):
        for row in self.atlas['observations']:
            self.assertFalse(row['at_exact_measured_E'])
            self.assertGreater(row['Emax'],row['Emin'])
    def test_legendre_models_not_independent_observations(self):
        self.assertTrue(all(x['source_is_alternative_fit_not_independent_measurement'] for x in self.atlas['alternative_author_fit_rows']))
    def test_systematic_budget_reconstruction(self):
        d=self.atlas['sys_decomposition_from_thesis']['quadrature_percent']
        self.assertAlmostEqual(float(d['150-190']),7.1,delta=.05)
        self.assertAlmostEqual(float(d['190-250']),13.0,delta=.15)
    def test_gate_stays_hold(self):self.assertIsNone(self.atlas['gates']['R_event']);self.assertFalse(self.atlas['gates']['L4'])
    def test_zero_canonical_dag_promotion(self):self.assertEqual(self.atlas['DAG']['canonical_physical_delta'],0)
    def test_1998_not_double_counted(self):self.assertEqual(self.atlas['independent_original_campaigns'],1)
    def test_derive_deterministic(self):
        before=(ROOT/'results'/'RICE_2000_ABSOLUTE_ATLAS.json').read_bytes()
        m.dump(ROOT)
        self.assertEqual(before,(ROOT/'results'/'RICE_2000_ABSOLUTE_ATLAS.json').read_bytes())

if __name__=='__main__':unittest.main()
