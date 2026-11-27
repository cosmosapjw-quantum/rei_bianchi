"""Conditional finite-width dispersive density-only scattering accessibility.
Damped oscillator spectral FDT (classical) with quantum detailed-balance factor.
Numerical energy integral over allowed outgoing cold transverse states."""
import numpy as np,json
from scipy.integrate import quad
from scipy.constants import hbar,k,m_e,m_p,c
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 # Use actual C3R weak-coupling estimates; gamma=nu_ei/2 is a
 # chosen oscillator width, not a derived collision eigenmode.
 p=json.loads((D.parent/'r118c3r_subcell_moments/TRANSVERSE.json').read_text())
 h=np.genfromtxt(D.parent/'r118c3i_event_ledger/native/history.csv',names=True,delimiter=',')
 om=np.sqrt(1+m_e/m_p);gams=[p['nu_ei_over_wp'][0]/2,p['nu_ei_over_wp'][1]/2]
 # normalized classical even line shape, positive for both signs;
 # from Im chi(w)/w for oscillator with damping 2 gamma.
 def spec(z,g):return 2*g*om**2/(np.pi*((om*om-z*z)**2+4*g*g*z*z))
 rows=[]
 for gam in gams:
  # Transform around each pole via z=om+gam*tan(t) to resolve narrow peak.
  def integrate(f,l,r):
   l=max(l,0.);r=max(r,0.)
   if r<=l:return 0.
   a=np.arctan((l-om)/gam);b=np.arctan((r-om)/gam)
   return quad(lambda t:f(om+gam*np.tan(t))*2*om**2/(np.pi*((np.sin(t)*(2*om+gam*np.tan(t)))**2+4*(np.cos(t)*(om+gam*np.tan(t)))**2)),a,b,epsabs=1e-11,epsrel=1e-8,limit=250)[0]
  norm=2*integrate(lambda z:1.,0,1000.);assert abs(norm-1)<1e-5
  for x in [1.5,2.0002,1+om-10*gam,1+om,1+om+10*gam,2.001,2.1,3.]:
   phase=lambda out:out*np.sqrt(max(out*out-1,0.))/x**2
   emission=integrate(lambda z:phase(x-z),0,x-1)
   # Restrict absorption shifts to 5 omega_p, explicitly bounded
   # model; damped-oscillator tails outside are excluded from rates.
   absorption=integrate(lambda z:phase(x+z),0,5.)
   delta_em=.5*phase(x-om) if x-om>=1 else 0.
   delta_ab=.5*phase(x+om)
   rows.append(dict(gamma_over_wp=gam,x=float(x),classical_norm=norm,emission=emission,absorption=absorption,delta_emission=delta_em,delta_absorption=delta_ab))
 # detailed balance multiplier at actual plasma scales.
 beta=hbar*np.sqrt(h['ne']*1e6*1.602176634e-19**2/(8.8541878128e-12*m_e))/(k*h['T'])
 y=beta*om;db=float(np.max(abs(np.log((y/np.expm1(y))/(y/(-np.expm1(-y))))+y)))
 o=dict(rows=rows,actual_hbar_omega_over_kT=[float(min(beta)),float(max(beta))],kms_error=db,scope='density-only conditional oscillator DSF, chosen gamma=nu_ei/2, cold transverse final state DOS, finite outgoing absorption range; no actual vertex or rate; threshold broadening is model-dependent')
 (D/'FINITE_WIDTH.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
