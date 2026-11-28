import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from event_grid import make_plan
class EventGridTests(unittest.TestCase):
 def test_internal_event_has_no_birth(self):
  p=make_plan(20.,10.,[3.,7.],.25);d={x['t1']:x for x in p['segments']}
  self.assertIn(3.,d);self.assertEqual(d[3.]['birth_n'],0.);self.assertEqual(d[5.]['birth_n'],1.25)
 def test_union_keeps_both_thresholds_and_geometries(self):
  p=make_plan(20.,10.,[3.,3.5,4.,4.5],.25)
  self.assertTrue({3.,3.5,4.,4.5}<=set(p['points']))
 def test_original_birth_once(self):
  p=make_plan(20.,10.,[5.,5.,7.],.25)
  self.assertEqual(sum(x['birth_n'] for x in p['segments']),5.)
  self.assertEqual(sum(x['birth_n']>0 for x in p['segments']),4)
 def test_no_fuzzy_merging_of_close_events(self):
  r=math.nextafter(3.,math.inf);p=make_plan(20.,10.,[3.,r],.25)
  self.assertIn(3.,p['points']);self.assertIn(r,p['points'])
 def test_remeshed_children_are_identified(self):
  p=make_plan(20.,10.,[3.],.25)
  self.assertEqual([x['t1'] for x in p['segments'] if x['affected']],[3.,5.]);self.assertEqual(p['affected_count'],2)
 def test_outside_root_not_in_prefix(self):
  p=make_plan(20.,10.,[-1.,30.],.25);self.assertEqual(p['points'],[0.,5.,10.,15.,20.])
 def test_nonfinite_rejected(self):
  for x in (float('nan'),float('inf')):
   with self.assertRaises(ValueError):make_plan(20.,10.,[x],.25)
 def test_unaligned_horizon_rejected(self):
  with self.assertRaises(ValueError):make_plan(21.,10.,[],.25)
 def test_negative_source_rejected(self):
  with self.assertRaises(ValueError):make_plan(20.,10.,[],-1.)
if __name__=='__main__':unittest.main()
