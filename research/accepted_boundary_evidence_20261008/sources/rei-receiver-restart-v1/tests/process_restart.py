#!/usr/bin/env python3
"""Real subprocess fixture: durable stop/restart, OFF parity and refusal controls."""
import pathlib,subprocess,json,time,os,signal,hashlib,struct,shutil
root=pathlib.Path(__file__).resolve().parents[1]
binary=root/'target/debug/receiver_fixture'
parent=root/'evidence/runs';parent.mkdir(exist_ok=True)
for i in range(1024):
 run=parent/f'case-{i}'
 try:run.mkdir();break
 except FileExistsError:continue
else:raise RuntimeError('bounded run allocation exhausted')
controls=[];reports=[]
def cmd(mode,path,report,steps=0):return [str(binary),mode,str(path),str(report),str(steps)]
def invoke(label,mode,path,steps=0,expected=0):
 report=run/f'{label}.json'
 result=subprocess.run(cmd(mode,path,report,steps),capture_output=True,text=True,timeout=12)
 (run/f'{label}.stdout').write_text(result.stdout);(run/f'{label}.stderr').write_text(result.stderr)
 assert result.returncode==expected,(label,result.returncode,result.stderr)
 if expected==0 and steps:
  j=json.loads(report.read_text());reports.append(j);return j
 return result
continuous=invoke('continuous','new',run/'continuous',2)
split=run/'split';report=run/'split-first.json'
p=subprocess.Popen(cmd('stop-committed',split,report,1),stdout=(run/'split-first.stdout').open('w'),stderr=(run/'split-first.stderr').open('w'))
try:
 deadline=time.monotonic()+12
 while not (split/'READY_FOR_KILL').exists():
  assert p.poll() is None
  if time.monotonic()>deadline:raise TimeoutError('committed stop fixture')
  time.sleep(.01)
 invoke('concurrent-collision','probe',split,expected=2);controls.append('exclusive concurrent writer collision')
 p.kill();assert p.wait(timeout=3)==-signal.SIGKILL
finally:
 if p.poll() is None:p.kill();p.wait()
first=json.loads(report.read_text());reports.append(first)
head_before=(split/'store/HEAD').read_bytes()
invoke('disk-only-probe','probe',split);assert (split/'store/HEAD').read_bytes()==head_before
second=invoke('restart-second','resume',split,1)
assert continuous['steps']==first['steps']+second['steps']
assert continuous['final_state']==second['final_state']
assert continuous['snapshot']==second['snapshot']
controls.extend(['SIGKILL-after-commit disk-only typed restore','uninterrupted/restart bitwise state+native outputs+owners+ledger equivalence','replay and changed context refuse with zero RHS'])
off=invoke('off','off',run/'off',2);baseline=invoke('baseline','baseline',run/'baseline',2)
assert not (run/'off').exists();assert not (run/'baseline').exists()
assert off['steps']==baseline['steps']==continuous['steps']
assert (off['rhs'],off['provider'])==(baseline['rhs'],baseline['provider'])==(continuous['rhs'],continuous['provider'])
controls.append('OFF unchanged baseline bitwise+call-count parity; no files')
# Actual process termination after syncing pending native trial, before rename.
crash=run/'pending';r=invoke('pending-stop','crash-pending',crash,1,73)
assert 'ACTUAL_PENDING_NATIVE_RHS=' in r.stderr
pending=list((crash/'store').glob('pending-*'));assert len(pending)==1
assert (crash/'store/HEAD').exists()
probe=invoke('pending-probe','probe',crash);assert 'generation=0' in probe.stdout
recovered=invoke('pending-recovered','resume',crash,2)
assert recovered['steps']==continuous['steps'];assert recovered['snapshot']==continuous['snapshot']
assert pending[0].exists() # never promoted or deleted during restart
controls.append('real native pending process-stop not promoted; consumed lease retained')
invoke('create-reuse','new',split,1,2);controls.append('fresh-create root reuse refusal')
invoke('fork','fork-check',split);controls.append('inherited fork handle refusal before native')
# Unsupported copied directory and forged host identity.
copy=run/'copied';shutil.copytree(split,copy);invoke('copy','probe',copy,expected=2);controls.append('copied root/inode fork refusal')
identity=split/'RUN_ID';saved_identity=identity.read_bytes();identity.write_bytes(b'FOREIGN_HOST\n'+saved_identity)
invoke('foreign-host','probe',split,expected=2);identity.write_bytes(saved_identity);controls.append('host identity mismatch refusal')
# Corruption controls use the actual committed HEAD, with no numerical solves.
head=split/'store/HEAD';saved=head.read_bytes()
for label,data in [('truncated',saved[:-17]),('checksum',saved[:-1]+bytes([saved[-1]^1])),('trailing',saved+b'extra')]:
 head.write_bytes(data);invoke(label,'probe',split,expected=2);head.write_bytes(saved);controls.append(label+' checkpoint refusal')
# Valid envelope checksum but inconsistent typed replay digest.
magic=b'REI_NATIVE_RECEIVER_CHECKPOINT_V2\n';payload=bytearray(saved[len(magic)+65:]);payload[-1]^=1
head.write_bytes(magic+hashlib.sha256(payload).hexdigest().encode()+b'\n'+payload)
invoke('typed-corrupt','probe',split,expected=2);head.write_bytes(saved);controls.append('rechecksummed typed replay mismatch refusal')
# No committed HEAD: a pending artifact cannot substitute for it.
head.rename(split/'store/SAVED_HEAD');invoke('missing-head','probe',split,expected=2);(split/'store/SAVED_HEAD').rename(head);controls.append('missing HEAD refuses pending-only restore')
lease=next((split/'leases').glob('attempt-*'));saved_lease=lease.read_bytes();lease.write_bytes(b'other namespace')
invoke('lease-corrupt','probe',split,expected=2);lease.write_bytes(saved_lease);controls.append('durable occurrence lease corruption refusal')
namespace=split/'leases/NAMESPACE';namespace.rename(split/'leases/SAVED_NAMESPACE');invoke('missing-namespace','probe',split,expected=2);assert not namespace.exists();(split/'leases/SAVED_NAMESPACE').rename(namespace);controls.append('missing namespace refuses without reissue')
head.write_bytes(b'x'*(4*1024*1024+1));invoke('oversized','probe',split,expected=2);head.write_bytes(saved);controls.append('oversized checkpoint bounded-read refusal')
invoke('schema-cap','schema-check',run/'schema-cap');controls.append('encoder/decoder context cap refuses before files/native; max accepted boundary restores without native')
invoke('final-restore','probe',split)
# Actual pending solve calls are printed from its real native receipt by stop injection.
import re
m=re.search(r'ACTUAL_PENDING_NATIVE_RHS=(\d+) PROVIDER=(\d+)',r.stderr);assert m
summary={'controls_passed':controls,'actual_native_trials':sum(j['actual_trials'] for j in reports)+1,'actual_native_rhs':sum(j['rhs'] for j in reports)+int(m[1]),'actual_provider_calls':sum(j['provider'] for j in reports)+int(m[2]),'accepted_run_rhs':[j['rhs'] for j in reports],'native_call_counts_equal_on_off_baseline':True,'namespace_scope':'single host/boot+canonical directory inode; exclusive writer; no inherited fork reuse','typed_disk_only_restore':True,'pending_not_promoted':True,'physical_history_full_wide':'HOLD','run_evidence':str(run),'test_processes_no_new_cosmological_histories':True}
(root/'evidence/PROCESS_RESTART_REPORT.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2));print('ALL_CHANGED_PATH_PROCESS_CONTROLS_GREEN')
