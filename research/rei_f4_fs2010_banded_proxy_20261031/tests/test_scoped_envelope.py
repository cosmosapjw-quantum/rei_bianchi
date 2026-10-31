"""Unittest tests for scoped FS single-xi source projection only, never native cascade."""
import sys, tempfile, shutil, unittest, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import build_envelope as m

class EnvelopeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p,cls.c=m.source_data(m.DEFAULT_PARENT,m.DEFAULT_303)
  cls.out,cls.s=m.make(m.DEFAULT_PARENT,m.DEFAULT_303)
  cls.env=json.loads((ROOT/'fst_model_envelope_mirror.json').read_text())
 def test_source_sha_exact(self):
  self.assertEqual(m.sha(m.DEFAULT_PARENT),m.ORIGINAL_PARENT_CSV_SHA)
  self.assertEqual(m.sha(m.DEFAULT_303),m.ORIGINAL_PR303_CSV_SHA)
 def test_negative_sha_parent(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'bad.csv';p.write_bytes(m.DEFAULT_PARENT.read_bytes()+b'\n')
   with self.assertRaisesRegex(AssertionError,'SHA_MISMATCH'):m.source_data(p,m.DEFAULT_303)
 def test_negative_sha_pr303(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'bad.csv';b=m.DEFAULT_303.read_bytes();p.write_bytes(b.replace(b'0.9999',b'0.9998',1))
   with self.assertRaisesRegex(AssertionError,'SHA_MISMATCH'):m.source_data(m.DEFAULT_PARENT,p)
 def test_indices_and_redshift_join(self):
  self.assertEqual(len(self.p),192)
  self.assertTrue(np.array_equal(self.p.arrival_interval,self.c.arrival_interval))
  self.assertLess(max(abs(self.p.z_low-self.c.z_end)),1e-12)
 def test_positive_energy(self):
  self.assertGreater(self.out.primary_eV_per_b.sum(),0)
  self.assertTrue(np.all(self.out.primary_eV_per_b>=0))
  self.assertTrue(np.all(self.out.terminal_eV_per_b>=0))
 def test_energy_sum_regression(self):
  self.assertAlmostEqual(self.out.primary_eV_per_b.sum()/6.749242464433259e-11,1,places=12)
 def test_terminal_regression(self):
  self.assertAlmostEqual(self.out.terminal_eV_per_b.sum()/8.581099847924098e-12,1,places=12)
 def test_zero_zeroth_interval(self):
  self.assertEqual(self.out.iloc[0].primary_eV_per_b,0)
  self.assertEqual(self.out.iloc[0].xHII_heat_lo_eV_per_b,0)
 def test_band_envelope_monotone(self):
  bands=np.array(self.env['bands']);self.assertEqual(bands.shape,(14,4,6))
  self.assertTrue(np.all(bands[:,:,::2]<=bands[:,:,1::2]))
 def test_bracket_at_nodes(self):
  b=np.array(self.env['bands']);g=np.array(self.env['xi'])
  for i,x in enumerate(g):
   out,valid,cl=m.bracket(x,g,b)
   self.assertTrue(valid);self.assertAlmostEqual(cl,x)
   np.testing.assert_allclose(out,b[i],rtol=0,atol=1e-14)
 def test_bracket_interior_is_convex(self):
  b=np.array(self.env['bands']);g=np.array(self.env['xi']);i=7;t=.37
  x=(1-t)*g[i]+t*g[i+1];out,v,cl=m.bracket(x,g,b)
  self.assertTrue(v);np.testing.assert_allclose(out,(1-t)*b[i]+t*b[i+1],atol=2e-15)
 def test_projection_counts_differ(self):
  self.assertNotEqual(self.s['scenarios']['xHII']['out_of_grid_arrival_intervals'],self.s['scenarios']['electron_matched']['out_of_grid_arrival_intervals'])
 def test_ion_heat_exc_intervals(self):
  for name in ['xHII','electron_matched']:
   for ch in m.CHANNELS:
    a=self.out[f'{name}_{ch}_lo_eV_per_b'];b=self.out[f'{name}_{ch}_hi_eV_per_b']
    self.assertTrue(np.all(a<=b+1e-24))
 def test_partition_energy_cover(self):
  for name in ['xHII','electron_matched']:
   lo=sum(self.out[f'{name}_{ch}_lo_eV_per_b'].sum() for ch in m.CHANNELS)
   hi=sum(self.out[f'{name}_{ch}_hi_eV_per_b'].sum() for ch in m.CHANNELS)
   self.assertLessEqual(lo,self.out.primary_eV_per_b.sum()*(1+5e-5))
   self.assertGreaterEqual(hi,self.out.primary_eV_per_b.sum()*(1-5e-5))
 def test_outgrid_strict_support(self):
  for name in ['xHII','electron_matched']:
   s=self.s['scenarios'][name]
   self.assertGreaterEqual(s['above10p2_out_of_grid_unassigned_eV_per_b'],0)
   self.assertLessEqual(s['heat_lo_strict_xsupport_eV_per_b'],s['heat_hi_strict_xsupport_eV_per_b'])
   self.assertGreaterEqual(s['heat_lo_strict_xsupport_eV_per_b'],self.out.terminal_eV_per_b.sum())
 def test_heIII_off_manifold(self):
  self.assertGreater(self.c.xHeIII_end.max(),1e-3)
  self.assertTrue(np.all(self.c.xHeII_end>=0))
 def test_no_ivp(self):
  self.assertEqual(self.s['gates']['NEW_IVPS'],0)
  self.assertFalse(self.s['gates']['L4_READY'])
  self.assertEqual(self.s['gates']['CENTRAL_DAG'],'28/88')

if __name__=='__main__':unittest.main()
