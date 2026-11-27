"""Exact C3X source archive + initialization-only helium patch, native DG3 gas columns."""
from pathlib import Path
import sys,subprocess,hashlib,json,gzip,tarfile,io,os,time,concurrent.futures as cf,re,numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.linalg import expm
from scipy.constants import c
D=Path(__file__).resolve().parent;R=D.parents[1];P=D.parent;HOME=Path.home();SH=HOME/'r118c4c_dg_shadow';PR='b145729be3d9d103ef1379c9efe5f85687558bc6';XB='0e624af4668c7722759ccf781d91e15362b6d451';X='research/r118c3x_tangent_source';ZB='32d0724ae284a10b5e77377055c2b984e12180c2'
def blob(rev,p):return subprocess.check_output(['git','-C',str(R),'show',rev+':'+p])
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def build():
 SH.mkdir(exist_ok=False)
 ident=json.loads(blob(XB,X+'/ops/BUILD_ID.json'));a=ident['identity']
 paths=['rust/rei_microphysics','docs/fastest_track_chat/REI-AXBI-GOAL-20261014/OUTPUT_CONTRACT.json','research/flrw_jacobian_columns_20261016/CONTRACT.json','research/r118c3b_ff_balance/gauntff.dat','research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json','research/axbi_goal_20261014/scenario/AX05_NUMERICAL_CONTRACT.md','research/flrw_covariant_transport_20261015']
 def archive(paths,want):
  b=subprocess.check_output(['git','-C',str(R),'archive',PR,*paths]);assert sha(b)==want,(paths,sha(b),want)
  with tarfile.open(fileobj=io.BytesIO(b)) as t:t.extractall(SH,filter='data')
 archive(paths,a['archive_sha']);archive(['components/bass_rec/bass','components/bass_rec/rec'],a['integrated_archive_sha']);archive(['src/rei_bianchi/microphysics/data/savin2002_charge_exchange.csv'],a['savin_archive_sha'])
 for path,key in [('rust/rei_microphysics/src/axbi_covariant_driver.rs','axbi_covariant_driver.rs'),('rust/rei_microphysics/src/spectral_ff.rs','spectral_ff.rs')]:
  p=SH/path;assert sha(p.read_bytes())==a['original_sha'][path];raw=gzip.decompress(blob(XB,X+'/ops/'+key+'.gz'));assert sha(raw)==a['patched_sha'][path];p.write_bytes(raw)
 bridge=SH/'bridge';(bridge/'src').mkdir(parents=True)
 for path,src,hashkey in [('Cargo.toml','ops/Cargo.toml','bridge_manifest_sha'),('Cargo.lock','ops/Cargo.lock',None),('src/main.rs','metric_bridge.rs','bridge_sha'),('src/frequency.rs','frequency.rs','frequency_sha'),('src/dg.rs','dg.rs','dg_sha'),('dg_rhs.cpp','dg_rhs.cpp','kernel_sha'),('build.rs','build.rs','build_sha')]:
  raw=blob(XB,X+'/'+src);want=a[hashkey] if hashkey else ident['cargo_lock'];assert sha(raw)==want,(src,sha(raw),want);(bridge/path).write_bytes(raw)
 p=SH/'rust/rei_microphysics/src/axbi_covariant_driver.rs';s=p.read_text();token='impl Driver {\n    pub fn new(config: DriverConfig)'
 add='''impl Driver {
    /// C4C research-only: rebase the initial energy after a fresh admissible gas perturbation.
    pub fn c4c_rebase_initial(&mut self,s:&DriverState)->Result<(),ForwardError>{
        if s.accepted!=0 || s.a!=1./21. || s.ledgers.source_n!=0. || s.ledgers.source_u!=0. || self.photon_inventory(s)!=(0.,0.){return Err(err("C4C_INITIAL_REBASE_DOMAIN"))}
        self.initial_energy=self.total_energy(s)?;
        self.validate(s,1e-8)
    }
    pub fn new(config: DriverConfig)'''
 assert s.count(token)==1;p.write_text(s.replace(token,add));(D/'driver_patch.rs.txt').write_text(add)
 m=bridge/'src/main.rs';s=m.read_text();old=s
 assert s.count('if args.len()!=10')==1;s=s.replace('if args.len()!=10','if args.len()!=12').replace('let(d,mut gas)=Driver::new_general','let(mut d,mut gas)=Driver::new_general')
 token=' gas.ff_spectrum=Some(SpectralFf::new(1e-10,60.,bins)?);'
 add=''' let heii:f64=args[10].parse()?;let heiii:f64=args[11].parse()?;
 if heii!=0. || heiii!=0.{
  let nh=d.n_h0_cm3/gas.a.powi(3);let nhe=d.n_he0_cm3/gas.a.powi(3);let t=map(gas.gas.eos(nh,nhe))?.temperature_k;
  gas.gas=map(rei_microphysics::igm_state::IgmGasState::from_temperature([gas.gas.fractions[0],heii,heiii],nh,nhe,t))?;
  map(d.c4c_rebase_initial(&gas))?;
 }
'''+token
 assert s.count(token)==1;s=s.replace(token,add);m.write_text(s)
 (D/'metric_bridge_patched.rs').write_text(s)
 info=dict(base=PR,pinned=XB,original=a,driver_patch_sha=sha(p.read_bytes()),bridge_patch_sha=sha(m.read_bytes()),bridge_original_sha=sha(old.encode()),cargo_lock_sha=sha((bridge/'Cargo.lock').read_bytes()),scope='original C3X physics and accepted-step gates unchanged; only initialization and initial energy reference modified')
 write('BUILD_ID.json',info)
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='4'
 with (D/'build.log').open('w') as f:z=subprocess.run(['cargo','build','--offline','--release','--manifest-path',str(bridge/'Cargo.toml')],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240)
 assert z.returncode==0
 b=bridge/'target/release/c3x_dg_bridge';assert b.is_file();info['binary_sha']=sha(b.read_bytes());info['binary_bytes']=b.stat().st_size;write('BUILD_ID.json',info);(D/'c4c_dg_bridge.gz').write_bytes(gzip.compress(b.read_bytes(),mtime=0));print('build verified',info['binary_sha'],flush=True)
