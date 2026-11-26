"""Audit actual accepted frequency ray stock against physical moments and native ledger."""
import numpy as np,json,gzip,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;KT0=8.617333262145e-5*2.7255
def run():
 rows={};data={}
 mesh=np.genfromtxt(D.parent/'r118c3k_metric_spectral/mode3_on2048/history.csv',names=True,delimiter=',')['a']
 for label in ['freq_512','mean_512','freq_1024','mean_1024','freq_1024_32ray','mean_1024_32ray']:
  p=D/label;a=np.genfromtxt(p/'history.csv',names=True,delimiter=',');data[label]=a
  assert np.array_equal(a['a'],mesh) and np.max(a['metric'])<1.6e-4
  u=a['cool']+a['spec'];tr=a['secPxx']+a['secPyy']+a['secPzz']
  l=a['primary']+a['w']+a['b']+u-a['w'][0]-a['b'][0]-a['source']+a['thermal_work']+a['photon_work']+a['boundary']+a['secondary_work']
  assert max(abs(tr-u))<1e-14 and max(abs(l-a['ledger']))<1e-14
  f=p/'directional.csv.gz';s=np.genfromtxt(f if f.exists() else p/'directional.csv',names=True,delimiter=',')
  E=KT0/a['a'][-1]*s['x'];N=s['N_per_H'];pp=np.stack([s['nx'],s['ny'],s['nz']],axis=1)
  us=float(N@E);ns=float(N.sum());P=(pp.T*(N*E))@pp
  assert abs(us-a['spec'][-1])<1e-14 and abs(ns-a['N_dir'][-1])<1e-12 and abs(np.trace(P)-us)<1e-14
  assert max(abs(a['N_dir']-a['N_source']))<1e-12
  p1=np.genfromtxt(p/'projected.csv',names=True,delimiter=',');p2=np.genfromtxt(p/'spectrum.csv',names=True,delimiter=',');x=p1['x'];assert np.array_equal(x,p2['x'])
  assert min(p1['delta']+1/np.expm1(x))>=0 and min(p2['delta']+1/np.expm1(x))>=0
  d=p1['delta']-p2['delta'];pn=np.linalg.norm(P-us*np.eye(3)/3)
  rows[label]=dict(steps=len(a)-1,max_ledger=float(max(abs(l))),max_trace=float(max(abs(tr-u))),max_gauss=float(max(abs(a['gauss']))),max_metric=float(max(a['metric'])),number_closure=float(max(abs(a['N_dir']-a['N_source']))),spectral_energy_closure=float(abs(us-a['spec'][-1])),terminal_N=ns,terminal_U=us,spectral_pi_norm=float(pn),total_pi_norm=float(np.linalg.norm(np.array([[a['secPxx'][-1],a['secPxy'][-1],a['secPxz'][-1]],[a['secPxy'][-1],a['secPyy'][-1],a['secPyz'][-1]],[a['secPxz'][-1],a['secPyz'][-1],a['secPzz'][-1]]])-u[-1]*np.eye(3)/3)),max_edge_abs_N=float(max(a['edgeNabs'])),max_edge_abs_U=float(max(a['edgeUabs'])),projected_shape_N=float(np.sum(x**3*abs(d))/np.sum(x**3*abs(p2['delta']))),projected_shape_U=float(np.sum(x**4*abs(d))/np.sum(x**4*abs(p2['delta']))),terminal_T=float(a['T'][-1]),terminal_x=float(a['xHII'][-1]),terminal_H=float(a['h'][-1]))
 comps={}
 for n in ['512','1024','1024_32ray']:
  a=rows[f'freq_{n}'];b=rows[f'mean_{n}'];comps[str(n)]={k:b[k]-a[k] for k in ['terminal_T','terminal_x','terminal_H','terminal_N','terminal_U','spectral_pi_norm']}
 grid={}
 for key in ['freq','mean']:
  a,b,c=[rows[f'{key}_{x}'] for x in ['512','1024_32ray','1024']]
  grid[key]=dict(frequency_T=b['terminal_T']-a['terminal_T'],angular_T=c['terminal_T']-b['terminal_T'],frequency_U=b['terminal_U']-a['terminal_U'],angular_U=c['terminal_U']-b['terminal_U'],angular_N=c['terminal_N']-b['terminal_N'],angular_Pi=c['spectral_pi_norm']-b['spectral_pi_norm'])
 o=dict(rows=rows,comparisons=comps,grid_comparisons=grid,scope='actual common mesh and signed spectral packets, mean feedback in scalar native chemistry, no angle-dependent Compton kernel; separated frequency and angular refinement')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
