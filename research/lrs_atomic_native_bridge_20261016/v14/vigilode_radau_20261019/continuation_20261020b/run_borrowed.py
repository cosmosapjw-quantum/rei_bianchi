"""Frozen finite borrowed-cell implementation evidence; no publication/admission."""
from pathlib import Path
import os,subprocess,time,json,hashlib,sys,statistics,math
T=Path(__file__).resolve().parent;O=Path('/workspace/scratch/6af5e9e6c737/optimization_20261020/coder');W=O/'baseline';E=T/'evidence';E.mkdir(exist_ok=True);BIN=O/'target_baseline/release/rei-vigilode-radau-research';CPU=0
ENV=os.environ.copy();ENV.update(PATH=str(O/'rust_prefix/bin')+':'+ENV['PATH'],RUSTC=str(O/'rust_prefix/bin/rustc'),CARGO_HOME=str(O/'cargo_home'),CARGO_TARGET_DIR=str(O/'target_baseline'),CARGO_BUILD_JOBS='1',LD_LIBRARY_PATH=str(O/'rust_prefix/lib'))
sys.path.insert(0,str(O));from experiment import compare
native_total=0.
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,argv,timeout):
 d=E/name;d.mkdir();sourcefiles=[W/'adapter/src/lib.rs',W/'adapter/src/main.rs',W/'native_owner/rust/rei_microphysics/src/axbi_native_rhs.rs'];meta={'argv':list(map(str,argv)),'timeout_s':timeout,'environment':{k:ENV[k] for k in ['RUSTC','CARGO_HOME','CARGO_TARGET_DIR','CARGO_BUILD_JOBS']},'source_sha256':{str(p):sha(p) for p in sourcefiles}}
 if argv[0]=='taskset':meta.update(binary_sha256=sha(argv[3]),cpu=CPU)
 (d/'inputs.json').write_text(json.dumps(meta,indent=2));start=time.monotonic()
 with (d/'stdout.txt').open('wb') as so,(d/'stderr.txt').open('wb') as se:
  try:code=subprocess.run(list(map(str,argv)),env=ENV,stdout=so,stderr=se,timeout=timeout).returncode
  except subprocess.TimeoutExpired:code=None
 outcome={'exit_code':code,'process_wall_s':time.monotonic()-start};(d/'outcome.json').write_text(json.dumps(outcome,indent=2));print(name,outcome,flush=True)
 if code!=0:raise RuntimeError('STOP_FOR_ASTRA: '+name)
 return d

def case(name,mode,method,n,variant,profile=False):
 global native_total
 if native_total>=180:raise RuntimeError('native total cap')
 d=E/name;argv=['taskset','-c',str(CPU),BIN,d/'raw.json',mode,method,str(n),'--native-eval',variant]
 if profile:argv+=['--profile']
 run(name,argv,min(40,180-native_total));outcome=json.loads((d/'outcome.json').read_text());native_total+=outcome['process_wall_s'];raw=json.loads((d/'raw.json').read_text());assert raw['completed'];return raw

def check(ref,raw,name):
 issues=compare(ref,raw)
 # New clone counters must not replace unchanged work/call/preparation/node evidence.
 workkeys=['charged_rhs_attempts','occupied_cell_preparations','node_visits']
 counterissues=[]
 if 'native_evaluation' in ref:
  a=ref['native_evaluation']['profile'];b=raw['native_evaluation']['profile']
  counterissues=[{'key':k,'a':a[k],'b':b[k]} for k in workkeys if a[k]!=b[k]]
 record={'scientific_mismatches':issues,'unchanged_work_mismatches':counterissues};(E/(name+'_comparison.json')).write_text(json.dumps(record,indent=2))
 if issues or counterissues:raise RuntimeError('STOP_FOR_ASTRA comparison '+name+' '+str((issues+counterissues)[:3]))

