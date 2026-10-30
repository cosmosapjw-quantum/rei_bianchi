import importlib.util
import pathlib
import tempfile
import unittest
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pair_joint', ROOT/'code/pair_joint.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PairJointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.grid,cls.summary,cls.aux=m.calculate(8)
    def test_archive_identity(self):
        self.assertEqual(m.sha(m.SRC283),m.SHA_283)
    def test_negative_archive_sha_guard(self):
        hold=m.SHA_283
        try:
            m.SHA_283='0'*64
            with self.assertRaisesRegex(ValueError,'SOURCE_ZIP_SHA'):m.read_owner()
        finally:m.SHA_283=hold
    def test_193_times_25(self):
        self.assertEqual((len(self.rows),len(self.grid)),(193,4825))
        self.assertEqual(self.summary['shape']['epochs'],193)
    def test_pair_probability(self):
        for row in self.rows:
            self.assertLess(abs(sum(float(row['P_'+q+'_absorbed']) for q in ['zero','one','two'])-1),4e-13)
        self.assertLess(np.max(abs(self.aux['joint'].sum(axis=(1,2))-1)),4e-13)
    def test_category_channel_probability_nonnegative(self):
        self.assertTrue(np.all(self.aux['joint']>=0))
        self.assertTrue(np.all(self.aux['indep']>=0))
    def test_pair_electron_first_moment(self):
        for row in self.rows:
            target=float(row['P_one_absorbed'])+2*float(row['P_two_absorbed'])
            self.assertLess(abs(target-float(row['mean_photoelectrons_per_singlet_pair'])),1e-13)
    def test_marginal_joint_independence_not_equal(self):
        err=[float(r['two_photon_joint_TV_vs_marginal_independence']) for r in self.rows]
        self.assertGreater(max(err),.1)
        self.assertLess(max(err),1.)
    def test_covariance_changes_sign(self):
        v=[float(r['event_correlation_covariance']) for r in self.rows]
        self.assertLess(min(v),-.01)
        self.assertGreater(max(v),.01)
    def test_HeII_cannot_be_lower_energy_absorber(self):
        j=m.CATEGORIES.index('He_II')
        self.assertTrue(np.all(self.aux['joint'][:,j,:]==0))
    def test_photons_both_above_HeII_threshold_impossible(self):
        self.assertLess(2*54.417765486,2*60.922559447552)
        self.assertGreater(2*54.417765486,60.922559447552)
    def test_conservation_of_source_rate(self):
        for r in self.rows:
            inrate=r['conditional_all_singlet_pair_rate_per_baryon_s']
            outrate=sum(r['conditional_pair_source_'+k+'_absorbed_per_baryon_s'] for k in ['zero','one','two'])
            self.assertLess(abs(inrate-outrate),max(1e-70,abs(inrate)*4e-13))
    def test_original_DAG_unchanged(self):
        self.assertEqual(self.summary['DAG']['working'],'33/88')
        self.assertEqual(self.summary['DAG']['central'],'28/88')
        self.assertEqual(self.summary['DAG']['physical_fast'],'4/7')
        self.assertEqual(self.summary['DAG']['delta'],0)
        self.assertEqual(self.summary['boundaries']['new_IVPs'],0)
    def test_original_source_uncertainty_preserved(self):
        self.assertEqual(self.summary['source_table']['visual_scan'],'UNVERIFIED')
        self.assertEqual(self.summary['boundaries']['actual_pair_emission'],'UNBOUND')
        self.assertEqual(self.summary['boundaries']['gas_heat'],'UNBOUND')
    def test_converged_Gauss_4_8_16(self):
        ref=self.summary
        for order in [4,16]:
            _,_,d,_=m.calculate(order)
            for key in ['zero_absorbed','one_absorbed','two_absorbed','expected_photoelectrons']:
                x=d['integrated_conditional_events_per_baryon'][key]
                y=ref['integrated_conditional_events_per_baryon'][key]
                self.assertLess(abs(x-y),max(1e-27,2e-12*abs(y)))
    def test_total_source_events_is_old_singlet_allowed(self):
        s=self.summary['integrated_conditional_events_per_baryon']
        self.assertAlmostEqual((s['zero_absorbed']+s['one_absorbed']+s['two_absorbed'])/s['source_pairs'],1,places=12)
        self.assertAlmostEqual((s['one_absorbed']+2*s['two_absorbed'])/s['expected_photoelectrons'],1,places=12)
    def test_no_ivp_in_code(self):
        src=(ROOT/'code/pair_joint.py').read_text()
        self.assertNotIn('solve_ivp(',src)
        self.assertNotIn('odeint(',src)

if __name__=='__main__':unittest.main()
