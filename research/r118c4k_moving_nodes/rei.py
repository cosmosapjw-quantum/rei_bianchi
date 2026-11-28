"""C4K native controlled threshold and steep probes, actual moving-node moment tangent."""
from pathlib import Path
import sys,json,subprocess,hashlib,tarfile,gzip,os,time,numpy as np
D=Path(__file__).resolve().parent;P=D.parent;J=P/'r118c4j_shape_jac';F=P/'r118c4f_external_stress';SH=Path.home()/'r118c4k_rei_shadow'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def build():
 arc=F/'NATIVE_SHADOW_SOURCE.tar.gz';meta=json.loads((F/'SHADOW_ARCHIVE.json').read_text());assert sha(arc.read_bytes())==meta['archive_sha256'];SH.mkdir(exist_ok=os.environ.get('C4K_REBUILD')=='1')
 with tarfile.open(arc) as t:
  for m in t.getmembers():
   assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
   p=SH/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
 prev=json.loads((J/'BUILD_ID.json').read_text());changes={}
 for name,v in prev['changes'].items():
  src=J/v['file'];s=src.read_text();assert sha(s.encode())==v['sha'];p=SH/name
  if 'driver' in name:
   tok='                *s = next;\n                return Ok(());';assert s.count(tok)==1;s=s.replace(tok,(D/'stage.rs.txt').read_text()+'\n'+tok)
  else:
   tok='impl PreparedAbsorption {\n';assert s.count(tok)==1;s=s.replace(tok,tok+(D/'probe.rs.txt').read_text())
  p.write_text(s);(D/v['file']).write_text(s);changes[name]=dict(file=v['file'],sha=sha(s.encode()),prior_sha=v['sha'])
 env=os.environ.copy();env['CARGO_BUILD_JOBS']='3';cmd=['cargo','build','--offline','--release','--manifest-path',str(SH/'bridge/Cargo.toml')]
 with (D/'build.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=450)
 assert r.returncode==0
 b=SH/'bridge/target/release/c3x_dg_bridge';raw=b.read_bytes();(D/'moving_bridge.gz').write_bytes(gzip.compress(raw,mtime=0));write('BUILD_ID.json',dict(prior_archive=meta['archive_sha256'],changes=changes,binary_sha=sha(raw),cargo_lock_sha=sha((SH/'bridge/Cargo.lock').read_bytes()),command=cmd,rustc=subprocess.check_output(['rustc','--version'],text=True).strip()))
def native():
 b=SH/'bridge/target/release/c3x_dg_bridge';assert sha(b.read_bytes())==json.loads((D/'BUILD_ID.json').read_text())['binary_sha'];tag='1024_4_base';out=SH/tag;cfg=F/(tag+'.cfg')
 env=os.environ.copy();env['R118C4K_MOVING']='1'
 args=[str(b),str(cfg),str(out),'1024','129','4','4','19.99995','on','fine','mean','0','0'];tm=time.monotonic()
 with (D/(tag+'.log')).open('w') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=350)
 for p in out.iterdir():
  if p.is_file():(D/(tag+'_'+p.name)).write_bytes(p.read_bytes())
 same={k:sha((out/k).read_bytes())==sha((J/(tag+'_'+k)).read_bytes()) for k in ['history.csv','matter.csv','stock.csv','external.csv','RETURN.txt']}
 raw=(D/(tag+'.log')).read_text();assert r.returncode==0 and all(same.values()) and 'C4K_SOURCE,' in raw
 row=dict(tag=tag,exit=r.returncode,seconds=time.monotonic()-tm,replay_equal=same,diagnostic_lines=sum(l.startswith('C4K_') for l in raw.splitlines()),args=args)
 write('NATIVE_RUNS.json',[row]);print(row,flush=True)
def parse():
 raw=(D/'1024_4_base.log').read_text();cases={};invalid=[]
 for l in raw.splitlines():
  s=l.split(',')
  if s[0]=='C4K_SOURCE':source=list(map(float,s[1:]))
  elif s[0]=='C4K_CASE':
   key=(int(s[1]),int(s[2]),float(s[3]));v=np.array(s[4:],float)
   assert len(v)==25,(len(v),l);cases[key]=dict(r=v[0],mean=v[1],scheme=int(v[2]),nh=v[3],dt=v[4],a=v[5:8],n=v[8],lo=v[9],hi=v[10],count=int(v[11]),out=v[12:],nodes=[])
  elif s[0]=='C4K_NODE':
   key=(int(s[1]),int(s[2]),float(s[3]));r=cases[key];assert int(s[4])==len(r['nodes']);r['nodes'].append(list(map(float,s[5:])))
  elif s[0]=='C4K_INVALID':invalid.append(l)
 for r in cases.values():
  r['nodes']=np.array(r['nodes']);assert r['nodes'].shape==(r['count'],8) and len(r['out'])==13
  assert abs(r['nodes'][:,1].sum()/r['n']-1)<1e-12
 return source,cases,invalid
