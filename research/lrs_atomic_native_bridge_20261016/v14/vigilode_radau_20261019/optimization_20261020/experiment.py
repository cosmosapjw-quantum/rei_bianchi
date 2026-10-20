"""Bounded offline optimization evidence. No publication or scientific admission."""
from pathlib import Path
import subprocess,os,json,time,hashlib,resource,statistics,math,sys
W=Path(os.environ.get('LRS_OPT_WORKSPACE',str(Path(__file__).resolve().parent))); E=Path(os.environ.get('LRS_OPT_EVIDENCE',str(W/'experiments'))); E.mkdir(exist_ok=True)
BASE=W/'immutable_baseline/rei-vigilode-radau-research'; CAND=W/'target_baseline/release/rei-vigilode-radau-research'; CPU=min(os.sched_getaffinity(0))
ENV=os.environ.copy();ENV.update(PATH=str(W/'rust_prefix/bin')+':'+ENV['PATH'],RUSTC=str(W/'rust_prefix/bin/rustc'),CARGO_HOME=str(W/'cargo_home'),CARGO_TARGET_DIR=str(W/'target_baseline'),CARGO_BUILD_JOBS='2',LD_LIBRARY_PATH=str(W/'rust_prefix/lib'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,argv,timeout=30):
 d=E/name;d.mkdir();(d/'inputs.json').write_text(json.dumps({'argv':list(map(str,argv)),'cpu':CPU,'timeout_s':timeout,'binary_sha256':sha(argv[3]) if argv[0]=='taskset' else None},indent=2));start=time.monotonic()
 with (d/'stdout.txt').open('wb') as so,(d/'stderr.txt').open('wb') as se:
  try:p=subprocess.run(list(map(str,argv)),env=ENV,stdout=so,stderr=se,timeout=timeout);code=p.returncode
  except subprocess.TimeoutExpired:code=None
 outcome={'exit':code,'process_wall_s':time.monotonic()-start,'peak_children_rss_kb_cumulative':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss};(d/'outcome.json').write_text(json.dumps(outcome,indent=2));print(name,outcome,flush=True)
 if code!=0:raise RuntimeError(name)
 return d

def case(name,binary,mode,method,n,variant=None,profile=False):
 d=E/name
 if (d/'raw.json').exists() and json.loads((d/'outcome.json').read_text())['exit']==0:return json.loads((d/'raw.json').read_text())
 argv=['taskset','-c',str(CPU),str(binary),str(d/'raw.json'),mode,method,str(n)]
 if variant:argv+=['--native-eval',variant]
 if profile:argv+=['--profile']
 run(name,argv);return json.loads((d/'raw.json').read_text())
SKIP={'wall_s','native_evaluation'}
def compare(a,b,path='$',issues=None):
 if issues is None:issues=[]
 if isinstance(a,dict) and isinstance(b,dict):
  for k in (set(a)|set(b))-SKIP:
   if k not in a or k not in b:issues.append({'path':path+'.'+k,'reason':'missing'})
   else:compare(a[k],b[k],path+'.'+k,issues)
 elif isinstance(a,list) and isinstance(b,list):
  if len(a)!=len(b):issues.append({'path':path,'reason':'length'})
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,f'{path}[{i}]',issues)
 elif isinstance(a,(int,float)) and isinstance(b,(int,float)) and not isinstance(a,bool):
  if not math.isfinite(a) or not math.isfinite(b):issues.append({'path':path,'reason':'nonfinite'})
  elif a!=b:issues.append({'path':path,'a':a,'b':b,'abs':abs(a-b),'scaled':abs(a-b)/max(abs(a),abs(b),1e-300)})
 elif a!=b:issues.append({'path':path,'a':a,'b':b})
 return issues

