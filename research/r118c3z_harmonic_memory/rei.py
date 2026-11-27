"""C3Z primary harmonic tangent + exact EOS map; actual nonstationary auxiliary elimination."""
from pathlib import Path
import numpy as np,json,hashlib,subprocess,io
from scipy.constants import c,G,electron_volt,k,m_e,e,epsilon_0,hbar
from scipy.interpolate import PchipInterpolator
from scipy.integrate import solve_ivp
from scipy.sparse import csr_matrix
D=Path(__file__).resolve().parent;ROOT=D.parents[1];Y=D.parent/'r118c3y_material_jacobian'
BREPO=Path.home()/'worktrees/bass-r109-native-20261124';BBASE='c502814d4708bdfde88b1eb0a369df611905aaf1';PR='b145729be3d9d103ef1379c9efe5f85687558bc6';XBASE='0e624af4668c7722759ccf781d91e15362b6d451';X='research/r118c3x_tangent_source';OLD='research/r118c3u_positive_owner/birth_1024_32ray/history.csv'
H0=2.1842852410855023e-18;RHO0=3*c*c*H0*H0/(8*np.pi*G);OG=5.4437488671046486e-5;OL=.684908;FHE=.2454/(4*(1-.2454));CHI=np.array([13.598434599702,24.587389011,54.41776]);SIG=6.6524587051e-29;Y00=np.sqrt(4*np.pi);M=25
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def blob(repo,ref,path):return subprocess.check_output(['git','-C',str(repo),'show',ref+':'+path])
def hashb(b):return hashlib.sha256(b).hexdigest()
def csv(path):
 b=blob(ROOT,XBASE,path);return np.genfromtxt(io.BytesIO(b),names=True,delimiter=','),hashb(b)
