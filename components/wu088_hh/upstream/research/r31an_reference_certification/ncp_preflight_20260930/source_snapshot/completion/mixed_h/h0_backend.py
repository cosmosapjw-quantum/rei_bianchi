"""Fused weighted radial-moment candidate, explicit diagnostic upper envelopes."""
import ctypes,subprocess,json,hashlib,os,fcntl
import numpy as np
from native import Native,HERE,ROOT,sha,DP,LP,LD,CD,inputs
class H0Fused:
 def __init__(self):
  sources=[HERE/'h0_fused.cpp',ROOT/'completion/radial/radial_wide.cpp'];self.identity={str(p.relative_to(ROOT)):sha(p)for p in sources};self.identity['adapter_sha256']=sha(__file__);key=hashlib.sha256(json.dumps(self.identity,sort_keys=True).encode()).hexdigest();folder=HERE/'build'/key;folder.mkdir(parents=True,exist_ok=True);lib=folder/'h0.so';manifest=folder/'BUILD.json'
  with(folder/'BUILD.lock').open('a')as lock:
   fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
   if manifest.exists():
    old=json.loads(manifest.read_text())
    if old['identity']!=self.identity or old['binary_sha256']!=sha(lib):raise RuntimeError('h0 cache mismatch')
   else:
    command=['g++','-O3','-std=c++17','-fPIC','-shared','-fno-fast-math','-ffp-contract=off',str(HERE/'h0_fused.cpp'),'-o',str(lib.with_suffix('.tmp.so'))];p=subprocess.run(command,capture_output=True,text=True);(folder/'compile.stderr').write_text(p.stderr);(folder/'compile.stdout').write_text(p.stdout)
    if p.returncode:raise RuntimeError(p.stderr)
    os.replace(lib.with_suffix('.tmp.so'),lib);tmp=folder/'BUILD.tmp.json';tmp.write_text(json.dumps({'identity':self.identity,'command':command,'binary_sha256':sha(lib)},indent=2));os.replace(tmp,manifest)
  self.lib=ctypes.CDLL(str(lib));self.lib.mh_h0.argtypes=[ctypes.c_size_t,DP,DP,DP,DP,LP,LP];self.lib.mh_h0.restype=ctypes.c_int;self.lib.precision_bits.restype=ctypes.c_int
  if self.lib.precision_bits()!=np.finfo(LD).nmant+1:raise RuntimeError('h0 precision mismatch')
  self.identity['binary_sha256']=sha(lib)
 def h0(self,a,b,t,W,z,q,active,sign=1,inverted=False):
  for value in(a,b,z,q):
   if np.iscomplexobj(value)or np.asarray(value).shape!=()or not np.isfinite(value):raise ValueError('finite scalar')
  d=inputs()
  if a not in d['exponents']or b not in d['exponents']or q!=float(d['v'])or abs(z)>64:raise ValueError('frozen target domain')
  if isinstance(active,(bool,np.bool_))or active not in(0,1)or sign not in(-1,1)or not isinstance(inverted,(bool,np.bool_)):raise ValueError('labels')
  t=np.asarray(t);W=np.asarray(W)
  if t.dtype!=np.dtype(np.float64)or t.ndim!=1 or not 0<t.size<=192 or not np.isfinite(t).all()or np.any(t<=0)or W.dtype!=np.dtype(np.float64)or W.shape!=(3,9,t.size,t.size)or not np.isfinite(W).all():raise ValueError('node/weight tensor')
  t=np.require(t,requirements=['C','A']);W=np.require(W,requirements=['C','A']);pars=np.array([a,b,z,q,active,sign,int(inverted)],float);norm=np.sqrt(2)*float(d['pref'])*(2*a/np.pi)**.75*(2*b/np.pi)**.75*np.array([1,2*np.sqrt(a),2*np.sqrt(a)],float);out=np.empty((7,3),CD);sa=np.empty((7,3),LD)
  status=self.lib.mh_h0(t.size,t.ctypes.data_as(DP),W.ctypes.data_as(DP),pars.ctypes.data_as(DP),norm.ctypes.data_as(DP),out.ctypes.data_as(LP),sa.ctypes.data_as(LP))
  if status:raise RuntimeError('h0 status '+str(status))
  if not np.isfinite(out).all()or not np.isfinite(sa).all():raise FloatingPointError('nonfinite h0')
  return out,sa
