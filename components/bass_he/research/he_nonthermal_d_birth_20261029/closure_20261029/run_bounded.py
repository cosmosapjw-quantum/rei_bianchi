"""Run only this source unit's affected tests, reference, or saved-data plot."""
from pathlib import Path
import os,sys,json,time,resource,subprocess,math,platform,hashlib
ROOT=Path(__file__).resolve().parent
mode=sys.argv[1]
if mode not in ('unit','reference','plot'):raise SystemExit('mode: unit|reference|plot')
p=ROOT/'evidence/RESOURCE_LEDGER.json'
ledger=json.loads(p.read_text()) if p.exists() else {'unit':'HE_NONTHERMAL_SOURCE_CLOSURE_20261029','old_budgets':'NO_TRANSFER','runs':[]}
kind='plot' if mode=='plot' else 'tests'
cap=10 if mode=='plot' else 8
used=sum(r['cpu_s'] for r in ledger['runs'] if r['budget_kind']==kind)
usedwall=sum(r['wall_s'] for r in ledger['runs'] if r['budget_kind']==kind)
if used>=cap or usedwall>=30:raise SystemExit('unit allowance exhausted; preserve result')
argv=[sys.executable,'tests/test_source_closure.py','-v'] if mode=='unit' else [sys.executable,'validate_reference.py'] if mode=='reference' else [sys.executable,'make_plot.py']
def limits():
 resource.setrlimit(resource.RLIMIT_CPU,(math.ceil(cap-used),math.ceil(cap-used)+1))
 resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','MPLBACKEND':'Agg','PYTHONDONTWRITEBYTECODE':'1'}
t=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
try:
 r=subprocess.run(argv,cwd=ROOT,env=env,preexec_fn=limits,timeout=30-usedwall,text=True,capture_output=True)
 exit_code=r.returncode;stdout=r.stdout;stderr=r.stderr
except subprocess.TimeoutExpired as exc:
 exit_code=124;stdout=str(exc.stdout or '');stderr=str(exc.stderr or '')+'\nWALL_LIMIT'
after=resource.getrusage(resource.RUSAGE_CHILDREN)
rec=dict(mode=mode,budget_kind=kind,argv=argv,exit_code=exit_code,cpu_s=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,wall_s=time.monotonic()-t,peak_child_rss_KiB=after.ru_maxrss,python=sys.version,platform=platform.platform(),old_science_replays=0,new_physical_IVPs=0)
attempt=1+sum(r['mode']==mode for r in ledger['runs'])
rec['stdout']=f'{mode}_{attempt:02d}_stdout.txt';rec['stderr']=f'{mode}_{attempt:02d}_stderr.txt'
(ROOT/'evidence'/rec['stdout']).write_text(stdout);(ROOT/'evidence'/rec['stderr']).write_text(stderr)
rec['input_code_sha256']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'src').glob('*.py'))}
ledger['runs'].append(rec);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(ledger,indent=2)+'\n');os.replace(tmp,p)
print(json.dumps(rec));print(stdout);print(stderr,file=sys.stderr)
raise SystemExit(exit_code)
