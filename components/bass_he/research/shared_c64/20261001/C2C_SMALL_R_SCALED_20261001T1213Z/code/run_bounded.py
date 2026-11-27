"""Run one batch via the launcher's inseparable preflight+execute path."""
import argparse,datetime,json,os,signal,subprocess,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes,code_identity,read_manifest
from process_guard import (BATCH_TOKEN_ENV,TASK_TOKEN_ENV,registry_record,
                           cleanup_record,cleanup_batch)

def events():
    try:return {k:int(v) for k,v in (line.split() for line in Path('/sys/fs/cgroup/memory.events').read_text().splitlines())}
    except (OSError,ValueError):return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True);ap.add_argument('--output-dir',required=True);ap.add_argument('--mpirun',required=True);ap.add_argument('--ranks',type=int,required=True);ap.add_argument('--wall-cap',type=int,required=True);ap.add_argument('--local-unbound',action='store_true');args=ap.parse_args()
    if args.wall_cap<=0 or args.wall_cap>1800:raise ValueError('invalid batch wall cap')
    out=(ROOT/args.output_dir).resolve()
    if not out.is_relative_to(ROOT.resolve()):raise ValueError('output outside package')
    log=out.with_name(out.name+'_LOG.txt');receipt=out.with_name(out.name+'_LAUNCH.json');preflight=out.with_name(out.name+'_PREFLIGHT.json')
    if any(x.exists() or x.is_symlink() for x in (out,log,receipt,preflight)):raise FileExistsError('create-only batch')
    manifest,manifest_sha,_=read_manifest((ROOT/args.manifest).resolve())
    task_ids=[task['task_id'] for task in manifest['tasks']]
    batch_token=uuid.uuid4().hex;launcher_token=uuid.uuid4().hex
    environment=os.environ.copy();environment[BATCH_TOKEN_ENV]=batch_token;environment[TASK_TOKEN_ENV]=launcher_token
    command=[sys.executable,str(ROOT/'code/launch_ncp.py'),'--manifest',args.manifest,'--output-dir',args.output_dir,
        '--backend','native','--ranks',str(args.ranks),'--threads','1','--mpirun',args.mpirun,
        '--memory-accounting','clean-file-half-v1','--bind-to','none' if args.local_unbound else 'core','--execute']
    start=time.perf_counter();before=events();identity=code_identity();timed_out=False;started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    cleanup_reports=[];launcher_record=None
    with log.open('xb') as stream:
        process=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,env=environment)
        try:
            launcher_record=registry_record(process.pid,'__launcher__',launcher_token,batch_token)
            code=process.wait(timeout=args.wall_cap)
        except subprocess.TimeoutExpired:
            timed_out=True
            # Rank handlers run their active-task finally blocks on SIGTERM.
            # The owned task registry also covers independent sessions.
            cleanup_reports.append({'stage':'launcher_term','report':cleanup_record(launcher_record,batch_token,'__launcher__',timeout=0.25,signum=signal.SIGTERM)})
            cleanup_reports.append({'stage':'tasks_after_term','reports':cleanup_batch(out,batch_token,task_ids)})
            try:process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                cleanup_reports.append({'stage':'launcher_kill','report':cleanup_record(launcher_record,batch_token,'__launcher__')})
                process.wait(timeout=3)
            code=124
        finally:
            # Also cover interruption and registry/spawn exceptions. Never
            # operate on another batch or on a reused numeric PID.
            if launcher_record is not None:
                cleanup_reports.append({'stage':'launcher_final','report':cleanup_record(launcher_record,batch_token,'__launcher__')})
            cleanup_reports.append({'stage':'tasks_final','reports':cleanup_batch(out,batch_token,task_ids)})
        stream.flush();os.fsync(stream.fileno())
    text=log.read_text();pf=None
    try:
        pf,_=json.JSONDecoder().raw_decode(text[text.index('{'):])
        if not isinstance(pf,dict) or pf.get('action')!='EXECUTE':raise ValueError('not preflight')
        atomic_create(preflight,json_bytes(pf))
    except (ValueError,json.JSONDecodeError):pf=None
    after=events();record={'command_argv':command,'started_utc':started,'returncode':code,'timed_out':timed_out,
        'elapsed_seconds':time.perf_counter()-start,'wall_cap_seconds':args.wall_cap,
        'preflight_passed':pf is not None,'memory_accounting':'clean-file-half-v1','binding':'none' if args.local_unbound else 'core',
        'memory_events_before':before,'memory_events_after':after,
        'memory_events_delta':{k:after[k]-before[k] for k in before.keys()&after.keys()} if before is not None and after is not None else None,
        'source_identity_before':identity,'source_unchanged':code_identity()==identity}
    record['manifest_sha256']=manifest_sha
    record['batch_owner_token']=batch_token
    record['owned_process_cleanup']=cleanup_reports
    record['cleanup_complete']=all(report.get('status')=='NO_LIVE_OWNED_MEMBERS'
        for stage in cleanup_reports if stage['stage'] in ('launcher_final','tasks_final')
        for report in ([stage['report']] if 'report' in stage else stage.get('reports',[])))
    if not record['cleanup_complete']:
        record['returncode']=code=125
    atomic_create(receipt,json_bytes(record))
    print(json.dumps({k:record[k] for k in ('returncode','preflight_passed','elapsed_seconds','memory_events_delta','source_unchanged')}))
    return code

if __name__=='__main__':raise SystemExit(main())
