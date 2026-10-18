import csv,hashlib,json,math,os,resource,signal,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parent.parent;repo=root.parent.parent.parent;c=json.loads((root/'CONTRACT.json').read_text());ledger=root/'raw/EXECUTIONS.json';assert not ledger.exists();calls=[];checks={}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def require(ok,msg):
 if not ok:raise ValueError(msg)
def all_finite(x):
 if isinstance(x,dict):return all(all_finite(v) for v in x.values())
 if isinstance(x,list):return all(all_finite(v) for v in x)
 return not isinstance(x,float) or math.isfinite(x)
def inspect(case,out):
 r=json.loads((out/'result.json').read_text());owner=json.loads((out/'owner_rates.json').read_text());rate=dict(x.split('=',1) for x in (out/'source_time_check.txt').read_text().splitlines());trace=list(csv.DictReader((out/'step_trace.csv').open()))
 checkpoint=(out/'checkpoint.bass-v1').read_text();head,body=checkpoint.split('\nAXBI_CHECKPOINT_V4\n',1);h=head.splitlines();body='AXBI_CHECKPOINT_V4\n'+body;bl=body.splitlines();counts=list(map(int,bl[2].split()));state=list(map(float,bl[1].split()))
 a={'expected_case_grid_steps_workers':r['case']==case and r['grid_points']==121 and r['steps']==4 and r['workers']==1 and r['dln_a']==.0001,'finite_result_and_owner':all_finite(r) and all_finite(owner),'photon_normalized':abs(r['photon_normalized'])<=1e-8,'energy_normalized':abs(r['energy_normalized'])<=1e-8,'Hamiltonian':r['max_hamiltonian_normalized']<=3e-12,'Raychaudhuri_native_constructor':'native exact absolute+relative row validator completed before run','Newton':r['newton_residual']<=1e-11,'source_increment':abs(float(rate['max_source_residual_per_h']))<=1e-10,'point_energy_owner':abs(owner['owner_normalized'])<=1e-12,'restart_exact_state_native_and_abs':r['restart_max_abs']==0.0 and r['restart_max_abs']<=1e-14,'native_compiled_identity':h[4]==c['frozen_compiled_source_sha256'],'checkpoint_passive_mode':('|inactive_hi_split=true' in h[2] and 'CURRENT_PROVIDER=SOURCE008' in h[3]),'mode_metadata':('inactive_hi_split=true' in (out/'transport_variant.txt').read_text() and 'selected_BASS_certified_forward_ray_monotone_only' in (out/'transport_variant.txt').read_text() and 'q0_forward_monotonic_only' not in (out/'transport_variant.txt').read_text()),'checkpoint_body_binding':h[9]==hashlib.sha256(body.encode()).hexdigest() and int(h[10])==len(body.encode()),'checkpoint_state_and_counters':len(bl)==11 and len(state)==11 and counts[0]==2 and counts[1]==2 and len(counts)==6,'finite_nonnegative_arrays':all(math.isfinite(v) and v>=0 for line in bl[4:10] for v in map(float,line.split())),'point_domain':1/21<=r['a']<=.2 and r['temperature_k']>0 and r['time_s']>0 and r['h_per_s']>0,'fractions_nonnegative':0<=r['x_hii']<=1 and 0<=r['x_heii']<=1 and 0<=r['x_heiii']<=1 and r['x_heii']+r['x_heiii']<=1,'no_adaptive_probe_or_fabricated_metrics':r['adaptive_status']=='NOT_RUN_FIXED_STEP_COMPONENT_ONLY' and not any(k in r for k in ['adaptive_error','adaptive_accepted','adaptive_rejects']),'four_trace_steps':len(trace)==4 and [int(x['step']) for x in trace]==[1,2,3,4],'finite_forward_trace':all(all(math.isfinite(float(v)) for v in row.values()) and float(row['dt_s'])>0 and abs(float(row['source_residual_per_h']))<=1e-10 for row in trace)}
 a['signed_geometry']=r['signed_s_over_h']<0 and r['b']<0 if case=='SIGNED_MINUS' else r['signed_s_over_h']==0 and r['b']==0
 require(all(v is not False for v in a.values()),'ACCEPTANCE_FAILURE '+json.dumps(a))
 return {'acceptance_observed':a,'result':r,'owner_rates':owner,'source_time_check':{k:float(v) for k,v in rate.items()},'main_branch':{'fixed_steps':4,'rhs_evaluations':r['rhs_evaluations']},'restarted_branch':{'extra_fixed_steps_after_checkpoint':2,'checkpoint_initial_rhs_evaluations':counts[4],'final_rhs_counter':r['rhs_evaluations'],'extra_rhs_calls_derived_from_exact_native_restart_parity':r['rhs_evaluations']-counts[4],'derivation':'native exact final-state parity includes RHS counter; extra calls = final main RHS - saved midpoint RHS'},'aggregate_executed_rhs_calls_derived':2*r['rhs_evaluations']-counts[4],'clock':{'native_point_minus_interval_residual_s':r['clock_residual_s'],'GL4_GL8_difference':None,'GL4_GL8_status':'NOT_EMITTED_BY_THIS_EXAMPLE; no inferred error bound'},'native_checkpoint_identity':h[4],'checkpoint_config_sha256':h[5],'trace_steps':len(trace),'output_files':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()]}
