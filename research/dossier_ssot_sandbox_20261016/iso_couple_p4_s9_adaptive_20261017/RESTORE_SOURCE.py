#!/usr/bin/env python3
"""Reconstruct complete P9 source from verified P8 and exact delta. No network/code execution."""
from pathlib import Path,PurePosixPath
import argparse,base64,hashlib,json,lzma
HERE=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def path(s):
    p=PurePosixPath(s)
    if p.is_absolute() or '..' in p.parts or not p.parts:raise ValueError('unsafe path')
    return Path(*p.parts)
def restore(base,out):
    if out.exists():raise ValueError('Output exists; choose a new directory')
    expected=json.loads((HERE/'PACKET_IDENTITY.json').read_text())
    packed=base64.b64decode(''.join((HERE/f'source_delta.part{i}').read_text().strip() for i in range(expected['parts'])),validate=True)
    if sha(packed)!=expected['packed_sha256']:raise ValueError('Packed delta mismatch')
    raw=lzma.decompress(packed,memlimit=268435456)
    if sha(raw)!=expected['json_sha256']:raise ValueError('JSON mismatch')
    p=json.loads(raw)
    payload={}
    for k in p['parent_paths']:
        b=(base/path(k)).read_bytes()
        payload[k]=b
    manifest=lambda d:sha(json.dumps({k:sha(v) for k,v in d.items()},sort_keys=True,separators=(',',':')).encode())
    if manifest(payload)!=p['parent_manifest_sha256']:raise ValueError('Parent source tree mismatch')
    for k,v in p['source_delta'].items():payload[k]=v.encode('utf-8')
    if manifest(payload)!=p['complete_manifest_sha256']:raise ValueError('Output source manifest mismatch')
    for k,v in payload.items():
        q=out/path(k);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(v)
    return {'status':'EXACT_SOURCE_RESTORED','files':len(payload),'parent_commit':p['parent_commit']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    print(json.dumps(restore(a.base,a.out),indent=2))
