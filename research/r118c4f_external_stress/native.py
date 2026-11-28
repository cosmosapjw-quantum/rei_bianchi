"""Instrument the exact pinned C4C native shadow, without changing its physical step or acceptance."""
from pathlib import Path
import sys,os,subprocess,json,hashlib,concurrent.futures as cf,time,re,numpy as np,gzip,tarfile,io
D=Path(__file__).resolve().parent;R=D.parents[1];P=D.parent;HOME=Path.home();SH=HOME/'r118c4f_external_shadow';C3=P/'r118c4c_dg3_gas_jacobian';C4=P/'r118c4d_refined_jacobian';PR='b145729be3d9d103ef1379c9efe5f85687558bc6';C3REV='112a133a423877bb46e0c766e158819c7e14929f';C4REV='7695ed8f7d5243c85ecd7a0a335b93fad70a8271'
def blob(rev,p):return subprocess.check_output(['git','-C',str(R),'show',rev+':'+p])
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def build():
 src=blob(C3REV,'research/r118c4c_dg3_gas_jacobian/rei.py').decode();src=src[:src.index('\ndef native():')];src=src.replace("SH=HOME/'r118c4c_dg_shadow'","SH=HOME/'r118c4f_external_shadow'")
 token=" (D/'metric_bridge_patched.rs').write_text(s)"
 assert src.count(token)==1
 # Nested triple quote generated safely from a separate source file in the scope.
 patch=(D/'instrumentation_patch.py.txt').read_text()
 src=src.replace(token,patch+'\n'+token).replace("timeout=240","timeout=330").replace("env['CARGO_BUILD_JOBS']='4'","env['CARGO_BUILD_JOBS']='6'").replace("'c4c_dg_bridge.gz'","'c4f_dg_bridge.gz'").replace("scope='original C3X physics and accepted-step gates unchanged; only initialization and initial energy reference modified'","scope='pinned C4C shadow owner with accepted-node external component diagnostics; no physics step change'")
 g={'__file__':str(D/'native.py'),'__name__':'prior','C3REV':C3REV};exec(compile(src,'C4C_build_instrumented','exec'),g);g['build']()
def native():
 b=SH/'bridge/target/release/c3x_dg_bridge';bid=json.loads((D/'BUILD_ID.json').read_text());assert sha(b.read_bytes())==bid['binary_sha'];cfg=(C4/'BASE.cfg').read_text()
 x0=float(re.search(r'^initial_x_hii=(.*)$',cfg,re.M)[1]);T0=float(re.search(r'^initial_temperature_k=(.*)$',cfg,re.M)[1]);root=SH/'runs';root.mkdir(exist_ok=False)
 cases=[('base',0.,0.,0.,0.)]+[(f'H_{e:g}',e,0.,0.,0.) for e in [-.01,.01]]+[(f'T_{e:g}',0.,0.,0.,e) for e in [-.01,.01]]+[(f'HeII_{e:g}',0.,e,0.,0.) for e in [5e-7,1e-6]]+[(f'HeIII_{e:g}',0.,0.,e,0.) for e in [5e-7,1e-6]]
 jobs=[(bins,n,*q) for bins,n in [(1024,4),(2048,2)] for q in cases]
 def job(q):
  bins,n,name,h,y,z,t=q;tag=f'{bins}_{n}_{name}';out=root/tag;cp=root/(tag+'.cfg');s=re.sub(r'^initial_x_hii=.*$',f'initial_x_hii={x0*(1+h):.17g}',cfg,flags=re.M);s=re.sub(r'^initial_temperature_k=.*$',f'initial_temperature_k={T0*(1+t):.17g}',s,flags=re.M);cp.write_text(s);(D/(tag+'.cfg')).write_text(s)
  args=[str(b),str(cp),str(out),str(bins),'129','4',str(n),'19.99995','on','fine','mean',format(y,'.17g'),format(z,'.17g')];tm=time.monotonic();r=dict(tag=tag,args=args,config_sha=sha(s.encode()))
  try:
   with (D/(tag+'.log')).open('w') as f:a=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=200)
   r['exit']=a.returncode
  except subprocess.TimeoutExpired:r['exit']=124
  r['seconds']=time.monotonic()-tm
  if out.exists():
   for name0 in ['history.csv','matter.csv','stock.csv','external.csv','RETURN.txt']:
    if (out/name0).exists():(D/(tag+'_'+name0)).write_bytes((out/name0).read_bytes())
  if r['exit']==0:
   hist=np.genfromtxt(out/'history.csv',names=True,delimiter=',');assert len(hist)==n+1 and hist['accepted'][-1]==n and 'status=COMPLETE' in (out/'RETURN.txt').read_text()
   ext=np.genfromtxt(out/'external.csv',names=True,delimiter=',',dtype=np.longdouble);assert np.array_equal(ext['a'].astype(float),hist['a'])
   equal={};diff={}
   for name0 in ['history.csv','matter.csv','stock.csv','RETURN.txt']:
    old=C4/(tag+'_'+name0);raw=(out/name0).read_bytes();equal[name0]=bool(old.is_file() and raw==old.read_bytes())
    if name0 in ['history.csv','matter.csv'] and old.is_file():
     v=np.genfromtxt(old,names=True,delimiter=',');w=np.genfromtxt(out/name0,names=True,delimiter=',');assert np.array_equal(v['a'],w['a'])
     diff[name0]=max(float(np.max(abs(v[k]-w[k]))/max(float(np.max(abs(v[k]))),1.)) for k in v.dtype.names)
   r.update(replay_equal=equal,replay_scaled_max_diff=diff,ledger=float(max(abs(hist['ledger']))),gauss=float(max(abs(hist['gauss']))),source_sha=sha((out/'source.txt').read_bytes()) if (out/'source.txt').exists() else None,external_sha=sha((out/'external.csv').read_bytes()))
  print(tag,r['exit'],r.get('replay_equal'),flush=True);return r
 rows=[]
 with cf.ThreadPoolExecutor(max_workers=6) as ex:
  for x in ex.map(job,jobs):rows.append(x);write('NATIVE_RUNS.json',rows)
 assert all(x['exit']==0 for x in rows)
if __name__=='__main__':{'build':build,'native':native}[sys.argv[1]]()
