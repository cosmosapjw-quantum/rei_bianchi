"""Execute one frozen new R11 lane and preserve full OS process evidence."""
from pathlib import Path
import datetime,hashlib,json,os,platform,resource,subprocess,sys,time
L=Path(__file__).resolve().parents[1];ROOT=L.parents[1]
def main():
 lane=sys.argv[1]
 if lane not in ('primary','reference'):raise ValueError('Explicit primary/reference lane required')
 out=L/'raw';out.mkdir(exist_ok=True)
 attempt=out/(lane.upper()+'_ATTEMPT.json');process=out/(lane.upper()+'_PROCESS.json')
 if attempt.exists() or process.exists() or (out/(lane.upper()+'_RESULTS.json')).exists():raise ValueError('Existing actual attempt; never silently rerun')
 freeze=json.loads((out/'PREEXECUTION_FREEZE.json').read_text());assert freeze['status']=='PASS'
 for r in freeze['files']:
  b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],r['path']
 state_path=ROOT.parent/'r11_publication'/'STATE.json'
 if state_path.exists():
  state=json.loads(state_path.read_text());pub={'source_commit':state['commit'],'source_tree':state['tree']}
 elif (ROOT/'CHECKPOINT_MANIFEST.json').exists():pub=json.loads((ROOT/'CHECKPOINT_MANIFEST.json').read_text())
 else:pub={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();command=[sys.executable,str(L/'verification'/('run_'+lane+'.py'))]
 initial={'schema':'WU_R11_EXECUTION_ATTEMPT_V1','lane':lane,'source_commit':pub['source_commit'],'started_utc':start,'command':command,'CPU_limit_s':60,'wall_limit_s':90,'attempt':1}
 with attempt.open('x') as f:json.dump(initial,f,indent=2);f.write('\n')
 def limit():resource.setrlimit(resource.RLIMIT_CPU,(60,61))
 before=resource.getrusage(resource.RUSAGE_CHILDREN);wall=time.monotonic()
 try:
  cp=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=90,preexec_fn=limit);code=cp.returncode;stdout=cp.stdout;stderr=cp.stderr;timeout=False
 except subprocess.TimeoutExpired as e:code=124;stdout=e.stdout or b'';stderr=e.stderr or b'';timeout=True
 after=resource.getrusage(resource.RUSAGE_CHILDREN)
 rec={**initial,'schema':'WU_R11_ACTUAL_PROCESS_V1','finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':code,'timeout':timeout,'OS_user_CPU_s':after.ru_utime-before.ru_utime,'OS_system_CPU_s':after.ru_stime-before.ru_stime,'OS_CPU_s':after.ru_utime-before.ru_utime+after.ru_stime-before.ru_stime,'wall_s':time.monotonic()-wall,'includes_imports_and_serialization':True,'python':sys.version,'platform':platform.platform(),'old_science_replay':0,'new_ODE_runs':0}
 (out/(lane.upper()+'_STDOUT.txt')).write_bytes(stdout);(out/(lane.upper()+'_STDERR.txt')).write_bytes(stderr)
 with process.open('x') as f:json.dump(rec,f,indent=2);f.write('\n')
 ledger=L/'EXECUTION_LEDGER.json';v=json.loads(ledger.read_text());v[lane].update(consumed=1,remaining=0,status='COMPLETED' if code==0 else 'FAILED',process=rec)
 if code!=0:v['failures'].append({'class':'implementation_or_numerical_pending_diagnosis','lane':lane,'returncode':code,'first_output':'raw/'+lane.upper()+'_RESULTS.json','next_action':'Inspect exact first failure; preserve original run and fix only diagnosed cause'})
 ledger.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(rec));print(stdout.decode(errors='replace'))
 if stderr:print(stderr.decode(errors='replace'),file=sys.stderr)
 return code
if __name__=='__main__':raise SystemExit(main())