def native():
 b=SH/'bridge/target/release/c3x_dg_bridge';assert sha(b.read_bytes())==json.loads((D/'BUILD_ID.json').read_text())['binary_sha']
 cfg=blob(PR,'research/r118c3i_event_ledger/table.cfg').decode();(D/'BASE.cfg').write_text(cfg);x0=float(re.search(r'^initial_x_hii=(.*)$',cfg,re.M)[1]);T0=float(re.search(r'^initial_temperature_k=(.*)$',cfg,re.M)[1])
 root=SH/'runs';root.mkdir(exist_ok=False)
 # Same C4B short clock and DG 1024/129/32, 2 accepted steps.
 cases=[('base',0.,0.,0.,0.)]+[(f'H_{e:g}',e,0.,0.,0.) for e in [-.01,.01]]+[(f'T_{e:g}',0.,0.,0.,e) for e in [-.01,.01]]+[(f'HeII_{e:g}',0.,e,0.,0.) for e in [5e-7,1e-6,2e-6]]+[(f'HeIII_{e:g}',0.,0.,e,0.) for e in [5e-7,1e-6,2e-6]]
 def job(q):
  tag,h,y,z,t=q;out=root/tag;cf=root/(tag+'.cfg')
  s=re.sub(r'^initial_x_hii=.*$',f'initial_x_hii={x0*(1+h):.17g}',cfg,flags=re.M);s=re.sub(r'^initial_temperature_k=.*$',f'initial_temperature_k={T0*(1+t):.17g}',s,flags=re.M);cf.write_text(s);(D/(tag+'.cfg')).write_text(s)
  args=[str(b),str(cf),str(out),'1024','129','4','2','19.99995','on','fine','mean',format(y,'.17g'),format(z,'.17g')]
  start=time.monotonic();r=dict(case=tag,perturb=[h,y,z,t],cmd=args)
  try:
   with (D/(tag+'.log')).open('w') as f:a=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=130)
   r['exit']=a.returncode
  except subprocess.TimeoutExpired:r['exit']=124
  r['seconds']=time.monotonic()-start
  if out.exists():
   for n in ['history.csv','matter.csv','stock.csv','RETURN.txt']:
    if (out/n).exists():(D/(tag+'_'+n)).write_bytes((out/n).read_bytes())
  if r['exit']==0:
   v=np.genfromtxt(out/'history.csv',names=True,delimiter=',');assert len(v)==3 and int(v['accepted'][-1])==2 and 'status=COMPLETE' in (out/'RETURN.txt').read_text()
   r.update(source_sha=sha((out/'source.txt').read_bytes()),accepted=2,ledger=float(max(abs(v['ledger']))),gauss=float(max(abs(v['gauss']))),metric=float(max(v['metric'])),margin=float(min(v['margin'])),terminal={k:float(v[k][-1]) for k in v.dtype.names},initial={k:float(v[k][0]) for k in ['T','xHII','xHeII','xHeIII','thermal','binding']})
  print(tag,r['exit'],r.get('ledger'),r.get('margin'),flush=True);return r
 rows=[]
 with cf.ThreadPoolExecutor(max_workers=3) as ex:
  for r in ex.map(job,cases):rows.append(r);write('NATIVE_RUNS.json',rows)
