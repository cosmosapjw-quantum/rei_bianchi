"""Bounded new-adapter tests. No solve_ivp calls or scientific trajectories."""
import hashlib
import json
import math
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
import adapter as ad
import pilot
import resources as rs


class Mechanical(unittest.TestCase):
    def test_exact_vendor(self):
        ad.verify_source()
        self.assertEqual(ad.SOURCE['source_commit'], '3b85dedce84d37b3e165da00685a8a984950aafe')

    def test_grid_identity(self):
        cases = ad.cases()
        self.assertEqual(len(cases), 94)
        self.assertEqual(len({c['id'] for c in cases}), 94)
        self.assertEqual(cases, ad.cases())
        self.assertEqual(sum(not c['config']['guard'] for c in cases), 91)
        self.assertNotEqual(ad.digest({'a': 1}), ad.digest({'a': 2}))

    def test_norm_calibration_initialized(self):
        for s, p in ((0., 0.), (.1, .001), (.1, -.001), (0., .001)):
            config = ad.config(s, p)
            obj = ad.model(config)
            state = obj.initial_state()
            d = obj.fields(0., state)
            sf = math.sqrt(6)*abs(d['s'])/d['H']
            kt = 8*math.pi*ad.fv.G_SI/ad.fv.C_SI**2
            pi = math.sqrt(6)*kt*(d['Pi_radiation_J_m3']+d['Pi_matter_J_m3'])/d['H']**2
            self.assertLessEqual(abs(sf-s), 5e-12)
            self.assertLessEqual(abs(pi-p), 5e-12)
            self.assertEqual(state[0], 0.)
            self.assertEqual(state[1], 0.)
            self.assertEqual(obj.ne_source, None)
            self.assertEqual(d['GammaT'], 0.)
            self.assertAlmostEqual(sf, math.sqrt(2)*d['Sigma'], places=14)

    def test_invalid_amplitude(self):
        with self.assertRaisesRegex(ValueError, 'AMPLITUDE'):
            ad.calibration(.1, 1.)
        for sigma in (-.01, .2, float('nan')):
            with self.assertRaises(ValueError):
                ad.calibration(sigma, 0.)

    def test_immutable_setup_cache(self):
        for power in (3, 4):
            expected = ad._original_matrix(8, None, power)
            actual = ad.cached_matrix(8, None, power)
            self.assertTrue(np.array_equal(expected, actual))
            self.assertIs(actual, ad.cached_matrix(8, None, power))
            with self.assertRaises(ValueError):
                actual[0, 0] = 1
        self.assertIs(ad.momentum(), ad.momentum())
        with self.assertRaises(ValueError):
            ad.momentum().cell_numbers[0, 0] = 1

    def test_resources_busy_and_memory(self):
        gib = rs.GIB
        self.assertEqual(rs.allocation('ncp', None, 64, 128*gib, 120*gib, 0), 1)
        self.assertEqual(rs.allocation('ncp', None, 64, 128*gib, 128*gib, 1), 63)
        self.assertEqual(rs.allocation('sandbox', None, 8, 16*gib, 12*gib, 1), 4)
        self.assertEqual(rs.allocation('ncp', None, 2, 4*gib, .5*gib, .5), 0)
        self.assertEqual(rs.allocation('ncp', 2, 64, 128*gib, 120*gib, 1), 2)

    def test_affinity_ticks_and_conservative_initial_slots(self):
        stat = 'cpu 1000 0 0 99000 0 0 0 0\ncpu0 100 0 0 0 0 0 0 0\ncpu1 0 0 0 100 0 0 0 0\n'
        self.assertEqual(rs.cpu_ticks(stat, {0}), (100, 0))
        self.assertEqual(rs.cpu_ticks(stat, {1}), (100, 100))
        with patch.object(rs, 'cpu_ticks', return_value=(100, 0)), \
             patch.object(rs, 'memory', return_value=(128*rs.GIB, 120*rs.GIB)), \
             patch.object(rs, 'effective_cpus', return_value=64):
            sampler = rs.Sampler()
            self.assertEqual(sampler.sample('ncp')['slots'], 1)
        with patch.object(rs, 'cpu_ticks', side_effect=[(100, 0), (200, 0)]), \
             patch.object(rs, 'memory', return_value=(128*rs.GIB, 120*rs.GIB)), \
             patch.object(rs, 'effective_cpus', return_value=64):
            self.assertEqual(rs.Sampler().sample('ncp')['slots'], 1)

    def test_future_resume_code_mismatch(self):
        with tempfile.TemporaryDirectory(dir=ad.ROOT) as tmp:
            root = Path(tmp)
            identity = pilot.bind_execution_identity(root)
            self.assertEqual(pilot.bind_execution_identity(root), identity)
            changed = dict(identity, numpy_version='changed')
            with patch.object(pilot, 'execution_identity', return_value=changed):
                with self.assertRaisesRegex(ValueError, 'CODE_MISMATCH'):
                    pilot.bind_execution_identity(root)
            moved = dict(identity, python_executable='/other/bin/python3', python_version='other build string')
            with patch.object(pilot, 'execution_identity', return_value=moved):
                self.assertEqual(pilot.bind_execution_identity(root), moved)

    def test_resume_mismatch_and_failure_preservation(self):
        with tempfile.TemporaryDirectory(dir=ad.ROOT) as tmp:
            root = Path(tmp)
            case = ad.cases()[0]
            self.assertEqual(pilot.resume_state(root, case), 'PENDING')
            folder = root/'cases'/case['id']
            pilot.atomic_json(folder/'INPUT.json', case)
            pilot.atomic_json(folder/'ATTEMPT.json', {'profile': 'sandbox'})
            self.assertEqual(pilot.resume_state(root, case), 'INCOMPLETE_PRESERVED')
            pilot.atomic_json(folder/'RESULT.json', {'id': case['id'], 'config': case['config'], 'status': 'FAILED'})
            self.assertEqual(pilot.resume_state(root, case), 'FAILED')
            pilot.atomic_json(folder/'INPUT.json', {'wrong': True})
            with self.assertRaisesRegex(ValueError, 'MISMATCH'):
                pilot.resume_state(root, case)

    def test_bound_controller_launches_zero_without_budget(self):
        with tempfile.TemporaryDirectory(dir=ad.ROOT) as tmp:
            root = Path(tmp)
            manifest = pilot.plan(root)
            approval = root/'review.json'
            pilot.atomic_json(approval, {'decision': 'PASS_SCOPED_EXECUTION',
                                        'contract_sha256': manifest['contract_sha256']})
            before = pilot.LIMITS['sandbox']
            pilot.LIMITS['sandbox'] = dict(before, child_s=0.)
            try:
                result = pilot.run(root, 'sandbox', 1, True, approval)
            finally:
                pilot.LIMITS['sandbox'] = before
            self.assertEqual(set(result['states'].values()), {'PENDING'})
            self.assertEqual(result['cumulative_child_charged_wall_s'], 0)
            self.assertEqual(result['stop_reason'], 'CHILD_WALL_LAUNCH_RESERVATION')


if __name__ == '__main__':
    unittest.main(verbosity=2)
