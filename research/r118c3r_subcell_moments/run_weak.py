"""Actual coarse-frequency weak subcell moment tests and full-field admission."""
import numpy as np,json,sys
from pathlib import Path
from scipy.interpolate import PchipInterpolator
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3q_finite_jump'))
from experiments import actual
from jump import ray_grid
from weak import moments,test
def run():
 X,dd,d,n,w,theta,tr,cap,E=actual();y=np.log(X);sp=PchipInterpolator(y,dd,axis=1)
 # Reference interpolated separately at same input knots; exact Planck
 # reference used for all quadrature calls (not a fitted physical spectrum).
 def delta(z):return sp(z)
 def ref(z):
  x=np.exp(z);r=1/np.expm1(x[None,:]/d[:,None]);return r*((1/np.expm1(x))/(w@r))[None,:]
 testy=np.linspace(y[0],y[-1],10001);assert np.min(ref(testy)+delta(testy))>=0
 rows={}
 for N in [128,256,512,1024]:
  ed=np.linspace(y[0],y[-1],N+1)
  a,b,q=moments(ed,n,w,theta,tr,delta,ref,8,3)
  np.savez_compressed(D/f'actual_{N}.npz',edges=ed,N=a,Ucenter=b)
  xc=np.exp((ed[:-1]+ed[1:])/2)
  q.update(bins=N,energy_eV_H_tau=q['energy']*cap*E,center_only_energy=float(np.sum(a*xc)),centered_energy=float(np.sum(b)),same_cell_energy_fraction=q['same_cell_energy']/q['energy'],max_cell_dln=float(max(np.diff(ed))))
  rows[str(N)]=q;print('actual',N,q,flush=True)
 # Quadrature refinement at 512 grid, independent Gauss/Hermite order
 ed=np.linspace(y[0],y[-1],513);a,b,q=moments(ed,n,w,theta,tr,delta,ref,12,5)
 np.savez_compressed(D/'actual_512_refined.npz',edges=ed,N=a,Ucenter=b);rows['512_refined']=q;print('refined',q,flush=True)
 # Full field (not just distortion), exact physical explicit step at max
 # C3P half optical depth, enforce number and energy moment interval.
 ed=np.linspace(y[0],y[-1],257);a,b,q=moments(ed,n,w,theta,tr,delta,ref,8,4,True);xc=np.exp((ed[:-1]+ed[1:])/2)
 z,wq=leggauss(8);t=(ed[:-1,None]+ed[1:,None])/2+np.diff(ed)[:,None]*z/2
 x=np.exp(t);qwt=np.diff(ed)[:,None]*wq/2;F=(ref(t.ravel())+delta(t.ravel())).reshape(len(w),len(ed)-1,len(z))
 C=w[:,None,None]*x**3*qwt
 N0=np.sum(C*F,axis=2);U0=np.sum(C*F*x,axis=2);tau=1.64886e-9
 N1=N0+tau*a;U1=U0+tau*(b+a*xc);lo=np.exp(ed[:-1]);hi=np.exp(ed[1:])
 ratio=np.minimum(U1-lo*N1,hi*N1-U1)/(N1*(hi-lo))
 assert np.min(N1)>0 and np.min(ratio)>0
 full=dict(**q,min_N=float(N1.min()),min_relative_energy_margin=float(ratio.min()),dtau=tau)
 # Smooth angle-averaged signed Kompaneets energy (weak test x).
 zz,ww=leggauss(12);t=(y[:-1,None]+y[1:,None])/2+np.diff(y)[:,None]*zz/2;z=t.ravel();x=np.exp(z);r=1/np.expm1(x);dbar=w@sp(z);dbary=w@sp.derivative()(z);bose=dbar*(1+2*r+dbar);integ=(np.diff(y)[:,None]*ww/2).ravel()
 kom=-theta*np.sum(integ*(x**4*dbary+x**5/tr*bose))
 o=dict(rows=rows,full=full,kompaneets_energy=float(kom),actual_theta=theta,cap_per_H=cap,eV_per_x=E,scope='actual conditional coarse spectral reconstruction, continuous finite-rate jump measure, physical subcell N and U moments; no dynamic reconstruction/whole live integration')
 (D/'WEAK_RESULTS.json').write_text(json.dumps(o,indent=2)+'\n');print('full',full,'kom',kom,flush=True)
if __name__=='__main__':run()
