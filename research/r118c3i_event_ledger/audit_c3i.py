"""Independent midpoint gas and full energy audit on accepted native event sources."""
import numpy as np,json,gzip
from pathlib import Path
from event_spectral import load,sha,cv,binding
from event_inventory import archive
D=Path(__file__).resolve().parent
def main():
 rows={}
 for label,raw in [('event_coarse4096','native_coarse'),('event4096','native'),('midpoint_coarse4096','native_coarse'),('midpoint_fine4096','native')]:
  raw=D/raw;r,e,v,Y,f,cool,absorb,Q,ff,birthT,checks=load(raw)
  z=np.load(D/(label+'.npz'));p=json.loads((D/(label+'.json')).read_text());a,T,w,b,q,cu,fu,wg,wr,res=z['rows'][:,:10].T
  assert np.array_equal(a,r['a'][1:]) and np.max(abs(q-Q))<1e-16
  C=cv(f,Y);B=binding(f,Y);w0=C[0]*r['T'][0];prev=np.r_[w0,w[:-1]]
  R=r['a'][:-1]/a;timing=p.get('timing','endpoint');scale=R if timing=='midpoint' else np.ones_like(R)
  dB=np.diff(B);net=Q-dB-cu-fu
  calc=w-prev*R**2-scale*net;gwork=prev*(1-R**2)+(1-scale)*net
  residual=w-prev+dB+gwork-Q+cu+fu
  assert max(np.max(abs(calc)),np.max(abs(gwork-wg)),np.max(abs(residual)))<1e-14
  U=v['BB_U'][-1]*15/np.pi**4*(z['x']@z['delta'])
  total=w[-1]-w0+B[-1]-B[0]+U+r['J0'][-1]-r['J0'][0]+wg.sum()+wr.sum()+e['photon_work'][-1]-e['photon_work'][0]+cool.sum()+e['boundary_u'][-1]-e['boundary_u'][0]-e['source_u'][-1]+e['source_u'][0]
  assert abs(total)<1e-11 and abs(total-p['global_total'])<1e-15
  for x in p['source_hashes']:assert p['source_hashes'][x]==sha(raw/x)
  rows[label]=dict(max_midpoint_equation=float(np.max(abs(calc))),max_gas_ledger=float(np.max(abs(residual))),total=float(total),delta_T=p['delta_T'])
 # Exact original C3G history identity and aggregate source check.
 old=D.parent/'r118c3g_spectral_cutoff/inputs/history.csv';assert sha(old)==sha(D/'native_coarse/history.csv')
 ref=archive();check=json.loads((D/'event_coarse4096.json').read_text())['source_checks'];assert abs(ref['other']-check['non_spectral_input'])<1e-14
 ffs={};base=np.load(D/'ff10.npz')['edges']
 for name in ['ff10','ff12','ff14']:
  p=json.loads((D/(name+'.json')).read_text());e=np.load(D/(name+'.npz'))['edges'];assert np.array_equal(e[-len(base):],base)
  ffs[name]=dict(net=p['net_number'],gross=p['gross_emission_number'],absorption=p['effective_absorption_number'],max_tau=p['max_tau'],energy=p['net_energy'])
 out=dict(rows=rows,ff=ffs,reference_sha=sha(old),scope='accepted source replay with midpoint impulse; independent arithmetic, not autonomous chemistry or exact two-half substage transfer')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
