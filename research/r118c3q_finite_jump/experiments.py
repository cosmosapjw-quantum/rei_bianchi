"""Finite-rate kernel: moment limit, actual patch, manufactured continuum check."""
import json,numpy as np,sys
from pathlib import Path
from scipy.constants import k,m_e,c,h,electron_volt
from scipy.interpolate import PchipInterpolator
from jump import kernel,ray_grid,proposal
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c3p_live_shape';KT0=8.617333262145e-5*2.7255
def table(p,k):
 f=p/(k+'.csv.gz');return np.genfromtxt(f if f.exists() else p/(k+'.csv'),names=True,delimiter=',')
def actual():
 p=P/'angular_1024';r=table(p,'history');a=r['a'][-1];nh0=float((p/'NORMALIZATION.txt').read_text().split('=')[1]);z=table(p,'directional')
 nr=int(z['ray'].max()+1);nq=len(z)//nr;q=z['q'].reshape(nr,nq);xx=z['x'].reshape(nr,nq);N=z['N_per_H'].reshape(nr,nq);dirs=np.stack([z[j].reshape(nr,nq)[:,0] for j in ['nx','ny','nz']],axis=1);d=xx[:,0]/q[:,0];nm=int(np.sqrt(nr/2));_,w=leggauss(nm);w=np.repeat(w/(4*nm),2*nm)/d**3;w/=w.sum()
 X=table(p,'spectrum')['x'];dl=np.log(X[1]/X[0]);tc=2.7255/a;nh=nh0*1e6/a**3;bb=8*np.pi**5*k**4*tc**4/(15*h**3*c**3*nh*electron_volt);cap=bb*a/KT0*15/np.pi**4;stock=np.zeros((nr,len(X)));lo=X[0]*np.exp(-dl/2);hi=X[-1]*np.exp(dl/2)
 for i in range(nr):
  idx=np.searchsorted(X,xx[i],side='right');ok=(idx>0)&(idx<len(X));j=idx[ok];f=(xx[i,ok]-X[j-1])/(X[j]-X[j-1]);np.add.at(stock[i],j-1,N[i,ok]*(1-f));np.add.at(stock[i],j,N[i,ok]*f)
  edge=(~ok)&(xx[i]>=lo)&(xx[i]<=hi)
  for j in [0,len(X)-1]:stock[i,j]+=N[i,edge&((idx==0) if j==0 else (idx==len(X)))].sum()
 delta=stock/(cap*w[:,None]*X**3*dl);theta=k*r['T'][-1]/(m_e*c*c);Tratio=r['T'][-1]/tc
 return X,delta,d,dirs,w,theta,Tratio,cap,KT0/a
def evaluate(x,n,w,theta,tr,F,R):
 out,full,ref,a=kernel(x,n,w,theta,tr,F.astype(np.longdouble),R.astype(np.longdouble))
 err=float(np.max(abs(out-(full-ref)))); bound=4096*np.finfo(np.longdouble).eps*float(np.max(abs(full))+np.max(abs(ref)))
 assert err<=max(1e-11*float(np.max(abs(out))),bound,1e-300),(err,bound)
 assert abs(a['number'])<1e-11*max(a['absflux'],1e-300) and abs(a['energy']-a['pair_energy'])<1e-11*max(a['absflux']*max(x),1e-300)
 assert a['max_rate']<1.00001
 P=(n.T*np.sum(out*x,axis=1))@n;Pi=P-np.eye(3)*np.trace(P)/3
 return dict(**a,L1=float(np.sum(abs(out))),Pi=float(np.sqrt(np.sum(Pi*Pi))),direct_subtraction_relative=err/max(float(np.max(abs(out))),1e-300),cancellation_bound=float(bound))
def moments():
 # Free photon Kramers-Moyal moments at x=1, Thomson angle quadrature.
 mu,w=leggauss(64);w=w*3/8*(1+mu*mu);tr=.7;rows=[]
 for theta in [1e-3,1e-4,1e-5,1e-6]:
  for fac in [4,8,16]:
   dy=np.sqrt(theta)/fac;y=np.arange(-int(np.ceil(16*np.sqrt(theta)/dy)),int(np.ceil(16*np.sqrt(theta)/dy))+1)*dy
   m=np.zeros(3)
   for z,ww in zip(mu,w):
    sig=np.sqrt(2*theta*(1-z))
    for i,p in proposal(y,sig):
     for j in [0] if i==0 else [-i,i]:
      eta=j*dy;dx=np.expm1(eta);rate=min(1.,np.exp(3*eta-dx/tr))*p*ww
      m+=rate*np.array([1.,dx,dx*dx])
   rows.append(dict(theta=theta,cells_per_sqrt_theta=fac,rate=float(m[0]),drift_over_theta=float(m[1]/theta),variance_over_theta=float(m[2]/theta),drift_relative=float(abs(m[1]/theta-(4-1/tr))/(4-1/tr)),variance_relative=float(abs(m[2]/theta-2)/2)))
 return rows
def run():
 rows={};n,w=ray_grid(3)
 for N in [128,256,512]:
  x=np.exp(np.linspace(-3,1,N));f=1/np.expm1(x/.7);R=np.broadcast_to(f,(len(w),N));v=.02*(3*n[:,2,None]**2-1)/2*np.exp(-.5*(np.log(x)[None,:]/.6)**2);F=R+v
  rows[f'manufactured_{N}']=evaluate(x,n,w,4e-4,.7,F,R)
  assert rows[f'manufactured_{N}']['L1']>1e-4
 X,delta,d,n,w,theta,tr,cap,energy=actual()
 # Original angular control excludes rejected C3P shape. Conditional
 # interpolation of actual smooth spectrum, not actual fine-grid source.
 interp=PchipInterpolator(np.log(X),delta,axis=1)
 for N in [128,256,512]:
  x=np.exp(np.linspace(-.005,.005,N));f=1/np.expm1(x);R=1/np.expm1(x[None,:]/d[:,None]);R*=f/(w@R);R=R.astype(np.longdouble);F=R+interp(np.log(x)).astype(np.longdouble)
  assert F.min()>0
  a=evaluate(x,n,w,theta,tr,F,R);b=evaluate(x,n,w,0.,tr,F,R)
  a.update(cells_per_sqrt_theta=float(np.sqrt(theta)/np.log(x[1]/x[0])),energy_eV_H_per_tau=float(cap*energy*a['energy']),elastic_L1=b['L1'],elastic_energy=b['energy'],patch=[float(x[0]),float(x[-1])])
  rows[f'actual_patch_{N}']=a
 # At original grid, thermal shifts almost exclusively map back to same cell.
 y=np.log(X);mx=max(sum(2*p for j,p in proposal(y,np.sqrt(2*theta*(1-mu))) if j>0) for mu in [-1.,0.,1.])
 o=dict(rows=rows,moments=moments(),actual_theta=float(theta),actual_temperature_ratio=float(tr),actual_coarse_dy=float(y[1]-y[0]),max_original_grid_offfrequency_proposal=float(mx),scope='conditional finite-rate nonrel Doppler Gaussian plus Metropolis phase-space detailed balance. Actual patch uses interpolated C3P angular control and reflecting boundary, not full live donor or exact microscopic kernel')
 (D/'JUMP_RESULTS.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
