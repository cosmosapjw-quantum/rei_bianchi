"""Bound and preserve focused scientific postprocessing receipts (120s aggregate)."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
TASK=HERE.parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--data32',type=Path,required=True);p.add_argument('--data64',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--receipts',type=Path,required=True);p.add_argument('--postprocess-only',action='store_true')
    a=p.parse_args()
    if a.out.exists() and any(a.out.iterdir()):raise ValueError('NONEMPTY_OUTPUT_ATTEMPT_REFUSED')
    a.receipts.mkdir(parents=True,exist_ok=True)
    ledger=a.receipts/'RECEIPTS.json'
    old=json.loads(ledger.read_text()) if ledger.exists() else []
    total=sum(r['wall_seconds'] for r in old)
    commands=[('focused_tests',[sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_analysis.py','-v']),('integration_tests',[sys.executable,'-m','unittest','discover','-s',str(TASK/'tests'),'-p','test_photon_ledger_diagnosis.py','-v']),('postprocess',[sys.executable,str(HERE/'analysis.py'),'--data32',str(a.data32.resolve()),'--data64',str(a.data64.resolve()),'--out',str(a.out.resolve())])]
    if a.postprocess_only: commands=commands[-1:]
    env=dict(os.environ);env['PYTHONPATH']=str(HERE)+os.pathsep+str(TASK/'src');env['REI_V9_DATA32']=str(a.data32.resolve());env['REI_V9_DATA64']=str(a.data64.resolve())
    for label,cmd in commands:
        if total>=120:raise RuntimeError('SCIENTIFIC_WALL_CAP_EXHAUSTED')
        number=len(old)+1;prefix=a.receipts/f'{number:02d}_{label}'
        start=time.monotonic()
        try:
            result=subprocess.run(cmd,cwd='/tmp',env=env,capture_output=True,text=True,timeout=120-total)
            code,stdout,stderr=result.returncode,result.stdout,result.stderr
        except subprocess.TimeoutExpired as e:
            code,stdout,stderr=124,e.stdout or '',e.stderr or ''
            if isinstance(stdout,bytes):stdout=stdout.decode(errors='replace')
            if isinstance(stderr,bytes):stderr=stderr.decode(errors='replace')
        wall=time.monotonic()-start;total+=wall
        prefix.with_suffix('.stdout.log').write_text(stdout);prefix.with_suffix('.stderr.log').write_text(stderr)
        r=dict(label=label,command=cmd,cwd='/tmp',exit_code=code,wall_seconds=wall,aggregate_scientific_wall_seconds=total,stdout=str(prefix.with_suffix('.stdout.log')),stderr=str(prefix.with_suffix('.stderr.log')))
        old.append(r);ledger.write_text(json.dumps(old,indent=2)+'\n');print(json.dumps(r),flush=True)
        if code:sys.exit(code)
if __name__=='__main__':main()
