"""Create-only local synthetic MPI launcher. No remote hosts or scientific mode."""
import argparse,json,os,re,resource,signal,subprocess,sys,time
from pathlib import Path
from planner import GiB,detect,identity,mpi_tools,plan
from rank_guard import THREAD_ENV

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent


def manifest_check(path,p,resume=False):
    path=Path(path)
    if path.stat().st_size>16*1024**2:raise ValueError('manifest too large')
    m=json.loads(path.read_text())
    if m.get('schema')!='WU088_NCP64_TASK_MANIFEST_V1' or m.get('scope')!='SYNTHETIC_ONLY':raise ValueError('only synthetic manifest authorized')
    tasks=m.get('tasks')
    if not isinstance(tasks,list) or not 1<=len(tasks)<=4096:raise ValueError('executor requires 1..4096 tasks')
    out=Path(m['output_root'])
    if not out.is_absolute() or (out.exists() and not resume):raise ValueError('manifest output_root must be new; explicit --resume permits identity-checked reuse')
    for task in tasks:
        lim=task['limits']
        if not 0<lim['address_space_bytes']<=p['worker_bytes'] or not 0<lim['rss_bytes']<=p['worker_bytes']:
            raise ValueError('task memory exceeds worker reservation')
        if not 0<lim['wall_seconds']<=86400 or not 0<lim['max_output_bytes']<=64*1024**2:
            raise ValueError('task wall/output bound')
    return m


def worklist_check(path,m):
    lines=Path(path).read_text().splitlines()
    if len(lines)!=len(m['tasks'])+1 or int(lines[0])!=len(m['tasks']):raise ValueError('worklist count mismatch')
    expected=m.get('dispatch_order')
    if expected is None:expected=sorted(range(len(m['tasks'])),key=lambda i:(-m['tasks'][i].get('cost_hint',0),m['tasks'][i]['task_id']))
    rows=[tuple(map(int,x.split())) for x in lines[1:]]
    if sorted(expected)!=list(range(len(m['tasks']))) or any(len(r)!=2 for r in rows):raise ValueError('worklist permutation/row shape')
    if [r[0] for r in rows]!=expected or any(r[1]!=m['tasks'][r[0]]['limits']['wall_seconds']+10 for r in rows):
        raise ValueError('worklist indices/timeouts differ from manifest')


def mpi_argv(p,tools,binary,manifest,worklist,python,runroot):
    return [tools['mpirun']['command_path'],'-np',str(p['rank_count']),'--host','localhost:'+str(p['rank_count']),
            '--map-by','slot','--bind-to','none','--nooversubscribe','--report-bindings',
            str(python),str(HERE/'rank_guard.py'),'--plan',str(runroot/'HOST_PLAN.json'),'--',
            str(binary),str(python),str(ROOT/'executor/worker.py'),str(manifest),str(worklist)]


def refresh_plan(old,fresh):
    if fresh['status']!='PLAN_READY' or fresh['rank_count']!=old['rank_count'] or fresh['rank_os_cpus']!=old['rank_os_cpus']:
        raise ValueError('host resources changed; replan')
    return {**old,'host':fresh['host'],'observed_available_memory_bytes':fresh['observed_available_memory_bytes'],
            'job_memory_budget_bytes':min(old['job_memory_budget_bytes'],fresh['job_memory_budget_bytes']),
            'quota_cpu_equivalent':fresh['quota_cpu_equivalent'],'cpu_budget':fresh['cpu_budget']}


