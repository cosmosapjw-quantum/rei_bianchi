#!/usr/bin/env python3
"""Finite native executor. Authored in cloud; transferred without native edits.

One isolated job, no network, no full-history launch, no automatic process retry.
Original checkpoints are read/copied, never modified. All attempts are charged.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time,resource,signal,shutil,traceback

ROOT=Path(sys.argv[1]).resolve()
ALLOC=json.loads((ROOT/'ALLOCATION.json').read_text())
AMEND=json.loads((ROOT/'ALLOCATION_AMENDMENT_2.json').read_text())
ALLOC['caps'].update(AMEND['caps_overrides']);CAP=ALLOC['caps']
previous=json.loads((ROOT/'NATIVE_JOB_RECEIPT.json').read_text())
START=time.monotonic()-previous['wall_elapsed_s'];records=previous['records'];binaries=previous['binaries']
RUNS=ROOT/'time_preflight_results';RUNS.mkdir(exist_ok=False)
for pin in binaries.values():assert hashlib.sha256(Path(pin['path']).read_bytes()).hexdigest()==pin['sha256']


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def used_bytes():return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
def save():
    (ROOT/'TIME_PREFLIGHT_JOB_RECEIPT.json').write_text(json.dumps(dict(
        allocation=ALLOC,wall_elapsed_s=time.monotonic()-START,
        historical_cumulative_cost='UNKNOWN; unchanged',records=records,binaries=binaries),indent=2)+'\n')
def run(name,cmd,cwd,env,wall,memory,allow_expected_failure=False):
    assert len(records)<CAP['child_build_test_window_process_starts']
    remaining=CAP['aggregate_native_wall_seconds']-(time.monotonic()-START)
    remaining_cpu=CAP['aggregate_native_cpu_seconds']-sum(r.get('cpu_s',0) for r in records)
    wall=min(wall,remaining,remaining_cpu)
    assert wall>1 and used_bytes()<CAP['aggregate_output_and_build_bytes']-ALLOC['terminal_reserve_bytes']
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(int(wall)+1,int(wall)+2))
        resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
        resource.setrlimit(resource.RLIMIT_FSIZE,(CAP['per_window_output_bytes'],CAP['per_window_output_bytes']))
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
    if reason or (code!=0 and not allow_expected_failure):raise RuntimeError(f'{name}: {reason or code}; no process retry')
    return rec

def check_inputs():
    manifest=json.loads((ROOT/'source/SOURCE_PACKAGE_MANIFEST.json').read_text())
    for p,v in manifest['files'].items():
        actual=ROOT/'source'/p
        assert actual.stat().st_size==v['bytes'] and digest(actual)==v['sha256'], p
    # A read-only copy from already inspected original output directories.
    base=Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/axbi_goal_20261014/runs')
    locations={'ZERO':base/'flrw/32d11e733155/ZERO','PLUS':base/'paired/32d11e733155/SHEAR_PLUS'}
    inp=ROOT/'inputs';inp.mkdir(exist_ok=False)
    receipts={}
    for case,d in locations.items():
        for fn,target,pin in [('config.cfg',case+'.cfg',ALLOC['config_pins'][case]),('checkpoints/00199980.txt',case+'_199980.txt',ALLOC['checkpoint_pins'][case+'_199980'])]:
            src=d/fn;assert digest(src)==pin,(case,fn)
            shutil.copyfile(src,inp/target)
            receipts[target]={'sha256':pin,'bytes':(inp/target).stat().st_size,'original':str(src)}
    (ROOT/'INPUT_RECEIPT.json').write_text(json.dumps(receipts,indent=2)+'\n')


def main():
    manifest=json.loads((ROOT/'source/SOURCE_PACKAGE_MANIFEST.json').read_text())
    for p,v in manifest['files'].items():assert digest(ROOT/'source'/p)==v['sha256'],p
    inputs=ROOT/'time_preflight_inputs';inputs.mkdir(exist_ok=False)
    env=os.environ.copy();env.update(CARGO_BUILD_JOBS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',AX11_CACHE='1',AX11_LAZY='1')
    binary=binaries['instrumented']['path'];bindings={};outcomes={}
    def variant(case,level,start_floor=False):
        source=ROOT/'inputs'/f'{case}.cfg';assert digest(source)==ALLOC['config_pins'][case]
        text=source.read_text();assert text.count('local_target=1e-05\n')==1
        target={1:'2.5e-6',2:'6.25e-7'}[level]
        text=text.replace('local_target=1e-05\n',f'local_target={target}\n')
        if start_floor:
            assert text.count('initial_dln_a=0.0001\n')==1
            text=text.replace('initial_dln_a=0.0001\n','initial_dln_a=1e-10\n')
        name=f'{case}_T{level}'+('_FLOOR_START' if start_floor else '_ORIGINAL_START')
        p=inputs/(name+'.cfg');p.write_text(text)
        bindings[name]={'config_sha256':digest(p),'baseline_config_sha256':digest(source),'changes':{'local_target':target,**({'initial_dln_a':'1e-10'} if start_floor else {})},'physical_IC_unchanged':True,'same_model_clock_source':True}
        return name,p
    for case in ['PLUS','ZERO']:
        name,cfg=variant(case,1)
        cmd=[binary,str(cfg),'IC',str(RUNS/name),'2048','8000','60000','120','NONE',case]
        run(name,cmd,ROOT,env,120,CAP['per_window_memory_bytes'])
        outcomes[name]=json.loads((RUNS/name/'window_summary.json').read_text())
    failed=[]
    for case in ['PLUS','ZERO']:
        name,cfg=variant(case,2)
        cmd=[binary,str(cfg),'IC',str(RUNS/name),'4096','15000','110000','120','NONE',case]
        rec=run(name,cmd,ROOT,env,120,CAP['per_window_memory_bytes'],allow_expected_failure=True)
        summary=json.loads((RUNS/name/'window_summary.json').read_text());outcomes[name]=summary
        if rec['returncode']!=0:
            assert rec['returncode']==2 and summary['status']=='AXBI_REJECT_CAP' and summary['delta_counts']['accepted']==0,('UNEXPECTED_FAILURE',name)
            failed.append(case)
    for case in failed:
        name,cfg=variant(case,2,start_floor=True)
        cmd=[binary,str(cfg),'IC',str(RUNS/name),'4096','15000','110000','120','NONE',case]
        run(name,cmd,ROOT,env,120,CAP['per_window_memory_bytes'])
        outcomes[name]=json.loads((RUNS/name/'window_summary.json').read_text())
    (ROOT/'TIME_PREFLIGHT_BINDINGS.json').write_text(json.dumps(bindings,indent=2)+'\n')
    (ROOT/'TIME_PREFLIGHT_OUTCOMES.json').write_text(json.dumps(outcomes,indent=2)+'\n')
    (ROOT/'TIME_PREFLIGHT_STATUS.json').write_text(json.dumps({'status':'SHORT_ORIGINAL_IC_TIME_PREFLIGHT_COMPLETE','original_DAG':'10/17','expansion_DAG':'28/88','AX11_complete':False,'failed_original_T2_startups_preserved':failed,'startup_correction':'only initial_dln_a=1e-10, original1e-10minimum and6.25e-7localtarget unchanged','full_history_runs':0},indent=2)+'\n')
    save();print('SHORT_ORIGINAL_IC_TIME_PREFLIGHT_COMPLETE',flush=True)
try:main()
except BaseException as e:
    save();(ROOT/'TIME_PREFLIGHT_FAILURE.json').write_text(json.dumps({'type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc()},indent=2)+'\n');traceback.print_exc();sys.exit(1)
