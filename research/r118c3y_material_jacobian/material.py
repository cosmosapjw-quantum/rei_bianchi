"""C3Y actual coframe-history collisionless material Jacobian and nonstationary two-time OU."""
import numpy as np,json,subprocess,io,hashlib
from pathlib import Path
from scipy.linalg import expm
from scipy.interpolate import PchipInterpolator
from scipy.integrate import solve_ivp
from scipy.constants import c,G,electron_volt,k,m_e,e,epsilon_0,hbar
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;ROOT=D.parents[1];BASE='0e624af4668c7722759ccf781d91e15362b6d451';OLD='research/r118c3x_tangent_source';OU='research/r118c3u_positive_owner/birth_1024_32ray/history.csv';NATIVE='b145729be3d9d103ef1379c9efe5f85687558bc6'
H0=2.1842852410855023e-18;RHO0=3*c*c*H0*H0/(8*np.pi*G);OL=.684908;OG=5.4437488671046486e-5;ON=3.7562511328953514e-5;OM=.315;T=.00016763891604963858
def read(path):
 b=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+path]);return np.genfromtxt(io.BytesIO(b),names=True,delimiter=','),hashlib.sha256(b).hexdigest()
def basis():
 B=np.zeros((5,3,3));B[0]=np.diag([1,-1,0])/np.sqrt(2);B[1]=np.diag([-1,-1,2])/np.sqrt(6)
 for k,(i,j) in enumerate([(0,1),(0,2),(1,2)],2):B[k,i,j]=B[k,j,i]=1/np.sqrt(2)
 return B
B=basis();stf=lambda P:np.einsum('kij,...ij->...k',B,P)
def particles(nr=32,nt=8,np_=16):
 x,w=leggauss(nr);y=30*(1+x);norm=np.sum(30*w*y**3/(1+np.exp(y)));mu,ww=leggauss(nt);p=2*np.pi*np.arange(np_)/np_;mu,p=np.meshgrid(mu,p,indexing='ij')
 n=np.stack([np.sqrt(1-mu**2)*np.cos(p),np.sqrt(1-mu**2)*np.sin(p),mu],axis=-1).reshape(-1,3);ang=np.repeat(ww/(2*np_),np_)
 q=[];wt=[];mass=[];cold=OM+ON
 for m,J in [(0.001/T,B[1]),(.05/T,.6*B[2]+.8*B[3])]:
  cold-=ON/2*np.sum(30*w*y*y*np.hypot(y,m)/(1+np.exp(y)))/norm
  df=np.exp(-.03*np.einsum('ni,ij,nj->n',n,J,n));pwt=ON/2*ang[:,None]*30*w*y*y/(1+np.exp(y[None,:]*df[:,None]))/norm
  q.append((n[:,None,:]*y[None,:,None]).reshape(-1,3));wt.append(pwt.ravel());mass.append(np.full(n.shape[0]*nr,m))
 return np.concatenate(q),np.concatenate(wt),np.concatenate(mass),cold
Q,W,M,COLD=particles()
def matter(a,F,A=None):
 v=np.linalg.solve(F.T,Q.T).T;E=np.hypot(np.linalg.norm(v,axis=1),a*M);fac=a**-4
 rho=fac*(W@E);P=fac*np.einsum('n,ni,nj->ij',W/E,v,v)
 if A is None:return rho,P
 dv=-v@A;de=np.einsum('ni,ni->n',v,dv)/E
 dr=fac*(W@de);dP=fac*(np.einsum('n,ni,nj->ij',W/E,dv,v)+np.einsum('n,ni,nj->ij',W/E,v,dv)-np.einsum('n,ni,nj->ij',W*de/E**2,v,v))
 return dr,dP
def matrix(row,keys):
 x=[row[k] for k in keys];return np.array([[x[0],x[3],x[4]],[x[3],x[1],x[5]],[x[4],x[5],x[2]]])
