"""Independent Linux lifetime probes; Python fixtures only, zero HH calls."""
import importlib.util, json, os, pathlib, select, signal, subprocess, sys, unittest
HERE=pathlib.Path(__file__).resolve().parent
HOST=HERE.parent/'process_host/host.py'
spec=importlib.util.spec_from_file_location('independent_host',HOST);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
PYTHON=str(pathlib.Path(sys.executable).resolve())
ENV={'PATH':'/usr/bin:/bin','LC_ALL':'C','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
IMPORT=f"import importlib.util,os,sys,time; s=importlib.util.spec_from_file_location('h',{str(HOST)!r});h=importlib.util.module_from_spec(s);s.loader.exec_module(h);"

class HostReview(unittest.TestCase):
 def test_wrong_expected_parent_refused_before_program(self):
  cmd=[str(h.BUILD/'guarded_exec'),str(os.getpid()+10000000),str(256*1024*1024),str(h.MAX_JSON),'5','1','0','--',PYTHON,'-c',"print('SHOULD_NOT_EXECUTE')"]
  p=subprocess.run(cmd,capture_output=True,timeout=5,env=ENV)
  self.assertEqual(p.returncode,125)
  self.assertNotIn(b'SHOULD_NOT_EXECUTE',p.stdout)
 def test_seccomp_refuses_native_fork_and_thread_creation(self):
  script="import os,threading,json; results=[]\ntry:\n os.fork();results.append('fork unexpectedly allowed')\nexcept OSError as e: results.append(e.errno)\ntry:\n t=threading.Thread(target=lambda:None);t.start();t.join();results.append('thread unexpectedly allowed')\nexcept RuntimeError:results.append('thread refused')\nprint(json.dumps(results))"
  p=h._launch([PYTHON,'-c',script],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=ENV,memory_mib=256,cpu_seconds=5,nofork=True)
  out,err=p.communicate(timeout=5)
  self.assertEqual(p.returncode,0,err)
  self.assertEqual(json.loads(out),[1,'thread refused'])
 def test_dispatcher_death_terminates_worker_and_native_pidfds(self):
  leaf="import json,os,time;print(json.dumps({'leaf':os.getpid()}),flush=True);time.sleep(30)"
  worker=IMPORT+f"print(__import__('json').dumps({{'worker':os.getpid()}}),flush=True);p=h._launch([{PYTHON!r},'-c',{leaf!r}],stdout=None,stderr=None,env={ENV!r},memory_mib=256,cpu_seconds=5,nofork=True);p.wait()"
  dispatcher=IMPORT+f"p=h.spawn_guarded([{PYTHON!r},'-c',{worker!r}],stdout=None,stderr=None,env={ENV!r},memory_mib=512);p.wait()"
  p=subprocess.Popen([PYTHON,'-c',dispatcher],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=ENV,bufsize=0)
  fds=[]
  try:
   found={}
   for _ in range(2):
    self.assertTrue(select.select([p.stdout],[],[],5)[0],'process-chain ready timeout')
    found.update(json.loads(p.stdout.readline()))
   self.assertEqual(set(found),{'worker','leaf'})
   fds=[os.pidfd_open(found[k]) for k in ('worker','leaf')]
   p.kill();self.assertEqual(p.wait(timeout=5),-signal.SIGKILL)
   poll=select.poll()
   for fd in fds:poll.register(fd,select.POLLIN)
   remaining=set(fds)
   deadline=__import__('time').monotonic()+5
   while remaining and __import__('time').monotonic()<deadline:
    for fd,event in poll.poll(100):
     if event&select.POLLIN:remaining.discard(fd)
   self.assertFalse(remaining,'known worker/native still alive after dispatcher death')
  finally:
   if p.poll() is None:p.kill();p.wait(timeout=5)
   for fd in fds:
    try:signal.pidfd_send_signal(fd,signal.SIGKILL)
    except ProcessLookupError:pass
    finally:os.close(fd)
   p.stdout.close();p.stderr.close()

if __name__=='__main__':unittest.main(verbosity=2)
