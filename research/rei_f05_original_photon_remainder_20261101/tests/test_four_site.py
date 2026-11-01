#!/usr/bin/env python3
import importlib.util,sys,unittest,math
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parents[1]/"four_site_shared_source_remainder.py"
s=importlib.util.spec_from_file_location("original_12site_source",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)

class FourSiteSourceTests(unittest.TestCase):
  def test_original_identity(self):
    self.assertEqual(m.N,46080);self.assertEqual(m.SITES,12);self.assertEqual(m.GROUPS,4)
    self.assertEqual(len(m.STATE_SHA),64);self.assertEqual(len(m.STAGE_CSV_SHA),64)
  def test_exact_source_fraction_for_realistic_positivity(self):
    for p0 in ([.2,.7,.05],[.0,.0,.0],[.4,.5,.08]):
      p0=np.asarray(p0)
      if sum(p0)>1:continue
      for ratios in ([1,1,1],[1.01,.99,1.002],[.996,1.003,.998]):
        ratio=np.asarray(ratios,float)
        external=max(0.,1.-float(sum(p0)))
        den=external+float(np.dot(p0,ratio))
        p1=p0*ratio/den
        rr=den-1.
        linear=p0*(ratio-1.-rr)
        R=-linear*rr/(1+rr)
        self.assertLess(float(max(abs((p1-p0)-linear-R))),7e-16)
  def test_denominator_r_curvature_positive(self):
    for r in (-.9,-.1,0,.004,.5,1.5):
      ref=10.0
      site=ref/(1+r)
      L=-ref*r
      R=site-ref-L
      self.assertAlmostEqual(R,site*r*r,delta=2e-14*max(1,abs(site)))
  def test_stage_source_is_not_canonical(self):
    self.assertTrue(m.ORIGINAL_ARTIFACT_SHA.startswith("41105018"))
    self.assertEqual(m.ORIGINAL_TAR_SHA,"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
  def test_source_weights_identical_group_fraction(self):
    share=[{"group":g,"source_photons_per_s":[10*g,3*g,0]} for g in range(4)]
    group=[(a,{"r_global_denominator":0.004*a["group"]}) for a in share]
    p,rmax=m.per_site_coeff(group)
    self.assertAlmostEqual(p[0],p[1],delta=1e-16)
    self.assertEqual(p[2],0.)
    self.assertAlmostEqual(rmax,(.004*3)**2,delta=1e-16)
  def test_missing_source_fail_closed(self):
    with self.assertRaises(Exception):m.get_data("/no/such/source/REI337.zip")
if __name__=="__main__":unittest.main()
