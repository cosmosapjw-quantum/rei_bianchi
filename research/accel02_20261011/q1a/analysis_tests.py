#!/usr/bin/env python3
"""Bounded comparison-meaning regressions; no historical run or ODE replay."""
import unittest

import numpy as np

from compare import metric, pair_identities, PROTECTED


class FrozenGateSemantics(unittest.TestCase):
    def test_zero_reference_requires_exact_zero(self):
        zeros = np.zeros(129)
        changed = zeros.copy()
        changed[0] = np.nextafter(0., 1.)
        self.assertTrue(metric(zeros, zeros, np.arange(129), 1e-3)['pass_budget'])
        self.assertFalse(metric(changed, zeros, np.arange(129), 1e-3)['pass_budget'])

    def test_65_and_129_have_their_own_reference_amplitude(self):
        fine = np.ones(129)
        fine[1] = 100.
        coarse = fine.copy()
        coarse[2] += .01
        full = metric(coarse, fine, np.arange(129), 1e-3)
        subset = metric(coarse, fine, np.arange(0, 129, 2), 1e-3)
        self.assertEqual(full['fine_whole_history_amplitude'], 100.)
        self.assertEqual(subset['fine_whole_history_amplitude'], 1.)
        self.assertTrue(full['pass_budget'])
        self.assertFalse(subset['pass_budget'])
        self.assertEqual(subset['worst_epoch_index'], 2)

    def test_nonfinite_field_fails_closed(self):
        fine = np.ones(129)
        fine[64] = np.nan
        with self.assertRaisesRegex(ValueError, 'NONFINITE_OR_NON129_FIELD'):
            metric(np.ones(129), fine, np.arange(0, 129, 2), 1e-3)

    @staticmethod
    def identity(order, rtol):
        result = {key: 'same' for key in PROTECTED}
        result.update(grid_kind='fixed_q_composite_gauss', grid_order=order,
                      grid_sha=f'grid{order}', grid_arrays_sha256=f'arrays{order}',
                      args=dict(angle=2, shear=0., max_step=1/256, rtol=rtol, energy=384*order))
        return result

    @staticmethod
    def grid(order):
        return dict(schema='rei.fixed_q_gauss.v1', panel_edges_eV=[10., 20., 50000., 169000.],
                    n_mu=2, construction={'fixed': True}, input_identity={'source': 'same'},
                    implementation_sha256='same', order=order)

    def test_temporal_gate_cannot_adopt_changed_grid(self):
        left = self.identity(1, 1e-11)
        right = self.identity(2, 3e-12)
        checks = pair_identities(left, right, self.grid(1), self.grid(2), 'time')
        self.assertFalse(checks['same_grid_arrays_sha256'])
        self.assertFalse(all(checks.values()))
        checks = pair_identities(left, self.identity(1, 3e-12), self.grid(1), self.grid(1), 'time')
        self.assertTrue(all(checks.values()))

    def test_spectral_gate_requires_same_time_settings_and_panels(self):
        left, right = self.identity(1, 1e-11), self.identity(2, 1e-11)
        checks = pair_identities(left, right, self.grid(1), self.grid(2), 'spectral')
        self.assertTrue(all(checks.values()))
        right['args']['rtol'] = 3e-12
        checks = pair_identities(left, right, self.grid(1), self.grid(2), 'spectral')
        self.assertFalse(checks['arg_rtol_equal'])
        changed = self.grid(2)
        changed['panel_edges_eV'][1] = 21.
        checks = pair_identities(left, self.identity(2, 1e-11), self.grid(1), changed, 'spectral')
        self.assertFalse(checks['grid_panel_edges_eV'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
