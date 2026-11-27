"""Run only the new bounded PHYS02 checks into a new directory."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    out=args.output.resolve()
    if out.exists():
        raise FileExistsError('output must be a new directory')
    if out==root or root in out.parents:
        raise ValueError('output must be outside the sealed package')
    out.mkdir(parents=True)
    stage=out/'package'
    shutil.copytree(root,stage,ignore=shutil.ignore_patterns('__pycache__','.venv'))
    commands=[
        ('unit',[sys.executable,'-B','-m','unittest','discover','-s','tests','-v']),
        ('remainder',[sys.executable,'-B','bound_remainder.py','--output',str(out/'REMAINDER.json')]),
        ('quartic',[sys.executable,'-B','independent/check_k4.py']),
        ('source',[sys.executable,'-B','independent/check_source_portable.py','--output',str(out/'SOURCE_AUDIT.json')]),
    ]
    rows=[]
    for name,cmd in commands:
        proc=subprocess.run(cmd,cwd=stage,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        (out/(name+'.stdout')).write_text(proc.stdout)
        (out/(name+'.stderr')).write_text(proc.stderr)
        rows.append({'name':name,'command':cmd,'exit_code':proc.returncode})
        (out/'RUN_LEDGER.json').write_text(json.dumps(rows,indent=2)+'\n')
        if proc.returncode:
            raise SystemExit(proc.returncode)
    print(json.dumps({'status':'FOUR_NEW_BOUNDED_COMMANDS_EXIT0','results':str(out),
                      'native_dispatch':0,'BE_roots':0,'IVP_trajectories':0,'NCP_dispatch':0}))


if __name__=='__main__':
    main()
