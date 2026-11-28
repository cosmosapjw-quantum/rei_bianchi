"""Record one integrated run of only new C2g affected unit tests."""
from pathlib import Path
import subprocess,sys,os,time,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from runtime_support import atomic_create,file_identity,code_identity
out=ROOT/'results/INTEGRATED_TESTS.txt'
if out.exists():raise FileExistsError(out)
before=code_identity(ROOT/'code');start=time.monotonic()
command=[sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_*.py','-v']
env=os.environ.copy();env.update(PYTHONPATH=str(ROOT/'code'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',OMP_DYNAMIC='FALSE',OMP_PROC_BIND='FALSE')
p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
with out.open('x') as f:f.write(p.stdout+p.stderr);f.flush();os.fsync(f.fileno())
unchanged=code_identity(ROOT/'code')==before
atomic_create(ROOT/'results/INTEGRATED_TESTS.json',{'status':'PASS' if p.returncode==0 and unchanged else 'FAIL','returncode':p.returncode,'source_unchanged':unchanged,'source_identity':before,'command':command,'wall_seconds':time.monotonic()-start,'log':file_identity(out),'scope':'only new C2g affected manufactured, mocked and negative unit tests; no physical eigensolves, no unchanged old suite'})
print(p.stdout+p.stderr);sys.exit(0 if p.returncode==0 and unchanged else 1)
