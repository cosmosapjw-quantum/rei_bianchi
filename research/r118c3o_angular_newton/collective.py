"""One-component classical Debye screening diagnostic and free Maxwell structure factor."""
import sys,numpy as np,json
from scipy.constants import c,k,m_e,epsilon_0,e,hbar
from numpy.polynomial.legendre import leggauss
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 a=np.genfromtxt(D.parent/'r118c3i_event_ledger/native/history.csv',names=True,delimiter=',');ne=a['ne']*1e6;T=a['T'];wp=np.sqrt(ne*e*e/(epsilon_0*m_e));lam=np.sqrt(epsilon_0*k*T/(ne*e*e));v=np.sqrt(k*T/m_e)
 mu,w=leggauss(96);wt=3/8*w*(1+mu*mu)
 rows=[]
 for x in [.001,.01,.1,1.,10.,100.,1e3,1e4]:
  wave=x*wp/c;transfer=wave[:,None]*np.sqrt(2*(1-mu))[None,:];t=transfer*lam[:,None]
  S=t*t/(1+t*t);supp=S@wt
  rows.append(dict(kc_over_wp=x,klambdaD_range=[float(min(wave*lam)),float(max(wave*lam))],static_angular_screening_range=[float(min(supp)),float(max(supp))],vth_over_vg_range=[float(min(v/c*np.hypot(x,1)/x)),float(max(v/c*np.hypot(x,1)/x))]))
 # Dimensionless free-particle S0 with recoil; test exact KMS ratio and f-sum.
 z,w=leggauss(128);z=z*10;w=w*10;rr=[]
 for eta in [.0001,.01,.1,1.]:
  # frequency / (k vth); recoil / width = eta/2, eta = hbar k/(m vth)
  r=eta/2;sf=np.exp(-.5*(z-r)**2)/np.sqrt(2*np.pi);sm=np.exp(-.5*(-z-r)**2)/np.sqrt(2*np.pi)
  err=float(max(abs(np.log(sm/sf)+eta*z)))
  rr.append(dict(eta=eta,normalization=float(w@sf),f_sum_over_recoil=float((w@(z*sf))/r),kms_error=err))
 assert max(abs(v['normalization']-1) for v in rr)<1e-12 and max(v['kms_error'] for v in rr)<1e-12
 o=dict(rows=rows,free_structure=rr,debye_m_range=[float(min(lam)),float(max(lam))],omega_p_s_inv_range=[float(min(wp)),float(max(wp))],scope='static electron one-component Debye-Huckel with rigid neutralizer; free Maxwell dynamic structure factor checks, NOT collective photon scattering kernel or total ion-electron DSF')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
