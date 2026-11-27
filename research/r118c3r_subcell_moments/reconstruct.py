"""Two-moment local reconstruction with a positive base and explicit perturbation.
For each ray and cell use f=f_base(1+a+b(x-m)/s), normalized using quadrature.
Tracks relative N and U updates without subtracting huge full-reference states.
"""
import numpy as np,json,sys
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import PchipInterpolator
from weak import moments
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3q_finite_jump'))
from experiments import actual
def projector(edges,n,w,base,nq=16):
 z,g=leggauss(nq);y=(edges[:-1,None]+edges[1:,None])/2+np.diff(edges)[:,None]*z/2
 x=np.exp(y);g=np.diff(edges)[:,None]*g/2
 F=base(y.ravel()).reshape(len(w),len(edges)-1,nq).astype(np.longdouble)
 assert F.min()>0
 q=F*w[:,None,None]*x**3*g
 N=q.sum(axis=2);m=(q*x).sum(axis=2)/N
 s=(np.exp(edges[1:])-np.exp(edges[:-1]))[None,:];v=(q*((x-m[:,:,None])/s[:,:,None])**2).sum(axis=2)/N
 assert min(v.ravel())>0
 xc=np.exp((edges[:-1]+edges[1:])/2)
 def fit(dN,dU):
  a=dN/N;b=(dU+(xc-m)*dN)/(N*s*v)
  # Check full reconstruction at both endpoints, not just quadrature nodes.
  left=1+a+b*(np.exp(edges[:-1])-m)/s;right=1+a+b*(np.exp(edges[1:])-m)/s
  assert min(left.min(),right.min())>0
  # Orthogonality at quadrature order, independent recomputation of delta moments.
  df=a[:,:,None]+b[:,:,None]*(x-m[:,:,None])/s[:,:,None]
  nd=np.sum(q*df,axis=2);ud=np.sum(q*df*(x-xc[None,:,None]),axis=2)
  eN=np.max(abs(nd-dN))/max(np.max(abs(dN)),1e-300)
  eU=np.max(abs(ud-dU))/max(np.max(abs(dU)),1e-300)
  def evaluate(y):
   j=np.clip(np.searchsorted(edges,y,side='right')-1,0,len(edges)-2)
   return base(y)*(1+a[:,j]+b[:,j]*(np.exp(y)[None,:]-m[:,j])/s[:,j])
  return evaluate,dict(min_multiplier=float(min(left.min(),right.min())),N_reconstruction=float(eN),U_reconstruction=float(eU),max_a=float(np.max(abs(a))),max_b=float(np.max(abs(b))))
 return N,m,fit
def run():
 X,dd,d,n,w,theta,tr,cap,E=actual();y=np.log(X);sp=PchipInterpolator(y,dd,axis=1)
 def R(z):
  x=np.exp(z);r=1/np.expm1(x[None,:]/d[:,None]);return r*((1/np.expm1(x))/(w@r))[None,:]
 def F(z):return R(z)+sp(z)
 ed=np.linspace(y[0],y[-1],129);tau=1.64886e-9
 # Full and reference increments separately; stable signed increment independently.
 a,b,af=moments(ed,n,w,theta,tr,sp,R,8,3,True)
 zeros=lambda y:np.zeros((len(w),len(y)))
 c,e,ar=moments(ed,n,w,theta,tr,zeros,R,8,3,True)
 s,t,asig=moments(ed,n,w,theta,tr,sp,R,8,3)
 # independent full-minus-reference difference condition bound; use stable signed result for tiny delta.
 dN=np.sum(abs(a-c-s));dU=np.sum(abs(b-e-t))
 _,_,fitF=projector(ed,n,w,F);_,_,fitR=projector(ed,n,w,R)
 ff,qf=fitF(tau*a,tau*b);rr,qr=fitR(tau*c,tau*e)
 # Independent full second half from positive reconstructed spectra,
 # not the rounded signed difference; full/reference increments stored separately.
 halfF,_=fitF(.5*tau*a,.5*tau*b);halfR,_=fitR(.5*tau*c,.5*tau*e)
 af2,bf2,q2=moments(ed,n,w,theta,tr,zeros,halfF,8,3,True)
 ar2,br2,q3=moments(ed,n,w,theta,tr,zeros,halfR,8,3,True)
 # Total increment relative to each physical base; moment reconstruction is
 # exact for quadrature moments but finite pair stage only, not selfconsistent geometry.
 _,qfh=fitF(.5*tau*(a+af2),.5*tau*(b+bf2));_,qrh=fitR(.5*tau*(c+ar2),.5*tau*(e+br2))
 out=dict(full=qf,reference=qr,full_two_half=qfh,ref_two_half=qrh,fullhalf_N_rel=float(np.sum(abs(af2-a))/(2*np.sum(abs(a)))),fullhalf_U_rel=float(np.sum(abs(bf2-b))/(2*np.sum(abs(b)))),refhalf_N_rel=float(np.sum(abs(ar2-c))/(2*np.sum(abs(c)))),signed_N_l1=float(np.sum(abs(s))),signed_U_l1=float(np.sum(abs(t))),direct_subtraction_N_relative=float(dN/np.sum(abs(s))),direct_subtraction_U_relative=float(dU/np.sum(abs(t))),scope='actual 128-cell local two-moment reconstruction, one physical optical-depth step and two half steps separately for full/reference; signed derivative primary, rounded full-reference update not promoted. Not a live trajectory or fully dynamic signed moment owner.')
 (D/'RECONSTRUCTION.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
