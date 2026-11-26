import unittest,numpy as np
from event_inventory import archive,species_events,transfer
from ff_cutoff import grid,ff_step,SignedKompaneets,FreeFree,G
class T(unittest.TestCase):
 def test_archive(self):self.assertLess(abs(archive()['gas_closure']),1e-10)
 def test_events(self):
  np.testing.assert_allclose(species_events([.2,.1,.03],[0,0,0],[.1,.02,.01],.01,.1),[.1,.5,.2])
  self.assertAlmostEqual(transfer(5.,1.,2.,.3,.2,np.array([1.,2.]))[1],.5)
 def test_grid(self):
  a=grid(1e-10);b=grid(1e-14);np.testing.assert_array_equal(b[-len(a):],a)
 def test_equilibrium(self):
  s=SignedKompaneets(grid(1e-12,1024));ff=FreeFree(G,s)
  d,inc,em,ab,tau=ff_step(s,ff,np.zeros_like(s.x),50.,50.,0.,1e-9,1e7)
  np.testing.assert_array_equal(d,0);np.testing.assert_array_equal(em,ab);self.assertTrue(np.max(tau)>0)
if __name__=='__main__':unittest.main()
