"""Independent high-precision pair algebra and recorded resolution/DSF audit."""
import json,numpy as np,mpmath as mp
from pathlib import Path
from jump import test,ray_grid,kernel
D=Path(__file__).resolve().parent
def run():
 mp.mp.dps=70;err=[]
 for g in ['1e-8','-1e-4','0.1']:
  a=mp.mpf('0.5819767068693264');b=a+mp.mpf('1e-5');u=mp.mpf('1.1e-14');v=mp.mpf('-1.7e-14');q=mp.exp(mp.mpf(g))
  raw=(a+u)*(1+b+v)-q*(b+v)*(1+a+u)-(a*(1+b)-q*b*(1+a))
  stable=u-v-mp.expm1(mp.mpf(g))*(v*(1+a)+b*u+u*v)
  err.append(float(abs(raw-stable)/max(abs(stable),mp.mpf('1e-100'))))
 j=json.loads((D/'JUMP_RESULTS.json').read_text());r=json.loads((D/'REFINEMENT.json').read_text());rows={**j['rows'],**r['rows']}
 assert len(rows)==8 and all(v['L1']>0 and v['max_rate']<=1.00001 for v in rows.values())
 for v in rows.values():assert abs(v['number'])<1e-11*v['absflux'] and abs(v['energy']-v['pair_energy'])<1e-11*v['absflux']*3
 p=json.loads((D/'RPA_SPLIT.json').read_text());assert all(v['pass'] for v in p['rows'])
 conv={}
 for name in ['manufactured','actual_patch']:
  a,b=[rows[f'{name}_{n}'] for n in [512,1024]]
  conv[name]={k:float(abs(a[k]-b[k])/max(abs(b[k]),1e-300)) for k in ['L1','Pi','energy']}
 out=dict(high_precision_pair_relative=max(err),equilibrium=test(),refinement=conv,kompaneets=r['kompaneets'],static_residual=max(abs(v['static_residual']) for v in p['rows']),second_residual=max(abs(v['second_residual']) for v in p['rows']),scope='independent high precision pair algebra, finite-rate graph and nonzero test; no resolved full-grid live coupling')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
 assert max(err)<1e-50
if __name__=='__main__':run()
