"""C4F full measured external stress conditional geometry and adaptive low-l closure diagnostic."""
from pathlib import Path
import numpy as np,json,sys,hashlib,subprocess,io
from scipy.linalg import expm
from scipy.interpolate import PchipInterpolator
D=Path(__file__).resolve().parent;P=D.parent;E=P/'r118c4e_signed_geometry';C4=P/'r118c4d_refined_jacobian'
src=(E/'rei.py').read_text();src=src[:src.index('\ndef regime():')]
def rep(a,b):
 global src
 assert src.count(a)==1,(a,src.count(a));src=src.replace(a,b)
rep("path=C4/f'{grid}_{case}_{kind}.csv';b=path.read_bytes();assert b==blob(BASE,'research/r118c4d_refined_jacobian/'+path.name);hashes[path.name]=sha(b);return np.genfromtxt(io.BytesIO(b),names=True,delimiter=',')","path=D/f'{grid}_{case}_{kind}.csv';b=path.read_bytes();hashes[path.name]=sha(b);return np.genfromtxt(io.BytesIO(b),names=True,delimiter=',',dtype=np.longdouble if kind=='external' else float)")
rep("pex=P0-pm-pg;rex=p['rho']-rm-rg;trace=fac*(h['primary']+h['cool']+h['spec']+2*h['thermal'])","""ext=read('base','external');assert np.array_equal(ext['a'].astype(float),a)
  keys=['Pxx','Pyy','Pzz','Pxy','Pxz','Pyz']
  def component(ex,prefix):return matrow(ex,[prefix+'_'+k for k in keys])
  def physical(ex):
   pp=component(ex,'prim');pc=component(ex,'cool');pd=component(ex,'spec');w=ex['thermal'];fac0=ex['nh_m3']*electron_volt/RHO0
   P=pp+pc+pd+2*w[:,None,None]*np.eye(3)/3
   # STF from radiation pieces only, so gas isotropic pressure cancels exactly.
   def st(M):return np.einsum('kij,nij->nk',B.astype(np.longdouble),M)
   return fac0*np.trace(P,axis1=1,axis2=2),fac0[:,None]*(st(pp)+st(pc)+st(pd)),ex['rho_stable'],ex['rho_owner'],ex['ne_m3']
  trace0,pi0,rho0,rho_owner,ne0=physical(ext)
  pex=component(ext,'owner').astype(float);rex=rho0.astype(float);trace=trace0.astype(float)
  direct_stf=pi0.astype(float)
  raw_trace=fac*(h['primary']+h['cool']+h['spec']+2*h['thermal'])
  direct_trace_error=float(max(abs(raw_trace-trace)))
  stock_ledger=ext['primary']+ext['cool']+ext['spec']+(ext['thermal']-ext['init_w'])+(ext['binding']-ext['init_b'])-ext['source_u']+ext['thermal_work']+ext['photon_work']+ext['boundary_u']+ext['secondary_work']
  owner_stable_gap=float(max(abs(rho0-rho_owner)))""")
rep("stf(pex),J.reshape(len(u),-1)","direct_stf,J.reshape(len(u),-1)")
rep("np.c_[trace,stf(pex),S]","np.c_[trace,direct_stf,S]")
rep("dpi=stf(dC)*fac[:,None];source=PchipInterpolator(u,np.c_[dtr,dpi,dk],axis=0)","""corr_dpi=stf(dC)*fac[:,None]
   def evec(k):
    ex=read(k,'external');assert np.array_equal(ex['a'].astype(float),a);v=physical(ex)
    return np.column_stack([v[0],v[1],v[2],v[3],v[4]])
   v0=evec('base')
   if name in ['H','T']:dv=(evec(name+'_0.01')-evec(name+'_-0.01'))/np.longdouble('.02')
   else:
    v1=evec(name+'_5e-07');v2=evec(name+'_1e-06')
    # Difference first, avoiding subtracting three large baseline terms.
    dv=(4*(v1-v0)-(v2-v0))/np.longdouble('1e-6')
   dtr_full=dv[:,0].astype(float);dpi=dv[:,1:6].astype(float);direct_dr=dv[:,6].astype(float);direct_owner_dr=dv[:,7].astype(float);dk_full=(dv[:,8]/ne0).astype(float)
   trace_diff=float(np.max(abs(dtr_full-dtr)))
   opacity_diff=float(np.max(abs(dk_full-dk)))
   dtr=dtr_full;dk=dk_full;source=PchipInterpolator(u,np.c_[dtr,dpi,dk],axis=0)""")
