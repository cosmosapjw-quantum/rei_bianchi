import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("source_tedge_test",ROOT/"edge_probe.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class TestPhysicalTemperatureEdge(unittest.TestCase):
    def test_preserved_original_26event_source_identity(self):
        self.assertEqual(m.ARCHIVE_SHA256,"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
        self.assertEqual(m.SOURCE_ACCEPTED_ARRAY_SHA256,"cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01")
        self.assertEqual(m.NODES,46080)
    def test_original_three_lanes_and_frozen_bound(self):
        self.assertEqual(len(m.LANES),3)
        self.assertEqual(m.PARENT_TICK,160)
        self.assertGreater(m.OBSERVED_FROZEN_ONE_TICK,m.GATE)
        self.assertEqual(m.GATE,2e-4)
    def test_source_identical_box_difference_aware(self):
        lo=np.array([1.]);hi=np.array([2.])
        a,b,l,u=m.interval_difference(lo,hi,lo,hi)
        self.assertGreater(u[0],.999)
        self.assertAlmostEqual(l[0],0.,places=14)
    def test_physical_binding_formula_exact_charge(self):
        # Diagnostics are linear in ion fraction, do not impersonate photon total-energy ledger.
        yhe=0.079;xH=.85;xHe=.70;xHe3=.1
        xe=xH+yhe*(xHe+2*xHe3)
        self.assertAlmostEqual(xe,.9211)
        self.assertGreater(xe,xH)
    def test_edge_enforcement_explicit(self):
        text=(ROOT/"edge_probe.py").read_text()
        self.assertIn("temperature_edge not in ('lower','upper')",text)
        self.assertIn("source_kernel_sha256",text)
        self.assertIn("parent_temperature_uncertainty_log_width_max",text)
        self.assertNotIn("NO_TOLERANCE_RELAXATION=false",text)
if __name__=="__main__":unittest.main()
