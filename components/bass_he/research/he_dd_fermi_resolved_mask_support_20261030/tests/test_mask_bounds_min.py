"""Focused regression for the Git-published standalone condensed implementation."""
import json, sys, unittest
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mask_bounds_min import read,flat_mean,compute,OMEGA_H,E

class PublishedScriptTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data,cls.sigma=read(ROOT)
  cls.res=compute(ROOT)
 def test_real_78mirror_sixrows(self):
  self.assertEqual(len(self.data),3)
  self.assertEqual([(F(z[1]),F(z[2])) for z in self.data['A']],[(F(200),F('282.8')),(F('282.8'),F(400))])
 def test_14measured_nuclear_knots(self):
  self.assertEqual(len(E),6)
  self.assertNotIn(F(330),E)
 def test_fsrc_same_ABC(self):
  self.assertEqual([self.data[m][0][13] for m in 'ABC'],['4.092e-07']*3)
 def test_exact_flat(self):
  self.assertEqual(flat_mean(F(200),F('282.8'),self.sigma),F('104.421075')/F('82.8'))
 def test_mask_not_full_sky(self):
  self.assertLess(OMEGA_H,4*__import__('math').pi)
 def test_resolved_rate(self):
  r=next(x for x in self.res['rows'] if x['component']=='resolved_highlat')
  self.assertAlmostEqual(r['flat_s_inv_per_He']/5.41491699924193e-39,1.,places=13)
  self.assertAlmostEqual(r['spectrum_shape_free_upper_s_inv_per_He']/1.075618749129087e-38,1.,places=13)
 def test_physical_hold(self):
  self.assertEqual(len(self.res['rows']),7)
  self.assertIsNone(self.res['R_event'])
  self.assertIsNone(self.res['heat_rate'])
  self.assertEqual(self.res['production'],'HOLD')

if __name__=='__main__':unittest.main()
