import unittest
import numpy as np
from compare_clock import compare, prefix_tau, tau_at
from cold_history_tau import OPACITY_FACTOR

class ClockDecomposeTests(unittest.TestCase):
    def test_constant(self):
        t=np.array([0.,1.,2.,3.])
        ne=np.full_like(t,2.)
        tau=prefix_tau(t,ne)
        self.assertAlmostEqual(tau_at(t,ne,tau,1.5),3*OPACITY_FACTOR)
    def test_linear_cell(self):
        t=np.array([0.,2.]);ne=np.array([0.,2.]);tau=prefix_tau(t,ne)
        self.assertAlmostEqual(tau_at(t,ne,tau,1.),.5*OPACITY_FACTOR)
    def test_decomposition(self):
        a={"case":"A","t":np.array([0.,1.,2.]),"ne":np.array([1.,1.,1.]),
           "sha":"a","a_end":.2,"zbar_end":4.}
        b={"case":"B","t":np.array([0.,1.,3.]),"ne":np.array([2.,2.,2.]),
           "sha":"b","a_end":.2,"zbar_end":4.}
        for c in (a,b):c["tau"]=prefix_tau(c["t"],c["ne"])
        result=compare(a,b)
        self.assertAlmostEqual(result["delta_tau_at_common_proper_time"],2*OPACITY_FACTOR)
        self.assertAlmostEqual(result["terminal_clock_contribution"],2*OPACITY_FACTOR)
        self.assertAlmostEqual(result["delta_tau_at_common_zbar"],4*OPACITY_FACTOR)
    def test_requires_shared_endpoint(self):
        a={"case":"A","t":np.array([0.,1.]),"ne":np.array([1.,1.]),
           "sha":"a","a_end":.2,"zbar_end":4.}
        b={"case":"B","t":np.array([0.,1.]),"ne":np.array([1.,1.]),
           "sha":"b","a_end":.19,"zbar_end":4.1}
        for c in (a,b):c["tau"]=prefix_tau(c["t"],c["ne"])
        with self.assertRaises(ValueError):compare(a,b)
if __name__=="__main__":unittest.main()
