import json,time,pathlib,subprocess,sys
import numpy as np
private=pathlib.Path(sys.argv[1]); allocation=json.loads((private/'ALLOCATION.json').read_text())
old=pathlib.Path('/home/cosmosapjw/REI_PRIVATE_SOURCE012_INPUTS_20261016/resume_20261018/source_age_ready_execution_proposal_001/collected/stage')
raw=old/'outputs/age64'; configs=['server','0','64','8','8','16']
servers=[];count=0;records=[];start=time.monotonic()
try:
 for name,binary in [('original',old/'inputs/positive_native'),('compact',private/'positive_compact')]:
  proc=subprocess.Popen([str(binary),*configs],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(private/(name+'.stderr')).open('w'),text=True,bufsize=1)
  servers.append(proc); setup_line=proc.stdout.readline();(private/(name+'_setup.json')).write_text(setup_line)
  setup=json.loads(setup_line)
  if name=='original': reference_setup=setup
  else: assert setup==reference_setup,'setup differs'
 cells=setup['cells'];size=4+2*len(setup['births'])*cells+setup['extra']
 cases=[('accepted',0),('accepted',4),('accepted',16),('accepted',34),('rejected',4),('rejected',35)]
 def request(proc,mode,active,x,values):
  global count
  assert count<12 and time.time()<allocation['deadline_epoch']
  count+=1; begin=time.perf_counter()
  line=f'{mode} {active} {x:.17e} '+' '.join(format(v,'.17e') for v in values)+'\n'
  # Keep actual newline protocol, rather than a literal backslash sequence.
  line=line[:-2]+'\n' if line.endswith('\\n') else line
  proc.stdin.write(line);proc.stdin.flush();answer=proc.stdout.readline()
  assert answer,'server returned EOF'
  return answer.strip(),time.perf_counter()-begin,len(line.encode()),len(answer.encode())
 for kind,event in cases:
  path=raw/(f'accepted_coordinates_event{event}.npy' if kind=='accepted' else f'first_failed_state_event{event}_retry0.npy')
  saved=np.load(path,allow_pickle=False)
  x=setup['births'][event] if kind=='accepted' else float(saved[0]);whole=saved if kind=='accepted' else saved[1:];active=event
  indices=np.array([*range(4),*[k for group in setup['active_indices'][:active] for k in group],*range(size-setup['extra'],size)],dtype=int)
  reconstructed=np.zeros(size)
  for i in range(active):reconstructed[4+2*cells*i:4+2*cells*(i+1)]=setup['encoded_births'][i]
  reconstructed[indices]=whole[indices]
  assert np.array_equal(reconstructed.view(np.uint64),whole.view(np.uint64)),f'input expansion mismatch {kind}{event}'
  before,t0,n0,m0=request(servers[0],'R',active,x,whole)
  after,t1,n1,m1=request(servers[1],'RC',active,x,whole[indices])
  (private/f'{kind}{event}_original.txt').write_text(before+'\n');(private/f'{kind}{event}_compact.txt').write_text(after+'\n')
  if before.startswith('ERR'):assert before==after,(kind,event,before,after)
  else:
   tokens=before.split();assert len(tokens)==size
   assert [tokens[i] for i in indices]==after.split(),f'selected derivative mismatch {kind}{event}'
  records.append(dict(kind=kind,event=event,active=active,full_scalars=size,compact_scalars=len(indices),bitwise_input_reconstruction=True,formatted_derivative_or_error_parity=True,reply_kind='ERR' if before.startswith('ERR') else 'RHS',original_roundtrip_s=t0,compact_roundtrip_s=t1,original_request_bytes=n0,compact_request_bytes=n1,original_reply_bytes=m0,compact_reply_bytes=m1))
 result=dict(state='PASS_SIX_SAVED_STATE_PROTOCOL_PAIRS',pairs=len(records),RHS_helper_calls=count,wall_s=time.monotonic()-start,records=records,scientific_admission='NOT_ISSUED',full_solver_runs=0,runtime_speedup_scope='Six saved-state request round trips only; no full-solver ETA claim')
 (private/'PARITY_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
finally:
 for proc in servers:
  proc.stdin.close()
  try:proc.wait(timeout=1)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
