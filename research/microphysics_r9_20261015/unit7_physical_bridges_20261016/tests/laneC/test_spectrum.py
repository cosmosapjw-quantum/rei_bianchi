import importlib.util,unittest
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parents[2]/'code/laneC/run_spectrum.py'
s=importlib.util.spec_from_file_location('spectrum',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class ExportTests(unittest.TestCase):
    def test_analytic_uniform_redshift_toy(self):
        checks=m.toy_checks()
        for key in ('bin_relative','total_relative','cropped_number_closure','outside_support_absolute'): self.assertLessEqual(checks[key],1e-11)
    def test_input_invariant_is_not_clipped(self):
        with self.assertRaisesRegex(ValueError,'negative'): m.Measure(np.array([1.,2.,3.]),np.array([1.,1.1,0.]))
    def test_internal_boundary_and_zeros(self):
        measure=m.Measure(np.array([1.,2.,3.]),np.array([1.,.5,0.]))
        np.testing.assert_allclose(measure.moments(12,0,100),[1,6*np.log(2),18],rtol=1e-14)
        np.testing.assert_array_equal(measure.moments(12,0,0),[0,0,0])
if __name__=='__main__': unittest.main()