# Native CGS constants from HHeModel::controlled_fixture, exact values read from source below.
C=2.99792458e10;EV=1.602176634e-12
def bgeom(q):
 assert len(q)%8==0
 # For both moderate and steep branch, original base weight is GL weight times physical panel width times exp(k q).
 gl,gw=np.polynomial.legendre.leggauss(8);qq=q.reshape(-1,8);width=abs(qq[:,-1]-qq[:,0])/(gl[-1]-gl[0])
 return (width[:,None]*gw).ravel()
def evald(r,dq,dw,dlogr):
 q,w=r['nodes'][:,:2].T;sig=r['nodes'][:,2:5];ex=r['nodes'][:,5:8];a=r['a'];cd=C*r['dt'];E=q*r['r'];dE=r['r']*(dq+q*dlogr);dlogE=dE/E
 dsig=np.zeros_like(sig)
 for j,(e0,ya,p,yw,y0,y1) in enumerate([(0.4298,32.88,2.963,0.,0.,0.),(13.61,1.469,3.188,2.039,.4434,2.136),(1.720,32.88,2.963,0.,0.,0.)]):
  x=E/e0-y0;y=np.hypot(x,y1);z=np.sqrt(y/ya)
  dlog=(2*(x-1)/((x-1)**2+yw*yw)+(p/2-5.5-p*.5*z/(1+z))*x/y**2)*E/e0
  dsig[:,j]=sig[:,j]*dlog*dlogE
 X=cd*(sig@a);dX=cd*(dsig@a);exp=np.exp(-X);phi=np.ones_like(X);psi=np.full_like(X,.5);dp=np.full_like(X,-.5);dpsi=np.full_like(X,-1/6)
 z=X>=.05;v=X[z];phi[z]=-np.expm1(-v)/v;psi[z]=(1-phi[z])/v;dp[z]=(exp[z]-phi[z])/v;dpsi[z]=(-dp[z]-psi[z])/v
 # stable Taylor for X small.
 xx=X[~z]
 import math
 phi[~z]=sum((-1)**k*xx**k/math.factorial(k+1) for k in range(15))
 psi[~z]=sum((-1)**k*xx**k/math.factorial(k+2) for k in range(15))
 dp[~z]=sum((-1)**k*k*xx**(k-1)/math.factorial(k+1) for k in range(1,15))
 dpsi[~z]=sum((-1)**k*k*xx**(k-1)/math.factorial(k+2) for k in range(1,15))
 sc=r['scheme']
 if sc==0:s=mean=1/(1+X);ds=dm=-s*s*dX
 elif sc==1:s,mean=exp,phi;ds=-exp*dX;dm=dp*dX
 else:s,mean=phi,psi;ds=dp*dX;dm=dpsi*dX
 S=w*s;dS=dw*s+w*ds;M=w*mean;dM=dw*mean+w*dm
 events=cd*a*sig*M[:,None];devents=cd*a*(dsig*M[:,None]+sig*dM[:,None]);rate=C*r['nh']*sig*M[:,None];drate=C*r['nh']*(dsig*M[:,None]+sig*dM[:,None]);dex=np.where(sig>0,dE[:,None],0.)
 # Binding thresholds are not the Verner thresholds; use native excess = E - binding.
 binding=np.where(sig>0,E[:,None]-ex,0.)
 base=np.r_[S.sum(),S@q,rate.sum(0),(rate*ex*EV).sum(0),events.sum(0),(events*binding).sum(),(events*ex).sum()]
 out=np.r_[dS.sum(),dS@q+S@dq,drate.sum(0),((drate*ex+rate*dex)*EV).sum(0),devents.sum(0),(devents*binding).sum(),(devents*ex+events*dex).sum()]
 return base,out
