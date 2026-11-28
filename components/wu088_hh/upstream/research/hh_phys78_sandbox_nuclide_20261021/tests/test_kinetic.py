import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from kinetic import PreparedKinetic

class KineticTests(unittest.TestCase):
    def test_initial_isotropic_and_normalization(self):
        m=PreparedKinetic().moments(0.,0.)
        self.assertAlmostEqual(m['rho_m'],1.,places=14)
        self.assertAlmostEqual(m['rho_r'],1.,places=14)
        self.assertLess(abs(m['pi_m']),1e-16)
        self.assertLess(abs(m['pi_r']),1e-14)

    def test_positive_stress_and_massless_trace(self):
        for A in (-1.,.8,2.):
            o=PreparedKinetic(A,A)
            for x,b in [(0.,0.),(.8,-.2),(1.94,.2)]:
                m=o.moments(x,b)
                for k in ('rho_m','rho_r','pperp_m','pparallel_m','pperp_r','pparallel_r'):
                    self.assertGreaterEqual(m[k],0.)
                self.assertLess(3*m['pbar_m'],m['rho_m'])
                self.assertAlmostEqual((2*m['pperp_r']+m['pparallel_r'])/m['rho_r'],1.,places=14)
                self.assertGreaterEqual(float(o.weights.min()),0.)

    def test_analytic_energy_identity(self):
        o=PreparedKinetic(.8,-.8)
        for x,b,w in [(0.2,.03,.04),(1.,-.15,-.03)]:
            h=1e-5
            lo=o.moments(x-h,b-w*h);hi=o.moments(x+h,b+w*h)
            d=o.continuity(x,b,w)
            for name in ('rho_m','rho_r'):
                fd=(hi[name]-lo[name])/(2*h)
                self.assertLess(abs(fd/d[name+'_prime']-1),3e-9)

    def test_massless_exact_initial_quadrupole(self):
        for A in (-.8,0.,.8):
            m=PreparedKinetic(.2,A).moments(0.,0.)
            self.assertAlmostEqual(m['pi_r'],A/15,places=14)

    def test_batch_matches_scalar_and_is_immutable(self):
        o=PreparedKinetic(.8,-.4)
        x=np.linspace(0.,np.log(7),31);b=.08*np.sin(x)
        v=o.moments_batch(x,b,chunk=7)
        for i in range(x.size):
            s=o.moments(float(x[i]),float(b[i]))
            for k in v:self.assertAlmostEqual(v[k][i],s[k],places=14)
        with self.assertRaises(ValueError):o.weights[0,0]=0.

    def test_domain_guards(self):
        with self.assertRaises(ValueError):PreparedKinetic(2.01,0.)
        with self.assertRaises(ValueError):PreparedKinetic(0.,-1.01)
        with self.assertRaises(ValueError):PreparedKinetic().moments(0.,4.)

if __name__=='__main__':unittest.main()
