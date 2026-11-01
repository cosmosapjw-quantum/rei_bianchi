"""Independent exact-arithmetic negative and positive controls for direct interval Cramer."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import unittest

SRC=Path(__file__).resolve().parents[1]/"direct_cramer_audit.py"
spec=importlib.util.spec_from_file_location("direct_cramer_test_module",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def det(A):
    return m.det_interval(A,Q(0))

class ExactCramerTests(unittest.TestCase):
    def test_permutation_sign(self):
        self.assertEqual(m.sign((0,1,2)),1)
        self.assertEqual(m.sign((1,0,2)),-1)
        self.assertEqual(m.sign((2,0,1)),1)

    def test_exact_2x2_physical_positive(self):
        A=[[Q(11,10),Q(-1,10)],[Q(-1,5),Q(6,5)]]
        b=[Q(-3,10),Q(3,10)]
        d=det(A)
        self.assertGreater(d,0)
        x=[det([[b[i] if col==j else A[i][col] for col in range(2)]
                  for i in range(2)])/d for j in range(2)]
        self.assertEqual([sum(A[i][j]*x[j] for j in range(2)) for i in range(2)],b)

    def test_exact_3x3_physical_positive(self):
        A=[[Q(11,10),Q(-1,10),Q(0)],
           [Q(-1,20),Q(6,5),Q(-1,10)],
           [Q(0),Q(-1,20),Q(11,10)]]
        b=[Q(1,9),Q(-2,9),Q(1,9)]
        d=det(A)
        self.assertGreater(d,0)
        x=[det([[b[i] if col==j else A[i][col] for col in range(3)]
                 for i in range(3)])/d for j in range(3)]
        self.assertEqual([sum(A[i][j]*x[j] for j in range(3)) for i in range(3)],b)

    def test_singular_negative_det(self):
        A=[[Q(1),Q(1)],[Q(1),Q(1)]]
        self.assertEqual(det(A),0)
        self.assertFalse(det(A)>0)

if __name__=="__main__":
    unittest.main()
