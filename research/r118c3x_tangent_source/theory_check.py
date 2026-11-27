import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent;OL=.684908
def rhs(y,r,p,pi):
 s=y[:5];h=np.exp(y[5]);q=s@s/3+(r+p-2*OL)/(2*h*h)
 return np.r_[(q-2)*s+3*pi/h**2,-(1+q)]
def tangent(y,r,p,pi,dy,dr,dp,dpi):
 s=y[:5];h=np.exp(y[5]);v=dy[:5];l=dy[5];q=s@s/3+(r+p-2*OL)/(2*h*h)
 dq=2*s@v/3+(dr+dp)/(2*h*h)-(r+p-2*OL)*l/h**2
 return np.r_[(q-2)*v+dq*s+3*(dpi-2*pi*l)/h**2,-dq]
def run():
 rng=np.random.default_rng(19);err=[]
 for _ in range(100):
  y=np.r_[rng.normal(size=5)*.01,np.log(54.)];r,p=2900.,10.;pi=rng.normal(size=5)*.1;v=rng.normal(size=6)*.1;dr,dp=10.,2.;dpi=rng.normal(size=5)
  ex=tangent(y,r,p,pi,v,dr,dp,dpi)
  e=1e-5;fd=(rhs(y+e*v,r+e*dr,p+e*dp,pi+e*dpi)-rhs(y-e*v,r-e*dr,p-e*dp,pi-e*dpi))/(2*e)
  err.append(float(np.linalg.norm(fd-ex)/np.linalg.norm(ex)))
 assert max(err)<1e-7
 out=dict(max_tangent_relative=max(err),scope='direct differentiation of Bianchi I native normalized geometry RHS; conditional prescribed matter, not full feedback')
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
