"""Read-only audit of accepted live DG trials; keep separate physical scales."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rows={}
 for p in sorted(D.iterdir()):
  if not p.is_dir() or not (p/'RETURN.txt').exists():continue
  ret=dict(x.split('=',1) for x in (p/'RETURN.txt').read_text().splitlines());assert ret['status']=='COMPLETE'
  a=np.genfromtxt(p/'history.csv',names=True,delimiter=',');s=np.genfromtxt(p/'stock.csv',names=True,delimiter=',');cap=float(ret['cap'])
  assert len(a)==int(ret['accepted'])+1 and len(s)==int(ret['cells'])*int(ret['rays'])
  assert np.isfinite(a.view(float)).all() and np.isfinite(s.view(float)).all()
  assert np.all(np.diff(a['a'])>0) and np.all(np.diff(a['proper_s'])>0)
  assert np.all(a['margin']>0)
  P=np.array([a[k][-1] for k in ['corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz']])
  pp=np.array([[P[0],P[3],P[4]],[P[3],P[1],P[5]],[P[4],P[5],P[2]]])
  stf=pp-np.eye(3)*np.trace(pp)/3
  n=float(cap*np.sum(s['N']+s['collision_N']))
  nc=float(cap*np.sum(s['collision_N']))
  r=dict(accepted=int(ret['accepted']),rejected=int(ret['rejected']),rollback=ret['rollback']=='true',rays=int(ret['rays']),bins=int(ret['bins']),cells=int(ret['cells']),margin=float(min(a['margin'])),max_ledger=float(max(abs(a['ledger']))),max_gauss=float(max(abs(a['gauss']))),max_metric=float(max(abs(a['metric']))),N_source_mismatch=float(max(abs(a['N']-a['N_source']))),stock_number_mismatch=abs(n-a['N'][-1]),corr_number_mismatch=abs(nc-a['corr_N'][-1]),collision_N_res=float(max(a['coll_N_res'])),collision_U_res=float(max(a['coll_U_res'])),fullhalf_N=float(max(a['fullhalf_N'])),fullhalf_V=float(max(a['fullhalf_V'])),coll_moved=float(a['coll_moved'][-1]),corr_P=pp.tolist(),corr_stf=stf.tolist(),corr_stf_norm=float(np.linalg.norm(stf)),corr_U=float(a['corr_U'][-1]),trace_error=float(abs(np.trace(pp)-a['corr_U'][-1])),T=float(a['T'][-1]),xHII=float(a['xHII'][-1]),xHeII=float(a['xHeII'][-1]),spec=float(a['spec'][-1]),N=float(a['N'][-1]),proper_s=float(a['proper_s'][-1]))
  assert r['max_ledger']<1e-8 and r['N_source_mismatch']<1e-12 and r['collision_N_res']<1e-10 and r['collision_U_res']<1e-10
  assert r['stock_number_mismatch']<1e-20 and r['trace_error']<1e-32 and r['max_gauss']<1e-10
  if r['rejected']:assert r['rollback']
  rows[p.name]=r
 assert len(rows)==6
 base=rows['on_512_129_32_2'];off=rows['off_512_129_32_2']
 def rel(a,b):return float(np.linalg.norm(np.asarray(a)-np.asarray(b))/np.linalg.norm(b))
 cmp={}
 for label in ['on_512_129_32_1','on_512_129_32_4','on_1024_258_32_2','on_512_129_72_2']:
  q=rows[label]
  cmp[label]=dict(stf_relative_to_32_2=rel(q['corr_stf'],base['corr_stf']),scalar_spec_relative=abs(q['spec']-base['spec'])/abs(base['spec']),temperature_abs=abs(q['T']-base['T']),ionization_abs=abs(q['xHII']-base['xHII']))
 a=np.genfromtxt(D/'on_512_129_32_2/history.csv',names=True,delimiter=',');b=np.genfromtxt(D/'off_512_129_32_2/history.csv',names=True,delimiter=',')
 cols=['a','h','T','xHII','xHeII','xHeIII','S0','S1','S2','S3','S4','primary','thermal','binding','cool','spec','N','N_source','proper_s']
 onoff={k:float(max(abs(a[k]-b[k]))) for k in cols}
 dsf=json.loads((D/'CURRENT_DSF_REFINED.json').read_text())['rows']
 result=dict(rows=rows,comparisons=cmp,onoff_stored_abs=onoff,dsf_max_32_64_rel=max(x['quadrature_rel'] for x in dsf),dsf_max_old_current_rel=max(x['old_current_relative'] for x in dsf),scope='actual native secondary DG coupled short z20->19.9998 trials, exact PR378 integrated Rust sources, angular-zero-mean finite jump, native scalar mean UV separate, no full AX11 or feedback detection')
 (D/'AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(comparisons=cmp,onoff_stored_abs=onoff,max_ledger=max(x['max_ledger'] for x in rows.values()),max_gauss=max(x['max_gauss'] for x in rows.values()),max_N_res=max(x['collision_N_res'] for x in rows.values()),max_U_res=max(x['collision_U_res'] for x in rows.values()),max_stock_mismatch=max(x['stock_number_mismatch'] for x in rows.values()),base_norm=base['corr_stf_norm'],timefine_norm=rows['on_512_129_32_4']['corr_stf_norm'],min_margin=min(x['margin'] for x in rows.values()),dsf_max_old_current_rel=result['dsf_max_old_current_rel']),indent=2))
if __name__=='__main__':run()
