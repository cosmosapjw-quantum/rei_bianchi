from pathlib import Path
import concurrent.futures,subprocess,json,time,os,hashlib,threading
R=Path.cwd();P=R/'.cuh/fastest-track/REI-F08-PAIRED';C=P/'conservative-candidate';lock=threading.Lock();states={};env={**os.environ,'CUHG_EXECUTION_MODE':'CODEX_ONLY'}
for rel,sha in json.loads((P/'matched-source-input-manifest.json').read_text())['files'].items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==sha,rel
for rel,sha in json.loads((C/'candidate-manifest.json').read_text())['source_files'].items():assert hashlib.sha256((C/rel).read_bytes()).hexdigest()==sha,rel
labels=['S2_FLRW','S2_BI','A0_BI','A2_FLRW','A2_BI','T2_FLRW','T2_BI']
initial={}
for l in labels:
 b=(C/('whole-'+l) if l.startswith('T2') else P/'whole-matched'/l);d=b/l
 initial[l]={'directory':str(d),'checkpoint_header':(d/'checkpoint.dat').read_text().splitlines()[0] if (d/'checkpoint.dat').exists() else None,'pending_transaction':(d/'pending.transaction').exists(),'summary_exists':(d/'summary.json').exists(),'prior_process_exit':'UNKNOWN_AFTER_INTERRUPTION','prior_prefix_preserved':(d/'independent_prefix.pkl').exists()}
(P/'interruption-reconciliation.json').write_text(json.dumps({'task':'REI-F08','observed_live_original_processes':0,'axes':initial,'successful_axes_replayed':False,'known_native_tokens':10419630,'native_dispatches':4},indent=2)+'\n')
def save():
 with lock:(P/'resume-live.json').write_text(json.dumps(states,indent=2)+'\n')
def run(kind,l):
 repair=l.startswith('T2');b=C/('whole-'+l) if repair else P/'whole-matched'/l;d=b/l;start=time.monotonic()
 if kind=='producer' and (d/'summary.json').exists():return
 if kind=='independent' and (d/'independent_history_receipt.json').exists():return
 base=['cuhg-telemetry','run','--project',str(R),'--task','REI-F08','--']
 if kind=='producer':
  cmd=base+[str(C/'paired_history' if repair else P/'matched-producer.binary'),'--scenario',str(R/'configs/rei_fastest_v1/science_scenario_v1.json'),'--output',str(b),'--full','--only',l]
  if b.exists():cmd+=['--resume']
 else:
  while not (d/'header.jsonl').exists():time.sleep(.5)
  cmd=base+['sage','-python',str(P/'checker_v5/check_history.py'),str(d),'--stream']
 name=l+'-'+kind;log=P/(name+'-resume.log')
 with log.open('wb') as f:
  proc=subprocess.Popen(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT);states[name]={'pid':proc.pid,'argv':cmd,'status':'ACTUALLY_RUNNING'};save();code=proc.wait()
 result={'task':'REI-F08','run':l,'kind':kind,'argv':cmd,'exit_code':code,'wall_s':time.monotonic()-start,'status':'ACTUAL_EXIT0' if code==0 else 'ACTUAL_FAILURE','prior_exit':'UNKNOWN_AFTER_INTERRUPTION','durable_resume':True};states[name]=result;save();(P/(name+'-resume-execution.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as prod,concurrent.futures.ThreadPoolExecutor(max_workers=6) as proof:
 fs=[prod.submit(run,'producer',l) for l in labels if not l.startswith('T2')]+[prod.submit(run,'producer',l) for l in labels if l.startswith('T2')]
 fs += [proof.submit(run,'independent',l) for l in labels]
 for f in concurrent.futures.as_completed(fs):f.result()
for l in ['T2_FLRW','T2_BI']:
 a=states[l+'-producer'];v=states[l+'-independent'];(C/(l+'-repair-execution.json')).write_text(json.dumps({'task':'REI-F08','run':l,'producer_exit_code':a['exit_code'],'independent_exit_code':v['exit_code'],'producer_argv':a['argv'],'validator_argv':v['argv'],'execution_interrupted_and_durably_resumed':True,'original_production_failure_exit':2,'scientific_gate':1e-12,'successful_axes_replayed':False,'scientific_admission':'HOLD'},indent=2)+'\n')
print('RESUMED_EXECUTIONS_FINISHED',flush=True)
