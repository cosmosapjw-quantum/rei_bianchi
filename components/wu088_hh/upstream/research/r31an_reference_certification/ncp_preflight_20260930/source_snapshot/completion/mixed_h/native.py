"""Isolated batched foreign integration and inherited guarded H0."""
import os,sys,json,hashlib,ctypes,subprocess
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'foreign_analytic'),str(ROOT/'exact_weights'),str(ROOT/'exact_weights/deps')]
from guarded_foreign import AnalyticForeign
from exact_laplace_weights import exact_weights,contract
from scipy.special import roots_legendre
LD=np.longdouble;CD=np.clongdouble;DP=ctypes.POINTER(ctypes.c_double);LP=ctypes.POINTER(ctypes.c_longdouble)
PARENT=ROOT/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inputs():
 with np.load(PARENT/'inputs/FROZEN_INPUTS.npz',allow_pickle=False)as f:return {k:f[k]for k in f.files}
def nodes(n):
 x,w=roots_legendre(n);u=(x+1)/2;return u/(1-u),w/2/(1-u)**2
def grid(n,ng=80):
 d=inputs();t,w=nodes(n);U,V=exact_weights(t,w);W=contract(U,V,d['C']);gs,gw=nodes(ng);gw*=2/np.sqrt(np.pi)
 return d,t,W,gs,gw
class Native:
 def __init__(self):
  sources=[HERE/'batched.cpp',ROOT/'production/radial_power/radial_power.cpp',ROOT/'foreign_analytic/analytic.cpp']
  self.identity={str(p.relative_to(ROOT)):sha(p)for p in sources}
  key=hashlib.sha256(json.dumps(self.identity,sort_keys=True).encode()).hexdigest();folder=HERE/'build'/key;folder.mkdir(parents=True,exist_ok=True);lib=folder/'batched.so'
  if not lib.exists():
   command=['g++','-O3','-std=c++17','-fPIC','-shared','-fno-fast-math','-ffp-contract=off',str(HERE/'batched.cpp'),'-o',str(lib)]
   p=subprocess.run(command,capture_output=True,text=True);(folder/'compile.stderr').write_text(p.stderr);(folder/'compile.stdout').write_text(p.stdout)
   if p.returncode:raise RuntimeError('compile failed '+p.stderr)
   (folder/'identity.json').write_text(json.dumps({'sources':self.identity,'command':command},indent=2))
  self.lib=ctypes.CDLL(str(lib));self.lib.mh_foreign.argtypes=[ctypes.c_size_t,ctypes.c_size_t,DP,DP,DP,DP,DP,LP,LP];self.lib.mh_foreign.restype=ctypes.c_int
  self.h=AnalyticForeign(HERE/'cache');self.identity.update(self.h.identity)
 def foreign(self,a,b,t,gs,gw,W,z,q):
  arrays=[np.ascontiguousarray(x,dtype=np.float64)for x in(t,gs,gw,W,np.array([a,b,z,q]))]
  if arrays[3].shape!=(9,len(t),len(t))or gs.shape!=gw.shape:raise ValueError('shape')
  if not all(np.isfinite(x).all()for x in arrays)or np.any(t<=0)or np.any(gs<0):raise ValueError('domain')
  out=np.empty((2,2,3),CD);sa=np.empty((2,2,3),LD)
  status=self.lib.mh_foreign(len(t),len(gs),*[x.ctypes.data_as(DP)for x in arrays],out.ctypes.data_as(LP),sa.ctypes.data_as(LP))
  if status:raise RuntimeError('batched status '+str(status))
  if not np.isfinite(out).all()or not np.isfinite(sa).all():raise FloatingPointError('nonfinite result')
  return out,sa
 def h0(self,a,b,t,W,z,q,active,sign=1,inverted=False):
  v=LD(q);R=np.array([2,0,z],LD);d1=np.zeros(3,LD)if active==0 else-R;d2=-R if active==0 else np.zeros(3,LD)
  q1=0 if active==0 else v;q2=v if active==0 else 0;ka=v/2 if active==0 else-v/2;kb=-ka
  if inverted:d1=-d1;d2=-d2;q1=-q1;q2=-q2;ka=-ka;kb=-kb
  f=self.h.fields(a,b,t[:,None],t[None,:],d1,d2,sign*q1,sign*q2,sign*ka,sign*kb)
  pref=float(inputs()['pref']);norm=np.sqrt(2)*pref*(2*a/np.pi)**.75*(2*b/np.pi)**.75*np.array([1,2*np.sqrt(a),2*np.sqrt(a)])
  return self.h.contract_fields(f,W,norm)
