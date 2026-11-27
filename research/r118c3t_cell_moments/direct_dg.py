"""Direct canonical DG weak collision; continuous angular-mean subtraction.
Only signed angular increment is evolved. Scalar collision owner unchanged.
"""
import numpy as np,sys,json,importlib.util
from pathlib import Path
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.hermite import hermgauss
from scipy.constants import k,m_e,c
from dg import centers,remap,density,project
from actual_dg import prev,extended,T
D=Path(__file__).resolve().parent;P=D.parent/'r118c3s_moment_transport'
def rhs(ed,ce,d,n,w,theta,tr,delta,reference,gh=8,gl=3):
 nr=len(d);nc=len(ce)-1;qc=centers(ce);N=np.zeros((nr,nc),dtype=T);V=N.copy()
 # Split every source and target canonical edge and the conditional reference
 # discontinuities; no local-cell remapping inside the weak collision.
 cuts=np.unique(np.r_[ed,*[np.log(np.asarray(ce,float)*v) for v in d]])
 z,p=hermgauss(gh);p/=np.sqrt(np.pi);xg,wg=leggauss(gl)
 groups={};mu=np.clip(n@n.T,-1,1)
 for i in range(nr):
  for j in range(nr):
   if mu[i,j]<1-1e-14:groups.setdefault(round(float(mu[i,j]),13),[]).append((i,j))
 pair_abs=T(0);rawU=T(0)
 for m,pairs in groups.items():
  ii,jj=np.array(pairs).T;K=.75*(1+m*m);sig=np.sqrt(2*theta*(1-m))
  for zz,pp in zip(z,p):
   if zz<=0:continue
   eta=float(np.sqrt(2)*sig*zz);lo=ed[0];hi=ed[-1]-eta
   if hi<=lo:continue
   sp=np.unique(np.r_[cuts[(cuts>lo)&(cuts<hi)],(cuts-eta)[(cuts-eta>lo)&(cuts-eta<hi)],lo,hi]);l,r=sp[:-1],sp[1:]
   y=((l+r)[:,None]/2+(r-l)[:,None]*xg/2).ravel();qy=((r-l)[:,None]*wg/2).ravel()
   yy=y+eta;x=np.exp(y);xp=np.exp(yy);dg=x*np.expm1(eta)/tr
   da,db=delta(y)[ii],delta(yy)[jj];ra,rb=reference(y)[ii],reference(yy)[jj]
   C=(K*pp*w[ii]*w[jj])[:,None]*(qy*np.minimum(x**3,xp**3*np.exp(-dg)))[None,:]
   F=C*(da-db-np.expm1(dg)*(db*(1+ra)+rb*da+da*db));F=F.astype(T)
   ft=F.sum(axis=0);left=w[:,None]*ft;right=-w[:,None]*ft
   for z0,(i,j) in enumerate(pairs):left[i]-=F[z0];right[j]+=F[z0]
   pair_abs+=np.sum(abs(F));rawU+=np.sum(ft*x*np.expm1(eta))
   for i in range(nr):
    for xx,ff in [(x,left[i]),(xp,right[i])]:
     q=np.asarray(xx,dtype=T)/T(d[i]);j=np.searchsorted(ce,q,side='right')-1;assert min(j)>=0 and max(j)<nc
     np.add.at(N[i],j,ff);np.add.at(V[i],j,ff*(q-qc[j]))
 U=(V+N*qc)*d[:,None];den=max(np.sum(abs(N)),T('1e-300'));denu=max(np.sum(abs(U)),T('1e-300'))
 en=float(abs(U.sum())/denu);nn=float(abs(N.sum())/den);assert max(en,nn)<1e-12
 Pi=(n.T*np.sum(U,axis=1))@n;Pi-=np.eye(3)*np.trace(Pi)/3
 return N,V,dict(N_res=nn,U_res=en,raw_energy=float(rawU),projected_N_L1=float(np.sum(abs(N))),projected_U_L1=float(np.sum(abs(V))),Pi=float(np.sqrt(np.sum(Pi*Pi))),pair_abs=float(pair_abs))
