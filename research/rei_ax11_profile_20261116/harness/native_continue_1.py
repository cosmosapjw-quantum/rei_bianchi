#!/usr/bin/env python3
"""Finite native executor. Authored in cloud; transferred without native edits.

One isolated job, no network, no full-history launch, no automatic process retry.
Original checkpoints are read/copied, never modified. All attempts are charged.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time,resource,signal,shutil,traceback

ROOT=Path(sys.argv[1]).resolve()
ALLOC=json.loads((ROOT/'ALLOCATION.json').read_text())
AMEND=json.loads((ROOT/'ALLOCATION_AMENDMENT_1.json').read_text())
ALLOC['caps'].update(AMEND['caps_overrides'])
CAP=ALLOC['caps']
prior_path=ROOT/'NATIVE_JOB_RECEIPT.json'
previous=json.loads(prior_path.read_text())
backup=ROOT/'NATIVE_ATTEMPT_1.json'
assert not backup.exists(), 'No automatic continuation replay'
backup.write_bytes(prior_path.read_bytes())
START=time.monotonic()-previous['wall_elapsed_s']
records=previous['records']; binaries=previous['binaries']
RUNS=ROOT/'results'; assert RUNS.exists() and not any(RUNS.iterdir())
for kind,pin in binaries.items():
    assert hashlib.sha256(Path(pin['path']).read_bytes()).hexdigest()==pin['sha256']
(ROOT/'test_temp').mkdir(exist_ok=False)


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def used_bytes():return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
def save():
    (ROOT/'NATIVE_JOB_RECEIPT.json').write_text(json.dumps(dict(
        allocation=ALLOC,wall_elapsed_s=time.monotonic()-START,
        historical_cumulative_cost='UNKNOWN; unchanged',records=records,binaries=binaries),indent=2)+'\n')
def run(name,cmd,cwd,env,wall,memory):
    assert len(records)<CAP['child_build_test_window_process_starts']
    remaining=CAP['aggregate_native_wall_seconds']-(time.monotonic()-START)
    remaining_cpu=CAP['aggregate_native_cpu_seconds']-sum(r.get('cpu_s',0) for r in records)
    wall=min(wall,remaining,remaining_cpu)
    assert wall>1 and used_bytes()<CAP['aggregate_output_and_build_bytes']-ALLOC['terminal_reserve_bytes']
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(int(wall)+1,int(wall)+2))
        resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
        file_limit=AMEND['scoped_sparse_test_file_limit_bytes'] if name.startswith('test_') else CAP['per_window_output_bytes']
        resource.setrlimit(resource.RLIMIT_FSIZE,(file_limit,file_limit))
    log=ROOT/(name+'.log'); t=time.monotonic(); max_rss=0
    rec=dict(name=name,command=cmd,environment={k:env.get(k) for k in ('RUSTFLAGS','AX11_CACHE','AX11_LAZY','CARGO_BUILD_JOBS')},status='STARTED',wall_cap=wall,memory_cap=memory)
    records.append(rec);save()
    with log.open('wb') as f:
        p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=limits)
        reason=None
        while p.poll() is None:
            try:
                for line in Path(f'/proc/{p.pid}/status').read_text().splitlines():
                    if line.startswith('VmHWM:'):max_rss=max(max_rss,int(line.split()[1])*1024)
            except FileNotFoundError:pass
            if time.monotonic()-t>wall:reason='WALL_CAP'
            if used_bytes()>CAP['aggregate_output_and_build_bytes']-ALLOC['terminal_reserve_bytes']:reason='AGGREGATE_OUTPUT_CAP'
            out=RUNS/name
            if out.exists() and sum(x.stat().st_size for x in out.rglob('*') if x.is_file())>CAP['per_window_output_bytes']-1048576:reason='WINDOW_OUTPUT_CAP'
            if reason:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=2)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                break
            time.sleep(.15)
        code=p.wait()
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    rec.update(returncode=code,status=reason or ('COMPLETE' if code==0 else 'FAILED'),wall_s=time.monotonic()-t,
       cpu_s=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime),peak_rss_bytes=max_rss,
       stdout_log=log.name,log_sha256=digest(log))
    save(); print(json.dumps(rec),flush=True)
    if code!=0 or reason:raise RuntimeError(f'{name}: {reason or code}; no process retry')

def check_inputs():
    manifest=json.loads((ROOT/'source/SOURCE_PACKAGE_MANIFEST.json').read_text())
    for p,v in manifest['files'].items():
        actual=ROOT/'source'/p
        assert actual.stat().st_size==v['bytes'] and digest(actual)==v['sha256'], p
    # A read-only copy from already inspected original output directories.
    base=Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/axbi_goal_20261014/runs')
    locations={'ZERO':base/'flrw/32d11e733155/ZERO','PLUS':base/'paired/32d11e733155/SHEAR_PLUS'}
    inp=ROOT/'inputs';assert inp.exists()
    receipts={}
    for case,d in locations.items():
        for fn,target,pin in [('config.cfg',case+'.cfg',ALLOC['config_pins'][case]),('checkpoints/00199980.txt',case+'_199980.txt',ALLOC['checkpoint_pins'][case+'_199980'])]:
            src=d/fn;assert digest(src)==pin,(case,fn)
            assert digest(inp/target)==pin
            receipts[target]={'sha256':pin,'bytes':(inp/target).stat().st_size,'original':str(src)}
    (ROOT/'INPUT_RECEIPT.json').write_text(json.dumps(receipts,indent=2)+'\n')

def main():
    check_inputs()
    env=os.environ.copy();env.update(CARGO_BUILD_JOBS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',RUSTFLAGS='-C codegen-units=1')
    cargo=shutil.which('cargo') or '/home/cosmosapjw/.cargo/bin/cargo'
    for kind in []: # original and instrumented binary hashes verified above; no rebuild
        cwd=ROOT/'source'/kind/'rust/rei_microphysics'
        e=env.copy()
        if kind=='instrumented':e['RUSTFLAGS']+=' --cfg ax11_profile -A unexpected_cfgs'
        run('build_'+kind,[cargo,'build','--release','--locked','--offline','--example','ax11_profile_window'],cwd,e,180,CAP['per_build_memory_bytes'])
        b=cwd/'target/release/examples/ax11_profile_window';binaries[kind]={'path':str(b),'sha256':digest(b),'bytes':b.stat().st_size};save()
    cwd=ROOT/'source/instrumented/rust/rei_microphysics';e=env.copy();e.update(RUSTFLAGS=env['RUSTFLAGS']+' --cfg ax11_profile -A unexpected_cfgs',AX11_CACHE='1',AX11_LAZY='1',TMPDIR=str(ROOT/'test_temp'))
    tests=[['--test','ax11_invariance'],['--test','axbi_driver','sparse_full_spectra_keep_each_abundance_and_align_terminal_resume_and_cap'],['--test','axbi_driver','hard_caps_charge_started_trials_and_resume_without_off_by_one']]
    for i,selection in list(enumerate(tests))[1:]:run('test_'+str(i)+'_corrected_fsize',[cargo,'test','--release','--locked','--offline']+selection+['--','--test-threads=1'],cwd,e,180,CAP['per_build_memory_bytes'])
    schedule=[]
    for mode in ['original','instrumented','cache','lazy']:schedule.append(('PLUS','IC',mode,1024,0))
    for mode in ['original','lazy']:schedule.append(('ZERO','IC',mode,1024,0))
    for repeat in range(2):
        for mode in ['original','lazy']:schedule.append(('PLUS','PLATEAU',mode,128,repeat))
    for mode in ['original','lazy']:schedule.append(('ZERO','PLATEAU',mode,128,0))
    for case,window,mode,steps,repeat in schedule:
        name=f'{case}_{window}_{mode}_{repeat}'
        b=binaries['original' if mode=='original' else 'instrumented']['path']
        e=env.copy();e['AX11_CACHE']='1' if mode in ['cache','lazy'] else '0';e['AX11_LAZY']='1' if mode=='lazy' else '0'
        checkpoint='IC' if window=='IC' else str(ROOT/'inputs'/f'{case}_199980.txt')
        cmd=[b,str(ROOT/'inputs'/f'{case}.cfg'),checkpoint,str(RUNS/name),str(steps),str(5000 if window=='IC' else 1000),str(50000 if window=='IC' else 10000),'120','NONE',case]
        run(name,cmd,ROOT,e,120,CAP['per_window_memory_bytes'])
        # Immediate exact-state gate against the same-source original run.
        if mode!='original':
            ref=RUNS/f'{case}_{window}_original_{repeat if window=="PLATEAU" and case=="PLUS" else 0}'
            cand=RUNS/name
            assert digest(ref/'raw/state_trace.bin')==digest(cand/'raw/state_trace.bin'),('STATE_BIT_MISMATCH',name)
            for fn in ['history.csv','abundances.csv','ledgers.csv','feedback.csv']:
                assert digest(ref/fn)==digest(cand/fn),('OUTPUT_MISMATCH',name,fn)
    # Optional common-a refinement is a separately gated second phase, so no
    # process is started here merely because unused allocation remains.
    (ROOT/'STATUS.json').write_text(json.dumps({'status':'BOUNDED_PROFILE_COMPLETE','full_history_runs':0,'original_DAG':'10/17','expansion_DAG':'28/88','AX11_complete':False,'optional_time_preflight':'NOT_STARTED_PENDING_MEASURED_PROFILE_GATE'},indent=2)+'\n')
    save()
    print('BOUNDED_PROFILE_COMPLETE',flush=True)

try:main()
except BaseException as e:
    save()
    (ROOT/'FAILURE_CONTINUATION_1.json').write_text(json.dumps({'type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'automatic_retries':0,'historical_cumulative_cost':'UNKNOWN unchanged'},indent=2)+'\n')
    traceback.print_exc();sys.exit(1)
