#!/usr/bin/env python3
"""Meaningful adverse tests for the integration contract. No large quadrature."""
import ctypes,importlib.util,json,os,shutil,subprocess,sys,tempfile,time,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from native_support import (Radial,build_radial,checked_manifest,save_checkpoint,
                           load_checkpoint,array_schema,sha)

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SOURCE=ROOT/'cont2c/analytic/hybrid_radial.cpp'
EVIDENCE=HERE/'evidence'

class Support(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(tempfile.mkdtemp(prefix='adverse-',dir=EVIDENCE))
        cls.cache=cls.root/'cache'
        cls.radial=Radial(SOURCE,cls.cache)
        cls.measurements={'build_key':cls.radial.folder.name,'abi':cls.radial.abi,
                          'source_sha256':sha(SOURCE),'tests':[]}
    def test_01_exact_legacy_values(self):
        spec=importlib.util.spec_from_file_location('legacy_radial_for_control',SOURCE.with_suffix('.py'))
        legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
        x=np.array([-32,-1,-.5,0,.5,32,256,512],np.clongdouble)+np.clongdouble('0.5j')
        counts=0
        for order in range(3):
            old=legacy.radial_moments(1,2*x,order);new=self.radial.radial_moments(1,2*x,order)
            for a,b in zip(old,new):self.assertTrue(np.array_equal(a,b));counts+=a.size
        self.measurements['exact_legacy_numeric_values']=counts
    def test_02_order_validation(self):
        for order in (-1,3,True,1.0):
            with self.assertRaises(ValueError):self.radial.radial_moments(1,0,order)
    def test_03_finite_variance_and_domain(self):
        for v,s in [(0,0),(-1,0),(np.inf,0),(1,np.nan),(1,1025),(1,4.01j),([],[])]:
            with self.assertRaises(ValueError):self.radial.radial_moments(v,s)
        with self.assertRaises(TypeError):self.radial.radial_moments(1+0j,0)
    def test_04_unaligned_and_reversed_input(self):
        buf=bytearray(3*np.dtype(np.longdouble).itemsize+1)
        v=np.ndarray((3,),np.longdouble,buffer=buf,offset=1);v[:]=[1,2,3]
        self.assertFalse(v.flags.aligned)
        a=self.radial.radial_moments(v[::-1],0)
        b=self.radial.radial_moments(np.array([3,2,1],np.longdouble),0)
        self.assertTrue(all(np.array_equal(x,y) for x,y in zip(a,b)))
    def test_05_native_buffer_and_order_guard(self):
        lp=ctypes.POINTER(ctypes.c_longdouble);v=np.ones(1,np.longdouble);out=np.empty(60,np.longdouble);it=ctypes.c_int()
        ptr=v.ctypes.data_as(lp);op=out.ctypes.data_as(lp)
        fn=self.radial.lib.production_radial
        self.assertEqual(fn(1,ptr,1,ptr,1,ptr,1,3,op,60,ctypes.byref(it)),-101)
        self.assertEqual(fn(1,ptr,1,ptr,1,ptr,1,2,op,59,ctypes.byref(it)),-102)
        self.assertEqual(fn(1,None,1,ptr,1,ptr,1,2,op,60,ctypes.byref(it)),-101)
    def test_06_rounding_mode_rejected(self):
        libc=ctypes.CDLL(None);libc.fegetround.restype=ctypes.c_int
        libc.fesetround.argtypes=[ctypes.c_int];libc.fesetround.restype=ctypes.c_int
        old=libc.fegetround()
        try:
            self.assertEqual(libc.fesetround(0x400),0) # FE_DOWNWARD, tested Linux x86_64 target.
            with self.assertRaisesRegex(ValueError,'-103'):self.radial.radial_moments(1,0)
        finally:libc.fesetround(old)
    def test_07_concurrent_build_clients(self):
        cache=self.root/'concurrent_cache'
        with ThreadPoolExecutor(max_workers=3) as pool:
            paths=list(pool.map(lambda _:build_radial(SOURCE,cache),range(3)))
        self.assertEqual(len(set(paths)),1)
        self.assertEqual(len([p for p in cache.iterdir() if p.is_dir()]),1)
        checked_manifest(paths[0])
    def test_08_source_change_same_mtime(self):
        source=self.root/'changed.cpp';source.write_bytes(SOURCE.read_bytes());stamp=source.stat().st_mtime_ns
        first=build_radial(source,self.cache)
        source.write_bytes(source.read_bytes()+b'\n// same mtime, changed content\n')
        os.utime(source,ns=(stamp,stamp));second=build_radial(source,self.cache)
        self.assertNotEqual(first.name,second.name)
    def test_09_cache_corruption_rejected(self):
        cache=self.root/'corrupt_cache';cache.mkdir()
        dest=cache/self.radial.folder.name;shutil.copytree(self.radial.folder,dest)
        # Do not touch a loaded library. This is a private copied build.
        (dest/'radial.so').write_bytes(b'corrupt')
        with self.assertRaisesRegex(RuntimeError,'artifact corrupt'):build_radial(SOURCE,cache)
    def test_10_abi_mismatch_rejected(self):
        source=self.root/'wrong_abi.cpp'
        source.write_bytes(SOURCE.read_bytes()+b'\n#undef LDBL_MANT_DIG\n#define LDBL_MANT_DIG 53\n')
        with self.assertRaisesRegex(RuntimeError,'ABI or rounding mismatch'):Radial(source,self.cache)
    def test_11_checkpoint_roundtrip_and_identity(self):
        arrays={'raw':np.array([1+2j,3+4j],np.clongdouble),'sumabs':np.array([3,7],np.longdouble)}
        identity={'source':sha(SOURCE),'build':self.radial.folder.name,'grid':'fixture-only'}
        row=self.root/'row';seal=save_checkpoint(row,identity,arrays)
        actual=load_checkpoint(row,identity,array_schema(arrays),manifest_sha256=seal)
        self.assertTrue(all(np.array_equal(actual[k],a) for k,a in arrays.items()))
        with self.assertRaises(FileExistsError):save_checkpoint(row,identity,arrays)
        with self.assertRaisesRegex(RuntimeError,'identity mismatch'):load_checkpoint(row,{'source':'wrong'},array_schema(arrays))
        with self.assertRaisesRegex(RuntimeError,'schema mismatch'):load_checkpoint(row,identity,{'bad':{}})
        (row/'arrays.npz').write_bytes(b'corrupt')
        with self.assertRaisesRegex(RuntimeError,'data hash mismatch'):load_checkpoint(row,identity,array_schema(arrays))
    def test_12_interrupted_checkpoint_not_visible(self):
        arrays={'raw':np.ones(2)};partial=self.root/'.checkpoint-interrupted';partial.mkdir()
        (partial/'arrays.npz').write_bytes(b'partial ZIP')
        with self.assertRaises(FileNotFoundError):load_checkpoint(self.root/'missing-row',{},array_schema(arrays))
    def test_13_compile_failure_preserved(self):
        bad=self.root/'bad.cpp';bad.write_text('#error intentional compile failure\n')
        with self.assertRaises(Exception):build_radial(bad,self.root/'failure_cache')
        failures=list((self.root/'failure_cache').glob('failed-*/failure.json'))
        self.assertEqual(len(failures),1)
        self.assertIn('intentional compile failure',json.loads(failures[0].read_text())['stderr'])
    def test_14_checkpoint_invalid_arrays(self):
        for arrays in ({'raw':np.array([np.nan])},{'raw':np.array([object()])},{'raw':np.array([])}):
            with self.assertRaises(ValueError):save_checkpoint(self.root/'bad-checkpoint',{},arrays)
    def test_15_native_exception_translated(self):
        source=self.root/'throw.cpp'
        original=SOURCE.read_text()
        source.write_text('#include <stdexcept>\n'+original.replace(
            'const R pi=acosl(-1.L),rootpi=sqrtl(pi);',
            'throw std::runtime_error("intentional native failure");\nconst R pi=acosl(-1.L),rootpi=sqrtl(pi);'))
        radial=Radial(source,self.cache)
        with self.assertRaisesRegex(ValueError,'-105'):radial.radial_moments(1,0)
    def test_16_killed_writer_before_commit(self):
        target=self.root/'killed-row'
        code='''import sys\nfrom pathlib import Path\nimport numpy as np\nimport native_support as ns\ndef pause(p):\n print("READY",flush=True)\n sys.stdin.readline()\nns.sync_dir=pause\nns.save_checkpoint(Path(sys.argv[1]),{"fixture":"kill"},{"raw":np.ones(2)})\n'''
        proc=subprocess.Popen([sys.executable,'-c',code,str(target)],cwd=HERE,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            self.assertEqual(proc.stdout.readline().strip(),'READY')
            proc.kill();proc.wait(timeout=5)
            self.assertFalse(target.exists())
            self.assertTrue(list(self.root.glob('.checkpoint-*/arrays.npz')))
            with self.assertRaises(FileNotFoundError):load_checkpoint(target,{'fixture':'kill'},{'raw':{'shape':[2],'dtype':'<f8'}})
        finally:
            if proc.poll() is None:proc.kill();proc.wait(timeout=5)
            proc.stdin.close();proc.stdout.close();proc.stderr.close()
    @classmethod
    def tearDownClass(cls):
        (EVIDENCE/'MEASUREMENTS.json').write_text(json.dumps(cls.measurements,indent=2)+'\n')

if __name__=='__main__':
    EVIDENCE.mkdir(exist_ok=True)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Support))
    (EVIDENCE/'TEST_RESULTS.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),
        'errors':len(result.errors),'success':result.wasSuccessful(),'scope':'owner engineering tests; not independent science'},indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() else 1)
