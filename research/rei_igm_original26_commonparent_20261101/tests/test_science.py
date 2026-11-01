import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parents[1]/"science.py"
sp=importlib.util.spec_from_file_location("source_science_tick160",p)
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
class SourceContracts(unittest.TestCase):
    def test_original_lock(self):self.assertEqual(m.ARRAY_SHA,"cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01")
    def test_gates_unchanged(self):self.assertEqual((m.STRICT_ERROR,m.STRICT_WIDTH),(2e-4,2e-3))
    def test_dag_unmodified(self):self.assertEqual(m.LANE,"LOCAL_NEUTRAL_HAZARD_PRIMARY")
    def test_node_percentile(self):self.assertEqual(m.distribution(np.zeros(46080))["50"],0.)
    def test_nan_guard(self):
        x=np.ones(46080);x[10]=float("nan")
        with self.assertRaises(ValueError):m.distribution(x)
    def test_short_data_rejected(self):
        with self.assertRaises(ValueError):m.distribution(np.ones(2))
    def test_perturbation_local(self):self.assertLess(m.DELTA_LOGT,0.001)
    def test_source_branch(self):self.assertIn("original_26event_tick160",str(m.BASE_SRC))
if __name__=="__main__":unittest.main()
