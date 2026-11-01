import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("original_tick160_point_probe",root/"probe.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Tests(unittest.TestCase):
    def test_null_box_is_not_zero_error(self):
        l,h,low,up=m.interval_difference(np.array([2.]),np.array([3.]),np.array([2.]),np.array([3.]))
        self.assertLess(low[0],1e-13);self.assertGreater(up[0],1.)
    def test_point_null(self):
        l,h,low,up=m.interval_difference(np.array([.2]),np.array([.2]),np.array([.2]),np.array([.2]))
        self.assertLess(up[0],1e-14)
    def test_interval_disjoint(self):
        l,h,low,up=m.interval_difference(np.array([3.]),np.array([4.]),np.array([0.]),np.array([2.]))
        self.assertGreaterEqual(low[0],1.-1e-14)
    def test_inverted_box_rejected(self):
        with self.assertRaises(ValueError):
            m.interval_difference(np.array([2.]),np.array([1.]),np.array([1.]),np.array([1.]))
    def test_physical_parent_nuclei(self):
        x=np.tile(np.array([.1,.9,.05,.04,.01]),(m.NODES,1))
        y=m.element_conserving_parent_candidate(x-1e-9,x+1e-9,np.ones(m.NODES),np.full(m.NODES,.1))
        np.testing.assert_allclose(y[:,:2].sum(axis=1),1.,atol=3e-15)
        np.testing.assert_allclose(y[:,2:].sum(axis=1),.1,atol=3e-15)
    def test_immutables(self):
        self.assertEqual(m.PARENT_TICK,160);self.assertEqual(m.NODES,46080)
        self.assertEqual(len(m.LANES),3);self.assertGreater(m.OBSERVED_FROZEN_ONE_TICK,m.GATE)
if __name__=="__main__":unittest.main()
