"""Prepared portable future-reproduction entry; no computation on --help."""
import argparse,datetime,json,os,re,resource,subprocess,sys,time
from pathlib import Path

def put_exclusive(path,data):
    with open(path,'x') as f:json.dump(data,f,indent=2);f.write('\n')

def main():
    ap=argparse.ArgumentParser(description='New independent HE38 oracle execution with hard 30 CPU second / 512 MiB limits. Existing attempts are refused.')
    ap.add_argument('--implementation-root',required=True,type=Path,help='Restored unit/components/finite_mass directory containing h1_finite_mass.')
    ap.add_argument('--output-root',required=True,type=Path,help='Parent for a new exclusive attempt directory and launch receipts.')
    ap.add_argument('--attempt',required=True,help='Unique attempt name; never reuses attempt_001 or overwrites existing evidence.')
    args=ap.parse_args()
    if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}',args.attempt) is None:
        ap.error('--attempt must be one safe nonempty name, at most 96 characters')
    impl=args.implementation_root.expanduser().resolve(strict=True)
    if not (impl/'h1_finite_mass'/'__init__.py').is_file():
        ap.error('--implementation-root must contain h1_finite_mass/__init__.py')
    output=args.output_root.expanduser().resolve()
    output.mkdir(parents=True,exist_ok=True)
    attempt=output/args.attempt
    if attempt.exists():
        raise FileExistsError('REFUSE_EXISTING_ATTEMPT: '+str(attempt))
    begin=output/(args.attempt+'.LAUNCH_START.json')
    final=output/(args.attempt+'.LAUNCH_RESULT.json')
    if final.exists():
        raise FileExistsError('REFUSE_EXISTING_LAUNCH_RESULT: '+str(final))
    # Atomic reservation prevents concurrent launch of the same attempt id.
    put_exclusive(begin,{'status':'FUTURE_ENTRY_ACTUALLY_INVOKED',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'attempt_path':str(attempt),'implementation_root':str(impl),
        'CPU_limit_seconds':30,'address_space_limit_bytes':512*1024**2})
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',
             OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
        resource.setrlimit(resource.RLIMIT_CPU,(30,30))
    command=[sys.executable,str(Path(__file__).with_name('run_oracle.py')),
             '--implementation-root',str(impl),'--output-root',str(output),
             '--attempt',args.attempt]
    wall=time.perf_counter()
    try:
        process=subprocess.run(command,env=env,capture_output=True,text=True,
                               preexec_fn=limits,timeout=90)
        record={'returncode':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
        rc=process.returncode
    except subprocess.TimeoutExpired as exc:
        record={'returncode':None,'status':'TIMEOUT_RETAIN_PARTIAL_ATTEMPT',
                'error':str(exc),'stdout':str(exc.stdout),'stderr':str(exc.stderr)}
        rc=124
    except BaseException as exc:
        put_exclusive(final,{'status':'LAUNCH_FAILED_RETAIN_RESERVATION','error':repr(exc),
                            'wall_s':time.perf_counter()-wall})
        raise
    usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    record.update({'wall_s':time.perf_counter()-wall,'child_CPU_user_s':usage.ru_utime,
       'child_CPU_system_s':usage.ru_stime,'child_maxRSS_KiB':usage.ru_maxrss,
       'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'CPU_limit_seconds':30,'address_space_limit_bytes':512*1024**2,
       'attempt_path':str(attempt),'implementation_root':str(impl)})
    put_exclusive(final,record)
    print(json.dumps(record))
    return rc
if __name__=='__main__':sys.exit(main())
