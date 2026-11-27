"""Independent saved live trial verification and isolated refinement comparisons."""
import json,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent
def row(p):
 ret=dict(x.split('=',1) for x in (p/'RETURN.txt').read_text().splitlines());assert ret['status']=='COMPLETE'
 a=np.genfromtxt(p/'history.csv',names=True,delimiter=',');s=np.genfromtxt(p/'stock.csv',names=True,delimiter=',');cap=float(ret['cap'])
 assert len(a)==int(ret['accepted'])+1 and len(s)==int(ret['cells'])*int(ret['rays'])
 assert np.isfinite(a.view(float)).all() and np.isfinite(s.view(float)).all() and np.all(a['margin']>0)
 P=np.array([a[k][-1] for k in ['corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz']]);pp=np.array([[P[0],P[3],P[4]],[P[3],P[1],P[5]],[P[4],P[5],P[2]]])
 stf=pp-np.eye(3)*np.trace(pp)/3;n=float(cap*np.sum(s['N']+s['collision_N']))
 r=dict(accepted=int(ret['accepted']),rejected=int(ret['rejected']),rays=int(ret['rays']),bins=int(ret['bins']),cells=int(ret['cells']),quadrature=ret['quadrature_fine'],margin=float(min(a['margin'])),max_ledger=float(max(abs(a['ledger']))),max_gauss=float(max(abs(a['gauss']))),max_metric=float(max(abs(a['metric']))),N_source_mismatch=float(max(abs(a['N']-a['N_source']))),stock_number_mismatch=abs(n-a['N'][-1]),collision_N_res=float(max(a['coll_N_res'])),collision_U_res=float(max(a['coll_U_res'])),fullhalf_N=float(max(a['fullhalf_N'])),fullhalf_V=float(max(a['fullhalf_V'])),corr_stf=stf.tolist(),corr_stf_norm=float(np.linalg.norm(stf)),corr_U=float(a['corr_U'][-1]),T=float(a['T'][-1]),xHII=float(a['xHII'][-1]),xHeII=float(a['xHeII'][-1]),spec=float(a['spec'][-1]),N=float(a['N'][-1]),proper_s=float(a['proper_s'][-1]))
 assert r['max_ledger']<1e-8 and r['max_gauss']<1e-10 and r['collision_N_res']<1e-10 and r['collision_U_res']<1e-10 and r['stock_number_mismatch']<1e-20
 return r
def run():
 rows={p.name:row(p) for p in sorted(D.iterdir()) if p.is_dir() and (p/'RETURN.txt').exists()}
 prior=row(D.parent/'r118c3v_live_dg/on_512_129_32_4')
 def compare(a,b):
  return dict(stf_relative=float(np.linalg.norm(np.array(a['corr_stf'])-b['corr_stf'])/np.linalg.norm(b['corr_stf'])),spec_relative=abs(a['spec']-b['spec'])/abs(b['spec']),T_abs=abs(a['T']-b['T']),xHII_abs=abs(a['xHII']-b['xHII']))
 cmp={}
 for label,x,y in [('same_quad_acceleration','coarse_512_129_32_4','PRIOR'),('quadrature','coarse_512_129_32_4','fine_512_129_32_4'),('time','fine_512_129_32_4','fine_512_129_32_8'),('DG_grid','fine_512_129_32_4','fine_512_258_32_4'),('scalar_grid','fine_512_258_32_4','fine_1024_258_32_4')]:
  if x in rows and (y in rows or y=='PRIOR'):cmp[label]=compare(rows[x],prior if y=='PRIOR' else rows[y])
 b=json.loads((D/'KERNEL_BENCH.json').read_text())['rows'];assert len(b)==4 and max(max(x['N_relative'],x['V_relative']) for x in b)<1e-8
 o=dict(rows=rows,compare=cmp,kernel=b,scope='exact same quadrature accelerated DG and actual native GH8/GL4 bounded live, one axis at a time; prior C3V 32/72 angle and rollback not rerun in C3W; no full AX11')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(dict(rows={k:{i:v for i,v in x.items() if i!='corr_stf'} for k,x in rows.items()},compare=cmp),indent=2))
if __name__=='__main__':run()