def main():
 run('release_build',[O/'rust_prefix/bin/cargo','build','--offline','--locked','--release','--jobs','1','--manifest-path',W/'adapter/Cargo.toml','--bin','rei-vigilode-radau-research'],1200)
 run('focused_tests',[O/'rust_prefix/bin/cargo','test','--offline','--locked','--release','--jobs','1','--manifest-path',W/'adapter/Cargo.toml','--lib','--test','focused','--','--test-threads=1','--nocapture'],600)
 # Limited shared-kernel continuity controls against the admitted previous cache binary/raw.
 refs={m:json.loads((O/f'experiments/matrix_{m}_radau_16/raw.json').read_text()) for m in ['fixed','birth','disabled']}
 for variant in ['legacy','cell-cache']:
  got=case('control_'+variant,'fixed','radau',16,variant)
  reference=refs['fixed']
  if variant=='legacy':reference=json.loads((O/'experiments/profile_legacy/raw.json').read_text())
  check(reference,got,'control_'+variant)
 settings=[(mode,method,n) for mode,methods in [('fixed',{'radau':[2,4,8,16],'ssprk':[8,16,32]}),('birth',{'radau':[4,8,16],'ssprk':[4,8,16]}),('disabled',{'radau':[4,8,16],'ssprk':[4,8,16]})] for method,levels in methods.items() for n in levels]
 replay=[]
 for mode,method,n in settings:
  name=f'replay_{mode}_{method}_n{n}';got=case(name,mode,method,n,'cell-borrowed');ref=json.loads((O/f'experiments/matrix_{mode}_{method}_{n}/raw.json').read_text());check(ref,got,name);replay.append({'mode':mode,'method':method,'N':n,'completed':True,'comparison':'EXACT_FINITE_EQUAL','work':got['native_evaluation']['profile']});(E/'REPLAY_SUMMARY.json').write_text(json.dumps(replay,indent=2))
 timings=[]
 for mode in ['fixed','birth','disabled']:
  for variant in ['cell-cache','cell-borrowed']:
   got=case(f'warm_{mode}_{variant}',mode,'radau',16,variant);check(refs[mode],got,f'warm_{mode}_{variant}')
  for pair in range(5):
   order=['cell-cache','cell-borrowed'] if pair%2==0 else ['cell-borrowed','cell-cache'];row={'mode':mode,'pair':pair,'order':order}
   for variant in order:
    name=f'paired_{mode}_{pair}_{variant}';got=case(name,mode,'radau',16,variant);check(refs[mode],got,name);row[variant]={'native_wall_s':got['wall_s'],'process_wall_s':json.loads((E/name/'outcome.json').read_text())['process_wall_s'],'work':got['native_evaluation']['profile']}
   row['paired_native_ratio_cache_over_borrowed']=row['cell-cache']['native_wall_s']/row['cell-borrowed']['native_wall_s'];row['paired_process_ratio_cache_over_borrowed']=row['cell-cache']['process_wall_s']/row['cell-borrowed']['process_wall_s'];timings.append(row);(E/'PAIRED_SAMPLES.json').write_text(json.dumps(timings,indent=2))
 summary={}
 for mode in ['fixed','birth','disabled']:
  rows=[r for r in timings if r['mode']==mode];summary[mode]={'all_native_paired_ratios':[r['paired_native_ratio_cache_over_borrowed'] for r in rows],'median_native_paired_ratio':statistics.median(r['paired_native_ratio_cache_over_borrowed'] for r in rows),'all_process_paired_ratios':[r['paired_process_ratio_cache_over_borrowed'] for r in rows],'median_process_paired_ratio':statistics.median(r['paired_process_ratio_cache_over_borrowed'] for r in rows)}
  for v in ['cell-cache','cell-borrowed']:
   summary[mode][v]={}
   for clock in ['native_wall_s','process_wall_s']:
    xs=[r[v][clock] for r in rows];q=statistics.quantiles(xs,n=4);summary[mode][v][clock]={'median':statistics.median(xs),'range':[min(xs),max(xs)],'iqr':[q[0],q[2]]}
 (E/'C8_SUMMARY.json').write_text(json.dumps({'candidate_binary_sha256':sha(BIN),'native_cumulative_process_wall_s':native_total,'cpu':CPU,'settings':summary,'admission':'ASTRA_PENDING','new_NCP':'NOT_RUN'},indent=2));print('FINITE EVIDENCE COMPLETE',native_total,flush=True)
if __name__=='__main__':main()