B=np.zeros((5,3,3));B[0]=np.diag([1,-1,0])/np.sqrt(2);B[1]=np.diag([-1,-1,2])/np.sqrt(6)
for j,(i,k0) in enumerate([(0,1),(0,2),(1,2)],2):B[j,i,k0]=B[j,k0,i]=1/np.sqrt(2)
def stf(P):return np.einsum('kij,...ij->...k',B,P)
def mat(s):return np.einsum('k,kij->ij',s,B)
def matrix(a,keys):
 z=np.stack([a[k] for k in keys],axis=-1);P=np.zeros(z.shape[:-1]+(3,3))
 for k,(i,j) in enumerate([(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]):P[...,i,j]=P[...,j,i]=z[...,k]
 return P
def operators(lmax):
 m=(lmax+1)**2
 ids={}
 for f in ['kinetic/lie_hierarchy.rs','kinetic/lie_history.rs','kinetic/spin_sht.rs','homogeneous_sky/field.rs']:
  b=blob(BREPO,BBASE,'_rustcore/src/'+f);r=blob(ROOT,PR,'components/bass_rec/bass/_rustcore/src/'+f);assert b==r;ids[f]=hashb(b)
 p='research/r118c3o_analytic_s3/'
 data=blob(BREPO,BBASE,p+'generator.csv');ident=json.loads(blob(BREPO,BBASE,p+'ops/BUILD_ID.json'))
 assert hashb(data)==ident['generator_csv_sha256'];a=np.genfromtxt(io.BytesIO(data),names=True,delimiter=',')
 sel=np.concatenate([np.arange(m)+j*81 for j in range(3)]);op=[]
 for k0 in range(5):
  x=a[a['axis']==k0];A=csr_matrix((x['re']+1j*x['im'],(x['row'].astype(int),x['col'].astype(int))),shape=(243,243));op.append(A[sel][:,sel])
 return op,dict(generator_sha=hashb(data),matched_native_source_sha=ids,lmax=lmax)
def collision(y,m):
 v=y.reshape(3,m);o=-v.copy();o[:,0]=0
 d=np.sqrt(8/3);z=v[:,4:9];it=z[0];ee=-(z[1]+z[2])*.5;bb=.5j*(z[1]-z[2])
 di=-.9*it+.4/d*ee;de=.15*d*it-.4*ee;db=-bb
 o[0,4:9]=di;o[1,4:9]=-de-1j*db;o[2,4:9]=-de+1j*db
 return o.ravel()
def photon(y,a0,m):
 # Absolute moment map: native HarmonicSky::moments multiplied by rho; linear before normalization.
 z=y[:m];fac=OG/a0**4/Y00;rho=fac*z[0].real
 t=np.sqrt(16*np.pi/45)*z[6].real/Y00 # native t_zz numerator normalized by Y00; factor OG/a0^4 / Y00? energy = Y00*Y00 coefficient? see below
 # energy = sqrt(area)*a00; rho = OG/a0^4 * energy/area = OG/a0^4*a00/Y00.
 # rho * tzz = OG/a0^4 / area * sqrt(16pi/45)*a20.
 fac2=OG/a0**4/(4*np.pi);zz=fac2*np.sqrt(16*np.pi/45)*z[6].real;u=fac2*np.sqrt(8*np.pi/15)
 P=np.eye(3)*rho/3;P[0,0]+=-zz/2+u*z[8].real;P[1,1]+=-zz/2-u*z[8].real;P[2,2]+=zz
 P[0,1]=P[1,0]=-u*z[8].imag;P[0,2]=P[2,0]=-u*z[7].real;P[1,2]=P[2,1]=u*z[7].imag
 assert abs(np.trace(P)-rho)<=1e-12*max(abs(rho),np.linalg.norm(P),1e-300)
 return rho,P
def history(name,lmax=4):
 ops,identity=operators(lmax);m=(lmax+1)**2
 h,sh=csv(X+'/'+name+'/history.csv');a,sa=csv(X+'/'+name+'/matter.csv');j=np.load(Y/(name+'_J.npz'));u=np.log(a['a']/a['a'][0]);assert np.allclose(u,j['u'],rtol=0,atol=1e-14);assert np.array_equal(h['a'],a['a'])
 F=a['a'];S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);P=matrix(a,['Pxx','Pyy','Pzz','Pxy','Pxz','Pyz']);C=matrix(h,['corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz']);pm=j['massive_P'];J=j['J'];hp=a['h'][0]**2
 ne=a['ne_m3'];K=c*SIG*ne/(H0*a['h']);f=a['nh_m3']*electron_volt/RHO0;force=stf(C)*f[:,None];fs=np.max(np.linalg.norm(force,axis=1))/hp;assert fs>0
 bg=PchipInterpolator(u,np.c_[S,K],axis=0);y0=np.zeros(3*m,complex);y0[0]=Y00
 def Lop(s,y):return sum(x*(op@y) for x,op in zip(s,ops))
 def solve_y(eps=0,pert=None,ref=2):
  def fun(t,y):
   row=bg(t);s=row[:5];kk=row[5]
   if pert is not None:
    ds,dl=pert(t);s=s+eps*ds;kk=kk*np.exp(-eps*dl)
   return Lop(s,y)+kk*collision(y,m)
  z=solve_ivp(fun,(u[0],u[-1]),y0,t_eval=u,dense_output=True,rtol=2e-12/ref,atol=1e-16/ref,max_step=max(np.diff(u))/ref,method='DOP853');assert z.success
  return z
 yy=solve_y(ref=4);yr=np.array([photon(y,F[0],m)[0] for y in yy.y.T]);pp=np.array([photon(y,F[0],m)[1] for y in yy.y.T])
 trace_reference=np.trace(P-pm,axis1=1,axis2=2)-f*(h['primary']+h['cool']+h['spec']+2*h['thermal'])
 trace_error=float(np.max(abs(yr-trace_reference)/np.maximum(abs(trace_reference),1e-300)))
 assert trace_error<1e-5,(name,trace_error)
 # Exact EOS/binding on native data. No chemistry rate derivative claimed.
 x=np.stack([h['xHII'],h['xHeII'],h['xHeIII']],axis=1);g=np.array([1,FHE,2*FHE]);part=1+FHE+x@g
 nh=a['nh_m3'];w=h['thermal'];T=h['T'];neref=nh*(x@g);wref=1.5*(k/electron_volt)*T*part;bindg=np.array([CHI[0],FHE*CHI[1],FHE*(CHI[1]+CHI[2])]);bind=x@bindg
 e0=dict(ne_rel=float(np.max(abs(neref-ne)/ne)),thermal_rel=float(np.max(abs(wref-w)/w)),binding_rel=float(np.max(abs(bind-h['binding'])/np.maximum(abs(h['binding']),1e-300))))
 assert max(e0.values())<1e-7,e0
 dTdx=-T[:,None]*g/part[:,None];dTdw=T/w;dnedx=nh[:,None]*g
 # Admissible positive perturbation for boundary He fractions; check algebraic derivative via forward/central.
 dx=np.array([.0002,.0001,.0001]);dw=1e-5;es=[]
 for eps in [1e-3,1e-4,1e-5]:
  Te=2*(w+eps*dw)/(3*(k/electron_volt)*(1+FHE+(x+eps*dx)@g))
  Tr=2*w/(3*(k/electron_volt)*part);dt=Tr*(dw/w-dx@g/part)
  es.append(float(np.linalg.norm((Te-Tr)/eps-dt)/np.linalg.norm(dt)))
 # Continuous tangent using actual background and normalized DG source.
 raw=PchipInterpolator(u,np.c_[S,a['h'],a['rho'],P.reshape(-1,9),pm.reshape(-1,9),force/(hp*fs),J.reshape(len(u),-1),K],axis=0)
 def rhs(t,y,active):
  row=raw(t);s=row[:5];H,rho=row[5:7];pt=row[7:16].reshape(3,3);pma=row[16:25].reshape(3,3);fo=row[25:30];jj=row[30:-1].reshape(10,9);kk=row[-1]
  ds=y[:5].real;dl=y[5].real;rr=y[6].real;A=y[7:16].real.reshape(3,3);Z=y[16:];Yt=yy.sol(t);_,pga=photon(Yt,F[0],m)
  AA=mat(s);dAA=mat(ds);dA=dAA+AA@A-A@AA
  mt=jj@A.ravel();drm=mt[0];dpm=mt[1:].reshape(3,3)
  drg,dpg=photon(Z,F[0],m) if active else (0.,np.zeros((3,3)))
  rtot=hp*rr+drm+drg;dtr=hp*rr+np.trace(dpm)+drg;pi=stf(pt);dp=hp*fo+stf(dpm+dpg)
  q=s@s/3+(rho+np.trace(pt)-2*OL)/(2*H**2);dq=2*s@ds/3+(rtot+dtr)/(2*H**2)-(rho+np.trace(pt)-2*OL)*dl/H**2
  dds=(q-2)*ds+dq*s+3*(dp-2*pi*dl)/H**2
  res=stf(pt-pma-pga) if active else stf(pt-pma)
  drr=-4*rr-ds@res/hp-s@fo
  dZ=Lop(s,Z)+kk*collision(Z,m)+Lop(ds,Yt)-kk*dl*collision(Yt,m) if active else np.zeros_like(Z)
  return np.r_[dds,-dq,drr,dA.ravel(),dZ]
 def tangent(active,ref):
  z=solve_ivp(lambda t,y:rhs(t,y,active),(u[0],u[-1]),np.zeros(16+3*m,complex),t_eval=u,dense_output=True,rtol=1e-11/ref,atol=1e-15/ref,max_step=max(np.diff(u))/ref,method='DOP853');assert z.success
  return z
 off=tangent(False,2);on=tangent(True,2);fine=tangent(True,4);yf=fine.y.T
 norm=lambda x:float(np.linalg.norm(x))
 # Independent amplified frozen-history tangent derivative (not microscopic chemistry).
 def perturb(t):
  v=(t-u[0])/(u[-1]-u[0]);return np.array([.002*np.sin(2*v),.001*v,0.,0.,.001]),.01*v
 def rhsz(t,z):
  row=bg(t);ds,dl=perturb(t);yt=yy.sol(t);return Lop(row[:5],z)+row[5]*collision(z,m)+Lop(ds,yt)-row[5]*dl*collision(yt,m)
 zz=solve_ivp(rhsz,(u[0],u[-1]),np.zeros(3*m,complex),rtol=1e-12,atol=1e-18,max_step=max(np.diff(u))/4,method='DOP853');assert zz.success
 fd=[]
 for eps in [.1,.01,.001]:
  vp=solve_y(eps,perturb,4).y[:,-1];vm=solve_y(-eps,perturb,4).y[:,-1]
  fd.append(norm((vp-vm)/(2*eps)-zz.y[:,-1])/norm(zz.y[:,-1]))
 A=yf[:,7:16].real.reshape(-1,3,3);drm=np.einsum('nij,nj->ni',J,A.reshape(-1,9))[:,0];drg=np.array([photon(z,F[0],m)[0] for z in yf[:,16:]]);deltaR=hp*yf[:,6].real+drm+drg
 gauss=-np.sum(S*yf[:,:5].real,axis=1)/3-deltaR/a['h']**2+2*(a['rho']+OL)*yf[:,5].real/a['h']**2
 out=dict(case=name,lmax=lmax,source_sha=sh,matter_sha=sa,identity=identity,primary_trace_reconstruction_relative=trace_error,eos_identity=e0,eos_directional_FD=es,opacity_fraction_derivative_at_last=(dnedx[-1]/ne[-1]).tolist(),binding_derivative_eV_per_H=bindg.tolist(),source_scale=float(fs),terminal_shear_norm=norm(yf[-1,:5])*fs,without_primary_feedback=norm(off.y[:5,-1])*fs,primary_feedback_relative=norm(yf[-1,:5]-off.y[:5,-1])/norm(yf[-1,:5]),harmonic_tangent_norm=norm(yf[-1,16:])*fs,solver_relative=norm(on.y[:,-1]-fine.y[:,-1])/norm(fine.y[:,-1]),frozen_history_FD_relative=fd,gauss_scaled_max=float(max(abs(gauss))),scope='continuous harmonic streaming+rest-electron collision projected l<=L from byte-matched source, actual accepted clock; massive tangent and primary harmonic material response; remaining external sector radiation-like conditional; chemistry algebraic only, not native rate Jacobian nor discrete step tangent')
 assert min(fd)<1e-5,(name,fd)
 np.savez_compressed(D/(name+f'_l{lmax}_TANGENT.npz'),u=u,Y=yy.y.T,Z=yf[:,16:]*fs,geom=yf[:,:16].real*fs,EOS_dTdx=dTdx,EOS_dTdw=dTdw,EOS_dnedx=dnedx)
 print(out,flush=True);return out
