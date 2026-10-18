import importlib.util,unittest
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parents[2]/'code/laneC/gamma_transfer.py'
s=importlib.util.spec_from_file_location('gamma',p);g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
class KernelTests(unittest.TestCase):
    def test_jacobian_independent_variable(self):
        E=g.E0;x=E/g.ME;mu=.2;r=1/(1+x*(1-mu));ds=np.pi*g.RE**2*r*r*(r+1/r-(1-mu*mu))
        self.assertAlmostEqual(g.rdr(r,x)/(ds/(x*r*r)),1,places=13)
    def test_kernel_energy_is_integrated(self):
        edges,b=g.recoil_bins();np.testing.assert_allclose(b[:,1]+b[:,3],g.E0*b[:,0],rtol=1e-14)
        self.assertGreaterEqual(b.min(),0);self.assertLess(abs(b[:,0].sum()-1),1e-12)
    def test_source_plateaus(self):
        z=g.source_nodes(np.array([0,0,.5,1,1.]),np.array([5,4,3,2,1.]),4)
        np.testing.assert_allclose(z,[3.75,3.25,2.75,2.25],rtol=0,atol=0)
if __name__=='__main__':unittest.main()
