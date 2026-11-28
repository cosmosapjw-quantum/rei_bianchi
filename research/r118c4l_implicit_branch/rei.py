"""Native implicit-stage directional probe in the C4K shadow, exact source reconstruction."""
from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,gzip,os,time,numpy as np
D=Path(__file__).resolve().parent;P=D.parent;K=P/'r118c4k_moving_nodes';F=P/'r118c4f_external_stress';SH=Path.home()/'r118c4l_rei_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def build():
 arc=F/'NATIVE_SHADOW_SOURCE.tar.gz';meta=json.loads((F/'SHADOW_ARCHIVE.json').read_text());assert sha(arc.read_bytes())==meta['archive_sha256'];SH.mkdir(exist_ok=os.environ.get('C4L_REBUILD')=='1')
 with tarfile.open(arc) as t:
  for m in t.getmembers():
   assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
   p=SH/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
 prev=json.loads((K/'BUILD_ID.json').read_text());changes={}
 for name,v in prev['changes'].items():
  s=(K/v['file']).read_text();assert sha(s.encode())==v['sha'];p=SH/name
  if 'driver' in name:
   tok='                *s = next;\n                return Ok(());';assert s.count(tok)==1;s=s.replace(tok,(D/'stage.rs.txt').read_text()+'\n'+tok)
  else:
   tok='    pub(crate) fn c4j_replace_cell(&self,k:usize,local:&Self)->Self{';assert s.count(tok)==1
   s=s.replace(tok,'''    pub(crate) fn c4l_replace_cell(&self,k:usize,local:&Self)->Self{
        let mut v=self.c4j_replace_cell(k,local);v.template.number[k]=local.template.number[0];v.template.support_lo[k]=local.template.support_lo[0];v.template.support_hi[k]=local.template.support_hi[0];v
    }
'''+tok)
  p.write_text(s);(D/v['file']).write_text(s);changes[name]=dict(file=v['file'],sha=sha(s.encode()),prior_sha=v['sha'])
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='3';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'bridge/Cargo.toml')]
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 b=SH/'bridge/target/release/c3x_dg_bridge';raw=b.read_bytes();(D/'implicit_bridge.gz').write_bytes(gzip.compress(raw,mtime=0));write('BUILD_ID.json',dict(prior_archive=meta['archive_sha256'],changes=changes,binary_sha=sha(raw),cargo_lock_sha=sha((SH/'bridge/Cargo.lock').read_bytes()),command=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def native():
 b=SH/'bridge/target/release/c3x_dg_bridge';assert sha(b.read_bytes())==json.loads((D/'BUILD_ID.json').read_text())['binary_sha'];tag='1024_4_base';out=SH/tag;cfg=F/(tag+'.cfg')
 env=os.environ.copy();env['R118C4L_IMPLICIT']='1';args=[str(b),str(cfg),str(out),'1024','129','4','4','19.99995','on','fine','mean','0','0'];tm=time.monotonic()
 with (D/(tag+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 for p in out.iterdir():
  if p.is_file():(D/(tag+'_'+p.name)).write_bytes(p.read_bytes())
 same={k:sha((out/k).read_bytes())==sha((K/(tag+'_'+k)).read_bytes()) for k in ['history.csv','matter.csv','stock.csv','external.csv','RETURN.txt']}
 raw=(D/(tag+'.log')).read_text();assert r.returncode==0 and all(same.values()) and 'C4L_SOURCE,' in raw
 write('NATIVE_RUNS.json',[dict(exit=r.returncode,seconds=time.monotonic()-tm,replay_equal=same,errors=[l for l in raw.splitlines() if l.startswith('C4L_ERROR')],command=args)])
def analyze():
 raw=(D/'1024_4_base.log').read_text();base={};rows=[];errors=[]
 for l in raw.splitlines():
  a=l.split(',')
  if a[0]=='C4L_SOURCE':src=list(map(float,a[1:]))
  elif a[0]=='C4L_ERROR':errors.append(l)
  elif a[0]=='C4L_BASE':
   key=tuple(map(int,a[1:3]));amp,norm,it,nodes=map(float,a[3:7]);v=np.array(a[7:],float);assert len(v)==4+4+21+16+84
   base[key]=dict(amp=amp,norm=norm,it=int(it),nodes=int(nodes),z=v[:4],R=v[4:8],O=v[8:29],A=v[29:45].reshape(4,4),J=v[45:].reshape(21,4))
  elif a[0]=='C4L_DIR':
   key=tuple(map(int,a[1:3]));sg,h,res,it,nodes=map(float,a[3:8]);v=np.array(a[8:],float);assert len(v)==54
   b=base[key];p,f=v[:4],v[4:8];q,g=v[8:29],v[29:50];rp=v[50:];ag=b['A']@p+rp
   # Relative errors at physical response scale; explicit numerical floors from stored root ULPs.
   floor=np.spacing(abs(b['z']))/h;se=np.maximum.reduce([abs(p),abs(f),floor]);oe=np.maximum.reduce([abs(q),abs(g),np.spacing(abs(b['O']))/h,np.full(21,1e-300)])
   row=dict(scenario=['interior','endpoint'][key[0]],amplification=b['amp'],direction=int(sg),h=h,nodes=[b['nodes'],int(nodes)],base_residual=b['norm'],solved_residual=res,iterations=int(it),cond=float(np.linalg.cond(b['A'])),implicit_solve_residual=float(np.linalg.norm(ag)),gas_pred=p.tolist(),gas_FD=f.tolist(),gas_scaled_gap=(abs(p-f)/se).tolist(),gas_abs_gap=abs(p-f).tolist(),gas_ULP_per_h=floor.tolist(),output_pred=q.tolist(),output_FD=g.tolist(),output_scaled_gap=(abs(q-g)/oe).tolist(),photon_number_balance=float(abs(q[0]+q[2:5].sum())),local_number_balance=float(abs(q[8]+q[16:19].sum())))
   rows.append(row);print(row['scenario'],b['amp'],sg,h,row['nodes'],'H',row['gas_scaled_gap'][0],'w',row['gas_scaled_gap'][3],'local',row['local_number_balance'],flush=True)
 out=dict(source=src,base=[dict(scenario=['interior','endpoint'][k[0]],amp=v['amp'],root=v['z'].tolist(),residual=v['norm'],nodes=v['nodes']) for k,v in base.items()],rows=rows,errors=errors,scope='Controlled single actual birth-cell re-preparation with actual implicit accepted chemical-stage context, one-sided finite p secants and gas Jacobian, independent re-solved roots; amplified stock diagnostic only, prescribed geometry. Not full production geometry tangent.')
 write('IMPLICIT_BRANCH.json',out);assert len(rows)==16 and not errors,(len(rows),errors)
if __name__=='__main__':{'build':build,'native':native,'analyze':analyze}[sys.argv[1]]()
