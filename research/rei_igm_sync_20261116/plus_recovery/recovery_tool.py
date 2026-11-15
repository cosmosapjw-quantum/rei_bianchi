#!/usr/bin/env python3
"""Exact-source preparation and one finite AX08 continuation. No automatic retry."""
import argparse, datetime, fcntl, hashlib, io, json, os, pathlib, shutil, subprocess, tarfile, time

BUNDLE = pathlib.Path(__file__).resolve().parent
BASE = '44af42ba60a44a3e9ee23288b766c025c4e0de11'
CONFIG_SHA = 'b9a8bdeaf61a68839e23486fa8ad0740fe1318c55cbc7f522e11cacbb4ff21c0'
CHECKPOINT_SHA = '7af4071c8267f349c0a1d106759aa39d5fa47423ecbb76137692d31d1f5f82a2'
IDENTITY_SHA = 'd7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185'
INCLUDED = [*(f'rust/rei_microphysics/src/{n}.rs' for n in ['axbi_driver','axbi_background','axbi_sources','axbi_rates','igm_rates','igm_thermal','igm_state','igm_background','atomic_provider','bianchi_i','hhe_events']), 'rust/rei_microphysics/examples/axbi_reionization.rs','rust/rei_microphysics/src/lib.rs','rust/rei_microphysics/Cargo.toml','docs/fastest_track_chat/REI-AXBI-GOAL-20261014/OUTPUT_CONTRACT.json','research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json','research/axbi_goal_20261014/scenario/AX05_NUMERICAL_CONTRACT.md']

def digest(p):
    h=hashlib.sha256()
    with pathlib.Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def verify(p, sha):
    actual=digest(p)
    if actual!=sha:raise RuntimeError(f'BYTE_IDENTITY_MISMATCH {p}: {actual}')

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write_json(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

def bundle_identity():
    m=json.loads((BUNDLE/'BUNDLE_MANIFEST.json').read_text())
    verify(BUNDLE/'ALLOCATION.json',m['allocation_sha256'])
    verify(BUNDLE/'axbi_plus_recovery_002.rs',m['wrapper_sha256'])
    verify(BUNDLE/'recovery_tool.py',m['launcher_sha256'])
    return m

def predecessor(repo):
    p=repo/'research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_PLUS_continuation_001'
    verify(p/'checkpoint.txt',CHECKPOINT_SHA)
    verify(p/'source_identity.txt',IDENTITY_SHA)
    verify(p/'config.cfg',CONFIG_SHA)
    if (p/'case_id.txt').read_text()!='SHEAR_PLUS':raise RuntimeError('CASE_ID_MISMATCH')
    # Preserve a newly discovered terminal receipt for review; do not overwrite it.
    if (p/'RETURN.txt').exists():raise RuntimeError('PREDECESSOR_CHANGED_TERMINAL_REVIEW_REQUIRED')
    return p

def source_sections(pred):
    sections=(pred/'source_identity.txt').read_bytes().split(b'\nAXBI_SOURCE_BOUNDARY\n')
    if len(sections)!=len(INCLUDED):raise RuntimeError('SOURCE_CORPUS_SHAPE')
    return dict(zip(INCLUDED,sections))

def native_argv(repo, stage, output, mode):
    pred=predecessor(repo)
    return [str(stage/'rust/rei_microphysics/target/release/examples/axbi_plus_recovery_002'), '--config',str(pred/'config.cfg'),'--predecessor',str(pred),'--output',str(output),'--case','SHEAR_PLUS','--allocation',str(stage/'ALLOCATION.json'),'--mode',mode]

def prepare(repo,stage):
    m=bundle_identity();pred=predecessor(repo)
    if stage.exists():raise RuntimeError('STAGE_EXISTS_DO_NOT_OVERWRITE')
    blob=subprocess.check_output(['git','-C',str(repo),'archive','--format=tar',BASE,'rust/rei_microphysics','docs/fastest_track_chat/REI-AXBI-GOAL-20261014','research/axbi_goal_20261014/scenario'])
    stage.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(blob)) as tf:
        for member in tf.getmembers():
            p=pathlib.PurePosixPath(member.name)
            if p.is_absolute() or '..' in p.parts or member.issym() or member.islnk():raise RuntimeError('ARCHIVE_PATH_NOT_PLAIN')
        tf.extractall(stage)
    restored=[];manifest={}
    for rel,b in source_sections(pred).items():
        p=stage/rel
        if not p.exists() or p.read_bytes()!=b:
            restored.append(rel);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        manifest[rel]=hashlib.sha256(b).hexdigest()
    for name in ['ALLOCATION.json','BUNDLE_MANIFEST.json','recovery_tool.py']:
        shutil.copyfile(BUNDLE/name,stage/name)
    shutil.copyfile(BUNDLE/'axbi_plus_recovery_002.rs',stage/'rust/rei_microphysics/examples/axbi_plus_recovery_002.rs')
    # Keep a complete immutable wrapper copy beside the allocation for handoff.
    shutil.copyfile(BUNDLE/'axbi_plus_recovery_002.rs',stage/'axbi_plus_recovery_002.rs')
    write_json(stage/'SOURCE_CORPUS_MANIFEST.json',{'base':BASE,'source_identity_sha256':IDENTITY_SHA,'files':manifest,'restored_to_embedded_identity':restored})
    cmd=['cargo','build','--release','--manifest-path','rust/rei_microphysics/Cargo.toml','--locked','--example','axbi_plus_recovery_002']
    started=time.monotonic()
    p=subprocess.run(cmd,cwd=stage,capture_output=True,text=True,timeout=120)
    (stage/'BUILD.stdout').write_text(p.stdout);(stage/'BUILD.stderr').write_text(p.stderr)
    receipt={'observed_utc':utc(),'command':cmd,'exit_code':p.returncode,'wall_s':time.monotonic()-started,'base_commit':BASE,'allocation_sha256':m['allocation_sha256'],'wrapper_sha256':m['wrapper_sha256'],'cargo_lock_sha256':digest(stage/'rust/rei_microphysics/Cargo.lock'),'rustc':subprocess.check_output(['rustc','--version'],text=True).strip(),'cargo':subprocess.check_output(['cargo','--version'],text=True).strip(),'science_runs':0}
    if p.returncode==0:receipt['binary_sha256']=digest(stage/'rust/rei_microphysics/target/release/examples/axbi_plus_recovery_002')
    write_json(stage/'BUILD_RECEIPT.json',receipt)
    if p.returncode:raise RuntimeError('BUILD_FAILED_INSPECT_PRESERVED_STDERR')
    print(json.dumps(receipt))

