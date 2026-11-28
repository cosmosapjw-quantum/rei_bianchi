import unittest
from fractions import Fraction as Q
from g7_reference import moments, response, remainder_bound, angular_moments_14

class G7Tests(unittest.TestCase):
    S=((Q(-1,2),0,0),(0,Q(-1,2),0),(0,0,1))
    def test_exact_axisymmetric_moments(self):
        self.assertEqual(moments(self.S),{'trace_s2':Q(3,2),'mean_delta_second':Q(3,10),'mean_delta2_second':Q(1,5),'spectral_norm_upper':Q(1)})
    def test_response_has_A_term(self): self.assertEqual(response(self.S,1,0),Q(3,10))
    def test_response_AB(self): self.assertEqual(response(self.S,2,3),Q(9,10))
    def test_zero(self): self.assertEqual(response(((0,0,0),)*3,3,4),Q(0))
    def test_conditional_remainder(self): self.assertEqual(remainder_bound(self.S,2,3,6),Q(20,3))
    def test_negative_M3_rejected(self):
        with self.assertRaises(ValueError): remainder_bound(self.S,1,1,-1)
    def test_float_rejected(self):
        with self.assertRaises(TypeError): response(self.S,1.0,0)
    def test_bool_rejected(self):
        with self.assertRaises(TypeError): response(self.S,True,0)
    def test_trace_rejected(self):
        with self.assertRaises(ValueError): moments(((1,0,0),(0,1,0),(0,0,1)))
    def test_asymmetry_rejected(self):
        with self.assertRaises(ValueError): moments(((0,1,0),(0,0,0),(0,0,0)))
    def test_shape_rejected(self):
        with self.assertRaises(ValueError): moments(((0,0),(0,0)))
    def test_exact_cubature(self):
        self.assertEqual(angular_moments_14(self.S),{'mean_q':Q(0),'mean_r':Q(1,2),'mean_q2':Q(1,5)})
    def test_cubature_nondiagonal(self):
        S=((1,2,3),(2,-4,5),(3,5,3))
        m=angular_moments_14(S)
        self.assertEqual(m,{'mean_q':Q(0),'mean_r':Q(34),'mean_q2':Q(68,5)})
    def test_quadratic_scaling(self):
        T=tuple(tuple(Q(x,10) for x in r) for r in self.S)
        self.assertEqual(response(T,3,4),Q(13,1000))
    def test_cubic_scaling_bound(self):
        T=tuple(tuple(Q(x,10) for x in r) for r in self.S)
        self.assertEqual(remainder_bound(T,2,3,6),Q(1,150))
if __name__=='__main__': unittest.main()
