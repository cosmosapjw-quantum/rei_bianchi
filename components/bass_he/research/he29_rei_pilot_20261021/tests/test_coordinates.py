import sys,math,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from coordinates import normalized,c15_normalized,initial_mapping
from pilot import source,case_grid,CanonicalFVSpecies,FIXED
class Coordinates(unittest.TestCase):
 def test_full_grid_initial_inverse(self):
  src=source()
  for c in case_grid():
   m=CanonicalFVSpecies(src,2.7255,**initial_mapping(c['Sigma_F'],c['Pi_F'],c['stress_sign'],src),**FIXED);d=m.fields(0.,m.initial_state());v=normalized(d['H'],d['s'],[d['Pi_gamma_J_m3'],d['Pi_nu_J_m3'],d['Pi_matter_J_m3']]);self.assertLessEqual(abs(v['Sigma_F']-c['Sigma_F']),1e-12);self.assertLessEqual(abs(v['v']-c['stress_sign']*c['Pi_F']),1e-12)
 def test_signed_cancellation_and_half(self):
  d=normalized(2.,.1,[3.,-3.]);self.assertEqual(d['Pi_F'],0.);self.assertAlmostEqual(d['Sigma_F']/d['Sigma_half'],math.sqrt(2))
 def test_control_keeps_physical_stress(self):
  data=json.loads((ROOT/'data/original/C15_STUDY_RESULTS.json').read_text());control=next(s for s in data['series'] if s['scientific_case']=='GRAVITY_PI_DISABLED_CONTROL');r=c15_normalized(control['history'][-1],True);self.assertEqual(r['gravitational_source_v'],0.);self.assertGreater(r['Pi_F'],0.)
if __name__=='__main__':unittest.main()
