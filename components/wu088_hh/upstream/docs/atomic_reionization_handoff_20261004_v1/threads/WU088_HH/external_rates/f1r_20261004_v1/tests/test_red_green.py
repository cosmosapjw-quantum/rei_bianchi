import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from hh_source_jet import log_jet,source_jet,taylor_step,ProviderError

class NewContract(unittest.TestCase):
    def test_log_temperature_third_derivative_exists(self):
        got=log_jet('LCS91','10000')
        self.assertIsInstance(got,dict)
        self.assertEqual(len(got['global_dlogT_m3_s']),4)
    def test_mixed_source_jet(self):
        got=source_jet('LCS91','10000','2','3e-18')
        self.assertIsInstance(got,dict)
        self.assertEqual(set(got['hessian']),{'nn','ny','yy'})
    def test_remainder_is_explicit(self):
        got=taylor_step('LCS91','10000','2','0.1','0.2','3e-18')
        self.assertIsInstance(got,dict)
        self.assertIn('event_remainder_abs_upper_m3_s',got)
        self.assertFalse(got['admission'])
    def test_cutoff_crossing_not_taylor(self):
        with self.assertRaisesRegex(ProviderError,'NONSMOOTH'):
            taylor_step('LCS91','2999','2','0.01','0','3e-18')
    def test_negative_endpoint_is_not_clipped(self):
        with self.assertRaisesRegex(ProviderError,'NEGATIVE_DENSITY'):
            taylor_step('LCS91','10000','1','0','-2','3e-18')
    def test_event_correlation_is_preserved(self):
        got=taylor_step('LCS91','10000','2','0.1','0.2','3e-18')
        self.assertIsInstance(got,dict)
        self.assertEqual(got['conservation_residuals'],{'H_nuclei':['0','0'],'charge':['0','0'],'thermal_plus_binding':['0','0']})
if __name__=='__main__':unittest.main()
