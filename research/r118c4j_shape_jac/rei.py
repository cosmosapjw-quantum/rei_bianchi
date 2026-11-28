"""C4J REI native selected-cell shape and redshift response with local implicit composition."""
from pathlib import Path
import os,sys,json,subprocess,tarfile,gzip,hashlib,numpy as np,time,concurrent.futures as cf
D=Path(__file__).resolve().parent;P=D.parent;F=P/'r118c4f_external_stress';H=P/'r118c4h_stage_jacobian';I=P/'r118c4i_transport_jac';SH=Path.home()/'r118c4j_rei_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n')
def build():
 arc=F/'NATIVE_SHADOW_SOURCE.tar.gz';meta=json.loads((F/'SHADOW_ARCHIVE.json').read_text());assert sha(arc.read_bytes())==meta['archive_sha256'];SH.mkdir(exist_ok=False)
 with tarfile.open(arc) as t:
  for m in t.getmembers():
   assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
   p=SH/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
 prior=json.loads((I/'BUILD_ID.json').read_text());changes={}
 for n,patch,key,tok in [('axbi_covariant_driver.rs','stage.rs.txt','new_driver_sha','                *s = next;\n                return Ok(());'),('axbi_covariant_transport.rs','transport.rs.txt','new_transport_sha','impl PreparedAbsorption {\n')]:
  p=SH/'rust/rei_microphysics/src'/n;src='instrumented_driver.rs' if 'driver' in n else 'instrumented_transport.rs';s=(I/src).read_text();assert sha(s.encode())==prior[key] and s.count(tok)==1
  s=s.replace(tok,(D/patch).read_text()+'\n'+tok if 'driver' in n else tok+(D/patch).read_text());p.write_text(s);(D/src).write_text(s);changes[str(p.relative_to(SH))]=dict(file=src,sha=sha(s.encode()),prior_sha=prior[key])
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='3';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'bridge/Cargo.toml')]
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 b=SH/'bridge/target/release/c3x_dg_bridge';raw=b.read_bytes();(D/'shape_bridge.gz').write_bytes(gzip.compress(raw,mtime=0));write('BUILD_ID.json',dict(prior_archive=meta['archive_sha256'],changes=changes,binary_sha=sha(raw),binary_archive_sha=sha((D/'shape_bridge.gz').read_bytes()),cargo_lock_sha=sha((SH/'bridge/Cargo.lock').read_bytes()),command=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def native():
 b=SH/'bridge/target/release/c3x_dg_bridge';assert sha(b.read_bytes())==json.loads((D/'BUILD_ID.json').read_text())['binary_sha']
 def job(q):
  bins,n=q;tag=f'{bins}_{n}_base';out=SH/tag;cfg=F/(tag+'.cfg');env=os.environ.copy();env['R118C4J_SHAPE']='1'
  args=[str(b),str(cfg),str(out),str(bins),'129','4',str(n),'19.99995','on','fine','mean','0','0'];tm=time.monotonic()
  with (D/(tag+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=350)
  if out.exists():
   for p in out.iterdir():
    if p.is_file():(D/(tag+'_'+p.name)).write_bytes(p.read_bytes())
  same={k:sha((out/k).read_bytes())==sha((I/(tag+'_'+k)).read_bytes()) for k in ['history.csv','matter.csv','stock.csv','external.csv','RETURN.txt'] if (out/k).exists()}
  raw=(D/(tag+'.log')).read_text();assert r.returncode==0 and len(same)==5 and all(same.values()) and 'C4J_SHAPE,base,' in raw
  row=dict(tag=tag,exit=r.returncode,seconds=time.monotonic()-tm,replay_equal=same,diagnostic_lines=sum(l.startswith('C4J_SHAPE,') for l in raw.splitlines()),args=args);print(row,flush=True);return row
 with cf.ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(job,[(1024,4),(2048,2)]))
 write('NATIVE_RUNS.json',rows)
def analyze():
 j=json.loads((H/'STAGE_JACOBIAN.json').read_text());rows=[]
 for tag in ['1024_4_base','2048_2_base']:
  groups={}
  for line in (D/(tag+'.log')).read_text().splitlines():
   if not line.startswith('C4J_SHAPE,'):continue
   a=line.split(',');key=tuple(map(int,a[2:6]));g=groups.setdefault(key,{})
   if a[1]=='base':g['base']=np.array(a[6:],float)
   elif a[1]=='col':g[('fd',int(a[6]),int(a[7]))]=np.array(a[8:],float)
   elif a[1]=='gas':g[('gas',int(a[6]))]=np.array(a[7:],float)
  for (i,pool,category,k),g in sorted(groups.items()):
   b=g['base'];n,lo,hi,m,beta,r,dn,du,nodes=b[:9];out=b[9:22];ana=np.stack([b[22:35],b[35:48]]);rows0=[]
   assert len(b)==48 and n>0 and lo<m<hi and abs(dn)<1e-8 and abs(du)<1e-8
   for mode in [0,1]:
    a=ana[mode];p0,p1=g[('fd',mode,0)],g[('fd',mode,1)];f0=p0[2:];f1=p1[2:];scale=np.maximum(np.abs(a),np.abs(f1))
    # output-wise relative gap; a zero reference/output derivative may suffer FD cancellation. normalize absolute residual by output baseline too.
    rel=np.divide(abs(a-f1),scale,out=np.zeros(13),where=scale>0)
    base_scaled=np.divide(abs(a-f1),np.maximum(abs(out),scale),out=np.zeros(13),where=np.maximum(abs(out),scale)>0)
    s2=np.maximum(abs(f0),abs(f1));stencil=np.divide(abs(f0-f1),s2,out=np.zeros(13),where=s2>0)
    rr=dict(mode=['mean','log_scale'][mode],analytic=a.tolist(),fd_coarse=f0.tolist(),fd_fine=f1.tolist(),relative_gap=rel.tolist(),base_scaled_gap=base_scaled.tolist(),stencil_gap=stencil.tolist(),same_node_count=bool(p0[0]==p0[1]==p1[0]==p1[1]==nodes),counts=[int(nodes),int(p0[0]),int(p0[1]),int(p1[0]),int(p1[1])])
    if ('gas',mode) in g:
     x=next(q for q in j['rows'] if q['tag']==tag and q['stage']==i and q['status']=='COMPLETE')
     f=g[('gas',mode)];X=np.array(x['inverse']);J=np.array(x['J']);dg=X@f[:4];L=np.array(x['ledger_cmb_escape_derivative']);rr.update(rate_increment=f.tolist(),gas_derivative=dg.tolist(),ledger_derivative=(f[4:]+L@f[:4]).tolist(),implicit_residual=float(np.linalg.norm(J@dg-f[:4])))
    rows0.append(rr)
   row=dict(tag=tag,stage=i,pool=pool,category=category,cell=k,number=n,lo=lo,hi=hi,mean=m,beta=beta,scale=r,node_count=int(nodes),number_score_defect=dn,energy_score_defect=du,base=out.tolist(),directions=rows0)
   rows.append(row);print(tag,i,pool,category,k,'nodes',nodes,'score',dn,du,[(x['mode'],max(x['base_scaled_gap']),max(x['stencil_gap']),x['same_node_count']) for x in rows0],flush=True)
 assert len(rows)>0
 write('SHAPE_JACOBIAN.json',dict(rows=rows,output_keys=['N','Uref','Gamma_H','Gamma_HeI','Gamma_HeII','heat_rate_H','heat_rate_HeI','heat_rate_HeII','events_H','events_HeI','events_HeII','binding','heat'],scope='actual selected native cells; analytic fixed-node moment score and smooth Verner log-scale derivative, compared with actual re-prepared cell stencils; crossing and moving-node branches separate; implicit local gas composition with C4H stage J, no full spectral reconstruction/coframe Jacobian'))
if __name__=='__main__':{'build':build,'native':native,'analyze':analyze}[sys.argv[1]]()
