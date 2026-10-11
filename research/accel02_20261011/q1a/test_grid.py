"""New quadrature properties only; no historical science replay."""
import importlib
from pathlib import Path
import unittest
import numpy as np

class QuadratureTests(unittest.TestCase):
    def module(self):
        self.assertTrue(Path(__file__).with_name('fixed_grid.py').exists(), 'fixed-grid implementation missing')
        return importlib.import_module('fixed_grid')

    def test_gauss_polynomial_exactness_and_normalized_angles(self):
        m=self.module()
        edges=np.exp([1.,1.4,2.3,3.])
        for order in [1,2]:
            q,mu,w=m.composite_grid(edges,order,2)
            self.assertTrue(np.all(w>0))
            for degree in range(2*order):
                got=np.dot(w,np.log(q)**degree)
                exact=(3.**(degree+1)-1.)/(degree+1)
                self.assertAlmostEqual(got,exact,delta=2e-13*abs(exact))
            self.assertAlmostEqual(np.dot(w,mu),0.,delta=1e-15)
            self.assertAlmostEqual(np.dot(w,mu**2),2/3,delta=1e-14)

    def test_invalid_panels_and_orders_fail_closed(self):
        m=self.module()
        for edges,order,nmu in [([1.,1.,2.],2,2),([0.,1.],2,2),([1.,float('nan')],2,2),([1.,2.],0,2),([1.,2.],2,0)]:
            with self.assertRaises(ValueError):m.composite_grid(edges,order,nmu)

    def test_arrays_are_immutable(self):
        m=self.module()
        for a in m.composite_grid([10.,20.,30.],2,2):
            self.assertFalse(a.flags.writeable)
            with self.assertRaises(ValueError):a[0]=1.

if __name__=='__main__':unittest.main()
