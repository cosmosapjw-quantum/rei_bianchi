#!/usr/bin/env python3
"""Read-only transport identity verifier for the frozen HE18 C3 full ZIP."""
import sys,json,zipfile,hashlib
from pathlib import Path

def verify(path):
 with zipfile.ZipFile(path) as z:
  bad=z.testzip()
  if bad is not None:raise ValueError('ZIP_CRC_FAILURE:'+bad)
  root='HE18_C3_20261015/'
  manifest=json.loads(z.read(root+'MANIFEST.json'))
  for n,v in manifest['payloads'].items():
   b=z.read(root+n)
   if len(b)!=v['bytes'] or hashlib.sha256(b).hexdigest()!=v['sha256']:
    raise ValueError('ZIP_PAYLOAD_FAILURE:'+n)
  return {'status':'TRANSPORT_CHECKS_PASS','payload_count':len(manifest['payloads']),
   'files_total':len(z.namelist()),'archive_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
   'scientific_theorem_independently_verified':False,'remote_restore_performed':False}
if __name__=='__main__':
 print(json.dumps(verify(sys.argv[1]),indent=2))
