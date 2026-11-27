import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from source_cone_verifier import compute,load
class Cone(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=compute(ROOT)
 def test_six_targets_excluded(self):
  for mode,x in self.d["cases"].items():
   self.assertFalse(x["six_moment_feasible"])
   self.assertGreater(x["HeI_HI_event_dual_violation_s"],0)
   self.assertGreater(x["HI_excess_energy_cone_violation_eV_s"],0)
   self.assertGreater(x["HeII_energy_equality_violation_eV_s"],0)
 def test_ambiguous_effective_rate_not_admitted(self):
  self.assertEqual(self.d["rux04"],"NOT_ADMITTED")
 def test_counts_protected(self):
  self.assertEqual(self.d["central_rei"],"28/88_REPORTED")
  self.assertEqual(self.d["BASS_HE_physical"],"14/18_REPORTED")
  self.assertEqual(self.d["canonical_delta"],0)
 def test_no_original_ivp(self):
  self.assertEqual(self.d["new_cosmological_ivps"],0)
 def test_source_groups(self):
  self.assertEqual(self.d["source_group_count"],4)
  self.assertEqual(self.d["real_original_nodes_reused"],46080)
 def test_three_group_spectrum(self):
  sci,p,h=load(ROOT)
  self.assertEqual(len(p),3)
  self.assertEqual(sum(a>0 for a in p[0]),2)
  self.assertEqual(sum(a>0 for a in p[2]),1)
if __name__=="__main__":unittest.main()
