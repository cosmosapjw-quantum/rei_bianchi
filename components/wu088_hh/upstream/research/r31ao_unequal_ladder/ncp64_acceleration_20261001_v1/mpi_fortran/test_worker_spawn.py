import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from export_worklist import export

HERE=Path(__file__).resolve().parent
TOY='''import argparse,json,os,signal,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('--manifest');p.add_argument('--task-index',type=int);a=p.parse_args()
d=json.load(open(a.manifest));out=d['output']
def stop(sig,frame):
 open(out,'w').write(json.dumps({'signal':sig}));sys.exit(2)
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
if d.get('mode')=='sleep':
 open(out+'.ready','w').write('ready');time.sleep(30)
if d.get('mode')=='leak':
 child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 open(out+'.child','w').write(str(child.pid))
inherited=False
if 'NCP_TEST_FD' in os.environ:
 try:os.fstat(int(os.environ['NCP_TEST_FD']));inherited=True
 except OSError:pass
json.dump({'task_index':a.task_index,'manifest':a.manifest,'env':dict(os.environ),'pgid':os.getpgrp(),'pid':os.getpid(),'test_fd_inherited':inherited},open(out,'w'))
sys.exit(d.get('exit',0))
'''


class ShimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build=tempfile.TemporaryDirectory()
        cls.exe=Path(cls.build.name)/'spawn_cli'
        cls.compile_command=['/usr/bin/gcc','-std=c11','-O3','-fno-fast-math','-ffp-contract=off',
                     '-Wall','-Wextra','-Werror','-pedantic',str(HERE/'worker_spawn.c'),
                     str(HERE/'spawn_cli.c'),'-o',str(cls.exe)]
        subprocess.run(cls.compile_command,check=True,capture_output=True,text=True,timeout=20)

    @classmethod
    def tearDownClass(cls): cls.build.cleanup()

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.worker=self.root/'worker ; literal $(echo unsafe).py';self.worker.write_text(TOY)
        self.manifest=self.root/'manifest ; literal.json';self.output=self.root/'result.json'

    def tearDown(self):self.tmp.cleanup()

    def command(self,mode='ok',exit=0,seconds=3):
        self.manifest.write_text(json.dumps({'mode':mode,'exit':exit,'output':str(self.output)}))
        return [str(self.exe),sys.executable,str(self.worker),str(self.manifest),'17',str(seconds)]

    def test_literal_argv_environment_and_distinct_process_group(self):
        env=dict(os.environ,OMPI_FAKE='bad',PMIX_FAKE='bad',PMI_FAKE='bad',MPI_FAKE='bad',
                 MPICH_FAKE='bad',I_MPI_FAKE='bad',HYDRA_FAKE='bad',OPENBLAS_NUM_THREADS='9',OMP_NUM_THREADS='9')
        p=subprocess.run(self.command(),env=env,capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
        d=json.loads(self.output.read_text());self.assertEqual(d['task_index'],17)
        self.assertEqual(d['manifest'],str(self.manifest));self.assertEqual(d['pid'],d['pgid'])
        self.assertFalse(any(k.startswith(('OMPI_','PMIX_','PMI_','MPI_','MPICH_','I_MPI_','HYDRA_')) for k in d['env']))
        self.assertEqual(d['env']['OMP_NUM_THREADS'],'1');self.assertEqual(d['env']['OPENBLAS_NUM_THREADS'],'1')

    def test_nonzero_worker_status_is_preserved(self):
        p=subprocess.run(self.command(exit=7),capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stdout)['shim_status'],7)

    def test_unrelated_descriptor_not_inherited(self):
        with (self.root/'private_descriptor').open('w') as descriptor:
            env=dict(os.environ,NCP_TEST_FD=str(descriptor.fileno()))
            p=subprocess.run(self.command(),env=env,pass_fds=(descriptor.fileno(),),capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertFalse(json.loads(self.output.read_text())['test_fd_inherited'])

    def test_successful_leader_with_live_group_is_failure_and_cleaned(self):
        p=subprocess.run(self.command(mode='leak'),capture_output=True,text=True,timeout=10)
        child=int(Path(str(self.output)+'.child').read_text())
        try:
            self.assertEqual(json.loads(p.stdout)['shim_status'],1106)
            deadline=time.monotonic()+2
            while Path(f'/proc/{child}/stat').exists():
                state=Path(f'/proc/{child}/stat').read_text().split()[2]
                if state=='Z':break
                if time.monotonic()>deadline:self.fail('child remained executable after shim returned')
                time.sleep(.01)
        finally:
            try:os.kill(child,signal.SIGKILL)
            except ProcessLookupError:pass

    def test_missing_absolute_executable_fails(self):
        command=self.command();command[1]='/nonexistent/ncp64-python'
        p=subprocess.run(command,capture_output=True,text=True,timeout=10)
        self.assertEqual(json.loads(p.stdout)['shim_status'],1100)

    def test_posix_spawn_error_is_reported(self):
        bad=self.root/'bad-executable';bad.write_text('not executable format');bad.chmod(0o700)
        command=self.command();command[1]=str(bad)
        p=subprocess.run(command,capture_output=True,text=True,timeout=10)
        self.assertEqual(json.loads(p.stdout)['shim_status'],1103)

    def test_watchdog_requests_worker_cleanup(self):
        p=subprocess.run(self.command(mode='sleep',seconds=1),capture_output=True,text=True,timeout=10)
        self.assertEqual(json.loads(p.stdout)['shim_status'],124)
        self.assertEqual(json.loads(self.output.read_text())['signal'],signal.SIGTERM)

    def test_parent_sigterm_relay_and_reaping(self):
        p=subprocess.Popen(self.command(mode='sleep',seconds=10),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        deadline=time.monotonic()+5
        while not Path(str(self.output)+'.ready').exists():
            if time.monotonic()>deadline: p.kill();self.fail('toy worker not ready')
            time.sleep(.01)
        p.send_signal(signal.SIGTERM);out,err=p.communicate(timeout=8)
        self.assertEqual(json.loads(out)['shim_status'],128+signal.SIGTERM,err)
        self.assertEqual(json.loads(self.output.read_text())['signal'],signal.SIGTERM)


class WorklistTests(unittest.TestCase):
    def test_cost_order_deadlines_create_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);m=root/'m.json';out=root/'worklist.txt'
            d={'schema':'WU088_NCP64_TASK_MANIFEST_V1','scope':'SYNTHETIC_ONLY','tasks':[
                {'task_id':name,'cost_hint':cost,'limits':{'wall_seconds':5}}
                for name,cost in [('z',1),('b',9),('a',9)]]}
            m.write_text(json.dumps(d));r=export(m,out)
            self.assertEqual(r['dispatch_order'],[2,1,0]);self.assertEqual(out.read_text(),'3\n2 15\n1 15\n0 15\n')
            with self.assertRaises(FileExistsError):export(m,out)
            d['dispatch_order']=[0,1,2];m.write_text(json.dumps(d))
            with self.assertRaises(ValueError):export(m,root/'bad')

    def test_actual_scope_and_bool_index_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);m=root/'m.json'
            d={'schema':'WU088_NCP64_TASK_MANIFEST_V1','scope':'ACTUAL_HH','tasks':[]}
            m.write_text(json.dumps(d))
            with self.assertRaises(ValueError):export(m,root/'bad')
            d.update(scope='SYNTHETIC_ONLY',tasks=[{'task_id':'a','cost_hint':1,'limits':{'wall_seconds':1}}],dispatch_order=[False])
            m.write_text(json.dumps(d))
            with self.assertRaises(ValueError):export(m,root/'bad')


if __name__=='__main__':unittest.main()
