import unittest,numpy as np
from spectral_coupling import SignedKompaneets, FreeFree, candidate, sink_stock, G, birth_scaled, electron_fraction, abundance_from_clock, H
class SpectralCouplingTest(unittest.TestCase):
 def setUp(self):self.s=SignedKompaneets(np.geomspace(1e-6,60,129));self.ff=FreeFree(G,self.s)
 def test_planck_fixed(self):
  s=self.s;d,cu,fu,nn,_=candidate(np.zeros(128),s,self.ff,50.,50.,1e-8,0.,0.,1.)
  np.testing.assert_allclose(d,0,atol=1e-15);self.assertLess(abs(cu)+abs(fu)+abs(nn),1e-15)
 def test_ledger(self):
  s=self.s;old=np.zeros(128);d,cu,fu,nn,_=candidate(old,s,self.ff,10.,50.,1e-8,1e-8,0.,1.)
  self.assertGreaterEqual(min(s.f0+d/s.c),0)
  self.assertLess(abs(15/np.pi**4*(s.x@(d-old))-cu-fu),1e-14)
  self.assertLess(abs(d.sum()-nn),1e-14);np.testing.assert_array_equal(old,0)
 def test_sink(self):
  s=self.s;old=np.zeros(128);a=.1*s.c[0]*s.f0[0];d,N,E=sink_stock(old,s,a,2.)
  self.assertAlmostEqual(d.sum()+N,0);self.assertAlmostEqual(2*s.x@d+E,0);self.assertGreaterEqual(min(s.f0+d/s.c),0)
 def test_bad_sink(self):
  with self.assertRaises(ValueError):sink_stock(np.zeros(128),self.s,1.,1.)
 def test_helium_normalization(self):
  self.assertAlmostEqual(electron_fraction(1,0,1,.08),1.16)
  r=np.genfromtxt(H,names=True,delimiter=',');Y=abundance_from_clock(r);self.assertTrue(.08<Y<.083)
  x=electron_fraction(r['xHII'],r['xHeII'],r['xHeIII'],Y);q=r['ne']*r['a']**3/x;np.testing.assert_allclose(q,q[0],rtol=1e-12,atol=0)
 def test_birth(self):self.assertAlmostEqual(birth_scaled(2.,50.,50.),2.)
if __name__=='__main__':unittest.main()
