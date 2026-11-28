"""Capture actual C4M native stage external material and DG collision arguments; replay parity."""
from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,gzip,os,time,numpy as np,concurrent.futures as cf
D=Path(__file__).resolve().parent;P=D.parent;K=P/'r118c4m_coupled_stage';F=P/'r118c4f_external_stress';SH=Path.home()/'r118c4n_rei_shadow'
B=Path.home()/'worktrees/bass-r109-native-20261124/research/r118c4n_rei_stage_owner'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def build():
 arc=F/'NATIVE_SHADOW_SOURCE.tar.gz';meta=json.loads((F/'SHADOW_ARCHIVE.json').read_text());assert sha(arc.read_bytes())==meta['archive_sha256'];SH.mkdir(exist_ok=os.environ.get('C4N_REBUILD')=='1')
 with tarfile.open(arc) as t:
  for m in t.getmembers():
   assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
   p=SH/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
 prev=json.loads((K/'BUILD_ID.json').read_text());changes={}
 for name,v in prev['changes'].items():
  s=(K/v['file']).read_text();assert sha(s.encode())==v['sha'];(SH/name).write_text(s);changes[name]=dict(file=v['file'],sha=v['sha'],prior_sha=v['prior_sha']);(D/v['file']).write_text(s)
 name='bridge/src/main.rs';p=SH/name;s=p.read_text();old=sha(s.encode())
 a='  Ok(ExternalContribution{rho:fac*(m.energy+w+b-self.init-s.gas.ledgers.source_u+sec),pressure:std::array::from_fn(|i|std::array::from_fn(|j|fac*(m.pressure[i][j]+ps[i][j]+if i==j{2.*w/3.}else{0.}))),photon_rho:fac*(m.energy+sec),ne_m3:ne})'
 assert s.count(a)==1
 s=s.replace(a,'''  let v=ExternalContribution{rho:fac*(m.energy+w+b-self.init-s.gas.ledgers.source_u+sec),pressure:std::array::from_fn(|i|std::array::from_fn(|j|fac*(m.pressure[i][j]+ps[i][j]+if i==j{2.*w/3.}else{0.}))),photon_rho:fac*(m.energy+sec),ne_m3:ne};
  if std::env::var_os("C4N_CAPTURE").is_some(){
   let l=&s.gas.ledgers;let work=-fac*(l.thermal_work+l.photon_work+l.boundary_u+s.work);
   eprintln!("C4N_EXT,{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",self.calls,g.a,v.rho,work,v.pressure[0][0],v.pressure[1][1],v.pressure[2][2],v.pressure[0][1],v.pressure[0][2],v.pressure[1][2],v.ne_m3,v.photon_rho);
  }Ok(v)''')
 p.write_text(s);(D/'instrumented_bridge.rs').write_text(s);changes[name]=dict(file='instrumented_bridge.rs',sha=sha(s.encode()),prior_sha=old)
 name='bridge/src/dg.rs';p=SH/name;s=p.read_text();old=sha(s.encode());a='  for i in 0..dn.len(){s.dn[i]+=depth*dn[i];s.dv[i]+=depth*dv[i];}self.coefficients(s)?;Ok(diag)'
 assert s.count(a)==1
 s=s.replace(a,'''  if std::env::var_os("C4N_CAPTURE_DG").is_some(){
   static COUNT:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);
   let i=COUNT.fetch_add(1,std::sync::atomic::Ordering::Relaxed);
   if i==0||i==22{
    let dir=std::env::var("C4N_CAPTURE_DG").map_err(|e|e.to_string())?;
    let path=std::path::Path::new(&dir).join(format!("dg_{i}.txt"));
    use std::io::Write;let mut f=std::io::BufWriter::new(std::fs::File::create(path).map_err(|e|e.to_string())?);
    let meta=[self.nr()as f64,self.nc()as f64,self.xe[0].ln(),self.xe[self.xe.len()-1].ln(),theta,tr,depth,self.cap,g.a,g.h];
    for (key,x) in [("meta",&meta[..]),("e",&self.e),("d",&d),("n",&n),("w",&w),("w0",&self.w0),("A",&a),("B",&b),("zh",zh),("wh",wh),("zl",&zl),("wl",&wl),("rhsN",&dn),("rhsV",&dv),("N",&s.n),("V",&s.v),("dN",&s.dn),("dV",&s.dv)]{
      write!(f,"{key}").map_err(|e|e.to_string())?;for v in x{write!(f," {v:.17e}").map_err(|e|e.to_string())?}writeln!(f).map_err(|e|e.to_string())?;
    }
   }
  }
'''+a)
 p.write_text(s);(D/'instrumented_dg.rs').write_text(s);changes[name]=dict(file='instrumented_dg.rs',sha=sha(s.encode()),prior_sha=old)
 name='bridge/src/bin/c4n_bass.rs';p=SH/name;p.parent.mkdir(exist_ok=True);s=(B/'native.rs').read_text();p.write_text(s);(D/'bass_native_dependency.rs').write_text(s);changes[name]=dict(file='bass_native_dependency.rs',sha=sha(s.encode()),prior_sha=None)
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='3';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'bridge/Cargo.toml'),'--bin','c3x_dg_bridge','--bin','c4n_bass']
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 bins={}
 for n in ['c3x_dg_bridge','c4n_bass']:
  raw=(SH/'bridge/target/release'/n).read_bytes();(D/(n+'.gz')).write_bytes(gzip.compress(raw,mtime=0));bins[n]=sha(raw)
 write('BUILD_ID.json',dict(prior_archive=meta['archive_sha256'],changes=changes,bins=bins,cargo_lock_sha=sha((SH/'bridge/Cargo.lock').read_bytes()),command=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def capture():
 b=SH/'bridge/target/release/c3x_dg_bridge';assert sha(b.read_bytes())==json.loads((D/'BUILD_ID.json').read_text())['bins']['c3x_dg_bridge']
 jobs=['base','H-0.01','H+0.01','H-0.003','H+0.003']
 def run(tag):
  cfg=K/(tag+'.cfg');out=SH/tag;env=os.environ.copy();env['R118C4M_TRACE']='1';env['C4N_CAPTURE']='1'
  if tag in ['base','H-0.003','H+0.003']:env['C4N_CAPTURE_DG']=str(out)
  cmd=[str(b),str(cfg),str(out),'1024','129','4','4','19.99995','on','fine','mean','0','0'];tm=time.monotonic()
  with (D/(tag+'.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=400)
  if out.is_dir():
   for p in out.iterdir():
    if p.is_file():(D/(tag+'_'+p.name)).write_bytes(p.read_bytes())
  parity={n:(D/(tag+'_'+n)).read_bytes()==(K/(tag+'_'+n)).read_bytes() for n in ['history.csv','matter.csv','stock.csv','external.csv','RETURN.txt']} if r.returncode==0 else {}
  v=dict(tag=tag,exit=r.returncode,seconds=time.monotonic()-tm,cmd=cmd,config_sha=sha(cfg.read_bytes()),parity=parity);print(v,flush=True);return v
 with cf.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(run,jobs))
 write('NATIVE_RUNS.json',rows);assert all(r['exit']==0 and all(r['parity'].values()) for r in rows)
 for r in rows:
  tag=r['tag'];raw=(D/(tag+'.log')).read_text().splitlines();a=np.array([list(map(float,l.split(',')[1:])) for l in raw if l.startswith('C4N_EXT,')]);g=np.array([list(map(float,l.split(',')[1:])) for l in raw if l.startswith('C4M_GEOM,')]).reshape(4,3,27)
  assert len(set(a[:,0]))==9 and a.shape[1]==12
  tab=[]
  for j in range(9):
   v=a[a[:,0]==j,1:];assert len(v)>0 and np.array_equal(v,np.broadcast_to(v[0],v.shape))
   tab.append(v[0])
  tab=np.array(tab);assert np.array_equal(tab[:,0],np.r_[g[0,0,2],g[:,1:,2].ravel()])
  # a,rho,P6,ne,photon,du; preserve original rho and independent work separately
  dd=np.zeros((9,11));dd[:,:2]=tab[:,:2];dd[:,2:10]=tab[:,3:];dd[::2][:4,10]=g[:,0,1]
  np.savetxt(D/(tag+'_stage.csv'),dd,delimiter=',',fmt='%.17e')
  np.savetxt(D/(tag+'_work.csv'),tab[:,[0,1,2]],delimiter=',',fmt='%.17e')
 write('CAPTURE.json',dict(rows=rows,stage_count=9,source='actual 4-step native owner; three states per step with duplicate accepted endpoints, table rho exact source and independent work identity',scope='read-only instrumentation, original C4M outputs byte-equal'))
if __name__=='__main__':{'build':build,'capture':capture}[sys.argv[1]]()
