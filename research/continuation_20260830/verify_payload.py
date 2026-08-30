#!/usr/bin/env python3
"""Check delivered raw bytes and optional immutable Git inputs; never physics.

No mutable branch-tip equality, normalization of file bytes, obsolete R2
bootstrap helper, or canonical simulation is part of this check.
"""
from pathlib import Path, PurePosixPath
import argparse
import ast
import hashlib
import json
import re
import subprocess

REL=Path('research/continuation_20260830')
BASE='053b97c56e089e28a83f37d79a4128ed3cdae9f4'
BASE_TREE='46a96c789a691d671644685893a552cd9486788d'
PARTIAL='82c67218248cb896019b2bffc590da1260a214fc'
PARTIAL_TREE='dc801c78f01be32f6e6d74cc2d3f2abcfe2279d2'
HELPER_BLOB='8d0920626f6f90b4e6997c3daf01c4cca7ff0eee'

def git_bytes(repo,*args):
    p=subprocess.run(['git','--no-replace-objects',*args],cwd=repo,capture_output=True,timeout=30)
    if p.returncode:raise ValueError('required immutable Git object could not be read')
    return p.stdout

def git_line(repo,*args):
    # Only metadata is trimmed. Source-content hashing always receives raw bytes.
    return git_bytes(repo,*args).decode('ascii').removesuffix('\n')

def validate(root,repo=None):
    root=Path(root).resolve();directory=root/REL;entries={}
    for line in (directory/'MANIFEST.sha256').read_text(encoding='ascii').splitlines():
        parts=line.split('  ',1)
        if len(parts)!=2:raise ValueError('unsafe manifest syntax')
        digest,name=parts;path=PurePosixPath(name)
        if (not re.fullmatch(r'[0-9a-f]{64}',digest) or path.is_absolute()
            or '..' in path.parts or '\\' in name or str(path)!=name
            or not name.startswith(REL.as_posix()+'/')):
            raise ValueError('unsafe manifest path or digest')
        if name in entries:raise ValueError('duplicate manifest entry')
        target=root/name
        if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
            raise ValueError('unsafe or missing payload file')
        raw=target.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('payload digest mismatch: '+name)
        if target.suffix=='.py':ast.parse(raw,filename=name)
        entries[name]=digest
    contract=json.loads((directory/'CONTRACT.json').read_bytes())
    if set(entries)!=set(contract['delivery_paths']):raise ValueError('payload closure mismatch')
    if contract['source']['commit']!=BASE or contract['source']['tree']!=BASE_TREE:
        raise ValueError('source pin mismatch')
    if contract['partial_publication']['commit']!=PARTIAL or contract['partial_publication']['tree']!=PARTIAL_TREE:
        raise ValueError('preimage pin mismatch')
    if contract['claims']['current']!='NO_PASS_FIRST_CANONICAL_INTERVAL':raise ValueError('claim mismatch')
    locked=contract['locked']
    if (locked['local_quantity_limit_hex']!=float(2e-4).hex()
        or locked['public_width_limit_hex']!=float(2e-3).hex()
        or locked['minimum_ticks']!=1 or locked['state_nodes']!=46080):
        raise ValueError('frozen numerical scope changed')
    raw=(directory/'paired_budget.py').read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob!=HELPER_BLOB:raise ValueError('helper preimage mismatch')
    if repo is not None:
        repo=Path(repo)
        for head,tree in ((BASE,BASE_TREE),(PARTIAL,PARTIAL_TREE)):
            if git_line(repo,'rev-parse',head+'^{tree}')!=tree:raise ValueError('immutable tree mismatch')
        if git_line(repo,'rev-parse',PARTIAL+'^')!=BASE:raise ValueError('preimage parent mismatch')
        if git_bytes(repo,'show',PARTIAL+':'+str(REL/'paired_budget.py'))!=raw:
            raise ValueError('remote helper raw-byte mismatch')
        if git_line(repo,'rev-parse',BASE+':external/rec_bianchi.lock.json')!='d68cde8382f0c8c81e2747823bf11b6befb63f8b':
            raise ValueError('source rec-monitoring lock mismatch')
    return {'status':'PASS_PAYLOAD_ONLY','files':len(entries),
            'source_objects':'CHECKED' if repo is not None else 'NOT_RUN',
            'claim':'NO_PASS_FIRST_CANONICAL_INTERVAL','next':contract['next_action']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--repo',type=Path)
    a=p.parse_args()
    try:print(json.dumps(validate(a.root,a.repo),sort_keys=True))
    except (OSError,ValueError,KeyError,SyntaxError,subprocess.SubprocessError) as e:
        p.exit(2,'FAIL_PAYLOAD: '+str(e)+'\n')
