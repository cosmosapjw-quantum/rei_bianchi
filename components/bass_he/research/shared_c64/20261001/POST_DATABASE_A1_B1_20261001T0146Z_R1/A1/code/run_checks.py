"""Run only A1 algebra fixtures and preserve the exact subprocess result."""
from pathlib import Path
import datetime,hashlib,json,os,platform,subprocess,sys,tempfile,time
import numpy,scipy

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'evidence'
OUT.mkdir(exist_ok=True)
def create_atomic(path,data):
    raw=data.encode()
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        temp=Path(f.name);f.write(raw);f.flush();os.fsync(f.fileno())
    try:
        os.link(temp,path)
    finally:
        temp.unlink()
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)

started=time.perf_counter()
command=[sys.executable,str(HERE/'test_connection_algebra.py')]
completed=subprocess.run(command,capture_output=True,text=True,timeout=30)
duration=time.perf_counter()-started
log=completed.stdout+completed.stderr
create_atomic(OUT/'ALGEBRA_TEST_LOG.txt',log)
result={'schema':'bass_he.a1.algebra_verification.v1','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'command':command,'exit_code':completed.returncode,'elapsed_seconds':duration,'python':sys.version,
 'numpy':numpy.__version__,'scipy':scipy.__version__,'platform':platform.platform(),
 'scope':'12 bounded finite-matrix algebra fixtures; no physical electronic eigenproblem, collision solve, or cross-section integration',
 'declared_test_tolerance':2e-12,'matrix_validation_tolerance':1e-12,'metric_condition_limit':1e8,
 'status':'PASS' if completed.returncode==0 else 'FAIL','tests_expected':12,
 'log_sha256':hashlib.sha256(log.encode()).hexdigest(),
 'source_identities':[{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(HERE.glob('*.py'))],
 'reference':'Exact constant-H matrix representation and analytic frame identities',
 'tested_formulation':'Metric/orthonormalized generators; no empirical fitting',
 'performance_claim':'NOT_MADE; wall time describes this algebra fixture suite only'}
create_atomic(OUT/'ALGEBRA_TEST_RESULT.json',json.dumps(result,indent=2)+'\n')
print(json.dumps(result));print(log)
sys.exit(completed.returncode)
