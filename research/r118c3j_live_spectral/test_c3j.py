import unittest,numpy as np
from plasma import cutoff,dos
class T(unittest.TestCase):
 def test_cutoff(self):
  self.assertGreater(cutoff(1e-6,55.),0);self.assertAlmostEqual(cutoff(4e-6,55.)/cutoff(1e-6,55.),2.)
 def test_dos(self):
  self.assertEqual(dos(.9,1.),0.);self.assertAlmostEqual(dos(2.,1.),np.sqrt(.75))
if __name__=='__main__':unittest.main()
