"""Sampled first-Born forcing envelope from compensated shape stock.
Bound ||STF P|| <= sqrt(2/3) sum |N| E. Use actual normalization,
sampled shear max for redshift bound, exact integrating factor from stored h.
This is NOT the full tangent response or a certified between-node bound.
"""
import numpy as np,json
from pathlib import Path
from scipy.constants import c,G,electron_volt
D=Path(__file__).resolve().parent;H0=2.1842852410855023e-18;KT0=8.617333262145e-5*2.7255
RHO0=3*c*c*H0*H0/(8*np.pi*G)
def table(p,k):
 f=p/(k+'.csv.gz')
 return np.genfromtxt(f if f.exists() else p/(k+'.csv'),names=True,delimiter=',')
def run():
 rows={}
 for name in ['shape_512','shape_1024','shape_1024_72ray']:
  p=D/name
  if not (p/'RETURN.txt').exists():continue
  a=table(p,'history');s=table(p,'shape');nh0=float((p/'NORMALIZATION.txt').read_text().split('=')[1])
  u=np.log(a['a']);h=a['h'];S=np.stack([a[f'S{i}'] for i in range(5)],axis=1)
  maxS=max(np.linalg.norm(S,axis=1))
  dmax=np.exp(maxS*(u-u[0]));emax=KT0*np.max(s['q'])*dmax/a['a']
  envelope=np.sqrt(2/3)*a['shape_l1']*emax
  fac=nh0*1e6/a['a']**3*electron_volt/RHO0
  source=3*fac*envelope/h**2
  weight=(a['a']/a['a'][-1])**3*h/h[-1]
  bound=np.trapezoid(source*weight,u)
  E=KT0/a['a'][-1]*s['x'];N=s['N_per_H'];dirs=np.stack([s[k] for k in ['nx','ny','nz']],axis=1)
  P=(dirs.T*(N*E))@dirs;Pi=P-np.eye(3)*np.trace(P)/3
  rows[name]=dict(nh0_cm3=nh0,final_Pi=float(np.linalg.norm(Pi)),terminal_absolute_U=float(np.sum(abs(N*E))),terminal_envelope=float(envelope[-1]),sampled_first_born_forcing_envelope=float(bound),max_sampled_S=float(maxS),rho_crit_J_m3=RHO0)
  assert np.linalg.norm(Pi)<=envelope[-1]
 o=dict(rows=rows,scope='first-Born frozen geometry source-only upper estimate sampled at accepted states; uses sampled max shear and qmax, not rigorous continuous bound or full tangent derivative')
 (D/'TANGENT_ENVELOPE.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
