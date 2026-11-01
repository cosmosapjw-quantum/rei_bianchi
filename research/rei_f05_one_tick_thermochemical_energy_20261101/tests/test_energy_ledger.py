import importlib.util
from pathlib import Path
from types import SimpleNamespace
import inspect
import unittest
import numpy as np

SCRIPT=Path(__file__).resolve().parents[1]/"energy_ledger.py"
spec=importlib.util.spec_from_file_location("rei_energy_tested",SCRIPT)
e=importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


class IV:
    def __init__(self,a,b=None):
        self.lo=np.asarray(a,dtype=float)
        self.hi=np.asarray(self.lo if b is None else b,dtype=float)
    def __add__(self,other):
        other=other if isinstance(other,IV) else IV(other)
        return IV(self.lo+other.lo,self.hi+other.hi)
    __radd__=__add__
    def __sub__(self,other):
        other=other if isinstance(other,IV) else IV(other)
        return IV(self.lo-other.hi,self.hi-other.lo)
    def __mul__(self,x):
        if np.any(np.asarray(x)<0):raise ValueError("positive synthetic factors only")
        return IV(self.lo*x,self.hi*x)
    __rmul__=__mul__
    def __truediv__(self,x):
        if np.any(np.asarray(x)<=0):raise ValueError("positive")
        return IV(self.lo/x,self.hi/x)


class SourceEnergyBudgetMath(unittest.TestCase):
    def test_sdirk_weights_return_constant_integrated_rate(self):
        g=1-1/(2**0.5)
        self.assertAlmostEqual(e.weighted(g,2.,2.,5.),10.)
        self.assertAlmostEqual(e.weighted(g,2.,2.,2.5)+
                               e.weighted(g,2.,2.,2.5),10.)

    def test_full_minus_half_energy_exact_linear_identity(self):
        g=1-1/(2**0.5)
        h=6.0
        vf=e.weighted(g,4.-2.-0.3,5.-2.5-0.4,h)
        vh=e.weighted(g,3.-2.-0.2,3.5-1.8-0.25,h/2)+e.weighted(g,4.-2.2-0.3,4.5-2.4-0.31,h/2)
        q=e.weighted(g,4.,5.,h)-e.weighted(g,3.,3.5,h/2)-e.weighted(g,4.,4.5,h/2)
        sink=e.weighted(g,2.+0.3,2.5+0.4,h)-e.weighted(g,2.+0.2,1.8+0.25,h/2)-e.weighted(g,2.2+0.3,2.4+0.31,h/2)
        self.assertAlmostEqual(vf-vh,q-sink,places=12)

    def test_frozen_parent_energy_difference_is_independent_interval(self):
        full=IV([10.,20.],[11.,21.])
        half1=IV([4.,9.],[4.5,10.])
        half2=IV([5.,9.],[5.5,9.5])
        x=e.normalized_data(full,half1,half2,np.array([2.,4.]))
        self.assertTrue(np.all(x["difference_independent_upper"]>=np.abs(x["difference_center"])))
        self.assertTrue(np.all(x["difference_lower"]<=x["difference_center"]))
        self.assertTrue(np.all(x["difference_center"]<=x["difference_upper"]))

    def test_reject_nonpositive_h_nuclei(self):
        with self.assertRaises(ValueError):
            e.normalized_data(IV([1.]),IV([1.]),IV([1.]),np.array([0.]))

    def test_ots_ledger_accepts_only_enclosure_of_zero(self):
        ev=SimpleNamespace(chemical_energy=IV([-4.]),resolved_heat=IV([1.]),
                           escaped_energy=IV([2.]),unresolved_energy=IV([1.]))
        self.assertEqual(e.verify_ots_ledger(ev),0.)
        ev.unresolved_energy=IV([1.1])
        with self.assertRaises(ValueError):
            e.verify_ots_ledger(ev)

    def test_locked_original_contract(self):
        source=inspect.getsource(e.run)
        self.assertIn('"full_source_correlated_dh_remainder_certified":False',source)
        self.assertIn('"production":"HOLD"',source)
        self.assertIn('"canonical_delta":0',source)
        self.assertEqual(e.LOCAL_GATE,2e-4)
        self.assertEqual(e.PUBLIC_WIDTH_GATE,2e-3)
        self.assertEqual(len(e.SRC_SHA),64)
        self.assertEqual(len(e.ARR_SHA),64)

    def test_fixed_original_mapping_has_three_native_steps(self):
        src=inspect.getsource(e.run)
        self.assertIn('("full",X,LT,t0,t1)',src)
        self.assertIn('("half1",X,LT,t0,tm)',src)
        self.assertIn('("half2",None,None,tm,t1)',src)

    def test_invalid_duration_is_rejected(self):
        with self.assertRaises(ValueError):
            e.weighted(0.3,IV([1.]),IV([2.]),0.)

if __name__=="__main__":
    unittest.main()
