import unittest
import sys
import tempfile
from pathlib import Path
from fractions import Fraction
import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'src'))
from experimental_shape_atlas import parse_original, build, contrast, git_blob, EXPECTED_SOURCE_GIT_BLOB, fit_models, generate

class MeasuredShapeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ROOT/'sources/M0475.x4'
        cls.rows = parse_original(cls.source)
        cls.out = build(cls.source)

    def test_01_source_identity_exact(self):
        self.assertEqual(git_blob(self.source.read_bytes()), EXPECTED_SOURCE_GIT_BLOB)
        self.assertEqual(len(self.source.read_bytes()), 3349)

    def test_02_source_tamper_closed(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d)/'M0475.x4'; f.write_bytes(self.source.read_bytes()+b'#')
            with self.assertRaises(ValueError):parse_original(f)

    def test_03_differential_source_provenance(self):
        self.assertEqual(len(self.rows), 12)
        self.assertEqual(sorted(set(x['E_gamma_MeV'] for x in self.rows)), [213,258,330])
        self.assertEqual(sorted(set(x['theta_CM_deg'] for x in self.rows)), [46,61,73,87])

    def test_04_original_values_and_errs(self):
        s={(r['E_gamma_MeV'],r['theta_CM_deg']):(r['DA_nb_per_srCM'],r['ERR_S_nb_per_srCM']) for r in self.rows}
        self.assertEqual(s[213,46],(Fraction(11,50),Fraction(1,25)))
        self.assertEqual(s[213,87],(Fraction(27,50),Fraction(1,10)))
        self.assertEqual(s[258,46],(Fraction(2,25),Fraction(3,100)))
        self.assertEqual(s[330,46],(Fraction(7,50),Fraction(3,100)))
        self.assertEqual(s[330,87],(Fraction(19,100),Fraction(1,20)))

    def test_05_no_measured_330_total(self):
        self.assertIsNone(self.out['admissibility']['source_330_total_SIG'])
        self.assertIsNone(self.out['admissibility']['R_event'])

    def test_06_exact_contrast_213(self):
        c=contrast(self.rows[0],self.rows[3],'WITHIN_ENERGY_ANGLE_PAIR')
        self.assertEqual(c['contrast_exact'],'8/19')
        self.assertEqual(c['ERR_S_box_min_exact'],'9/35')
        self.assertEqual(c['ERR_S_box_max_exact'],'23/41')

    def test_07_exact_contrast_258(self):
        c=contrast(self.rows[4],self.rows[7],'WITHIN_ENERGY_ANGLE_PAIR')
        self.assertEqual(c['contrast_exact'],'17/33')
        self.assertEqual(c['ERR_S_box_min_exact'],'7/29')
        self.assertEqual(c['ERR_S_box_max_exact'],'27/37')

    def test_08_exact_contrast_330(self):
        c=contrast(self.rows[8],self.rows[11],'WITHIN_ENERGY_ANGLE_PAIR')
        self.assertEqual(c['contrast_exact'],'5/33')
        self.assertEqual(c['ERR_S_box_min_exact'],'-3/31')
        self.assertEqual(c['ERR_S_box_max_exact'],'13/35')

    def test_09_monotonic_source_box_bounds_all(self):
        for c in self.out['pairwise_shape_contrasts']:
            self.assertLessEqual(c['ERR_S_box_min'],c['contrast'])
            self.assertLessEqual(c['contrast'],c['ERR_S_box_max'])
            self.assertGreaterEqual(c['delta_sigma_covariance_unknown_min'],0)
            self.assertLessEqual(c['delta_sigma_covariance_unknown_min'],c['delta_sigma_independent_ONLY'])
            self.assertLessEqual(c['delta_sigma_independent_ONLY'],c['delta_sigma_covariance_unknown_max'])

    def test_10_cardinality_and_non_independence(self):
        self.assertEqual(len(self.out['pairwise_shape_contrasts']),30)
        self.assertEqual(sum(c['dimension']=='WITHIN_ENERGY_ANGLE_PAIR' for c in self.out['pairwise_shape_contrasts']),18)
        self.assertEqual(sum(c['dimension']=='FIXED_ANGLE_ENERGY_PAIR' for c in self.out['pairwise_shape_contrasts']),12)
        self.assertEqual(len(self.out['statistical_fit_diagnostics']),9)

    def test_11_213_measured_fit(self):
        fits={z['model']:z for z in self.out['statistical_fit_diagnostics'] if z['E_gamma_MeV']==213}
        self.assertAlmostEqual(fits['sin_squared']['chi_squared_conditional_independent_ERR_S'],0.8761462424937408)
        self.assertAlmostEqual(fits['constant']['chi_squared_conditional_independent_ERR_S'],11.522317490561377)
        self.assertAlmostEqual(fits['sin_squared']['pvalue_conditional_Gaussian_independent'],chi2.sf(0.8761462424937408,3))

    def test_12_330_not_overclaim(self):
        fits={z['model']:z for z in self.out['statistical_fit_diagnostics'] if z['E_gamma_MeV']==330}
        self.assertAlmostEqual(fits['constant']['chi_squared_conditional_independent_ERR_S'],3.12)
        self.assertGreater(fits['sin_squared']['pvalue_conditional_Gaussian_independent'],0.05)
        self.assertTrue(all('conditional' in str(k) for k in fits['constant'] if 'chi_squared_' in k))

    def test_13_quartic_positive_over_full_angle_range(self):
        for z in self.out['statistical_fit_diagnostics']:
            if z['model']=='even_quartic':
                a,b=z['parameters_nb_per_srCM'];self.assertGreater(a,0);self.assertGreater(a+b,0)

    def test_14_source_observations_not_reconstructed(self):
        self.assertEqual(self.out['original_measured_rows'][0]['DA_nb_per_srCM_exact'],'11/50')
        self.assertEqual(self.out['original_measured_rows'][11]['DA_nb_per_srCM_exact'],'19/100')
        self.assertEqual(self.out['admissibility']['production'],'HOLD')
        self.assertEqual(self.out['admissibility']['central_DAG'],'28/88')

    def test_15_source_generated_outputs_reproducible(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'sources').mkdir()
            (root/'sources/M0475.x4').write_bytes(self.source.read_bytes())
            generate(root)
            import json
            actual=json.loads((root/'results/SOURCE_ANGULAR_SHAPES.json').read_text())
            self.assertEqual(actual,self.out)
            self.assertEqual((root/'results/MEASURED_30_SHAPE_CONTRASTS.csv').read_text().count('\n'),31)
            self.assertEqual((root/'results/SOURCE_9_SHAPE_MODEL_FITS.csv').read_text().count('\n'),10)

if __name__=='__main__':unittest.main()
