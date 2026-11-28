"""Host contracts. FakeCgroup tests do NOT verify Linux cgroup containment."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import cgroup_guard as c
import launcher as h
import containment_probe


class FakeCgroup:
    """Mock only the unavailable cgroup API; a real direct child runs below."""
    def __init__(self, root): self.path=Path(root)/'pid'; self.killed=False
    def enter(self): self.path.write_text(str(os.getpid()))
    def populated(self): return False
    def snapshot(self): return {'memory_events':{},'pids_events':{},'events':{'populated':0}}
    def kill_and_empty(self):
        self.killed=True
        if self.path.exists():
            try: os.kill(int(self.path.read_text()),signal.SIGKILL)
            except ProcessLookupError: pass


class HostTests(unittest.TestCase):
    def test_root_containment_probe_refuses_before_creation(self):
        with tempfile.TemporaryDirectory() as d, patch.object(os,'getuid',return_value=0):
            out=Path(d)/'must_not_exist'
            with self.assertRaisesRegex(ValueError,'nonroot'): containment_probe.probe('/sys/fs/cgroup',out,[0])
            self.assertFalse(out.exists())

    def test_root_refuses_before_plan_or_process(self):
        with patch.object(h.os,'getuid',return_value=0),patch.object(h,'prepare_plan') as plan:
            with self.assertRaisesRegex(ValueError,'NONROOT'): h.run(argparse.Namespace())
            plan.assert_not_called()

    def test_ordinary_directory_is_not_cgroup(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'real cgroup'): c.real_cgroup2(d)

    def test_strict_cgroup_caps(self):
        for options in ({'memory_bytes':True,'ranks':1,'pids':32},
                        {'memory_bytes':128*1024**2,'ranks':65,'pids':32},
                        {'memory_bytes':128*1024**2,'ranks':1,'pids':0}):
            with self.assertRaisesRegex(ValueError,'caps'):c.JobCgroup('/not-used',**options)

    def test_fixed_argv_has_no_root_or_remote_escape(self):
        plan={'rank_count':2,'mpirun':{'path':'/usr/bin/mpirun'},'python':{'path':'/usr/bin/python3'},
            'run_root':'/tmp/new','plan_payload_sha256':'a'*64}
        argv=h.fixed_argv(plan)
        self.assertIn('localhost:2',argv);self.assertIn('--nooversubscribe',argv)
        self.assertNotIn('--allow-run-as-root',argv);self.assertEqual(argv[-1],'a'*64)

    def test_real_direct_process_success_with_mock_cgroup(self):
        with tempfile.TemporaryDirectory() as d:
            group=FakeCgroup(d)
            r=c.execute_contained([sys.executable,'-I','-c','print(42)'],group=group,output=d,
                seconds=2,cpus=sorted(os.sched_getaffinity(0))[:1],env={'PATH':'/usr/bin:/bin'})
            self.assertEqual(r['status'],'COMPLETED');self.assertTrue(r['process_started']);self.assertTrue(group.killed)

    def test_real_wall_limit_with_mock_cgroup(self):
        with tempfile.TemporaryDirectory() as d:
            group=FakeCgroup(d)
            r=c.execute_contained([sys.executable,'-I','-c','import time;time.sleep(30)'],group=group,output=d,
                seconds=1,cpus=sorted(os.sched_getaffinity(0))[:1],env={'PATH':'/usr/bin:/bin'})
            self.assertEqual(r['status'],'JOB_WALL_LIMIT');self.assertLess(r['wall_seconds'],3)
            self.assertEqual(r['returncode'],-signal.SIGKILL)

    def test_preexec_failure_not_counted_as_started(self):
        with tempfile.TemporaryDirectory() as d:
            group=FakeCgroup(d)
            with patch.object(group,'enter',side_effect=OSError('deliberate refused entry')):
                r=c.execute_contained([sys.executable,'-I','-c','print(42)'],group=group,output=d,
                    seconds=1,cpus=sorted(os.sched_getaffinity(0))[:1],env={'PATH':'/usr/bin:/bin'})
            self.assertEqual(r['status'],'LAUNCH_OR_SUPERVISION_ERROR');self.assertFalse(r['process_started'])
            self.assertIsNone(r['returncode'])

    def test_cleanup_failure_propagates_no_success(self):
        with tempfile.TemporaryDirectory() as d:
            group=FakeCgroup(d)
            with patch.object(group,'kill_and_empty',side_effect=c.Refusal('CGROUP_CLEANUP_NOT_EMPTY')):
                with self.assertRaisesRegex(ValueError,'CLEANUP'):
                    c.execute_contained([sys.executable,'-I','-c','print(42)'],group=group,output=d,
                        seconds=1,cpus=sorted(os.sched_getaffinity(0))[:1],env={'PATH':'/usr/bin:/bin'})

    def test_sessions_escape_process_group_only_cleanup(self):
        # Falsifiable evidence for rejecting the former process-group fallback.
        # Child PID comes from our own pipe, not a /proc namespace mapping.
        code="import os,subprocess,sys,time; p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)'],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); print(p.pid,flush=True); time.sleep(20)"
        p=subprocess.Popen([sys.executable,'-I','-c',code],stdout=subprocess.PIPE,text=True,start_new_session=True)
        child=None
        try:
            child=int(p.stdout.readline())
            self.assertEqual(os.getsid(child),child)
            os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=2)
            os.kill(child,0) # detached grandchild remains alive
        finally:
            if p.poll() is None:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=2)
            if child is not None:
                try:os.kill(child,signal.SIGKILL)
                except ProcessLookupError:pass
            p.stdout.close()


if __name__=='__main__':unittest.main()
