"""Classical RPA electron density spectrum for electron-only and H plasma.
Frequency z=omega/(k v_e), classical free spectra normalized to 1.
No transverse quasiparticle matrix element or near-gap pole calculation.
"""
import numpy as np,json
from scipy.special import wofz
from scipy.integrate import quad
from scipy.constants import m_e,m_p,k,c,epsilon_0,e,hbar
from pathlib import Path
D=Path(__file__).resolve().parent
def model(z,K,ion):
 ze=z/np.sqrt(2);zi=ze*np.sqrt(m_p/m_e)
 xe=(1+1j*np.sqrt(np.pi)*ze*wofz(ze))/K**2
 xi=(1+1j*np.sqrt(np.pi)*zi*wofz(zi))/K**2 if ion else 0.
 eps=1+xe+xi
 se=np.exp(-ze*ze)/np.sqrt(2*np.pi)
 si=np.sqrt(m_p/m_e)*np.exp(-zi*zi)/np.sqrt(2*np.pi)
 return abs((1+xi)/eps)**2*se+(abs(xe/eps)**2*si if ion else 0.)
def run():
 rows=[]
 for K in [.3,.5,1.,3.]:
  for ion in [False,True]:
   bounds=sorted(set([0,.005,.02,.05,.1,.2,.5,1,2,3,4,5,6,8,10,15,30]))
   s=2*sum(quad(lambda z:model(z,K,ion),a,b,epsabs=1e-12,epsrel=1e-9,limit=500)[0] for a,b in zip(bounds[:-1],bounds[1:]))
   m2=2*sum(quad(lambda z:z*z*model(z,K,ion),a,b,epsabs=1e-12,epsrel=1e-9,limit=500)[0] for a,b in zip(bounds[:-1],bounds[1:]))
   want=(K*K+1)/(K*K+2) if ion else K*K/(1+K*K)
   assert abs(s-want)<1e-7 and abs(m2-1)<1e-7,(K,ion,s,want,m2)
   low=2*quad(lambda z:model(z,K,ion),0,.15,epsabs=1e-12)[0]
   # semiclassical KMS multiplier on even classical spectrum; valid as
   # a detailed-balance model, not exact quantum RPA.
   z=np.linspace(.001,10,400);eta=.01;y=eta*z
   plus=y/(-np.expm1(-y));minus=y/np.expm1(y)
   db=float(np.max(abs(np.log(minus/plus)+y)))
   rows.append(dict(K=K,ion=ion,static=s,static_exact=want,second_moment=m2,low_frequency_fraction=low/s,kms_error=db))
 a=np.genfromtxt(D.parent/'r118c3i_event_ledger/native/history.csv',names=True,delimiter=',');theta=k*a['T']/(m_e*c*c);K=np.sqrt(theta)
 wp=np.sqrt(a['ne']*1e6*e*e/(epsilon_0*m_e));v=np.sqrt(k*a['T']/m_e);ld=v/wp
 # q=omega_p/c; for backscatter transfer <=2q, actual electron K small
 eta=hbar*(wp/c)/(m_e*v)
 o=dict(rows=rows,actual_K_q_eq_gap=[float(min(K)),float(max(K))],actual_recoil_eta=[float(min(eta)),float(max(eta))],debye_m=[float(min(ld)),float(max(ld))],scope='classical collisionless longitudinal RPA hydrogen, Te=Ti, rigid OCP comparison, finite K=.3..3 only; KMS multiplier is semiclassical ansatz; near-gap actual K not resolved; not transverse scattering rate')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
