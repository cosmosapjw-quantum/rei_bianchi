"""Independent actual ray number/energy/stress inventory and live covariance diagnostic."""
import numpy as np,json
from pathlib import Path
from scipy.constants import k,electron_volt
D=Path(__file__).resolve().parent;KT0=8.617333262145e-5*2.7255
def run():
 rows={};raw={}
 mesh=np.genfromtxt(D.parent/'r118c3k_metric_spectral/mode3_on2048/history.csv',names=True,delimiter=',')['a']
 for label in ['elastic_512','angular_512','elastic_1024','angular_1024','angular_1024_72ray']:
  p=D/label;a=np.genfromtxt(p/'history.csv',names=True,delimiter=',');raw[label]=a
  assert np.array_equal(a['a'],mesh) and len(a)==484 and max(a['metric'])<1.6e-4
  f=p/'directional.csv.gz';f=f if f.exists() else p/'directional.csv';d=np.genfromtxt(f,names=True,delimiter=',')
  E=KT0/a['a'][-1]*d['x'];N=d['N_per_H'];n=np.stack([d[k] for k in ['nx','ny','nz']],axis=1)
  U=float(N@E);P=(n.T*(N*E))@n;Pi=P-np.eye(3)*U/3
  assert abs(U-a['spec'][-1])<1e-14 and abs(N.sum()-a['N_dir'][-1])<1e-12
  sec=a['cool']+a['spec'];tr=a['secPxx']+a['secPyy']+a['secPzz']
  l=a['primary']+a['w']+a['b']+sec-a['w'][0]-a['b'][0]-a['source']+a['thermal_work']+a['photon_work']+a['boundary']+a['secondary_work']
  assert max(abs(l-a['ledger']))<1e-14 and max(abs(tr-sec))<1e-14 and max(abs(a['N_dir']-a['N_source']))<1e-12
  assert min(a['canonical_min_full_ratio'])>0 and min(a['cov_min_full'])>0
  if label.startswith('angular'):assert abs(a['cov_work'][-1])>0
  else:assert a['cov_work'][-1]==0
  s=np.genfromtxt(p/'projected.csv',names=True,delimiter=',');assert min(s['delta']+1/np.expm1(s['x']))>=0
  rows[label]=dict(accepted=int(a['accepted'][-1]),rejected=int(a['rejected'][-1]),max_metric=float(max(a['metric'])),energy_ledger=float(max(abs(l))),trace_error=float(max(abs(tr-sec))),number_error=float(max(abs(a['N_dir']-a['N_source']))),ray_energy_residual=float(abs(U-a['spec'][-1])),canonical_min=float(min(a['canonical_min_full_ratio'])),conditional_full_min=float(min(a['cov_min_full'])),covariance_work_attribution=float(a['cov_work'][-1]),reference_max_relative=float(a['cov_ref_max'][-1]),marginal_error=float(a['cov_marginal_err'][-1]),Pi_norm=float(np.linalg.norm(Pi)),T=float(a['T'][-1]))
 comp={}
 for n in [512,1024]:
  a,b=raw[f'elastic_{n}'],raw[f'angular_{n}'];keys=['T','h','xHII','spec','N_dir']+[f'S{i}' for i in range(5)]
  comp[str(n)]={k:float(max(abs(b[k]-a[k]))) for k in keys}
 o=dict(rows=rows,max_path_differences=comp,scope='actual common mesh, frozen angular covariance correction in candidate scalar Newton; cov_work is instantaneous first-order attribution not resolved physical difference; directional energy redistribution diagnostic only')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
