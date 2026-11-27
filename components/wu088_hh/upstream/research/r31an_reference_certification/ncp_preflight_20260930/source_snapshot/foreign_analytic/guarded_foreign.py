"""Scoped exact-even / streamed-odd extension of the reviewed GuardedH API."""
from pathlib import Path
import sys,ctypes
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path[:0]=[str(HERE),str(ROOT/'issue_resolution/h_engineering')]
from guarded_h import GuardedH,_array,_real_scalar,ek,ns,LP,UP,Z as SZ
import build_native
LD=np.longdouble;CD=np.clongdouble
DP=ctypes.POINTER(ctypes.c_double)
def ptr(a,typ=LP):return a.ctypes.data_as(typ)
def checked(status):
 if status:raise RuntimeError('foreign analytic status '+str(status))
def insertion(which):
 if isinstance(which,(bool,np.bool_)) or not isinstance(which,(int,np.integer)) or which not in (1,2):
  raise ValueError('insertion must be integer1 or2')
 return int(which)

class AnalyticForeign(GuardedH):
 def __init__(self,cache):
  super().__init__(cache)
  self.newfolder=build_native.build(Path(cache)/'analytic')
  self.newmanifest=build_native.checked(self.newfolder)
  self.newlib=ctypes.CDLL(str(self.newfolder/'analytic.so'))
  sig={'fg_probe':[UP,SZ],'fg_layout':[LP,SZ],
   'fg_boys':[SZ,LP,SZ,LP,SZ],
   'fg_even':[SZ,ctypes.c_int,LP,SZ,DP,SZ,LP,SZ,LP,SZ,LP,SZ],
   'fg_odd':[SZ,LP,SZ,DP,SZ,LP,SZ,LP,SZ]}
  for name,args in sig.items():
   f=getattr(self.newlib,name);f.argtypes=args;f.restype=ctypes.c_int
  self.new_abi()
  layout=np.empty(2,CD);checked(self.newlib.fg_layout(ptr(layout),4))
  if not np.array_equal(layout,np.array([1.25-2.5j,-3.75+4.5j],CD)):
   raise RuntimeError('new native complex layout mismatch')
  self.identity.update({'analytic_build_key':self.newfolder.name,
   'analytic_adapter_sha256':ns.sha(__file__),'analytic_builder_sha256':ns.sha(build_native.__file__)})

 def new_abi(self):
  self._check_abi();p=np.zeros(10,np.uint64);checked(self.newlib.fg_probe(ptr(p,UP),10))
  if p.tolist()!=self.abi:raise RuntimeError('new native ABI or rounding mismatch')

 def boys(self,x):
  self.new_abi();x=_array(x,CD,name='Boys argument');shape=x.shape
  out=np.empty((x.size,10),CD)
  checked(self.newlib.fg_boys(x.size,ptr(x),2*x.size,ptr(out),2*out.size))
  return out.reshape(shape+(10,))

 def even_packed(self,g,weights,which):
  self.new_abi();which=insertion(which)
  g=_array(g,CD,name='even geometry');w=_array(weights,np.float64,name='even weights')
  if g.ndim<2 or g.shape[0]!=13 or w.shape!=(5,)+g.shape[1:]:raise ValueError('geometry[13,...],weights[5,...] required')
  n=g[0].size;raw=np.empty((n,5,2,3),CD);out=np.empty((6,2,3),CD);sa=np.empty((6,2,3),LD)
  checked(self.newlib.fg_even(n,which,ptr(g),2*g.size,ptr(w,DP),w.size,ptr(raw),2*raw.size,ptr(out),2*out.size,ptr(sa),sa.size))
  return {'total':out[5],'sumabs':sa[5],'per_sector':out[:5],'per_sector_sumabs':sa[:5],
   'raw_fields':raw.reshape(g.shape[1:]+(5,2,3)),'powers':(0,2,4,6,8)}

 def even_geometry(self,a,b,t1,t2,z,q2,which):
  self.new_abi();which=insertion(which)
  a=_real_scalar(a,'a');b=_real_scalar(b,'b');z=_real_scalar(z,'z');q2=_real_scalar(q2,'q2')
  if np.iscomplexobj(t1) or np.iscomplexobj(t2):raise TypeError('Laplace nodes must be real')
  C=np.array([-2,0,-z],LD)
  geo=ek.geometry(a,b,t1,t2,[0,0,0],C,0,q2)
  A,B,m1,m2,n1,n2,d,v,s,base=geo;mean=m1 if which==1 else m2
  R=mean-C.reshape((3,)+(1,)*(mean.ndim-1))
  packed=np.stack([A,B,base,n1[0],n1[2],n2[0],n2[2],*d,*R]).astype(CD)
  return geo,packed

 def even_foreign(self,a,b,t1,t2,z,q2,which,W):
  geo,packed=self.even_geometry(a,b,t1,t2,z,q2,which)
  W=_array(W,np.float64,name='full weights',shape=(9,)+geo[8].shape)
  return self.even_packed(packed,np.ascontiguousarray(W[::2]),which)

 def p0_foreign(self,a,b,t1,t2,z,q2,which,W0):
  geo,packed=self.even_geometry(a,b,t1,t2,z,q2,which)
  W0=_array(W0,np.float64,name='p0 weights',shape=geo[8].shape)
  weights=np.zeros((5,)+W0.shape,np.float64);weights[0]=W0
  # Explicit sector selection; other donor sectors must be retained by full assembly.
  return self.even_packed(packed,weights,which)

 def odd_plane(self,a,b,t1,t2,z,q2,gamma,which,W):
  self.new_abi();which=insertion(which);gamma=_real_scalar(gamma,'gamma')
  a=_real_scalar(a,'a');b=_real_scalar(b,'b');z=_real_scalar(z,'z');q2=_real_scalar(q2,'q2')
  if gamma<0:raise ValueError('gamma must be nonnegative')
  if np.iscomplexobj(t1) or np.iscomplexobj(t2):raise TypeError('Laplace nodes must be real')
  C=np.array([-2,0,-z],LD);extra=gamma*gamma
  geo=ek.geometry(a,b,t1,t2,[0,0,0],C,0,q2,extra1=extra if which==1 else 0,extra2=extra if which==2 else 0,foreign=C)
  A,B,m1,m2,n1,n2,d,v,s,base=geo
  packed=_array(np.stack([A,B,v,s,base,*m1,*m2,*n1,*n2,*d]),CD,name='odd geometry')
  W=_array(W,np.float64,name='full weights',shape=(9,)+s.shape)
  ww=np.ascontiguousarray(W[1::2]);out=np.empty((2,3),CD);sa=np.empty((2,3),LD)
  checked(self.newlib.fg_odd(s.size,ptr(packed),2*packed.size,ptr(ww,DP),ww.size,ptr(out),2*out.size,ptr(sa),sa.size))
  x=s/(2*v)
  return out,sa,{'min_real':float(x.real.min()),'max_real':float(x.real.max()),'max_abs_imag':float(abs(x.imag).max())}
