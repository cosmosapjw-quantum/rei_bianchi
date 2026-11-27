"""32-ray native-state direct DG local collision; exact union of all mapped edges.
Compile C++ implementation separately. Compare nested conservative coarsening,
quadrature and physical full/two-half update; no live feedback.
"""
import numpy as np,json,ctypes,sys,time
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.hermite import hermgauss
from scipy.constants import k,m_e,c
from replay import Owner,ray,KT0,T
D=Path(__file__).resolve().parent
def library():
 lib=ctypes.CDLL(str(D/'dg_rhs.so'));p=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
 lib.dg_rhs.argtypes=[ctypes.c_int,ctypes.c_int]+[p]*7+[ctypes.c_double]*4+[ctypes.c_int,p,p,ctypes.c_int,p,p,p,p,p];lib.dg_rhs.restype=ctypes.c_int
 return lib.dg_rhs
def run(nmu=4):
 label='1024' if nmu==4 else f'1024_{2*nmu*nmu}ray'
 z=np.load(D/f'replay_{label}.npz');e0=z['edges'];N0=z['N'];V0=z['V'];d=z['d'];F=z['F'];n=z['n'];w0=z['w0'];h=np.genfromtxt(D/'birth_1024_32ray/history.csv',names=True,delimiter=',');x=np.genfromtxt(D/'birth_1024_32ray/spectrum.csv',names=True,delimiter=',')['x'];dl=np.log(x[1]/x[0]);lo=np.log(x[0])-dl/2;hi=np.log(x[-1])+dl/2
 d0,nlocal,w,_=ray(F,n,w0);assert np.max(abs(d-d0))<1e-14;theta=k*h['T'][-1]/(m_e*c*c);tr=h['T'][-1]*h['a'][-1]/2.7255;dt=T(h['max_depth'][-1]);fn=library();rows=[]
 c0=(e0[1:]+e0[:-1])/2
 def rhs(o,N,V,gh,gl):
  aa,bb,mi=o.coefficients(N,V);assert mi>0
  e=np.asarray(o.e,dtype=float);ng,wg=leggauss(gl);zh,wh=hermgauss(gh);wh/=np.sqrt(np.pi);a=np.zeros(N.shape);b=a.copy();diag=np.zeros(6)
  f=lambda x:np.ascontiguousarray(x,dtype=np.float64)
  t=time.monotonic();rc=fn(len(d),len(e)-1,*[f(q) for q in [e,d,nlocal,w,w0,aa,bb]],lo,hi,theta,tr,gh,f(zh),f(wh),gl,f(ng),f(wg),a,b,diag);assert rc==0 and max(diag[:2])<1e-10,(rc,diag)
  return a.astype(T),b.astype(T),dict(N_res=float(diag[0]),U_res=float(diag[1]),raw_energy=float(diag[2]),pair_abs=float(diag[3]),N_L1=float(diag[4]),V_L1=float(diag[5]),seconds=time.monotonic()-t)
 for stride in ([8,4] if nmu==4 else [8]):
  assert (len(e0)-1)%stride==0
  e=e0[::stride];o=Owner(e,n,w0);cc=o.c
  N=N0.reshape(len(n),-1,stride).sum(axis=2);V=(V0+N0*(c0-np.repeat(cc,stride))).reshape(len(n),-1,stride).sum(axis=2)
  mi=o.admit(N,V);assert abs(N.sum()-N0.sum())<1e-22
  a,b,q=rhs(o,N,V,4,2);A,B=N+dt*a/2,V+dt*b/2;mh=o.admit(A,B)
  a2,b2,q2=rhs(o,A,B,4,2);n1,v1=N+dt*a,V+dt*b;n2,v2=N+dt*(a+a2)/2,V+dt*(b+b2)/2
  m=min(o.admit(n1,v1),o.admit(n2,v2))
  af,bf,f=rhs(o,N,V,8,4)
  norm=lambda x:float(np.sum(abs(x)))
  # Global scalar mean projected to zero; direct independent array check.
  u=(bf+af*cc)*d[:,None];assert abs(af.sum())/norm(af)<1e-10 and abs(u.sum())/norm(u)<1e-10
  row=dict(cells=len(e)-1,stride=stride,initial_margin=mi,updated_margin=m,coarse=q,fine=f,quadrature_N=norm(af-a)/norm(af),quadrature_V=norm(bf-b)/norm(bf),fullhalf_N=norm(a2-a)/(2*norm(a)),fullhalf_V=norm(b2-b)/(2*norm(b)),Pi=float(np.linalg.norm(np.asarray((nlocal.T*np.sum(u,axis=1))@nlocal,dtype=float))),dtau=float(dt))
  np.savez_compressed(D/(f'collision_{len(e)-1}'+('' if nmu==4 else f'_{len(n)}ray')+'.npz'),edges=e,N=N,V=V,dN=a*dt,dV=b*dt,fine_dN=af*dt,fine_dV=bf*dt)
  rows.append(row);print(row,flush=True)
 (D/('COLLISION.json' if nmu==4 else f'COLLISION_{len(n)}ray.json')).write_text(json.dumps(dict(rows=rows,scope='actual 1024 native terminal source state, exact nested coarsening and direct canonical weak projection, indicated angular grid, physical local timestep; no live chemistry/geometry evolution'),indent=2)+'\n')
if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else 4)
