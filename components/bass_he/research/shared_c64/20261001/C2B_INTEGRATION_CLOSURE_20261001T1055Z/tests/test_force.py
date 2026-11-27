"""Manufactured tests: must run before evaluation of frozen physical states."""
import math
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
import force_integral as force


def dummy_pair():
    radial = SimpleNamespace(edges=np.array([1., 1.0001, 1.02, 1.4, 3.]))
    angular = SimpleNamespace(edges=np.array([-1., -.6, .2, 1.]))
    common = dict(R=2., ZA=1., ZB=2., xi_max=3., _radial=radial,
                  _angular=angular)
    return (SimpleNamespace(m=0, energy=-2., **common),
            SimpleNamespace(m=1, energy=-.5, **common))


class ManufacturedEvaluator:
    def __init__(self, state):
        self.m = state.m

    def values(self, xi, eta):
        if self.m == 0:
            return np.ones_like(xi)
        return np.sqrt((xi*xi-1)*(1-eta*eta))*(xi+eta)**3


class ForceQuadratureTests(unittest.TestCase):
    def test_partition_moments_and_geometry(self):
        xe, ye = [1., 1.0001, 1.03, 2.], [-1., -.8, .6, 1.]
        cells, meta = force.rectangles(xe, ye)
        self.assertGreater(meta['splits'], 0)
        self.assertAlmostEqual(sum((b-a)*(d-c) for a,b,c,d in cells), 2., places=14)
        for a,b,c,d in cells:
            hx, hy = b-a, d-c
            distance = a-1+min(c+1,1-d)
            self.assertLessEqual(max(hx,hy), 2*(distance+min(hx,hy)))
        x,y,w,counts,meta = force.patches_from_edges(xe, ye, 6)
        self.assertAlmostEqual(float(np.sum(w)), 2., places=14)
        self.assertAlmostEqual(float(np.sum(w*x)), 3., places=14)
        self.assertAlmostEqual(float(np.sum(w*y)), 0., places=14)
        self.assertAlmostEqual(float(np.sum(w*x*y*y)), 1., places=14)
        self.assertEqual(int(sum(counts)), meta['points'])

    def test_anisotropic_weak_corner_exact_integral(self):
        a, b = 1.e-4, 2.
        x,y,w,_,_ = force.patches_from_edges([1.,1+a],[-1.,1.],12)
        actual_a = (1+a)-1
        exact = ((actual_a+b)*math.log(actual_a+b)
                 -actual_a*math.log(actual_a)-b*math.log(b))
        actual = float(np.sum(w/((x-1)+(y+1))))
        self.assertLess(abs(actual-exact), 2.e-12)

    def test_original_geometry_matches_parent_nodes(self):
        g,b = dummy_pair()
        xi,eta,w,counts,_ = force.patches_from_edges(g._radial.edges,g._angular.edges,4,'original')
        old = force.fast._patches(g,b,4,True)
        for a,c in zip((xi,eta,w,counts),old):
            np.testing.assert_array_equal(a,c)

    def test_manufactured_exact_force_python(self):
        g,b = dummy_pair()
        with patch.object(force.fast,'Evaluator',ManufacturedEvaluator):
            result = force.torque(g,b,order=12,backend='python')
        expected = g.R/(2*np.sqrt(2))*(4/15)*(3.**5-2*3.**3+3.)
        self.assertLess(abs(result['T_A']-expected), 3.e-12)
        self.assertEqual(result['gap'], 1.5)
        self.assertAlmostEqual(result['L_B_bar'],-g.ZA*g.R*result['T_A']/1.5)

    def test_manufactured_native_matches_python(self):
        g,b = dummy_pair()
        with patch.object(force.fast,'Evaluator',ManufacturedEvaluator):
            a = force.torque(g,b,order=12,backend='python')
            c = force.torque(g,b,order=12,backend='native')
        for key in ('T_A','T_B','L_O_bar','L_B_bar'):
            self.assertLess(abs(a[key]-c[key]), 4.e-12)

    def test_streamed_batch1_batch32_full_reference_parity(self):
        g,b = dummy_pair()
        order = 12
        for variant in ('balanced','original'):
            x,y,w,counts,metadata = force.patches_from_edges(
                g._radial.edges,g._angular.edges,order,variant)
            G,A = ManufacturedEvaluator(g).values(x,y), ManufacturedEvaluator(b).values(x,y)
            full = np.zeros(2)
            force.fast._native().bass_torque(len(x),len(counts),counts,x,y,w,G,A,g.R,full)
            with patch.object(force.fast,'Evaluator',ManufacturedEvaluator), \
                 patch.object(force,'patches_from_edges',side_effect=AssertionError('no full arrays')):
                for batch_size in (1,32):
                    result = force.torque(g,b,order=order,backend='native',
                                          variant=variant,batch_patches=batch_size)
                    np.testing.assert_allclose([result['T_A'],result['T_B']],full,rtol=0,atol=1.e-11)
                    self.assertEqual(result['points'], metadata['points'])
                    self.assertEqual(result['patches'], len(counts))
                    self.assertEqual(result['batches'], math.ceil(len(counts)/batch_size))
                    self.assertLessEqual(result['maximum_batch_points'],batch_size*order*order)
                    self.assertFalse(result['full_quadrature_materialized'])

    def test_input_rejection(self):
        for edges in ([1.,1.], [0.,2.], [1.,np.nan]):
            with self.assertRaises(ValueError):
                force.rectangles(edges,[-1.,1.])
        with self.assertRaises(ValueError):
            force.patches_from_edges([1.,2.],[-1.,1.],True)
        with self.assertRaises(ValueError):
            force.rectangles([1.,2.],[-1.,1.],variant='adaptive_fit')
        for batch in (0,65,True):
            with self.assertRaises(ValueError):
                list(force.patch_batches([(1.,2.,-1.,0.)],4,batch))
        with self.assertRaises(RuntimeError):
            force.rectangles(np.linspace(1.,2.,252),np.linspace(-1.,1.,252))
        g,b = dummy_pair()
        b.energy = g.energy
        with self.assertRaises(ValueError):
            force.torque(g,b,backend='python')

    def test_single_angular_cell_separates_two_corners(self):
        cells, _ = force.rectangles([1.,3.],[-1.,1.])
        self.assertFalse(any(a == 1 and c == -1 and d == 1 for a,b,c,d in cells))
        _,_,_,_,meta = force.patches_from_edges([1.,3.],[-1.,1.],6)
        self.assertEqual(meta['duffy_cells'], 2)


if __name__ == '__main__':
    unittest.main()