def analyze():
 source,cases,invalid=parse();rows=[];arrays={}
 # Native physical constants (checked against actual owner source by build).
 for id,label in enumerate(['actual_smooth','interior_HI_cross','steep_interior_cross','support_endpoint_cross','beta30_transition']):
  r=cases[id,0,0.];q,w=r['nodes'][:,:2].T;n=r['n'];p=w/n;mu=p@q;var=p@((q-mu)**2);ms=min(r['mean']-r['lo'],r['hi']-r['mean'])
  b=bgeom(q);logw=np.log(w/b);kappa=(p@((q-mu)*(logw-p@logw)))/var
  resid=float(max(abs(logw-(p@logw+kappa*(q-mu)))));assert var>0 and resid<1e-7,(id,resid)
  base,zero=evald(r,np.zeros_like(q),np.zeros_like(q),0.);scale=np.maximum(abs(base),abs(r['out']));err=float(max(np.divide(abs(base-r['out']),scale,out=np.zeros_like(scale),where=scale>0)))
  assert err<1e-7,(id,err,base,r['out'])
  for mode in [0,1]:
   for h in [1e-3,1e-4]:
    if (id,mode,h) not in cases or (id,mode,-h) not in cases:
     rows.append(dict(id=id,scenario=label,mode=mode,h=h,status='INVALID_BRANCH'));continue
    up,um=cases[id,mode,h],cases[id,mode,-h];fd=(up['out']-um['out'])/(2*h);dp=(up['out']-r['out'])/h;dm=(r['out']-um['out'])/h
    counts=[r['count'],up['count'],um['count']]
    vscale=np.maximum(abs(fd),abs(r['out']));sided=float(max(np.divide(abs(dp-dm),vscale,out=np.zeros_like(fd),where=vscale>0)))
    row=dict(id=id,scenario=label,mode=['mean','log_scale'][mode],h=h,counts=counts,kappa=float(kappa),logweight_defect=resid,base_relative_gap=err,sided_scaled_gap=sided,fd=fd.tolist())
    if len(set(counts))!=1:
     row.update(status='TOPOLOGY_CHANGE',plus=dp.tolist(),minus=dm.tolist());rows.append(row);print(row,flush=True);continue
    qp,qm=up['nodes'][:,0],um['nodes'][:,0]
    if not np.array_equal(up['nodes'][:,2:5]>0,um['nodes'][:,2:5]>0):
     row.update(status='NODE_THRESHOLD_BRANCH_CHANGE',plus=dp.tolist(),minus=dm.tolist());rows.append(row);print(row,flush=True);continue
    dq=(qp-qm)/(2*h);db=(np.log(bgeom(qp))-np.log(bgeom(qm)))/(2*h);dmu=ms if mode==0 else 0.
    l=db+kappa*dq;dk=(dmu-p@dq-p@((q-mu)*l))/var;dw=w*(l-p@l+dk*(q-mu))
    number=float(dw.sum()/n);energy=float((dw@q+w@dq)/n-dmu)
    _,a=evald(r,dq,dw,float(mode));_,fixed=evald(r,np.zeros_like(q),w*(q-mu)*dmu/var,float(mode))
    nd=float((a[0]+a[8:11].sum())/n)
    es=np.maximum.reduce([abs(fd),abs(a),abs(r['out'])]);e=np.divide(abs(fd-a),es,out=np.zeros_like(fd),where=es>0);ef=np.divide(abs(fd-fixed),es,out=np.zeros_like(fd),where=es>0)
    row.update(status='SAME_TOPOLOGY',number_defect=number,energy_defect=energy,photon_derivative_defect=nd,scaled_gap=e.tolist(),fixed_node_scaled_gap=ef.tolist(),analytic=a.tolist(),max_scaled_gap=float(max(e)),max_fixed_node_gap=float(max(ef)),node_motion_norm=float(np.linalg.norm(dq)))
    assert abs(number)<1e-9 and abs(energy)<1e-9 and abs(nd)<1e-8,(id,mode,h,row)
    if id==1 and mode==1:
     cut=13.60/r['r'];qpred=np.where(q<cut,-cut*(q-r['lo'])/(cut-r['lo']),-cut*(r['hi']-q)/(r['hi']-cut))
     row['moderate_cut_node_motion_relative']=float(np.linalg.norm(dq-qpred)/np.linalg.norm(qpred))
    rows.append(row);print(id,label,mode,h,row['status'],counts,row.get('max_scaled_gap'),row.get('max_fixed_node_gap'),flush=True)
 write('MOVING_NODES.json',dict(source=source,rows=rows,invalid=invalid,native_source_sha=json.loads((D/'BUILD_ID.json').read_text())['binary_sha'],scope='controlled local re-preparation of one actual represented birth cell; implicit discrete moment tilt with centered node/panel motion; smooth Verner derivative on fixed topology; explicit topology-change classification, not full actual cosmological threshold trajectory'))
if __name__=='__main__':{'build':build,'native':native,'analyze':analyze}[sys.argv[1]]()