def history(name):
 h,sha=read(OLD+'/'+name+'/history.csv');m,shm=read(OLD+'/'+name+'/matter.csv');assert np.array_equal(h['a'],m['a']);a=m['a'];F=np.stack([m[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=-1).reshape(-1,3,3);assert np.max(abs(np.linalg.det(F)-1))<1e-7
 PP=np.array([matrix(r,['Pxx','Pyy','Pzz','Pxy','Pxz','Pyz']) for r in m]);CC=np.array([matrix(r,['corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz']) for r in h]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=-1)
 pm=[];rm=[];J=[];FD=[]
 for i,(aa,f) in enumerate(zip(a,F)):
  r,P=matter(aa,f);pm.append(P);rm.append(r+COLD/aa**3)
  j=[]
  for A in np.eye(9).reshape(9,3,3):
   # Full left generator for linearized F'=S F; tangent stays tracefree.
   dr,dP=matter(aa,f,A);assert abs(dr+np.sum(A*P))<1e-12*max(np.linalg.norm(P),1.)
   j.append(np.r_[dr,dP.ravel()])
  J.append(np.array(j).T)
  if i in [0,len(a)//2,len(a)-1]:
   for A in B:
    dr,dP=matter(aa,f,A)
    for eps in [1e-3,1e-4,1e-5]:
     r1,p1=matter(aa,expm(eps*A)@f);r0,p0=matter(aa,expm(-eps*A)@f)
     FD.append(dict(i=i,eps=eps,pressure_relative=float(np.linalg.norm((p1-p0)/(2*eps)-dP)/np.linalg.norm(dP)),density_absolute=float(abs((r1-r0)/(2*eps)-dr))))
 pm=np.array(pm);rm=np.array(rm);J=np.array(J)
 # Native initial identity: isotropic primary photons, initial gas correction rho=0; thermal pressure known.
 fac=m['nh_m3']*electron_volt/RHO0;Pinit=pm[0]+np.eye(3)*(OG/a[0]**4/3+fac[0]*2*h['thermal'][0]/3)
 rinit=rm[0]+OG/a[0]**4
 init_r=float(abs(rinit-m['rho'][0])/m['rho'][0]);init_p=float(np.linalg.norm(Pinit-PP[0])/np.linalg.norm(PP[0]))
 assert init_r<1e-10 and init_p<1e-10,(init_r,init_p)
 assert max(x['pressure_relative'] for x in FD if x['eps']==1e-4)<1e-6
 u=np.log(a/a[0]);hp=m['h'][0]**2;src=stf(CC)*fac[:,None];fscale=np.max(np.linalg.norm(src,axis=1))/hp;assert fscale>0
 base=PchipInterpolator(u,np.c_[S,m['h'],m['rho'],PP.reshape(-1,9),pm.reshape(-1,9),src/(hp*fscale),J.reshape(len(u),-1)],axis=0)
 def rhs(t,y,material):
  row=base(t);s=row[:5];H,rho=row[5:7];P=row[7:16].reshape(3,3);Pmass=row[16:25].reshape(3,3);force=row[25:30];j=row[30:].reshape(10,9)
  ds=y[:5];dl=y[5];rr=y[6];A=y[7:].reshape(3,3);SS=np.einsum('k,kij->ij',s,B);dSS=np.einsum('k,kij->ij',ds,B);dA=dSS+SS@A-A@SS
  mt=j@A.ravel() if material else np.zeros(10);drm=mt[0];dpm=mt[1:].reshape(3,3)
  pi=stf(P);resid=stf(P-Pmass) if material else pi
  dr=hp*rr+drm;tr=np.trace(P);dtr=hp*rr+np.trace(dpm);dp=hp*force+stf(dpm)
  q=s@s/3+(rho+tr-2*OL)/(2*H**2);dq=2*s@ds/3+(dr+dtr)/(2*H**2)-(rho+tr-2*OL)*dl/H**2
  dds=(q-2)*ds+dq*s+3*(dp-2*pi*dl)/H**2
  drr=-4*rr-ds@resid/hp-s@force
  return np.r_[dds,-dq,drr,dA.ravel()]
 def solve(material,ref):
  z=solve_ivp(lambda t,y:rhs(t,y,material),(u[0],u[-1]),np.zeros(16),t_eval=u,method='DOP853',rtol=1e-11/ref,atol=1e-15/ref,max_step=max(np.diff(u))/ref);assert z.success;return z.y.T
 y0=solve(False,2);y=solve(True,2);yf=solve(True,4);A=yf[:,7:].reshape(-1,3,3);assert max(abs(np.trace(A,axis1=1,axis2=2)))<1e-10
 dmass=np.einsum('nij,nj->ni',J,A.reshape(-1,9));totaldr=hp*yf[:,6]+dmass[:,0]
 gauss=-np.sum(S*yf[:,:5],axis=1)/3-totaldr/m['h']**2+2*(m['rho']+OL)*yf[:,5]/m['h']**2
 out=dict(case=name,history_sha=sha,matter_sha=shm,initial_rho_relative=init_r,initial_pressure_relative=init_p,max_FD_pressure_relative_1e4=max(x['pressure_relative'] for x in FD if x['eps']==1e-4),max_FD_density_abs_1e4=max(x['density_absolute'] for x in FD if x['eps']==1e-4),FD=FD,source_scale=float(fscale),terminal_shear_norm=float(np.linalg.norm(yf[-1,:5])*fscale),frozen_shear_norm=float(np.linalg.norm(y0[-1,:5])*fscale),material_relative=float(np.linalg.norm(yf[-1,:5]-y0[-1,:5])/np.linalg.norm(yf[-1,:5])),solver_relative=float(np.linalg.norm(y[-1]-yf[-1])/np.linalg.norm(yf[-1])),max_linear_constraint_abs=float(max(abs(gauss))*fscale),max_linear_constraint_scaled=float(max(abs(gauss))),scope='actual represented native massive quadrature reconstructed in Python and initial total checked; remainder radiation-like conditional closure; not native harmonic/chemistry tangent')
 np.savez_compressed(D/(name+'_J.npz'),u=u,F=F,massive_rho=rm,massive_P=pm,J=J,tangent=yf*fscale,source=src)
 return out
def ou():
 h,sha=read(OU);u=np.log(h['a']/h['a'][0]);TT=h['T'];ne=h['ne']*1e6;v=np.sqrt(k*TT/m_e);wp=np.sqrt(ne*e**2/(epsilon_0*m_e));ln=np.log(v/wp/np.maximum(e**2/(4*np.pi*epsilon_0*k*TT),hbar/(m_e*v)))
 nu=4*np.sqrt(2*np.pi)/3*ne*e**4*ln/((4*np.pi*epsilon_0)**2*np.sqrt(m_e)*(k*TT)**1.5);H=H0*h['h'];sig=ne*TT/(ne[0]*TT[0]);f=PchipInterpolator(u,np.c_[nu,wp,H,v,sig],axis=0)
 rows=[]
 for q0 in [1e-8,1e-6,1e-5,2e-5,5e-5,1e-4]:
  def calc(n):
   x=np.concatenate([np.linspace(a,b,n,endpoint=False) for a,b in zip(u[:-1],u[1:])]+[u[-1:]]);z=(x[1:]+x[:-1])/2;nn,ww,HH,vv,ss=f(z).T
   q=q0*np.exp(-z)*wp[0]/ww;L=1+1/q**2;g=nn/L/HH;eq=ss/L;assert min(g)>=0 and min(eq)>=0
   G=np.r_[0,np.cumsum(g*np.diff(x))];V=np.zeros((len(x),2));V[0,1]=1/(1+1/q0**2)
   for i,(dt,gg,ee) in enumerate(zip(np.diff(x),g,eq)):V[i+1]=V[i]+(-np.expm1(-2*gg*dt))*(ee-V[i])
   ids=np.unique(np.rint(np.linspace(0,len(x)-1,17)).astype(int));C=np.empty((2,len(ids),len(ids)))
   for i,j in np.ndindex(len(ids),len(ids)):
    a,b=sorted([ids[i],ids[j]]);C[:,i,j]=np.exp(-(G[b]-G[a]))*V[a]
   scale=max(np.max(V),1e-300);mineig=min(np.linalg.eigvalsh(C/scale).ravel());assert mineig>-1e-10
   return C,G[-1],mineig,float(max(q*ww*vv/(c*nn))),scale
  c4,_,_,_,_=calc(4);c8,g,ev,kn,scale=calc(8);err=np.linalg.norm(c4-c8)/max(np.linalg.norm(c8),1e-300)
  rows.append(dict(q=q0,integrated_gamma=float(g),min_psd_eigenvalue_normalized=float(ev),refinement_relative=float(err),terminal_from_zero=float(c8[0,-1,-1]),terminal_initial_eq=float(c8[1,-1,-1]),endpoint_correlation_initial_eq=float(c8[1,0,-1]/np.sqrt(c8[1,0,0]*c8[1,-1,-1])),max_knudsen=kn,fluid_domain_all=bool(kn<=.1)))
 return dict(rows=rows,history_sha=sha,scope='conditional time-dependent scalar OU two-time covariance on actual thermal history; not full angular collision kernel')
if __name__=='__main__':
 rows=[]
 for name in ['fine_1024_129_32_8','fine_1024_129_32_16','fine_2048_129_32_8']:
  r=history(name);rows.append(r);print({k:v for k,v in r.items() if k!='FD'},flush=True)
 (D/'MATERIAL.json').write_text(json.dumps(rows,indent=2)+'\n')
 o=ou();(D/'OU_TWO_TIME.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)

