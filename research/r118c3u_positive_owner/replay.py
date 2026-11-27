"""Actual native accepted spectral births -> positive reference-weighted canonical moments.
No angular collision feedback in replay; direct finite-rate local step separate.
"""
import numpy as np,json,sys
from pathlib import Path
from scipy.constants import k,h,c,electron_volt
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;P=D.parent/'r118c3t_cell_moments'
sys.path.insert(0,str(P))
from dg import centers
from actual_dg import extended,T
from positive import Cell
KT0=8.617333262145e-5*2.7255
def raygrid(nmu):
 m,w=leggauss(nmu);m,p=np.meshgrid(m,2*np.pi*np.arange(2*nmu)/(2*nmu),indexing='ij')
 return np.stack([np.sqrt(1-m*m)*np.cos(p),np.sqrt(1-m*m)*np.sin(p),m],axis=-1).reshape(-1,3),np.repeat(w/(4*nmu),2*nmu)
def ray(F,n,w0):
 v=n@np.linalg.inv(F);d=np.linalg.norm(v,axis=1);w=w0/d**3;err=abs(w.sum()-1);return d,v/d[:,None],w/w.sum(),float(err)
def deposit(e,x,N,ce,d,w):
 # piecewise affine signed source density, exactly preserving native nodal
 # number and energy of each source cell. Overlap integrates q, q*q.
 e=np.asarray(e,dtype=T);x=np.asarray(x,dtype=T);ce=np.asarray(ce,dtype=T)
 nr=len(d);nx=len(x);qc=centers(ce)
 lo=e[:-1][None,:]/d[:,None];hi=e[1:][None,:]/d[:,None];width=hi-lo;cc=(lo+hi)/2
 birth=N[None,:]*w[:,None];V=birth*(x[None,:]/d[:,None]-cc);A=birth/width;B=12*V/width**3
 out=np.zeros((nr,len(qc)),dtype=T);vv=out.copy()
 j0=np.searchsorted(ce,lo,side='right')-1;j1=np.searchsorted(ce,hi,side='left')-1
 assert min(j0.ravel())>=0 and max(j1.ravel())<len(qc) and max((j1-j0).ravel())<=2
 i=np.broadcast_to(np.arange(nr)[:,None],lo.shape)
 for sh in range(3):
  j=np.minimum(j0+sh,len(qc)-1);l=np.maximum(lo,ce[j]);r=np.minimum(hi,ce[j+1]);length=np.maximum(r-l,0);m=(l+r)/2
  v=length*(A+B*(m-cc));z=(m-qc[j])*v+B*length**3/12
  np.add.at(out,(i,j),v);np.add.at(vv,(i,j),z)
 return out,vv
class Owner:
 def __init__(self,e,n,w0):
  self.e=np.asarray(e,dtype=T);self.c=centers(self.e);self.h=np.diff(self.e)/2;self.n=n;self.w0=np.asarray(w0,dtype=T)
  base=lambda q:q*q/np.expm1(q)
  self.ref=Cell(self.e,base,32)
  self.M0=self.w0[:,None]*self.ref.M0;self.M1=self.w0[:,None]*self.ref.M1;self.M2=self.w0[:,None]*self.ref.M2
  self.det=self.M0*self.M2-self.M1*self.M1
  self.N=np.zeros_like(self.M0);self.V=np.zeros_like(self.N)
 def coefficients(self,N,V):
  z=V/self.h;A=(self.M2*N-self.M1*z)/self.det;B=(self.M0*z-self.M1*N)/self.det
  margin=float(np.min(1+A-abs(B)))
  return A,B,margin
 def admit(self,N,V):
  A,B,m=self.coefficients(N,V)
  if not np.isfinite(m) or m<=0:raise ValueError(f'positive weighted reconstruction {m}')
  return m
 def trial(self,N,V):
  a,b=self.N+N,self.V+V;mi=self.admit(a,b);return a,b,mi
 def occupation(self,N,V,d,w):
  A,B,mi=self.coefficients(N,V);assert mi>0
  def ref(y):
   x=np.exp(y).astype(T);q=x[None,:]/d[:,None]
   # Reference conserved canonical stock; actual normalized local angular
   # weight yields a common near-unity solid-angle normalization.
   return self.w0[:,None]*q*q/np.expm1(q)/(d[:,None]*w[:,None]*x*x)
  def delta(y):
   x=np.exp(y).astype(T);q=x[None,:]/d[:,None];j=np.clip(np.searchsorted(self.e,q,side='right')-1,0,len(self.c)-1);i=np.arange(len(d))[:,None];xi=(q-self.c[j])/self.h[j]
   assert min(q.ravel())>=self.e[0] and max(q.ravel())<=self.e[-1]
   return ref(y)*(A[i,j]+B[i,j]*xi)
  return delta,ref
 def energy(self,N,V,d,a):
  return np.sum((V+N*self.c)*d[:,None])*T(KT0)/T(a)