def process_table():
    # /proc may be mounted in an ancestor PID namespace. Convert both child
    # and parent IDs before comparing to Popen.pid or sending a signal.
    namespace=os.readlink('/proc/self/ns/pid');rows={};host_to_local={};scanned=0
    for d in Path('/proc').iterdir():
        if not d.name.isdigit():continue
        scanned+=1
        if scanned>65536:raise RuntimeError('PROCESS_SCAN_LIMIT')
        try:
            if os.readlink(d/'ns/pid')!=namespace:continue
            status={k:v.strip() for k,v in (line.split(':',1) for line in (d/'status').read_text().splitlines() if ':'in line)}
            local_pid=int(status['NSpid'].split()[-1]);host_pid=int(status['Pid']);parent_host=int(status['PPid'])
            s=(d/'stat').read_text();fields=s[s.rfind(')')+2:].split()
            if local_pid in rows:raise RuntimeError('AMBIGUOUS_PID_NAMESPACE_MAPPING')
            host_to_local[host_pid]=local_pid
            rows[local_pid]={'parent_host':parent_host,'host_pid':host_pid,'start':fields[19],
                             'rss':int(status.get('VmRSS','0 kB').split()[0])*1024,
                             'state':status['State'].split()[0]}
        except (FileNotFoundError,ProcessLookupError,PermissionError):continue
        except (ValueError,KeyError,IndexError) as exc:raise RuntimeError('UNSUPPORTED_PROC_PID_METADATA') from exc
    if os.getpid() not in rows:raise RuntimeError('SELF_PID_NAMESPACE_MAPPING_MISSING')
    table={pid:{**row,'ppid':host_to_local.get(row['parent_host'],0)} for pid,row in rows.items()}
    return table


def descendants(table,pid):
    seen={pid}
    while True:
        more={p for p,v in table.items() if v['ppid'] in seen}
        new=seen|more
        if new==seen:return {p:table[p] for p in seen if p in table}
        seen=new


def cleanup(proc,tracked):
    for sig in (signal.SIGTERM,signal.SIGKILL):
        try:os.killpg(proc.pid,sig)
        except ProcessLookupError:pass
        try:current=process_table();tracked.update(descendants(current,proc.pid))
        except (OSError,RuntimeError):current={}
        for pid,item in tracked.items():
            if pid in current and current[pid]['start']==item['start']:
                try:os.kill(pid,sig)
                except ProcessLookupError:pass
        if sig==signal.SIGTERM:
            try:proc.wait(timeout=2)
            except subprocess.TimeoutExpired:pass
    proc.wait()


def json_stage(script,manifest,root,label,seconds,cap,env):
    if seconds<=0:return {'status':'INCONCLUSIVE','reason':'JOB_WALL_LIMIT'}
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
        resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,64*1024**2))
    with (root/(label+'.stdout')).open('xb') as out,(root/(label+'.stderr')).open('xb') as err:
        proc=subprocess.Popen([sys.executable,str(script),'--manifest',str(manifest)],env=env,cwd=root,
                              stdout=out,stderr=err,stdin=subprocess.DEVNULL,start_new_session=True,preexec_fn=limits)
        try:proc.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            cleanup(proc,descendants(process_table(),proc.pid));return {'status':'INCONCLUSIVE','reason':'JOB_WALL_LIMIT'}
    path=root/(label+'.stdout')
    if path.stat().st_size>64*1024**2:return {'status':'INCONCLUSIVE','reason':'METADATA_OUTPUT_LIMIT'}
    try:
        result=json.loads(path.read_text())
        if not isinstance(result,dict):raise ValueError('object required')
        if proc.returncode:result.update(status='INCONCLUSIVE',process_returncode=proc.returncode)
        return result
    except (ValueError,OSError):return {'status':'INCONCLUSIVE','reason':'INVALID_'+label.upper()+'_JSON'}


