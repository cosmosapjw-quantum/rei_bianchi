"""Reproduce only PHYS03 source identity and new bounded algebra checks.

Existing evidence is immutable. A new output directory is required. There is
no native/IVP/nonlinear-BE/NCP execution path in this runner.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent


def verify_manifest():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text())
    for row in manifest['files']:
        path=ROOT/row['path']
        data=path.read_bytes()
        if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:
            raise ValueError('manifest mismatch: '+row['path'])
    return len(manifest['files'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--verify-only',action='store_true')
    args=parser.parse_args()
    checked=verify_manifest()
    if args.verify_only:
        print(json.dumps({'manifest_files_verified':checked,'science_runs':0}))
        return
    if args.output is None:
        parser.error('--output with a new directory is required')
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    smooth=out/'smooth'
    smooth.mkdir()
    for name in ('check_nonautonomous.py','SOURCE_PROFILE_INPUT.json'):
        shutil.copy2(ROOT/'smooth_theory'/name,smooth/name)
    jobs=[
        ('source_identity',[sys.executable,'-B',str(ROOT/'inputs/source_survey/verify_source_intake.py'),
                            '--output',str(out/'SOURCE_IDENTITY_NEW.json')]),
        ('nonautonomous',[sys.executable,'-B',str(smooth/'check_nonautonomous.py')]),
        ('hybrid',[sys.executable,'-B','-m','unittest','discover','-s',str(ROOT/'tests'),'-v']),
        ('chronology',[sys.executable,'-B',str(ROOT/'src/analyze_chronology.py'),
                       '--output',str(out/'CHRONOLOGY_NEW.json')])]
    ledger={'manifest_files_verified':checked,'runs':[],
            'native_dispatches':0,'IVP_trajectories':0,'nonlinear_BE_roots':0,
            'NCP_dispatches':0,'legacy_or_parent_science_runs':0}
    for name,command in jobs:
        with (out/(name+'.stdout')).open('xb') as stdout, (out/(name+'.stderr')).open('xb') as stderr:
            result=subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr,check=False)
        ledger['runs'].append({'name':name,'command':command,'exit_code':result.returncode})
        (out/'REPRODUCTION_STATUS.json').write_text(json.dumps(ledger,indent=2)+'\n')
        if result.returncode:
            raise SystemExit(result.returncode)
    print(json.dumps({'status':'PASS_PHYS03_BOUNDED_REPRODUCTION','output':str(out),
                      'runs':len(jobs)}))


if __name__=='__main__':
    main()
