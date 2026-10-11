"""New positive-step gas solver and split work checks; no old ABI replay."""
import unittest
import numpy as np
from native_step import implicit_gas_solve, gas_temperature, gas_energy_eV, split_thermal_work, EV_ERG

class NativeStepTests(unittest.TestCase):
    def setUp(self):
        self.g = dict(nH=1e-3,nHe=8e-5,H=2e-17,a_rel=1.2)
        self.y0=np.array([0.,0.,0.,1.])
    def test_newton_boundary_and_fixed_scales(self):
        rates=np.array([.1,.03,.02,.04])
        target=np.array([.8,.4,.3,2.])
        visited=[]
        def evaluate(y):
            visited.append(y.copy())
            return rates*(target-y), {'test':'linear endpoint RHS'}
        y,p,d=implicit_gas_solve(self.y0,2.,self.g,evaluate)
        expected=(self.y0+2*rates*target)/(1+2*rates)
        np.testing.assert_allclose(y,expected,rtol=0,atol=2e-11)
        self.assertLessEqual(d['scaled_residual'],1e-11)
        for p in visited:
            self.assertTrue(np.all(p[:3]>=0));self.assertLessEqual(p[1]+p[2],1.)
        self.assertEqual(d['residual_scales'],[1.,1.,1.,1.])
    def test_invalid_gas_domain_refuses_instead_of_projecting(self):
        bad=self.y0.copy();bad[2]=-.01
        with self.assertRaisesRegex(ValueError,'GAS_DOMAIN'):
            implicit_gas_solve(bad,1.,self.g,lambda y:(np.zeros(4),None))
    def test_thermal_split_does_not_recount_radiation(self):
        h_ref=self.g['nH']*self.g['a_rel']**3
        gas=np.array([.2,.1,.05,.1]); lam=np.array([3e-17,4e-17]);U=np.array([.3,.8])
        native=np.zeros(15)
        expected=2*self.g['H']*h_ref*gas[3]
        native[5]=(expected+np.dot(lam,U))*EV_ERG
        thermal,diag=split_thermal_work(native,gas,self.g,lam,U)
        self.assertAlmostEqual(thermal/expected,1.,places=14)
        self.assertLess(diag['relative_work_owner_disagreement'],1e-12)
    def test_gas_energy_linear_chemical_pairing(self):
        y=np.array([.2,.1,.3,.5]);dy=np.array([.01,-.02,.01,.03]);nh,he=.004,.0003
        expected=nh*(dy[3]+13.598434599702*dy[0])+he*(24.587389011*dy[1]+(24.587389011+54.41776)*dy[2])
        self.assertAlmostEqual((gas_energy_eV(y+dy,nh,he)-gas_energy_eV(y,nh,he))/expected,1.,places=13)

if __name__=='__main__':unittest.main(verbosity=2)
