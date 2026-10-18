#!/usr/bin/env python3
"""Restore exact 91-file REACTIVE-01 crate; no network calls or source execution."""
from pathlib import Path, PurePosixPath
import argparse, base64, hashlib, json, lzma
HERE=Path(__file__).resolve().parent
PACKED_SHA='ec5116a57bfe9ef0c9a30a60d823df2a77b5a048326af9940dc5a1cd6204c600'
def digest(b): return hashlib.sha256(b).hexdigest()
def safe(s):
    p=PurePosixPath(s)
    if p.is_absolute() or '..' in p.parts or not p.parts: raise ValueError('unsafe path')
    return Path(*p.parts)
def restore(bases,out):
    if out.exists(): raise ValueError('output exists; choose a fresh directory')
    raw=base64.b64decode(''.join((HERE/f'source.part{i}').read_text().strip() for i in range(2)),validate=True)
    if digest(raw)!=PACKED_SHA: raise ValueError('packed source identity mismatch')
    packet=json.loads(lzma.decompress(raw,memlimit=268435456))
    contents={}
    for key,ref in packet['base'].items():
        data=(bases[ref['group']]/safe(ref['path'])).read_bytes()
        if digest(data)!=ref['sha256']: raise ValueError('base mismatch: '+key)
        contents[key]=data.decode('utf-8')
    for op in packet['ops']:
        if 'text' in op: text=op['text']
        else:
            lines=contents[op['from']].splitlines(keepends=True); pieces=[]
            for chunk in op['chunks']:
                if isinstance(chunk,str): pieces.append(chunk)
                else:
                    start,end=chunk
                    if not (0<=start<=end<=len(lines)):raise ValueError('invalid copy span')
                    pieces.append(''.join(lines[start:end]))
            text=''.join(pieces)
        contents[op['name']]=text
    output={}
    for name,expected in packet['output_sha256'].items():
        safe(name); data=contents[name].encode('utf-8')
        if digest(data)!=expected:raise ValueError('output mismatch: '+name)
        output[name]=data
    if len(output)!=91: raise ValueError('unexpected output count')
    out.mkdir(parents=True)
    for name,data in output.items():
        target=out/safe(name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    return {'status':'EXACT_91_FILE_CRATE_RESTORED','files':len(output),'output':str(out)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--p9',type=Path,required=True);p.add_argument('--intake',type=Path,required=True);p.add_argument('--prototype',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    print(json.dumps(restore({'p9':a.p9,'intake':a.intake,'prototype':a.prototype},a.out),indent=2))
