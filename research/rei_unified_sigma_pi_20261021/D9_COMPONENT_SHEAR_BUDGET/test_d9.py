"""Small falsifiable controls for the new saved-data transform and quadrature."""
import unittest
import numpy as np
from analyze_d9 import budget

class BudgetControls(unittest.TestCase):
    def geometry(self):
        x=np.array([0.,.02,.09,.21,.38,.64,.9])
        a=np.exp(x)/21.;h=np.exp(-3*x)*2.
        return x,a,h
    def test_nonuniform_quadratic_weighted_source_primitive(self):
        x,a,h=self.geometry();m=(a/a[0])**3*h/h[0]
        f=2*x*x-3*x+4;primitive=2*x**3/3-1.5*x*x+4*x
        pm=f/m;s=(.003+primitive)*h/(np.sqrt(6)*m)
        b=budget(x,a,h,s,pm,pm*0,pm*0)
        np.testing.assert_allclose(b['I_m'],primitive,rtol=0,atol=2e-15)
        np.testing.assert_allclose(b['R'],0,rtol=0,atol=2e-15)
    def test_source_free_decay_and_broadcast(self):
        x,a,h=self.geometry();h=2*np.exp(-1.5*x);h=np.stack((h,h*1.2));a=np.stack((a,a));m=(a/a[:,0,None])**3*h/h[:,0,None]
        s0=np.array([.003,-.02]);sf=s0[:,None]/m;s=sf*h/np.sqrt(6);zero=np.zeros_like(a)
        b=budget(x,a,h,s,zero,zero,zero)
        np.testing.assert_allclose(b['Q'],np.broadcast_to(s0[:,None],s.shape),rtol=0,atol=1e-17)
        np.testing.assert_allclose(b['S_F_reconstructed'],sf,rtol=0,atol=1e-17)
    def test_opposite_sources_cancel_on_prescribed_geometry(self):
        x,a,h=self.geometry();source=.02+3*x*x;s=.003*h/np.sqrt(6)
        b=budget(x,a,h,s,source,-source,source*0)
        np.testing.assert_array_equal(b['I_m'],-b['I_r'])
        np.testing.assert_allclose(b['R'],0,rtol=0,atol=5e-17)
    def test_nonmonotone_grid_rejected(self):
        x,a,h=self.geometry();x[2]=x[1]
        with self.assertRaisesRegex(ValueError,'NONMONOTONE'):
            budget(x,a,h,a*0,a*0,a*0,a*0)

if __name__=='__main__': unittest.main(verbosity=2)