def active_native():
    out=[]
    for p in pathlib.Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            a=(p/'cmdline').read_bytes().split(b'\0')
            if a and pathlib.Path(os.fsdecode(a[0])).name in ['axbi_reionization','axbi_plus_resource_continuation','axbi_plus_recovery_002']:out.append({'pid':int(p.name),'argv':[os.fsdecode(x) for x in a if x]})
        except (FileNotFoundError,PermissionError,ProcessLookupError):pass
    return out

def preflight(repo,stage,output):
    m=bundle_identity();pred=predecessor(repo)
    if output.exists():raise RuntimeError('OUTPUT_EXISTS_DO_NOT_OVERWRITE')
    for rel,b in source_sections(pred).items():verify(stage/rel,hashlib.sha256(b).hexdigest())
    verify(stage/'ALLOCATION.json',m['allocation_sha256'])
    verify(stage/'rust/rei_microphysics/examples/axbi_plus_recovery_002.rs',m['wrapper_sha256'])
    build=json.loads((stage/'BUILD_RECEIPT.json').read_text())
    verify(stage/'rust/rei_microphysics/target/release/examples/axbi_plus_recovery_002',build['binary_sha256'])
    running=active_native()
    if running:raise RuntimeError('LIVE_NATIVE_PROCESS_HOLD '+json.dumps(running))
    if shutil.disk_usage(stage).free < 3*1024**3:raise RuntimeError('DISK_HEADROOM_UNDER_3_GIB')
    for tool in ['/usr/bin/time','/usr/bin/timeout','/usr/bin/taskset','/usr/bin/prlimit']:
        if not pathlib.Path(tool).is_file():raise RuntimeError('REQUIRED_LAUNCH_TOOL_MISSING '+tool)
    result=subprocess.run(native_argv(repo,stage,output,'check'),cwd=stage,capture_output=True,text=True,timeout=30)
    if result.returncode or 'AXBI_RECOVERY_NATIVE_PREFLIGHT_PASS' not in result.stdout:raise RuntimeError('NATIVE_PREFLIGHT_FAILED '+result.stdout+result.stderr)
    receipt={'observed_utc':utc(),'status':'NATIVE_PREFLIGHT_PASS','native_stdout':result.stdout.strip(),'predecessor':str(pred),'checkpoint_sha256':CHECKPOINT_SHA,'compiled_physics_identity_sha256':IDENTITY_SHA,'binary_sha256':build['binary_sha256'],'wrapper_sha256':m['wrapper_sha256'],'allocation_sha256':m['allocation_sha256'],'live_native_processes':running,'output_absent':True,'science_runs':0}
    write_json(stage/'PREFLIGHT_RECEIPT.json',receipt)
    print(json.dumps(receipt));return receipt

