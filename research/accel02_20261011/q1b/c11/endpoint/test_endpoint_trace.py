"""New trace semantics only; no replay of original cross-section suite."""
from pathlib import Path
import sys
import unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent.parent))
from endpoint_trace import native_trace, TraceContractError
from opacity_native import NativeOpacity,THRESHOLDS_EV

class EndpointTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.opacity=NativeOpacity()
    @classmethod
    def tearDownClass(cls): cls.opacity.close()

    def test_native_threshold_left_right_semantics(self):
        for species,energy in enumerate(THRESHOLDS_EV):
            right=native_trace(self.opacity,float(energy),'right')
            left=native_trace(self.opacity,float(energy),'left')
            self.assertGreater(right.sigma_cm2[species],0.)
            self.assertEqual(left.sigma_cm2[species],0.)
            self.assertEqual(left.input_energy_hex,float(energy).hex())
            self.assertEqual(left.native_evaluation_energy_hex,float(energy).hex())
            self.assertEqual(right.native_evaluation_energy_hex,float(energy).hex())
            self.assertEqual(left.trace_branch[species],'BELOW_THRESHOLD_ANALYTIC_ZERO')
            self.assertEqual(right.trace_branch[species],'CONTINUOUS_ACTIVE_NATIVE_VALUE')
            for k in range(3):
                if k!=species:self.assertEqual(left.sigma_cm2[k],right.sigma_cm2[k])
            self.assertFalse(left.admits_rounded_endpoint)
            self.assertFalse(left.supplies_endpoint_jacobian)

    def test_domain_cap_has_only_left_interior_trace(self):
        left=native_trace(self.opacity,50000.,'left')
        self.assertTrue(np.all(np.asarray(left.sigma_cm2)>0.))
        before=self.opacity.native_calls
        with self.assertRaisesRegex(TraceContractError,'RIGHT_TRACE_OUTSIDE_PROVIDER_DOMAIN'):
            native_trace(self.opacity,50000.,'right')
        self.assertEqual(before,self.opacity.native_calls)

    def test_no_ambiguous_side_or_invalid_energy_is_repaired(self):
        before=self.opacity.native_calls
        for energy,side in [(13.6,'auto'),(13.6,None),(0.,'right'),(-1.,'left'),
                            (float('nan'),'left'),(50001.,'left')]:
            with self.assertRaises(TraceContractError):native_trace(self.opacity,energy,side)
        self.assertEqual(before,self.opacity.native_calls)

    def test_no_non_native_or_claimed_identity_provider_is_admitted(self):
        class ClaimedProvider:
            binary_sha256=self.opacity.binary_sha256
            def sigma(self,_):raise AssertionError('must not call spoofed provider')
        with self.assertRaisesRegex(TraceContractError,'ACTUAL_PINNED_NATIVE_OPACITY_REQUIRED'):
            native_trace(ClaimedProvider(),13.6,'left')

    def test_trace_is_value_only_not_a_reconstructed_cell_conversion(self):
        value=native_trace(self.opacity,70.,'left')
        self.assertEqual(value.claim,'EXPLICIT_ENERGY_ONE_SIDED_VALUE_ONLY')
        self.assertFalse(value.admits_rounded_endpoint)
        self.assertFalse(value.supplies_endpoint_jacobian)
        self.assertEqual(value.energy_ev,70.)
        self.assertEqual(value.side,'left')

if __name__=='__main__':unittest.main(verbosity=2)
