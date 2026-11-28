"""Lifecycle tests use synthetic Python children only; no HH invocations."""
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("host_under_test", HERE / "host.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
PYTHON = str(Path(sys.executable).resolve())
ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "OPENBLAS_NUM_THREADS": "1",
       "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}


class HostTests(unittest.TestCase):
    def test_exec_pid_limits_and_seccomp_fork_refusal(self):
        script = ("import os,resource,json,errno\n"
                  "try:\n os.fork(); raise RuntimeError('fork unexpectedly admitted')\n"
                  "except OSError as e:\n assert e.errno==errno.EPERM\n"
                  "print(json.dumps({'pid':os.getpid(),'as':resource.getrlimit(resource.RLIMIT_AS),"
                  "'cpu':resource.getrlimit(resource.RLIMIT_CPU),'core':resource.getrlimit(resource.RLIMIT_CORE)}))")
        p = h._launch([PYTHON, "-c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      env=ENV, memory_mib=256, cpu_seconds=3, nofork=True)
        out, err = p.communicate(timeout=5)
        self.assertEqual(p.returncode, 0, err)
        result = json.loads(out)
        self.assertEqual(result["pid"], p.pid)
        self.assertEqual(result["as"], [256 * 1024 * 1024] * 2)
        self.assertEqual(result["cpu"], [3, 3])
        self.assertEqual(result["core"], [0, 0])

    def test_wrong_parent_refused_before_payload(self):
        cmd = [str(h.BUILD / "guarded_exec"), str(os.getpid() + 100000), str(256 * 1024 * 1024),
               str(h.MAX_JSON), "3", "1", "0", "--", PYTHON, "-c", "print('SHOULD_NOT_RUN')"]
        p = subprocess.run(cmd, capture_output=True, timeout=5)
        self.assertEqual(p.returncode, 125)
        self.assertNotIn(b"SHOULD_NOT_RUN", p.stdout)
        self.assertIn(b"parent changed", p.stderr)

    def test_parent_death_chain_closes_native_pipe(self):
        # The grandchild owns the inherited stdout pipe. EOF after parent SIGKILL
        # is independent of /proc visibility and shows it is no longer alive.
        leaf = "import os,time;print('LEAF_READY',os.getpid(),flush=True);time.sleep(30)"
        worker = ("import importlib.util,subprocess,time\n"
                  f"s=importlib.util.spec_from_file_location('h',{str(HERE / 'host.py')!r});h=importlib.util.module_from_spec(s);s.loader.exec_module(h)\n"
                  f"p=h._launch([{PYTHON!r},'-c',{leaf!r}],stdout=None,stderr=None,env={ENV!r},memory_mib=256,cpu_seconds=5,nofork=True)\n"
                  "p.wait()")
        parent = h.spawn_guarded([PYTHON, "-c", worker], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  env=ENV, memory_mib=512)
        try:
            ready, _, _ = select.select([parent.stdout], [], [], 5)
            self.assertTrue(ready, "grandchild did not signal readiness")
            self.assertTrue(parent.stdout.readline().startswith(b"LEAF_READY"))
            parent.kill()
            parent.wait(timeout=5)
            ready, _, _ = select.select([parent.stdout], [], [], 5)
            self.assertTrue(ready, "native stdout remained open after worker death")
            self.assertEqual(parent.stdout.read(), b"")
        finally:
            if parent.poll() is None:
                parent.kill(); parent.wait(timeout=5)
            parent.stdout.close(); parent.stderr.close()

    def test_dispatcher_death_propagates_two_exec_edges(self):
        leaf = "import os,time;print('CHAIN_READY',os.getpid(),flush=True);time.sleep(30)"
        middle = ("import importlib.util\n"
                  f"s=importlib.util.spec_from_file_location('h',{str(HERE / 'host.py')!r});h=importlib.util.module_from_spec(s);s.loader.exec_module(h)\n"
                  f"h._launch([{PYTHON!r},'-c',{leaf!r}],stdout=None,stderr=None,env={ENV!r},memory_mib=256,cpu_seconds=5,nofork=True).wait()")
        dispatcher = ("import importlib.util\n"
                      f"s=importlib.util.spec_from_file_location('h',{str(HERE / 'host.py')!r});h=importlib.util.module_from_spec(s);s.loader.exec_module(h)\n"
                      f"h.spawn_guarded([{PYTHON!r},'-c',{middle!r}],stdout=None,stderr=None,env={ENV!r},memory_mib=512).wait()")
        p = subprocess.Popen([PYTHON, "-c", dispatcher], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
        try:
            self.assertTrue(select.select([p.stdout], [], [], 5)[0])
            self.assertTrue(p.stdout.readline().startswith(b"CHAIN_READY"))
            p.kill(); p.wait(timeout=5)
            self.assertTrue(select.select([p.stdout], [], [], 5)[0])
            self.assertEqual(p.stdout.read(), b"")
        finally:
            if p.poll() is None:
                p.kill(); p.wait(timeout=5)
            p.stdout.close(); p.stderr.close()

    def test_hardwall_kill_wait_and_raw_rejection(self):
        class FakeDriver:
            DriverError = ValueError
            parse_json = staticmethod(json.loads)
            validate_result = staticmethod(lambda *_args, **_kw: {})
            @staticmethod
            def write_new(out, record):
                with Path(out).open("x") as stream:
                    json.dump(record, stream)
        d = FakeDriver()
        h.install(d)
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "result.json"
            limits = {"memory_mib": 256, "wall_seconds": 1}
            started = time.monotonic()
            with self.assertRaisesRegex(ValueError, "EXTERNAL_WALL_CAP"):
                d.execute_bound_native([PYTHON, "-c", "import time;print('started',flush=True);time.sleep(30)"], ENV,
                                       limits, {}, out, {"plan_sha256": "p"}, {"index": 0, "task_sha256": "t"}, {})
            self.assertLess(time.monotonic() - started, 9)
            result = json.loads(out.read_bytes())
            self.assertEqual(result["reason"], "EXTERNAL_WALL_CAP")
            self.assertEqual(result["returncode"], -signal.SIGKILL)
            self.assertFalse(result["wrapper"]["native_execution_observed"])
            self.assertEqual(Path(str(out) + ".stdout").read_bytes(), b"started\n")
            h.validate_receipt(result["wrapper"]["process_host"], command=[PYTHON, "-c", "import time;print('started',flush=True);time.sleep(30)"],
                               limits=limits, output_path=out)

    def test_python_driver_import_under_1024mib(self):
        ladder = HERE.parents[1]
        driver_path = ladder / "wide_domain_20261001_v1/range_native_driver/driver.py"
        script = ("import importlib.util,json,resource\n"
                  f"s=importlib.util.spec_from_file_location('d',{str(driver_path)!r});d=importlib.util.module_from_spec(s);s.loader.exec_module(d)\n"
                  "a,g=d.dependencies();print(json.dumps({'dependencies_loaded':True,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))")
        p = h.spawn_guarded([PYTHON, "-c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=ENV, memory_mib=1024)
        out, err = p.communicate(timeout=10)
        self.assertEqual(p.returncode, 0, err)
        self.assertTrue(json.loads(out)["dependencies_loaded"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
