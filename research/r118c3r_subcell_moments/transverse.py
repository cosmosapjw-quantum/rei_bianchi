"""Conditional transverse-mode kinematics and weak-coupling collisional scales.
No scattering amplitude inferred from longitudinal DSF alone.
"""
import numpy as np,json
from pathlib import Path
from scipy.constants import c,k,e,m_e,m_p,epsilon_0,hbar,pi
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
def run():
 v=np.genfromtxt(D.parent/'r118c3i_event_ledger/native/history.csv',names=True,delimiter=',');ne=v['ne']*1e6;T=v['T'];wp=np.sqrt(ne*e*e/(epsilon_0*m_e));ve=np.sqrt(k*T/m_e);ld=ve/wp;ldtot=ld/np.sqrt(2)
 b90=e*e/(4*pi*epsilon_0*k*T);bq=hbar/np.sqrt(m_e*k*T);log=np.log(ldtot/np.maximum(b90,bq))
 nu=4*np.sqrt(2*pi)*ne*e**4*log/(3*(4*pi*epsilon_0)**2*np.sqrt(m_e)*(k*T)**1.5)
 delta=m_e/m_p;omL=np.sqrt(1+delta);mu,w=leggauss(64);wt=3/8*w*(1+mu*mu)
 rows=[]
 for om in [1.000001,1.01,1.1,1.5,1.99,2.0002,2.001,2.1,3.,10.]:
  ki=np.sqrt(om*om-1);r=[]
  for sign in [-1,1]:
   # Fixed zero-k plasma pole. Actual small K dispersive root differs O(K²).
   out=om+sign*omL
   if out<=1:r.append(dict(branch='emission' if sign<0 else 'absorption',allowed=False));continue
   ko=np.sqrt(out*out-1);Q=np.sqrt(ki*ki+ko*ko-2*ki*ko*mu)
   K=Q[None,:]*ve[:,None]/c
   W=K*K/(1+delta)**2
   # Phase-space factor for outgoing mode at fixed omega, not full cross-section.
   # k²/(domega/dk)=k*omega/c², normalized to omega_i²/c³.
   ps=ko*out/(om*om);weight=W@wt
   r.append(dict(branch='emission' if sign<0 else 'absorption',allowed=True,out_omega_over_wp=float(out),Q_c_over_wp_range=[float(min(Q)),float(max(Q))],K_range=[float(K.min()),float(K.max())],phase_space_relative=float(ps),angular_pole_static_range=[float(weight.min()),float(weight.max())]))
  rows.append(dict(omega_over_wp=om,branches=r))
 # Free thermal ion width Q v_i and physical collisional damping compare.
 q=wp/c;ionwidth=q*np.sqrt(k*T/m_p)
 o=dict(rows=rows,threshold=float(1+omL),coulomb_log_range=[float(log.min()),float(log.max())],nu_ei_s_inv=[float(nu.min()),float(nu.max())],nu_ei_over_wp=[float(min(nu/wp)),float(max(nu/wp))],nu_ei_over_ion_width_q_wp_c=[float(min(nu/ionwidth)),float(max(nu/ionwidth))],plasma_parameter_range=[float(min(ne*ldtot**3)),float(max(ne*ldtot**3))],scope='cold transverse branch and fixed long-wave Langmuir pole kinematics; conditional outgoing phase space not scattering rate, Coulomb weak-coupling Maxwellian estimate; damping eigenvalue not simply nu_ei')
 assert log.min()>1 and np.min(nu)>0
 (D/'TRANSVERSE.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
