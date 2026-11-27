#!/usr/bin/env python3
"""A real sleeping-process interrupt control; no scientific worker or MPI call."""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import signal
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from common import read,save,sha

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def exercise(module,folder,expect_orphan):
    folder.mkdir(parents=True,exist_ok=False)
    real_popen=subprocess.Popen
    active=[]
    class InterruptOnce:
        def __init__(self,*args,**kwargs):
            # Deliberately replace the MPI command with a harmless real child.
            self.process=real_popen([sys.executable,'-c','import time; time.sleep(30)'],
                                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            self.first=True;active.append(self.process)
        @property
        def pid(self):return self.process.pid
        @property
        def returncode(self):return self.process.returncode
        def poll(self):return self.process.poll()
        def wait(self,timeout=None):
            if self.first:
                self.first=False
                raise KeyboardInterrupt('synthetic boundary interruption; no MPI/scientific run')
            return self.process.wait(timeout=timeout)
    module.verify_closure=lambda *args: {'synthetic_identity_fixture':True}
    old_popen=module.subprocess.Popen;module.subprocess.Popen=InterruptOnce
    old_argv=sys.argv
    sys.argv=['synthetic-entrypoint','--package',str(ROOT),'--output-dir',str(folder/'OUTPUT'),
              '--execution-lock-sha256','0'*64]
    log=io.StringIO()
    try:
        with contextlib.redirect_stdout(log):
            rc=module.main()
        child=active[0]
        orphan=child.poll() is None
        assert rc==1 and orphan==expect_orphan
        failure=read(folder/'OUTPUT/ATTEMPT_FAILURE.json')
        assert failure['error_type']=='KeyboardInterrupt' and failure['automatic_retries']==0
        if not expect_orphan:
            assert failure['cleanup']['quiesced'] and child.returncode is not None
        reply=json.loads(log.getvalue().strip())
        archive=Path(reply['return']['archive'])
        assert sha(archive)==reply['return']['sha256']
        with zipfile.ZipFile(archive) as z:
            manifest=json.loads(z.read('RETURN_MANIFEST.json'))['files']
            assert set(z.namelist())==set(manifest)|{'RETURN_MANIFEST.json'}
            for name,pin in manifest.items():
                raw=z.read(name)
                assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256']
        return {'status':'REPRODUCED_ORPHAN_FAILURE' if expect_orphan else 'PASS_INTERRUPT_CLEANUP_AND_RETURN_BYTES',
                'original_error_type':failure['error_type'],'child_alive_when_old_or_new_main_returned':orphan,
                'child_returncode_before_test_cleanup':child.returncode,
                'failure_archive_sha256':sha(archive),'verified_member_count':len(manifest),
                'scientific_kernel_invocations':0,'MPI_invocations':0,'synthetic_sleeping_processes':1,
                'source_identity_stub':'explicit fixture, not a production or scientific record'}
    finally:
        module.subprocess.Popen=old_popen;sys.argv=old_argv
        for child in active:
            if child.poll() is None:
                os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=5)

def main():
    out=ROOT/'tests/ENTRYPOINT_INTERRUPT_CONTROL'
    out.mkdir(exist_ok=False)
    old=load_module('old_ncp_entrypoint',ROOT/'evidence/PRE_REPAIR_NCP_EXECUTE_BATCH.py')
    new=load_module('new_ncp_entrypoint',ROOT/'code/ncp_execute_batch.py')
    first=exercise(old,out/'FIRST_FAILURE',True)
    fixed=exercise(new,out/'AFTER_REPAIR',False)
    result={'status':'PASS_BOUNDARY_REPAIR','first_failure':first,'after_repair':fixed,
        'old_source_sha256':sha(ROOT/'evidence/PRE_REPAIR_NCP_EXECUTE_BATCH.py'),
        'new_source_sha256':sha(ROOT/'code/ncp_execute_batch.py'),
        'old_orphan_was_terminated_by_test_cleanup':True,'scientific_kernel_invocations':0,'MPI_invocations':0}
    save(ROOT/'tests/NCP_ENTRYPOINT_CONTROL.json',result)
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