def run(bins,nmu=4,fine=False):
 label=f"{bins}"+("_fine" if fine else "")+(f"_{2*nmu*nmu}ray" if nmu!=4 else "")
 p=D/(f"birth_{bins}"+("_fine" if fine else "")+"_32ray");h0=np.genfromtxt(p/'history.csv',names=True,delimiter=',');z=np.loadtxt(p/('births.csv.gz' if (p/'births.csv.gz').exists() else 'births.csv'),delimiter=',');x=np.genfromtxt(p/'spectrum.csv',names=True,delimiter=',')['x'].astype(T)
 assert len(z)==2*(len(h0)-1) and z.shape[1]==32+bins
 assert np.array_equal(z[::2,0],h0['a'][:-1]) and np.array_equal(z[1::2,2],h0['a'][1:])
 dl=np.log(x[1]/x[0]);e=np.r_[x*np.exp(-dl/2),x[-1]*np.exp(dl/2)];ce=extended(e,4);n,w0=raygrid(nmu);o=Owner(ce,n,w0)
 nh0=float((p/'NORMALIZATION.txt').read_text().split('=')[1]);a0=h0['a'][0];tc=2.7255/a0;nh=nh0*1e6/a0**3;bb=8*np.pi**5*k**4*tc**4/(15*h**3*c**3*nh*electron_volt);cap=T(bb*a0/KT0*15/np.pi**4)
 maxN=maxU=maxray=0.;work=T(0);birthN=T(0);birthU=T(0);minratio=1.;max_pathN=0.;rows=[];fprev=np.eye(3);blocked=None
 for ii,s in enumerate(z):
  a,m,b=s[:3];F0,Fm,F1=s[5:32].reshape(3,3,3)
  d0,_,_,er0=ray(F0,n,w0);dm,_,wm,erm=ray(Fm,n,w0);d1,_,_,er1=ray(F1,n,w0);maxray=max(maxray,er0,erm,er1)
  # Source is exact native spectral distortion change, not inferred from a
  # cumulative stock or terminal shape. Distribution within a bin is chosen.
  qn=x**3*dl*s[32:].astype(T);dn,dv=deposit(e,x,qn,ce,dm.astype(T),wm.astype(T));nn=qn.sum();uu=np.sum(qn*x)*KT0/T(m)
  oldU=o.energy(o.N,o.V,d0,a);midU=o.energy(o.N,o.V,dm,m)
  try:A,B,mi=o.trial(dn,dv)
  except ValueError as ex:
   blocked=dict(half=ii,a=float(a),reason=str(ex));break
  minratio=min(minratio,mi);midnew=o.energy(A,B,dm,m);newU=o.energy(A,B,d1,b);w=oldU-midU+midnew-newU
  maxN=max(maxN,float(abs(np.sum(dn)-nn)/max(np.sum(abs(qn)),T('1e-300'))));maxU=max(maxU,float(abs(midnew-midU-uu)/max(np.sum(abs(qn*x))*KT0/T(m),T('1e-300'))))
  # Conservative source and geometry ledger with signed stock in canonical cells.
  o.N,o.V=A,B;work+=w;birthN+=nn;birthU+=uu
  if ii%2==1:
   max_pathN=max(max_pathN,float(abs(cap*o.N.sum()-T(h0['N_source'][ii//2+1]))))
   rows.append([b,float(cap*o.N.sum()),float(cap*newU),float(cap*work),float(cap*birthU),mi])
  if ii%256==0:print(bins,ii,mi,flush=True)
 # Rollback negative perturbation without mutation.
 oldN,oldV=o.N.copy(),o.V.copy()
 try:o.trial(-2*o.M0,np.zeros_like(o.V))
 except ValueError:pass
 else:raise AssertionError('rollback failure')
 assert np.array_equal(oldN,o.N) and np.array_equal(oldV,o.V)
 a=np.array(rows)
 if len(a):assert max(abs(a[:,2]+a[:,3]-a[:,4]))<1e-13
 out=dict(bins=bins,rays=len(n),accepted_half_steps=ii if blocked else len(z),blocked=blocked,min_full_multiplier=minratio,max_birth_N_relative=maxN,max_birth_U_relative=maxU,max_solid_angle_error=maxray,max_native_N_source_abs=max_pathN,terminal_signed_N=float(cap*o.N.sum()),terminal_signed_U=float(cap*o.energy(o.N,o.V,d1,b)) if not blocked else None,scope='actual native accepted spectral births and coframe; exact canonical N/V source deposition and collisionless metric transport, positive reference-weighted signed reconstruction, no finite jump live feedback. Full reference collisionless canonical Planck, native primary already owns Thomson.')
 np.savez_compressed(D/f'replay_{label}.npz',edges=ce,N=o.N,V=o.V,n=n,w0=w0,d=d1,F=F1,cap=cap,rows=a)
 (D/f'replay_{label}.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run(int(sys.argv[1]),int(sys.argv[2]) if len(sys.argv)>2 else 4,len(sys.argv)>3 and sys.argv[3]=='fine')
