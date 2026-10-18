#!/usr/bin/env python3
"""Reconstruct additive V14 files from the exact V13 parent. No solver design."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path);p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    spec=json.loads((ROOT/'SOURCE_DELTA.json').read_text())
    if a.out.exists():raise SystemExit('Refusing to overwrite output: '+str(a.out))
    if a.base:
        for rel,h in spec['parent_hashes'].items():
            if sha(a.base/rel)!=h:raise SystemExit('V13 parent mismatch: '+rel)
        shutil.copytree(a.base,a.out,ignore=shutil.ignore_patterns('target','.git','__pycache__'))
    else:
        v13=ROOT.parent/'v13/RESTORE_NATIVE.py';v12=ROOT.parent/'v12/native_owner'
        if not v13.exists() or not v12.exists():
            raise SystemExit('Need sibling v12/native_owner and v13/RESTORE_NATIVE.py, or --base restored V13')
        subprocess.run([sys.executable,str(v13),'--base',str(v12),'--out',str(a.out)],check=True)
        for rel,h in spec['parent_hashes'].items():
            if sha(a.out/rel)!=h:raise SystemExit('Restored V13 mismatch: '+rel)
    for src,rec in spec['files'].items():
        q=ROOT/src
        if sha(q)!=rec['source_sha256']:raise SystemExit('Changed V14 payload: '+src)
        target=a.out/rec['destination'];target.parent.mkdir(parents=True,exist_ok=True)
        if rec['operation']=='append':
            target.write_bytes(target.read_bytes()+q.read_bytes())
        elif rec['operation']=='create':
            if target.exists():raise SystemExit('Unexpected file conflict: '+str(target))
            shutil.copyfile(q,target)
        else:raise SystemExit('Unknown restore operation')
        if sha(target)!=rec['output_sha256']:raise SystemExit('Output mismatch: '+str(target))
    receipt={'schema':'rei.v14.restore.1','parent_pr':196,'parent_sha':spec['parent_commit'],
             'output':str(a.out),'verified_files':len(spec['files']),
             'native_compile':'NOT_PERFORMED_BY_RESTORE',
             'sha256':{r['destination']:sha(a.out/r['destination']) for r in spec['files'].values()}}
    (a.out/'V14_RESTORE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
