import unittest
from decimal import Decimal
import numpy as np
from streaming import cumulative_tau_chunked,decimal_tau_bounds

class TestExactDecimal(unittest.TestCase):
    def test_exponent_range_preserves_small_positive_term(self):
        a,b=decimal_tau_bounds(["0","1","2"],["1e40","1e-40"],["1e40","1e-40"],
                               sigma_t_m2="1e-6",c_m_s="1")
        desired="1"+"0"*40+"."+"0"*39+"1"
        self.assertEqual(a[-1],desired)
        self.assertEqual(a,b)

    def test_nonfinite_time_inside_late_chunk_rejected(self):
        t=np.array([0.,1.,2.,3.,np.nan])
        arr=np.ones(5)
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            cumulative_tau_chunked(t,arr,arr,np.zeros(5),np.zeros(5),0,chunk_size=2)

    def test_decreasing_time_inside_late_chunk_rejected(self):
        t=np.array([0.,1.,2.,1.5,3.])
        arr=np.ones(5)
        with self.assertRaisesRegex(ValueError,"strictly"):
            cumulative_tau_chunked(t,arr,arr,np.zeros(5),np.zeros(5),0,chunk_size=2)

if __name__=="__main__":unittest.main()
