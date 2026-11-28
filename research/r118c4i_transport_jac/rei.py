"""Restore C4F exact shadow and C4H driver; add actual prepared-node tangent and amplitude perturbation."""
from pathlib import Path
import os,sys,json,subprocess,tarfile,gzip,hashlib,numpy as np,time,concurrent.futures as cf
D=Path(__file__).resolve().parent;P=D.parent;F=P/'r118c4f_external_stress';H=P/'r118c4h_stage_jacobian';SH=Path.home()/'r118c4i_rei_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n')
def build():
 arc=F/'NATIVE_SHADOW_SOURCE.tar.gz';meta=json.loads((F/'SHADOW_ARCHIVE.json').read_text());assert sha(arc.read_bytes())==meta['archive_sha256'];SH.mkdir(exist_ok=False)
 with tarfile.open(arc) as t:
  for m in t.getmembers():
   assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
   p=SH/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
 p=SH/'rust/rei_microphysics/src/axbi_covariant_driver.rs';prior=json.loads((H/'BUILD_ID.json').read_text());assert sha(p.read_bytes())==prior['old_driver_sha'];s=(H/'instrumented_driver.rs').read_text();assert sha(s.encode())==prior['new_driver_sha']
 a0='                // C4H research-only accepted chemical-substage diagnostic.';assert s.count(a0)==1;s=s.replace(a0,'                let mut c4i_local_jac:Option<[[f64;4];4]>=None;\n'+a0)
 a1='                            if ok { if let Ok(v)=solve4(jac,[1.,0.,0.,0.]) {';assert s.count(a1)==1;s=s.replace(a1,'                            if ok { c4i_local_jac=Some(jac); if let Ok(v)=solve4(jac,[1.,0.,0.,0.]) {')
 tok='                *s = next;\n                return Ok(());';assert s.count(tok)==1;s=s.replace(tok,(D/'stage_patch.rs.txt').read_text()+'\n'+tok);p.write_text(s);(D/'instrumented_driver.rs').write_text(s)
 q=SH/'rust/rei_microphysics/src/axbi_covariant_transport.rs';s=q.read_text();orig=sha(s.encode());tok='impl PreparedAbsorption {\n';assert s.count(tok)==1;s=s.replace(tok,tok+(D/'transport_patch.rs.txt').read_text());q.write_text(s);(D/'instrumented_transport.rs').write_text(s)
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='3';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'bridge/Cargo.toml')]
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 b=SH/'bridge/target/release/c3x_dg_bridge';raw=b.read_bytes();(D/'transport_bridge.gz').write_bytes(gzip.compress(raw,mtime=0));write('BUILD_ID.json',dict(prior_archive=meta['archive_sha256'],old_driver_sha=prior['new_driver_sha'],new_driver_sha=sha(p.read_bytes()),old_transport_sha=orig,new_transport_sha=sha(q.read_bytes()),binary_sha=sha(raw),binary_archive_sha=sha((D/'transport_bridge.gz').read_bytes()),cargo_lock_sha=sha((SH/'bridge/Cargo.lock').read_bytes()),command=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def native():
 b=SH/'bridge/target/release/c3x_dg_bridge';assert sha(b.read_bytes())==json.loads((D/'BUILD_ID.json').read_text())['binary_sha']
 def job(q):
  bins,n=q;tag=f'{bins}_{n}_base';out=SH/tag;cfg=F/(tag+'.cfg');env=os.environ.copy();env['R118C4H_STAGE']='1';env['R118C4I_TRANSPORT']='1'
  args=[str(b),str(cfg),str(out),str(bins),'129','4',str(n),'19.99995','on','fine','mean','0','0'];tm=time.monotonic()
  with (D/(tag+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=350)
  if out.exists():
   for p in out.iterdir():
    if p.is_file():(D/(tag+'_'+p.name)).write_bytes(p.read_bytes())
  same={k:sha((out/k).read_bytes())==sha((H/(tag+'_'+k)).read_bytes()) for k in ['history.csv','matter.csv','stock.csv','external.csv','RETURN.txt'] if (out/k).exists()}
  raw=(D/(tag+'.log')).read_text();prior=(H/(tag+'.log')).read_text();old=[l for l in prior.splitlines() if l.startswith('C4H_STAGE,')];new=[l for l in raw.splitlines() if l.startswith('C4H_STAGE,')]
  assert r.returncode==0 and len(same)==5 and all(same.values()) and old==new and 'C4I_TRANS,' in raw
  row=dict(tag=tag,exit=r.returncode,seconds=time.monotonic()-tm,replay_equal=same,C4H_diagnostic_equal=old==new,diagnostic_lines=sum(l.startswith('C4I_TRANS,') for l in raw.splitlines()),args=args);print(row,flush=True);return row
 with cf.ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(job,[(1024,4),(2048,2)]))
 write('NATIVE_RUNS.json',rows)
def analyze():
 prior=json.loads((H/'STAGE_JACOBIAN.json').read_text());rows=[]
 for tag in ['1024_4_base','2048_2_base']:
  groups={}
  for l in (D/(tag+'.log')).read_text().splitlines():
   if not l.startswith('C4I_TRANS,'):continue
   a=l.split(',');g=groups.setdefault(int(a[2]),{});k=a[1]
   if k=='base':g['base']=np.array(a[3:],float)
   elif k=='col':g[('col',int(a[3]))]=(int(a[4]),np.array(a[5:],float))
   elif k=='amp':g[('amp',int(a[3]),int(a[4]))]=np.array(a[5:],float)
   elif k=='check':g[('check',int(a[3]))]=np.array(a[4:],float)
  for i,g in sorted(groups.items()):
   x=next(r for r in prior['rows'] if r['tag']==tag and r['stage']==i and r['status']=='COMPLETE')
   b=g['base'];nh=b[0];ab=b[1:4];base=b[4:17];old=b[17:30];birth=b[30:43];a=np.column_stack([g[('col',j)][1][:13] for j in range(3)]);fd=np.column_stack([g[('col',j)][1][13:] for j in range(3)])
   assert np.allclose(base,old+birth,rtol=1e-13,atol=0)
   # use physically distinct output rows, not a dimensionally mixed norm
   scale=np.maximum(np.max(abs(a),axis=1),np.max(abs(fd),axis=1));rel=np.divide(np.max(abs(a-fd),axis=1),scale,out=np.zeros(13),where=scale>0)
   # zero derivative of total photon number + absorption, per absorber; normalize by sum of absolute terms
   cons=a[0]+a[8:11].sum(0);den=abs(a[0])+abs(a[8:11]).sum(0);err=np.divide(abs(cons),den,out=np.zeros(3),where=den>0)
   X=np.array(x['inverse']);f0=np.column_stack([g[('amp',k,0)] for k in range(2)]);f1=np.column_stack([g[('amp',k,1)] for k in range(2)]);dg=X@f0[:4];L=np.array(x['ledger_cmb_escape_derivative']);J=np.array(x['J']);local_out=f0[4:]+L@f0[:4] # d ledger = direct + ledger_z J^-1 rate_amp
   # fractions xHII,HeII,HeIII per species -> absorber number cm^-3
   fHe=.2454/(4*(1-.2454));Dab=np.array([[-nh,0,0,0],[0,-nh*fHe,-nh*fHe,0],[0,nh*fHe,0,0]])
   # incoming amplitude changes prepared stock directly and trial absorber densities indirectly
   direct=np.column_stack([old,birth]);composed=direct+a@Dab@dg
   out=dict(tag=tag,stage=i,nh=nh,absorbers=ab.tolist(),base=base.tolist(),old=old.tolist(),birth=birth.tolist(),analytic=a.tolist(),finite_difference=fd.tolist(),output_relative_gap=rel.tolist(),number_derivative_balance=err.tolist(),FD_modes=[g[('col',j)][0] for j in range(3)],amplitude_rate_increment=f0.tolist(),amplitude_stencil_gap=np.linalg.norm(f0-f1,axis=0).tolist(),gas_amplitude_response=dg.tolist(),implicit_residual=np.linalg.norm(J@dg-f0[:4],axis=0).tolist(),composed_transport_response=composed.tolist(),composed_cmb_escape=local_out.tolist(),predicted_residual_check={str(k):g[('check',k)].tolist() for k in range(2) if ('check',k) in g})
   assert np.all(np.isfinite(a)) and max(err)<1e-12
   rows.append(out);print(tag,i,'rel',rel,'N balance',err,'amp gas',dg,flush=True)
 assert len(rows)==6
 write('TRANSPORT_JACOBIAN.json',dict(rows=rows,output_keys=['N','Uref','Gamma_H','Gamma_HeI','Gamma_HeII','heat_rate_H','heat_rate_HeI','heat_rate_HeII','events_H','events_HeI','events_HeII','binding_eV_per_H','heat_eV_per_H'],scope='actual frozen prepared quadrature node derivatives; common old/birth amplitude derivative of native implicit stage and composed gas/stock response; fixed geometry, support and reconstruction; not full coupled native derivative'))
if __name__=='__main__':{'build':build,'native':native,'analyze':analyze}[sys.argv[1]]()
