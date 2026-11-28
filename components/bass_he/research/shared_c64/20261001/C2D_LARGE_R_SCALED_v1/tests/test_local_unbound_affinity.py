"""Fresh-process ABI load and environment checks; no physical workload."""
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

STAGE=Path(__file__).resolve().parents[1]
REAL=STAGE.parent/'BASS_HE_C2D_LARGE_R_SCALED_20261001_v1'
sys.path[:0]=[str(STAGE/'code'),str(REAL/'code')]
from mpi_batch import child_environment


class LocalUnboundTests(unittest.TestCase):
    def test_explicit_core_clears_stale_local_marker(self):
        with patch.dict(os.environ,{'BASS_LOCAL_UNBOUND':'1','OMP_PROC_BIND':'FALSE'}):
            env=child_environment(binding='core')
        self.assertEqual(env['BASS_LOCAL_UNBOUND'],'0');self.assertEqual(env['OMP_PROC_BIND'],'close')

    def test_explicit_none_propagates_to_nested_worker(self):
        env=child_environment(binding='none')
        self.assertEqual(env['OMP_PROC_BIND'],'FALSE')
        with patch.dict(os.environ,env,clear=True):nested=child_environment()
        self.assertEqual(nested['OMP_PROC_BIND'],'FALSE');self.assertEqual(nested['BASS_LOCAL_UNBOUND'],'1')

    def test_invalid_marker_fails_closed(self):
        with patch.dict(os.environ,{'BASS_LOCAL_UNBOUND':'maybe'}):
            with self.assertRaises(ValueError):child_environment()

    def test_native_abi_load_preserves_all_allowed_cpus(self):
        library=REAL/'native/build/libbass_element.so'
        script='''import ctypes,json,os,sys
before=sorted(os.sched_getaffinity(0))
lib=ctypes.CDLL(sys.argv[1]);lib.bass_native_abi.restype=ctypes.c_int
lib.bass_native_max_threads.restype=ctypes.c_int
abi=lib.bass_native_abi();threads=lib.bass_native_max_threads()
after=sorted(os.sched_getaffinity(0))
assert abi==3 and threads==1 and before==after
print(json.dumps(dict(before=before,after=after,abi=abi,threads=threads)))
'''
        completed=subprocess.run([sys.executable,'-c',script,str(library)],env=child_environment(binding='none'),
                                  capture_output=True,text=True,check=True,timeout=15)
        evidence=json.loads(completed.stdout)
        self.assertEqual(evidence['before'],sorted(os.sched_getaffinity(0)))
        self.assertEqual(completed.stderr,'')


if __name__=='__main__':unittest.main()
