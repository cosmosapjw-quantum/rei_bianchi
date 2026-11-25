"""Re-evaluate the C2N prescribed shear response on exact new V6 histories."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.integrate import cumulative_trapezoid,solve_ivp
D=Path(__file__).resolve().parent;B=Path('/home/cosmosapjw/worktrees/bass-r109-native-20261124')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
a0=1/21;C=299792458.;SIG=6.6524587051e-29;H20=67.4e3/3.0856775814913673e22*np.sqrt(.315*21**3+9.2e-5*21**4+1-.315-9.2e-5)
def response(a,t,ne):
 t=t-t[0];k=C*SIG*ne
 future=cumulative_trapezoid(k[::-1],-t[::-1],initial=0)[::-1]
 s=H20*(a0/a)**3;ex=np.exp(-future);sl=np.exp(-.3*future)
 A=-4*np.trapezoid(s*(6*ex+sl)/7,t);B=6/7*np.trapezoid(s*(sl-ex),t)
 mass=-np.expm1(-future[0]);dm=np.exp(-future[1:])*(-np.expm1(-(future[:-1]-future[1:])))
 assert abs(dm.sum()-mass)<5e-13*mass
 z=1/a-1;mean=float(dm@(.5*(z[1:]+z[:-1]))/mass)
 return dict(tau=float(future[0]),A_per_s20=float(A),B_per_s20=float(B),mean_z=mean)
data=json.loads((D/'RESULTS.json').read_text());out={};source={}
for name,r in data['cases'].items():
 if r['status']!='COMPLETE':continue
 rows=[]
 for s in r['segments']:
  p=Path(s['raw_path'])/'history.csv';assert sha(p)==s['hashes']['history.csv'];source[str(p)]=sha(p)
  x=np.genfromtxt(p,names=True,delimiter=',',usecols=['a','time_s','ne_proper_cm3'])
  rows.append(np.stack([x['a'],x['time_s'],1e6*x['ne_proper_cm3']],axis=1))
 x=np.concatenate([rows[0]]+[v[1:] for v in rows[1:]])
 out[name]=response(*x.T)
j=json.loads((B/'research/r118c2m_energy_budget/RESULTS.json').read_text());p=Path(j['raw'])/'cross'/'history.tsv';r=next(v for v in j['results'] if v['name']=='cross')
assert sha(p)==r['hashes']['history.tsv'];source[str(p)]=sha(p)
x=np.genfromtxt(p,names=True,delimiter='\t',usecols=['eta','time_s','nH_m3','xe']);out['bass_cross']=response(a0*np.exp(x['eta']),x['time_s'],x['nH_m3']*x['xe'])
old=json.loads((B/'research/r118c2n_visibility/RESULTS.json').read_text())
for k in ('A_per_s20','B_per_s20','tau','mean_z'):assert abs(out['bass_cross'][k]-old['results']['bass_cross'][k])<2e-12
for n,r in out.items():r['B_relative_to_bass']=r['B_per_s20']/out['bass_cross']['B_per_s20']-1
print(json.dumps(out,indent=2))
(D/'VISIBILITY.json').write_text(json.dumps(dict(status='PASS_SCOPED_REEVALUATED_C2N_RESPONSE',scope='weak prescribed LRS shear and actual V6 ne; no feedback/observed C_ell; same C2N quadrature',results=out,sources=source),indent=2)+'\n')
