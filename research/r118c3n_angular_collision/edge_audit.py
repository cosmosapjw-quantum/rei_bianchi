"""Project signed stock onto finite local physical-frequency cells and audit realizability."""
import numpy as np,json
from pathlib import Path
from scipy.constants import c,k,h,electron_volt,m_e
from numpy.polynomial.legendre import leggauss
from audit import load,KT0,tangent
D=Path(__file__).resolve().parent
def project(label):
 r,d,sp,nh0=load(label);a=r['a'][-1];nr=int(d['ray'].max()+1);nq=len(d)//nr;nm=int(np.sqrt(nr/2));assert 2*nm*nm==nr
 q=d['q'].reshape(nr,nq);x=d['x'].reshape(nr,nq);N=d['N_per_H'].reshape(nr,nq);dirs=np.stack([d[k].reshape(nr,nq)[:,0] for k in ['nx','ny','nz']],axis=1)
 _,w0=leggauss(nm);w0=np.repeat(w0/(4*nm),2*nm);ds=x[:,0]/q[:,0];w=w0/ds**3;w/=w.sum()
 X=sp['x'];dl=np.log(X[1]/X[0]);tc=2.7255/a;nh=nh0*1e6/a**3;bb=8*np.pi**5*k**4*tc**4/(15*h**3*c**3*nh*electron_volt);cap=bb*a/KT0*15/np.pi**4
 ref=cap*w0[:,None]*q**3*dl/np.expm1(x);canonical_ratio=1+N/ref
 stock=np.zeros((nr,len(X)));tail=np.zeros(4);lo=X[0]*np.exp(-dl/2);hi=X[-1]*np.exp(dl/2)
 for j in range(nr):
  idx=np.searchsorted(X,x[j],side='right');ok=(idx>0)&(idx<len(X));ids=idx[ok];f=(x[j,ok]-X[ids-1])/(X[ids]-X[ids-1])
  np.add.at(stock[j],ids-1,N[j,ok]*(1-f));np.add.at(stock[j],ids,N[j,ok]*f)
  edge=(~ok)&(x[j]>=lo)&(x[j]<=hi)
  for i in [0,len(X)-1]:
   m=edge&((idx==0) if i==0 else (idx==len(X)))
   stock[j,i]+=N[j,m].sum();e=N[j,m]*(x[j,m]-X[i])*KT0/a;tail[1]+=e.sum();tail[3]+=abs(e).sum()
  out=(~ok)&(~edge);e=N[j,out]*x[j,out]*KT0/a
  tail[0]+=N[j,out].sum();tail[1]+=e.sum();tail[2]+=abs(N[j,out]).sum();tail[3]+=abs(e).sum()
 U=float(np.sum(N*x)*KT0/a);P=(dirs.T*np.sum(N*x,axis=1)*KT0/a)@dirs;Pi=P-np.eye(3)*U/3
 assert abs(stock.sum()+tail[0]-N.sum())<1e-12 and abs(np.sum(stock*X)*KT0/a+tail[1]-U)<1e-14
 delta=stock/(cap*w[:,None]*X**3*dl);f0=1/np.expm1(X);projected_ratio=1+delta/f0
 tr=r['secPxx']+r['secPyy']+r['secPzz'];sec=r['spec']+r['cool'];l=r['primary']+r['w']+r['b']+sec-r['w'][0]-r['b'][0]-r['source']+r['thermal_work']+r['photon_work']+r['boundary']+r['secondary_work']
 assert abs(U-r['spec'][-1])<1e-14 and max(abs(l-r['ledger']))<1e-14 and max(abs(tr-sec))<1e-14 and max(abs(r['N_dir']-r['N_source']))<1e-12
 row=dict(rays=nr,steps=len(r)-1,terminal_T=float(r['T'][-1]),terminal_x=float(r['xHII'][-1]),terminal_H=float(r['h'][-1]),N=float(N.sum()),U=U,Pi_norm=float(np.linalg.norm(Pi)),Pi=Pi.tolist(),number_error=float(max(abs(r['N_dir']-r['N_source']))),energy_ledger=float(max(abs(l))),trace_error=float(max(abs(tr-sec))),elastic_depth=float(r['elastic_depth'][-1]),max_depth=float(max(r['max_depth'])),collision_energy=float(max(r['max_collision_U'])),collision_number=float(max(r['max_collision_N'])),moved=float(r['elastic_moved'][-1]),blocked=float(r['elastic_blocked'][-1]),canonical_min_ratio=float(canonical_ratio.min()),canonical_negative_cells=int(np.count_nonzero(canonical_ratio<0)),projected_min_ratio=float(projected_ratio.min()),projected_negative_cells=int(np.count_nonzero(projected_ratio<0)),projection_tail_number=float(tail[0]),projection_energy_defect=float(tail[1]),projection_abs_tail=float(tail[2]),projection_abs_energy_defect=float(tail[3]))
 if 'canonical_min_full_ratio' in r.dtype.names:
  row['min_ratio_all_accepted']=float(min(r['canonical_min_full_ratio']))
  assert abs(canonical_ratio.min()-r['canonical_min_full_ratio'][-1])<1e-9
 return row,r,nh0,(X,delta,w,dirs,bb)
def run():
 rows={};raw={}
 labels=['mean_512','elastic_512','mean_1024','elastic_1024','elastic_1024_72ray','edge_mean512','edge_elastic512','edge_mean1024','edge_elastic1024','edge_elastic1024_72ray']
 for lab in labels:
  a,r,n,_=project(lab);rows[lab]=a;raw[lab]=r
  if lab.startswith('edge_'):assert a['canonical_negative_cells']==0 and a['min_ratio_all_accepted']>0 and a['projected_negative_cells']==0,(lab,a)
 comp={}
 for nbin in [512,1024]:
  l,h=rows[f'edge_mean{nbin}'],rows[f'edge_elastic{nbin}'];a,b=raw[f'edge_mean{nbin}'],raw[f'edge_elastic{nbin}']
  comp[str(nbin)]=dict(delta_T=h['terminal_T']-l['terminal_T'],delta_U=h['U']-l['U'],delta_Pi_norm=float(np.linalg.norm(np.array(h['Pi'])-l['Pi'])),**tangent(a,b,n))
 o=dict(rows=rows,comparisons=comp,scope='actual canonical and finite physical cell projection; isotropic local Planck reference is chosen realizability diagnostic, not a fully evolved directional reference field')
 (D/'EDGE_AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print({k:{i:v for i,v in a.items() if i not in ['Pi']} for k,a in rows.items()});print(comp)
if __name__=='__main__':run()
