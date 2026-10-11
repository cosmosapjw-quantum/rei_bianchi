"""New C10 positive-step checks; never replays a previous campaign."""
import math
import sys
from pathlib import Path
import unittest
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent))
from positive_absorption import prepare_incident,absorb
from reconstruction import InvalidCone,TraceRequired,QuadratureNotConverged
from opacity_native import NativeOpacity,C_CM_S


def grey(energy):
    return np.broadcast_to(np.array([1e-18,2e-18,3e-18]),(len(energy),3)).copy()


class PositiveAbsorptionTests(unittest.TestCase):
    def test_grey_stiff_and_counter_pairing(self):
        p=prepare_incident(2.,80.,1.,20.,60.,grey)
        lower=np.array([.01,.02,.03])
        rate=C_CM_S*float(lower@np.array([1e-18,2e-18,3e-18]))
        for stiffness in (0.,1e-6,1.,1e6,1e16):
            h=stiffness/rate
            out=absorb(p,lower,h)
            self.assertAlmostEqual(out['N']/(2./(1+stiffness)),1.,places=12)
            self.assertAlmostEqual(out['U']/(80./(1+stiffness)),1.,places=12)
            self.assertLess(abs(out['N']+sum(out['number_absorbed_species'])-2.)/2.,1e-12)
            self.assertLess(abs(out['U']+sum(out['energy_absorbed_species'])-80.)/80.,1e-12)

    def test_affine_fitted_moments(self):
        # The number kernel is affine in physical q: its integral follows
        # directly from N,U and is independent of the closure reconstruction.
        def affine(E):
            return (1e-18*(1+E/60.))[:,None]*np.ones((1,3))
        p=prepare_incident(7.,252.,.8,20.,80.,affine)
        out=absorb(p,[0.,0.,0.],4e15)
        expected=C_CM_S*1e-18*(7.+252./60.)
        np.testing.assert_allclose(out['K0'],expected,rtol=1e-12,atol=0)
        self.assertTrue(np.all(p.P>0))
        self.assertLess(abs(math.fsum(p.P)-7.)/7.,1e-12)
        self.assertLess(abs(math.fsum(p.q*p.P)*.8-252.)/252.,1e-12)
        np.testing.assert_array_equal(out['number_absorbed_species'],np.zeros(3))

    def test_empty_and_domain_rejections(self):
        def forbidden(_):raise AssertionError('Empty state called opacity')
        p=prepare_incident(0.,0.,1.,20.,20.,forbidden)
        out=absorb(p,[1.,1.,1.],1.)
        self.assertEqual(out['N'],0.)
        self.assertEqual(out['U'],0.)
        np.testing.assert_array_equal(out['K0'],np.zeros(3))
        with self.assertRaises(InvalidCone):prepare_incident(0.,1.,1.,20.,60.,grey)
        with self.assertRaises(TraceRequired):prepare_incident(1.,20.,1.,20.,60.,grey)
        with self.assertRaises(QuadratureNotConverged):
            prepare_incident(1.,1.+3e-10,1.,1.,1.+1e-9,grey)
        with self.assertRaises(ValueError):absorb(p,[-1.,0.,0.],1.)
        with self.assertRaises(ValueError):absorb(p,[0.,0.,0.],-1.)
        with self.assertRaises(ValueError):prepare_incident(1.,40.,1.,20.,60.,lambda E: -np.ones((len(E),3)))
        with self.assertRaises(QuadratureNotConverged):
            prepare_incident(1.,40.,1.,20.,60.,
                lambda E: ((1.+.9*np.sin(1000.*E))*1e-18)[:,None]*np.ones((1,3)))

    def test_actual_native_high_energy_cell(self):
        with NativeOpacity() as opacity:
            p=prepare_incident(1e-12,4.97e-8,1.,49000.,50000.,opacity)
            out=absorb(p,[1e-4,8e-6,1e-7],1e15)
            self.assertEqual(opacity.native_calls,2)
            self.assertTrue(np.all(out['K0']>0))
            self.assertTrue(np.all(out['energy_absorbed_species']>0))
            self.assertLess(out['diagnostics']['order_pair_max_error'],1e-7)
            self.assertLess(abs(out['diagnostics']['number_pairing_relative_residual']),1e-12)
            self.assertLess(abs(out['diagnostics']['energy_pairing_relative_residual']),1e-12)
            self.assertLess(max(out['diagnostics']['native_counter_link_component_errors']),1e-12)


if __name__=='__main__':unittest.main(verbosity=2)
