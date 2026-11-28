"""C4G fresh native larger-stencil source responses, work-based external density, and projected defect estimator."""
from pathlib import Path
import sys,os,subprocess,json,hashlib,concurrent.futures as cf,time,re,numpy as np,gzip,io
from scipy.interpolate import PchipInterpolator
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply
D=Path(__file__).resolve().parent;P=D.parent;R=D.parents[1];H=Path.home();F=P/'r118c4f_external_stress';SH=H/'r118c4g_native_scratch'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def native():
 SH.mkdir(exist_ok=False);binary=SH/'c4f_dg_bridge';data=gzip.decompress((F/'c4f_dg_bridge.gz').read_bytes());want=json.loads((F/'BUILD_ID.json').read_text())['binary_sha'];assert sha(data)==want;binary.write_bytes(data);binary.chmod(0o755)
 cfg=(F/'1024_4_base.cfg').read_text();x0=float(re.search(r'^initial_x_hii=(.*)$',cfg,re.M)[1]);T0=float(re.search(r'^initial_temperature_k=(.*)$',cfg,re.M)[1])
 cases=[(f'H_{e:g}',e,0.,0.,0.) for e in [-.02,.02]]+[(f'T_{e:g}',0.,0.,0.,e) for e in [-.02,.02]]+[(f'HeII_{e:g}',0.,e,0.,0.) for e in [2e-6,4e-6]]+[(f'HeIII_{e:g}',0.,0.,e,0.) for e in [2e-6,4e-6]]
 jobs=[(bins,n,*q) for bins,n in [(1024,4),(2048,2)] for q in cases]
 def job(q):
  bins,n,name,h,y,z,t=q;tag=f'{bins}_{n}_{name}';out=SH/tag;cp=SH/(tag+'.cfg');s=re.sub(r'^initial_x_hii=.*$',f'initial_x_hii={x0*(1+h):.17g}',cfg,flags=re.M);s=re.sub(r'^initial_temperature_k=.*$',f'initial_temperature_k={T0*(1+t):.17g}',s,flags=re.M);cp.write_text(s);(D/(tag+'.cfg')).write_text(s)
  args=[str(binary),str(cp),str(out),str(bins),'129','4',str(n),'19.99995','on','fine','mean',format(y,'.17g'),format(z,'.17g')];tm=time.monotonic();r=dict(tag=tag,args=args,binary_sha=want,config_sha=sha(s.encode()))
  with (D/(tag+'.log')).open('w') as f:
   try:r['exit']=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=220).returncode
   except subprocess.TimeoutExpired:r['exit']=124
  r['seconds']=time.monotonic()-tm
  if out.exists():
   for p in out.iterdir():
    if p.is_file():(D/(tag+'_'+p.name)).write_bytes(p.read_bytes())
  if r['exit']==0:
   hist=np.genfromtxt(out/'history.csv',names=True,delimiter=',');old=np.genfromtxt(F/f'{bins}_{n}_base_history.csv',names=True,delimiter=',');assert np.array_equal(hist['a'],old['a']) and len(hist)==n+1 and hist['accepted'][-1]==n
   assert 'status=COMPLETE' in (out/'RETURN.txt').read_text();r.update(ledger=float(max(abs(hist['ledger']))),gauss=float(max(abs(hist['gauss']))),source_sha=sha((out/'source.txt').read_bytes()),external_sha=sha((out/'external.csv').read_bytes()))
  print(tag,r['exit'],flush=True);return r
 rows=[]
 with cf.ThreadPoolExecutor(max_workers=4) as ex:
  for r in ex.map(job,jobs):rows.append(r);write('NATIVE_RUNS.json',rows)
 assert len(rows)==16 and all(x['exit']==0 for x in rows)
