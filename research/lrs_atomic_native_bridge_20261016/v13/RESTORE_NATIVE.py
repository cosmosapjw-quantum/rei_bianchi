#!/usr/bin/env python3
"""Reconstruct the tested V13 native changes on the exact PR195 source capsule.

No existing source tree is edited. The V12 files remain the source authority.
Requires only Python's standard library and git (for applying a textual diff).
"""
from __future__ import annotations
import argparse,base64,hashlib,json,shutil,subprocess,zlib
from pathlib import Path

HERE=Path(__file__).resolve().parent

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def restore(base:Path,out:Path)->dict:
    packet=json.loads((HERE/'SOURCE_DELTA.json').read_text())
    if not base.is_dir(): raise FileNotFoundError(f'V12_SOURCE_MISSING: {base}')
    if out.exists(): raise FileExistsError(f'RESTORE_DESTINATION_EXISTS: {out}; use a fresh directory')
    for p,expected in packet['base_sha256'].items():
        if digest(base/p)!=expected: raise ValueError(f'BASE_IDENTITY_MISMATCH: {p}')
    encoded=''.join((HERE/name).read_text().strip() for name in packet['patch_chunks'])
    patch=zlib.decompress(base64.b64decode(encoded,validate=True))
    if hashlib.sha256(patch).hexdigest()!=packet['patch_sha256']: raise ValueError('PATCH_HASH_MISMATCH')
    out.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(base,out,ignore=shutil.ignore_patterns('.git','target','__pycache__','test_scratch'))
    subprocess.run(['git','apply','--check','-'],input=patch,cwd=out,check=True)
    subprocess.run(['git','apply','-'],input=patch,cwd=out,check=True)
    for p,expected in packet['output_sha256'].items():
        if digest(out/p)!=expected: raise ValueError(f'OUTPUT_IDENTITY_MISMATCH: {p}')
    result={'schema':'rei.v13.restore.1','parent_commit':packet['parent_commit'],
            'changed_file_hashes':packet['output_sha256'],'base':str(base),'output':str(out),
            'restored_files':len(packet['output_sha256']),'status':'SOURCE_RESTORED'}
    (out/'V13_RESTORE_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,default=HERE.parent/'v12'/'native_owner')
    parser.add_argument('--out',type=Path,default=HERE/'runtime'/'native_owner')
    args=parser.parse_args()
    print(json.dumps(restore(args.base.resolve(),args.out.resolve()),indent=2))
