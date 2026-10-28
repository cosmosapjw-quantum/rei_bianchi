"""Small saved-result controls. Does NOT rerun exact 256-corner source worker."""
from pathlib import Path
import unittest,json,hashlib,math

R=Path(__file__).resolve().parents[1]
source=R/'source/FROZEN_BB13_SUPPORT_INPUT.json'
inp=json.loads(source.read_text())
out=json.loads((R/'results/EXACT_SUPPORT.json').read_text())
ref=json.loads((R/'results/NUMPY_REFERENCE.json').read_text())

class StoredSupportTests(unittest.TestCase):
    def test_input_identity(self):
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),'13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b')
        self.assertEqual(inp['original_source_observation_git_blob'],'61c1ecdcb1be05d47bb59165fb4cac8bb14deb52')
        self.assertEqual(inp['original_saved_calibration_git_blob'],'abd45812fb38691bcc76b5bddd33c55e2e5e4be3')
    def test_unchanged_source_grid(self):
        self.assertEqual(inp['z'],[2.4,2.8,3.2,3.6,4,4.4,4.75])
        self.assertEqual(inp['eos_theta_bounds'],[-1,1]);self.assertEqual(out['n_gls'],7)
    def test_actual_saved_exact_controls(self):
        self.assertEqual(out['corner_count'],256)
        self.assertTrue(all(out['controls'].values()))
        self.assertEqual(out['covariance_LDL_exact_pivots_positive'],7)
    def test_exact_numpy_value_comparison(self):
        t=out['nuisance_support']
        for k in ('kappa_min','kappa_max','beta_min','beta_max'):
            self.assertLessEqual(abs(float(t[k])-ref[k]),inp['test_tolerance_abs']+inp['test_tolerance_rel']*abs(ref[k]))
    def test_kappa_signed_exclusion_conditional(self):
        t=out['nuisance_support']; self.assertGreater(float(t['kappa_min']),0)
        self.assertLess(float(t['kappa_min']),float(t['kappa_max']))
        self.assertEqual(t['kappa_min_witness']['theta'],1);self.assertEqual(t['kappa_max_witness']['theta'],-1)
        self.assertEqual(t['kappa_min_witness']['gamma_TDR'],1.6)
        self.assertEqual(t['kappa_max_witness']['gamma_TDR'],1.2)
    def test_projected_slope_normalization(self):
        a=[float(v) for v in out['nuisance_support']['kappa_weights_d_perbin']]
        self.assertLess(abs(sum(a)),5e-15)
        self.assertLess(abs(sum(w*(z-3.6) for w,z in zip(a,inp['z']))-1),5e-15)
    def test_eos_jeans_additivity(self):
        t=out['nuisance_support'];width=(float(t['kappa_max'])-float(t['kappa_min']))/2
        self.assertLess(abs(width-float(t['kappa_EOS_halfwidth'])-float(t['kappa_Jeans_halfwidth'])),1e-14)
    def test_scope_and_null_claims(self):
        self.assertEqual(out['claim'],'CONDITIONAL_DETERMINISTIC_OUTER_BOX_NOT_STATISTICAL_INDEPENDENCE')
        self.assertIsNone(out['actual_REI_T']);self.assertIsNone(out['physical_radii'])
        self.assertEqual(out['new_IVP'],0)
        self.assertEqual(out['original_DAG_working'],'33/88')

if __name__=='__main__':unittest.main(verbosity=2)
