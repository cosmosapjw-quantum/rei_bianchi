"""New pinned native-opacity binding tests, not any previous native suite."""
import unittest
import numpy as np
from reconstruction import reconstruct, TraceRequired
from opacity_native import NativeOpacity, DEFAULT_BINARY, EXPECTED_BINARY_SHA256


class OpacityBindingTests(unittest.TestCase):
    def test_actual_pinned_provider_and_domains(self):
        with NativeOpacity(DEFAULT_BINARY) as native:
            self.assertEqual(native.binary_sha256,EXPECTED_BINARY_SHA256)
            sigma=native.sigma(np.array([5.,13.60,24.59,54.42,70.]))
            self.assertEqual(sigma.shape,(5,3))
            np.testing.assert_array_equal(sigma[0],np.zeros(3))
            self.assertTrue(np.all(sigma[-1]>0))
            count=native.native_calls
            for bad in [0.,50000.01,float('nan')]:
                with self.assertRaises(ValueError):native.sigma(np.array([bad]))
            self.assertEqual(native.native_calls,count)

    def test_exact_empty_and_endpoint_fail_closed(self):
        with NativeOpacity(DEFAULT_BINARY) as native:
            out=native.moments(reconstruct(0.,0.,1.,10.,40.))
            self.assertEqual(out['K0'],[0.,0.,0.])
            self.assertEqual(out['KE'],[0.,0.,0.])
            self.assertEqual(native.native_calls,0)
            with self.assertRaises(TraceRequired):
                native.moments(reconstruct(1.,13.6,1.,13.6,20.))
            self.assertEqual(native.native_calls,0)

    def test_actual_interior_pairing(self):
        with NativeOpacity(DEFAULT_BINARY) as native:
            out=native.moments(reconstruct(1e-8,60e-8,1.,55.,70.))
            self.assertEqual(out['native_binding'],'ACTUAL_PINNED_SIGMA')
            self.assertTrue(np.all(np.asarray(out['K0'])>0))
            np.testing.assert_allclose(np.asarray(out['heat_eV'])+np.asarray(out['chemical_eV']),
                                       out['KE'],rtol=5e-15,atol=0.)
            self.assertEqual(native.native_calls,2)


if __name__=='__main__':unittest.main(verbosity=2)
