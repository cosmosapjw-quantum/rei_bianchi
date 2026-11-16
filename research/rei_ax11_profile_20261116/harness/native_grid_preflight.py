#!/usr/bin/env python3
"""Finite native executor. Authored in cloud; transferred without native edits.

One isolated job, no network, no full-history launch, no automatic process retry.
Original checkpoints are read/copied, never modified. All attempts are charged.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time,resource,signal,shutil,traceback

ROOT=Path(sys.argv[1]).resolve()
ALLOC=json.loads((ROOT/'ALLOCATION.json').read_text())
AMEND=json.loads((ROOT/'ALLOCATION_AMENDMENT_3.json').read_text())
ALLOC['caps'].update(AMEND['caps_overrides']);CAP=ALLOC['caps']
previous=json.loads((ROOT/'TIME_PREFLIGHT_JOB_RECEIPT.json').read_text())
START=time.monotonic()-previous['wall_elapsed_s'];records=previous['records'];binaries=previous['binaries']
RUNS=ROOT/'grid_preflight_results';RUNS.mkdir(exist_ok=False)
for pin in binaries.values():assert hashlib.sha256(Path(pin['path']).read_bytes()).hexdigest()==pin['sha256']


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def used_bytes():return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
def save():
    (ROOT/'GRID_PREFLIGHT_JOB_RECEIPT.json').write_text(json.dumps(dict(
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
    inputs=ROOT/'grid_preflight_inputs';inputs.mkdir(exist_ok=False)
    env=os.environ.copy();env.update(CARGO_BUILD_JOBS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',AX11_CACHE='1',AX11_LAZY='1')
    binary=binaries['instrumented']['path'];bindings={};outcomes={}
    schedule=[(case,'E',n) for case in ['PLUS','ZERO'] for n in [32,64]]
    schedule += [('MINUS','A',8)]+[(case,'A',n) for case in ['PLUS','MINUS'] for n in [16,32]]
    for case,axis,n in schedule:
        origin='PLUS' if case=='MINUS' else case
        source=ROOT/'inputs'/f'{origin}.cfg';assert digest(source)==ALLOC['config_pins'][origin]
        text=source.read_text();changes={}
        if case=='MINUS':
            assert text.count('q_ref=0.01\n')==1;text=text.replace('q_ref=0.01\n','q_ref=-0.01\n');changes['q_ref']=-0.01
        if axis=='E':
            assert text.count('energy_subdivisions=16\n')==1;text=text.replace('energy_subdivisions=16\n',f'energy_subdivisions={n}\n');changes['energy_subdivisions']=n
        else:
            assert text.count('n_mu=8\n')==1;text=text.replace('n_mu=8\n',f'n_mu={n}\n');changes['n_mu']=n
        name=f'{case}_{axis}{n}';p=inputs/(name+'.cfg');p.write_text(text)
        bindings[name]={'config_sha256':digest(p),'baseline_config_sha256':digest(source),'changes':changes,'scenario':'PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1','physical_IC':'same original gas/source/clock, q_ref sign declared; nocheckpointgridremapping'}
        cmd=[binary,str(p),'IC',str(RUNS/name),'1024','5000','50000','120','NONE',case]
        run(name,cmd,ROOT,env,120,CAP['per_window_memory_bytes'])
        outcomes[name]=json.loads((RUNS/name/'window_summary.json').read_text())
    (ROOT/'GRID_PREFLIGHT_BINDINGS.json').write_text(json.dumps(bindings,indent=2)+'\n')
    (ROOT/'GRID_PREFLIGHT_OUTCOMES.json').write_text(json.dumps(outcomes,indent=2)+'\n')
    (ROOT/'GRID_PREFLIGHT_STATUS.json').write_text(json.dumps({'status':'SHORT_ORIGINAL_IC_GRID_PREFLIGHT_COMPLETE','original_DAG':'10/17','expansion_DAG':'28/88','AX11_complete':False,'axes':'dE and dmu separately, unchangedlocaltarget1e-5','full_history_runs':0},indent=2)+'\n')
    save();print('SHORT_ORIGINAL_IC_GRID_PREFLIGHT_COMPLETE',flush=True)
try:main()
except BaseException as e:
    save();(ROOT/'GRID_PREFLIGHT_FAILURE.json').write_text(json.dumps({'type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc()},indent=2)+'\n');traceback.print_exc();sys.exit(1)
