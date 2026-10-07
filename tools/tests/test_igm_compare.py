import sys
from pathlib import Path as _Path
sys.path.insert(0,str(_Path(__file__).resolve().parent.parent))
import unittest
from igm_compare import compare_rows

class CompareTests(unittest.TestCase):
    def test_missing_required_history_observable_rejects_comparison(self):
        with self.assertRaises(ValueError):
            compare_rows([dict(ln_a=0,T=30)],[dict(ln_a=0,T=30)])

    def test_fraction_allowance_retains_near_zero_absolute_scale(self):
        import igm_compare as cmp
        a={k:0. for k in getattr(cmp,'REQUIRED',['ln_a'])}
        a.update(ln_a=0,T=30.,Tcmb=35.,w=1e-15)
        b=dict(a,x_heiii=2e-6)
        self.assertFalse(compare_rows([b],[a])['passed'])

class LedgerTests(unittest.TestCase):
    def test_matching_histories_with_corrupted_budget_do_not_pass(self):
        import igm_compare as cmp
        row={key:0. for key in cmp.REQUIRED}
        row.update(T=30,Tcmb=35,emitted_N=1.,emitted_E=1e-11,number_residual=1e-4)
        self.assertFalse(compare_rows([row],[row])['passed'])
        row.update(number_residual=0.,energy_residual=1e-15)
        self.assertFalse(compare_rows([row],[row])['passed'])

if __name__=='__main__': unittest.main()
