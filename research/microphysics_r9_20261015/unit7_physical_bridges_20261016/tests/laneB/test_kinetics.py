import importlib.util,unittest
from pathlib import Path
import numpy as np
from scipy.linalg import expm
p=Path(__file__).resolve().parents[2]/'code/laneB/run_kinetics.py'
s=importlib.util.spec_from_file_location('kinetics',p); k=importlib.util.module_from_spec(s); s.loader.exec_module(k)
class FrozenTests(unittest.TestCase):
    def test_rates_and_independent_one_cell(self):
        # A single midpoint-frozen physical cell matches an independent 3x3 exponential.
        u,z,y=k.midpoint(1); zm=100001*np.exp(-u[-1]/2)-1
        r,b,H,*_=k.rates(zm)
        A=np.array([[-r,b,0],[r,-b-k.lam,0],[0,k.lam,0]])
        # Explicit coefficient reward avoids unreliable full-matrix expm at enormous stiffness;
        # test at a low-z cell with dt chosen to give O(1) generator norm.
        dt=1/max(r,b,k.lam); D=np.sqrt((r-b-k.lam)**2+4*r*b); ks=2*r*k.lam/(r+b+k.lam+D); kf=(r+b+k.lam+D)/2
        es=np.exp(-ks*dt); ef=np.exp(-kf*dt)
        a=((b+k.lam-ks)*es+(r-ks)*ef)/D; be=r*es*(-np.expm1(-D*dt))/D
        reward=k.lam*r/D*((-np.expm1(-ks*dt)/ks)-(-np.expm1(-kf*dt)/kf))
        np.testing.assert_allclose([a,be,reward],expm(A*dt)@np.array([1,0,0]),rtol=2e-12,atol=1e-15)
        self.assertGreaterEqual(reward,0)
    def test_all_species_and_units(self):
        self.assertEqual(len(k.abund),59)
        self.assertAlmostEqual(k.Om,.3)
        self.assertGreater(k.Ye,.8)
if __name__=='__main__': unittest.main()
