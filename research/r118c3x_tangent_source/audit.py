"""Audit actual fixed-DG live source refinement, exact accepted matter and tangent."""
import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent/'r118c3w_refined_dg'
def row(p):
 ret=dict(x.split('=',1) for x in (p/'RETURN.txt').read_text().splitlines());assert ret['status']=='COMPLETE'
 a=np.genfromtxt(p/'history.csv',names=True,delimiter=',');s=np.genfromtxt(p/'stock.csv',names=True,delimiter=',');cap=float(ret['cap'])
 assert len(a)==int(ret['accepted'])+1 and len(s)==int(ret['cells'])*int(ret['rays'])
 assert np.isfinite(a.view(float)).all() and np.isfinite(s.view(float)).all() and np.all(a['margin']>0)
 P=np.array([a[k][-1] for k in ['corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz']]);pp=np.array([[P[0],P[3],P[4]],[P[3],P[1],P[5]],[P[4],P[5],P[2]]]);stf=pp-np.eye(3)*np.trace(pp)/3
 n=float(cap*np.sum(s['N']+s['collision_N']))
 r=dict(accepted=int(ret['accepted']),rejected=int(ret['rejected']),rays=int(ret['rays']),bins=int(ret['bins']),cells=int(ret['cells']),margin=float(min(a['margin'])),max_ledger=float(max(abs(a['ledger']))),max_gauss=float(max(abs(a['gauss']))),max_metric=float(max(abs(a['metric']))),N_source_mismatch=float(max(abs(a['N']-a['N_source']))),stock_number_mismatch=abs(n-a['N'][-1]),collision_N_res=float(max(a['coll_N_res'])),collision_U_res=float(max(a['coll_U_res'])),corr_stf=stf.tolist(),corr_stf_norm=float(np.linalg.norm(stf)),corr_U=float(a['corr_U'][-1]),T=float(a['T'][-1]),xHII=float(a['xHII'][-1]),spec=float(a['spec'][-1]),N=float(a['N'][-1]),proper_s=float(a['proper_s'][-1]),positive_repair_log_count=(D/(p.name+'.log')).read_text().count('DG_POSITIVE_SCALAR') if (D/(p.name+'.log')).exists() else None)
 assert r['max_ledger']<1e-8 and r['max_gauss']<1e-10 and r['collision_N_res']<1e-10 and r['collision_U_res']<1e-10 and r['stock_number_mismatch']<1e-20
 e=s['lo'][:r['cells']];edge=np.r_[e,s['hi'][r['cells']-1]]
 if (p/'matter.csv').exists():
  m=np.genfromtxt(p/'matter.csv',names=True,delimiter=',');assert np.array_equal(m['a'],a['a']) and np.isfinite(m.view(float)).all()
  assert np.all(m['rho']>0)
  r['native_matter_nodes']=len(m)
 return r,edge
def compare(a,b):
 return dict(stf_relative=float(np.linalg.norm(np.array(a['corr_stf'])-b['corr_stf'])/np.linalg.norm(b['corr_stf'])),spec_relative=abs(a['spec']-b['spec'])/abs(b['spec']),T_abs=abs(a['T']-b['T']),xHII_abs=abs(a['xHII']-b['xHII']))
def run():
 rows={};edges={}
 for p in sorted(D.glob('fine_*')):
  if p.is_dir() and (p/'RETURN.txt').exists():rows[p.name],edges[p.name]=row(p)
 prior,ep=row(W/'fine_512_129_32_8')
 base='fine_1024_129_32_8';fine='fine_2048_129_32_8';time='fine_1024_129_32_16';cmp={}
 assert base in rows and fine in rows
 for k,e in edges.items():assert np.array_equal(e,edges[base])
 cmp['512_1024']=compare(prior,rows[base]);cmp['1024_2048']=compare(rows[base],rows[fine])
 if time in rows:cmp['8_16']=compare(rows[base],rows[time])
 tg=json.loads((D/'TANGENT.json').read_text())['rows'];assert {x['label'] for x in tg}==set(rows)
 for x in tg:assert x['native_gauss_reconstruction_abs']<1e-12 and x['projected_relative']<1e-8 and x['terminal_shear_norm']>0
 out=dict(rows=rows,comparisons=cmp,fixed_grid_exact=True,prior_grid_relative=float(np.max(abs(ep-edges[base])/edges[base])),tangent=tg,scope='actual bounded native PR378 source-only scalar refinement at fixed canonical grid; exact C3W kernel, conditional tangent not full matter feedback. Generic initial SPECTRAL_FF_DOMAIN cannot uniquely identify failing subcheck; corrected physical edges and donor repair tested separately.')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(rows={k:{i:v for i,v in r.items() if i!='corr_stf'} for k,r in rows.items()},comparisons=cmp,prior_grid_relative=out['prior_grid_relative']),indent=2))
if __name__=='__main__':run()
