"""Read-only original-byte and member verification for an R6 source ZIP."""
import argparse, hashlib, json, zipfile
from pathlib import Path, PurePosixPath
ap=argparse.ArgumentParser();ap.add_argument('archive');ap.add_argument('--sha256');a=ap.parse_args()
p=Path(a.archive);b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
if a.sha256 and sha!=a.sha256:raise ValueError('Original ZIP SHA256 mismatch')
with zipfile.ZipFile(p) as z:
    if z.testzip():raise ValueError('CRC failure')
    m=json.loads(z.read('ZIP_MANIFEST.json'));seen=set()
    for r in m['members']:
        n=PurePosixPath(r['path'])
        if n.is_absolute() or '..' in n.parts or str(n) in seen:raise ValueError('Unsafe or duplicate member')
        seen.add(str(n));data=z.read(str(n))
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if len(data)!=r['bytes'] or hashlib.sha256(data).hexdigest()!=r['sha256'] or blob!=r['git_blob']:raise ValueError('Member identity mismatch: '+str(n))
        if z.getinfo(str(n)).external_attr>>16 != int(r['mode'],8):raise ValueError('Member mode mismatch')
    if set(z.namelist())!=seen|{'ZIP_MANIFEST.json'}:raise ValueError('Unexpected archive members')
print(json.dumps({'status':'PASS_METADATA_ONLY','source_commit':m['source_commit'],'bytes':len(b),'sha256':sha,'payload_members':len(seen),'scientific_executions':0}))