def execute(repo,stage,output):
    # Lock covers reservation, native process, and terminal receipt.
    with (stage/'run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        pf=preflight(repo,stage,output)
        raw=stage/'recovery_002_raw'
        if raw.exists():raise RuntimeError('RAW_OUTPUT_EXISTS_DO_NOT_OVERWRITE')
        cpu=min(os.sched_getaffinity(0));raw.mkdir()
        argv=['/usr/bin/time','-v','-o',str(raw/'time.log'),'/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=1s','2699s','/usr/bin/taskset','-c',str(cpu),'/usr/bin/prlimit','--as=2147483648','--fsize=2013265920','--cpu=2700:2700','--',*native_argv(repo,stage,output,'execute')]
        reservation={'observed_utc':utc(),'status':'RESERVED_ONE_START_NO_RETRY','argv':argv,'cwd':str(stage),'preflight':pf,'prior_actual_cost':'UNKNOWN; prior full allocation reserved in ALLOCATION.json','orphan_history_rows_quarantined':47}
        with (stage/'RUN_RESERVED.json').open('x') as f:json.dump(reservation,f,indent=2)
        env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        started=time.monotonic()
        with (raw/'stdout.log').open('wb') as out,(raw/'stderr.log').open('wb') as err:
            proc=subprocess.Popen(argv,cwd=stage,env=env,stdout=out,stderr=err)
            write_json(stage/'RUN_PROCESS.json',{'observed_utc':utc(),'pid':proc.pid,'argv':argv,'maximum_starts':1})
            rc=proc.wait()
        terminal={'observed_utc':utc(),'exit_code':rc,'launcher_wall_s':time.monotonic()-started,'status':'TERMINATED_PENDING_SCIENCE_REVIEW','scientific_admission':'NOT_ISSUED','prior_actual_total_cost':'UNKNOWN'}
        scientific_bytes=sum(p.stat().st_size for p in output.rglob('*') if p.is_file()) if output.exists() else 0
        raw_bytes=sum(p.stat().st_size for p in raw.rglob('*') if p.is_file())
        terminal['output_accounting']={'scientific_bytes':scientific_bytes,'raw_launcher_bytes':raw_bytes,'combined_bytes':scientific_bytes+raw_bytes,'under_total_allocation':scientific_bytes+raw_bytes<=2147483648,'enforcement':'Native aggregate scientific cap plus terminal aggregate check; prlimit fsize is per-file only.'}
        for n in ['RETURN.txt','checkpoint.txt','source_identity.txt','execution_wrapper_identity.json']:
            p=output/n
            terminal[n]={'exists':p.exists(),'sha256':digest(p) if p.is_file() else None}
        if (output/'RETURN.txt').exists():terminal['RETURN_text']=(output/'RETURN.txt').read_text()
        write_json(stage/'RUN_TERMINAL_RECEIPT.json',terminal);print(json.dumps(terminal))
        return rc

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','preflight','execute']);p.add_argument('--repo',type=pathlib.Path,required=True);p.add_argument('--stage',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path)
    a=p.parse_args();a.repo=a.repo.resolve();a.stage=a.stage.resolve();a.output=(a.output or a.stage/'SHEAR_PLUS_continuation_002').resolve()
    if a.stage==a.repo or a.repo in a.stage.parents:raise RuntimeError('STAGE_MUST_BE_OUTSIDE_MUTABLE_OWNER_REPO')
    if a.stage not in a.output.parents:raise RuntimeError('OUTPUT_MUST_BE_STRICT_DESCENDANT_OF_STAGE')
    if a.mode=='prepare':prepare(a.repo,a.stage)
    elif a.mode=='preflight':preflight(a.repo,a.stage,a.output)
    else:raise SystemExit(execute(a.repo,a.stage,a.output))

if __name__=='__main__':main()
