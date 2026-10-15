import unittest
import numpy as np
from decimal import Decimal
from optical_depth import cumulative_tau_trapezoid
from streaming import cumulative_tau_chunked, decimal_tau_bounds

class Tests(unittest.TestCase):
    def test_chunk_invariance(self):
        t=np.linspace(0,3000,103);x=np.linspace(.1,.9,len(t));n=np.linspace(.001,.002,len(t));y=0.5*x;z=0.2*x
        reference=cumulative_tau_trapezoid(t,n,x,y,z,3/38)
        for chunk in [2,3,7,31,128]:
            measured=cumulative_tau_chunked(t,n,x,y,z,3/38,chunk)
            np.testing.assert_allclose(measured,reference,rtol=4e-15,atol=1e-24)
    def test_simple_decimal(self):
        lo,hi=decimal_tau_bounds(['0','2','5'],['1','2'],['2','3'],sigma_t_m2='0.1',c_m_s='1')
        self.assertEqual(Decimal(lo[-1]),Decimal('800000'))
        self.assertEqual(Decimal(hi[-1]),Decimal('1300000'))
    def test_decimal_reject_binary(self):
        with self.assertRaises(TypeError):
            decimal_tau_bounds([0.,1.],['0'],['1'])
    def test_node_input(self):
        with self.assertRaises(ValueError):
            cumulative_tau_chunked([0,1],[1,1],[1],[0,0],[0,0],0)

if __name__ == '__main__': unittest.main()
