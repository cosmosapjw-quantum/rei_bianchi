"""Exact restored C4C DG3 executable: gas-coordinate Jacobian refinement and source-only tangent."""
from pathlib import Path
import sys,subprocess,hashlib,json,gzip,io,os,time,concurrent.futures as cf,re,numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.linalg import expm
from scipy.integrate import solve_ivp,quad_vec
from scipy.constants import c,G,electron_volt
D=Path(__file__).resolve().parent;R=D.parents[1];P=D.parent;HOME=Path.home();SH=HOME/'r118c4d_dg_scratch';C3=P/'r118c4c_dg3_gas_jacobian';BASE='112a133a423877bb46e0c766e158819c7e14929f';XBASE='0e624af4668c7722759ccf781d91e15362b6d451';X='research/r118c3x_tangent_source';ZBASE='32d0724ae284a10b5e77377055c2b984e12180c2'
def blob(rev,p):return subprocess.check_output(['git','-C',str(R),'show',rev+':'+p])
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def native():
 prefix='research/r118c4c_dg3_gas_jacobian/';bid=json.loads(blob(BASE,prefix+'BUILD_ID.json'));arc=blob(BASE,prefix+'c4c_dg_bridge.gz');raw=gzip.decompress(arc);assert sha(raw)==bid['binary_sha'] and len(raw)==bid['binary_bytes']
 SH.mkdir(exist_ok=False);b=SH/'c4c_dg_bridge';b.write_bytes(raw);b.chmod(0o700)
 cfg=blob(BASE,prefix+'BASE.cfg').decode();(D/'BASE.cfg').write_text(cfg);x0=float(re.search(r'^initial_x_hii=(.*)$',cfg,re.M)[1]);T0=float(re.search(r'^initial_temperature_k=(.*)$',cfg,re.M)[1])
 write('BINARY_ID.json',dict(pinned=BASE,binary_sha256=sha(raw),gzip_sha256=sha(arc),cfg_sha256=sha(cfg.encode()),source_sha_expected='cd68c54d5cd560f32018ffa786bc5532be128f02ef6022686075c6ab6f215260',scope='exact C4C research shadow binary, no production mutation or rebuild'))
 cases=[('base',0.,0.,0.,0.)]+[(f'H_{e:g}',e,0.,0.,0.) for e in [-.01,.01]]+[(f'T_{e:g}',0.,0.,0.,e) for e in [-.01,.01]]+[(f'HeII_{e:g}',0.,e,0.,0.) for e in [5e-7,1e-6]]+[(f'HeIII_{e:g}',0.,0.,e,0.) for e in [5e-7,1e-6]]
 jobs=[(bins,n,*q) for bins,n in [(1024,4),(2048,2)] for q in cases];root=SH/'runs';root.mkdir()
 def job(q):
  bins,n,name,h,y,z,t=q;tag=f'{bins}_{n}_{name}';out=root/tag;config=root/(tag+'.cfg')
  s=re.sub(r'^initial_x_hii=.*$',f'initial_x_hii={x0*(1+h):.17g}',cfg,flags=re.M);s=re.sub(r'^initial_temperature_k=.*$',f'initial_temperature_k={T0*(1+t):.17g}',s,flags=re.M);config.write_text(s);(D/(tag+'.cfg')).write_text(s)
  args=[str(b),str(config),str(out),str(bins),'129','4',str(n),'19.99995','on','fine','mean',format(y,'.17g'),format(z,'.17g')]
  t0=time.monotonic();r=dict(case=tag,grid=f'{bins}_{n}',name=name,perturb=[h,y,z,t],command=args,config_sha256=sha(s.encode()))
  try:
   with (D/(tag+'.log')).open('w') as f:a=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=220)
   r['exit']=a.returncode
  except subprocess.TimeoutExpired:r['exit']=124
  r['seconds']=time.monotonic()-t0
  if out.exists():
   for k in ['history.csv','matter.csv','stock.csv','RETURN.txt']:
    p=out/k
    if p.exists():(D/(tag+'_'+k)).write_bytes(p.read_bytes())
  if r['exit']==0:
   v=np.genfromtxt(out/'history.csv',names=True,delimiter=',');assert len(v)==n+1 and int(v['accepted'][-1])==n and 'status=COMPLETE' in (out/'RETURN.txt').read_text()
   source=sha((out/'source.txt').read_bytes());assert source=='cd68c54d5cd560f32018ffa786bc5532be128f02ef6022686075c6ab6f215260'
   r.update(source_sha=source,accepted=n,ledger=float(max(abs(v['ledger']))),gauss=float(max(abs(v['gauss']))),metric=float(max(v['metric'])),margin=float(min(v['margin'])),terminal={k:float(v[k][-1]) for k in v.dtype.names})
  print(tag,r['exit'],r.get('ledger'),flush=True);return r
 rows=[]
 with cf.ThreadPoolExecutor(max_workers=4) as ex:
  for r in ex.map(job,jobs):rows.append(r);write('NATIVE_RUNS.json',rows)
