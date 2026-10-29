"""Targeted preparation checks; no render/IVP. Execute only when authorized."""
import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('builder',ROOT/'build_figures.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class ContractTests(unittest.TestCase):
    def test_full_positive_range_includes_early_tiny_value(self):
        self.assertEqual(b.limits([{'y':[9,1e-30,1e-2]}],[0,1e-10,1]),(1e-30,.01))
    def test_signed_magnitudes_share_limits(self):
        values=[{'y':[0,-1e-12,1e-4]}]
        self.assertEqual(b.limits([dict(y=[abs(v) for v in s['y']]) for s in values],[0,1,2]),(1e-12,1e-4))
    def test_redshift_ticks_never_overlap(self):
        import math
        x=[0,1e-15,1e-4,1,10,100];eta=[0,1e-16,.01,.2,.5,2]
        ticks=b.top_ticks(x,eta,(x[1],x[-1]));positions=[math.log10(t/x[1])/math.log10(x[-1]/x[1])*426 for t,_ in ticks]
        self.assertTrue(all(q-p>=32 for p,q in zip(positions,positions[1:])))
if __name__=='__main__':unittest.main()
