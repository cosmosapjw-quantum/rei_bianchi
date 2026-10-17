import importlib.util,unittest
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parents[2]/'code/laneC2/collision_count.py';s=importlib.util.spec_from_file_location('cc',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ProjectionTests(unittest.TestCase):
    def test_barycentric_energy_and_count(self):
        E,P,sig,K,err=m.operator(8,16)
        np.testing.assert_allclose(P.sum(axis=0),1,rtol=0,atol=1e-14)
        np.testing.assert_allclose(E@P+K,E,rtol=1e-14,atol=1e-12)
        self.assertTrue(np.all(P>=0));self.assertEqual(P[0,0],1)
    def test_recoil_support_induction(self):
        E=1e5;a=.8;f=lambda E:E/(1+2*E/m.ME)
        self.assertGreaterEqual(f(a*E),a*f(E))
if __name__=='__main__':unittest.main()
