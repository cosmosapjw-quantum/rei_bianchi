#!/usr/bin/env python3
"""Restore this source-only stage from exact P9 files, without running code."""
from pathlib import Path, PurePosixPath
import argparse,base64,hashlib,json,lzma
HERE=Path(__file__).resolve().parent
def sha(x): return hashlib.sha256(x).hexdigest()
def safe(n):
 p=PurePosixPath(n)
 if p.is_absolute() or '..' in p.parts or not p.parts: raise ValueError('unsafe path')
 return Path(*p.parts)
def restore(base,out):
 ident=json.loads((HERE/'PACKET_IDENTITY.json').read_text())
 b=base64.b64decode(''.join((HERE/f'source_delta.part{i}').read_text().strip() for i in range(ident['parts'])),validate=True)
 if sha(b)!=ident['lzma_sha256']: raise ValueError('packet bytes mismatch')
 data=lzma.decompress(b,memlimit=268435456)
 if sha(data)!=ident['json_sha256']: raise ValueError('decoded packet mismatch')
 p=json.loads(data)
 if out.exists(): raise ValueError('refuse overwrite; choose a new output directory')
 payload={}
 for n,h in p['base_sha256'].items():
  q=base/safe(n)
  if q.is_symlink(): raise ValueError('source symlink')
  payload[n]=q.read_bytes()
  if sha(payload[n])!=h: raise ValueError('parent mismatch: '+n)
 payload.update({n:t.encode('utf-8') for n,t in p['files'].items()})
 if {n:sha(v) for n,v in payload.items()}!=p['complete_sha256']: raise ValueError('output manifest mismatch')
 for n in payload: safe(n)
 out.mkdir(parents=True)
 for n,b in payload.items():
  q=out/safe(n);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
 return {'status':'SOURCE_BYTES_RESTORED','files':len(payload),'base_commit':p['base_commit'],'output':str(out)}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--base',type=Path,required=True);a.add_argument('--out',type=Path,required=True);o=a.parse_args();print(json.dumps(restore(o.base,o.out),indent=2))
