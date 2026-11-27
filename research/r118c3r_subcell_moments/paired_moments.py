"""Paired two-moment reconstruction: evolve reference and signed increments stably."""
import sys,json,numpy as np
from pathlib import Path
from scipy.interpolate import PchipInterpolator
from numpy.polynomial.legendre import leggauss
from weak import moments
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3q_finite_jump'))
from experiments import actual
def solve2(M,v):
 a,b,c=M[...,0,0],M[...,0,1],M[...,1,1];q=a*c-b*b
 assert np.min(q)>0
 return np.stack([(c*v[...,0]-b*v[...,1])/q,(a*v[...,1]-b*v[...,0])/q],axis=-1)
class Owner:
 def __init__(self,edges,n,w,R,delta):
  self.edges=edges;self.n=n;self.w=w;self.R=R;self.delta=delta
  self.xc=np.exp((edges[:-1]+edges[1:])/2);self.dx=np.diff(np.exp(edges))
  z,g=leggauss(16);y=(edges[:-1,None]+edges[1:,None])/2+np.diff(edges)[:,None]*z/2;x=np.exp(y)
  cap=w[:,None,None]*x**3*np.diff(edges)[:,None]*g/2
  b=(x-self.xc[:,None])/self.dx[:,None];self.b=b
  self.mat=[]
  for f in [R,delta]:
   f=f(y.ravel()).reshape(cap.shape).astype(np.longdouble);q=cap*f
   a=q.sum(axis=2);c=(q*b).sum(axis=2);d=(q*b*b).sum(axis=2)
   self.mat.append(np.stack([a,c,c,d],axis=-1).reshape(a.shape+(2,2)))
  self.MR,self.Md=self.mat;self.MF=self.MR+self.Md
  assert np.min(self.MF[...,0,0])>0
 def update(self,nr,ur,nd,ud):
  rr=np.stack([nr,ur/self.dx],axis=-1);dd=np.stack([nd,ud/self.dx],axis=-1)
  cr=solve2(self.MR,rr)
  cd=solve2(self.MF,dd-np.einsum('...ij,...j->...i',self.Md,cr))
  cf=cr+cd
  left=(np.exp(self.edges[:-1])-self.xc)/self.dx;right=(np.exp(self.edges[1:])-self.xc)/self.dx
  mm=min(float(np.min(1+cr[...,0]+cr[...,1]*left)),float(np.min(1+cr[...,0]+cr[...,1]*right)),float(np.min(1+cf[...,0]+cf[...,1]*left)),float(np.min(1+cf[...,0]+cf[...,1]*right)))
  assert mm>0
  dr=np.einsum('...ij,...j->...i',self.MR,cr)-rr
  ds=np.einsum('...ij,...j->...i',self.MF,cd)+np.einsum('...ij,...j->...i',self.Md,cr)-dd
  er=float(np.max(abs(dr))/max(np.max(abs(rr)),1e-300));es=float(np.max(abs(ds))/max(np.max(abs(dd)),1e-300))
  assert max(er,es)<1e-12
  def eval(y):
   j=np.clip(np.searchsorted(self.edges,y,side='right')-1,0,len(self.edges)-2);b=(np.exp(y)-self.xc[j])/self.dx[j]
   ar=cr[:,j,0]+cr[:,j,1]*b;ad=cd[:,j,0]+cd[:,j,1]*b
   R=self.R(y);d=self.delta(y)
   return R*(1+ar),d*(1+ar)+(R+d)*ad
  return lambda y:eval(y)[0],lambda y:eval(y)[1],dict(min_multiplier=mm,reference_moment_error=er,signed_moment_error=es,max_diff_coefficient=float(np.max(abs(cd))))
def run():
 X,dd,d,n,w,theta,tr,cap,E=actual();y=np.log(X);sp=PchipInterpolator(y,dd,axis=1)
 def R(z):
  x=np.exp(z);r=1/np.expm1(x[None,:]/d[:,None]);return r*((1/np.expm1(x))/(w@r))[None,:]
 def delta(z):return sp(z)
 ed=np.linspace(y[0],y[-1],129);tau=1.64886e-9;zero=lambda y:np.zeros((len(w),len(y)))
 def rates(R,d):
  a,b,q=moments(ed,n,w,theta,tr,zero,R,8,3,True);c,e,v=moments(ed,n,w,theta,tr,d,R,8,3)
  return a,b,c,e,v
 a,b,c,e,v=rates(R,delta);O=Owner(ed,n,w,R,delta)
 Rf,df,f=O.update(tau*a,tau*b,tau*c,tau*e)
 Rh,dh,h=O.update(tau/2*a,tau/2*b,tau/2*c,tau/2*e)
 A,B,C,F,V=rates(Rh,dh);R2,d2,h2=O.update(tau/2*(a+A),tau/2*(b+B),tau/2*(c+C),tau/2*(e+F))
 den=lambda a:float(np.sum(abs(a)))
 relN=den(C-c)/(2*den(c));relU=den(F-e)/(2*den(e))
 # Store precise increments (not state subtraction), compare total energy independent of coarse center.
 N=tau/2*(c+C);U=tau/2*(e+F);energy=float(np.sum(U+N*O.xc))
 expected=tau/2*(v['energy']+V['energy'])
 assert abs(energy-expected)<1e-10*max(abs(expected),1e-300)
 np.savez_compressed(D/'PAIRED_STEP.npz',edges=ed,signed_N=N,signed_Ucenter=U,reference_N=tau/2*(a+A),reference_Ucenter=tau/2*(b+B))
 o=dict(full=f,half=h,two_half=h2,signed_fullhalf_N_relative=relN,signed_fullhalf_U_relative=relU,signed_number_res=float(N.sum()),signed_energy=float(energy),energy_res=float(abs(energy-expected)),signed_energy_eV_H=energy*cap*E,scope='local paired reference/signed two-moment owner, stable coefficient difference; one physical optical-depth step vs two half, no native full trajectory')
 (D/'PAIRED_STEP.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
