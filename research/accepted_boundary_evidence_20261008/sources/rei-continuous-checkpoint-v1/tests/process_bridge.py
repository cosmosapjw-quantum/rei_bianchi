#!/usr/bin/env python3
"""Actual cold broadband frozen-panel caller: one existing final interval per lane."""
import pathlib,subprocess,os,time,signal,json,hashlib,struct,shutil,resource
root=pathlib.Path(__file__).resolve().parents[1]
binary=root/'target/debug/continuous_receiver'
parent=root/'evidence/runs';parent.mkdir(exist_ok=True)
for i in range(128):
 run=parent/f'case-{i}'
 try:run.mkdir();break
 except FileExistsError:continue
else:raise RuntimeError('bounded case allocation')
controls=[];commands=[]
def working(name):
 d=run/name;d.mkdir();(d/'results').mkdir();(d/'inputs').symlink_to(root/'vendor/frozen-panel-fixed-j32-final-interval-v1/inputs',target_is_directory=True);(d/'oracle.py').symlink_to(root/'oracle.py');return d
context={**os.environ,'REI_WORKERS':'1','REI_SIMD':'scalar','CONTINUATION_WALL_BUDGET_SECONDS':'90','PYTHONDONTWRITEBYTECODE':'1'}
def invoke(name,mode=None,namespace=None,expected=0,extra=None):
 d=working(name);env=dict(context)
 if mode:env['REI_CONTINUOUS_DURABLE']=mode
 else:env.pop('REI_CONTINUOUS_DURABLE',None)
 if namespace:env['REI_CONTINUOUS_RUN_ROOT']=str(namespace)
 if extra:env.update(extra)
 t=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
 result=subprocess.run([str(binary)],cwd=d,env=env,capture_output=True,text=True,timeout=95)
 after=resource.getrusage(resource.RUSAGE_CHILDREN)
 (d/'stdout').write_text(result.stdout);(d/'stderr').write_text(result.stderr)
 commands.append({'case':name,'mode':mode,'exit':result.returncode,'CPU_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'wall_s':time.monotonic()-t,'maxrss_kib':after.ru_maxrss})
 assert result.returncode==expected,(name,result.returncode,result.stderr[-1000:],result.stdout[-1000:])
 return d,result
# Durable k3 prime uses the exact accepted cold broadband checkpoint and actual loader.
namespace=run/'frozen-run';d=working('prime');env={**context,'REI_CONTINUOUS_DURABLE':'prime','REI_CONTINUOUS_RUN_ROOT':str(namespace)}
fout=(d/'stdout').open('w');ferr=(d/'stderr').open('w');t=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
p=subprocess.Popen([str(binary)],cwd=d,env=env,stdout=fout,stderr=ferr)
try:
 while not (namespace/'READY_FOR_KILL').exists():
  assert p.poll() is None,(d/'stderr').read_text()
  if time.monotonic()-t>15:raise TimeoutError('k3 checkpoint prime')
  time.sleep(.02)
 p.kill();assert p.wait(timeout=3)==-signal.SIGKILL
finally:
 if p.poll() is None:p.kill();p.wait()
 fout.close();ferr.close()
after=resource.getrusage(resource.RUSAGE_CHILDREN);commands.append({'case':'prime','mode':'prime','exit':-9,'CPU_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'wall_s':time.monotonic()-t,'maxrss_kib':after.ru_maxrss})
probe,_=invoke('k3-probe','probe',namespace);assert 'stage=3' in (probe/'stdout').read_text();controls.append('SIGKILL then typed disk restore of exact admitted k3 cold broadband state')
head=namespace/'HEAD';saved=head.read_bytes();magic=b'REI_FROZEN_PANEL_CONTINUATION_CHECKPOINT_V1\n'
def rehash(payload):return magic+hashlib.sha256(payload).hexdigest().encode()+b'\n'+payload
payload=bytearray(saved[len(magic)+65:]);pos=0
def skiptext():
 global pos
 n=struct.unpack_from('<Q',payload,pos)[0];pos+=8+n
skiptext();skiptext();pos+=8 # BUILD_PIN, run namespace, committed attempt
config_pos=pos+8;skiptext();gas_pos=pos;clock_pos=gas_pos+32;mesh_count_pos=clock_pos+17*8
mesh_n=struct.unpack_from('<Q',payload,mesh_count_pos)[0];panel_l_pos=mesh_count_pos+8+mesh_n*8+8+8
# Rechecksummed exact identity mismatches; these must refuse before any new step.
for name,at,needle in [('clock',clock_pos,'EXACT_CLOCK_MISMATCH'),('panel',panel_l_pos,'EXACT_PANEL_MISMATCH'),('gas-context',gas_pos,'GAS_CONTEXT_MISMATCH'),('source-context',config_pos,'SOURCE_CONTEXT_MISMATCH')]:
 damaged=payload[:];damaged[at]^=1;head.write_bytes(rehash(damaged))
 _,result=invoke(name,'probe',namespace,expected=1);assert needle in result.stderr;head.write_bytes(saved);controls.append(name+' exact mismatch refusal with valid checksum')
head.write_bytes(saved[:-19]);invoke('incomplete','probe',namespace,expected=1);head.write_bytes(saved);controls.append('incomplete checkpoint refusal')
lease=namespace/'attempt-0';lease.rename(namespace/'SAVED_ATTEMPT');invoke('missing-lease','probe',namespace,expected=1);(namespace/'SAVED_ATTEMPT').rename(lease);controls.append('missing committed namespace lease refusal')
_,refused=invoke('be-handoff',extra={'REI_NATIVE_BE_HANDOFF':'1'},expected=1);assert 'NATIVE_BE_INCOMPATIBLE' in refused.stderr;assert 'COUNT characteristic_segments' not in refused.stdout;controls.append('BE solver handoff refused before characteristic/native work')
# A checkpoint-only crash uses the real admitted k3 state and never advances science.
pending_namespace=run/'pending-frozen-run'
_,stopped=invoke('pending-stop','pending-control',pending_namespace,expected=73)
assert 'NO_SCIENCE_TRIAL' in stopped.stderr
pending=list(pending_namespace.glob('pending-*'));assert len(pending)==1
saved_pending=pending[0].read_bytes();pending_head=(pending_namespace/'HEAD').read_bytes()
assert (pending_namespace/'attempt-1').exists()
_,restored_pending=invoke('pending-probe','probe',pending_namespace)
assert 'stage=3' in restored_pending.stdout
assert (pending_namespace/'HEAD').read_bytes()==pending_head and pending[0].read_bytes()==saved_pending
controls.append('checkpoint-only real k3 pending process-stop preserves HEAD and consumed lease; never promoted')
_,unknown=invoke('unknown-mode','invalid-mode',namespace,expected=1);assert 'UNKNOWN_DURABLE_MODE' in unknown.stderr;controls.append('unknown opt-in mode refuses before Frame/science')
# Only two real final-interval numerical executions. Both retain all original gates.
baseline,first=invoke('uninterrupted-off')
assert 'FOUR_INTERVAL_IMPLEMENTATION_GATES=PASS' in first.stdout
continued,second=invoke('disk-restart-accept','resume',namespace)
assert 'FOUR_INTERVAL_IMPLEMENTATION_GATES=PASS' in second.stdout
assert 'FROZEN_DURABLE_COMMIT stage=4 directory_synced=true' in second.stdout
for file in ['continuation_k4_oracle.csv','precommit_k4_HIGH_PRECISION.json']:
 assert (baseline/'results'/file).read_bytes()==(continued/'results'/file).read_bytes(),file
controls.append('actual original midpoint characteristic k3->k4 acceptance; exact uninterrupted/restarted oracle bytes')
# Final typed disk-only state restores the accepted k4 panels and loss registry.
final_probe,third=invoke('k4-final-restore','probe',namespace)
assert 'stage=4' in third.stdout
assert (final_probe/'results/continuation_oracle.csv').read_bytes()==(continued/'results/continuation_oracle.csv').read_bytes()
controls.append('accepted k4 full typed panel/ledger/source audit restore with exact final oracle bytes')
# A fourth-stage checkpoint cannot silently extend past the frozen history window.
_,past=invoke('no-extension','resume',namespace,expected=1);assert 'NO_HISTORY_EXTENSION' in past.stderr;controls.append('frozen-window end refuses further continuation')
# Numerical work is in the original segment counters, not mislabeled as BASS/native BE solves.
def counts(text):
 values={}
 for line in text.splitlines():
  if line.startswith('COUNT '):_,name,value=line.split();values[name]=int(value)
 return values
b=counts(first.stdout);s=counts(second.stdout)
assert b['characteristic_segments']==s['characteristic_segments'];assert b['endpoint_fits']==s['endpoint_fits'];assert b['opacity_calls']==s['opacity_calls']
assert b['zero_photo_rhs_calls']==s['zero_photo_rhs_calls'];controls.append('OFF/restart original arithmetic work-count parity')
report={'controls_passed':controls,'selected_real_receiver':'continuation_driver::run -> step -> physics::Frame::replay/stock_density_control','actual_final_interval_acceptances':2,'characteristic_segments_each':b['characteristic_segments'],'endpoint_fits_each':b['endpoint_fits'],'opacity_calls_each':b['opacity_calls'],'zero_photo_rhs_calls_each':b['zero_photo_rhs_calls'],'original_config_and_tolerances_preserved':True,'BE_handoff':'BLOCKED_INCOMPATIBLE_SOLVER_AND_STATE','history_claim':'FROZEN_PANEL_K3_TO_K4_ONLY','physical_full_history_full_wide':'HOLD','namespace':'local host/boot/directory only','run_evidence':str(run),'commands':commands}
(root/'evidence/PROCESS_BRIDGE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));print('ALL_FROZEN_CONTINUOUS_CHANGED_PATH_CONTROLS_GREEN')
