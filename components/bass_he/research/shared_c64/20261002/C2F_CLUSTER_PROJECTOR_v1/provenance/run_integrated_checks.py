"""Run the affected manufactured suite once and preserve fresh byte identities."""
from pathlib import Path
import argparse
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from runtime_support import atomic_create, file_identity


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--label',required=True)
    a=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_]+',a.label):raise SystemExit('unsafe label')
    output=ROOT/'review'/f'{a.label}.json'
    if output.exists():raise SystemExit('CREATE_ONLY existing evidence')
    env=os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',OMP_NUM_THREADS='1',
               OMP_DYNAMIC='FALSE',OMP_PROC_BIND='FALSE',BASS_LOCAL_UNBOUND='1')
    identities={str(p.relative_to(ROOT)):file_identity(p)for folder in ['code','native','tests']
                for p in sorted((ROOT/folder).rglob('*'))
                if p.is_file() and '__pycache__' not in p.parts
                and 'baseline_v1' not in p.parts and p.suffix in ['.py','.f90','.so']}
    cmd=[sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-v']
    run=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
    log=run.stdout+run.stderr
    count=re.search(r'Ran (\d+) tests?',log)
    unchanged=all(file_identity(v['path'])==v for v in identities.values())
    result={'schema':'bass-he.c2f.integrated-tests.v1','created_utc':datetime.now(timezone.utc).isoformat(),
            'command':cmd,'cwd':str(ROOT),'exit_code':run.returncode,'test_count':int(count[1]) if count else None,
            'status':'PASS' if run.returncode==0 and unchanged and count else 'FAIL',
            'code_unchanged_during_run':unchanged,'input_identities':identities,'log':log,
            'scope':'affected manufactured implementation tests only','old_scientific_suites_rerun':0,
            'new_molecular_eigensolves':0}
    atomic_create(output,result)
    print(log)
    print(output)
    raise SystemExit(0 if result['status']=='PASS' else 1)


if __name__=='__main__':main()
