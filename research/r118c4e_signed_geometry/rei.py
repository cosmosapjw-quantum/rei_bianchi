"""Signed constrained Einstein response using actual native material histories; conditional external tensor."""
from pathlib import Path
import numpy as np,json,sys,hashlib,subprocess,io,time
from scipy.constants import c,G,electron_volt
from scipy.interpolate import PchipInterpolator
from scipy.integrate import solve_ivp,quad_vec
from scipy.linalg import expm
D=Path(__file__).resolve().parent;R=D.parents[1];P=D.parent;C4=P/'r118c4d_refined_jacobian';BASE='7695ed8f7d5243c85ecd7a0a335b93fad70a8271';ZBASE='32d0724ae284a10b5e77377055c2b984e12180c2';XBASE='0e624af4668c7722759ccf781d91e15362b6d451'
def blob(rev,p):return subprocess.check_output(['git','-C',str(R),'show',rev+':'+p])
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
gsrc=blob(ZBASE,'research/r118c3z_harmonic_memory/rei.py');g={'__file__':str(D/'prior_generator.py'),'__name__':'prior'};exec(compile(gsrc,'C3Z/rei.py','exec'),g)
msrc=blob(ZBASE,'research/r118c3y_material_jacobian/material.py');m0={'__file__':str(D/'prior_material.py'),'__name__':'prior'};exec(compile(msrc,'C3Y/material.py','exec'),m0)
B,stf,mat,matrow,photon,operators,collision=[g[k] for k in ['B','stf','mat','matrix','photon','operators','collision']];H0,RHO0,OL,OG,FHE,SIG,Y00=[g[k] for k in ['H0','RHO0','OL','OG','FHE','SIG','Y00']]
def geometry():
 rows=[]
 for grid in ['1024_4','2048_2']:
  hashes={}
  def read(case,kind='history'):
   path=C4/f'{grid}_{case}_{kind}.csv';b=path.read_bytes();assert b==blob(BASE,'research/r118c4d_refined_jacobian/'+path.name);hashes[path.name]=sha(b);return np.genfromtxt(io.BytesIO(b),names=True,delimiter=',')
  h=read('base');p=read('base','matter');a=h['a'];assert np.array_equal(a,p['a']);u=np.log(a/a[0]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);P0=matrow(p,['Pxx','Pyy','Pzz','Pxy','Pxz','Pyz']);F=np.stack([p[f'F{i}{j}'] for i in range(3) for j in range(3)],axis=-1).reshape(-1,3,3);fac=p['nh_m3']*electron_volt/RHO0;K=c*SIG*p['ne_m3']/(H0*h['h'])
  rm=[];pm=[];J=[]
  for aa,ff in zip(a,F):
   r,pp=m0['matter'](aa,ff);rm.append(r+m0['COLD']/aa**3);pm.append(pp)
   j=[]
   for A in np.eye(9).reshape(9,3,3):
    dr,dP=m0['matter'](aa,ff,A);assert abs(dr+np.sum(A*pp))<1e-10
    j.append(np.r_[dr,dP.ravel()])
   J.append(np.array(j).T)
  rm,pm,J=np.array(rm),np.array(pm),np.array(J);ops,ident=operators(6);m=49;bg=PchipInterpolator(u,np.c_[S,K],axis=0)
  def Lop(s,y):return sum(x*(op@y) for x,op in zip(s,ops))
  y0=np.zeros(3*m,complex);y0[0]=Y00
  def fun(t,y):
   r=bg(t);return Lop(r[:5],y)+r[5]*collision(y,m)
  yy=solve_ivp(fun,(0,u[-1]),y0,dense_output=True,rtol=2e-13,atol=1e-19,max_step=max(np.diff(u))/8,method='DOP853');assert yy.success
  mom=[photon(yy.sol(t),aa,m) for t,aa in zip(u,a)];rg=np.array([x[0] for x in mom]);pg=np.array([x[1] for x in mom]);pex=P0-pm-pg;rex=p['rho']-rm-rg;trace=fac*(h['primary']+h['cool']+h['spec']+2*h['thermal'])
  trace_error=float(max(abs(np.trace(pex,axis1=1,axis2=2)-trace)))
  ic_r=float(abs(rm[0]+rg[0]-p['rho'][0]));assert ic_r/max(abs(p['rho'][0]),1e-300)<1e-10
  # Actual native raw history, reconstructed source trace and native collision STF; no other STF derivative claimed.
  base_cols=['primary','cool','spec','thermal','binding','xHII','xHeII','xHeIII','corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz','h','S0','S1','S2','S3','S4']
  def val(name):
   q=read(name);assert np.array_equal(q['a'],a);return np.stack([q[k] for k in base_cols],axis=1)
  v0=val('base');jac={}
  for k in ['H','T']:jac[k]=(val(k+'_0.01')-val(k+'_-0.01'))/.02
  for k in ['HeII','HeIII']:jac[k]=(-3*v0+4*val(k+'_5e-07')-val(k+'_1e-06'))/1e-6
  q=S.__class__ if False else np.sum(S*S,axis=1)/3+(p['rho']+np.trace(P0,axis1=1,axis2=2)-2*OL)/(2*h['h']**2)
  base=PchipInterpolator(u,np.c_[S,h['h'],p['rho'],P0.reshape(-1,9),stf(pex),J.reshape(len(u),-1),K,fac],axis=0)
  # Baseline continuity audit: subtracting large background moments can lose the small external density.
  ff=PchipInterpolator(u,np.c_[trace,stf(pex),S],axis=0)
  ref=solve_ivp(lambda t,z:np.array([-3*z[0]-ff(t)[0]-ff(t)[1:6]@ff(t)[6:11]]),(0,u[-1]),[rex[0]],t_eval=u,rtol=1e-12,atol=1e-18,max_step=max(np.diff(u))/4,method='DOP853');assert ref.success
  errors=[]
  for name,j in jac.items():
   dtr=fac*(j[:,0]+j[:,1]+j[:,2]+2*j[:,3]);dne= p['nh_m3']*(j[:,5]+FHE*(j[:,6]+2*j[:,7]));dk=dne/p['ne_m3'];dC=np.zeros((len(u),3,3))
   for k,(i,l) in enumerate([(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]):dC[:,i,l]=dC[:,l,i]=j[:,8+k]
   dpi=stf(dC)*fac[:,None];source=PchipInterpolator(u,np.c_[dtr,dpi,dk],axis=0)
   # Common scaling avoids absolute-tolerance loss of tiny geometry response; physical numbers recovered at output.
   scale=max(float(np.max(abs(dtr))/h['h'][0]**2),float(np.max(abs(dpi))/h['h'][0]**2),float(np.max(abs(K*dk)))*1e-7,1e-300);hp=h['h'][0]**2
   def terms(t,y,algebraic):
    r=base(t);s=r[:5];hh,rho=r[5:7];pt=r[7:16].reshape(3,3);pix=r[16:21];jj=r[21:111].reshape(10,9);kk=r[111];fd=source(t)/scale;ds=y[:5].real;dl=y[5].real;rr=y[6].real;A=y[7:16].real.reshape(3,3);Z=y[16:]
    mt=jj@A.ravel();drm=mt[0];dpm=mt[1:].reshape(3,3);drg,dpg=photon(Z,a[0]*np.exp(t),m);dr=hp*rr+drm+drg
    dP_trace=fd[0]+np.trace(dpm)+drg;dpi_all=fd[1:6]+stf(dpm+dpg);pi=stf(pt)
    la=(dr/hh**2+s@ds/3)/(2*(1-s@s/6))
    use=la if algebraic else dl
    q=s@s/3+(rho+np.trace(pt)-2*OL)/(2*hh**2)
    dq=2*s@ds/3+(dr+dP_trace)/(2*hh**2)-(rho+np.trace(pt)-2*OL)*use/hh**2
    dds=(q-2)*ds+dq*s+3*(dpi_all-2*pi*use)/hh**2
    AA=mat(s);dA=mat(ds)+AA@A-A@AA
    drr=-3*rr-(fd[0]+ds@pix+s@fd[1:6])/hp
    Y=yy.sol(t);dZ=Lop(s,Z)+kk*collision(Z,m)+Lop(ds,Y)+kk*(fd[6]-use)*collision(Y,m)
    return np.r_[dds,-dq,drr,dA.ravel(),dZ],la
   def solve(algebraic,ref):
    z=solve_ivp(lambda t,y:terms(t,y,algebraic)[0],(0,u[-1]),np.zeros(16+3*m,complex),t_eval=u,rtol=2e-12/ref,atol=1e-21/ref,max_step=max(np.diff(u))/ref,method='DOP853');assert z.success
    la=np.array([terms(t,y,algebraic)[1] for t,y in zip(u,z.y.T)])
    return z.y.T,la
   x,la=solve(True,4);xf,laf=solve(True,8);v,lv=solve(False,8);den=max(np.linalg.norm(xf[-1,:16]),1e-300)
   # use algebraic lnH as physical; independently integrate lnH'=-delta q.
   consistency=float(np.max(abs(xf[:,5].real-laf))*scale);dyn_constraint=float(np.max(abs(v[:,5].real-lv))*scale)
   r=dict(grid=grid,direction=name,source_scale=scale,delta_shear_norm=float(np.linalg.norm(xf[-1,:5])*scale),delta_lnh_constraint=float(laf[-1]*scale),delta_lnh_dynamic=float(v[-1,5].real*scale),lnh_consistency_abs=consistency,dynamic_constraint_abs=dyn_constraint,geometry_relative_between_formulations=float(np.linalg.norm(xf[-1,:16]-v[-1,:16])/den),solver_geometry_relative=float(np.linalg.norm(xf[-1,:16]-x[-1,:16])/den),coframe_trace_abs=float(max(abs(np.trace(xf[:,7:16].real.reshape(-1,3,3),axis1=1,axis2=2)))*scale),primary_tangent_norm=float(np.linalg.norm(xf[-1,16:])*scale),source_trace_derivative_end=float(dtr[-1]),collision_stf_derivative_end=float(np.linalg.norm(dpi[-1])),native_h_FD=float(j[-1,14]/h['h'][-1]),native_shear_FD_norm=float(np.linalg.norm(j[-1,15:20])),native_h_floor=float(np.spacing(h['h'][-1])/h['h'][-1]),scope='conditional continuous tangent with imposed native gas and radiation trace response, known collision STF; excludes other external anisotropic derivatives and self-consistent chemistry feedback')
   np.savez_compressed(D/f'{grid}_{name}_TANGENT.npz',u=u,algebraic=xf*scale,dynamic=v*scale,lnh_constraint=laf*scale,lnh_dynamic_constraint=lv*scale,source_trace=dtr,source_stf=dpi,opacity_fraction=dk)
   errors.append(r);print(r,flush=True)
  rows.append(dict(grid=grid,history_hashes=hashes,identity=ident,source_module_hashes=[sha(gsrc),sha(msrc)],initial_density_abs=ic_r,base_external_trace_reconstruction_abs=trace_error,base_external_continuity_abs=float(max(abs(ref.y[0]-rex))),base_external_density_subtraction_max=float(max(abs(rex))),directions=errors))
 write('SIGNED_GEOMETRY.json',dict(rows=rows,scope='conditional geometry/primary/massive coupled tangent, actual native gas derivative imposed; not complete native discrete Jacobian; omitted primary/cooling/secondary noncollision STF derivative'))
def regime():
 raw=blob(XBASE,'research/r118c3u_positive_owner/birth_1024_32ray/history.csv');h=np.genfromtxt(io.BytesIO(raw),names=True,delimiter=',');u=np.log(h['a']/h['a'][0]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);K=c*SIG*h['ne']*1e6/(H0*h['h']);f=PchipInterpolator(u,np.c_[S,K],axis=0);ops,ident=operators(6);m=49;N=3*m;I=np.eye(N,dtype=complex);C=np.column_stack([collision(I[:,i],m) for i in range(N)]);L0=np.array([x.toarray() for x in ops])
 def eb(y):
  v=y.reshape(3,m);return -.5*(v[1]+v[2]),.5j*(v[1]-v[2])
 rows=[]
 for kfac in [1.,1e3,1e6]:
  for sfac in [1.,10.,100.]:
   for n in [32,64]:
    t=np.linspace(0,u[-1],n+1);y=np.zeros(N,complex);y[0]=Y00;states={}
    for tag,ip in [('I0I2_pol234',np.r_[0,np.arange(4,9)]),('I0I2I4_pol234',np.r_[0,np.arange(4,9),np.arange(16,25)])]:
     p=np.r_[ip,m+np.arange(4,25),2*m+np.arange(4,25)];states[tag]=dict(p=p,local=y[p].copy(),cell=y[p].copy())
    for l,r in zip(t[:-1],t[1:]):
     v=f((l+r)/2);A=sfac*np.einsum('k,kij->ij',v[:5],L0)+kfac*v[5]*C;E=expm((r-l)*A);y=E@y
     for z in states.values():
      p=z['p'];z['local']=expm((r-l)*A[np.ix_(p,p)])@z['local'];z['cell']=E[np.ix_(p,p)]@z['cell']
    for tag,z in states.items():
     out={};p=z['p'];ys={}
     for k in ['local','cell']:
      q=np.zeros(N,complex);q[p]=z[k];ys[k]=q
     for name,sl in [('E2',slice(4,9)),('B3',slice(9,16)),('E4',slice(16,25))]:
      k=int(name[0]=='B');x=eb(y)[k][sl];norm=float(np.linalg.norm(x));out[name]=dict(norm=norm,**{k0+'_rel':float(np.linalg.norm(eb(v)[k][sl]-x)/max(norm,1e-300)) for k0,v in ys.items()},**{k0+'_abs':float(np.linalg.norm(eb(v)[k][sl]-x)) for k0,v in ys.items()})
     rows.append(dict(opacity_scale=kfac,shear_scale=sfac,steps=n,retained=tag,tau=float(kfac*np.trapezoid(K,u)),shear_path=float(sfac*np.trapezoid(np.linalg.norm(S,axis=1),u)),observables=out))
    print('regime',kfac,sfac,n,flush=True)
 write('CLOSURE_REGIME.json',dict(rows=rows,history_sha256=sha(raw),generator_identity=ident,scope='diagnostic scaled prescribed history, not self-consistent alternative cosmology; finite lmax6 closure accuracy vs optical depth and integrated shear'))
if __name__=='__main__':{'geometry':geometry,'regime':regime}[sys.argv[1]]()
