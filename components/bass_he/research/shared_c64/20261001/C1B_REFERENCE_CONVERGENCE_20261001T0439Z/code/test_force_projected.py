"""Force angular moments checked against unintegrated point force at smooth radii."""
import unittest
import numpy as np
from numpy.polynomial.legendre import leggauss
from force_projected import angular_force_moments,force_integrals
from partialwave_centered import angular

class ForceTests(unittest.TestCase):
    def test_projected_vs_point_force_both_sides(self):
        C,K=angular_force_moments((0,1,2,3),(1,2,3,4))
        eta,w=leggauss(240);s=np.sqrt(1-eta*eta);a=-2.;Z=1.
        for r in (0.7,1.7,2.3,3.6):
            orders=np.arange(K.shape[0]);rad=abs(a)
            vl=-Z/max(r,rad)*(min(r,rad)/max(r,rad))**orders*np.sign(a)**orders
            projected=np.einsum('nlk,n->lk',K,vl)/(Z*a)
            actual=np.array([[np.dot(w,angular(l,0,eta)*angular(k,1,eta)*r*s/(r*r+a*a-2*a*r*eta)**1.5) for k in (1,2,3,4)] for l in (0,1,2,3)])
            np.testing.assert_allclose(projected,actual,atol=3e-12,rtol=0)
    def test_zero_charge_geometric_force(self):
        class Fixture:
            R=2.;ZB=2.;boundaries=np.array([0.,1.,2.,4.])
            metadata={'origin_center':'B','nuclear_positions':[-2.,0.]}
            def __init__(self,m,ZA):self.m=m;self.ZA=ZA;self.ls=np.array([m])
            def radial(self,r):return np.array([r**(self.m+1)*np.exp(-r)])
        f0=force_integrals(Fixture(0,0.),Fixture(1,0.))
        f1=force_integrals(Fixture(0,1.),Fixture(1,1.))
        self.assertTrue(np.isfinite(f0['T_A']))
        self.assertEqual(f0['T_A'],f1['T_A'])
        self.assertEqual(f0['T_B'],f1['T_B'])
    def test_central_selection(self):
        C,_=angular_force_moments((0,1,2,3),(1,2,3,4))
        self.assertAlmostEqual(C[0,0],np.sqrt(2/3),places=13)
        for i,l in enumerate((0,1,2,3)):
            for j,k in enumerate((1,2,3,4)):
                if abs(l-k)!=1:self.assertEqual(C[i,j],0.)
if __name__=='__main__':unittest.main(verbosity=2)
