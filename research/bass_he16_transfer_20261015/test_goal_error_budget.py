import unittest
import numpy as np
from goal_error_budget import integral_nh,SIGMA_C,N_H0,A_REF

class GoalErrorBudgetTests(unittest.TestCase):
    def test_constant_density_integral(self):
        t=np.array([0.,1.,3.])
        a=np.array([float(A_REF)]*3)
        calc=integral_nh(t,a)
        want=SIGMA_C*N_H0*3
        self.assertLess(float(abs(calc-want)/want),1e-15)

    def test_partial_end_time_integral(self):
        t=np.array([0.,1.,3.]);a=np.array([float(A_REF)]*3)
        calc=integral_nh(t,a,1.5)
        want=SIGMA_C*N_H0*np.longdouble("1.5")
        self.assertLess(float(abs(calc-want)/want),1e-15)

    def test_out_of_domain_time_rejected(self):
        t=np.array([0.,1.,3.]);a=np.array([float(A_REF)]*3)
        with self.assertRaises(ValueError):
            integral_nh(t,a,4.0)

if __name__=="__main__":unittest.main()
