"""Independent directional energy-shape correction, no scalar double counting."""
import numpy as np,json,sys
from pathlib import Path
from scipy.constants import k,m_e,c,h,electron_volt
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;KT0=8.617333262145e-5*2.7255
def run_case(label):
 p=D/label;r=np.genfromtxt(p/'history.csv',names=True,delimiter=',');a=r['a'][-1];nh0=float((p/'NORMALIZATION.txt').read_text().split('=')[1])
 f=p/'directional.csv.gz';f=f if f.exists() else p/'directional.csv';z=np.genfromtxt(f,names=True,delimiter=',');nr=int(z['ray'].max()+1);nq=len(z)//nr
 q=z['q'].reshape(nr,nq);xx=z['x'].reshape(nr,nq);n=z['N_per_H'].reshape(nr,nq);dirs=np.stack([z[k].reshape(nr,nq)[:,0] for k in ['nx','ny','nz']],axis=1)
 d=xx[:,0]/q[:,0];nm=int(np.sqrt(nr/2));_,w=leggauss(nm);w=np.repeat(w/(4*nm),2*nm)/d**3;w/=w.sum()
 X=np.genfromtxt(p/'spectrum.csv',names=True,delimiter=',')['x'];dl=np.log(X[1]/X[0]);tc=2.7255/a;nh=nh0*1e6/a**3;bb=8*np.pi**5*k**4*tc**4/(15*h**3*c**3*nh*electron_volt);cap=bb*a/KT0*15/np.pi**4
 stock=np.zeros((nr,len(X)));tail=0.;lo=X[0]*np.exp(-dl/2);hi=X[-1]*np.exp(dl/2)
 for i in range(nr):
  idx=np.searchsorted(X,xx[i],side='right');ok=(idx>0)&(idx<len(X));j=idx[ok];f=(xx[i,ok]-X[j-1])/(X[j]-X[j-1]);np.add.at(stock[i],j-1,n[i,ok]*(1-f));np.add.at(stock[i],j,n[i,ok]*f)
  edge=(~ok)&(xx[i]>=lo)&(xx[i]<=hi)
  for j in [0,len(X)-1]:stock[i,j]+=n[i,edge&((idx==0) if j==0 else (idx==len(X)))].sum()
  tail+=np.sum(abs(n[i,(~ok)&(~edge)]))
 f0=1/np.expm1(X);R=1/np.expm1(X[None,:]/d[:,None]);R*=f0/(w@R)
 delta=stock/(cap*w[:,None]*X**3*dl);F=R+delta;assert np.min(F)>=0
 mu=dirs@dirs.T;M=.75*(1+mu*mu)*(1-mu)*w[:,None]*w[None,:]
 for _ in range(64):
  s=np.sqrt(w/M.sum(axis=1));M*=s[:,None]*s[None,:]
 assert np.max(abs(M.sum(axis=1)-w))<1e-12
 theta=r['T'][-1]/tc;dt=np.log(r['a'][-1]/r['a'][-2])/(2.1842852410855023e-18*r['h'][-1]);clock=k*r['T'][-1]/(m_e*c*c)*r['ne'][-1]*1e6*c*6.6524587051e-29*dt
 ds=np.zeros_like(delta);covQ=0.;refmean=w@R;dm=w@delta;rd=R-refmean;dd=delta-dm
 for j,dx in enumerate(np.diff(X)):
  p=-np.expm1(-dx/theta);z=np.exp(-dx/theta);g=(X[j]*X[j+1])**2/(theta*p)
  U=delta[:,j];V=delta[:,j+1]
  flux=g*((1+p*R[:,j,None])*V[None,:]+(-z+p*R[None,:,j+1])*U[:,None]+p*U[:,None]*V[None,:])
  t=clock*M*flux;ds[:,j]+=t.sum(axis=1);ds[:,j+1]-=t.sum(axis=0)
  cov=np.sum(M*(rd[:,j,None]*dd[None,:,j+1]+dd[:,j,None]*rd[None,:,j+1]+dd[:,j,None]*dd[None,:,j+1]))
  covQ-=bb*15/np.pi**4*dx*clock*g*p*cov
 # mean portion already belongs to scalar Newton; keep zero-angle-mean shape only.
 shape=ds-w[:,None]*ds.sum(axis=0);scale=np.sum(abs(shape))
 nrerr=float(np.max(abs(shape.sum(axis=0))));energy=bb*15/np.pi**4*np.sum(shape*X);stress=(dirs.T*(bb*15/np.pi**4*np.sum(shape*X,axis=1)))@dirs
 assert nrerr<1e-13*max(scale,1e-300)
 assert abs(energy)<1e-13*bb*15/np.pi**4*np.sum(abs(shape)*X)
 new=F+shape/(w[:,None]*X**3*dl);assert np.min(new)>=0
 return dict(rays=nr,clock=clock,cov_energy_eV_H=float(covQ),shape_number_l1_per_H=float(cap*scale),mean_zero_max=float(nrerr),shape_energy_eV_H=float(energy),shape_stf_norm_eV_H=float(np.linalg.norm(stress-np.eye(3)*np.trace(stress)/3)),min_full_ratio=float(np.min(new/f0)),tail_abs_number=float(tail),scope='one actual terminal physical step, reference-normalized full-minus-reference conditional operator; zero-angle-mean part not inserted in live bridge')
def run():
 o={k:run_case(k) for k in ['angular_512','angular_1024','angular_1024_72ray']}
 (D/'SHAPE_DIAGNOSTIC.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
