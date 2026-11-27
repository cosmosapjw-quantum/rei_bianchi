"""Pinned actual C3X DG3 binary, finite directional perturbation and exact projected harmonic memory."""
from pathlib import Path
import subprocess,hashlib,json,sys,gzip,concurrent.futures as cf,time,numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.linalg import expm
from scipy.constants import c
D=Path(__file__).resolve().parent;ROOT=D.parents[1];H=Path.home();XBASE='0e624af4668c7722759ccf781d91e15362b6d451';X='research/r118c3x_tangent_source';ZBASE='32d0724ae284a10b5e77377055c2b984e12180c2';PR='b145729be3d9d103ef1379c9efe5f85687558bc6'
def blob(rev,p):return subprocess.check_output(['git','-C',str(ROOT),'show',rev+':'+p])
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,o):(D/n).write_text(json.dumps(o,indent=2)+'\n')
def restore():
 q=json.loads(blob(XBASE,X+'/ops/BUILD_ID.json'));raw=blob(XBASE,X+'/ops/c3x_dg_bridge.gz');b=gzip.decompress(raw);assert sha(raw)==q['binary']['archive_sha256'] and sha(b)==q['binary']['sha256']
 root=H/'r118c4b_dg_scratch';root.mkdir(exist_ok=False);exe=root/'c3x_dg_bridge';exe.write_bytes(b);exe.chmod(0o700)
 cfg=blob(PR,'research/r118c3i_event_ledger/table.cfg');(D/'BASE.cfg').write_bytes(cfg)
 write('BINARY_ID.json',dict(pinned=XBASE,original_PR=PR,binary_sha256=sha(b),archive_sha256=sha(raw),config_sha256=sha(cfg),source_identity=q['identity'],build_scope='exact archived C3X executable; no rebuild or source mutation'))
 return root,exe,cfg.decode()
def native():
 root,exe,cfg=restore()
 # Use fresh config/initial-reference energy per signed perturbation; same geometry IC and final a.
 # 1024 2/4 steps on short interval; independent 2048 and full 4096 refinement.
 import re
 x0=float(re.search(r'^initial_x_hii=(.*)$',cfg,re.M)[1]);T0=float(re.search(r'^initial_temperature_k=(.*)$',cfg,re.M)[1])
 cases=[(1024,2,0.),(1024,2,-.01),(1024,2,.01),(1024,4,0.),(1024,4,-.01),(1024,4,.01),(1024,4,-.005),(1024,4,.005),(2048,4,0.),(2048,4,-.01),(2048,4,.01),(4096,8,0.)]
 def job(q):
  bins,n,e=q;tag=f'dg_{bins}_{n}_{e:g}';out=root/tag;config=root/(tag+'.cfg')
  # Physical directional perturbation x increases, T decreases. Direction specified in dimensionless fractions.
  s=re.sub(r'^initial_x_hii=.*$',f'initial_x_hii={x0*(1+e):.17g}',cfg,flags=re.M);s=re.sub(r'^initial_temperature_k=.*$',f'initial_temperature_k={T0*(1-e):.17g}',s,flags=re.M)
  config.write_text(s);end=19.9998 if bins==4096 else 19.99995
  args=[str(exe),str(config),str(out),str(bins),'129','4',str(n),str(end),'on','fine','mean']
  t=time.monotonic();result=dict(case=tag,bins=bins,steps=n,eps=e,z_end=end,config_sha256=sha(s.encode()),command=args)
  try:
   with (D/(tag+'.log')).open('w') as log:r=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,timeout=160)
   result['exit']=r.returncode
  except subprocess.TimeoutExpired:result['exit']=124
  result['seconds']=time.monotonic()-t
  if result['exit']==0:
   h=np.genfromtxt(out/'history.csv',names=True,delimiter=',');a=np.genfromtxt(out/'matter.csv',names=True,delimiter=',');ret=(out/'RETURN.txt').read_text()
   assert len(h)==n+1 and len(a)==len(h) and 'status=COMPLETE' in ret and int(h['accepted'][-1])==n
   for name in ['history.csv','matter.csv','RETURN.txt','stock.csv']:
    (D/(tag+'_'+name)).write_bytes((out/name).read_bytes())
   result['source_sha256']=sha((out/'source.txt').read_bytes());assert result['source_sha256']=='12758019c9c3827562e7eba091a94d93018e0b0d43ba6c29b36c325ae86912cf'
   result.update(accepted=n,max_ledger=float(np.max(abs(h['ledger']))),max_gauss=float(np.max(abs(h['gauss']))),max_metric=float(np.max(h['metric'])),min_margin=float(np.min(h['margin'])),terminal={k:float(h[k][-1]) for k in ['a','h','T','xHII','xHeII','xHeIII','S0','S1','S2','S3','S4','thermal','binding','spec','corr_U','corr_N','corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz']})
  (D/(tag+'.cfg')).write_text(s);print(result,flush=True)
  return result
 with cf.ThreadPoolExecutor(max_workers=3) as ex:
  rows=[]
  for r in ex.map(job,cases):rows.append(r);write('NATIVE_RUNS.json',rows)
