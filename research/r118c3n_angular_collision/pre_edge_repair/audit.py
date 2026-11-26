"""Independent actual signed elastic ray inventory and same-direction nonlinear diffusion diagnostic."""
import numpy as np,json,gzip
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_trapezoid,trapezoid
from scipy.constants import c,k,m_e,G,h,electron_volt
D=Path(__file__).resolve().parent;KT0=8.617333262145e-5*2.7255
RHO0=3*c*c*2.1842852410855023e-18**2/(8*np.pi*G)
def load(label):
 p=D/label;r=np.genfromtxt(p/'history.csv',names=True,delimiter=',')
 path=p/'directional.csv.gz';d=np.genfromtxt(path if path.exists() else p/'directional.csv',names=True,delimiter=',')
 sp=np.genfromtxt(p/'spectrum.csv',names=True,delimiter=',')
 nh0=float((p/'NORMALIZATION.txt').read_text().split('=')[1])
 return r,d,sp,nh0
def diagnose(label):
 r,d,sp,nh0=load(label);a=r['a'][-1];nr=int(d['ray'].max()+1);nq=len(d)//nr;assert nr*nq==len(d)
 N=d['N_per_H'].reshape(nr,nq);x=d['x'].reshape(nr,nq);q=d['q'].reshape(nr,nq);n=np.stack([d[k].reshape(nr,nq)[:,0] for k in ['nx','ny','nz']],axis=1);E=KT0/a*x
 U=float(np.sum(N*E));P=(n.T*np.sum(N*E,axis=1))@n;Pi=P-np.eye(3)*U/3
 assert abs(U-r['spec'][-1])<1e-14 and abs(N.sum()-r['N_dir'][-1])<1e-12
 tr=r['secPxx']+r['secPyy']+r['secPzz'];sec=r['spec']+r['cool'];l=r['primary']+r['w']+r['b']+sec-r['w'][0]-r['b'][0]-r['source']+r['thermal_work']+r['photon_work']+r['boundary']+r['secondary_work']
 assert np.max(abs(l-r['ledger']))<1e-14 and np.max(abs(tr-sec))<1e-14
 assert max(abs(r['N_dir']-r['N_source']))<1e-12 and max(r['metric'])<1.6e-4
 # Project EACH ray's signed stock to common physical x, retaining explicit tails.
 nmu=int(np.sqrt(nr/2));assert 2*nmu*nmu==nr
 _,w0=leggauss(nmu);w0=np.repeat(w0/(4*nmu),2*nmu);wt=w0/(x[:,0]/q[:,0])**3;wt/=wt.sum()
 X=sp['x'];dl=np.log(X[1]/X[0]);stock=np.zeros((nr,len(X)));tails=np.zeros(2)
 for j in range(nr):
  idx=np.searchsorted(X,x[j],side='right');ok=(idx>0)&(idx<len(X));ids=idx[ok];f=(x[j,ok]-X[ids-1])/(X[ids]-X[ids-1])
  np.add.at(stock[j],ids-1,N[j,ok]*(1-f));np.add.at(stock[j],ids,N[j,ok]*f)
  tails[0]+=np.sum(N[j,~ok]);tails[1]+=np.sum(N[j,~ok]*E[j,~ok])
 assert abs(stock.sum()+tails[0]-N.sum())<1e-12 and abs(np.sum(stock*X)*KT0/a+tails[1]-U)<1e-14
 Tgamma=2.7255/a;nh=nh0*1e6/a**3;bb=8*np.pi**5*k**4*Tgamma**4/(15*h**3*c**3*nh*electron_volt);cap=bb*a/KT0*15/np.pi**4
 delta=stock/(wt[:,None]*cap*X**3*dl);mean=wt@delta;f0=1/np.expm1(X)
 theta=r['T'][-1]/Tgamma;dx=np.diff(X);dd=dx/theta;b=-np.expm1(-dd);qq=np.exp(-dd);g=(X[:-1]*X[1:])**2*dd/(dx*b)
 u,v=mean[:-1],mean[1:];cov=np.sum(wt[:,None]*(delta[:,:-1]-u)*(delta[:,1:]-v),axis=0)
 j0=-g*f0[:-1]*(1+f0[1:])*np.exp(-dx)*np.expm1(dx*(1-1/theta))
 flux=j0+g*((1+b*f0[:-1])*v+(-qq+b*f0[1:])*u+b*u*v);diff=g*b*cov
 rate=k*r['T'][-1]/(m_e*c*c)*r['ne'][-1]*1e6*c*6.6524587051e-29
 scalar=float(-bb*15/np.pi**4*rate*np.sum(dx*flux));cor=float(-bb*15/np.pi**4*rate*np.sum(dx*diff))
 return dict(rays=nr,steps=len(r)-1,terminal_T=float(r['T'][-1]),terminal_x=float(r['xHII'][-1]),terminal_H=float(r['h'][-1]),N=float(N.sum()),U=U,spectral_Pi=float(np.linalg.norm(Pi)),spectral_Pi_tensor=Pi.tolist(),max_energy_ledger=float(max(abs(l))),trace_error=float(max(abs(tr-sec))),number_error=float(max(abs(r['N_dir']-r['N_source']))),collision_energy=float(max(r['max_collision_U'])),collision_number=float(max(r['max_collision_N'])),elastic_depth=float(r['elastic_depth'][-1]),max_depth=float(max(r['max_depth'])),moved=float(r['elastic_moved'][-1]),blocked=float(r['elastic_blocked'][-1]),min_direction_full_occ=float(np.min(delta+f0)),projected_tail=tails.tolist(),same_direction_compton_rate_eV_H_s=scalar,covariance_correction_rate=cor,relative_covariance_correction=abs(cor)/abs(scalar)),r,nh0
