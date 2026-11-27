from pathlib import Path
import ast,datetime,hashlib,json,os,subprocess,sys
root=Path('/tmp/he38_raw_controls')
portable=root/'portable';portable.mkdir(exist_ok=False)
original_names=['raw_oracle.py','run_oracle.py','launch.py','CONTRACT.json','LAUNCH_RECEIPT.json']
original_names += [str(p.relative_to(root)) for p in sorted((root/'attempts').rglob('*')) if p.is_file()]
def sha(b):return hashlib.sha256(b).hexdigest()
original_hashes={n:sha((root/n).read_bytes()) for n in original_names}
old_manifest=(root/'FILE_MANIFEST.json').read_bytes()
history=root/'history';history.mkdir(exist_ok=True)
with open(history/'FILE_MANIFEST_BEFORE_PORTABILITY.json','xb') as f:f.write(old_manifest)
src=(root/'run_oracle.py').read_text()
preamble="""ROOT=Path(__file__).resolve().parents[1]
EXPECTED_RAW_ORACLE_SHA256='06005fbc72c88e36cf228f4003331a6a7c713514bff8c8e44d533ccfc25c747d'
EXPECTED_CONTRACT_SHA256='3f68eaf3eab717790949c006e2131b0f1b788ce67744026aa4d7f1232726745d'
for _name,_expected in [('raw_oracle.py',EXPECTED_RAW_ORACLE_SHA256),('CONTRACT.json',EXPECTED_CONTRACT_SHA256)]:
    if hashlib.sha256((ROOT/_name).read_bytes()).hexdigest()!=_expected:
        raise RuntimeError('ORIGINAL_RAW_OR_CONTRACT_IDENTITY_MISMATCH: '+_name)
sys.path.insert(0,str(ROOT))
from raw_oracle import evaluate, DIRECTIONS, KB
"""
old="from raw_oracle import evaluate, DIRECTIONS, KB\n\nROOT=Path(__file__).resolve().parent\n"
assert src.count(old)==1
src=src.replace(old,preamble)
old="    ap=argparse.ArgumentParser();ap.add_argument('attempt');args=ap.parse_args()\n    out=ROOT/'attempts'/args.attempt\n"
new="""    ap=argparse.ArgumentParser(description='Portable HE38 raw quadrature runner; invoke through portable/launch.py for hard resource limits.')
    ap.add_argument('--implementation-root',required=True,type=Path,help='Directory containing the restored h1_finite_mass package.')
    ap.add_argument('--output-root',required=True,type=Path,help='Fresh-run parent directory; existing attempt directories are never overwritten.')
    ap.add_argument('--attempt',required=True,help='Unique single-component attempt name.')
    args=ap.parse_args()
    import re
    if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}',args.attempt) is None:
        ap.error('--attempt must be one safe nonempty name, at most 96 characters')
    implementation_root=args.implementation_root.expanduser().resolve(strict=True)
    if not (implementation_root/'h1_finite_mass'/'__init__.py').is_file():
        ap.error('--implementation-root must contain h1_finite_mass/__init__.py')
    out=args.output_root.expanduser().resolve()/args.attempt
"""
assert src.count(old)==1;src=src.replace(old,new)
old="sources={str(p):sha(p) for p in [ROOT/'raw_oracle.py',ROOT/'run_oracle.py',ROOT/'CONTRACT.json']}"
new="sources={str(p):sha(p) for p in [ROOT/'raw_oracle.py',Path(__file__).resolve(),ROOT/'CONTRACT.json']}"
assert src.count(old)==1;src=src.replace(old,new)
old="prodroot=Path('/tmp/he38_implementation/h1_finite_mass')"
new="prodroot=implementation_root/'h1_finite_mass'"
assert src.count(old)==1;src=src.replace(old,new)
old="sys.path.insert(0,'/tmp/he38_implementation')"
new="sys.path.insert(0,str(implementation_root))"
assert src.count(old)==1;src=src.replace(old,new)
with open(portable/'run_oracle.py','x') as f:f.write(src)
launcher="""\"\"\"Prepared portable future-reproduction entry; no computation on --help.\"\"\"
import argparse,datetime,json,os,re,resource,subprocess,sys,time
from pathlib import Path

def put_exclusive(path,data):
    with open(path,'x') as f:json.dump(data,f,indent=2);f.write('\\n')

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
"""
with open(portable/'launch.py','x') as f:f.write(launcher)
# Static comparison of every scientific loop and the complete raw oracle bytes.
old_ast=ast.parse((root/'run_oracle.py').read_text());new_ast=ast.parse(src)
def loops(tree):
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    items=[]
    for n in ast.walk(fn):
        if isinstance(n,ast.For):items.append(ast.dump(n,include_attributes=False))
    return items
oldloops=loops(old_ast);newloops=loops(new_ast)
assert oldloops==newloops
assert len(oldloops)==3
for p in portable.glob('*.py'):compile(p.read_text(),str(p),'exec')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
helps=[]
for p in [portable/'launch.py',portable/'run_oracle.py']:
    q=subprocess.run([sys.executable,str(p),'--help'],capture_output=True,text=True,env=env,timeout=20)
    assert q.returncode==0,q.stderr
    helps.append({'path':str(p.relative_to(root)),'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr})
assert all(sha((root/n).read_bytes())==h for n,h in original_hashes.items())
evidence={'status':'PASS_STATIC_ONLY','scientific_executions':0,'loop_AST_equal':True,
          'number_of_matching_scientific_loops':len(oldloops),
          'scientific_loop_AST_sha256':[sha(t.encode()) for t in oldloops],
          'raw_oracle_byte_identity_unchanged':True,'originals_and_receipts_unchanged':True,
          'static_compile_files':[str(p.relative_to(root)) for p in portable.glob('*.py')],
          'help_checks':helps,
          'numerical_path_changes':'implementation_root argument only; raw quadrature/comparison/refinement bodies identical',
          'overwrite_policy':'launcher atomic exclusive reservation; runner mkdir exist_ok=False; every receipt open x'}
with open(root/'PORTABILITY_STATIC_VALIDATION.json','x') as f:json.dump(evidence,f,indent=2);f.write('\n')
revision={'schema':'HE38_RAW_ORACLE_PORTABILITY_REVISION_V1',
          'status':'PREPARED_NOT_SCIENCE_EXECUTED',
          'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'reason':'Independent review F2: original runner had absolute implementation path and launcher fixed attempt_001',
          'original_file_hashes_unchanged':original_hashes,
          'original_manifest_sha256':sha(old_manifest),
          'original_manifest_preserved_as':'history/FILE_MANIFEST_BEFORE_PORTABILITY.json',
          'new_files':{str(p.relative_to(root)):sha(p.read_bytes()) for p in portable.glob('*.py')},
          'resource_policy':'Use portable/launch.py: CPU30s and address-space512MiB hard limits, one-thread env, wall timeout90s',
          'execution_policy':'Explicit future new invocation only; no automatic rerun during restoration; existing attempts refused',
          'prepared_entry_scientific_execution_count':0,
          'static_evidence':'PORTABILITY_STATIC_VALIDATION.json'}
with open(root/'PORTABILITY_REVISION.json','x') as f:json.dump(revision,f,indent=2);f.write('\n')
print(json.dumps({'status':revision['status'],'static':evidence['status'],'loops_equal':len(oldloops),
                  'originals_unchanged':len(original_hashes),'new_files':revision['new_files']}))