def analyze():
 rows=json.loads((D/'NATIVE_RUNS.json').read_text());good={(r['bins'],r['steps'],r['eps']):r for r in rows if r['exit']==0};results={}
 keys=['h','T','xHII','xHeII','xHeIII','S0','S1','S2','S3','S4','thermal','binding','spec','corr_U','corr_N','corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz']
 for bins,n in [(1024,2),(1024,4),(2048,4)]:
  if (bins,n,0.) not in good:continue
  r0=good[bins,n,0.];v0=np.array([r0['terminal'][k] for k in keys]);res={}
  for e in [.01,.005]:
   if not all((bins,n,sg*e) in good for sg in [-1,1]):continue
   a,b=[np.array([good[bins,n,sg*e]['terminal'][k] for k in keys]) for sg in [-1,1]]
   assert good[bins,n,-e]['terminal']['a']==good[bins,n,e]['terminal']['a']==r0['terminal']['a']
   f=(b-a)/(2*e);even=(b+a-2*v0)/(2*e**2)
   res[str(e)]=dict(derivative=dict(zip(keys,f.tolist())),even=dict(zip(keys,even.tolist())),state_scale=dict(zip(keys,v0.tolist())))
  results[f'{bins}_{n}']=res
 # Check terminal directional derivative variation (gas and signed correction separately).
 comp=[]
 for a,b in [('1024_2','1024_4'),('1024_4','2048_4')]:
  if all(x in results and '.01' in results[x] for x in [a,b]):pass
  if all(x in results and '0.01' in results[x] for x in [a,b]):
   A=results[a]['0.01']['derivative'];B=results[b]['0.01']['derivative']
   comp.append(dict(a=a,b=b,relative={k:abs(B[k]-A[k])/max(abs(B[k]),1e-300) for k in keys}))
 if '1024_4' in results and all(e in results['1024_4'] for e in ['0.01','0.005']):
  A=results['1024_4']['0.01']['derivative'];B=results['1024_4']['0.005']['derivative']
  comp.append(dict(a='eps.01',b='eps.005',relative={k:abs(B[k]-A[k])/max(abs(B[k]),1e-300) for k in keys}))
 # 4096 full interval compare exact old C3X accepted endpoint, no claim of bitwise config match.
 full={}
 if (4096,8,0.) in good:
  import io
  old=np.genfromtxt(io.BytesIO(blob(XBASE,X+'/fine_2048_129_32_8/history.csv')),names=True,delimiter=',')
  q=good[4096,8,0.];full={k:{'old2048':float(old[k][-1]),'new4096':q['terminal'][k],'relative':abs(q['terminal'][k]-old[k][-1])/max(abs(q['terminal'][k]),1e-300)} for k in keys}
 out=dict(complete=sum(r['exit']==0 for r in rows),cases=len(rows),results=results,comparisons=comp,full_interval_4096_vs_prior=full,scope='central directional finite differences of actual C3X DG3 self-consistent accepted map, conditional fresh initial perturbation; no full Jacobian; compare prior clock/config only within explicit metadata')
 write('DIRECTIONAL.json',out);print(json.dumps(out),flush=True)
