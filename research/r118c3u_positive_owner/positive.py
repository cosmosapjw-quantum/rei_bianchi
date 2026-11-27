"""Positive exponential reconstruction and stable small signed corrections."""
import numpy as np,json
from scipy.special import logsumexp
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
from pathlib import Path
D=Path(__file__).resolve().parent;T=np.longdouble
class Cell:
 def __init__(self,edges,base,nq=24):
  self.e=np.asarray(edges,dtype=T);self.c=(self.e[1:]+self.e[:-1])/2;self.h=np.diff(self.e)/2
  z,w=leggauss(nq);self.z=z.astype(T);self.q=self.c[:,None]+self.h[:,None]*self.z
  self.base=base;B=np.asarray(base(self.q),dtype=T)*self.h[:,None]*w
  assert np.all(B>0)
  self.M0=B.sum(axis=1);self.M1=(B*self.z).sum(axis=1);self.M2=(B*self.z*self.z).sum(axis=1);self.B=B
 def solve(self,N,V):
  N=np.asarray(N,dtype=T);V=np.asarray(V,dtype=T);assert np.all(N>0) and np.all(abs(V)<N*self.h)
  # positive tilt of arbitrary base, normalized with shifted logarithm.
  b=[];a=[]
  for i,(v,n) in enumerate(zip(V,N)):
   target=float(v/(n*self.h[i]));log=np.log(self.B[i]).astype(float)
   def mean(t):
    y=log+t*self.z;y-=max(y);w=np.exp(y);return float(np.sum(w*self.z)/np.sum(w))
   lo,hi=-1.,1.
   while mean(lo)>target and abs(lo)<1e5:lo*=2
   while mean(hi)<target and hi<1e5:hi*=2
   if mean(lo)>target or mean(hi)<target:raise ValueError('quadrature realizability')
   v=brentq(lambda t:mean(t)-target,lo,hi,xtol=1e-13);b.append(v);q=np.log(self.B[i])+v*self.z;a.append(np.log(n)-np.max(q)-np.log(np.sum(np.exp(q-np.max(q)))))
  a,b=np.array(a,dtype=T),np.array(b,dtype=T)
  def fun(x):
   j=np.clip(np.searchsorted(self.e,x,side='right')-1,0,len(a)-1);return self.base(x)*np.exp(a[j]+b[j]*(x-self.c[j])/self.h[j])
  val=self.B*np.exp(a[:,None]+b[:,None]*self.z)
  err=max(np.max(abs(val.sum(axis=1)-N)/N),np.max(abs((val*self.z).sum(axis=1)-V/self.h)/N))
  return fun,float(err)
 def signed(self,dN,dV):
  # solve stable independent signed stock relative to positive base.
  det=self.M0*self.M2-self.M1**2;v=dV/self.h
  a=(self.M2*dN-self.M1*v)/det;b=(self.M0*v-self.M1*dN)/det
  margin=float(min(1+a-abs(b)))
  if margin<=0:raise ValueError('signed affine full positivity')
  def fun(x):
   j=np.clip(np.searchsorted(self.e,x,side='right')-1,0,len(a)-1);return self.base(x)*(a[j]+b[j]*(x-self.c[j])/self.h[j])
  return fun,margin
def test():
 # Very steep positive exponential reference, affine full density fails but
 # reference-weighted representation works. Test exact tilted moments.
 e=np.geomspace(.1,500,129,dtype=T);base=lambda x:x*x*np.exp(-x)
 c=Cell(e,base);N=c.M0.copy();V=c.h*c.M1;f,err=c.solve(N,V);assert err<1e-12
 dN=N*T('1e-14');dV=V*T('1e-14');f,mi=c.signed(dN,dV);assert mi>0
 try:c.signed(-2*N,-2*V)
 except ValueError:pass
 else:raise AssertionError('rollback')
 o=dict(max_exponential_error=err,min_multiplier=mi,affine_violations=int(np.sum(abs(V)>N*c.h/3)),scope='steep positive reference, independent signed moment solve, strict rejection for inadmissible perturbation')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':test()
