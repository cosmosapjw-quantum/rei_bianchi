"""Conditional dispersive Bose redistribution with exact pairwise implicit transfer."""
import numpy as np,json
from pathlib import Path
from scipy.optimize import brentq
D=Path(__file__).resolve().parent
def pair(Ni,Nj,ci,cj,q,dt):
 # Lower-energy i. Equilibrium flux zero when f_j/(1+f_j)=q f_i/(1+f_i).
 # Backward Euler scalar root on physical bounded transfer.
 def flux(d):
  a=(Ni+d)/ci;b=(Nj-d)/cj
  return b-q*a+(1-q)*a*b
 scale=max(Ni,Nj,1e-300)
 root=brentq(lambda t:t-dt*flux(t*scale)/scale,-Ni/scale,Nj/scale,xtol=5e-15,rtol=1e-14)*scale
 return root
def run():
 # Near-gap regime: scale energies by plasma gap rather than tiny absolute x;
 # select beta*gap=0.3 to stress detailed balance, not actual cosmological T.
 rows=[]
 for gap in [0.,.3,1.]:
  for n in [32,64,128]:
   edge=np.geomspace(.01,5.,n+1);x=np.sqrt(edge[:-1]*edge[1:]);c=np.diff(edge**3)/3
   E=np.hypot(x,gap);q=np.exp(-np.diff(E));mu=-.2
   eq=c/np.expm1(E-mu)
   f=eq/c;J=f[1:]-q*f[:-1]+(1-q)*f[:-1]*f[1:]
   # Perturbed positive spectrum, common conditional conductance dt per pair.
   N=eq*(1+.1*np.sin(3*x));N0=N.copy();Q=0.
   def H(N):
    f=N/c
    return np.sum(c*(f*np.log(f)-(1+f)*np.log1p(f))+E*N)
   H0=H(N)
   for _ in range(16):
    for i in range(n-1):
     d=pair(N[i],N[i+1],c[i],c[i+1],q[i],.005*min(c[i],c[i+1]))
     N[i]+=d;N[i+1]-=d;Q-=np.diff(E)[i]*d
   r=dict(gap=gap,n=n,eq_flux=float(max(abs(J))),number_rel=float(abs(N.sum()-N0.sum())/N0.sum()),energy_res=float(abs(E@(N-N0)-Q)),free_energy_change=float(H(N)-H0),min_stock=float(N.min()))
   assert r['number_rel']<1e-13 and r['energy_res']<1e-12 and r['free_energy_change']<=1e-13 and r['min_stock']>=0
   rows.append(r)
 (D/'R7.json').write_text(json.dumps(dict(rows=rows,scope='conditional reversible Bose pair kernel; dimensionless gap/T deliberately order unity stress test; not physical dispersive Compton conductance'),indent=2)+'\n')
 print(rows,flush=True)
if __name__=='__main__':run()
