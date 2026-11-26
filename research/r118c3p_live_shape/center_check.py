"""Independent centered-flux identity vs direct flux on accepted terminal spectra."""
import numpy as np,json
from pathlib import Path
from scipy.constants import k,m_e,c,h,electron_volt
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;KT0=8.617333262145e-5*2.7255
def table(p,k):
 f=p/(k+'.csv.gz');return np.genfromtxt(f if f.exists() else p/(k+'.csv'),names=True,delimiter=',')
def test_case(lab):
 p=D/lab;r=table(p,'history');a=r['a'][-1];nh0=float((p/'NORMALIZATION.txt').read_text().split('=')[1]);z=table(p,'directional')
 nr=int(z['ray'].max()+1);nq=len(z)//nr;q=z['q'].reshape(nr,nq);xx=z['x'].reshape(nr,nq);N=z['N_per_H'].reshape(nr,nq);dirs=np.stack([z[k].reshape(nr,nq)[:,0] for k in ['nx','ny','nz']],axis=1);d=xx[:,0]/q[:,0];nm=int(np.sqrt(nr/2));_,w=leggauss(nm);w=np.repeat(w/(4*nm),2*nm)/d**3;w/=w.sum()
 X=table(p,'spectrum')['x'];dl=np.log(X[1]/X[0]);tc=2.7255/a;nh=nh0*1e6/a**3;bb=8*np.pi**5*k**4*tc**4/(15*h**3*c**3*nh*electron_volt);cap=bb*a/KT0*15/np.pi**4;stock=np.zeros((nr,len(X)));lo=X[0]*np.exp(-dl/2);hi=X[-1]*np.exp(dl/2)
 for i in range(nr):
  idx=np.searchsorted(X,xx[i],side='right');ok=(idx>0)&(idx<len(X));j=idx[ok];f=(xx[i,ok]-X[j-1])/(X[j]-X[j-1]);np.add.at(stock[i],j-1,N[i,ok]*(1-f));np.add.at(stock[i],j,N[i,ok]*f)
  edge=(~ok)&(xx[i]>=lo)&(xx[i]<=hi)
  for j in [0,len(X)-1]:stock[i,j]+=N[i,edge&((idx==0) if j==0 else (idx==len(X)))].sum()
 f0=1/np.expm1(X);R=1/np.expm1(X[None,:]/d[:,None]);R*=f0/(w@R);delta=stock/(cap*w[:,None]*X**3*dl)
 M=.75*(1+(dirs@dirs.T)**2)*(1-dirs@dirs.T)*w[:,None]*w[None,:]
 for _ in range(64):
  t=np.sqrt(w/M.sum(axis=1));M*=t[:,None]*t[None,:]
 assert max(abs(M.sum(axis=1)-w))<1e-12
 theta=r['T'][-1]/tc;dt=np.log(r['a'][-1]/r['a'][-2])/(2.1842852410855023e-18*r['h'][-1]);clock=k*r['T'][-1]/(m_e*c*c)*r['ne'][-1]*1e6*c*6.6524587051e-29*dt
 out=[]
 for e in [1.,1e-4,1e-8]:
  dm=w@delta;de=dm+e*(delta-dm);ref=f0+e*(R-f0)
  u=w@de;rd=ref-f0;dd=de-u
  s=np.zeros_like(de);t=s.copy()
  for j,dx in enumerate(np.diff(X)):
   b=-np.expm1(-dx/theta);qq=np.exp(-dx/theta);g=(X[j]*X[j+1])**2/(theta*b)
   U,V=de[:,j],de[:,j+1];du,dv=dd[:,j],dd[:,j+1]
   raw=clock*M*g*((1+b*ref[:,j,None])*V[None,:]+(-qq+b*ref[None,:,j+1])*U[:,None]+b*U[:,None]*V[None,:])
   ce=clock*M*g*((1+b*f0[j]+b*u[j])*dv[None,:]+(-qq+b*f0[j+1]+b*u[j+1])*du[:,None]+b*(du[:,None]*dv[None,:]+rd[:,j,None]*V[None,:]+U[:,None]*rd[None,:,j+1]))
   for x,F in [(s,raw),(t,ce)]:x[:,j]+=F.sum(axis=1);x[:,j+1]-=F.sum(axis=0)
  s-=w[:,None]*s.sum(axis=0);t-=w[:,None]*t.sum(axis=0)
  scale=np.sum(abs(t));out.append(dict(anisotropy_scale=e,centered_l1=float(cap*scale),direct_centered_relative=float(np.sum(abs(s-t))/scale),centered_N_relative=float(abs(t.sum())/scale),centered_energy_relative=float(abs(np.sum(t*X))/np.sum(abs(t)*X))))
 assert out[0]['direct_centered_relative']<1e-6 and max(v['centered_N_relative'] for v in out)<1e-11
 return out
def run():
 rows={}
 for lab in ['shape_512','shape_1024','shape_1024_72ray']:
  if (D/lab/'RETURN.txt').exists():rows[lab]=test_case(lab)
 (D/'CENTER_CHECK.json').write_text(json.dumps(dict(rows=rows,scope='actual terminal state and controlled angular attenuation, direct vs centered local difference; no microscopic scattering claim'),indent=2)+'\n');print(rows)
if __name__=='__main__':run()
