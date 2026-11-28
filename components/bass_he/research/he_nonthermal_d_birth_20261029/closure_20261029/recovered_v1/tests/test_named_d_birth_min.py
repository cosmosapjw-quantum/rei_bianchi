import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from named_d_birth_min import *
class T(unittest.TestCase):
 def test_energy(self):
  x=source('3/2','MANUFACTURED_TEST_ONLY',('3/5','4/5',0))
  self.assertEqual(x['residual_J_m3s'],0)
  self.assertEqual(x['S_Dfast'],3)
  self.assertEqual(sum((x['S_fast_kin_J_m3s'],x['S_rest_J_m3s'],x['S_gamma_J_m3s'])),0)
  self.assertEqual(tuple(a+b for a,b in zip(x['S_D_momentum_N_m3'],x['S_gamma_momentum_N_m3'])),(0,0,0))
 def test_fail_closed(self):
  self.assertIsNone(source()['R'])
  with self.assertRaises(ValueError): source(1,'PHYSICAL')
  with self.assertRaises(ValueError): source(0.1,'MANUFACTURED_TEST_ONLY')
  with self.assertRaises(ValueError): source('-2','MANUFACTURED_TEST_ONLY')
  with self.assertRaises(ValueError): source(1,'MANUFACTURED_TEST_ONLY',(1,1,0))
if __name__=='__main__':unittest.main()