def tangent(a,b,nh0):
 assert np.array_equal(a['a'],b['a']);u=np.log(a['a']);h=a['h'];q=-1-np.gradient(np.log(h),u)
 def P(a):
  p=np.zeros((len(a),3,3))
  for i,k in enumerate(['xx','yy','zz']):p[:,i,i]=a['secP'+k]
  for i,j,k in [(0,1,'xy'),(0,2,'xz'),(1,2,'yz')]:p[:,i,j]=p[:,j,i]=a['secP'+k]
  return p-np.trace(p,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3
 dp=P(b)-P(a);src=3*(nh0*1e6/a['a']**3*electron_volt/RHO0/h**2)[:,None,None]*dp
 exp=cumulative_trapezoid(q-2,u,initial=0);out=trapezoid(src*np.exp(exp[-1]-exp)[:,None,None],u,axis=0)
 return dict(frozen_geometry_forcing_norm=float(np.linalg.norm(out)),max_pressure_diff=float(np.max(np.linalg.norm(dp,axis=(1,2)))),direct_S_diff=float(np.linalg.norm(np.array([b[f'S{i}'][-1]-a[f'S{i}'][-1] for i in range(5)]))),scope='first-Born shear forcing from secondary Pi only; no full metric/chemical tangent system')
def run():
 rows={};raw={}
 for label in ['mean_512','elastic_512','mean_1024','elastic_1024','elastic_1024_72ray']:
  a,r,n=diagnose(label);rows[label]=a;raw[label]=r
 comp={}
 for m in [512,1024]:
  l,h=rows[f'mean_{m}'],rows[f'elastic_{m}'];a,b=raw[f'mean_{m}'],raw[f'elastic_{m}']
  comp[str(m)]=dict(delta_T=h['terminal_T']-l['terminal_T'],delta_U=h['U']-l['U'],delta_Pi_tensor_norm=float(np.linalg.norm(np.array(h['spectral_Pi_tensor'])-l['spectral_Pi_tensor'])),**tangent(a,b,n))
 o=dict(rows=rows,comparisons=comp,scope='actual signed stock and fixed local-frame elastic closure; nonlinear covariance correction for separate same-direction Kompaneets-like pair only, NOT full angular energy-changing kernel')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
