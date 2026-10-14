import importlib.util,json,pathlib,shutil,tempfile,subprocess,time,hashlib
P=pathlib.Path('.cuh/fastest-track/REI-F05')
s=importlib.util.spec_from_file_location('v2',P/'verify_candidate_v2.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
s=importlib.util.spec_from_file_location('fast',P/'verify_whole_fast.py');fast=importlib.util.module_from_spec(s);s.loader.exec_module(fast)
fast.install_cache(v)
d=max((P/'pilot').iterdir(),key=lambda x:x.stat().st_mtime);tmp=pathlib.Path(tempfile.mkdtemp(prefix='rei-f05-repair-'));results={}
for name in ['row_ledger','summary_ledger','time_schedule','initial_state']:
 t=tmp/name;shutil.copytree(d,t)
 if name=='summary_ledger':
  f=t/'level_0_summary.json';x=json.loads(f.read_text());x['all_seven_ledgers'][v.lock['all_seven_ledgers'][3]]=1e-13;f.write_text(json.dumps(x))
 elif name=='initial_state':
  f=t/'level_0_summary.json';x=json.loads(f.read_text());x['initial_state'][0]+=1e-9;f.write_text(json.dumps(x))
 else:
  f=t/'level_0_transactions.jsonl';rows=[json.loads(l) for l in f.read_text().splitlines()]
  if name=='row_ledger':rows[0]['ledgers']={k:42 for k in rows[0]['ledgers']}
  else:rows[0]['dt_s']/=2
  f.write_text(''.join(json.dumps(x)+'\n' for x in rows))
 try:v.validate_run(t,True);raise RuntimeError(name+' false PASS')
 except AssertionError as e:results[name]={'rejected':True,'reason':str(e)}
exe=pathlib.Path('rust/rei_microphysics/target/release/examples/first_interval').resolve();base=[str(exe),'--input','docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json','--pilot']
t=tmp/'source';shutil.copytree(d,t);f=t/'source_identity.dat';f.write_text(f.read_text()+'changed source\n');r=subprocess.run(base+['--output',str(t)],capture_output=True,text=True);assert r.returncode and 'compiled source identity mismatch' in r.stderr;results['source_mismatch']={'exit':r.returncode,'stderr':r.stderr}
t=tmp/'resume';shutil.copytree(d,t);before={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in t.glob('*transactions.jsonl')};r=subprocess.run(base+['--output',str(t)],capture_output=True,text=True);assert r.returncode==0;assert before=={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in t.glob('*transactions.jsonl')};results['completed_resume']={'transaction_bytes_unchanged':True}
t=tmp/'first_crash';proc=subprocess.Popen(base+['--output',str(t)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
start=time.monotonic();log=t/'level_0_transactions.jsonl';cp=t/'level_0_checkpoint.dat'
while not log.exists() and proc.poll() is None and time.monotonic()-start<10:time.sleep(.001)
assert log.exists() and cp.exists();proc.terminate();stdout,stderr=proc.communicate();offset=int(cp.read_text().splitlines()[8]);assert offset==0,'fault window missed'
r=subprocess.run(base+['--output',str(t)],capture_output=True,text=True);assert r.returncode==0,r.stderr;verified=v.validate_run(t,True);results['first_transaction_crash']={'durable_checkpoint_offset_at_interrupt':offset,'resume_verified_trials':verified['uniformly_certified_trials']}
(P/'repair-regression.json').write_text(json.dumps({'status':'PASS','evidence_dir':str(tmp),'checks':results},indent=2)+'\n');print(json.dumps(results))
