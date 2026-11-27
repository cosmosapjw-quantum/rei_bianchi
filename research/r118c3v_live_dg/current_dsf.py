"""Conditional free Maxwell transverse current plus electromagnetic dressing.
Stationary unmagnetized classical electrons, immobile neutralizing background.
Not an interacting density DSF or full scattering rate.
"""
import numpy as np,json
from pathlib import Path
from scipy.special import wofz
from scipy.integrate import quad
from scipy.constants import k,m_e,c
D=Path(__file__).resolve().parent
def run():
 h=np.genfromtxt(D.parent/'r118c3u_positive_owner/birth_1024_32ray/history.csv',names=True,delimiter=',')
 beta=np.sqrt(k*h['T']/(m_e*c*c));rows=[]
 # xi=omega/(Q vth), Q=ck/wp. epsilon_T=1+Z/(sqrt2 beta Q Omega)
 # use stable Omega² epsilon_T=Omega²+Omega Z/(sqrt2 beta Q).
 for v in [float(min(beta)),float(max(beta))]:
  for Q in [1e-5,1e-4,1e-3,.01,.1,1.,10.]:
   def coeff(x):
    Om=Q*v*x;Z=1j*np.sqrt(np.pi)*wofz(x/np.sqrt(2))
    a=Q*Q-Om*Om;den=a-Om*Z/(np.sqrt(2)*v*Q)
    # j_total / j_free and canonical vorticity amplitude (in wp/c units).
    return a/den,Q*(1+a)/den
   def g(x):return np.exp(-x*x/2)/np.sqrt(2*np.pi)
   # integrate narrow magnetostatic peak separately; width~Q² in xi.
   ed=np.unique(np.r_[0.,min(Q*Q,1.),min(10*Q*Q,2.),min(100*Q*Q,3.),1.,3.,8.])
   j=C=0.;err=0.
   for a,b in zip(ed[:-1],ed[1:]):
    v0,e0=quad(lambda x:2*g(x)*abs(coeff(x)[0])**2,a,b,epsabs=1e-13,epsrel=1e-7,limit=200)
    v1,e1=quad(lambda x:2*g(x)*abs(coeff(x)[1])**2,a,b,epsabs=1e-11,epsrel=1e-7,limit=200)
    j+=v0;C+=v1;err+=e1
   static=coeff(0)
   # Cold fluid C term contributes current covariance beta² times spectrum.
   # Compare to *free* density variance, not longitudinal screened S_nn.
   rows.append(dict(beta=v,Qc_over_wp=Q,current_power_factor=j,vorticity_variance_over_free_density=v*v*C,static_vorticity_ratio=abs(static[1])*v,quad_err=err))
 o=dict(rows=rows,scope='collisionless electron-only Maxwellian transverse dielectric dressing of independent free-current noise. Longitudinal density-current correlation fixed by continuity and transverse correlation zero by symmetry. Current response conditional, no screened density comparison, no scattering rate or collisional width. Frequencies |omega|<=8Qvth.')
 (D/'CURRENT_DSF.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
