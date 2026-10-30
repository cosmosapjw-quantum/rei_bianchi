#!/usr/bin/env python3
"""Check exact byte identities of authored science payload and deterministic output."""
from __future__ import annotations
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(kind='manifest'):
    if kind=='outputs':
        obj=json.loads((ROOT/'OUTPUT_SHA256.json').read_text())
    else:obj=json.loads((ROOT/'MANIFEST.json').read_text())
    checks=obj['sha256']
    missing=[];bad=[]
    for name,sha in checks.items():
        p=ROOT/name
        if not p.is_file():missing.append(name)
        elif h(p)!=sha:bad.append({'path':name,'actual':h(p),'expected':sha})
    if missing or bad:raise ValueError('IDENTITY_FAIL '+str((missing,bad))[:3000])
    print(kind.upper()+'_SHA_PASS',len(checks),'/',len(checks))
if __name__=='__main__':verify(sys.argv[1] if len(sys.argv)>1 else 'manifest')