def analyze():
 rows=json.loads((D/'NATIVE_RUNS.json').read_text());g={x['case']:x for x in rows if x['exit']==0};keys=['xHII','xHeII','xHeIII','T','thermal','binding','spec','corr_U','corr_N','corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz','h','S0','S1','S2','S3','S4']
 if 'base' not in g:write('JACOBIAN.json',dict(success=len(g),blocked='base failed'));return
 def v(n):return np.array([g[n]['terminal'][k] for k in keys])
 b=v('base');old=np.genfromtxt(P/'r118c4b_dg3_memory/dg_1024_2_0_history.csv',names=True,delimiter=',');b0=np.array([old[k][-1] for k in keys]);diff=b-b0
 J={};err={}
 for q in ['H','T']:
  a,n=f'{q}_-0.01',f'{q}_0.01'
  if all(k in g for k in [a,n]):J[q]=(v(n)-v(a))/.02
 for q in ['HeII','HeIII']:
  n=[f'{q}_{e:g}' for e in [5e-7,1e-6,2e-6]]
  if all(k in g for k in n):
   x,y,z=map(v,n);j=(-3*b+4*y-z)/(2e-6);k=(-3*b+4*x-y)/1e-6
   J[q]=k;err[q]=dict(abs=np.abs(j-k).tolist(),rel=(abs(j-k)/np.maximum(abs(k),1e-300)).tolist())
 combined={}
 if 'H' in J and 'T' in J:
  prev=json.loads((P/'r118c4b_dg3_memory/DIRECTIONAL.json').read_text())['results']['1024_2']['0.01']['derivative'];val=J['H']-J['T']
  for k,x in zip(keys,val):
   if k in prev:combined[k]={'new':float(x),'prior':prev[k],'abs_diff':float(abs(x-prev[k])),'relative':float(abs(x-prev[k])/max(abs(prev[k]),1e-300))}
 out=dict(success=len(g),cases=len(rows),keys=keys,coordinate_units=['relative initial HII','absolute HeII','absolute HeIII','relative initial T'],columns={k:v.tolist() for k,v in J.items()},he_step_refinement=err,zero_reference_abs=dict(zip(keys,abs(diff).tolist())),combined_C4B=combined,scope='fresh native DG3 gas coordinates, no photon/geometry IC Jacobian or continuum; He boundary one-sided; geometry floor')
 write('JACOBIAN.json',out);print(out,flush=True)