for case in c['case_order']:
 try:
  for path,expected in [(c['binary_path'],c['binary_sha256']),(c['csv_path'],c['csv_sha256']),(c['manifest_path'],c['manifest_sha256'])]:require(sha(path)==expected,'IMMUTABLE_LAUNCH_IDENTITY_MISMATCH '+path)
  require(all(sha(x['path'])==x['sha256'] for x in c['bound_compiled_files']),'BOUND_COMPILED_SOURCE_CHANGED')
  require(all(sha(x['path'])==x['sha256'] for x in c['coarse_source007_reused_files']),'REUSED_SOURCE007_OUTPUT_CHANGED')
  out=root/'results'/case;require(not out.exists(),'FRESH_OUTPUT_REQUIRED');argv=[c['binary_path'],c['csv_path'],c['manifest_path'],c['csv_sha256'],c['manifest_sha256'],case,'121','0.0001','4','1',str(out),'--inactive-hi-split'];env=os.environ.copy();env.update({x:'1' for x in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']});prior=sum(x['wall_seconds'] for x in calls);cap=min(60,120-prior);require(cap>3,'COMPONENT_WALL_ALLOWANCE_EXHAUSTED');start=time.monotonic();epoch=time.time();pid=os.fork()
  if pid==0:
   os.setsid();os.chdir(repo);resource.setrlimit(resource.RLIMIT_AS,(2147483648,2147483648))
   for fd,suffix in [(1,'stdout'),(2,'stderr')]:f=os.open(str(root/'raw'/(case+'.'+suffix)),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644);os.dup2(f,fd)
   os.execve(argv[0],argv,env)
  rec={'case':case,'pid':pid,'argv':argv,'cwd':str(repo),'start_epoch':epoch,'wall_cap_seconds':cap,'AS_bytes':2147483648,'output_cap_bytes':134217728,'env_overrides':{x:'1' for x in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']},'HEAD_at_launch':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()};write(root/'raw'/(case+'.STARTED.json'),rec);print(json.dumps(rec),flush=True)
  reason=None;term=None;peak=0
  while True:
   got,status,usage=os.wait4(pid,os.WNOHANG)
   if got:break
   elapsed=time.monotonic()-start;total=sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) if out.exists() else 0;total+=sum(p.stat().st_size for p in (root/'raw').glob(case+'.*') if p.is_file());peak=max(peak,total)
   if term is None and (elapsed>=cap-3 or total>=134217728):reason='WALL_LIMIT' if elapsed>=cap-3 else 'OUTPUT_LIMIT';term=time.monotonic();os.killpg(pid,signal.SIGTERM)
   if term is not None and (time.monotonic()-term>=2 or elapsed>=cap-.3):
    try:os.killpg(pid,signal.SIGKILL)
    except ProcessLookupError:pass
   time.sleep(.015)
  rec.update(exit_code=os.waitstatus_to_exitcode(status),wait_status=status,wall_seconds=time.monotonic()-start,cpu_user_seconds=usage.ru_utime,cpu_system_seconds=usage.ru_stime,cpu_seconds=usage.ru_utime+usage.ru_stime,peak_rss_bytes=usage.ru_maxrss*1024,child_reaped=True,termination_reason=reason,peak_observed_output_bytes=peak,end_epoch=time.time(),stdout_path=str(root/'raw'/(case+'.stdout')),stderr_path=str(root/'raw'/(case+'.stderr')));calls.append(rec);write(root/'raw'/(case+'.execution.json'),rec);write(ledger,calls);require(rec['exit_code']==0 and reason is None,'FIRST_COMPONENT_COMMAND_FAILURE');require(rec['wall_seconds']<=60 and sum(x['wall_seconds'] for x in calls)<=120,'COMPONENT_WALL_LIMIT');require(sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<134217728,'COMPONENT_OUTPUT_LIMIT');checks[case]=inspect(case,out);write(root/'raw'/(case+'.INSPECTION.json'),checks[case]);print(json.dumps({'case':case,'exit_code':rec['exit_code'],'wall_seconds':rec['wall_seconds'],'native_source':checks[case]['native_checkpoint_identity'],'main_rhs':checks[case]['main_branch']['rhs_evaluations'],'restart_extra_rhs':checks[case]['restarted_branch']['extra_rhs_calls_derived_from_exact_native_restart_parity'],'acceptance':'OBSERVED_COMPONENT_ONLY'}),flush=True)
 except Exception as exc:
  write(root/'raw/STOP.json',{'case':case,'reason':str(exc),'completed_cases':list(checks),'next_case_started':False,'no_retry':True});print(json.dumps({'STOP':str(exc),'case':case}),flush=True);raise
write(root/'raw/COMPONENT_INSPECTIONS.json',checks)
