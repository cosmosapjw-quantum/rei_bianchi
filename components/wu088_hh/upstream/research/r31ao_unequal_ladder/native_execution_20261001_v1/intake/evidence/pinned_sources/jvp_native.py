from pathlib import Path
import sys,ctypes,json,hashlib
sys.dont_write_bytecode=True
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'foreign_analytic'),str(ROOT/'production/engineering')]
import build_native
LD=np.longdouble;CD=np.clongdouble;LP=ctypes.POINTER(ctypes.c_longdouble);DP=ctypes.POINTER(ctypes.c_double);SZ=ctypes.c_size_t
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Native:
 def __init__(self):
  source={'radial_power.cpp':ROOT/'completion/radial/radial_wide.cpp','analytic.cpp':HERE/'jvp.cpp'}
  self.folder=build_native.build(HERE/'build',sources=source);self.manifest=build_native.checked(self.folder)
  self.identity={'key':self.folder.name,'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in source.values()},'adapter':sha(__file__)}
  self.lib=ctypes.CDLL(str(self.folder/'analytic.so'))
  self.lib.mj_probe.argtypes=[ctypes.POINTER(ctypes.c_uint64),SZ];self.lib.mj_probe.restype=ctypes.c_int
  self.lib.mj_pair.argtypes=[SZ,DP,SZ,DP,SZ,DP,SZ,LP,SZ,LP,SZ,LP,SZ];self.lib.mj_pair.restype=ctypes.c_int
  self.lib.mj_point.argtypes=[LP,SZ,ctypes.c_int,LP,SZ];self.lib.mj_point.restype=ctypes.c_int
  p=np.zeros(5,np.uint64);rc=self.lib.mj_probe(p.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),5)
  if rc or p.tolist()!=[np.dtype(LD).itemsize,np.finfo(LD).nmant+1,np.dtype(CD).itemsize,1,1]:raise RuntimeError('mixed JVP ABI mismatch')
 def point(self,a,b,t,u,z,q,power):
  if type(power)is not int or power not in range(9):raise ValueError('integer power0..8 required')
  par=np.array([a,b,t,u,z,q],LD);out=np.empty((2,2,3),CD)
  rc=self.lib.mj_point(par.ctypes.data_as(LP),par.size,power,out.ctypes.data_as(LP),2*out.size)
  if rc:raise ValueError('mixed JVP status '+str(rc))
  return out
 def pair(self,a,b,t,W,z,q,pref):
  t=np.require(t,dtype=np.float64,requirements=['C','A']);W=np.require(W,dtype=np.float64,requirements=['C','A'])
  if t.ndim!=1 or W.shape!=(9,len(t),len(t)):raise ValueError('grid shape')
  # Same binary64 normalization constants as the frozen primitive assembly.
  a=float(a);b=float(b);pf=float(pref);norm0=np.sqrt(2)*pf*(2*a/np.pi)**.75*(2*b/np.pi)**.75
  norm1=np.sqrt(2)*pf*(2*b/np.pi)**.75*(2*a/np.pi)**.75
  norm=np.array([norm0*np.array([1,2*np.sqrt(a),2*np.sqrt(a)]),norm1*np.array([1,2*np.sqrt(b),2*np.sqrt(b)])],np.float64)
  par=np.array([a,b,z,q],LD);out=np.empty((2,2,3),CD);sa=np.empty((2,2,3),LD)
  rc=self.lib.mj_pair(len(t),t.ctypes.data_as(DP),t.size,W.ctypes.data_as(DP),W.size,norm.ctypes.data_as(DP),norm.size,par.ctypes.data_as(LP),par.size,out.ctypes.data_as(LP),2*out.size,sa.ctypes.data_as(LP),sa.size)
  if rc:raise ValueError('mixed JVP status '+str(rc))
  return out,sa