def memory():
 old=blob(ZB,'research/r118c3z_harmonic_memory/rei.py');ns={'__file__':str(D/'prior.py'),'__name__':'prior'};exec(compile(old,'C3Z/rei.py','exec'),ns);ops0,collision=ns['operators'],ns['collision'];H0=ns['H0'];SIG=ns['SIG']
 b=blob(XB,'research/r118c3u_positive_owner/birth_1024_32ray/history.csv');h=np.genfromtxt(io.BytesIO(b),names=True,delimiter=',');g=blob(XB,X+'/fine_2048_129_32_8/history.csv');a=blob(XB,X+'/fine_2048_129_32_8/matter.csv');hh=np.genfromtxt(io.BytesIO(g),names=True,delimiter=',');aa=np.genfromtxt(io.BytesIO(a),names=True,delimiter=',')
 rows=[]
 for name,h,ne,hs,nt in [('C3U',h,h['ne']*1e6,sha(b),32),('C3X',hh,aa['ne_m3'],sha(g),8)]:
  u=np.log(h['a']/h['a'][0]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);K=c*SIG*ne/(H0*h['h']);f=PchipInterpolator(u,np.c_[S,K],axis=0)
  for l in [4,6]:
   ops,ident=ops0(l);m=(l+1)**2;N=3*m;Id=np.eye(N,dtype=complex);C=np.column_stack([collision(Id[:,i],m) for i in range(N)]);A0=np.array([x.toarray() for x in ops]);p=np.r_[m+np.arange(4,m),2*m+np.arange(4,m)];q=np.setdiff1d(np.arange(N),p)
   def eb(y):
    v=y.reshape(3,m);return -0.5*(v[1]+v[2]),.5j*(v[1]-v[2])
   for n in [nt,2*nt]:
    full=np.zeros(N,complex);full[0]=np.sqrt(4*np.pi);pr=full[p].copy();slip=full[q].copy();terms=[];nomem=pr.copy();no_pol_stream=full.copy();t=np.linspace(u[0],u[-1],n+1)
    for j in range(n):
     h0=t[j+1]-t[j];r=f((t[j]+t[j+1])/2);L=np.einsum('k,kij->ij',r[:5],A0);A=L+r[5]*C;E=expm(h0*A);F,G,H,J=E[np.ix_(p,p)],E[np.ix_(p,q)],E[np.ix_(q,p)],E[np.ix_(q,q)]
     qr=slip+sum(terms,start=np.zeros(len(q),complex));npr=F@pr+G@qr;nomem=F@nomem+G@slip;terms=[J@v for v in terms]+[H@pr];slip=J@slip;pr=npr;full=E@full
     # Remove streaming with either input or output polarized, keep intensity streaming and collisions.
     L[p,:]=0;L[:,p]=0;no_pol_stream=expm(h0*(L+r[5]*C))@no_pol_stream
    # For each observable use absolute and relative error, especially extremely tiny B3.
    yy=full.copy();yy[p]=pr;zz=full.copy();zz[p]=nomem;out={}
    for k,sl in [('E2',slice(4,9)),('B3',slice(9,16)),('E4',slice(16,25))]:
     j=1 if k[0]=='B' else 0;x=eb(full)[j][sl];a=eb(yy)[j][sl];b=eb(zz)[j][sl];v=eb(no_pol_stream)[j][sl];norm=float(np.linalg.norm(x))
     out[k]=dict(norm=norm,exact_abs=float(np.linalg.norm(a-x)),omit_memory_abs=float(np.linalg.norm(b-x)),omit_memory_rel=float(np.linalg.norm(b-x)/max(norm,1e-300)),omit_polarized_streaming_norm=float(np.linalg.norm(v)),omit_streaming_relative=float(np.linalg.norm(v-x)/max(norm,1e-300)))
    err=float(np.linalg.norm(pr-full[p])/max(np.linalg.norm(full[p]),1e-300));assert err<1e-10
    rows.append(dict(case=name,lmax=l,steps=n,tau=float(np.trapezoid(K,u)),history_sha=hs,identity=ident,projection_relative=err,observables=out));print(name,l,n,err,out,flush=True)
 write('POL_MEMORY.json',dict(rows=rows,scope='actual native finite generator, resolved spin polarization, exact discrete causal elimination with initial slip; streaming removal only diagnostic, not alternate physical owner'))
if __name__=='__main__':{'build':build,'native':native,'analyze':analyze,'memory':memory}[sys.argv[1]]()
