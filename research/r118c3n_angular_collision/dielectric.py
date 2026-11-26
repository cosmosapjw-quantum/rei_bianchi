"""Conditional dielectric mode normalization and independent test-particle diffusion."""
import sys,numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3j_live_spectral'))
from plasma import cutoff
from scipy.constants import c,k,m_e
def run():
 p=D.parent/'r118c3i_event_ledger/native/history.csv';r=np.genfromtxt(p,names=True,delimiter=',');xp=cutoff(r['ne'],2.7255/r['a'])
 theta=k*r['T']/(m_e*c*c);rate=r['ne']*1e6*6.6524587051e-29*c
 # x = physical momentum c / kBTgamma; E/kBTgamma=hypot(x,xp).
 rows=[]
 for ratio in [.001,.01,.1,1.,10.,100.]:
  x=ratio*xp;E=np.hypot(x,xp);v=x/E
  # Conditional independent-scatterer mode: rate ~ vg; diffusion in momentum.
  Dq=rate*theta*v*E**2
  rows.append(dict(q_over_gap=ratio,vg_over_c=float(v[0]),diffusion_over_vacuum=float((v*E**2/x**2)[0]),max_vth_over_vg=float(max(np.sqrt(theta)/v)),Dq_s_inv_range=[float(min(Dq)),float(max(Dq))],valid_thermal_separation=bool(max(np.sqrt(theta)/v)<.1)))
  assert np.all(Dq>0)
 # Direct classical energy density: electric+electron kinetic+magnetic.
 E=np.geomspace(1.000001,1e6,100);eps=1-E**-2;der=1+E**-2
 assert max(abs(eps+der-2))<1e-15
 o=dict(rows=rows,xp_range=[float(min(xp)),float(max(xp))],rate_s_inv=[float(min(rate)),float(max(rate))],scope='test scatterers dilute in prescribed cold dielectric, fixed omega vertex and small thermal Doppler transfer; not collective electron plasma or near-gap thermal theory')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
