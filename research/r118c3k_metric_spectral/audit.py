"""Independent inventory and endpoint controls on actual coupled trajectories."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rows={};a={}
 for label in ['mode2_on','mode3_on512','mode3_on2048','mode3_off2048']:
  p=D/label;f=np.genfromtxt(p/'history.csv',names=True,delimiter=',');a[label]=f
  assert np.all(np.diff(f['a'])>0) and np.all(f['T']>0)
  l=f['primary']+f['w']+f['b']+f['cool']+f['spec']-f['w'][0]-f['b'][0]-f['source']+f['thermal_work']+f['photon_work']+f['boundary']+f['secondary_work']
  assert max(abs(l-f['ledger']))<1e-14 and max(abs(l))<1e-8
  assert max(f['metric'])<1.6e-4 and max(f['specN'])<1.6e-4 and max(f['specU'])<1.6e-4
  rows[label]=dict(rows=len(f),accepted=int(f['accepted'][-1]),rejected=int(f['rejected'][-1]),a=float(f['a'][-1]),T=float(f['T'][-1]),xHII=float(f['xHII'][-1]),H=float(f['h'][-1]),S=[float(f[f'S{i}'][-1]) for i in range(5)],max_ledger=float(max(abs(l))),max_gauss=float(max(abs(f['gauss']))),max_metric=float(max(f['metric'])),max_specN=float(max(f['specN'])),max_specU=float(max(f['specU'])),final_spec=float(f['spec'][-1]),final_cool=float(f['cool'][-1]))
  if label.startswith('mode3'):
   s=np.genfromtxt(p/'spectrum.csv',names=True,delimiter=',');assert min(s['delta']+1/np.expm1(s['x']))>=0
   dl=np.log(s['x'][1]/s['x'][0]);rows[label]['signed_number']=float(np.sum(s['x']**3*s['delta']*dl))
 r={}
 for name,a0,a1 in [('freq512to2048','mode3_on512','mode3_on2048'),('spectral_vs_mode2','mode2_on','mode3_on2048'),('feedback_on_minus_off','mode3_off2048','mode3_on2048')]:
  x,y=rows[a0],rows[a1];assert abs(x['a']-y['a'])<1e-12
  r[name]=dict(deltaT=y['T']-x['T'],deltaX=y['xHII']-x['xHII'],deltaH=y['H']-x['H'],deltaS=(np.array(y['S'])-x['S']).tolist())
 out=dict(rows=rows,comparisons=r,scope='actual endpoint controls, different adaptive clocks; spectral controller in each shadow candidate, CSV last geometry stage only. No anisotropic spectral transport or production admission.')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
