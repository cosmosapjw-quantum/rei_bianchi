#!/usr/bin/env python3
"""Exactly two genuine midpoint acceptances per science path, never full refinement."""
import pathlib,subprocess,os,time,signal,json,ast,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
BIN=ROOT/'rei-next-nodes/short-hhe-midpoint/target/release/record_bridge'
RUNS=ROOT/'evidence/campaign-1';RUNS.mkdir(exist_ok=False)
controls=[];commands=[]
def call(mode,store,out,expected=0,env=None):
    out.mkdir(exist_ok=True)
    cmd=[str(BIN),mode,str(store),str(out)]
    result=subprocess.run(cmd,env={**os.environ,**(env or {})},capture_output=True,text=True,timeout=12)
    (out/'stdout').write_text(result.stdout);(out/'stderr').write_text(result.stderr)
    commands.append({'command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    assert result.returncode==expected,(mode,result.returncode,result.stderr)
    return result
def passed(name):controls.append(name);print('GREEN',name,flush=True)
def raw_work(out):return ast.literal_eval((out/'work.txt').read_text())
def startup(out):return ast.literal_eval((out/'startup.txt').read_text())
def work(out):return tuple(a-b for a,b in zip(raw_work(out),startup(out)))
legacy=RUNS/'legacy';off=RUNS/'off';live=RUNS/'live';store=RUNS/'live-store'
call('legacy',RUNS/'unused-legacy',legacy);call('off',RUNS/'unused-off',off)
for k in [1,2]:assert (legacy/f'step{k}.science.txt').read_bytes()==(off/f'step{k}.science.txt').read_bytes()
assert work(legacy)==work(off);passed('unmodified midpoint baseline versus derivative OFF exact gas/owners/traces/work parity')
call('live',store,live)
for k in [1,2]:assert (off/f'step{k}.science.txt').read_bytes()==(live/f'step{k}.science.txt').read_bytes()
assert work(off)==work(live);passed('recording ON versus OFF two-transition exact outputs and actual RHS/sigma counts')
prime=RUNS/'prime';prime.mkdir();restart_store=RUNS/'restart-store'
cmd=[str(BIN),'prime',str(restart_store),str(prime)]
with (prime/'stdout').open('w') as out,(prime/'stderr').open('w') as err:
    child=subprocess.Popen(cmd,stdout=out,stderr=err)
    deadline=time.monotonic()+12
    while not (prime/'READY').exists():
        if child.poll() is not None:raise AssertionError((child.returncode,(prime/'stderr').read_text()))
        if time.monotonic()>deadline:child.kill();child.wait();raise AssertionError('primer timeout')
        time.sleep(.02)
    first_head=(restart_store/'HEAD').read_bytes()
    (ROOT/'evidence/first-accepted-HEAD.bin').write_bytes(first_head)
    child.send_signal(signal.SIGKILL);status=child.wait(timeout=3)
assert status==-signal.SIGKILL
assert (prime/'step1.science.txt').read_bytes()==(live/'step1.science.txt').read_bytes()
commands.append({'command':cmd,'exit':status,'scientific_steps_completed':1,'stop':'actual SIGKILL after committed record'})
passed('actual accepted first transition durably recorded then SIGKILL')
resume=RUNS/'resume';call('resume',restart_store,resume)
assert (resume/'step2.science.txt').read_bytes()==(live/'step2.science.txt').read_bytes()
assert (resume/'typed.bin').read_bytes()==(live/'typed.bin').read_bytes()
assert tuple(a+b for a,b in zip(work(prime),work(resume)))==work(live)
passed('disk-restored continuation second acceptance exact complete typed/state/owner/clock and cumulative work parity')
probe=RUNS/'probe';r=call('probe',restart_store,probe)
assert 'startup=(1, 1) after=(1, 1)' in r.stdout and (probe/'typed.bin').read_bytes()==(live/'typed.bin').read_bytes()
passed('SAME-context recorded-result replay and typed restoration with zero RHS/sigma evaluations')
for mutant in ['clock','source','grid','gas']:
    r=call('probe',restart_store,RUNS/f'mismatch-{mutant}',2,{'REI_RECORD_CONTEXT_MUTANT':mutant})
    assert 'EXACT_SOURCE_GAS_GRID_CLOCK_CONTEXT' in r.stderr and 'COUNTS=(1, 1)' in r.stderr
    passed(f'exact {mutant} mismatch before science refusal')
head=(restart_store/'HEAD').read_bytes();hpath=restart_store/'HEAD'
for name,data,reason in [('corruption',head[:-1]+bytes([head[-1]^1]),'CHECKSUM'),('incomplete',head[:80],'CHECKSUM'),('replay-old-HEAD',first_head,'CHECKPOINT_REPLAY_OR_INCOMPLETE_COMMIT'),('frozen-promotion',b'REI_FROZEN_PANEL_CONTINUATION_CHECKPOINT_V1\n','MIDPOINT_SCHEMA_ONLY_NO_FROZEN_PROMOTION')]:
    hpath.write_bytes(data)
    try:r=call('probe',restart_store,RUNS/name,2);assert reason in r.stderr and 'COUNTS=(1, 1)' in r.stderr
    finally:hpath.write_bytes(head)
    passed(name+' refusal')
lease=restart_store/'attempt-1';saved=lease.read_bytes();lease.unlink()
try:r=call('probe',restart_store,RUNS/'missing-lease',2);assert 'COUNTS=(1, 1)' in r.stderr
finally:lease.write_bytes(saved)
passed('missing committed attempt lease refusal')
r=call('republish',restart_store,RUNS/'duplicate');assert 'REPUBLISH_REFUSED startup=(1, 1) after=(1, 1)' in r.stdout
passed('duplicate accepted-record publication refusal')
foreign=RUNS/'foreign-root';shutil.copytree(restart_store,foreign)
r=call('probe',foreign,RUNS/'foreign-probe',2);assert 'unsupported host/root/fork reuse' in r.stderr
passed('copied-root namespace/inode refusal')
symlink=restart_store/'saved-HEAD';hpath.rename(symlink);hpath.symlink_to(symlink.name)
try:r=call('probe',restart_store,RUNS/'symlink-head',2);assert 'FILE_CAP_OR_SYMLINK' in r.stderr
finally:hpath.unlink();symlink.rename(hpath)
passed('nonregular/symlink HEAD refusal')
r=call('resume',restart_store,RUNS/'extend-window',2);assert 'NO_EXTENSION_BEYOND_TWO_TRANSITIONS' in r.stderr and 'COUNTS=(1, 1)' in r.stderr
passed('two-transition window extension refusal')
report={'controls':controls,'count':len(controls),'all_green':True,'commands':commands,'real_acceptances':{'legacy':2,'off':2,'live':2,'prime':1,'resume':1},'total_real_accepted_transitions':8,'RHS_sigma_per_two_transition_path':work(live),'raw_process_work_two_transition':raw_work(live),'startup_each_process':startup(live),'extra_restart_process_startup':startup(resume),'RHS_sigma_prime':work(prime),'RHS_sigma_resume':work(resume),'typed_sha256':hashlib.sha256((live/'typed.bin').read_bytes()).hexdigest(),'typed_bytes':(live/'typed.bin').stat().st_size,'scope':'first two transactions on original192-subdivision Gauss4/Grid512 normal unprojected cold broadband midpoint path; not an m64 history or projected/full-Wide certificate'}
(ROOT/'evidence/PROCESS_BRIDGE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print('ALL_CHANGED_PATH_CONTROLS_GREEN',len(controls),flush=True)