def execute(p,argv,wall_seconds):
    root=Path(p['run_root']);root.mkdir();(root/'bindings').mkdir()
    with (root/'HOST_PLAN.json').open('x') as f:json.dump(p,f,indent=2)
    env={'PATH':os.pathsep.join(dict.fromkeys([str(Path(x).parent) for x in (argv[0],sys.executable)]+['/usr/local/bin','/usr/bin','/bin'])),
         'LC_ALL':'C','LANG':'C','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1',**THREAD_ENV}
    # MPI root bypasses, scheduler allocation variables and LD_PRELOAD are not inherited.
    pld=p.get('backend_library_path')
    if pld:env['LD_LIBRARY_PATH']=pld
    tracked={};peak=0;start=time.monotonic();reason='COMPLETED';proc=None
    prepared=json_stage(ROOT/'executor/prepare.py',p['manifest'],root,'prepare',wall_seconds,p['coordinator_bytes'],env)
    if prepared.get('status')!='READY':
        result={'status':'EXECUTION_BLOCKED','prepare':prepared,'actual_HH_runs':0,'scientific_admission':False}
        with (root/'HOST_RUN.json').open('x') as f:json.dump(result,f,indent=2)
        return result
    with (root/'stdout.log').open('xb') as stdout,(root/'stderr.log').open('xb') as stderr:
        try:
            proc=subprocess.Popen(argv,env=env,cwd=root,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,
                                  start_new_session=True,shell=False)
            while proc.poll() is None:
                tree=descendants(process_table(),proc.pid);tracked.update(tree)
                rss=sum(v['rss'] for v in tree.values());peak=max(peak,rss)
                if rss>p['job_memory_budget_bytes']:reason='AGGREGATE_RSS_LIMIT';break
                if time.monotonic()-start>=wall_seconds:reason='JOB_WALL_LIMIT';break
                if max(os.fstat(stdout.fileno()).st_size,os.fstat(stderr.fileno()).st_size)>p['file_size_cap_bytes']:
                    reason='LAUNCHER_LOG_LIMIT';break
                time.sleep(.1)
            if proc.poll() is None:cleanup(proc,tracked)
            else:
                current=process_table()
                living={pid:x for pid,x in tracked.items() if pid in current and x['start']==current[pid]['start'] and pid!=proc.pid and current[pid]['state'] not in ('Z','X')}
                if living:reason='SURVIVING_DESCENDANTS';cleanup(proc,living)
            if reason=='COMPLETED' and proc.returncode:reason='MPI_NONZERO_EXIT'
            if reason=='COMPLETED' and max(os.fstat(stdout.fileno()).st_size,os.fstat(stderr.fileno()).st_size)>p['file_size_cap_bytes']:
                reason='LAUNCHER_LOG_LIMIT'
        finally:
            if proc is not None and proc.poll() is None:cleanup(proc,tracked)
    result={'status':reason,'returncode':proc.returncode,'peak_process_tree_rss_sampled_bytes':peak,
            'wall_seconds':time.monotonic()-start,'wall_cap_seconds':wall_seconds,
            'aggregate_memory_hard_cap':False,'actual_HH_runs':0,'scientific_admission':False,'performance_claim':None}
    if reason=='COMPLETED':
        bindings=[json.loads(x.read_text()) for x in sorted((root/'bindings').glob('rank_*.json'))]
        if len(bindings)!=p['rank_count'] or sorted(x['rank'] for x in bindings)!=list(range(p['rank_count'])) or any(x['after']!=[p['rank_os_cpus'][x['rank']]] for x in bindings):
            result['status']='BINDING_RECEIPTS_INCOMPLETE'
        else:
            result['status']='MPI_STAGE_COMPLETED'
            collected=json_stage(ROOT/'executor/collect.py',p['manifest'],root,'collector',
                                 wall_seconds-(time.monotonic()-start),p['coordinator_bytes'],env)
            result['collector']=collected
            if (collected.get('status')=='COLLECTED' and collected.get('declared_task_count')==p['expected_task_count']
                    and collected.get('complete_task_count')==p['expected_task_count']
                    and re.fullmatch('[0-9a-f]{64}',str(collected.get('canonical_payload_digest','')))):
                result['status']='EXECUTION_COMPLETE'
            else:result['status']='COLLECTOR_INCONCLUSIVE'
    result['wall_seconds']=time.monotonic()-start
    with (root/'HOST_RUN.json').open('x') as f:json.dump(result,f,indent=2)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('manifest','mpi-binary','worklist','output'):ap.add_argument('--'+name,required=True,type=Path)
    ap.add_argument('--execute-synthetic',action='store_true');ap.add_argument('--smt',action='store_true')
    ap.add_argument('--resume',action='store_true',help='permit existing task output only after executor identity and completeness checks')
    ap.add_argument('--ranks',type=int);ap.add_argument('--reserve-gib',type=int,default=16)
    ap.add_argument('--worker-mib',type=int,default=1024);ap.add_argument('--wall-seconds',type=int,default=900)
    ap.add_argument('--backend-library-path',type=Path)
    a=ap.parse_args();blocked=[]
    try:
        p=plan(detect(),smt=a.smt,reserve_bytes=a.reserve_gib*GiB,worker_bytes=a.worker_mib*1024**2,requested_ranks=a.ranks)
        blocked.extend(p['blocked_reasons']);mpi=mpi_tools();blocked.extend(mpi['blocked_reasons'])
        if not a.output.is_absolute() or a.output.exists() or not a.output.parent.is_dir():raise ValueError('new absolute output under existing parent required')
        if not 1<=a.wall_seconds<=86400:raise ValueError('bounded job wall required')
        m=manifest_check(a.manifest,p,a.resume);worklist_check(a.worklist,m)
        paths=[a.mpi_binary,a.manifest,a.worklist,ROOT/'executor/worker.py',ROOT/'executor/prepare.py',ROOT/'executor/collect.py',ROOT/'executor/core.py',ROOT/'executor/guard.py',HERE/'rank_guard.py',HERE/'planner.py',HERE/'launcher.py']
        identities=[]
        for path in paths:
            if not path.is_absolute():raise ValueError('all artifact paths must be absolute')
            try:identities.append(identity(path))
            except OSError:blocked.append('MISSING_ARTIFACT:'+str(path))
        if not os.access(a.mpi_binary,os.X_OK):blocked.append('MPI_BINARY_NOT_EXECUTABLE')
        p.update(run_root=str(a.output),file_size_cap_bytes=64*1024**2,mpi=mpi,artifact_identities=identities,
                 manifest=str(a.manifest),expected_task_count=len(m['tasks']),resume_requested=a.resume)
        if a.backend_library_path:
            if not a.backend_library_path.is_absolute() or not a.backend_library_path.is_dir():raise ValueError('absolute backend library directory required')
            p['backend_library_path']=str(a.backend_library_path.resolve())
        p['blocked_reasons']=blocked;p['status']='BLOCKED' if blocked else 'PLAN_READY'
        p['argv']=mpi_argv(p,mpi['tools'],a.mpi_binary,a.manifest,a.worklist,Path(sys.executable).resolve(),a.output) if not blocked else None
        if a.execute_synthetic and not blocked:
            # Reobserve capacity and input bytes immediately before process creation.
            fresh=plan(detect(),smt=a.smt,reserve_bytes=a.reserve_gib*GiB,worker_bytes=a.worker_mib*1024**2,requested_ranks=p['rank_count'])
            p=refresh_plan(p,fresh)
            for item in identities:
                if identity(item['path'])!=item:raise ValueError('input artifact changed; replan')
            process_table()  # Fail before spawning if PID-namespace mapping is unavailable.
            result=execute(p,p['argv'],a.wall_seconds)
        else:result=p
        print(json.dumps(result,indent=2));return 2 if blocked or result.get('status') not in ('PLAN_READY','EXECUTION_COMPLETE') else 0
    except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:
        print(json.dumps({'status':'BLOCKED','blocked_reasons':blocked+[str(exc)],'actual_HH_runs':0}));return 2


if __name__=='__main__':raise SystemExit(main())
