from pathlib import Path
import sys,json,ctypes
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path[:0]=[str(HERE),str(ROOT/'exact_weights/deps')]
import numpy as np
from guarded_foreign import AnalyticForeign,CD,LD,ptr,DP

def main():
 h=AnalyticForeign(HERE/'cache');checks=[]
 def rejects(name,fun):
  try:fun()
  except (ValueError,TypeError,RuntimeError,FloatingPointError):checks.append({'name':name,'PASS':True});return
  checks.append({'name':name,'PASS':False})
 _,g=h.even_geometry(.7,1.1,np.array([.1]),np.array([.2]),0.,.45,1)
 w=np.ones((5,1),np.float64)
 rejects('wrong_geometry_dtype',lambda:h.even_packed(g.astype(np.complex128),w,1))
 rejects('wrong_weights_shape',lambda:h.even_packed(g,w[:4],1))
 rejects('boolean_insertion',lambda:h.even_packed(g,w,True))
 rejects('nonfinite_geometry',lambda:h.even_packed(g*np.nan,w,1))
 rejects('Boys_domain_Re',lambda:h.boys(np.array([-33],CD)))
 rejects('Boys_domain_Im',lambda:h.boys(np.array([3j],CD)))
 # Noncontiguous inputs are copied into aligned arrays by supported Python API.
 gg=np.stack([g[:,0],g[:,0]],axis=1);wg=np.ones((5,2),np.float64)
 sliced=h.even_packed(gg[:,::2],wg[:,::2],1);contig=h.even_packed(g,w,1)
 checks.append({'name':'noncontiguous_copy_semantics','PASS':bool(np.array_equal(sliced['total'],contig['total']))})
 raw=np.full((1,5,2,3),CD(123+4j),CD);out=np.full((6,2,3),CD(123+4j),CD);sa=np.full((6,2,3),LD(123),LD)
 for name,n,ng in [('native_truncated',1,24),('native_overflow',2**63,26)]:
  status=h.newlib.fg_even(n,1,ptr(g),ng,ptr(w,DP),w.size,ptr(raw),raw.size*2,ptr(out),out.size*2,ptr(sa),sa.size)
  checks.append({'name':name,'status':status,'PASS':status==-202 and bool(np.all(raw==123+4j)and np.all(out==123+4j)and np.all(sa==123))})
 g0=g.copy();g0[0]=0
 status=h.newlib.fg_even(1,1,ptr(g0),26,ptr(w,DP),5,ptr(raw),60,ptr(out),72,ptr(sa),36)
 checks.append({'name':'native_invalid_precision_atomic','status':status,'PASS':status==-206 and bool(np.all(out==123+4j))})
 libc=ctypes.CDLL(None);libc.fegetround.restype=ctypes.c_int;libc.fesetround.argtypes=[ctypes.c_int];mode=libc.fegetround()
 try:
  if libc.fesetround(0x400)!=0:raise RuntimeError('cannot set rounding control')
  rejects('unsupported_rounding',lambda:h.boys(np.array([0],CD)))
 finally:libc.fesetround(mode)
 # Negative halfplane odd fallback, unlike the actualia3ib8 sample.
 t=np.array([.1,.2]);W=np.zeros((9,2,2),np.float64);W[1::2]=1
 for side in [1,2]:
  got,sa,domain=h.odd_plane(.7,1.1,t[:,None],t[None,:],0.,8.,0.,side,W)
  ref,rsa,_=h.foreign_plane(.7,1.1,t[:,None],t[None,:],0.,8.,0.,side,W)
  den=np.finfo(LD).eps*rsa;gap=abs(got-ref);ratio=float(np.max(gap/den))
  checks.append({'name':'negative_odd_bridge_side'+str(side),'domain':domain,'max_eps_sumabs':ratio,'PASS':bool(np.all(gap<=128*den))})
 # Explicit p0 supported API, same source as sector0; normalization is caller-owned.
 W=np.ones((9,1),np.float64);args=(.7,1.1,np.array([.1]),np.array([.2]),0.,.45,1)
 e=h.even_foreign(*args,W);p=h.p0_foreign(*args,W[0])
 checks.append({'name':'guarded_p0_equals_sector0','PASS':bool(np.array_equal(p['total'],e['per_sector'][0]))})
 result={'status':'PASS'if all(x['PASS']for x in checks)else'FAIL','checks':checks,'count':len(checks),'identity':h.identity}
 p=HERE/'GUARD_RESULTS.json'
 if p.exists():raise FileExistsError(p)
 p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 if result['status']=='FAIL':raise SystemExit(1)
if __name__=='__main__':main()
