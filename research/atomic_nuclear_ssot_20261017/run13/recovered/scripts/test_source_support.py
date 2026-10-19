"""RUN09 source-contract regression checks, not additional cosmological cases."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import unittest,json,hashlib,copy
from pathlib import Path
import numpy as np
from retarded_integrator import RetardedModel,coalesce_reflections
from nonlinear_birth_witness import quadrature,impulse_flow
import mpmath as mp
R=Path(__file__).resolve().parents[1]
class SupportTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.packets={n:json.loads((R/f'inputs/refined/r{n}.json').read_text()) for n in [1,2,4,6]}
 def test_unrefined_replays_actual_parent_packet(self):
  self.assertEqual(self.packets[1],json.loads((R/'inputs/FINITE_BIRTH_PACKET.json').read_text()))
  self.assertEqual(hashlib.sha256((R/'inputs/refined/r1.tuple.bin').read_bytes()).hexdigest(),'7d29d5c9dda88befd5141a9257170f70d96bcbd6937a2de14a159ac1e3d6a134')
 def test_all_supports_keep_spectrum_angle_and_positive_weights(self):
  base=np.array(self.packets[1]['cohorts'])[:384,[4,5,7,8]]
  for n,p in self.packets.items():
   a=np.asarray(p['cohorts']);self.assertEqual(a.shape,(15360*n,9));self.assertTrue((a[:,6]>0).all())
   for row in a.reshape(-1,384,9):self.assertTrue(np.array_equal(row[:,[4,5,7,8]],base))
 def test_reflection_quotient_preserves_new_support_number(self):
  p=self.packets[2];q=coalesce_reflections(p)
  self.assertEqual(2*len(q['cohorts']),len(p['cohorts']))
  self.assertAlmostEqual(sum(x[6] for x in q['cohorts']),sum(x[6] for x in p['cohorts']),places=13)
 def test_no_future_birth_or_lost_packet(self):
  for n,p in self.packets.items():
   a=np.asarray(p['cohorts']);t=a[:,1];self.assertTrue(np.all((t>p['t0_s'])&(t<p['t1_s'])))
   self.assertEqual(len(np.unique(t)),40*n)
   self.assertTrue(np.all(np.diff(t[::384])>0))
 def test_birth_energies_match_actual_killing_map(self):
  p=copy.deepcopy(self.packets[2]);p['cohorts']=[p['cohorts'][j] for j in [0,388,8000,30000]]
  m=RetardedModel(p)
  for j in range(m.m):self.assertLess(abs(m.rays(m.birth[j],j+1)[0][j]/m.eb[j]-1.),3e-14)
 def test_gl4_nonlinear_impulse_counterexample_not_order8(self):
  nodes,weights=quadrature()
  self.assertLess(max(abs(sum(w*x**k for x,w in zip(nodes,weights))-mp.mpf(1)/(k+1)) for k in range(8)),mp.mpf('1e-55'))
  e1=impulse_flow(16)-mp.tanh(1);e2=impulse_flow(32)-mp.tanh(1)
  self.assertGreater(e1/e2,mp.mpf('3.99'));self.assertLess(e1/e2,mp.mpf('4.01'))
 def test_no_endpoint_means_interrupted_support_not_admitted(self):
  self.assertFalse((R/'evidence/r8_paired_DOP853_3e-11/result.json').exists())
  self.assertTrue((R/'evidence/r8_paired_DOP853_3e-11/FAILURE.txt').exists())
if __name__=='__main__':unittest.main(verbosity=2)