def work():
 ld=np.longdouble;rho0=ld(3)*ld(299792458)**2*ld('2.1842852410855023e-18')**2/(8*ld(str(np.pi))*ld('6.67430e-11'));fac0=ld('1.602176634e-19')/rho0
 keys=['Pxx','Pyy','Pzz','Pxy','Pxz','Pyz'];basis=np.zeros((5,3,3),ld);basis[0]=np.diag([1,-1,0])/np.sqrt(ld(2));basis[1]=np.diag([-1,-1,2])/np.sqrt(ld(6))
 for i,(j,k) in enumerate([(0,1),(0,2),(1,2)],2):basis[i,j,k]=basis[i,k,j]=1/np.sqrt(ld(2))
 def read(grid,name):
  p=D/f'{grid}_{name}_external.csv';p=p if p.exists() else F/p.name;ex=np.genfromtxt(p,names=True,delimiter=',',dtype=ld);fac=ex['nh_m3']*fac0
  def mat(prefix):
   M=np.zeros((len(ex),3,3),ld)
   for k,(i,j) in enumerate([(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]):M[:,i,j]=M[:,j,i]=ex[prefix+'_'+keys[k]]
   return M
  rad=mat('prim')+mat('cool')+mat('spec');tr=fac*(np.trace(rad,axis1=1,axis2=2)+2*ex['thermal']);pi=fac[:,None]*np.einsum('kij,nij->nk',basis,rad)
  stock=fac*(ex['primary']+ex['cool']+ex['spec']+ex['thermal']-ex['init_w']+ex['binding']-ex['init_b']-ex['source_u'])
  w=-fac*(ex['thermal_work']+ex['photon_work']+ex['boundary_u']+ex['secondary_work'])
  return ex['a'],np.c_[w,stock,tr,pi,ex['ne_m3']]
 rows=[];arr={}
 for grid in ['1024_4','2048_2']:
  a,b=read(grid,'base');u=np.log(a/a[0]).astype(float)
  for name in ['H','T','HeII','HeIII']:
   def val(k):
    z,x=read(grid,k);assert np.array_equal(z,a);return x
   if name in ['H','T']:
    d1=(val(name+'_0.01')-val(name+'_-0.01'))/ld('.02');d2=(val(name+'_0.02')-val(name+'_-0.02'))/ld('.04')
   else:
    d1=(4*(val(name+'_5e-07')-b)-(val(name+'_1e-06')-b))/ld('1e-6')
    d2=(4*(val(name+'_2e-06')-b)-(val(name+'_4e-06')-b))/ld('4e-6')
   z=np.load(F/f'{grid}_{name}_TANGENT.npz');cont=z['continuity_rho'].astype(ld);prior=json.loads((F/'FULL_EXTERNAL_TANGENT.json').read_text())
   dr=next(v for r in prior['rows'] if r['grid']==grid for v in r['directions'] if v['direction']==name)
   # Stable work coordinate is a finite-difference derivative of the exact accepted discrete ledger.
   out=dict(grid=grid,direction=name,work_small_end=float(d1[-1,0]),work_large_end=float(d2[-1,0]),stock_small_end=float(d1[-1,1]),stock_large_end=float(d2[-1,1]),pressure_trace_small_end=float(d1[-1,2]),pressure_trace_large_end=float(d2[-1,2]),STF_small_end=float(np.linalg.norm(d1[-1,3:8])),STF_large_end=float(np.linalg.norm(d2[-1,3:8])),work_small_continuity_max=float(max(abs(d1[:,0]-cont))),work_large_continuity_max=float(max(abs(d2[:,0]-cont))),stock_large_continuity_max=float(max(abs(d2[:,1]-cont))),work_stencil_relative=float(np.linalg.norm(d2[:,0]-d1[:,0])/max(np.linalg.norm(d1[:,0]),ld('1e-300'))),trace_stencil_relative=float(np.linalg.norm(d2[:,2]-d1[:,2])/max(np.linalg.norm(d1[:,2]),ld('1e-300'))),STF_stencil_relative=float(np.linalg.norm(d2[:,3:8]-d1[:,3:8])/max(np.linalg.norm(d1[:,3:8]),ld('1e-300'))))
   arr[grid+'_'+name+'_small']=d1;arr[grid+'_'+name+'_large']=d2;rows.append(out);print(out,flush=True)
  arr[grid+'_u']=u
 np.savez_compressed(D/'WORK_STENCILS.npz',**arr);write('WORK_STENCILS.json',dict(rows=rows,keys=['rho_work','rho_stock','pressure_trace','STF0','STF1','STF2','STF3','STF4','ne_m3'],scope='fresh actual native discrete response from independently recorded work, pressure and density, larger physical perturbation stencils; no AD or closed chemistry feedback'))
def geometry():
 old=(F/'rei.py').read_text();old=old[:old.index("g={'__file__'")];ns={'__file__':str(F/'rei.py'),'__name__':'inspect'};exec(compile(old,str(F/'rei.py'),'exec'),ns);src=ns['src']
 # Keep original measured base and source normalization. Larger actual stencils replace perturbation derivatives.
 src=src.replace("path=D/f'{grid}_{case}_{kind}.csv';b=path.read_bytes()","path=D/f'{grid}_{case}_{kind}.csv';path=path if path.exists() else D.parent/'r118c4f_external_stress'/path.name;b=path.read_bytes()")
 # C4F val() uses old ±0.01 / one-sided h=5e-7; keep as comparison. Load newly computed stable response.
 token="dtr_full=dv[:,0].astype(float);dpi=dv[:,1:6].astype(float);direct_dr=dv[:,6].astype(float);direct_owner_dr=dv[:,7].astype(float);dk_full=(dv[:,8]/ne0).astype(float)"
 new="""wz=np.load(D/'WORK_STENCILS.npz');assert np.allclose(wz[grid+'_u'],u,rtol=0,atol=1e-14)
   work=wz[grid+'_'+name+'_large'];dtr_full=work[:,2].astype(float);dpi=work[:,3:8].astype(float);direct_dr=work[:,0].astype(float);direct_owner_dr=work[:,1].astype(float);dk_full=(work[:,8]/ne0).astype(float)
   density=PchipInterpolator(u,direct_dr)"""
 assert src.count(token)==1;src=src.replace(token,new)
 src=src.replace("dr=hp*rr+drm+drg","dr=density(t)/scale+drm+drg")
 src=src.replace("f'{grid}_{name}_TANGENT.npz'","f'{grid}_{name}_WORK_TANGENT.npz'").replace("'FULL_EXTERNAL_TANGENT.json'","'WORK_CONSTRAINED_TANGENT.json'")
 src=src.replace("conditional Einstein/massive/primary tangent with actual full external stress response; no exact native discrete tangent or self-consistent chemistry feedback","conditional Einstein/massive/primary tangent with imposed native work density and actual larger-stencil stress; continuity evolved independently; no exact native discrete tangent or self-consistent chemistry feedback")
 src=src.replace("conditional continuous tangent with measured full native external pressure derivative, imposed gas response; direct density vs continuity diagnostic; no self-consistent rate feedback or exact discrete tangent","conditional continuous geometry response with prescribed native discrete work density; Gauss/dynamic disagreement diagnostic; not native discrete coupled tangent")
 g={'__file__':str(D/'rei.py'),'__name__':'prior'};exec(compile(src,'C4G_work_density','exec'),g);g['geometry']()
def adaptive():
 old=(F/'rei.py').read_text();old=old[:old.index("g={'__file__'")];ns={'__file__':str(F/'rei.py'),'__name__':'inspect'};exec(compile(old,str(F/'rei.py'),'exec'),ns);g={'__file__':str(D/'rei.py'),'__name__':'prior'};exec(compile(ns['src'],'C4F_owner','exec'),g)
 raw=g['blob'](g['XBASE'],'research/r118c3u_positive_owner/birth_1024_32ray/history.csv');h=np.genfromtxt(io.BytesIO(raw),names=True,delimiter=',');u=np.log(h['a']/h['a'][0]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);K=g['c']*g['SIG']*h['ne']*1e6/(g['H0']*h['h']);f=PchipInterpolator(u,np.c_[S,K],axis=0);ops,ident=g['operators'](6);m=49;N=3*m;I=np.eye(N,dtype=complex);C=csr_matrix(np.column_stack([g['collision'](I[:,i],m) for i in range(N)]));ops=[x.tocsr() for x in ops];p0=np.r_[0,np.arange(4,9),m+np.arange(4,25),2*m+np.arange(4,25)];p1=np.sort(np.r_[p0,np.arange(16,25)]);pp=[p0,p1,np.arange(N)]
 def obs(y):
  v=y.reshape(3,m);e=-.5*(v[1]+v[2]);b=.5j*(v[1]-v[2]);return [e[4:9],b[9:16],e[16:25]]
 def error(a,b):return max(float(np.linalg.norm(x-y)/max(np.linalg.norm(y),1e-32)) for x,y in zip(obs(a),obs(b)))
 def taylor(A,y,degree):
  z=y.copy();v=y.copy()
  for k in range(1,degree+1):v=A@v/k;z+=v
  return z
 def project(A,y,p):
  z=np.zeros(N,complex);z[p]=expm_multiply(A[p][:,p],y[p]);return z
 rows=[]
 for kfac in [1.,1e3,1e6]:
  for sfac in [1.,10.,100.]:
   for n in [32,64]:
    t=np.linspace(0,u[-1],n+1);base=np.zeros(N,complex);base[0]=g['Y00'];ref=base.copy();fixed=base.copy();ad=[base.copy(),base.copy()];cnt=[[0,0,0],[0,0,0]];tol=[1e-6,1e-8];under=[0,0];maxratio=[0.,0.];cost=[0,0]
    for l,r in zip(t[:-1],t[1:]):
     v=f((l+r)/2);A=(r-l)*(sum(sfac*x*op for x,op in zip(v[:5],ops))+kfac*v[5]*C)
     ref=expm_multiply(A,ref);fixed=project(A,fixed,p0)
     for j,tt in enumerate(tol):
      yy=ad[j];pred=taylor(A,yy,6);pred5=taylor(A,yy,5);tail=error(pred5,pred)
      choice=2;est=0.
      for k,p in enumerate(pp[:2]):
       z=np.zeros(N,complex);z[p]=taylor(A[p][:,p],yy[p],6);est=error(z,pred)+tail
       if est<=tt/n:choice=k;break
      # Decision is made before full expm_multiply; full is only used as independent audit.
      zz=project(A,yy,pp[choice]);audit=expm_multiply(A,yy);exact=error(zz,audit)
      if choice<2:
       under[j]+=int(exact>tt/n);maxratio[j]=max(maxratio[j],exact/max(est,1e-300))
      cnt[j][choice]+=1;cost[j]+=A[pp[choice]][:,pp[choice]].nnz;ad[j]=zz
    for j,tt in enumerate(tol):
     ob={name:dict(norm=float(np.linalg.norm(x)),adaptive_rel=float(np.linalg.norm(y-x)/max(np.linalg.norm(x),1e-32)),fixed48_rel=float(np.linalg.norm(z-x)/max(np.linalg.norm(x),1e-32))) for name,x,y,z in zip(['E2','B3','E4'],obs(ref),obs(ad[j]),obs(fixed))}
     rows.append(dict(opacity_scale=kfac,shear_scale=sfac,steps=n,local_tol=tt,chosen_counts=cnt[j],false_accepts=under[j],max_actual_to_estimate=maxratio[j],mean_retained=float(np.dot(cnt[j],[48,57,147])/n),selected_nnz_sum=cost[j],observables=ob))
    print('adaptive',kfac,sfac,n,flush=True)
 write('DEFECT_CLOSURE.json',dict(rows=rows,source_sha=g['sha'](raw),identity=ident,scope='6th-order sparse polynomial projected defect estimator; full exponential only used after decision for audit and fallback; not certified relative bound or measured speedup; prescribed C3U shape scaled'))
if __name__=='__main__':{'native':native,'work':work,'geometry':geometry,'adaptive':adaptive}[sys.argv[1]]()
