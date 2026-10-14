import unittest, sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from moment_cone import exact_forward_euler_limit

class MomentConeTests(unittest.TestCase):
    def test_redshift_lower_face_is_stricter_than_positive_count(self):
        self.assertEqual(exact_forward_euler_limit(10,20,1,15,-1,-25),F(1,3))


class AdditionalConeTests(unittest.TestCase):
    def test_outward_boundary_has_zero_step(self):
        self.assertEqual(exact_forward_euler_limit(10,20,1,10,0,-1),0)
    def test_inward_vacuum(self):
        self.assertIsNone(exact_forward_euler_limit(10,20,0,0,1,15))
    def test_invalid_mean_is_rejected(self):
        with self.assertRaises(ValueError):exact_forward_euler_limit(10,20,1,21,0,0)
    def test_units_do_not_change_step(self):
        self.assertEqual(exact_forward_euler_limit(100,200,1,150,-1,-250),F(1,3))
    def test_above_limit_crosses_face(self):
        h=F(1,2);n=1-h;u=15-25*h
        self.assertGreater(n,0);self.assertLess(u,10*n)

if __name__=='__main__': unittest.main()
