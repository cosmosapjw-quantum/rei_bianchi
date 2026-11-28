"""Source-owned M0826 normalization witness: no inferred absolute rates."""
import importlib.util
import math
import shutil
from pathlib import Path
import unittest
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('atlas',ROOT/'src'/'build_m0826_event_consistency.py')
atlas=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(atlas)

class SourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=atlas.build(ROOT)
        cls.x=cls.out['cross_comparison']
    def test_source_data_counts(self):
        self.assertEqual(self.out['source_observation_counts'],
                         {'M0826003_angular_bin_DA':9,'M0826002_total_SIG_energy_bins':4,'M0011002_total_SIG_energy_points':14})
    def test_original_angular_integration(self):
        self.assertAlmostEqual(self.x['inclusive_daughter_4pi_microbarn'],5.430601681837213,places=12)
    def test_half_event(self):
        self.assertAlmostEqual(self.x['conditional_event_one_half_angular_microbarn'],2.7153008409186064,places=12)
    def test_source_SIG_mean(self):
        self.assertEqual(self.x['equal_width_SIG_energy_bin_mean_microbarn'],2.705)
    def test_direct_comparison(self):
        self.assertAlmostEqual(self.x['DA_integral_divided_by_SIG_mean'],2.007616148553498,places=12)
        self.assertAlmostEqual(self.x['event_minus_SIG_mean_microbarn'],0.0103008409186064,places=12)
    def test_independent_uncertainty_only(self):
        self.assertAlmostEqual(self.x['conditional_independent_DA_STAT_SD_event_microbarn'],0.35129532967193405,places=12)
        self.assertAlmostEqual(self.x['conditional_independent_SIG_STAT_SD_mean_microbarn'],0.45609757727924843,places=12)
    def test_unknown_covariance_not_assumed(self):
        self.assertEqual(self.x['joint_experimental_covariance'],'UNKNOWN')
        self.assertGreater(self.x['arbitrary_positive_covariance_DA_STAT_SD_event_upper_microbarn'],0.9)
    def test_no_physical_activation(self):
        p=self.out['physical_claims']
        self.assertIsNone(p['sigma_event_gamma_He4_dd'])
        self.assertIsNone(p['R_event'])
        self.assertIsNone(p['heat_rate'])
        self.assertFalse(p['L4'])
    def test_source_tampering_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'sources').mkdir()
            for key in atlas.SOURCE_SHA256:
                shutil.copyfile(ROOT/'sources'/f'{key}.x4',p/'sources'/f'{key}.x4')
            target=p/'sources'/'M0826.x4'
            target.write_bytes(target.read_bytes().replace(b'2.94',b'3.94',1))
            with self.assertRaisesRegex(ValueError,'SOURCE_SHA256_MISMATCH'):
                atlas.build(p)
    def test_original_M0011_preserved(self):
        self.assertEqual(self.out['original_M0011_SIG_points'][0]['SIG_microbarn'],0.87)
        self.assertEqual(self.out['original_M0011_SIG_points'][-1]['EN_MeV'],65.0)
    def test_M0826_per_bin_explicit(self):
        bins=self.out['original_M0826_SIG_energy_bins']
        self.assertEqual(bins[0]['SIG_microbarn'],2.94)
        self.assertEqual(bins[1]['SIG_microbarn'],2.47)
        self.assertEqual(bins[2]['SIG_microbarn'],0.79)
        self.assertEqual(bins[3]['SIG_microbarn'],1.14)
    def test_exposure_not_invented(self):
        self.assertEqual(self.x['equal_energy_width_comparison'],'ASSUMPTION_NO_FLUX_HISTORY')
        self.assertEqual(self.x['DA_source_inclusive_daughter_interpretation'],'SUPPORTED_BY_CONSISTENCY_NOT_ORIGINALLY_CONFIRMED')

if __name__=='__main__':unittest.main()
