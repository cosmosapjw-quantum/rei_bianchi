import csv, pathlib, json, hashlib, math, re, gzip, shutil
D=pathlib.Path(__file__).resolve().parent
H=pathlib.Path.home()/'Downloads'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
runs=[]
for variant in ('continuous','search','reduced'):
 for p in sorted((H/('rei_r118c2j_'+variant)).iterdir()):
  if not p.is_dir():continue
  m=dict(l.split('=',1) for l in (p/'RETURN.txt').read_text().splitlines())
  n=int(m['accepted']); assert m['status'] in ('STOPPED_CHECKPOINTED','COMPLETE_REPRESENTED_INTERVAL')
  if m['status']=='STOPPED_CHECKPOINTED':assert 'AXBI_RUNTIME_CAP' in m['result']
  assert m['scientific_admission']=='NOT_ISSUED'
  g=0; mx=0
  with (p/'ledgers.csv').open() as f:
   for r in csv.DictReader(f):
    if r['status']=='VALUE':continue
    assert r['status']=='PASS',(p,r)
    tol=float(r['tolerance']); val=abs(float(r['residual']));assert tol>0 and val<=tol*(1+1e-12)
    mx=max(mx,val/tol);g+=1
  count=0;tau=0.;last=None;charge=0.
  with (p/'history.csv').open() as f:
   for r in csv.DictReader(f):
    t=float(r['time_s']);ne=float(r['ne_proper_cm3']);nh=float(r['nH_proper_cm3'])
    x,y,z=[float(r[k]) for k in ('x_HII','x_HeII','x_HeIII')]
    assert 0<=x<=1 and y>=0 and z>=0 and y+z<=1+1e-12
    # The inherited primordial helium fraction follows AX01.
    charge=max(charge,abs(ne/nh-(x+0.08130135170951498*(y+2*z))))
    if last is not None:
     dt=t-last[0];assert dt>0
     tau+=dt*(ne+last[1])/2*2.99792458e10*6.6524587321e-25
    last=t,ne;count+=1
  assert count==n+1 and charge<1e-10,(p,count,n,charge)
  out=dict(variant=variant,case=p.name,accepted=n,attempts=int(m['attempts']),rejections=int(m['rejections']),wall_s=float(m['wall_s']),status=m['status'],z_end=float(r['zbar']),x_HII=x,x_HeII=y,x_HeIII=z,Tm_K=float(r['temperature_K']),tau_represented=tau,gate_rows=g,max_gate_ratio=mx,charge_defect=charge,raw_path=str(p),hashes={str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file()})
  runs.append(out);print(variant,p.name,n,out['z_end'],mx,g,flush=True)
  # preserve terminal resumable state and configuration, not entire large histories.
  k=variant+'_'+p.name
  for name in ('checkpoint.txt','config.cfg','RETURN.txt','source_identity.txt'):
   b=gzip.compress((p/name).read_bytes(),mtime=0)
   (D/(k+'_'+name+'.gz')).write_bytes(b)
assert len(runs)==8
for p in (H/'rei_r118c2j_probe').iterdir():
 if p.is_file():shutil.copyfile(p,D/p.name)
for p in sorted(pathlib.Path('/tmp').glob('r118c2j*.log')):
 if any(s in p.name for s in ('_rei_','_birth_','_probe_','_search_','_flrw_','_final_build')):
  (D/(p.name+'.gz')).write_bytes(gzip.compress(p.read_bytes(),mtime=0))
def tests(name):
 s=pathlib.Path('/tmp/r118c2j_rei_'+name+'.log').read_text()
 assert 'test result: FAILED' not in s
 return sum(map(int,re.findall(r'test result: ok\. (\d+) passed',s)))
(D/'RUNS.json').write_text(json.dumps(runs,indent=2)+'\n')
A=dict(status='PASS_SCOPED',scientific_admission='LONG_CONVERGENCE_UNRESOLVED',parent='b33b7f1c5945b9ccf3c59b0168305a7063ad4490',rust_tests=tests('full'),examples=tests('examples'),best_z=min(r['z_end'] for r in runs),total_gate_rows=sum(r['gate_rows'] for r in runs),max_gate_ratio=max(r['max_gate_ratio'] for r in runs),runs=len(runs),completed=sum(r['status']=='COMPLETE_REPRESENTED_INTERVAL' for r in runs),final_binary_sha256=sha(pathlib.Path('rust/rei_microphysics/target/release/examples/axbi_covariant_recovered')),limitations=['intermediate binary hashes not captured; source_identity and raw hashes retained','all long trials runtime capped; new opt-in controller empirically checked not a global error theorem','new IC runs; C2I checkpoint unchanged'],files={f.name:sha(f) for f in sorted(D.iterdir()) if f.is_file() and f.name!='ACCEPTANCE.json'})
(D/'ACCEPTANCE.json').write_text(json.dumps(A,indent=2)+'\n');print(json.dumps({k:v for k,v in A.items() if k!='files'},indent=2))
