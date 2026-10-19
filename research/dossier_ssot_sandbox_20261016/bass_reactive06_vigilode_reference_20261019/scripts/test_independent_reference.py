#!/usr/bin/env python3
"""Seven newly reconstructed recovery R1 controls; not restored old test bytes."""
from decimal import Decimal, localcontext
import math
import os
from pathlib import Path
import unittest
import numpy as np
from decimal_oracles_r1 import phi,j_jk
from independent_birth_reference import Fixture,PathGrid,EV_J,CHI,verner


class ConstantGeometry:
    def __init__(self,h):self.h=h
    def at(self,q):
        q=np.asarray(q);a=np.exp(self.h*q)
        return np.repeat(a[...,None],3,axis=-1),np.full(q.shape+(3,),self.h),a**3


class ConstantFixture:
    def __init__(self,rates,h):self.dt=1.;self.geometry=ConstantGeometry(h);self.k=np.array(rates)
    def rates(self,energy,volume):return np.broadcast_to(self.k,np.asarray(energy).shape+(4,))


class RecoveryControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f=Fixture(Path(os.environ['BR06_PARENT']))

    def test_phi_limits(self):
        with localcontext() as c:
            c.prec=110;c.Emin=-999999999999999999;c.Emax=999999999999999999
            self.assertEqual(phi(Decimal(0)),1)
            self.assertGreater(phi(Decimal('1e-300')),0)
            self.assertLess(abs(phi(Decimal('1e12'))*Decimal('1e12')-1),Decimal('1e-100'))
            self.assertLess(abs(phi(Decimal(1))-(1-Decimal(-1).exp())),Decimal('1e-100'))

    def test_dyadic_moment_identity(self):
        with localcontext() as c:
            c.prec=110
            for z in map(Decimal,('0','.01','1','10')):
                for j in range(3):
                    for k in range(3):
                        rhs=(sum(Decimal(math.comb(k,l))*j_jk(z,j,l) for l in range(k+1))+
                             (-z).exp()*sum(Decimal(math.comb(j,r))*j_jk(z,r,k) for r in range(j+1)))/Decimal(2)**(j+k+1)
                        self.assertLess(abs(rhs-j_jk(2*z,j,k)),Decimal('1e-95'))

    def test_direct_time_competition_heat_work(self):
        for scale in (.001,.1,10.):
            rates=scale*np.array([1.,2.,3.,4.]);kt=float(sum(rates));h=.01;E0=80.
            f=ConstantFixture(rates,h)
            out=PathGrid(f,np.array([0.]),128,16).evaluate(np.array([[E0,0.,0.]]))
            ph=-math.expm1(-kt)/kt;pe=-math.expm1(-(kt+h))/(kt+h)
            np.testing.assert_allclose(out['events'][0],rates*ph,rtol=2e-12,atol=1e-15)
            self.assertAlmostEqual(out['P'][0],math.exp(-kt),delta=2e-14)
            expected_heat=rates*(E0*pe-CHI*ph)*EV_J
            np.testing.assert_allclose(out['heat'][0],expected_heat,rtol=3e-12,atol=1e-32)
            self.assertLess(abs(out['work'][0]-(-h*E0*pe*EV_J))/abs(h*E0*pe*EV_J),3e-12)

    def test_transparent_geometric_work(self):
        h=.03;E0=80.;f=ConstantFixture([0.,0.,0.,0.],h)
        out=PathGrid(f,np.array([0.]),32,8).evaluate(np.array([[E0,0.,0.]]))
        self.assertEqual(out['P'][0],1.)
        self.assertTrue(np.all(out['events']==0))
        self.assertTrue(np.all(out['heat']==0))
        expected=E0*math.expm1(-h)*EV_J
        self.assertLess(abs(out['work'][0]/expected-1),2e-14)

    def test_actual_parent_geometry_opacity_source(self):
        checks=self.f.validate_recorded_inputs()
        self.assertEqual(checks['birth_rows'],19664)
        self.assertLess(checks['max_axes_relative'],2e-13)
        self.assertLess(checks['max_H_relative'],3e-13)
        self.assertLess(checks['max_midpoint_opacity_relative'],2e-13)

    def test_H_D_binding_and_fit_gates(self):
        energy=np.array([CHI[0],13.599,13.60,13.601,CHI[3]])
        rates=self.f.rates(energy,np.full(len(energy),self.f.anchor))
        self.assertTrue(np.all(rates[:2,0]==0))
        self.assertTrue(np.all(rates[2:,0]>0))
        self.assertTrue(np.all(rates[:-1,3]==0))
        self.assertGreater(rates[-1,3],0)
        self.assertTrue(np.all(rates[:,1:3]==0))

    def test_invalid_geometry_and_photon_inputs_rejected(self):
        for q in (-.01,1.01,float('nan')):
            with self.assertRaises(ValueError):self.f.geometry.at(np.array([q]))
        for e in (-1.,0.,50001.,float('nan')):
            with self.assertRaises(ValueError):verner(np.array([e]),0)
        with self.assertRaises(ValueError):
            PathGrid(self.f,np.array([0.]),8,8).evaluate(np.array([[float('nan'),0.,0.]]))


if __name__=='__main__':unittest.main(verbosity=2)
