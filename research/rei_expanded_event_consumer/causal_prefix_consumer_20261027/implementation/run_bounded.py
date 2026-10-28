"""Explicit GO only; one attempt; preserves child stdout/stderr and resource use."""
import hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path

UNIT=Path(__file__).resolve().parents[1]
IMPL=UNIT/'implementation'
go=json.loads((IMPL/'EXECUTION_GO.json').read_text())
if go.get('authorization')!='ROOT_C5_REVIEW_GO':raise SystemExit('missing C5 GO')
manifest=(IMPL/'PREEXEC_MANIFEST.json').read_bytes()
if hashlib.sha256(manifest).hexdigest()!=go['manifest_sha256']:raise SystemExit('manifest mismatch')
for row in json.loads(manifest)['files']:
    if hashlib.sha256((UNIT/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise SystemExit('frozen byte mismatch '+row['path'])
if go['prior_planning_known_CPU_s']+.18>14.99:raise SystemExit('cumulative reserve does not fit')
out=IMPL/'attempt01';out.mkdir(exist_ok=False)
env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def limits():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
    resource.setrlimit(resource.RLIMIT_CPU,(1,1))
start=time.monotonic();rc=None;error=None
(out/'START_RECEIPT.json').write_text(json.dumps({'authorization':go,'one_attempt':True,'reserve_CPU_s':.18,'child_target_CPU_s':.12,'wrapper_target_CPU_s':.04,'tail_CPU_s':.02,'wall_s':5,'RSS_MiB':512,'hard_CPU_s':1},indent=2)+'\n')
try:
    with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
        p=subprocess.Popen([sys.executable,'-B',str(IMPL/'checker.py')],cwd=str(UNIT),env=env,stdout=stdout,stderr=stderr,preexec_fn=limits)
        try:rc=p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill();rc=p.wait();error='WALL_LIMIT'
finally:
    child=resource.getrusage(resource.RUSAGE_CHILDREN);own=resource.getrusage(resource.RUSAGE_SELF)
    cc=child.ru_utime+child.ru_stime;wc=own.ru_utime+own.ru_stime;wall=time.monotonic()-start
    receipt={'exit_code':rc,'error':error,'child_CPU_s':cc,'wrapper_CPU_s_before_receipt_tail':wc,'tail_CPU_s':.02,'charged_new_CPU_s':cc+wc+.02,'wall_s':wall,'max_RSS_KiB':child.ru_maxrss,'targets':{'child':.12,'wrapper':.04,'total':.18},'within_targets':cc<=.12 and wc<=.04 and cc+wc+.02<=.18 and wall<=5,'reruns':0,'unmeasured':'tool/remote/LLM UNKNOWN_NOT_ZERO; .02 receipt tail held'}
    (out/'RESOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
sys.exit(rc if rc is not None else 1)
