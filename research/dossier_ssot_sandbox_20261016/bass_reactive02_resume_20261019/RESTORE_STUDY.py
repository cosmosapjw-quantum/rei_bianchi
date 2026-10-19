#!/usr/bin/env python3
"""Reconstruct complete new crate from exact parent ZIP plus committed delta.
No network calls, compilation or source execution. Refuse existing output paths.
"""
import argparse,base64,hashlib,json,lzma,zipfile
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent

def safe(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or not p.parts:raise ValueError('unsafe path')
    return Path(*p.parts)

def sha(data):return hashlib.sha256(data).hexdigest()

def restore(parent,out):
    packed=base64.b64decode((HERE/'SOURCE_DELTA.xz.b64').read_bytes(),validate=True)
    if sha(packed)!='19560505728534e90a7954277defd37443b2bd348ec854326733a52e3fa90599':raise ValueError('packed source mismatch')
    raw=lzma.decompress(packed,memlimit=268435456)
    packet=json.loads(raw)
    if sha(parent.read_bytes())!=packet['parent_zip_sha256']:raise ValueError('wrong parent archive')
    if out.exists():raise FileExistsError(out)
    prefix='REI_BASS_REACTIVE01_NATIVE_20261018/'
    with zipfile.ZipFile(parent) as z:
        for f in z.infolist():
            safe(f.filename)
            if ((f.external_attr>>16)&0o170000)==0o120000:raise ValueError('symlink')
        out.mkdir(parents=True)
        for f in z.infolist():
            if f.filename.startswith(prefix):
                rel=f.filename[len(prefix):]
                if rel.startswith(('crate/','donor_input/')) and not f.is_dir():
                    p=out/safe(rel);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(f))
    for name,text in packet['files'].items():
        p=out/safe(name)
        if p.exists():raise ValueError('delta unexpectedly overwrites: '+name)
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text.encode())
    actual={p.relative_to(out/'crate').as_posix():sha(p.read_bytes()) for p in (out/'crate').rglob('*') if p.is_file()}
    if len(actual)!=97 or sha(json.dumps(actual,sort_keys=True,separators=(',',':')).encode())!=packet['complete_crate_manifest_sha256']:raise ValueError('complete source mismatch')
    print(json.dumps({'status':'EXACT_NATIVE_SOURCE_RESTORED','native_files':len(actual),'new_files':len(packet['files']),'destination':str(out)}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('parent_zip',type=Path);p.add_argument('destination',type=Path);a=p.parse_args();restore(a.parent_zip,a.destination)