def run_one(label):
 h,n,w,X,ed,q,xx,cap,e,original,ref,hist,_,_,_=prev.reconstruct(P/label);d=xx[:,0]/q[:,0];E=np.exp(ed.astype(T));ce=extended(E,2);qc=centers(ce);theta=k*h['T'][-1]/(m_e*c*c);tr=h['T'][-1]*h['a'][-1]/2.7255;dt=T(h['max_depth'][-1])
 N=[];V=[]
 for i in range(len(d)):
  a,b=project(E,lambda x:w[i]*x*x*original(np.log(x).astype(float).ravel())[i].reshape(x.shape),16)
  a,b=remap(E/d[i],a,b/d[i],ce);N.append(a);V.append(b)
 N,V=np.array(N),np.array(V)
 def occupation(A,B):
  def fun(y):
   x=np.exp(y).astype(T);return np.array([density(ce,A[i],B[i],x/d[i])/(d[i]*w[i]*x*x) for i in range(len(d))])
  return fun
 # Check full/reference sampled positivity across all mapped knots, both
 # sides and within each cell. Reference is not stored as affine density.
 knots=np.unique(np.r_[ed,*[np.log(np.asarray(ce,float)*v) for v in d]]);knots=knots[(knots>=ed[0])&(knots<=ed[-1])]
 test=np.unique(np.r_[knots,(knots[:-1]+knots[1:])/2,np.nextafter(knots,np.inf),np.nextafter(knots,-np.inf)]);test=test[(test>=ed[0])&(test<=ed[-1])]
 def pos(A,B):
  R=ref(test);F=R+occupation(A,B)(test);return float(np.min(F/R))
 mi=pos(N,V)
 if mi<=0:
  return dict(label=label,status='BLOCKED_INITIAL_REFERENCE',min_ratio=mi,scope='signed affine number density fails full/reference sampled realizability')
 # Same initial canonical state; direct weak projection. Full and two half
 # update are independently calculated on immutable state; no scalar mean.
 a,b,r=rhs(ed,ce,d,n,w,theta,tr,occupation(N,V),ref,4,2)
 A,B=N+dt*a/2,V+dt*b/2;mh=pos(A,B);assert mh>0
 c0,e0,s=rhs(ed,ce,d,n,w,theta,tr,occupation(A,B),ref,4,2)
 N1,V1=N+dt*a,V+dt*b;N2,V2=N+dt*(a+c0)/2,V+dt*(b+e0)/2
 mp=min(pos(N1,V1),pos(N2,V2));assert mp>0
 # independent finer quadrature from same base, without repeating time update.
 af,bf,f=rhs(ed,ce,d,n,w,theta,tr,occupation(N,V),ref,8,4)
 norm=lambda x:float(np.sum(abs(x)))
 rN=norm(a-af)/norm(af);rV=norm(b-bf)/norm(bf)
 np.savez_compressed(D/(label+'_direct.npz'),edges=ce,base_N=N,base_V=V,increment_N=a*dt,increment_V=b*dt,fine_increment_N=af*dt,fine_increment_V=bf*dt,full_N=N1,full_V=V1,twohalf_N=N2,twohalf_V=V2)
 return dict(label=label,status='SCOPED_LOCAL_STEP',min_ratio_initial=mi,min_ratio_updated=mp,dtau=float(dt),coarse=r,fine=f,quadrature_N=rN,quadrature_V=rV,fullhalf_N=norm(c0-a)/(2*norm(a)),fullhalf_V=norm(e0-b)/(2*norm(b)),scope='actual terminal signed canonical DG weak angular owner; finite timestep, no native scalar or geometry update, no microscopic vertex')
def run():
 rows=[]
 for label in ['moment_512_8ray','moment_1024_8ray','moment_512_18ray']:
  v=run_one(label);rows.append(v);print(v,flush=True)
 (D/'DIRECT_DG.json').write_text(json.dumps(dict(rows=rows),indent=2)+'\n')
if __name__=='__main__':run()
