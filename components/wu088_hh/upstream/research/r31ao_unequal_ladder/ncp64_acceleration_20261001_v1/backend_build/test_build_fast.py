import unittest
from pathlib import Path
import build_fast as b


class BuildPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior, cls.gate, cls.hp = b.modules()

    def ready(self, cpu=64, mem=112):
        return {'status': 'PLAN_READY', 'cpu_budget': cpu,
                'job_memory_budget_bytes': mem*b.GiB}

    def test_ncp_build_uses_memory_bounded_56_not_fixed_two(self):
        c = b.configuration(self.prior, self.ready())
        self.assertEqual(c['jobs'], 56)
        self.assertEqual(c['memory_mib'], 2048)

    def test_small_host_and_cpu_reserve(self):
        self.assertEqual(b.configuration(self.prior, self.ready(8, 6))['jobs'], 3)
        self.assertEqual(b.configuration(self.prior, self.ready(1, 2))['jobs'], 1)

    def test_overbudget_or_bool_job_refused(self):
        for n in (0, 57, 100, True):
            with self.assertRaises(ValueError):
                b.configuration(self.prior, self.ready(), n)

    def test_blocked_memory_not_silently_increased(self):
        with self.assertRaises(ValueError):
            b.configuration(self.prior, {'status': 'BLOCKED'})
        with self.assertRaises(ValueError):
            b.configuration(self.prior, self.ready(8, 1))

    def test_strict_flags_and_existing_limits_preserved(self):
        c = b.configuration(self.prior, self.ready())
        for k, v in self.prior.CONFIG.items():
            if k not in ('jobs', 'memory_mib'):
                self.assertEqual(c[k], v)
        tools = {k: '/usr/bin/'+v for k, v in self.prior.TOOL_NAMES.items()}
        env = self.prior.clean_environment(Path('/scratch/build'),
                                           Path('/scratch/build/prefix'), tools, c)
        self.assertEqual(env['CFLAGS'], '-O2 -fno-fast-math -ffp-contract=off')
        self.assertEqual(env['OMP_NUM_THREADS'], '1')

    def test_steps_dependency_order_and_test_fanout(self):
        c = b.configuration(self.prior, self.ready())
        tools = {k: '/usr/bin/'+v for k, v in self.prior.TOOL_NAMES.items()}
        steps = b.steps(self.prior, Path('/scratch/build'), tools, c)
        self.assertEqual([s['library'] for s in steps if s['stage'] == 'configure'],
                         ['gmp', 'mpfr', 'flint'])
        for s in steps:
            if s['stage'] == 'build':
                self.assertEqual(s['argv'], ['/usr/bin/make', '-j56'])
            if s['stage'] == 'check':
                self.assertIn('-j2', s['argv'])
        self.assertEqual(sum(s['stage'] == 'bootstrap' for s in steps), 1)

    def test_old_input_lock_is_still_required(self):
        result = self.prior.check_input_lock()
        self.assertEqual(result['status'], 'PRIOR_CODE_BYTES_VERIFIED')
        self.assertFalse(result['actual_HH_input_loader_in_pipeline'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
