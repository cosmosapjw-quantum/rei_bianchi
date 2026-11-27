"""Long-wave separated longitudinal electron/proton RPA DSF.
Resolve ion feature by quadrature, narrow Langmuir pole by residue.
"""
import numpy as np,json
from scipy.special import wofz,logsumexp
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.constants import m_e,m_p
from pathlib import Path
D=Path(__file__).resolve().parent;delta=m_e/m_p
def H(z):return 1+1j*np.sqrt(np.pi/2)*z*wofz(z/np.sqrt(2))
def low(z,K):
 he=H(z);hi=H(z/np.sqrt(delta));den=K*K+he+hi
 se=np.exp(-z*z/2)/np.sqrt(2*np.pi);si=np.exp(-z*z/(2*delta))/np.sqrt(2*np.pi*delta)
 return abs((K*K+hi)/den)**2*se+abs(he/den)**2*si
def chi_real(O,K,mass):
 z=O/(K*np.sqrt(mass))
 if z<10:return H(z).real/K**2
 # high-frequency asymptotic, avoid cancellation in 1+zZ
 v=(K*np.sqrt(mass)/O)**2
 return -sum(float(np.prod(np.arange(1,2*j,2)))*v**j for j in range(1,9))/K**2
def chi_derivative(O,K,mass):
 z=O/(K*np.sqrt(mass))
 if z<10:
  h=H(z);return ((h-1)/z-z*h).real/(K**3*np.sqrt(mass))
 v=(K*np.sqrt(mass)/O)**2
 return sum(2*j*float(np.prod(np.arange(1,2*j,2)))*v**j for j in range(1,9))/(K*K*O)
def pole(K):
 def eps(O):return 1+chi_real(O,K,1.)+chi_real(O,K,delta)
 O=brentq(eps,.8,2.,xtol=1e-14)
 xe=chi_real(O,K,1.);xi=chi_real(O,K,delta);ep=chi_derivative(O,K,1.)+chi_derivative(O,K,delta)
 weight=-2*K*K*xe*(1+xi)/(O*ep)
 z=np.array([O/K,O/(K*np.sqrt(delta))])
 loggamma=logsumexp(.5*np.log(np.pi/2)+np.log(z)-z*z/2-2*np.log(K))-np.log(ep)
 return O,weight,weight*(O/K)**2,float(loggamma/np.log(10))
def run():
 rows=[]
 for K in [.15,.1,.05,.01,1e-3,4e-5,6.35e-5]:
  # separate ion feature and distant Langmuir pole; cutoff at halfway to pole
  O,w,m2,l=pole(K);hi=O*0.75/K;bounds=sorted(set([0,.005,.02,.05,.1,.2,.5,1,2,3,5,8,min(12,hi),hi]));bounds=[v for v in bounds if v<=hi]
  integ=lambda n:2*sum(quad(lambda z:z**n*low(z,K),a,b,epsabs=1e-12,epsrel=1e-10,limit=300)[0] for a,b in zip(bounds[:-1],bounds[1:]))
  s0,s2=integ(0),integ(2);exact=(K*K+1)/(K*K+2)
  rows.append(dict(K=K,omega_over_wp=O,low_static=s0,pole_static=w,static_total=s0+w,static_exact=exact,static_residual=s0+w-exact,low_second=s2,pole_second=m2,second_residual=s2+m2-1,log10_damping_over_wp=l))
  rows[-1]['pass']=bool(abs(s0+w-exact)<2e-5 and abs(s2+m2-1)<1e-3)
  if K<=.1:assert rows[-1]['pass'],(K,rows[-1])
 out=dict(rows=rows,asymptotic_pole_weight_per_K2=1/(1+delta)**2,asymptotic_low_second=delta/(1+delta),asymptotic_high_second=1/(1+delta),scope='collisionless equal-T classical longitudinal RPA; isolated narrow plasmon pole approximation, actual small K regime checked via residue, no transverse photon scattering vertex')
 (D/'RPA_SPLIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
