"""Only synthetic sleep processes; no MPI or scientific calculations."""
from pathlib import Path
import copy
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from unittest.mock import patch

CODE = Path(__file__).resolve().parents[1] / "code"
sys.path.insert(0, str(CODE))
import mpi_batch
from process_guard import (TASK_TOKEN_ENV, BATCH_TOKEN_ENV, REGISTRY_NAME,
                           process_identity, registry_record, cleanup_record, cleanup_batch)


def wait_until(predicate, timeout=5):
    deadline = time.monotonic()+timeout
    while time.monotonic()<deadline:
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("synthetic process condition timed out")


def live(pid):
    ident = process_identity(pid)
    return ident is not None and ident["state"] != "Z"


class ProcessCleanupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="c2c-process-test-")
        self.root = Path(self.temporary.name)
        self.batch_token, self.task_token = uuid.uuid4().hex, uuid.uuid4().hex
        self.processes, self.records = [], []

    def tearDown(self):
        for record in self.records:
            cleanup_record(record, self.batch_token, record["task_id"])
        for process in self.processes:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=3)
        self.temporary.cleanup()

    def tree(self):
        pidfile = self.root / (uuid.uuid4().hex+".json")
        body = ("import subprocess,sys,json,time,os;from pathlib import Path;"
                "child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']);"
                f"Path({str(pidfile)!r}).write_text(json.dumps([os.getpid(),child.pid]));time.sleep(60)")
        env = os.environ.copy()
        env.update({TASK_TOKEN_ENV: self.task_token, BATCH_TOKEN_ENV: self.batch_token})
        process = subprocess.Popen([sys.executable,"-c",body],env=env,start_new_session=True)
        self.processes.append(process)
        record = registry_record(process.pid,"owned",self.task_token,self.batch_token)
        self.records.append(record)
        wait_until(pidfile.exists)
        return process, record, json.loads(pidfile.read_text())

    def test_owned_child_and_grandchild_killed_unrelated_untouched(self):
        _,record,pids = self.tree()
        unrelated = subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"],start_new_session=True)
        self.processes.append(unrelated)
        report = cleanup_record(record,self.batch_token,"owned")
        self.assertEqual(report["status"],"NO_LIVE_OWNED_MEMBERS")
        self.assertFalse(any(live(pid) for pid in pids))
        self.assertIsNone(unrelated.poll())

    def test_pid_start_time_mismatch_rejects_without_signal(self):
        _,record,pids = self.tree()
        wrong = copy.deepcopy(record)
        wrong["leader"]["start_time_ticks"] += 1
        report = cleanup_record(wrong,self.batch_token,"owned")
        self.assertEqual(report["status"],"REJECTED")
        self.assertEqual(report["signals"],[])
        self.assertTrue(all(live(pid) for pid in pids))

    def test_wrong_batch_and_unlisted_task_not_touched(self):
        _,record,pids = self.tree()
        out = self.root / "batch"
        directory = out / "owned"
        directory.mkdir(parents=True)
        (directory/REGISTRY_NAME).write_text(json.dumps(record))
        self.assertEqual(cleanup_batch(out,self.batch_token,["different"]),[])
        report = cleanup_batch(out,"wrong-owner",["owned"])[0]
        self.assertEqual(report["status"],"REJECTED")
        self.assertTrue(all(live(pid) for pid in pids))

    def test_gate_prevents_exec_until_registry_release(self):
        marker = self.root/"started"
        r,w = os.pipe()
        env = os.environ.copy()
        env.update({TASK_TOKEN_ENV:self.task_token,BATCH_TOKEN_ENV:self.batch_token})
        command = [sys.executable,str(CODE/"process_guard.py"),"--supervisor-pid",str(os.getpid()),
                   "--gate-fd",str(r),"--",sys.executable,"-c",
                   f"from pathlib import Path;import time;Path({str(marker)!r}).touch();time.sleep(60)"]
        process = subprocess.Popen(command,env=env,start_new_session=True,pass_fds=(r,))
        self.processes.append(process)
        os.close(r)
        record = registry_record(process.pid,"owned",self.task_token,self.batch_token)
        self.records.append(record)
        time.sleep(0.1)
        self.assertFalse(marker.exists())
        os.write(w,b"1");os.close(w)
        wait_until(marker.exists)

    def test_parent_death_kills_guarded_worker(self):
        pidfile,marker = self.root/"pdeath.pid",self.root/"pdeath.started"
        command = [sys.executable,"-c",
                   f"from pathlib import Path;import time;Path({str(marker)!r}).touch();time.sleep(60)"]
        body = f'''import os,subprocess,sys,time
from pathlib import Path
r,w=os.pipe()
p=subprocess.Popen([sys.executable,{str(CODE/'process_guard.py')!r},'--supervisor-pid',str(os.getpid()),'--gate-fd',str(r),'--',*{command!r}],start_new_session=True,pass_fds=(r,))
os.close(r)
Path({str(pidfile)!r}).write_text(str(p.pid))
os.write(w,b'1');os.close(w)
deadline=time.monotonic()+3
while not Path({str(marker)!r}).exists() and time.monotonic()<deadline:time.sleep(.01)
os._exit(0)
'''
        supervisor = subprocess.Popen([sys.executable,"-c",body])
        self.processes.append(supervisor)
        wait_until(marker.exists)
        supervisor.wait(timeout=3)
        pid = int(pidfile.read_text())
        wait_until(lambda:not live(pid))

    def fake_worker(self):
        worker = self.root/"fake_worker.py"
        worker.write_text("""import argparse,json,os,subprocess,sys,time
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--task-json');ap.add_argument('--output-dir');ap.add_argument('--backend');a=ap.parse_args()
child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
Path(a.output_dir,'SYNTHETIC_PIDS.json').write_text(json.dumps([os.getpid(),child.pid]))
time.sleep(60)
""")
        return worker

    def test_task_wall_timeout_cleans_independent_session_descendants(self):
        output = self.root/"task-batch";output.mkdir()
        worker = self.fake_worker()
        with patch.object(mpi_batch,"code_identity",return_value={"sha256":"synthetic"}), \
             patch.object(mpi_batch,"backend_identity",return_value={"backend":"reference"}):
            result = mpi_batch.execute_task({"task_id":"task","parameters":{}},output,"reference",sys.executable,
                     {"per_worker_memory_gib":1.5,"task_wall_seconds":0.4},{"sha256":"synthetic"},1,
                     worker_path=worker,selected_backend={"backend":"reference"})
        pids = json.loads((output/"task/SYNTHETIC_PIDS.json").read_text())
        self.assertEqual(result["failure_class"],"TASK_WALL_TIMEOUT")
        self.assertEqual(result["process_cleanup"]["status"],"NO_LIVE_OWNED_MEMBERS")
        self.assertFalse(any(live(pid) for pid in pids))

    def test_rank_sigterm_runs_active_task_cleanup(self):
        output = self.root/"rank-batch";output.mkdir()
        worker = self.fake_worker()
        body = f'''import sys
sys.path.insert(0,{str(CODE)!r})
import mpi_batch
mpi_batch.code_identity=lambda:{{'sha256':'synthetic'}}
mpi_batch.backend_identity=lambda backend:{{'backend':'reference'}}
mpi_batch.execute_task({{'task_id':'task','parameters':{{}}}},{str(output)!r},'reference',sys.executable,
 {{'per_worker_memory_gib':1.5,'task_wall_seconds':60}},{{'sha256':'synthetic'}},1,
 worker_path={str(worker)!r},selected_backend={{'backend':'reference'}})
'''
        supervisor = subprocess.Popen([sys.executable,"-c",body])
        self.processes.append(supervisor)
        pidfile = output/"task/SYNTHETIC_PIDS.json"
        wait_until(pidfile.exists)
        pids = json.loads(pidfile.read_text())
        supervisor.send_signal(signal.SIGTERM)
        supervisor.wait(timeout=4)
        self.assertEqual(supervisor.returncode,128+signal.SIGTERM)
        wait_until(lambda:not any(live(pid) for pid in pids))


if __name__ == "__main__":
    unittest.main()
