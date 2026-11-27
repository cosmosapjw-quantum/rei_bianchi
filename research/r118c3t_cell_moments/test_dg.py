import json,numpy as np
from pathlib import Path
from dg import remap,project,centers,check_full,update
D=Path(__file__).resolve().parent
def run():
 rows=[]
 for n in [32,64,128,256]:
  e=np.linspace(1,3,n+1,dtype=np.longdouble);N,V=project(e,lambda x:np.sin(x)*.4+1)
  a,b=remap(e,N,V,e);err=max(np.max(abs(a-N)),np.max(abs(b-V)))
  assert err<1e-16
  # shifted interior with exactly common outer domain.
  d=e.copy();d[1:-1]+=np.diff(e)[0]*.37
  A,B=remap(e,N,V,d);n1,v1=remap(d,A,B,e)
  errn=float(np.linalg.norm(n1-N)/np.linalg.norm(N));errv=float(np.linalg.norm(v1-V)/np.linalg.norm(V))
  assert check_full(d,A,B)
  rows.append(dict(n=n,identity=float(err),roundtrip_N=errn,roundtrip_V=errv))
 # affine exactness independent of grid alignment
 e=np.linspace(1,3,65,dtype=np.longdouble);d=e.copy();d[1:-1]+=.23*(e[1]-e[0]);N,V=project(e,lambda x:1+2*x);A,B=remap(e,N,V,d);a,b=project(d,lambda x:1+2*x)
 assert max(np.max(abs(A-a)),np.max(abs(B-b)))<1e-15
 old=(N.copy(),V.copy());before=[a.copy() for a in old]
 try:update(e,old,(-2*N,np.zeros_like(V)),(np.zeros_like(N),np.zeros_like(V)))
 except ValueError:pass
 else:raise AssertionError('rollback failed')
 assert all(np.array_equal(a,b) for a,b in zip(old,before))
 o=dict(rows=rows,affine_exact=True,rollback=True,scope='manufactured affine and smooth density, exact overlap integrals in longdouble; shifted DG projection is not identity')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
