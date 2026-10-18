#!/usr/bin/env python3
"""Reconstruct exact 91-file reactive1 crate; no network or source execution."""
import argparse, base64, hashlib, json, lzma
from pathlib import Path, PurePosixPath
HERE=Path(__file__).resolve().parent
PACKED='dfdcdc99cafc414d05c6c2f4b71b5ee010cff20c7c15c4c5b8dc9ed1ab69c741'
RAW='2a8a05d36234999c13da0ce3522c812f70c8dccbe934bc60946904940ad75eda'
def sha(data): return hashlib.sha256(data).hexdigest()
def safe(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or not p.parts: raise ValueError('unsafe path')
    return Path(*p.parts)
def restore(p9, intake, out):
    if out.exists(): raise ValueError('refuse existing output')
    encoded=''.join((HERE/f'source.part{i}').read_text().strip() for i in range(4))
    packed=base64.b64decode(encoded,validate=True)
    if sha(packed)!=PACKED: raise ValueError('packed identity mismatch')
    raw=lzma.decompress(packed,memlimit=268435456)
    if sha(raw)!=RAW: raise ValueError('JSON identity mismatch')
    packet=json.loads(raw); pool={}; payload={}
    for name, expected in packet['base_sha256'].items():
        group,rel=name.split('/',1); root={'p9':p9,'intake':intake}[group]
        data=(root/safe(rel)).read_bytes()
        if sha(data)!=expected: raise ValueError('base mismatch: '+name)
        pool['base/'+name]=data
    for item in packet['steps']:
        name=item['path'];safe(name)
        if name in payload: raise ValueError('duplicate output')
        if 'copy' in item: data=pool[item['copy']]
        elif 'text' in item: data=item['text'].encode('utf-8')
        else:
            lines=pool[item['from']].decode('utf-8').splitlines(keepends=True)
            for a,b,text in reversed(item['edits']):
                if not 0<=a<=b<=len(lines): raise ValueError('bad edit index')
                lines[a:b]=[text]
            data=''.join(lines).encode('utf-8')
        if sha(data)!=item['sha256']:raise ValueError('output mismatch: '+name)
        pool['made/'+name]=data;payload[name]=data
    if len(payload)!=91:raise ValueError('incomplete source')
    for name,data in payload.items():
        p=out/safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    return {'status':'EXACT_SOURCE_RESTORED','files':len(payload),'base_commit':packet['base_commit']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--p9',type=Path,required=True);p.add_argument('--intake',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    print(json.dumps(restore(a.p9,a.intake,a.out),indent=2))
