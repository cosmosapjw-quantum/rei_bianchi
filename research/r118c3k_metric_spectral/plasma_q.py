"""Fixed canonical momentum bins for cold-plasma transverse quasiparticles."""
import numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
# x=q c/(kB T0), gap g=a*hbar omega_p/(kB T0) = x_p
def energy(x,g,a):return np.hypot(x,g)/a
def step(x,N,a0,a1,g0,g1,n=16):
 # physical gap omega proportional to g/a; interpolate log a and log omega linearly.
 u=np.log(a1/a0);v=np.log((g1/a1)/(g0/a0));t,w=leggauss(n);t=(t+1)/2;w=w/2
 a=a0*np.exp(u*t);omega=g0/a0*np.exp(v*t)
 p=x[None,:]/a[:,None];mass=omega[:,None];E=np.hypot(p,mass)
 Wexp=u*np.sum(w*((p*p/E)@N));Wpl=-v*np.sum(w*((mass*mass/E)@N))
 du=N@(energy(x,g1,a1)-energy(x,g0,a0))
 # Numerical cancellation at high q handled using stable factored difference in later audit.
 return du,Wexp,Wpl
def run():
 import sys
 sys.path.insert(0,str(D.parent/'r118c3j_live_spectral'));from plasma import cutoff
 h=np.genfromtxt(D.parent/'r118c3i_event_ledger/native/history.csv',names=True,delimiter=',');a=h['a'];g=cutoff(h['ne'],2.7255/a)
 # finite quasiparticle number distribution localized near plasma scale, normalize sum to 1
 out=[]
 for n in [64,256,1024]:
  edges=np.geomspace(g.min()/100,g.max()*100,n+1);x=np.sqrt(edges[:-1]*edges[1:]);N=np.diff(edges**3)/3/np.expm1(np.hypot(x,g[0]));N/=N.sum()
  U0=N@energy(x,g[0],a[0]);wp=we=0.;maxrel=0.
  for k in range(1,len(a)):
   du,w,p=step(x,N,a[k-1],a[k],g[k-1],g[k]);we+=w;wp+=p;maxrel=max(maxrel,abs(du+w+p)/U0)
  U=N@energy(x,g[-1],a[-1]);out.append(dict(bins=n,number=float(N.sum()),initial_E_over_kBT0=float(U0),final_E_over_kBT0=float(U),expansion_work=float(we),plasma_work=float(wp),relative_residual=float((U-U0+we+wp)/U0),max_step_res=maxrel))
 o=dict(rows=out,gap_min=float(g.min()),gap_max=float(g.max()),scope='normalized hypothetical initial near-gap transverse quasiparticle ensemble; actual plasma/expansion clock; collisionless fixed q, plasma work reservoir, not absolute CMB correction')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
