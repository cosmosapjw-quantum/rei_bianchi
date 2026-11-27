"""Manufactured spline tests only; no eigensolve or frozen physical state read."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
from scipy.interpolate import BSpline

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
import direct_stream as stream


def axis(edges, degree=3):
    edges = np.asarray(edges, dtype=float)
    knots = np.r_[np.repeat(edges[0], degree), edges,
                  np.repeat(edges[-1], degree)]
    n = len(knots)-degree-1
    return SimpleNamespace(edges=edges,
                           basis=BSpline(knots, np.eye(n), degree, extrapolate=False))


def manufactured_pair():
    radial = axis([1., 1.0001, 1.02, 1.07, 1.2, 1.6, 2.3, 3.])
    angular = axis([-1., -.9, -.6, -.2, .15, .4, .7, .9, 1.])
    states = []
    for m in (0, 1):
        nr, na = radial.basis.c.shape[1], angular.basis.c.shape[1]
        states.append(SimpleNamespace(
            m=m, R=2., ZA=1., ZB=2., xi_max=3.,
            _radial=radial, _angular=angular, normalization=.3,
            radial_coefficients=np.linspace(.2, 1., nr)**(m+1),
            angular_coefficients=np.linspace(.3, .7, na)**(m+1)))
    return states


class DirectStreamingTests(unittest.TestCase):
    def test_complete_tensor_nodes_weights_and_order_are_identical(self):
        g, b = manufactured_pair()
        # Unequal state partitions exercise the original union-knot contract.
        b._angular = axis([-1., -.8, -.2, .15, .45, .9, 1.])
        for batch in (1, 32, 64):
            batches = list(stream.patch_batches(g, b, order=7, batch_patches=batch))
            actual = [np.concatenate([item[i] for item in batches]) for i in range(4)]
            expected = stream.fast._patches(g, b, 7, False)
            for a, e in zip(actual, expected):
                np.testing.assert_array_equal(a, e)

    def test_direct_batch1_batch32_full_matches_parent_both_backends(self):
        g, b = manufactured_pair()
        for backend in ('python', 'native'):
            old = stream.fast.direct(g, b, order=10, backend=backend)
            for batch in (1, 32, 56):
                with patch.object(stream.fast, '_patches',
                                  side_effect=AssertionError('full quadrature forbidden')):
                    new = stream.direct(g, b, order=10, backend=backend, batch_patches=batch)
                for key in stream.DIRECT_KEYS:
                    self.assertAlmostEqual(new[key], old[key], delta=2.e-13)
                meta = new['streaming']
                self.assertEqual(meta['points'], 56*100)
                self.assertEqual(meta['maximum_batch_points'], min(56, batch)*100)
                self.assertEqual(meta['full_quadrature_materialized'], batch >= 56)
                self.assertFalse(meta['unbounded_domain_materialization'])
                self.assertFalse(meta['bitwise_parent_identity_claimed'])

    def test_native_python_direct_parity(self):
        g, b = manufactured_pair()
        a = stream.direct(g, b, order=12, backend='python')
        c = stream.direct(g, b, order=12, backend='native')
        for key in stream.DIRECT_KEYS:
            self.assertAlmostEqual(a[key], c[key], delta=2.e-13)

    def test_dark_batch1_batch32_full_matches_parent(self):
        g, b = manufactured_pair()
        for backend in ('python', 'native'):
            old = stream.fast.dark(g, b, order=10, phi_nodes=32, backend=backend)
            for batch in (1, 32, 56):
                with patch.object(stream.fast, '_patches',
                                  side_effect=AssertionError('full quadrature forbidden')):
                    new = stream.dark(g, b, order=10, phi_nodes=32,
                                      backend=backend, batch_patches=batch)
                for key, value in old.items():
                    if isinstance(value, float):
                        self.assertAlmostEqual(new[key], value, delta=2.e-13)
                    else:
                        self.assertEqual(new[key], value)
                self.assertEqual(new['streaming']['actual_operator_backend'], 'numpy')
                self.assertEqual(new['angular_sin_cos_factor'], old['angular_sin_cos_factor'])

    def test_invalid_inputs_fail_before_evaluation(self):
        g, b = manufactured_pair()
        for value in (True, 1, 0, 3.5):
            with self.assertRaises(ValueError):
                stream.direct(g, b, order=value, backend='python')
        for value in (True, 0, 65, 1.5):
            with self.assertRaises(ValueError):
                stream.direct(g, b, batch_patches=value, backend='python')
        for value in (True, 3, 0, 4.5):
            with self.assertRaises(ValueError):
                stream.dark(g, b, phi_nodes=value, backend='python')
        with self.assertRaises(ValueError):
            stream.direct(g, b, backend='automatic')
        with self.assertRaises(ValueError):
            stream.dark(g, b, backend='automatic')
        with self.assertRaises(ValueError):
            stream.direct(g, b, order=100_000, backend='python')
        for edges in ([1., 1., 3.], [1., np.nan, 3.], [1.1, 3.], [1., 2.9]):
            g, b = manufactured_pair()
            g._radial = SimpleNamespace(edges=np.asarray(edges))
            with self.assertRaises(ValueError):
                stream.direct(g, b, backend='python')

    def test_invalid_state_and_native_failure_never_fall_back(self):
        g, b = manufactured_pair()
        b.radial_coefficients[0] = np.nan
        with self.assertRaises(ValueError):
            stream.direct(g, b, backend='python')
        g, b = manufactured_pair()
        with patch.object(stream.fast, '_native', side_effect=RuntimeError('identity mismatch')):
            with self.assertRaises(RuntimeError):
                stream.direct(g, b, backend='native')
        with patch.object(stream.fast, 'native_identity', side_effect=RuntimeError('identity mismatch')):
            with self.assertRaises(RuntimeError):
                stream.dark(g, b, backend='native')


if __name__ == '__main__':
    unittest.main()
