"""Conditional quasistatic momentum-relaxation FDT; actual thermal scale, H-only ion diagnostic."""
import numpy as np,json
from scipy.constants import k,m_e,e,epsilon_0,hbar,c
from scipy.integrate import quad
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 h=np.genfromtxt(D.parent/'r118c3u_positive_owner/birth_1024_32ray/history.csv',names=True,delimiter=',')
 # Electron density column is native cm^-3. Singly charged ion surrogate ni=ne.
 T=h['T'];ne=h['ne']*1e6;assert np.min(ne)>0
 v=np.sqrt(k*T/m_e);wp=np.sqrt(ne*e**2/(epsilon_0*m_e))
 lam=v/wp;bcl=e**2/(4*np.pi*epsilon_0*k*T);bq=hbar/(m_e*v);ln=np.log(lam/np.maximum(bcl,bq))
 nu=4*np.sqrt(2*np.pi)/3*ne*e**4*ln/((4*np.pi*epsilon_0)**2*np.sqrt(m_e)*(k*T)**1.5)
 assert np.min(ln)>1
 rows=[]
 for i in [0,len(T)//2,len(T)-1]:
  for Q in [1e-8,1e-6,1e-4,.01,1]:
   L=1+1/Q**2;gamma=nu[i]/L;K=Q*wp[i]/c
   # For collisional fluid closure use small Knudsen and quasistatic rate ratio.
   kn=K*v[i]/nu[i];qs=gamma/(c*K)
   # Quantile half width is gamma; fraction inside omega_c equals 2/pi atan(omega_c/gamma).
   z=quad(lambda y:1/(np.pi*(1+y*y))/L,-np.inf,np.inf,epsabs=1e-14)[0]
   rows.append(dict(T=float(T[i]),ne_m3=float(ne[i]),wp_s=float(wp[i]),nu_ei_s=float(nu[i]),lnLambda=float(ln[i]),Qc_over_wp=Q,Knudsen=float(kn),quasistatic_ratio=float(qs),linewidth_s=float(gamma),normalized_variance=float(z),fluid_admissible=bool(kn<.1 and qs<.1)))
 o=dict(rows=rows,beta_range=[float(min(v/c)),float(max(v/c))],scope='conditional classical weakly coupled singly charged ion surrogate; quasistatic electromagnetic inertial loading, Markovian collisional OU model. No exact ion dynamics, collisionless kinetic limit or full scattering rate.')
 (D/'COLLISIONAL_DSF.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
