import unittest
import numpy as np
from scipy.linalg import expm
from radiation_flow import RadiationFlow

class FlowTests(unittest.TestCase):
    def test_zero_displacement_is_byte_exact(self):
        f=RadiationFlow([[0.,-2.],[-1.6,-1.4]]);y=np.array([1.,-.00001])
        self.assertEqual(f.at(0,y).tobytes(),y.tobytes())
    def test_diagonal_matches_scalar_exponentials(self):
        f=RadiationFlow(np.diag([1.,-2.,.5])); y=np.array([2.,-1.,3.])
        np.testing.assert_allclose(f.at(.01,y),y*np.exp(np.array([1.,-2.,.5])*.01),rtol=2e-15,atol=1e-16)
    def test_complex_pair_returns_real_rotation(self):
        f=RadiationFlow([[0.,-2.],[2.,0.]])
        np.testing.assert_allclose(f.at(.01,[1,0]),[np.cos(.02),np.sin(.02)],atol=2e-15)
    def test_defective_jordan_falls_back(self):
        f=RadiationFlow([[1.,1.],[0.,1.]])
        self.assertFalse(f.spectral)
        np.testing.assert_allclose(f.at(.02,[0,1]),[.02*np.exp(.02),np.exp(.02)],rtol=2e-15)
    def test_large_displacement_expm_fallback(self):
        M=np.array([[.2,3],[-2,-.3]]); f=RadiationFlow(M);y=np.array([1.,.3])
        np.testing.assert_array_equal(f.at(.2,y),expm(.2*M)@y)
    def test_small_step_semigroup(self):
        f=RadiationFlow([[0.,-2.],[-1.6,-1.4]]);y=np.array([1.,.001])
        np.testing.assert_allclose(f.at(.009,f.at(-.003,y)),f.at(.006,y),rtol=2e-15,atol=2e-16)
    def test_input_isolation(self):
        m=np.diag([1.,2.]);f=RadiationFlow(m);m[0,0]=99
        self.assertEqual(f.matrix[0,0],1);self.assertFalse(f.matrix.flags.writeable)
    def test_invalid_inputs_rejected(self):
        for m in ([[1,2,3],[1,2,3]],[[np.nan]],[]):
            with self.assertRaises(ValueError):RadiationFlow(m)
        f=RadiationFlow(np.eye(2))
        for b,y in [(np.nan,[1,2]),(0,[1]),(1,[1,np.inf])]:
            with self.assertRaises(ValueError):f.at(b,y)
    def test_complex_matrix_rejected(self):
        with self.assertRaises(ValueError):RadiationFlow(np.array([[1+1j]]))

if __name__=='__main__':unittest.main(verbosity=2)
