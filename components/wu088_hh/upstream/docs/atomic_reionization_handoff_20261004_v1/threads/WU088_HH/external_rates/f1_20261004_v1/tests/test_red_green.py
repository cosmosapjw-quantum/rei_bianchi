import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hh_external import evaluate_reference,rate_source,application_gate

class RequiredBehavior(unittest.TestCase):
    def result(self,*args):
        try:return evaluate_reference(*args)
        except Exception as e:self.fail('required provider response unavailable: '+str(e))
    def test_crossing_keeps_both_branches(self):
        x=self.result('LCS91','2999','3001')
        self.assertEqual([p['branch'] for p in x['pieces']],['ARTIFICIAL_FLOOR','ANALYTIC'])
        self.assertEqual(x['boundary_status'],'NONSMOOTH_3000K')
        self.assertIsNone(x['derivatives_global'])
    def test_boundary_has_no_derivative(self):
        x=self.result('LCS91','3000')
        self.assertEqual(x['rate_cm3_s'],['1E-20','1E-20'])
        self.assertIsNone(x['pieces'][0]['d1_cm3_s_K'])
    def test_ks_has_no_floor(self):
        x=self.result('KS92_corrected_Glover15','2999','3001')
        self.assertEqual(len(x['pieces']),1)
        self.assertEqual(x['boundary_status'],'SMOOTH_ANALYTIC')
        self.assertEqual(x['canonical_provider'],'GLOVER2015_KS91_EQ14')
    def test_no_extra_half_and_shared_energy(self):
        x=self.result('LCS91','2000')
        try:s=rate_source(x,'2','3')
        except Exception as e:self.fail('required source absent: '+str(e))
        self.assertEqual(s['event_rate_m3_s'],['4E-26','4E-26'])
        self.assertEqual(s['energy_sum_J_m3_s'],['0','0'])
        self.assertEqual(s['electron_delta_per_event'],1)
    def test_missing_domain_returns_explicit_fields(self):
        g=application_gate({})
        self.assertIn('temperature_K',g['missing'])
        self.assertIn('observable_budget',g['missing'])
        self.assertFalse(g['physical_admission'])

if __name__=='__main__':unittest.main()