def analyze():
 rows=json.loads((D/'NATIVE_RUNS.json').read_text());old=json.loads((C3/'JACOBIAN.json').read_text());keys=old['keys'];res={}
 H0=2.1842852410855023e-18;RHO0=3*c*c*H0*H0/(8*np.pi*G);OL=.684908
 # Exact STF convention of C3Z native generator.
 BB=np.zeros((5,3,3));BB[0]=np.diag([1,-1,0])/np.sqrt(2);BB[1]=np.diag([-1,-1,2])/np.sqrt(6)
 for k,(i,j) in enumerate([(0,1),(0,2),(1,2)],2):BB[k,i,j]=BB[k,j,i]=1/np.sqrt(2)
 def read(g,name,kind='history'):return np.genfromtxt(D/f'{g}_{name}_{kind}.csv',names=True,delimiter=',')
 for g in ['1024_4','2048_2']:
  good={r['name'] for r in rows if r['grid']==g and r['exit']==0}
  if 'base' not in good:continue
  base=read(g,'base');matter=read(g,'base','matter');u=np.log(base['a']/base['a'][0]);s=np.stack([base[f'S{i}'] for i in range(5)],axis=1)
  q=np.sum(s*s,axis=1)/3+(matter['rho']+matter['Pxx']+matter['Pyy']+matter['Pzz']-2*OL)/(2*base['h']**2)
  def vals(name):
   z=read(g,name);assert np.array_equal(z['a'],base['a']);return np.stack([z[k] for k in keys],axis=1)
  v0=vals('base');J={}
  for name in ['H','T']:
   a,b=name+'_-0.01',name+'_0.01'
   if {a,b}<=good:J[name]=(vals(b)-vals(a))/.02
  for name in ['HeII','HeIII']:
   a,b=name+'_5e-07',name+'_1e-06'
   if {a,b}<=good:J[name]=(-3*v0+4*vals(a)-vals(b))/1e-6
  # Independent source-only shear response to actual collision pressure derivative;
  # frozen q,H and omitted other material response. No full Einstein tangent claim.
  tan={};qp=PchipInterpolator(u,q-2)
  for name,j in J.items():
   z=np.zeros((len(u),3,3))
   for key,(a,b) in zip(['corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz'],[(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]):z[:,a,b]=z[:,b,a]=j[:,keys.index(key)]
   force=3*np.einsum('kij,tij->tk',BB,z)*matter['nh_m3'][:,None]*electron_volt/(RHO0*base['h'][:,None]**2)
   fs=float(np.max(np.linalg.norm(force,axis=1)))
   if fs==0:continue
   ff=PchipInterpolator(u,force/fs);zz=solve_ivp(lambda t,v:qp(t)*v+ff(t),(u[0],u[-1]),np.zeros(5),rtol=1e-12,atol=1e-15,max_step=max(np.diff(u))/4,method='DOP853');assert zz.success
   exact=quad_vec(lambda t:np.exp(qp.integrate(t,u[-1]))*ff(t),u[0],u[-1],epsabs=1e-17,epsrel=1e-11,points=u[1:-1])[0];er=float(np.linalg.norm(zz.y[:,-1]-exact)/max(np.linalg.norm(exact),1e-300))
   tan[name]=dict(forcing_scale=fs,terminal_shear_norm=float(np.linalg.norm(exact)*fs),quad_ode_relative=er,native_shear_derivative_norm=float(np.linalg.norm(j[-1,[keys.index(f'S{i}') for i in range(5)]])),scope='conditional frozen q,H source-only secondary collision pressure; excludes full matter and geometry feedback')
  comparisons={}
  for name,j in J.items():
   a=np.array(old['columns'][name]);b=j[-1];comparisons[name]=dict(absolute=abs(b-a).tolist(),relative=(abs(b-a)/np.maximum(abs(b),1e-300)).tolist())
  res[g]=dict(columns={k:v[-1].tolist() for k,v in J.items()},comparison_C4C=comparisons,source_only_tangent=tan,base_terminal={k:float(base[k][-1]) for k in keys})
  if J:np.savez_compressed(D/f'{g}_JACOBIAN_HISTORY.npz',u=u,keys=np.array(keys),**J)
 out=dict(keys=keys,grid_results=res,native_cases=len(rows),native_complete=sum(x['exit']==0 for x in rows),max_ledger=max((x['ledger'] for x in rows if x['exit']==0),default=None),max_gauss=max((x['gauss'] for x in rows if x['exit']==0),default=None),scope='actual discrete initial gas Jacobian refinement, separate source-only conditional shear response; not full tangent of geometry, photon spectrum or nonlinear continuum')
 write('REFINED_JACOBIAN.json',out);print(out,flush=True)
def closure():
 old=blob(ZBASE,'research/r118c3z_harmonic_memory/rei.py');ns={'__file__':str(D/'prior.py'),'__name__':'prior'};exec(compile(old,'C3Z/rei.py','exec'),ns);ops0,collision=ns['operators'],ns['collision'];H0=ns['H0'];SIG=ns['SIG']
 b=blob(XBASE,'research/r118c3u_positive_owner/birth_1024_32ray/history.csv');h=np.genfromtxt(io.BytesIO(b),names=True,delimiter=',');g=blob(XBASE,X+'/fine_2048_129_32_8/history.csv');a=blob(XBASE,X+'/fine_2048_129_32_8/matter.csv');hh=np.genfromtxt(io.BytesIO(g),names=True,delimiter=',');aa=np.genfromtxt(io.BytesIO(a),names=True,delimiter=',')
 rows=[]
 for name,h,ne,hs,nt in [('C3U',h,h['ne']*1e6,sha(b),32),('C3X',hh,aa['ne_m3'],sha(g),8)]:
  u=np.log(h['a']/h['a'][0]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);K=c*SIG*ne/(H0*h['h']);f=PchipInterpolator(u,np.c_[S,K],axis=0)
  for l in [4,6]:
   ops,ident=ops0(l);m=(l+1)**2;N=3*m;Id=np.eye(N,dtype=complex);C=np.column_stack([collision(Id[:,i],m) for i in range(N)]);L0=np.array([x.toarray() for x in ops])
   def eb(y):
    v=y.reshape(3,m);return -0.5*(v[1]+v[2]),.5j*(v[1]-v[2])
   for n in [nt,2*nt]:
    t=np.linspace(u[0],u[-1],n+1);full=np.zeros(N,complex);full[0]=np.sqrt(4*np.pi)
    states={}
    for tag,ip in [('I0I2_pol234',np.r_[0,np.arange(4,9)]),('I0I2I4_pol234',np.r_[0,np.arange(4,9),np.arange(16,25)])]:
     p=np.r_[ip,m+np.arange(4,25),2*m+np.arange(4,25)];q=np.setdiff1d(np.arange(N),p)
     states[tag]=dict(p=p,q=q,exact=full[p].copy(),memory=np.zeros(len(q),complex),local=full[p].copy(),onecell=full[p].copy(),max_second_order=0.)
    for j in range(n):
     du=t[j+1]-t[j];r=f((t[j]+t[j+1])/2);A=np.einsum('k,kij->ij',r[:5],L0)+r[5]*C;E=expm(du*A);full=E@full
     for z in states.values():
      p,q=z['p'],z['q'];F,G,H,J=E[np.ix_(p,p)],E[np.ix_(p,q)],E[np.ix_(q,p)],E[np.ix_(q,q)]
      ap=A[np.ix_(p,p)];prod=A[np.ix_(p,q)]@A[np.ix_(q,p)];local=expm(du*ap)
      z['max_second_order']=max(z['max_second_order'],float(np.linalg.norm(du*du*prod/2)))
      z['exact'],z['memory']=F@z['exact']+G@z['memory'],H@z['exact']+J@z['memory']
      z['local']=local@z['local'];z['onecell']=F@z['onecell']
    for tag,z in states.items():
     p=z['p'];error=float(np.linalg.norm(z['exact']-full[p])/max(np.linalg.norm(full[p]),1e-300));assert error<1e-11
     states_full={}
     for k in ['exact','local','onecell']:
      a=np.zeros(N,complex);a[p]=z[k];states_full[k]=a
     out={}
     for k,sl in [('E2',slice(4,9)),('B3',slice(9,16)),('E4',slice(16,25))]:
      j=1 if k[0]=='B' else 0;x=eb(full)[j][sl];norm=float(np.linalg.norm(x));out[k]=dict(norm=norm,**{m0+'_abs':float(np.linalg.norm(eb(y)[j][sl]-x)) for m0,y in states_full.items()},**{m0+'_rel':float(np.linalg.norm(eb(y)[j][sl]-x)/max(norm,1e-300)) for m0,y in states_full.items()})
     rows.append(dict(case=name,lmax=l,steps=n,retained=tag,dimension=len(p),projection_relative=error,max_one_step_second_order=z['max_second_order'],observables=out,history_sha=hs,identity=ident,tau=float(np.trapezoid(K,u))));print(name,l,n,tag,out,flush=True)
 write('LOW_L_CLOSURE.json',dict(rows=rows,scope='actual prescribed native history and full finite generator; exact discrete retained memory vs local PAP and one-cell projected exponential, no continuum nonlinear closure'))
if __name__=='__main__':{'native':native,'analyze':analyze,'closure':closure}[sys.argv[1]]()
