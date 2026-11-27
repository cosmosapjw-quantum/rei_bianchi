import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from species_stress import components,c15_row
class Species(unittest.TestCase):
 def test_opposite_signed_cancellation(self):
  r=components(1.,.01,2.,-2.,0.);self.assertEqual(r['v_total'],0.);self.assertEqual(r['chi_mr'],-1);self.assertGreater(r['Pi_m']+r['Pi_r'],r['Pi_total'])
 def test_C15_UV_is_radiation(self):
  r=c15_row(dict(H=1.,s_inv_s=0.,Pi_massive=0.,Pi_gamma=0.,Pi_nu=0.,Pi_UV=3.));self.assertEqual(r['v_m'],0.);self.assertEqual(r['v_r'],r['v_UV']);self.assertGreater(r['Pi_r'],0.)
if __name__=='__main__':unittest.main()
