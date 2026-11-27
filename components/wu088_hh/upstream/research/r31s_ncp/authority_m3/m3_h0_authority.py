"""Minimal exact-source H0 authority adapter for bounded R31T/M3.

It deliberately avoids importing historical WideReference/Production, whose constructor
builds additional guarded-H infrastructure not used by WideReference.h0 after the
H0Fused override. Scientific H0 arithmetic comes from the exact CP4 h0_fused.cpp,
which includes the exact CP4 radial_wide.cpp. Grid/model inputs remain authority-bound.
"""
from __future__ import annotations
from pathlib import Path
import ctypes, hashlib, json, os, shutil, subprocess
import numpy as np

HERE=Path(__file__).resolve().parent
RUNTIME=HERE/'runtime'
MIXED=RUNTIME/'completion/mixed_h'
FROZEN=RUNTIME/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'
H0_SOURCE=MIXED/'h0_fused.cpp'
RADIAL_SOURCE=RUNTIME/'completion/radial/radial_wide.cpp'
EXPECTED={
 'FROZEN_INPUTS.npz':'8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c',
 'h0_fused.cpp':'d019713f8a9c6e864d60cc796104a0cdef629e491e6ab8de757995aa4f3672f2',
 'radial_wide.cpp':'2c20c3e3de8a69a64363806512dde8b3dbae6b818c8aec458893906d9b21399a',
}
FLAGS=['-O3','-std=c++17','-fPIC','-shared','-fno-fast-math','-ffp-contract=off']
LD=np.longdouble;CD=np.clongdouble
DP=ctypes.POINTER(ctypes.c_double);LP=ctypes.POINTER(ctypes.c_longdouble)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify_sources():
 got={'FROZEN_INPUTS.npz':sha(FROZEN),'h0_fused.cpp':sha(H0_SOURCE),'radial_wide.cpp':sha(RADIAL_SOURCE)}
 if got!=EXPECTED: raise RuntimeError('M3 H0 authority source drift: '+repr(got))
 return got

def inputs():
 verify_sources()
 with np.load(FROZEN,allow_pickle=False) as f:return {k:f[k] for k in f.files}

def build(cache:Path):
 verify_sources(); cache=Path(cache).resolve();cache.mkdir(parents=True,exist_ok=True)
 for var in ('LD_PRELOAD','LD_LIBRARY_PATH'):
  if os.environ.get(var): raise RuntimeError(var+' must be unset for trusted M3 H0 build')
 compiler=Path(shutil.which('g++') or '').resolve()
 if not compiler.is_file(): raise RuntimeError('system g++ unavailable')
 spec={'sources':EXPECTED,'flags':FLAGS,'compiler_version':subprocess.run([str(compiler),'--version'],capture_output=True,text=True,check=True).stdout}
 key=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest();folder=cache/key;folder.mkdir(exist_ok=True)
 lib=folder/'h0.so';manifest=folder/'BUILD.json'
 if not lib.exists():
  tmp=folder/'h0.tmp.so';cmd=[str(compiler),*FLAGS,str(H0_SOURCE),'-o',str(tmp)]
  p=subprocess.run(cmd,capture_output=True,text=True)
  (folder/'compile.stdout').write_text(p.stdout);(folder/'compile.stderr').write_text(p.stderr)
  if p.returncode: raise RuntimeError('M3 H0 compile failed: '+p.stderr)
  os.replace(tmp,lib);manifest.write_text(json.dumps({'spec':spec,'command':cmd,'binary_sha256':sha(lib)},indent=2)+'\n')
 else:
  m=json.loads(manifest.read_text())
  if m['spec']!=spec or m['binary_sha256']!=sha(lib):raise RuntimeError('M3 H0 build cache identity mismatch')
 return lib,json.loads(manifest.read_text())

class H0Authority:
 def __init__(self,cache):
  libpath,self.manifest=build(cache);self.lib=ctypes.CDLL(str(libpath))
  self.lib.mh_h0.argtypes=[ctypes.c_size_t,DP,DP,DP,DP,LP,LP];self.lib.mh_h0.restype=ctypes.c_int
  self.lib.precision_bits.restype=ctypes.c_int
  if self.lib.precision_bits()!=np.finfo(LD).nmant+1:raise RuntimeError('M3 H0 precision mismatch')
  self.identity={'source_sha256':dict(EXPECTED),'build':self.manifest}
 def h0(self,a,b,t,W,z,q,active,sign=1,inverted=False):
  d=inputs();t=np.asarray(t);W=np.asarray(W)
  if t.dtype!=np.dtype(np.float64) or W.dtype!=np.dtype(np.float64) or W.shape!=(3,9,t.size,t.size):raise TypeError('exact binary64 grid required')
  if a not in d['exponents'] or b not in d['exponents'] or q!=float(d['v']) or abs(z)>64:raise ValueError('frozen H0 target domain')
  if active not in (0,1) or isinstance(active,(bool,np.bool_)) or sign not in (-1,1) or not isinstance(inverted,(bool,np.bool_)):raise ValueError('H0 labels')
  pars=np.array([a,b,z,q,active,sign,int(inverted)],float)
  norm=np.sqrt(2)*float(d['pref'])*(2*a/np.pi)**.75*(2*b/np.pi)**.75*np.array([1,2*np.sqrt(a),2*np.sqrt(a)],float)
  out=np.empty((7,3),CD);sa=np.empty((7,3),LD)
  rc=self.lib.mh_h0(t.size,np.require(t,requirements=['C','A']).ctypes.data_as(DP),np.require(W,requirements=['C','A']).ctypes.data_as(DP),pars.ctypes.data_as(DP),norm.ctypes.data_as(DP),out.ctypes.data_as(LP),sa.ctypes.data_as(LP))
  if rc:raise RuntimeError('M3 H0 status '+str(rc))
  if not np.isfinite(out).all() or not np.isfinite(sa).all():raise FloatingPointError('M3 H0 nonfinite')
  return out,sa
