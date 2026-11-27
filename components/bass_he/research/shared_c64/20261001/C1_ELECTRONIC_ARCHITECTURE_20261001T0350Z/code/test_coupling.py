"""New operator-specific analytic and failure checks; no repeated atomic solves."""
from types import SimpleNamespace
from pathlib import Path
import unittest,json
import numpy as np
from coupling import direct,torque

class AtomicMock:
    """Exact He 1s/2px about B; optional charge-center lever is geometric only."""
    R=2.; ZB=2.
    def __init__(self,m,ZA=0.):
        self.m=m; self.ZA=ZA; self.energy=-self.ZB**2/(2*(m+1)**2)
        self.xi_max=25.
        self._radial=SimpleNamespace(edges=1+24*np.linspace(0,1,25)**2)
        self._angular=SimpleNamespace(edges=np.linspace(-1,1,15))
    def evaluate(self,xi,eta):
        xi,eta=np.broadcast_arrays(xi,eta); c=self.R/2
        r=c*(xi-eta); z=self.ZB
        if self.m==0:
            G=np.sqrt(2)*z**1.5*np.exp(-z*r)
            return G,-z*c*G,z*c*G
        p=xi*xi-1; q=1-eta*eta
        rho=c*np.sqrt(p*q)
        rx=c*xi*np.sqrt(q/p); re=-c*eta*np.sqrt(p/q)
        f=z**2.5/(4*np.sqrt(2))*np.exp(-z*r/2)
        return rho*f,(rx-z*c*rho/2)*f,(re+z*c*rho/2)*f

class CouplingTests(unittest.TestCase):
    def test_analytic_atomic_direct_and_force(self):
        g,b=AtomicMock(0),AtomicMock(1)
        d=direct(g,b,16); t=torque(g,b,24)
        expected_d=128*np.sqrt(2)/(243*g.ZB)
        self.assertLess(abs(d['dipole_x']-expected_d),2e-11)
        self.assertLess(abs(d['p_x_bar']-(b.energy-g.energy)*expected_d),2e-11)
        self.assertLess(abs(d['L_O_bar']),2e-11)
        self.assertEqual(t['L_O_bar'],0.)
        self.assertLess(abs(d['norm_g']-1),2e-11)
        self.assertLess(abs(d['norm_b']-1),2e-11)
    def test_nonzero_origin_lever_on_known_states(self):
        g,b=AtomicMock(0,1),AtomicMock(1,1)
        d=direct(g,b,16)
        expected_p=3*g.ZB**2/8*128*np.sqrt(2)/(243*g.ZB)
        self.assertLess(abs(d['L_B_bar']),2e-11)
        self.assertLess(abs(d['L_O_bar']-g.R/3*expected_p),2e-11)
    def test_dark_and_equal_charge_parity_algebra(self):
        # Exact Fourier / meridional parity identities, no physical solve claimed.
        phi=2*np.pi*np.arange(32)/32
        self.assertLess(abs(np.mean(np.sin(phi)*np.cos(phi))),1e-15)
        # For equal charges, lowest G,A are even in z: torque is odd in eta.
        x,w=np.polynomial.legendre.leggauss(24)
        even=np.exp(x*x)
        odd=(2-x)**-3-(2+x)**-3
        self.assertLess(abs(np.dot(w,even*odd)),1e-15)
    def test_invalid_pair_and_q_rejected(self):
        with self.assertRaises(ValueError):direct(AtomicMock(1),AtomicMock(0))
        with self.assertRaises(ValueError):torque(AtomicMock(0),AtomicMock(1),1)
        b=AtomicMock(1);b.energy=-3
        with self.assertRaises(ValueError):torque(AtomicMock(0),b)

if __name__=='__main__':unittest.main(verbosity=2)
