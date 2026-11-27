"""Exact old/new quadrature benchmark on actual C3U replay state and native coframe."""
import sys,json,numpy as np,ctypes,time,os
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.hermite import hermgauss
from scipy.constants import k,m_e,c
D=Path(__file__).resolve().parent;P=D.parent/'r118c3u_positive_owner';sys.path.insert(0,str(P))
from replay import Owner,ray,T
def lib(path):
 l=ctypes.CDLL(str(path));f=l.dg_rhs;p=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
 f.argtypes=[ctypes.c_int,ctypes.c_int]+[p]*7+[ctypes.c_double]*4+[ctypes.c_int,p,p,ctypes.c_int,p,p,p,p,p];f.restype=ctypes.c_int
 return f
def run():
 z=np.load(P/'replay_1024.npz');e0=z['edges'];N0=z['N'];V0=z['V'];d=z['d'];F=z['F'];n=z['n'];w0=z['w0'];h=np.genfromtxt(P/'birth_1024_32ray/history.csv',names=True,delimiter=',');x=np.genfromtxt(P/'birth_1024_32ray/spectrum.csv',names=True,delimiter=',')['x'];dl=np.log(x[1]/x[0]);lo=np.log(x[0])-dl/2;hi=np.log(x[-1])+dl/2
 d0,nlocal,w,_=ray(F,n,w0);assert np.max(abs(d-d0))<1e-14
 theta=k*h['T'][-1]/(m_e*c*c);tr=h['T'][-1]*h['a'][-1]/2.7255;c0=(e0[1:]+e0[:-1])/2;rows=[]
 for stride in [8,4]:
  e=e0[::stride];o=Owner(e,n,w0);cc=o.c;N=N0.reshape(len(n),-1,stride).sum(axis=2);V=(V0+N0*(c0-np.repeat(cc,stride))).reshape(len(n),-1,stride).sum(axis=2)
  A,B,mi=o.coefficients(N,V);assert mi>0
  for gh,gl in [(4,2),(8,4)]:
   zh,wh=hermgauss(gh);wh/=np.sqrt(np.pi);zl,wl=leggauss(gl);f=lambda x:np.ascontiguousarray(x,dtype=np.float64)
   res=[];tm=[];dg=[]
   for name in ['old','new']:
    fn=lib(D/(name+'.so'));a=np.zeros(N.shape);b=a.copy();diag=np.zeros(6);t=time.monotonic()
    rc=fn(len(d),len(e)-1,*[f(q) for q in [e,d,nlocal,w,w0,A,B]],lo,hi,theta,tr,gh,f(zh),f(wh),gl,f(zl),f(wl),a,b,diag);tm.append(time.monotonic()-t)
    assert rc==0 and max(diag[:2])<1e-10,(rc,diag)
    res.append((a,b));dg.append(diag.tolist())
   norm=lambda x:float(np.sum(abs(x)))
   rel=[norm(res[0][i]-res[1][i])/norm(res[0][i]) for i in range(2)]
   row=dict(cells=len(e)-1,rays=len(n),gh=gh,gl=gl,N_relative=rel[0],V_relative=rel[1],old_s=tm[0],new_s=tm[1],speedup=tm[0]/tm[1],old_diag=dg[0],new_diag=dg[1])
   print(row,flush=True);assert max(rel)<1e-8
   rows.append(row)
 (D/'KERNEL_BENCH.json').write_text(json.dumps(dict(rows=rows,scope='same quadrature and actual C3U terminal state; finite array equivalence and measured wall time on same CPU, not general performance'),indent=2)+'\n')
if __name__=='__main__':run()
