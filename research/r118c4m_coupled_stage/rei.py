"""Actual complete coupled native stage directional experiment with stage telemetry."""
from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,gzip,os,time,numpy as np,concurrent.futures as cf
from scipy.linalg import expm,expm_frechet
D=Path(__file__).resolve().parent;P=D.parent;K=P/'r118c4l_implicit_branch';F=P/'r118c4f_external_stress';SH=Path.home()/'r118c4m_rei_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def build():
 arc=F/'NATIVE_SHADOW_SOURCE.tar.gz';meta=json.loads((F/'SHADOW_ARCHIVE.json').read_text());assert sha(arc.read_bytes())==meta['archive_sha256'];SH.mkdir(exist_ok=os.environ.get('C4M_REBUILD')=='1')
 with tarfile.open(arc) as t:
  for m in t.getmembers():
   assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
   p=SH/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
 prev=json.loads((K/'BUILD_ID.json').read_text());changes={}
 for name,v in prev['changes'].items():
  s=(K/v['file']).read_text();assert sha(s.encode())==v['sha'];(SH/name).write_text(s);(D/v['file']).write_text(s);changes[name]=dict(file=v['file'],sha=v['sha'],prior_sha=v['prior_sha'])
 name='components/bass_rec/bass/_rustcore/src/kinetic/owned_thomson.rs';p=SH/name;s=p.read_text();old=sha(s.encode());tok='        self.external_matter(&next, &xn, x)?;\n        Ok((next, xn, e0.max(e1)))';assert s.count(tok)==1
 s=s.replace(tok,(D/'telemetry.rs.txt').read_text()+'        Ok((next, xn, e0.max(e1)))');p.write_text(s);(D/'instrumented_thomson.rs').write_text(s);changes[name]=dict(file='instrumented_thomson.rs',sha=sha(s.encode()),prior_sha=old)
 name='bridge/src/main.rs';p=SH/name;s=p.read_text();old=sha(s.encode())
 tok='let mut g=owner.initial(1./21.,[0.01,0.,0.,0.,0.0075])?;';assert s.count(tok)==1
 s=s.replace(tok,'''let scale:f64=std::env::var("C4M_SHEAR_SCALE").unwrap_or("1".into()).parse()?;let mut g=owner.initial(1./21.,[0.01*scale,0.,0.,0.,0.0075*scale])?;''')
 tok='  let mut dg=s.dg.clone();';assert s.count(tok)==1
 s=s.replace(tok,'''  if std::env::var_os("R118C4M_TRACE").is_some(){
   for (role,z) in [(0,&base),(1,&first),(2,&fine),(3,&full)]{
    let mut line=format!("C4M_CHEM,{},{role},{:.17e},{:.17e}",self.calls,z.a,z.gas.w_erg_per_h);
    for v in z.gas.fractions{line.push_str(&format!(",{v:.17e}"));}
    let l=&z.ledgers;
    for v in [l.source_n,l.source_u,l.absorbed_n,l.escaped_u,l.thermal_work,l.photon_work,l.boundary_u,l.cmb_input,z.photons.iter().sum::<f64>(),z.photon_energy_ref.iter().sum::<f64>(),z.heii_above.as_ref().map_or(0.,|p|p.number.iter().sum()),z.hei_middle.as_ref().map_or(0.,|p|p.number.iter().sum()),z.hi_below.as_ref().map_or(0.,|p|p.number.iter().sum())]{line.push_str(&format!(",{v:.17e}"));}
    line.push_str(&format!(",{},{},{},{}",z.photons.iter().filter(|x|**x>0.).count(),z.heii_above.as_ref().map_or(0,|p|p.number.iter().filter(|x|**x>0.).count()),z.hei_middle.as_ref().map_or(0,|p|p.number.iter().filter(|x|**x>0.).count()),z.hi_below.as_ref().map_or(0,|p|p.number.iter().filter(|x|**x>0.).count())));eprintln!("{line}");
   }
  }
'''+tok)
 tok='  Ok(next)\n }\n}\nfn main';assert s.count(tok)==1
 s=s.replace(tok,'''  if std::env::var_os("R118C4M_TRACE").is_some(){eprintln!("C4M_ADVANCE,{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",self.calls,old.a,mid.a,end.a,next.cool,next.spec,next.work,next.source_n,next.tau);}
'''+tok)
 p.write_text(s);(D/'instrumented_bridge.rs').write_text(s);changes[name]=dict(file='instrumented_bridge.rs',sha=sha(s.encode()),prior_sha=old)
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='3';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'bridge/Cargo.toml')]
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 b=SH/'bridge/target/release/c3x_dg_bridge';raw=b.read_bytes();(D/'coupled_bridge.gz').write_bytes(gzip.compress(raw,mtime=0));write('BUILD_ID.json',dict(prior_archive=meta['archive_sha256'],changes=changes,binary_sha=sha(raw),cargo_lock_sha=sha((SH/'bridge/Cargo.lock').read_bytes()),command=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def native():
 b=SH/'bridge/target/release/c3x_dg_bridge';assert sha(b.read_bytes())==json.loads((D/'BUILD_ID.json').read_text())['binary_sha'];cfg=F/'1024_4_base.cfg';s=cfg.read_text()
 x=float(next(l.split('=')[1] for l in s.splitlines() if l.startswith('initial_x_hii=')))
 jobs=[('base','H',0.)]+[(f'{k}{v:+g}',k,v) for k in ['H','S'] for v in [-.01,.01,-.003,.003]]
 def job(q):
  tag,kind,v=q;out=SH/tag;path=D/(tag+'.cfg');ss=s
  if kind=='H':
   old=next(l for l in s.splitlines() if l.startswith('initial_x_hii='));ss=ss.replace(old,f'initial_x_hii={x*(1+v):.17e}')
  if v==0.:ss=s
  path.write_text(ss);env=os.environ.copy();env['R118C4M_TRACE']='1';env['C4M_SHEAR_SCALE']=str(1+v if kind=='S' else 1.)
  cmd=[str(b),str(path),str(out),'1024','129','4','4','19.99995','on','fine','mean','0','0'];tm=time.monotonic()
  with (D/(tag+'.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=400)
  if out.is_dir():
   for p in out.iterdir():
    if p.is_file():(D/(tag+'_'+p.name)).write_bytes(p.read_bytes())
  row=dict(tag=tag,kind=kind,p=v,exit=r.returncode,seconds=time.monotonic()-tm,cmd=cmd,config_sha=sha(path.read_bytes()));print(row,flush=True);return row
 with cf.ThreadPoolExecutor(max_workers=3) as ex:rr=list(ex.map(job,jobs))
 write('NATIVE_RUNS.json',rr);assert all(r['exit']==0 for r in rr)
def stf(x):
 v0,v1,v2,v3,v4=x;r=2**-.5;t=6**-.5
 return np.array([[r*v0-t*v1,r*v2,r*v3],[r*v2,-r*v0-t*v1,r*v4],[r*v3,r*v4,2*t*v1]])
def mat(x):
 xx,yy,zz,xy,xz,yz=x;return np.array([[xx,xy,xz],[xy,yy,yz],[xz,yz,zz]])
def comp(a):
 r=2**-.5;t=6**-.5
 return np.array([r*(a[0,0]-a[1,1]),t*(2*a[2,2]-a[0,0]-a[1,1]),r*(a[0,1]+a[1,0]),r*(a[0,2]+a[2,0]),r*(a[1,2]+a[2,1])])
OL=.684908
def stage(row):
 # role,du,a,h,S5,F9,rho,P6,ne,photon_rho
 S=stf(row[4:9]);h=row[3];F=row[9:18].reshape(3,3);rho=row[18];P=mat(row[19:25]);ne=row[25]
 q=np.sum(S*S)/3+(rho+np.trace(P)-2*OL)/(2*h*h);pi=P-np.eye(3)*np.trace(P)/3
 return S,h,F,rho,P,ne,q,(q-2)*S+3*pi/h**2
def parse(tag):
 log=(D/(tag+'.log')).read_text().splitlines()
 g=np.array([list(map(float,l.split(',')[1:])) for l in log if l.startswith('C4M_GEOM,')]).reshape(4,3,27)
 c=np.array([list(map(float,l.split(',')[1:])) for l in log if l.startswith('C4M_CHEM,')]).reshape(8,4,-1)
 a=np.array([list(map(float,l.split(',')[1:])) for l in log if l.startswith('C4M_ADVANCE,')])
 assert g.shape==(4,3,27) and c.shape[:2]==(8,4) and len(a)==8
 assert np.array_equal(g[:,:,0],np.tile(np.arange(3),(4,1)))
 h=np.genfromtxt(D/(tag+'_history.csv'),delimiter=',',names=True);m=np.genfromtxt(D/(tag+'_matter.csv'),delimiter=',',names=True)
 return g,c,a,h,m
def analyze():
 base,bc,ba,bh,bm=parse('base');same={n:(D/('base_'+n)).read_bytes()==(K/('1024_4_base_'+n)).read_bytes() for n in ['history.csv','matter.csv','stock.csv','external.csv','RETURN.txt']}
 assert all(same.values()),same
 runs=json.loads((D/'NATIVE_RUNS.json').read_text());rows=[];arrays={}
 for run in runs[1:]:
  tag,kind,p=run['tag'],run['kind'],run['p'];q=abs(p);g,c,a,h,m=parse(tag);assert np.array_equal(g[:,:,2],base[:,:,2]) and np.array_equal(c[:,:,2],bc[:,:,2])
  # Exact identity of the finite geometry step (stable log ratio and finite coframe secant).
  sc=[];lc=[]
  for i in range(4):
   O,M,N=map(stage,base[i]);o,md,n=map(stage,g[i]);du=base[i,0,1];assert du==g[i,0,1]
   so,h0,F0,_,_,_,_,_=O;sm,hm,Fm,rho,P,ne,q0,rhs=M;sn,hn,Fn,*_=N
   spo,hp,Fp,*_=o;spm,hpm,Fpm,rp,pp,np0,qp,rhsp=md;spn,hpn,Fpn,*_=n
   dlog=lambda x,y:np.log1p((x-y)/y)/q
   dh0=dlog(hp,h0);dhn=dlog(hpn,hn);exacth=dh0-du*(qp-q0)/q
   ds=(spo-so)/q+du*(rhsp-rhs)/q;obs=(spn-sn)/q
   # Actual finite perturbation of matrix exponential, independent scipy implementation.
   df=(expm(du*spm)@Fp-expm(du*sm)@F0)/q;obsf=(Fpn-Fn)/q
   dsm=(spm-sm)/q;dF0=(Fp-F0)/q;hm1=(hpm-hm)/q;dr=(rp-rho)/q;dP=(pp-P)/q;dne=(np0-ne)/q
   dq=2*np.sum(sm*dsm)/3+(dr+np.trace(dP))/(2*hm**2)-(rho+np.trace(P)-2*OL)*hm1/hm**3
   dPi=dP-np.eye(3)*np.trace(dP)/3;Pi=P-np.eye(3)*np.trace(P)/3
   dR=(q0-2)*dsm+dq*sm+3*(dPi/hm**2-2*Pi*hm1/hm**3)
   pred=(spo-so)/q+du*dR
   df1=expm(du*sm)@dF0+expm_frechet(du*sm,du*dsm,compute_expm=False)@F0
   op=(np0/hpm-ne/hm)/q;dop=dne/hm-ne*hm1/hm**2
   sc.append(dict(step=i,logH_FD=float(dhn),logH_exact_gap=float(abs(dhn-exacth)),logH_linear_gap=float(abs(dhn-(dh0-du*dq))),shear_exact_gap=float(np.linalg.norm(obs-ds)),shear_linear_gap=float(np.linalg.norm(obs-pred)),coframe_exact_gap=float(np.linalg.norm(obsf-df)),coframe_linear_gap=float(np.linalg.norm(obsf-df1)),opacity_fd=float(op),opacity_linear_gap=float(abs(op-dop)),q_direction=float(dq),external_mid_ne=float(dne)))
  fields=['xHII','xHeII','xHeIII','T','primary','thermal','binding','cool','spec','N','tau','ledger','gauss','h']
  end={k:float((h[k][-1]-bh[k][-1])/q) for k in fields};init={k:float((h[k][0]-bh[k][0])/q) for k in fields}
  # Compare full local source/stock path with nominal; count topology only, not complete node identity.
  top=np.count_nonzero(c[:,:,-4:]!=bc[:,:,-4:])
  row=dict(tag=tag,kind=kind,p=p,stage=sc,terminal=end,initial=init,stock_count_topology_differences=int(top),max_ledger=float(max(abs(h['ledger']))),max_gauss=float(max(abs(h['gauss']))))
  rows.append(row);arrays[tag+'_geometry']=g;arrays[tag+'_chem']=c;arrays[tag+'_advance']=a;print(tag,'stage gaps',max(r['shear_exact_gap'] for r in sc),'H',end['xHII'],'T',end['T'],'topology',top,flush=True)
 arrays.update(base_geometry=base,base_chem=bc,base_advance=ba)
 np.savez_compressed(D/'COUPLED_STAGE.npz',**arrays)
 convergence=[]
 for kind in ['H','S']:
  for sg in [-1,1]:
   a,b=[next(r for r in rows if r['kind']==kind and r['p']==sg*v) for v in [.01,.003]]
   convergence.append(dict(kind=kind,direction=sg,terminal_stencil_gap={k:abs(a['terminal'][k]-b['terminal'][k]) for k in a['terminal']}))
 write('COUPLED_STAGE.json',dict(runs=runs,base_replay_equal=same,rows=rows,stencil_convergence=convergence,scope='Actual full native step_external, both gas/secondary half/full submaps and corrected BASS metric. Stage-resolved finite directional secants and independent algebraic/linear geometry reconstruction; no claim of analytic full material/DG tangent. Fixed short z20→19.99995 clock.'))
if __name__=='__main__':{'build':build,'native':native,'analyze':analyze}[sys.argv[1]]()