rep("r=dict(grid=grid,direction=name,source_scale=scale,","""continuity_dr=hp*xf[:,6].real*scale
   refold=json.loads((D.parent/'r118c4e_signed_geometry/SIGNED_GEOMETRY.json').read_text())
   previous=next(x for rr in refold['rows'] if rr['grid']==grid for x in rr['directions'] if x['direction']==name)
   r=dict(grid=grid,direction=name,source_scale=scale,full_stf_end=float(np.linalg.norm(dpi[-1])),collision_only_stf_end=float(np.linalg.norm(corr_dpi[-1])),stf_difference_end=float(np.linalg.norm(dpi[-1]-corr_dpi[-1])),direct_rho_derivative_end=float(direct_dr[-1]),continuity_rho_derivative_end=float(continuity_dr[-1]),direct_vs_continuity_rho_max=float(max(abs(direct_dr-continuity_dr))),direct_owner_vs_stable_rho_max=float(max(abs(direct_dr-direct_owner_dr))),trace_derivative_check=trace_diff,opacity_derivative_check=opacity_diff,prior_conditional_shear_norm=previous['delta_shear_norm'],prior_conditional_lnh=previous['delta_lnh_constraint'],""")
rep("scope='conditional continuous tangent with imposed native gas and radiation trace response, known collision STF; excludes other external anisotropic derivatives and self-consistent chemistry feedback'","scope='conditional continuous tangent with measured full native external pressure derivative, imposed gas response; direct density vs continuity diagnostic; no self-consistent rate feedback or exact discrete tangent'")
rep("source_stf=dpi,opacity_fraction=dk)","source_stf=dpi,collision_stf=corr_dpi,opacity_fraction=dk,direct_rho=direct_dr,continuity_rho=continuity_dr)")
rep("base_external_density_subtraction_max=float(max(abs(rex))),directions=errors","base_external_density_max=float(max(abs(rex))),base_external_direct_trace_error=direct_trace_error,base_external_stock_ledger_max=float(max(abs(stock_ledger))),base_owner_vs_stable_rho_max=owner_stable_gap,directions=errors")
rep("write('SIGNED_GEOMETRY.json',dict(rows=rows,scope='conditional geometry/primary/massive coupled tangent, actual native gas derivative imposed; not complete native discrete Jacobian; omitted primary/cooling/secondary noncollision STF derivative'))","write('FULL_EXTERNAL_TANGENT.json',dict(rows=rows,scope='conditional Einstein/massive/primary tangent with actual full external stress response; no exact native discrete tangent or self-consistent chemistry feedback'))")
g={'__file__':str(D/'rei.py'),'__name__':'prior'};exec(compile(src,'C4E_full_external_tangent','exec'),g)
def adaptive():
 raw=g['blob'](g['XBASE'],'research/r118c3u_positive_owner/birth_1024_32ray/history.csv');h=np.genfromtxt(io.BytesIO(raw),names=True,delimiter=',');u=np.log(h['a']/h['a'][0]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);K=g['c']*g['SIG']*h['ne']*1e6/(g['H0']*h['h']);f=PchipInterpolator(u,np.c_[S,K],axis=0);ops,ident=g['operators'](6);m=49;N=3*m;I=np.eye(N,dtype=complex);C=np.column_stack([g['collision'](I[:,i],m) for i in range(N)]);L0=np.array([x.toarray() for x in ops])
 p0=np.r_[0,np.arange(4,9),m+np.arange(4,25),2*m+np.arange(4,25)];p1=np.sort(np.r_[p0,np.arange(16,25)]);p2=np.arange(N)
 def obs(y):
  v=y.reshape(3,m);e=-.5*(v[1]+v[2]);b=.5j*(v[1]-v[2]);return [e[4:9],b[9:16],e[16:25]]
 def delta(a,b):return max(float(np.linalg.norm(x-y)/max(np.linalg.norm(y),1e-32)) for x,y in zip(obs(a),obs(b)))
 def evolve(A,dt,y,p):
  z=np.zeros(N,complex);z[p]=expm(dt*A[np.ix_(p,p)])@y[p];return z
 rows=[]
 for kfac in [1.,1e3,1e6]:
  for sfac in [1.,10.,100.]:
   for n in [32,64]:
    t=np.linspace(0,u[-1],n+1);base=np.zeros(N,complex);base[0]=g['Y00'];ref=base.copy();fixed=[base.copy(),base.copy()];tol=[1e-6,1e-8];ad=[base.copy(),base.copy()];count=[[0,0,0],[0,0,0]];maxstep=[0.,0.]
    for l,r in zip(t[:-1],t[1:]):
     v=f((l+r)/2);A=sfac*np.einsum('k,kij->ij',v[:5],L0)+kfac*v[5]*C;dt=r-l;E0=expm(dt*A[np.ix_(p0,p0)]);E1=expm(dt*A[np.ix_(p1,p1)]);E2=expm(dt*A)
     def prop(y,p,E):
      z=np.zeros(N,complex);z[p]=E@y[p];return z
     ref=E2@ref;fixed=[prop(fixed[0],p0,E0),prop(fixed[1],p1,E1)]
     for j,tt in enumerate(tol):
      yy=ad[j];z0=prop(yy,p0,E0);z1=prop(yy,p1,E1);z2=E2@yy
      # Embedded nested propagation estimator; full used as comparison/fallback, not a speed claim.
      err0=delta(z0,z1);err1=delta(z1,z2);err02=delta(z0,z2)
      if err0+err1<=tt/n and err02<=tt/n:k=0;z=z0
      elif err1<=tt/n:k=1;z=z1
      else:k=2;z=z2
      count[j][k]+=1;ad[j]=z;maxstep[j]=max(maxstep[j],min(err02,err1) if k<2 else 0.)
    for j,tt in enumerate(tol):
     ob={name:dict(norm=float(np.linalg.norm(x)),adaptive_rel=float(np.linalg.norm(y-x)/max(np.linalg.norm(x),1e-32)),fixed48_rel=float(np.linalg.norm(a-x)/max(np.linalg.norm(x),1e-32)),fixed57_rel=float(np.linalg.norm(b-x)/max(np.linalg.norm(x),1e-32))) for name,x,y,a,b in zip(['E2','B3','E4'],obs(ref),obs(ad[j]),obs(fixed[0]),obs(fixed[1]))}
     rows.append(dict(opacity_scale=kfac,shear_scale=sfac,steps=n,local_tol=tt,chosen_counts=count[j],mean_retained=float(np.dot(count[j],[len(p0),len(p1),N])/n),max_local_estimator=maxstep[j],tau=float(kfac*np.trapezoid(K,u)),shear_path=float(sfac*np.trapezoid(np.linalg.norm(S,axis=1),u)),observables=ob))
    print('adaptive',kfac,sfac,n,flush=True)
 g['write']('ADAPTIVE_CLOSURE.json',dict(rows=rows,history_sha=g['sha'](raw),identity=ident,dimensions=[len(p0),len(p1),N],scope='nested embedded full lmax6 reference/fallback used at every step; scientific retained-mode diagnostic, not speedup or certified bound, prescribed scaled histories not self-consistent cosmologies'))
if __name__=='__main__':{'geometry':g['geometry'],'adaptive':adaptive}[sys.argv[1]]()
