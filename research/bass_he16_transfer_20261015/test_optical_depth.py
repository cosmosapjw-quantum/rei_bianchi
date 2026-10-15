import unittest
import numpy as np
from optical_depth import electron_density_cm3,cumulative_tau_trapezoid,cumulative_tau_bounds,C_M_S,SIGMA_T_M2
class TransferTests(unittest.TestCase):
    def test_constant(self):
        t=np.linspace(0,1000,17); n=np.ones(17)*1e-3
        v=cumulative_tau_trapezoid(t,n,np.ones(17),np.zeros(17),np.zeros(17),3/38)
        self.assertAlmostEqual(v[-1], SIGMA_T_M2*C_M_S*1e6,places=15)
    def test_census(self):
        self.assertAlmostEqual(float(electron_density_cm3(2,1,0,1,3/38)),2*(1+6/38))
    def test_bounds(self):
        a,b=cumulative_tau_bounds([0,1,4],[2,3],[3,4])
        self.assertTrue(np.all(b>=a))
        self.assertAlmostEqual(a[-1],11*SIGMA_T_M2*C_M_S*1e6)
    def test_invalid_simplex(self):
        with self.assertRaises(ValueError): electron_density_cm3(1,.2,.8,.4,3/38)
    def test_clock(self):
        with self.assertRaises(ValueError): cumulative_tau_trapezoid([0,0],[1,1],[1,1],[0,0],[0,0],0)
    def test_missing_history(self):
        with self.assertRaises(ValueError): cumulative_tau_trapezoid([0,1],[1],[1],[0],[0],0)
if __name__=="__main__": unittest.main()