def memory():
 import io
 old=blob(ZBASE,'research/r118c3z_harmonic_memory/rei.py');ns={'__file__':str(D/'memory_prior.py'),'__name__':'c4b_memory_prior'};exec(compile(old,'C3Z/rei.py','exec'),ns)
 operators,collision=ns['operators'],ns['collision'];H0=ns['H0'];SIG=ns['SIG']
 # Actual C3U trajectory (longer) and C3X short. Same native harmonic generator; exact finite projection.
 b=blob(XBASE,'research/r118c3u_positive_owner/birth_1024_32ray/history.csv');h=np.genfromtxt(io.BytesIO(b),names=True,delimiter=',')
 m=blob(XBASE,X+'/fine_2048_129_32_8/matter.csv');g=blob(XBASE,X+'/fine_2048_129_32_8/history.csv')
 matter=np.genfromtxt(io.BytesIO(m),names=True,delimiter=',');hist=np.genfromtxt(io.BytesIO(g),names=True,delimiter=',')
 cases=[('C3U',h,h['ne']*1e6,sha(b),32),('C3X',hist,matter['ne_m3'],sha(g),8)]
 res=[]
 for label,h,ne,hs,nt in cases:
  u=np.log(h['a']/h['a'][0]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);K=c*SIG*ne/(H0*h['h']);f=PchipInterpolator(u,np.c_[S,K],axis=0)
  for l in [4,6]:
   ops,identity=operators(l);m=(l+1)**2;N=3*m;I=np.eye(N,dtype=complex)
   C=np.column_stack([collision(I[:,i],m) for i in range(N)]);mat=np.array([a.toarray() for a in ops]);p=np.arange(4,9);q=np.setdiff1d(np.arange(N),p);y0=np.zeros(N,complex);y0[0]=np.sqrt(4*np.pi)
   for n in [nt,2*nt]:
    t=np.linspace(u[0],u[-1],n+1);full=y0.copy();pr=y0[p].copy();slip=y0[q].copy();terms=[];no_mem=pr.copy()
    for j in range(n):
     hh=t[j+1]-t[j];row=f((t[j]+t[j+1])/2);A=np.einsum('k,kij->ij',row[:5],mat)+row[5]*C;E=expm(hh*A);F,G,Hh,J=E[np.ix_(p,p)],E[np.ix_(p,q)],E[np.ix_(q,p)],E[np.ix_(q,q)]
     qr=slip+sum(terms,start=np.zeros(len(q),complex));new=F@pr+G@qr
     no_mem=F@no_mem+G@slip;terms=[J@z for z in terms]+[Hh@pr];slip=J@slip;pr=new;full=E@full
    qr=slip+sum(terms,start=np.zeros(len(q),complex));err=np.linalg.norm(pr-full[p])/max(np.linalg.norm(full[p]),1e-300);qerr=np.linalg.norm(qr-full[q])/np.linalg.norm(full[q]);assert err<1e-11 and qerr<1e-11
    res.append(dict(case=label,lmax=l,steps=n,history_sha=hs,identity=identity,exact_projection_relative=float(err),complement_relative=float(qerr),resolved_norm=float(np.linalg.norm(full[p])),initial_slip_complement_norm=float(np.linalg.norm(slip)),memory_complement_norm=float(np.linalg.norm(sum(terms,start=np.zeros(len(q),complex)))),omit_memory_relative=float(np.linalg.norm(no_mem-full[p])/np.linalg.norm(full[p])),resolved_re=full[p].real.tolist(),resolved_im=full[p].imag.tolist(),tau=float(np.trapezoid(K,u))))
    print(label,l,n,res[-1]['exact_projection_relative'],res[-1]['omit_memory_relative'],flush=True)
 write('HARMONIC_MEMORY.json',dict(rows=res,scope='actual native finite harmonic generator, piecewise midpoint exponential maps, exact discrete elimination of all non-intensity-l2 modes with initial slip; no continuum or full nonlinear closure'))
if __name__=='__main__':{'native':native,'analyze':analyze,'memory':memory}[sys.argv[1]]()