def memory():
 h,sh=csv(OLD);u=np.log(h['a']/h['a'][0]);du=u[-1]-u[0];t=u/du;T=h['T'];ne=h['ne']*1e6;v=np.sqrt(k*T/m_e);wp=np.sqrt(ne*e**2/(epsilon_0*m_e));ln=np.log(v/wp/np.maximum(e**2/(4*np.pi*epsilon_0*k*T),hbar/(m_e*v)));nu=4*np.sqrt(2*np.pi)/3*ne*e**4*ln/((4*np.pi*epsilon_0)**2*np.sqrt(m_e)*(k*T)**1.5);H=H0*h['h']
 f=PchipInterpolator(t,np.c_[nu,wp,H,v],axis=0);alpha=.2;b=1.;cc=1.;rows=[]
 for q0 in [1e-8,1e-6,1e-5,2e-5,5e-5,1e-4]:
  def gamma(tt):
   nn,ww,HH,vv=np.moveaxis(f(tt),-1,0);q=q0*np.exp(-tt*du)*wp[0]/ww;return du*nn/(1+1/q**2)/HH
  def fun(t,y):V,X=y;return [-alpha*V-b*X,cc*V-gamma(t)*X]
  ref=solve_ivp(fun,(0,1),[1.,0.],rtol=1e-12,atol=1e-14,method='DOP853',dense_output=True,max_step=.005);assert ref.success
  def discrete(n):
   ts=np.linspace(0,1,n+1);dt=1/n;g=gamma((ts[1:]+ts[:-1])/2);assert min(g)>0;V=np.empty(n+1);X=np.empty(n+1);V[0]=1;X[0]=0
   for i,gg in enumerate(g):
    phi=np.exp(-gg*dt);p=-np.expm1(-gg*dt)/gg*cc/2
    # exact cell memory for midpoint-constant V; trapezoid V equation.
    V[i+1]=((1-alpha*dt/2-b*dt*p/2)*V[i]-b*dt*(1+phi)*X[i]/2)/(1+alpha*dt/2+b*dt*p/2)
    X[i+1]=phi*X[i]+p*(V[i]+V[i+1])
   # independent direct causal convolution sum using same cell representation.
   ex=np.exp(-g*dt);G=np.r_[0,np.cumsum(g*dt)];weights=-np.expm1(-g*dt)/g
   Xdirect=np.sum(np.exp(-(G[-1]-G[1:]))*weights*cc*(V[:-1]+V[1:])/2)
   assert abs(Xdirect-X[-1])<1e-11
   markov=np.exp(-np.sum((alpha+b*cc/g)*dt));return V[-1],X[-1],Xdirect,float(np.sum(g*dt)),markov
  a=discrete(256);b1=discrete(512);d=discrete(1024);target=ref.y[:,-1];err=np.linalg.norm(np.array(d[:2])-target);coarse=np.linalg.norm(np.array(b1[:2])-target);assert err<1e-5
  rows.append(dict(q0=q0,integrated_gamma=d[3],explicit=target.tolist(),memory_recursive=list(d[:2]),direct_convolution=d[2],refinement_error=float(err),previous_error=float(coarse),ratio=float(coarse/max(err,1e-300)),markov_local=d[4],markov_abs_error=float(abs(d[4]-target[0])),scope='diagnostic dimensionless alpha=.2,b=c=1, V0=1,X0=0; gamma from actual thermal history; no physical coupling inference'))
 out=dict(rows=rows,history_sha=sh,scope='exact finite auxiliary elimination on actual time-dependent damping; Markov closure compared at fixed diagnostic coupling, not derived kinetic scattering kernel')
 write('MEMORY.json',out);print(out,flush=True)
if __name__=='__main__':
 import sys
 if sys.argv[1]=='memory':memory()
 elif sys.argv[1]=='harmonic':
  rows=[]
  for name in ['fine_1024_129_32_8','fine_1024_129_32_16','fine_2048_129_32_8']:
   for l in ([4,6] if name=='fine_2048_129_32_8' else [4]):
    r=history(name,l);rows.append(r);write('HARMONIC.json',rows)
 else:raise ValueError(sys.argv[1])

