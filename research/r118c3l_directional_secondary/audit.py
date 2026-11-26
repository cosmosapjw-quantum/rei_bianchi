"""Reconstruct directional secondary stress and energy ledger on common fixed mesh."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rows={};states={}
 mesh=np.genfromtxt(D.parent/'r118c3k_metric_spectral/mode3_on2048/history.csv',names=True,delimiter=',')['a']
 for label in ['iso_on','rays_on','rays_off']:
  p=D/label;a=np.genfromtxt(p/'history.csv',names=True,delimiter=',');states[label]=a
  assert len(a)==len(mesh) and max(abs(a['a']-mesh))<2e-16
  assert np.all(np.diff(a['a'])>0) and np.max(a['metric'])<1.6e-4
  U=a['cool']+a['spec'];P=np.zeros((len(a),3,3))
  for i,k in enumerate(['xx','yy','zz']):P[:,i,i]=a['secP'+k]
  for i,j,k in [(0,1,'xy'),(0,2,'xz'),(1,2,'yz')]:P[:,i,j]=P[:,j,i]=a['secP'+k]
  trace=np.trace(P,axis1=1,axis2=2);Pi=P-U[:,None,None]*np.eye(3)/3
  l=a['primary']+a['w']+a['b']+U-a['w'][0]-a['b'][0]-a['source']+a['thermal_work']+a['photon_work']+a['boundary']+a['secondary_work']
  assert max(abs(trace-U))<1e-14 and max(abs(l-a['ledger']))<1e-14
  rows[label]=dict(rows=len(a),max_mesh_error=float(max(abs(a['a']-mesh))),max_metric=float(max(a['metric'])),max_ledger=float(max(abs(l))),max_gauss=float(max(abs(a['gauss']))),trace_error=float(max(abs(trace-U))),final_U=float(U[-1]),final_Pi_norm=float(np.linalg.norm(Pi[-1])),final_spec=float(a['spec'][-1]),final_scalar_spec=float(a['spec_ref'][-1]),spec_transport_difference=float(a['spec'][-1]-a['spec_ref'][-1]),final_T=float(a['T'][-1]),final_x=float(a['xHII'][-1]),final_H=float(a['h'][-1]),final_S=[float(a[f'S{i}'][-1]) for i in range(5)])
  assert max(abs(l))<1e-8
 out={}
 for name,l,r in [('directional_minus_iso','iso_on','rays_on'),('feedback_on_minus_off','rays_off','rays_on')]:
  a,b=rows[l],rows[r];out[name]={k:b[k]-a[k] for k in ['final_T','final_x','final_H','final_U','final_spec','final_Pi_norm']};out[name]['S_diff_norm']=float(np.linalg.norm(np.array(b['final_S'])-a['final_S']))
 o=dict(rows=rows,comparisons=out,scope='same accepted mesh; scalar spectral chemistry with directional bolometric signed ray transport; not angular frequency collision solver')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
