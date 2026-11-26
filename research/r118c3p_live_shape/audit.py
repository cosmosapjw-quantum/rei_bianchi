"""Reconstruct live compensated shape stock, stress and full-vs-half metric."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent;KT0=8.617333262145e-5*2.7255
def table(p,n):
 f=p/(n+'.csv.gz');return np.genfromtxt(f if f.exists() else p/(n+'.csv'),names=True,delimiter=',')
def run():
 labels=['angular_512','angular_1024','shape_512','shape_1024','shape_1024_72ray','shape_512_fine']
 mesh=np.genfromtxt(D.parent/'r118c3k_metric_spectral/mode3_on2048/history.csv',names=True,delimiter=',')['a']
 rows={};raw={}
 for k in labels:
  p=D/k;a=table(p,'history');raw[k]=a
  want=mesh if k!='shape_512_fine' else np.loadtxt(D/'mesh_half.csv',skiprows=1)
  assert len(a)==len(want) and max(abs(a['a']-want))<2e-16 and max(a['metric'])<1.6e-4
  d=table(p,'directional');s=table(p,'shape');assert np.array_equal(d['q'],s['q'])
  E=KT0/a['a'][-1]*s['x'];N=s['N_per_H'];n=np.stack([s[j] for j in ['nx','ny','nz']],axis=1)
  U=float(N@E);P=(n.T*(N*E))@n;Pi=P-np.eye(3)*U/3
  assert abs(U-a['shape_U'][-1])<1e-11*max(np.sum(abs(N*E)),1e-300)
  assert abs(N.sum()-a['shape_N'][-1])<1e-11*max(np.sum(abs(N)),1e-300)
  sec=a['cool']+a['spec'];tr=a['secPxx']+a['secPyy']+a['secPzz'];ledger=a['primary']+a['w']+a['b']+sec-a['w'][0]-a['b'][0]-a['source']+a['thermal_work']+a['photon_work']+a['boundary']+a['secondary_work']
  assert max(abs(ledger-a['ledger']))<1e-14 and max(abs(tr-sec))<1e-14 and max(abs(a['N_dir']-a['N_source']))<1e-12
  assert min(a['canonical_min_full_ratio'])>0 and min(a['cov_min_full'])>0
  proj=table(p,'projected');assert min(proj['delta']+1/np.expm1(proj['x']))>=0
  if k.startswith('shape'):assert np.sum(abs(N))>0 and max(a['shape_fullhalf_abs'])<1e-20
  else:assert np.sum(abs(N))==0
  rows[k]=dict(accepted=int(a['accepted'][-1]),rejected=int(a['rejected'][-1]),T=float(a['T'][-1]),shape_l1=float(np.sum(abs(N))),shape_U=U,shape_N=float(N.sum()),shape_Pi_norm=float(np.linalg.norm(Pi)),shape_moved=float(a['shape_moved_l1'][-1]),max_shape_number_res=float(max(a['shape_num_res'])),max_shape_energy_res=float(max(a['shape_U_res'])),max_shape_mean_res=float(max(a['shape_mean_res'])),fullhalf_abs=float(max(a['shape_fullhalf_abs'])),fullhalf_rel=float(max(a['shape_fullhalf_rel'])),ledger=float(max(abs(ledger))),trace=float(max(abs(tr-sec))),number=float(max(abs(a['N_dir']-a['N_source']))),min_canonical=float(min(a['canonical_min_full_ratio'])),min_conditional=float(min(a['cov_min_full'])),metric=float(max(a['metric'])))
 comp={}
 for n in [512,1024]:
  a,b=raw[f'angular_{n}'],raw[f'shape_{n}'];comp[str(n)]={k:float(max(abs(a[k]-b[k]))) for k in ['T','h','xHII','spec','N_dir','S0','S1','S2','S3','S4']}
 p,q=[table(D/k,'shape') for k in ['shape_512','shape_512_fine']]
 assert np.array_equal(p['q'],q['q']) and np.array_equal(p['ray'],q['ray'])
 conv=dict(L1_relative=float(np.sum(abs(p['N_per_H']-q['N_per_H']))/np.sum(abs(q['N_per_H']))),Pi_norm_relative=float(abs(rows['shape_512']['shape_Pi_norm']-rows['shape_512_fine']['shape_Pi_norm'])/rows['shape_512_fine']['shape_Pi_norm']),frequency_L1_ratio=rows['shape_1024']['shape_l1']/rows['shape_512']['shape_l1'],angular_Pi_relative=float(abs(rows['shape_1024_72ray']['shape_Pi_norm']-rows['shape_1024']['shape_Pi_norm'])/rows['shape_1024_72ray']['shape_Pi_norm']))
 out=dict(rows=rows,path_diff=comp,refinement=conv,scope='actual full vs two-half shape stock using native full and fine chemistry candidates and frozen conditional reference; shape stored separately, total stress and ledger include it; absolute local metric criterion 1e-20/H, no relative local convergence admission; frequency closure fails continuum limit (SINGULAR_ANGULAR.json)')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
