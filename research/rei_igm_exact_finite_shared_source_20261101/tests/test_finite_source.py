import unittest
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from finite_source import source_response

class OriginalPhotonSourceFiniteRemainder(unittest.TestCase):
    def sample(self):
        rng=np.random.default_rng(123)
        n0=.2+rng.random((27,3));n1=.2+rng.random((27,3))
        lo=n1*.8;hi=n1*1.2
        coefficients=np.array([[.12,.34,.05],[0,.03,.1],[.13,.08,.04],[.19,0,.06]])
        external=np.array([1.,.4,.02,.9])
        photons=np.array([1e7,2e7,1e6,1e5])
        excess=np.array([[1.,2.,3.,1.5],[2.,1.,3.,2.],[3.,4.,1.,3.]])
        return [n0,n1,lo,hi,coefficients,external,photons,excess]
    def test_source_direct_equals_linear_plus_exact_nonlinear_remainder(self):
        r=source_response(*self.sample())
        np.testing.assert_allclose(r['change_photo_events_per_s'],
            r['linear_change_photo_events_per_s']+r['exact_remainder_photo_events_per_s'],atol=1e-8,rtol=2e-13)
    def test_accepted_original_allX_envelope(self):
        x=self.sample();rng=np.random.default_rng(5)
        for _ in range(10):
            x[1]=x[2]+(x[3]-x[2])*rng.random(x[2].shape)
            r=source_response(*x)
            self.assertTrue(np.all(np.abs(r['exact_remainder_photo_events_per_s'])<=r['allX_remainder_bound_photo_events_per_s']+1e-8))
            self.assertTrue(np.all(np.abs(r['exact_remainder_photoheat_erg_per_s'])<=r['allX_remainder_photoheat_bound_erg_per_s']+1e-16))
    def test_second_order_small_source_moment_change(self):
        x=self.sample();base=x[0].copy();delta=x[1]-base;v=[]
        for h in (0.01,0.005,0.0025):
            x[1]=base+h*delta
            x[2]=np.minimum(base,x[1])*.95;x[3]=np.maximum(base,x[1])*1.05
            r=source_response(*x)
            v.append(float(np.max(np.abs(r['exact_remainder_photo_events_per_s']))))
        self.assertTrue(3.5<v[0]/v[1]<4.5)
        self.assertTrue(3.5<v[1]/v[2]<4.5)
    def test_no_new_photon_absorber_support(self):
        x=self.sample();x[4][:,:]=0
        r=source_response(*x)
        np.testing.assert_array_equal(r['exact_remainder_photo_events_per_s'],0)
        self.assertEqual(len(r['group_rows']),4)
    def test_no_change_from_same_parent(self):
        x=self.sample();x[1]=x[0].copy();x[2]=x[0]*.95;x[3]=x[0]*1.05
        r=source_response(*x)
        np.testing.assert_array_equal(r['linear_change_photo_events_per_s'],0)
        np.testing.assert_array_equal(r['exact_remainder_photo_events_per_s'],0)
    def test_energy_owner_photoheat_budget(self):
        r=source_response(*self.sample())
        np.testing.assert_allclose(r['accepted_photoheat_erg_per_s']-r['initial_photoheat_erg_per_s'],
            r['linear_photoheat_erg_per_s']+r['exact_remainder_photoheat_erg_per_s'],atol=1e-16,rtol=1e-11)
    def test_source_lo_hi_bad(self):
        x=self.sample();x[3]=x[2]-.01
        with self.assertRaises(ValueError):source_response(*x)
    def test_unavailable_denominator(self):
        x=self.sample();x[4][:]=0;x[5][:]=0
        with self.assertRaises(ValueError):source_response(*x)
    def test_no_false_full_interval_admission(self):
        # Scope binding rather than conflating photon-source identity with the full MPRK/SDIRK map.
        s=(Path(__file__).resolve().parents[1]/'run_original.py').read_text()
        self.assertIn('first_canonical_interval="BLOCKED_MINIMUM_STEP"',s)
        self.assertIn('original_local_error_gate=2e-4',s)
        self.assertIn('source_fixed_forcing_only=True',s)

if __name__=='__main__':unittest.main()
