"""Native residual instrumentation; preserve original accepted stages and verify byte replay."""
from pathlib import Path
import sys,os,json,subprocess,hashlib,tarfile,io,gzip,time,numpy as np,concurrent.futures as cf
D=Path(__file__).resolve().parent;P=D.parent;F=P/'r118c4f_external_stress';H=Path.home();SH=H/'r118c4h_rei_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def build():
 arc=F/'NATIVE_SHADOW_SOURCE.tar.gz';meta=json.loads((F/'SHADOW_ARCHIVE.json').read_text());assert sha(arc.read_bytes())==meta['archive_sha256'];SH.mkdir(exist_ok=False)
 with tarfile.open(arc) as t:
  for m in t.getmembers():
   assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
   p=SH/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
 p=SH/'rust/rei_microphysics/src/axbi_covariant_driver.rs';s=p.read_text();oldsha=sha(p.read_bytes())
 tok='                *s = next;\n                return Ok(());'
 assert s.count(tok)==1
 patch=(D/'stage_patch.rs.txt').read_text();s=s.replace(tok,patch+'\n'+tok);p.write_text(s);(D/'instrumented_driver.rs').write_text(s)
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='5';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'bridge/Cargo.toml')]
 with (D/'build.log').open('w') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=360)
 assert r.returncode==0
 b=SH/'bridge/target/release/c3x_dg_bridge';raw=b.read_bytes();(D/'stage_bridge.gz').write_bytes(gzip.compress(raw,mtime=0));write('BUILD_ID.json',dict(prior_archive=meta['archive_sha256'],old_driver_sha=oldsha,new_driver_sha=sha(p.read_bytes()),binary_sha=sha(raw),binary_archive_sha=sha((D/'stage_bridge.gz').read_bytes()),cargo_lock_sha=sha((SH/'bridge/Cargo.lock').read_bytes()),command=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def native():
 b=SH/'bridge/target/release/c3x_dg_bridge';assert sha(b.read_bytes())==json.loads((D/'BUILD_ID.json').read_text())['binary_sha']
 def job(q):
  bins,n=q;tag=f'{bins}_{n}_base';out=SH/tag;cfg=F/(tag+'.cfg');env=os.environ.copy();env['R118C4H_STAGE']='1'
  args=[str(b),str(cfg),str(out),str(bins),'129','4',str(n),'19.99995','on','fine','mean','0','0'];tm=time.monotonic()
  with (D/(tag+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=280)
  if out.exists():
   for p in out.iterdir():
    if p.is_file():(D/(tag+'_'+p.name)).write_bytes(p.read_bytes())
  same={k:sha((out/k).read_bytes())==sha((F/(tag+'_'+k)).read_bytes()) for k in ['history.csv','matter.csv','stock.csv','external.csv','RETURN.txt'] if (out/k).exists()}
  raw=(D/(tag+'.log')).read_text();assert r.returncode==0 and len(same)==5 and all(same.values()) and 'C4H_STAGE,' in raw
  x=dict(tag=tag,exit=r.returncode,seconds=time.monotonic()-tm,replay_equal=same,diagnostic_lines=sum(l.startswith('C4H_STAGE,') for l in raw.splitlines()),args=args)
  print(x,flush=True);return x
 with cf.ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(job,[(1024,4),(2048,2)]))
 write('NATIVE_RUNS.json',rows)
def analyze():
 rows=[]
 for tag in ['1024_4_base','2048_2_base']:
  groups={}
  for l in (D/(tag+'.log')).read_text().splitlines():
   if not l.startswith('C4H_STAGE,'):continue
   a=l.split(',');kind=a[1];i=int(a[2]);g=groups.setdefault(i,{})
   if kind=='base':g['base']=list(map(float,a[3:]))
   elif kind=='col':g[(int(a[3]),int(a[4]))]=(int(a[5]),np.array(list(map(float,a[6:]))))
   elif kind=='check':g['check']=list(map(float,a[3:]))
  for i,g in sorted(groups.items()):
   assert 'base' in g
   if not all((j,k) in g for j in range(4) for k in range(2)):
    rows.append(dict(tag=tag,stage=i,status='INCOMPLETE_STENCIL',keys=[str(k) for k in g]));continue
   ds=[];rs=[];methods=[]
   for k in range(2):
    A=np.column_stack([g[(j,k)][1][:6] for j in range(4)]);R=np.column_stack([g[(j,k)][1][6:10] for j in range(4)]);J=np.eye(4)-A[:4];inv=np.linalg.inv(J);L=A[4:]@inv;ds.append((J,inv,L));rs.append(float(np.linalg.norm(J-R)));methods.append([g[(j,k)][0] for j in range(4)])
   fHe=.2454/(4*(1-.2454));cov=np.array([13.598434599702,fHe*24.587389011,fHe*(24.587389011+54.41776),1.])
   J,inv,L=ds[1];x=dict(tag=tag,stage=i,status='COMPLETE',a=g['base'][0],dt=g['base'][1],state=g['base'][2:6],J=J.tolist(),inverse=inv.tolist(),ledger_cmb_escape_derivative=L.tolist(),gas_energy_increment_derivative=(cov@(inv-np.eye(4))).tolist(),condition=float(np.linalg.cond(J)),inverse_residual=float(np.linalg.norm(J@inv-np.eye(4))),stencil_J_gap=float(np.linalg.norm(ds[0][0]-J)),stencil_ledger_gap=float(np.linalg.norm(ds[0][2]-L)),residual_vs_rate_J=rs,methods=methods,prediction_check=g.get('check'))
   assert x['inverse_residual']<1e-10;rows.append(x);print(x,flush=True)
 assert any(x['status']=='COMPLETE' for x in rows)
 write('STAGE_JACOBIAN.json',dict(rows=rows,scope='actual native converged implicit chemistry calls, fixed immutable prepared radiation, geometry, FF inputs and dt; local partial derivative, not composite native discrete Jacobian; finite differences of actual rate increments rather than full residual cancellation'))
if __name__=='__main__':{'build':build,'native':native,'analyze':analyze}[sys.argv[1]]()