def main():
 # Real original-binary outputs precede candidate build.
 for mode in ['fixed','birth','disabled']:
  if not (E/('baseline_'+mode)).exists():case('baseline_'+mode,BASE,mode,'radau',16)
 if not (E/'build_repair/outcome.json').exists():run('build_repair',[W/'rust_prefix/bin/cargo','build','--manifest-path',W/'baseline/adapter/Cargo.toml','--locked','--offline','--release','--jobs','2'],240)
 if not (E/'focused_repair/outcome.json').exists():run('focused_repair',[W/'rust_prefix/bin/cargo','test','--manifest-path',W/'baseline/adapter/Cargo.toml','--locked','--offline','--release','--lib','--test','focused','--','--test-threads=1','--nocapture'],120)
 settings=[(mode,method,n) for mode,methods in [('fixed',{'radau':[2,4,8,16],'ssprk':[8,16,32]}),('birth',{'radau':[4,8,16],'ssprk':[4,8,16]}),('disabled',{'radau':[4,8,16],'ssprk':[4,8,16]})] for method,levels in methods.items() for n in levels]
 old=Path(os.environ['LRS_REFERENCE_RECEIPTS']) if 'LRS_REFERENCE_RECEIPTS' in os.environ else Path('/workspace/scratch/6af5e9e6c737/resume_20261020/restored_c10/REI_LRS_V14_VIGILODE_C10_20261019T141050Z/repo_payload/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/receipts')
 checks=[];start=time.monotonic()
 for mode,method,n in settings:
  if time.monotonic()-start>120:raise RuntimeError('matrix total budget')
  got=case(f'matrix_{mode}_{method}_{n}',CAND,mode,method,n,'cell-cache')
  ref=old/f'matrix_{mode}_{method}_n{n}/raw.json'
  if mode in ['fixed','birth','disabled'] and method=='radau' and n==16:ref=E/f'baseline_{mode}/raw.json'
  if (mode,method,n)==('fixed','radau',4):ref=old/'final_source_n4/raw.json'
  issues=compare(json.loads(ref.read_text()),got)
  checks.append({'setting':[mode,method,n],'reference':str(ref),'issues':issues,'completed':got['completed']});(E/'matrix_comparison.json').write_text(json.dumps(checks,indent=2))
  if issues:raise RuntimeError('numerical mismatch '+str(issues[:3]))
 for variant in ['legacy','cell-cache']:case('profile_'+variant,CAND,'fixed','radau',16,variant,True)
 timings=[]
 for mode in ['fixed','birth','disabled']:
  reference=json.loads((E/f'baseline_{mode}/raw.json').read_text())
  for variant in ['legacy','cell-cache']:case(f'warm_{mode}_{variant}',CAND,mode,'radau',16,variant)
  for pair in range(5):
   row={'mode':mode,'pair':pair,'order':['legacy','cell-cache'] if pair%2==0 else ['cell-cache','legacy']}
   for variant in row['order']:
    name=f'bench_{mode}_{pair}_{variant}';raw=case(name,CAND,mode,'radau',16,variant)
    issues=compare(reference,raw)
    if issues:raise RuntimeError('bench mismatch '+str(issues[:3]))
    row[variant]={'native_wall_s':raw['wall_s'],'process_wall_s':json.loads((E/name/'outcome.json').read_text())['process_wall_s'],'work':raw['native_evaluation']['profile']}
   row['ratio_legacy_over_cache']=row['legacy']['native_wall_s']/row['cell-cache']['native_wall_s'];timings.append(row);(E/'paired_samples.json').write_text(json.dumps(timings,indent=2))
 summary={}
 for mode in ['fixed','birth','disabled']:
  rows=[r for r in timings if r['mode']==mode];summary[mode]={'paired_ratios':[r['ratio_legacy_over_cache'] for r in rows]}
  for variant in ['legacy','cell-cache']:
   xs=[r[variant]['native_wall_s'] for r in rows];q=statistics.quantiles(xs,n=4);summary[mode][variant]={'median_s':statistics.median(xs),'range_s':[min(xs),max(xs)],'iqr_s':[q[0],q[2]]}
 (E/'SUMMARY.json').write_text(json.dumps({'cpu':CPU,'candidate_sha256':sha(CAND),'baseline_sha256':sha(BASE),'settings':summary,'admission':'ROOT_PENDING'},indent=2));print('SERIAL COMPLETE',flush=True)
if __name__=='__main__':main()
